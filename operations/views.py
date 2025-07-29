from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from .models import User, Client, Assignment, LocationHistory
from .forms import ClientUploadForm

def home(request):
    if not request.user.is_authenticated:
        return redirect('/admin/login/')
    if request.user.role == 'manager':
        return redirect('manager_dashboard')
    else:
        return redirect('agent_dashboard')

@login_required
def manager_dashboard(request):
    if request.user.role != 'manager':
        return redirect('agent_dashboard')

    context = {
        'total_agents': User.objects.filter(role='agent').count(),
        'active_agents': User.objects.filter(role='agent', is_active_agent=True).count(),
        'total_clients': Client.objects.filter(is_active=True).count(),
        'active_assignments': Assignment.objects.filter(status__in=['assigned', 'in_progress']).count(),
        'completed_today': Assignment.objects.filter(
            status='completed',
            completed_at__date=timezone.now().date()
        ).count(),
        'recent_assignments': Assignment.objects.select_related('agent', 'client').all()[:10],
        'agents_data': [{
            'agent': agent,
            'current_assignment': agent.current_assignment,
            'location': agent.current_location,
        } for agent in User.objects.filter(role='agent')],
    }
    return render(request, 'operations/manager_dashboard.html', context)

@login_required
def agent_dashboard(request):
    if request.user.role != 'agent':
        return redirect('manager_dashboard')

    context = {
        'current_assignment': request.user.current_assignment,
        'assignment_history': Assignment.objects.filter(agent=request.user)[:10],
        'unread_notifications': [],
        'agent_location': request.user.current_location,
    }
    return render(request, 'operations/agent_dashboard.html', context)

@login_required
def upload_clients(request):
    if request.method == 'POST':
        form = ClientUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            try:
                df = pd.read_excel(excel_file)
                required_columns = ['name', 'phone', 'address', 'latitude', 'longitude']
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    messages.error(request, f"Missing columns: {', '.join(missing_columns)}")
                    return render(request, 'operations/upload_clients.html', {'form': form})

                created_count = 0
                for index, row in df.iterrows():
                    try:
                        location = Point(float(row['longitude']), float(row['latitude']))
                        client, created = Client.objects.get_or_create(
                            phone=str(row['phone']),
                            defaults={
                                'name': str(row['name']),
                                'address': str(row['address']),
                                'location': location,
                                'email': str(row.get('email', '')),
                                'priority': int(row.get('priority', 2)),
                                'notes': str(row.get('notes', '')),
                            }
                        )
                        if created:
                            created_count += 1
                    except Exception as e:
                        messages.warning(request, f"Error processing row {index + 1}: {str(e)}")

                messages.success(request, f"Successfully created {created_count} new clients.")
                return redirect('manager_dashboard')

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
    else:
        form = ClientUploadForm()

    return render(request, 'operations/upload_clients.html', {'form': form})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_assign_client(request):
    try:
        agent_id = request.data.get('agent_id')
        agent = User.objects.get(id=agent_id, role='agent')

        if not agent.current_location:
            return Response({'error': 'Agent location not available'}, status=400)

        if agent.current_assignment:
            return Response({'error': 'Agent already has an active assignment'}, status=400)

        # Get available clients
        assigned_client_ids = Assignment.objects.filter(
            status__in=['assigned', 'in_progress']
        ).values_list('client_id', flat=True)

        available_clients = Client.objects.filter(is_active=True).exclude(id__in=assigned_client_ids)

        if not available_clients.exists():
            return Response({'error': 'No available clients'}, status=404)

        selected_client = available_clients.first()

        assignment = Assignment.objects.create(
            agent=agent,
            client=selected_client,
            created_by=request.user
        )

        return Response({
            'message': 'Assignment created successfully',
            'assignment_id': str(assignment.id),
            'client_name': selected_client.name,
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_assignment_status(request, assignment_id):
    try:
        assignment = Assignment.objects.get(id=assignment_id)
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')

        if new_status == 'in_progress':
            assignment.start_assignment()
        elif new_status == 'completed':
            assignment.complete_assignment(notes)
        else:
            assignment.status = new_status
            assignment.notes = notes
            assignment.save()

        return Response({
            'message': 'Assignment status updated successfully',
            'status': assignment.get_status_display()
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_agent_location(request):
    try:
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
        accuracy = request.data.get('accuracy')

        location = Point(longitude, latitude)
        request.user.current_location = location
        request.user.save()

        LocationHistory.objects.create(
            agent=request.user,
            location=location,
            accuracy=accuracy,
            assignment=request.user.current_assignment
        )

        return Response({'message': 'Location updated successfully'})

    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_route(request):
    try:
        start_lat = float(request.GET.get('start_lat'))
        start_lng = float(request.GET.get('start_lng'))
        end_lat = float(request.GET.get('end_lat'))
        end_lng = float(request.GET.get('end_lng'))

        # Simple fallback route
        return Response({
            'coordinates': [[start_lng, start_lat], [end_lng, end_lat]],
            'distance': 0,
            'duration': 0,
            'instructions': ['Follow the route to destination']
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)
