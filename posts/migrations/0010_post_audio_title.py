# Generated by Django 3.1.7 on 2021-02-28 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_post_audio'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='audio_title',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
