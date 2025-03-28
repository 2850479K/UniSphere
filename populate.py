import os
import random
import django
import sys
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UniSphere.settings")
django.setup()

from django.conf import settings
from UniSphereApp.models import StudentProfile, SocietyProfile, Project, StudentPost, PostFile, Comment, Like, Repost
from django.contrib.auth import get_user_model

User = get_user_model()

MEDIA_ROOT = settings.MEDIA_ROOT
PROFILE_PICS = os.path.join(MEDIA_ROOT, 'profiles')
POST_IMAGES = os.path.join(MEDIA_ROOT, 'posts', 'images')
POST_DOCS = os.path.join(MEDIA_ROOT, 'posts', 'docs')
POST_VIDEOS = os.path.join(MEDIA_ROOT, 'posts', 'videos')

students = [
    {'username': 'leo.turner', 'full_name': 'Leo Turner', 'school': 'UCL', 'course': 'Architecture'},
    {'username': 'emily.chen', 'full_name': 'Emily Chen', 'school': 'Glasgow', 'course': 'Medicine'},
    {'username': 'jake.evans', 'full_name': 'Jake Evans', 'school': 'York', 'course': 'Cyber Security'},
    {'username': 'mia.patel', 'full_name': 'Mia Patel', 'school': 'KCL', 'course': 'Law'},
    {'username': 'ethan.brown', 'full_name': 'Ethan Brown', 'school': 'Manchester', 'course': 'Software Engineering'},
    {'username': 'ava.morris', 'full_name': 'Ava Morris', 'school': 'Nottingham', 'course': 'Linguistics'},
    {'username': 'oliver.clark', 'full_name': 'Oliver Clark', 'school': 'Durham', 'course': 'History'},
    {'username': 'freya.hall', 'full_name': 'Freya Hall', 'school': 'Warwick', 'course': 'Biology'},
]

societies = [
    {'username': 'codehub', 'society_name': 'CodeHub Society', 'category': 'Tech'},
    {'username': 'greenunite', 'society_name': 'Green Unite', 'category': 'Environment'},
    {'username': 'aiesec', 'society_name': 'AIESEC UK', 'category': 'Leadership'},
    {'username': 'musicwave', 'society_name': 'MusicWave', 'category': 'Arts'},
    {'username': 'enactus', 'society_name': 'Enactus Uni', 'category': 'Entrepreneurship'},
]

# --- Helper Functions ---
def get_random_file(path):
    files = [f for f in os.listdir(path) if not f.startswith('.')]
    return os.path.join(path, random.choice(files)) if files else None

def attach_random_media(post):
    folder = random.choice([POST_IMAGES, POST_VIDEOS, POST_DOCS])
    file_path = get_random_file(folder)
    if file_path:
        with open(file_path, 'rb') as f:
            PostFile.objects.create(
                post=post,
                file=SimpleUploadedFile(os.path.basename(file_path), f.read())
            )

# --- Captions and Comments ---
captions = [
    "Tried something new this time!",
    "Here’s a peek into my latest project 🎬",
    "From sketch to final render ✏️➡️🎨",
    "Late-night ideas turn into this!",
    "Does this make sense to you?",
    "Science meets art in this piece",
    "Bit outside my comfort zone, but proud of it!",
    "Throwback to last summer’s project",
    "Inspired by my travels 🌍",
    "Would love your feedback!",
    "First time using this tool and here’s the result",
    "Part of a bigger series",
    "Experiments don’t always go as planned 😅",
    "Started as a joke... turned serious 😳",
    "Quick weekend build!",
    "Who else relates to this?",
    "Based on a real-life moment 💭",
    "We talked about this in class today!",
    "Captured this on my old phone",
    "Mixing media types was fun!"
]

comments = [
    "Wow, this is amazing!",
    "So creative 👏",
    "Really insightful, thanks for sharing!",
    "Where did you shoot this?",
    "Love the aesthetic 😍",
    "Subscribed to your channel!",
    "This helped me a lot.",
    "Would you mind if I referenced this?",
    "Exactly what I was looking for.",
    "🔥🔥🔥",
    "How long did this take?",
    "Can I join your society?",
    "Reminds me of my own project!",
    "Please post more like this!",
    "Mind if I DM you for details?",
    "Such a vibe 💯",
    "I'm inspired to try this too!",
    "Love the writing style!",
    "Awesome colors",
    "Was this shot on a DSLR?"
]

# --- Create Users ---
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
        profile.bio = f"Hey! I'm {s['full_name']} studying {s['course']} at {s['school']}."
        profile.visibility = 'public'
        profile.gender = random.choice(['male', 'female'])
        profile.languages = random.choice(['English', 'French', 'Mandarin', 'Spanish'])
        profile.interests = random.choice(['Tech', 'Health', 'Art', 'Sustainability'])
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
        profile.description = f"{s['society_name']} is passionate about {s['category'].lower()}!"
        profile.contact_email = user.email
        profile.social_links = "https://instagram.com/example"
        logo = get_random_file(PROFILE_PICS)
        if logo:
            with open(logo, 'rb') as f:
                profile.logo.save(os.path.basename(logo), File(f), save=False)
        profile.save()

# --- Create Posts ---
def create_posts():
    users = list(User.objects.all())
    posts = []
    for user in users:
        for _ in range(random.randint(2, 3)):
            project = None
            if random.random() < 0.6:
                project = Project.objects.create(
                    user=user,
                    title=f"{user.username}'s Project",
                    description=random.choice([
                        "A sustainability-focused app", "A minimalist UI for students", 
                        "Machine learning dashboard", "Event promo with animation", 
                        "Hackathon project", "Python + Django backend",
                        "React frontend with charts", "Campaign branding", "Mobile game UX redesign"
                    ])
                )
            post = StudentPost.objects.create(
                user=user,
                project=project,
                title=random.choice(["Update", "Build Log", "Quick Post"]),
                caption=random.choice(captions)
            )
            attach_random_media(post)
            posts.append(post)
    return posts

# --- Create Interactions (Likes, Comments, Reposts) ---
def create_interactions(posts):
    users = list(User.objects.all())
    for post in posts:
        engaged_users = random.sample(users, random.randint(3, 5))
        for user in engaged_users:
            if random.random() < 0.85:
                Like.objects.get_or_create(user=user, post=post)
            if random.random() < 0.5:
                Comment.objects.create(user=user, post=post, content=random.choice(comments))
        if random.random() < 0.3:
            reposter = random.choice(users)
            Repost.objects.get_or_create(user=reposter, original_post=post)

def run():
    print("🚀 Populating UniSphere with realistic user activity...")
    create_students()
    create_societies()
    print("✅ Users created.")
    posts = create_posts()
    print(f"📸 {len(posts)} posts created.")
    create_interactions(posts)
    print("💬 Interactions added.")
    print("🎉 Done!")

if __name__ == '__main__':
    run()
