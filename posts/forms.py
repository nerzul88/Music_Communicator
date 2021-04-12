from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image", "audio", "audio_title"]
        labels = {
            "text": "Текст",
            "group": "Группа",
            "image": "Изображение",
            "audio": "Аудиофайл",
            "audio_title": "Название трека",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
