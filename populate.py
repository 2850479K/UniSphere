import os
import random
import django
import sys
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify
from django.contrib.auth import get_user_model

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UniSphere.settings")
django.setup()

from django.conf import settings
from UniSphereApp.models import StudentProfile, SocietyProfile, Project, StudentPost, PostFile, Comment, Like, Repost

User = get_user_model()

MEDIA_ROOT = settings.MEDIA_ROOT
PROFILE_PICS = os.path.join(MEDIA_ROOT, 'profiles')
POST_IMAGES = os.path.join(MEDIA_ROOT, 'posts', 'images')
POST_DOCS = os.path.join(MEDIA_ROOT, 'posts', 'docs')
POST_VIDEOS = os.path.join(MEDIA_ROOT, 'posts', 'videos')

students = [
    {'username': 'aisha.khan', 'full_name': 'Aisha Khan', 'school': 'University of Leeds', 'course': 'Data Science'},
    {'username': 'leo.turner', 'full_name': 'Leo Turner', 'school': 'UCL', 'course': 'Architecture'},
    {'username': 'emily.chen', 'full_name': 'Emily Chen', 'school': 'University of Glasgow', 'course': 'Medicine'},
    {'username': 'jake.evans', 'full_name': 'Jake Evans', 'school': 'University of York', 'course': 'Cyber Security'},
    {'username': 'mia.patel', 'full_name': 'Mia Patel', 'school': 'King’s College London', 'course': 'Law'},
    {'username': 'daniel.white', 'full_name': 'Daniel White', 'school': 'University of Exeter', 'course': 'Economics'},
    {'username': 'isla.green', 'full_name': 'Isla Green', 'school': 'University of Birmingham', 'course': 'Marketing'},
    {'username': 'harry.wilson', 'full_name': 'Harry Wilson', 'school': 'University of Sheffield', 'course': 'Physics'},
    {'username': 'amelia.james', 'full_name': 'Amelia James', 'school': 'University of Liverpool', 'course': 'Sociology'},
    {'username': 'ethan.brown', 'full_name': 'Ethan Brown', 'school': 'University of Manchester', 'course': 'Software Engineering'},
    {'username': 'sophia.wright', 'full_name': 'Sophia Wright', 'school': 'LSE', 'course': 'Political Science'},
    {'username': 'noah.hughes', 'full_name': 'Noah Hughes', 'school': 'University of Bath', 'course': 'Psychology'},
    {'username': 'ava.morris', 'full_name': 'Ava Morris', 'school': 'University of Nottingham', 'course': 'Linguistics'},
    {'username': 'oliver.clark', 'full_name': 'Oliver Clark', 'school': 'Durham University', 'course': 'History'},
    {'username': 'freya.hall', 'full_name': 'Freya Hall', 'school': 'University of Warwick', 'course': 'Biology'},
]

societies = [
    {'username': 'codehub', 'society_name': 'CodeHub Society', 'category': 'Tech'},
    {'username': 'greenunite', 'society_name': 'Green Unite', 'category': 'Environment'},
    {'username': 'aiesec', 'society_name': 'AIESEC UK', 'category': 'Leadership'},
    {'username': 'womensnetwork', 'society_name': 'Women in STEM', 'category': 'STEM'},
    {'username': 'musicwave', 'society_name': 'MusicWave', 'category': 'Arts'},
    {'username': 'sportsunited', 'society_name': 'Sports United', 'category': 'Sports'},
    {'username': 'enactus', 'society_name': 'Enactus Uni', 'category': 'Entrepreneurship'},
]

def get_random_file(path):
    files = [f for f in os.listdir(path) if not f.startswith('.')]
    if not files:
        return None
    return os.path.join(path, random.choice(files))

