# Generated by Django 3.2.6 on 2022-01-29 13:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0019_usertoken_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('user_key', models.CharField(blank=True, default=None, max_length=50, null=True, verbose_name='SNS')),
            ],
            options={
                'verbose_name': '회원 SNS',
                'verbose_name_plural': '회원 SNS 목록',
                'db_table': 'member_user_social',
            },
        ),
        migrations.CreateModel(
            name='UserSocialToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('token', models.CharField(max_length=255, unique=True, verbose_name='토큰')),
                ('type', models.CharField(choices=[('refresh', 'REFRESH'), ('access', 'ACCESS')], default='access', max_length=20, verbose_name='토큰 형태')),
                ('status', models.CharField(choices=[('used', '유효함'), ('expire', '만료됨')], default='used', max_length=20, verbose_name='유효 상태')),
            ],
            options={
                'verbose_name': '회원 토큰',
                'verbose_name_plural': '회원 토큰 목록',
                'db_table': 'member_user_social_token',
            },
        ),
        migrations.DeleteModel(
            name='UserSNS',
        ),
        migrations.AddField(
            model_name='usersocial',
            name='token',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='token_set', to='member.usersocialtoken', verbose_name='소셜 토큰'),
        ),
        migrations.AddField(
            model_name='usersocial',
            name='user_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sns_set', to='member.userprofile', verbose_name='회원 프로필'),
        ),
    ]