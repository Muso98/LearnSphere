import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearnSphere.settings')
django.setup()

from accounts.models import User

def create_admin():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created with password 'admin123'.")
    else:
        u = User.objects.get(username='admin')
        u.set_password('admin123')
        u.save()
        print("Superuser 'admin' password updated to 'admin123'.")

if __name__ == '__main__':
    create_admin()
