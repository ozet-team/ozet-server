# Generated by Django 3.2.6 on 2021-12-13 22:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resume', '0002_auto_20211213_1540'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resume',
            options={'verbose_name': '이력서'},
        ),
        migrations.RemoveField(
            model_name='resume',
            name='pdf',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='title',
        ),
        migrations.AlterField(
            model_name='resume',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resume', to=settings.AUTH_USER_MODEL, verbose_name='회원'),
        ),
    ]
