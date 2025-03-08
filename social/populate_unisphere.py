import os
import sys
import django

# Ensure the script runs from the correct directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniSphere.settings')
django.setup()

from UniSphereApp.models import StudentPost
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

def populate():
    # Create a test user (if not exists)
    user, created = User.objects.get_or_create(username="testuser", defaults={"password": "password123"})

    posts = [
        {"caption": "My first Django project!", "timestamp": now()},
        {"caption": "Machine Learning Model Deployment", "timestamp": now()},
        {"caption": "Personal Website Portfolio", "timestamp": now()},
    ]

    for post in posts:
        add_post(user, post["caption"], post["timestamp"])

    print("Database successfully populated!")


def add_post(user, caption, timestamp):
    post = StudentPost.objects.get_or_create(user=user, caption=caption, timestamp=timestamp)[0]
    post.save()
    return post


# Run the population script
if __name__ == '__main__':
    print("Starting UniSphere population script...")
    populate()
