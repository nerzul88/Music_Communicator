from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=600)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name="posts", blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    audio = models.FileField(upload_to='musics/', null=True)
    audio_title = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField("Дата добавления", auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL,
                             related_name="comments", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["created"]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
