# Generated by Django 3.2.6 on 2022-01-09 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0006_alter_announcement_external_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='shop_location',
            field=models.CharField(default='', max_length=256, verbose_name='지점 주소'),
            preserve_default=False,
        ),
    ]