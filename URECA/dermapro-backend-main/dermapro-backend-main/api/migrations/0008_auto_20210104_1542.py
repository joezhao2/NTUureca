# Generated by Django 2.2.15 on 2021-01-04 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0007_riskquestion_userriskquestion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.CharField(max_length=200)),
                ('point', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SkinQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='UserSkinQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Options')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.SkinQuestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='options',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.SkinQuestion'),
        ),
    ]