def create_students():
    for s in students:
        user, created = User.objects.get_or_create(
            username=s['username'],
            defaults={'email': f"{s['username'].replace('.', '')}@example.com", 'role': 'student'}
        )
        if created:
            user.set_password('testpassword123')
            user.save()
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        profile.full_name = s['full_name']
        profile.school = s['school']
        profile.course = s['course']
        profile.gender = random.choice(['female', 'male'])
        profile.bio = f"Hi! I'm {s['full_name']} studying {s['course']} at {s['school']}."
        profile.languages = random.choice(['English', 'Spanish, English', 'Mandarin, English'])
        profile.interests = random.choice(['AI, Robotics', 'Literature, Arts', 'Healthcare, Neuroscience'])
        profile.visibility = 'public'
        pic = get_random_file(PROFILE_PICS)
        if pic:
            with open(pic, 'rb') as f:
                profile.profile_picture.save(os.path.basename(pic), File(f), save=False)
        profile.save()

def create_societies():
    for s in societies:
        user, created = User.objects.get_or_create(
            username=s['username'],
            defaults={'email': f"{s['username']}@society.org", 'role': 'society'}
        )
        if created:
            user.set_password('testpassword123')
            user.save()
        profile, _ = SocietyProfile.objects.get_or_create(user=user)
        profile.society_name = s['society_name']
        profile.category = s['category']
        profile.description = f"We are {s['society_name']}, passionate about {s['category'].lower()}!"
        profile.contact_email = user.email
        profile.social_links = "https://instagram.com/example"
        logo = get_random_file(PROFILE_PICS)
        if logo:
            with open(logo, 'rb') as f:
                profile.logo.save(os.path.basename(logo), File(f), save=False)
        profile.save()

def attach_random_media(post):
    folder_choice = random.choice(['image', 'doc', 'video'])
    if folder_choice == 'image':
        path = get_random_file(POST_IMAGES)
    elif folder_choice == 'doc':
        path = get_random_file(POST_DOCS)
    else:
        path = get_random_file(POST_VIDEOS)
    if path:
        with open(path, 'rb') as f:
            PostFile.objects.create(post=post, file=SimpleUploadedFile(os.path.basename(path), f.read()))

def create_projects_and_posts():
    descriptions = [
        "An interactive web app built using Django.",
        "A machine learning model to predict housing prices.",
        "A 2D game created with Python and Pygame.",
        "A research-based project exploring UI/UX trends.",
        "An automated bot to help students manage tasks."
    ]
    captions = [
        "Excited to share this update!", "Here's a sneak peek into my work.",
        "Loving this project so far.", "Would love feedback on this!",
        "Working on something innovative!"
    ]
    users = User.objects.all()
    for user in users:
        # Create 1 project
        project = Project.objects.create(
            user=user,
            title=f"{user.username}'s Project",
            description=random.choice(descriptions)
        )

        # Create 1 post attached to that project
        post1 = StudentPost.objects.create(
            user=user,
            project=project,
            title=f"{user.username}'s Project Post",
            caption=random.choice(captions)
        )
        attach_random_media(post1)

        # Create 1 profile-level post not attached to a project
        post2 = StudentPost.objects.create(
            user=user,
            project=None,
            title=f"{user.username}'s Profile Post",
            caption=random.choice(captions)
        )
        attach_random_media(post2)

def create_social():
    users = list(User.objects.all())
    posts = StudentPost.objects.all()
    comments = [
        "This is amazing!", "Really impressive work.",
        "Thanks for sharing!", "How did you build this?",
        "Looks great! Keep going."
    ]
    for post in posts:
        random.shuffle(users)
        for user in users[:3]:
            if random.random() < 0.7:
                Comment.objects.create(post=post, user=user, content=random.choice(comments))
            if not Like.objects.filter(post=post, user=user).exists():
                Like.objects.create(post=post, user=user)
        if random.random() < 0.25:
            reposter = random.choice(users)
            if not Repost.objects.filter(original_post=post, user=reposter).exists():
                Repost.objects.create(original_post=post, user=reposter)

def run():
    print("\U0001F680 Starting population...")
    create_students()
    create_societies()
    print("✅ Users and profiles created.")
    create_projects_and_posts()
    print("✔ Projects and posts created (including society posts).")
    create_social()
    print("✔ Comments, likes, and reposts created.")
    print("\U0001F389 Population script complete!")

if __name__ == '__main__':
    run()
