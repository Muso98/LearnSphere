import os
import django
import sys

# Setup Django environment
sys.path.append('m:\\LearnSphere')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearnSphere.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from administration.views import stats_top_students, stats_struggling_students

User = get_user_model()

# Create a dummy superuser request
user = User.objects.filter(is_superuser=True).first()
if not user:
    print("No superuser found. Creating one.")
    user = User.objects.create_superuser('admin_debug', 'admin@example.com', 'password')

factory = RequestFactory()
request = factory.get('/fake-url')
request.user = user

print("Testing stats_top_students...")
try:
    response = stats_top_students(request)
    if response.status_code != 200:
        print(f"Failed with status {response.status_code}")
        print(response.content.decode())
    else:
        print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()

print("\nTesting stats_struggling_students...")
try:
    response = stats_struggling_students(request)
    if response.status_code != 200:
        print(f"Failed with status {response.status_code}")
        print(response.content.decode())
    else:
        print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
