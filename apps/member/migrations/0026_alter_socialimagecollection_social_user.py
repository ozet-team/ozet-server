# Generated by Django 3.2.6 on 2022-05-13 19:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0025_socialimagecollection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialimagecollection',
            name='social_user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='image_collection', to='member.usersocial', verbose_name='선택된 이미지 목록'),
        ),
    ]