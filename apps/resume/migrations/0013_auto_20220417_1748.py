# Generated by Django 3.2.6 on 2022-04-17 17:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resume', '0012_resume_pdf_file'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='academicbackground',
            options={'verbose_name': '학력'},
        ),
        migrations.AlterModelOptions(
            name='career',
            options={'verbose_name': '커리어'},
        ),
        migrations.AlterModelOptions(
            name='certificate',
            options={'verbose_name': '자격증'},
        ),
        migrations.AlterModelOptions(
            name='militaryservice',
            options={'verbose_name': '병역'},
        ),
        migrations.AlterField(
            model_name='academicbackground',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='academic_set', to='resume.resume', verbose_name='이력서'),
        ),
        migrations.AlterField(
            model_name='career',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='career_set', to='resume.resume', verbose_name='이력서'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificate_set', to='resume.resume', verbose_name='이력서'),
        ),
        migrations.AlterField(
            model_name='militaryservice',
            name='resume',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='military', to='resume.resume', verbose_name='이력서'),
        ),
        migrations.AlterField(
            model_name='resume',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resume', to=settings.AUTH_USER_MODEL, verbose_name='이력서'),
        ),
        migrations.CreateModel(
            name='PictureCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('image_id', models.CharField(max_length=20, null=True)),
                ('url', models.URLField()),
                ('is_active', models.BooleanField(default=True)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collection_set', to='resume.resume', verbose_name='이력서')),
            ],
            options={
                'verbose_name': '사진 모음',
                'db_table': 'member_user_resume_picture_collection',
            },
        ),
    ]
