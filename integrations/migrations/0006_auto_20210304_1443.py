# Generated by Django 3.0.5 on 2021-03-04 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0005_spotify_user_info_expires_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiinfo',
            name='api_endpoint',
            field=models.CharField(default='N/A', max_length=2083),
        ),
        migrations.AlterField(
            model_name='apiinfo',
            name='client_id',
            field=models.CharField(default='N/A', max_length=100),
        ),
    ]