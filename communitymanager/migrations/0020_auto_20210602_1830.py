# Generated by Django 2.1.15 on 2021-06-02 16:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communitymanager', '0019_merge_20210602_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='lecteurs',
            field=models.ManyToManyField(null=True, related_name='posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='lu',
            field=models.BooleanField(default=False),
        ),
    ]