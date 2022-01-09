# Generated by Django 2.0 on 2021-12-28 19:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0008_auto_20211219_1809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='census',
            name='voter_ids',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='census',
            name='voting_ids',
            field=models.ManyToManyField(blank=True, to='voting.Voting'),
        ),
    ]
