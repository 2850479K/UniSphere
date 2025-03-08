from django.urls import path
from . import views

urlpatterns = [
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('like/<int:portfolio_id>/', views.like_portfolio, name='like_portfolio'),
    path('comment/<int:portfolio_id>/', views.comment_on_portfolio, name='comment_on_portfolio'),
    path('share/<int:portfolio_id>/', views.share_portfolio, name='share_portfolio'),
]
    # Add other URLs for like, comment, etc.
]

