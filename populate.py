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
from UniSphereApp.models import (
    StudentProfile, SocietyProfile, Project, StudentPost, PostFile,
    Comment, Like, Repost
)
from django.contrib.auth import get_user_model

User = get_user_model()

# ----------------------------------
# File paths
# ----------------------------------
MEDIA_ROOT = settings.MEDIA_ROOT
PROFILE_PICS = os.path.join(MEDIA_ROOT, 'profiles')
POST_IMAGES = os.path.join(MEDIA_ROOT, 'posts', 'images')
POST_DOCS = os.path.join(MEDIA_ROOT, 'posts', 'docs')
POST_VIDEOS = os.path.join(MEDIA_ROOT, 'posts', 'videos')

# ----------------------------------
# Media Mapping (project + caption)
# ----------------------------------
media_map = {
    "digital art.jpg": ("Concept Art", "Playing with light and shadow in digital art."),
    "chess.jpg": ("Chess Tactics App", "Analyzing chess strategies for tournaments."),
    "knitting.jpg": ("Knitting for Beginners", "Relaxing weekend making a sweater 🧶"),
    "kayak.jpg": ("Kayaking Community", "Exploring nature in my free time 🌊"),
    "photography.jpg": ("Street Photography", "Captured this during golden hour."),
    "snorkling.jpg": ("Ocean Conservation", "Snorkeling trip footage 🐠"),
    "fishing.jpg": ("Outdoor Life", "Fishing trip with friends last month."),
    "painting.jpg": ("Art Showcase", "Working on a new acrylic piece 🎨"),
    "baking.jpg": ("Baking Club", "Fresh out of the oven 🍞"),
    "golf.jpg": ("Sports Analytics", "Golf day ⛳️"),
    "surfing.jpg": ("Extreme Sports", "Caught a wave 🌊"),
    "workout.jpg": ("Fitness Journey", "Post-workout pump 💪"),
    "research on AI ethics.pdf": ("AI and Ethics", "Sharing my AI ethics paper."),
    "math paper.pdf": ("Mathematics Research", "My recent math proof write-up."),
    "research on education.pdf": ("Comparative Education", "How education systems differ globally."),
    "research on nurses.pdf": ("Nursing Study", "Healthcare roles study."),
    "research into preschool education.pdf": ("Early Learning", "On child learning approaches."),
    "fish.mp4": ("Marine Biology Fieldwork", "Underwater shot of a curious fish 🐟"),
    "arts and crafts.mp4": ("Crafting Club", "My DIY project reel!"),
    "science lab.mp4": ("STEM Club", "Experiment from last week’s lab."),
}

# ----------------------------------
# Users
# ----------------------------------
students = [
    {"username": "leo.turner", "full_name": "Leo Turner", "school": "UCL", "course": "Architecture", "pic": "student1.jpg"},
    {"username": "emily.chen", "full_name": "Emily Chen", "school": "Glasgow", "course": "Medicine", "pic": "student2.jpg"},
    {"username": "jake.evans", "full_name": "Jake Evans", "school": "York", "course": "Cyber Security", "pic": "student3.jpg"},
    {"username": "mia.patel", "full_name": "Mia Patel", "school": "KCL", "course": "Law", "pic": "student4.jpg"},
    {"username": "ethan.brown", "full_name": "Ethan Brown", "school": "Manchester", "course": "Software Engineering", "pic": "student5.jpg"},
    {"username": "ava.morris", "full_name": "Ava Morris", "school": "Nottingham", "course": "Linguistics", "pic": "student6.jpg"},
]

societies = [
    {"username": "eco", "society_name": "Eco Society", "category": "Environment", "logo": "eco society.jpg"},
    {"username": "photo", "society_name": "Photography Society", "category": "Arts", "logo": "photography society.jpg"},
    {"username": "fin", "society_name": "Finance Society", "category": "Business", "logo": "finance society.jpg"},
]

# ----------------------------------
# Utilities
# ----------------------------------
def get_file(path):
    with open(path, "rb") as f:
        return SimpleUploadedFile(os.path.basename(path), f.read())

def get_random_file(path):
    files = [f for f in os.listdir(path) if not f.startswith('.')]
    return os.path.join(path, random.choice(files)) if files else None

def attach_media_to_post(post, filename):
    if filename.endswith(".jpg"):
        path = os.path.join(POST_IMAGES, filename)
    elif filename.endswith(".pdf"):
        path = os.path.join(POST_DOCS, filename)
    elif filename.endswith(".mp4"):
        path = os.path.join(POST_VIDEOS, filename)
    else:
        return
    PostFile.objects.create(post=post, file=get_file(path))

