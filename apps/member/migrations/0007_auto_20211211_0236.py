# Generated by Django 3.2.6 on 2021-12-11 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0006_auto_20211211_0219'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertoken',
            name='status',
            field=models.CharField(choices=[('used', '유효함'), ('expire', '만료됨')], default='used', max_length=20, verbose_name='유효 상태'),
        ),
        migrations.AlterField(
            model_name='userpasscodeverify',
            name='status',
            field=models.CharField(choices=[('used', '완료된 검증'), ('pending', '검증 대기중'), ('expire', '만료됨')], default='pending', max_length=20, verbose_name='인증 상태'),
        ),
    ]
