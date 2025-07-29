from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from operations.models import Client
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create superuser
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='manager'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))

        # Create manager
        if not User.objects.filter(username='manager').exists():
            User.objects.create_user(
                username='manager',
                email='manager@example.com',
                password='password123',
                role='manager',
                first_name='Manager',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created manager: manager/password123'))

        # Create agents
        for i in range(5):
            username = f'agent{i+1}'
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123',
                    role='agent',
                    first_name=f'Agent {i+1}',
                    phone=f'+91-98765432{i:02d}',
                    current_location=Point(
                        77.5946 + random.uniform(-0.1, 0.1),
                        12.9716 + random.uniform(-0.1, 0.1),
                    )
                )

        # Create sample clients
        sample_locations = [
            {'name': 'TechCorp Solutions', 'lat': 12.9279, 'lng': 77.6271, 'address': 'Koramangala, Bangalore'},
            {'name': 'Global Systems Inc', 'lat': 12.9719, 'lng': 77.6412, 'address': 'Indiranagar, Bangalore'},
            {'name': 'Innovate Corp', 'lat': 12.9698, 'lng': 77.7500, 'address': 'Whitefield, Bangalore'},
            {'name': 'StartUp Inc', 'lat': 12.8456, 'lng': 77.6621, 'address': 'Electronic City, Bangalore'},
            {'name': 'Enterprise Ltd', 'lat': 13.0355, 'lng': 77.5986, 'address': 'Hebbal, Bangalore'},
        ]

        for i, location_data in enumerate(sample_locations):
            if not Client.objects.filter(name=location_data['name']).exists():
                Client.objects.create(
                    name=location_data['name'],
                    phone=f'+91-98765{random.randint(10000, 99999)}',
                    email=f'client{i+1}@example.com',
                    address=location_data['address'],
                    location=Point(location_data['lng'], location_data['lat']),
                    priority=random.choice([1, 2, 3, 4]),
                    notes=f'Sample client {i+1} for testing'
                )

        self.stdout.write(
            self.style.SUCCESS(
                'Sample data created!\n'
                'Login: admin/admin123, manager/password123, agent1-5/password123'
            )
        )
