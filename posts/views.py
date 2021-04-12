from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow


User = get_user_model()


@cache_page(1)
def index(request):
    search_post = request.GET.get('search')
    if search_post and len(search_post) > 0:
        post_list = Post.objects.filter(text__icontains=search_post)
    else:
        post_list = Post.objects.all()
    group_list = Group.objects.all()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {
            "page": page,
            "paginator": paginator,
            "groups": group_list,
            "search_post": search_post,
        }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    group_list = Group.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group,
         "page": page,
         "paginator": paginator,
         "groups": group_list,
         }
    )


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")

    form = PostForm()
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = False
    for item in author.following.all():
        if item.user == user:
            following = True
            break
    return render(
        request,
        "profile.html", {
            "user": user,
            "author": author,
            "page": page,
            "paginator": paginator,
            "following": following
            }
        )


def post_view(request, username, post_id):
    user = request.user
    post = get_object_or_404(Post.objects, id=post_id, author__username=username)
    print(post.audio)
    author = post.author
    items = post.comments.all()
    form = CommentForm()
    return render(
        request,
        "post.html",
        {"user": user, "author": author, "post": post, "items": items, "form": form}
        )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post.objects.select_related("author"),
                             id=post_id, author__username=username)
    post_url = reverse("post", args=(post.author, post.id))

    if post.author != request.user:
        return redirect(post_url)

    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(post_url)

    return render(
        request,
        "new_post.html",
        {"form": form, "post": post}
        )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post.objects.select_related("author"),
                             id=post_id, author__username=username)
    post_url = reverse("post", args=(post.author, post.id))
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect(post_url)

    form = CommentForm()
    return render(request, "new_post.html", {"form": form})


@login_required
def follow_index(request):
    followed_authors = [i.author for i in
                        Follow.objects.filter(user=request.user)]
    post_list = Post.objects.filter(
        author__in=followed_authors
    ).prefetch_related('author')
    group_list = Group.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {"page": page,
         "paginator": paginator,
         "groups": group_list,
         }
    )


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User.objects, username=username)
    if author == user:
        return render(request, "misc/self_subscription_error.html")
    Follow.objects.get_or_create(author=author, user=user)
    return redirect(f"/{author.username}")


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User.objects, username=username)
    Follow.objects.filter(author=author, user=user).delete()
    return redirect(f"/{author.username}")

@login_required
def delete_post(request, post_id=None):
    print(post_id)
    post_to_delete=Post.objects.get(id=post_id)
    post_to_delete.delete()
    return redirect("index")


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
