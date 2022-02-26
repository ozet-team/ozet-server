# Generated by Django 3.2.6 on 2022-01-29 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0023_auto_20220129_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersocial',
            name='social',
            field=models.CharField(choices=[('instagram', '인스타그램')], default=None, max_length=20, verbose_name='소셜'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='usersocial',
            unique_together={('social', 'social_key')},
        ),
    ]