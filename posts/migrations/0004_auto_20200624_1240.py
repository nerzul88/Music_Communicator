# Generated by Django 2.2.9 on 2020-06-24 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20200525_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(max_length=600),
        ),
    ]
