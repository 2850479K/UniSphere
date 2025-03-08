from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)

    def __str__(self):
        return f"Friend request from {self.from_user} to {self.to_user}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)  # Reference to Portfolio
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} liked {self.portfolio}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.portfolio}"

class Share(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} shared {self.portfolio}"