# ----------------------------------
# Creation logic
# ----------------------------------
def create_users():
    for s in students:
        user, _ = User.objects.get_or_create(username=s["username"], defaults={"email": f"{s['username']}@mail.com", "role": "student"})
        user.set_password("test123")
        user.save()
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        profile.full_name = s["full_name"]
        profile.school = s["school"]
        profile.course = s["course"]
        profile.bio = f"Hi, I'm {s['full_name']} studying {s['course']} at {s['school']}."
        profile.languages = "English"
        profile.interests = random.choice(["Tech", "Nature", "Arts", "Education", "Health"])
        with open(os.path.join(PROFILE_PICS, s['pic']), 'rb') as f:
            profile.profile_picture.save(s['pic'], File(f), save=False)
        profile.save()

        for s in societies:
            user, _ = User.objects.get_or_create(username=s["username"], defaults={
                "email": f"{s['username']}@society.org",
                "role": "society"
            })
            user.set_password("test123")
            user.save()

            profile, _ = SocietyProfile.objects.get_or_create(user=user)
            profile.society_name = s["society_name"]
            profile.category = s["category"]
            profile.description = f"{s['society_name']} is all about {s['category'].lower()}!"
            profile.contact_email = user.email
            profile.social_links = "https://instagram.com/example"

            # ✅ Attempt to load specified logo
            logo_path = os.path.join(PROFILE_PICS, s['logo'])
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    profile.logo.save(s['logo'], File(f), save=False)
            else:
                # ✅ Fallback: pick any logo to assign
                random_logo = get_random_file(PROFILE_PICS)
                if random_logo:
                    with open(random_logo, 'rb') as f:
                        profile.logo.save(os.path.basename(random_logo), File(f), save=False)
                print(f"⚠️ Missing specified logo for {s['society_name']}, using random fallback.")

            profile.save()

def create_posts():
    users = list(User.objects.all())
    media_list = list(media_map.items())
    random.shuffle(media_list)
    posts = []

    for i, (filename, (project_title, caption)) in enumerate(media_list[:18]):
        user = users[i % len(users)]
        project = Project.objects.create(
            user=user,
            title=project_title,
            description=f"{project_title} - a creative exploration."
        )
        post = StudentPost.objects.create(
            user=user,
            project=project,
            title="Project Update",
            caption=caption
        )
        attach_media_to_post(post, filename)
        posts.append(post)
    return posts

def create_interactions(posts):
    users = list(User.objects.all())
    comments = [
        "This is amazing!", "Love this idea!", "Wow, so creative.",
        "Would love to learn more.", "Nice use of visuals.",
        "Great concept!", "So relevant.", "This is inspiring.",
        "Love your style.", "Fantastic explanation!"
    ]
    
    # General interactions (likes/comments)
    for post in posts:
        sample_users = random.sample(users, min(4, len(users)))
        for user in sample_users:
            Like.objects.get_or_create(user=user, post=post)
            if random.random() < 0.7:
                Comment.objects.create(user=user, post=post, content=random.choice(comments))

    # Ensure every user reposts at least one post not their own
    for user in users:
        other_posts = [p for p in posts if p.user != user]
        if other_posts:
            post_to_repost = random.choice(other_posts)
            Repost.objects.get_or_create(user=user, original_post=post_to_repost)

def create_relationships():
    students = StudentProfile.objects.all()
    societies = SocietyProfile.objects.all()
    for student in students:
        joined = random.sample(list(societies), random.randint(1, 2))
        for society in joined:
            society.members.add(student)

def create_friendships():
    students = list(StudentProfile.objects.all())
    random.shuffle(students)
    
    for i in range(0, len(students) - 1, 2):
        student1 = students[i]
        student2 = students[i + 1]
        student1.friends.add(student2)
        student2.friends.add(student1)

# ----------------------------------
# Run everything
# ----------------------------------
def run():
    print("🌍 Populating UniSphere...")
    create_users()
    print("✅ Users and profiles created.")
    posts = create_posts()
    print(f"📑 {len(posts)} posts created.")
    create_interactions(posts)
    print("💬 Comments, likes, reposts added.")
    create_relationships()
    print("👥 Students joined societies.")
    create_friendships()
    print("🎉 Done!")

if __name__ == '__main__':
    run()
