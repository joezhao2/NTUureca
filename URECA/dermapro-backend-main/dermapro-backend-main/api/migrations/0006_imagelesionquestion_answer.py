# Generated by Django 2.2.15 on 2021-01-03 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_lesionquestion_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagelesionquestion',
            name='answer',
            field=models.BooleanField(default=False),
        ),
    ]
