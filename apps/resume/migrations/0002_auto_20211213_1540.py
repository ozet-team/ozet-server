# Generated by Django 3.2.6 on 2021-12-13 15:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resume', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='resume_set', to='member.user', verbose_name='회원'),
            preserve_default=False,
        ),
        migrations.AlterModelTable(
            name='resume',
            table='member_user_resume',
        ),
    ]
