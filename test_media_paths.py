import os
import sys
import django

# Determine which project this is based on file location
current_dir = os.path.dirname(os.path.abspath(__file__))
project_name = os.path.basename(current_dir)

print(f"Testing: {project_name}")
print("=" * 60)

# Setup Django based on project
if project_name == 'event_admin':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_admin.settings')
    sys.path.insert(0, current_dir)
elif project_name == 'eventproject':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventproject.settings')
    sys.path.insert(0, current_dir)

django.setup()

from django.conf import settings

print(f"Project: {project_name}")
print(f"BASE_DIR: {settings.BASE_DIR}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")

# Check if directories exist
print("\nDirectory checks:")
print(f"MEDIA_ROOT exists: {os.path.exists(settings.MEDIA_ROOT)}")
if settings.MEDIA_ROOT:
    events_dir = os.path.join(settings.MEDIA_ROOT, 'events')
    print(f"events/ directory exists: {os.path.exists(events_dir)}")
    if os.path.exists(events_dir):
        files = os.listdir(events_dir)[:5]  # Show first 5 files
        print(f"Files in events/: {files}")

# Also check the actual path Django uses
try:
    from admin_panel.models import Event
    event = Event.objects.first()
    if event and event.image:
        print(f"\nSample Event: {event.name}")
        print(f"Image name in DB: {event.image.name}")
        print(f"Image path: {event.image.path}")
        print(f"Image exists: {os.path.exists(event.image.path)}")
except Exception as e:
    print(f"\nCould not access Event model: {e}")

print("=" * 60)