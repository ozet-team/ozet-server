# Generated by Django 3.2.6 on 2021-12-18 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0003_announcement_external_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeetype',
            name='codename',
            field=models.CharField(default='', max_length=16),
            preserve_default=False,
        ),
    ]
