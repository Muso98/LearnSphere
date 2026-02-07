import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LearnSphere.settings')
django.setup()

from accounts.models import User

def create_director():
    if not User.objects.filter(username='director1').exists():
        User.objects.create_user('director1', 'director1@example.com', 'password123', role='director', first_name='Director', last_name='User')
        print("Director user created.")
    else:
        print("Director user already exists.")

if __name__ == '__main__':
    create_director()
