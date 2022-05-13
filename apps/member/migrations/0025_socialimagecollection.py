# Generated by Django 3.2.6 on 2022-05-13 19:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0024_auto_20220129_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialImageCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('collection_data', models.JSONField(default=dict, verbose_name='추가 정보')),
                ('social_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_collection', to='member.usersocial', verbose_name='선택된 이미지 목록')),
            ],
            options={
                'verbose_name': '소셜 이미지 컬렉션',
                'verbose_name_plural': '소셜 이미지 컬렉션 목록',
                'db_table': 'member_user_social_image_collection',
            },
        ),
    ]