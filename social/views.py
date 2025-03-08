from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import FriendRequest
from django.http import HttpResponseForbidden

from django.shortcuts import get_object_or_404, redirect
from .models import Portfolio, Like, Comment, Share

@login_required
def send_friend_request(request, user_id):
    to_user = User.objects.get(id=user_id)
    if request.user != to_user:
        # Check if a request already exists
        if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
            return HttpResponseForbidden("Request already sent.")
        
        # Send the friend request
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
        return redirect('some_page')  # Redirect to a relevant page

    return HttpResponseForbidden("You can't send a request to yourself.")

@login_required
def accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)
    
    if friend_request.to_user != request.user:
        return HttpResponseForbidden("You can only accept requests sent to you.")

    friend_request.accepted = True
    friend_request.save()
    return redirect('some_page')

@login_required
def decline_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)

    if friend_request.to_user != request.user:
        return HttpResponseForbidden("You can only decline requests sent to you.")

    friend_request.declined = True
    friend_request.save()
    return redirect('some_page')

@login_required
def like_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    Like.objects.create(user=request.user, portfolio=portfolio)
    return redirect('portfolio_detail', portfolio_id=portfolio.id)

# Comment on a Portfolio
@login_required
def comment_on_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    if request.method == "POST":
        content = request.POST.get("content")
        Comment.objects.create(user=request.user, portfolio=portfolio, content=content)
    
    return redirect('portfolio_detail', portfolio_id=portfolio.id)

# Share a Portfolio
@login_required
def share_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    Share.objects.create(user=request.user, portfolio=portfolio)
    return redirect('portfolio_detail', portfolio_id=portfolio.id)
