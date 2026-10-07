# Generated manually for session timer features

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookings', '0002_initial'),
    ]

    operations = [
        # Add session_started_notification_sent field to Booking
        migrations.AddField(
            model_name='booking',
            name='session_started_notification_sent',
            field=models.BooleanField(default=False),
        ),
        
        # Remove old BookingSession and recreate with new structure
        migrations.RemoveField(
            model_name='bookingsession',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='bookingsession',
            name='checked_in_by',
        ),
        migrations.RemoveField(
            model_name='bookingsession',
            name='seat',
        ),
        migrations.DeleteModel(
            name='BookingSession',
        ),
        
        # Create new BookingSession model
        migrations.CreateModel(
            name='BookingSession',
            fields=[
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='active_session', serialize=False, to='bookings.booking')),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled / Waiting to Start'), ('IN_PROGRESS', 'Active In Progress'), ('EXTENDED', 'Session Extended'), ('PAUSED', 'Temporarily Paused'), ('COMPLETED', 'Session Completed'), ('TERMINATED', 'Manually Ended by Staff'), ('EXPIRED', 'Time Expired')], default='SCHEDULED', max_length=20)),
                ('scheduled_start_time', models.DateTimeField()),
                ('scheduled_end_time', models.DateTimeField()),
                ('actual_start_time', models.DateTimeField(blank=True, null=True)),
                ('actual_end_time', models.DateTimeField(blank=True, null=True)),
                ('extended_minutes', models.PositiveIntegerField(default=0)),
                ('extension_count', models.PositiveIntegerField(default=0)),
                ('total_paused_seconds', models.PositiveIntegerField(default=0)),
                ('paused_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='started_sessions', to=settings.AUTH_USER_MODEL)),
                ('terminated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='terminated_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-scheduled_start_time'],
            },
        ),
    ]
