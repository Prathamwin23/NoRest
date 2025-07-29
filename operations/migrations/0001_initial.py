import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.gis.db.models.fields
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):
    initial = True
    dependencies = [('auth', '0012_alter_user_first_name_max_length')]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('manager', 'Manager'), ('agent', 'Field Agent')], default='agent', max_length=20)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('current_location', django.contrib.gis.db.models.fields.PointField(blank=True, help_text='Current GPS location', null=True, srid=4326)),
                ('is_active_agent', models.BooleanField(default=True, help_text='Is agent currently working')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={'db_table': 'auth_user'},
            managers=[('objects', django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('address', models.TextField()),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='Client GPS coordinates', srid=4326)),
                ('priority', models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Urgent')], default=2)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-priority', 'name']},
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='assigned', max_length=20)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('estimated_duration', models.DurationField(blank=True, null=True)),
                ('actual_duration', models.DurationField(blank=True, null=True)),
                ('distance_to_client', models.FloatField(blank=True, help_text='Distance in kilometers', null=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='operations.client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-assigned_at']},
        ),
        migrations.CreateModel(
            name='LocationHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('accuracy', models.FloatField(blank=True, help_text='GPS accuracy in meters', null=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_history', to=settings.AUTH_USER_MODEL)),
                ('assignment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='operations.assignment')),
            ],
            options={'ordering': ['-timestamp']},
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notification_type', models.CharField(choices=[('assignment', 'New Assignment'), ('update', 'Assignment Update'), ('completion', 'Assignment Completed'), ('system', 'System Notification')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('assignment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='operations.assignment')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, unique=True)),
                ('value', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'System Setting', 'verbose_name_plural': 'System Settings'},
        ),
    ]
