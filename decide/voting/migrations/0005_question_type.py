# Generated by Django 2.0 on 2021-12-19 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_voting_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('O', 'Options'), ('B', 'Binary')], default='O', max_length=1),
        ),
    ]
