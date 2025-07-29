from django import forms
from django.contrib.gis.geos import Point
from .models import Client, Assignment, User

class ClientUploadForm(forms.Form):
    file = forms.FileField(
        label="Excel File",
        help_text="Upload Excel file with columns: name, phone, email, address, latitude, longitude, priority",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError("Please upload a valid Excel file (.xlsx or .xls)")
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 5MB")
        return file

class ClientForm(forms.ModelForm):
    latitude = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': 'any',
            'placeholder': '12.9716'
        }),
        help_text="Enter latitude coordinate"
    )
    longitude = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'step': 'any',
            'placeholder': '77.5946'
        }),
        help_text="Enter longitude coordinate"
    )

    class Meta:
        model = Client
        fields = ['name', 'phone', 'email', 'address', 'priority', 'notes', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.location:
                self.fields['latitude'].initial = self.instance.location.y
                self.fields['longitude'].initial = self.instance.location.x

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')

        if latitude is not None and longitude is not None:
            if not (-90 <= latitude <= 90):
                raise forms.ValidationError("Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise forms.ValidationError("Longitude must be between -180 and 180")
            cleaned_data['location'] = Point(longitude, latitude)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        latitude = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')

        if latitude is not None and longitude is not None:
            instance.location = Point(longitude, latitude)

        if commit:
            instance.save()
        return instance

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['agent', 'client', 'status', 'notes', 'estimated_duration']
        widgets = {
            'agent': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estimated_duration': forms.TimeInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agent'].queryset = User.objects.filter(role='agent', is_active=True)
        self.fields['client'].queryset = Client.objects.filter(is_active=True)
