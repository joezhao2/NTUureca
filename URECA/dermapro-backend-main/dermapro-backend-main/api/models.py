from django.db import models
from django.contrib.auth.models import User
import json
import datetime

# Create your models here.
class Album(models.Model):
	title = models.CharField(max_length=30)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	# if no reminders, set null
	next_reminder = models.DateField(null=True, blank=True)
	reminder_frequency = models.IntegerField(default=0)
	

class Image(models.Model):
	image = models.ImageField(upload_to="media/")
	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	comments = models.CharField(blank=True, max_length=10000, default="")

class LesionQuestion(models.Model):
	question = models.CharField(max_length=1000)
	points = models.IntegerField(default=1)
	has_image = models.BooleanField(default=False)

class ImageLesionQuestion(models.Model):
	image = models.ForeignKey(Image, on_delete=models.CASCADE)
	question = models.ForeignKey(LesionQuestion, on_delete=models.CASCADE)
	answer = models.BooleanField(default=False)

class RiskQuestion(models.Model):
	question = models.CharField(max_length=1000)

class UserRiskQuestion(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	question = models.ForeignKey(RiskQuestion, on_delete=models.CASCADE)
	answer = models.BooleanField(default=False)

class SkinQuestion(models.Model):
	question = models.CharField(max_length=1000)

class Options(models.Model):
	question = models.ForeignKey(SkinQuestion, on_delete=models.CASCADE)
	option = models.CharField(max_length=200)
	point = models.IntegerField()

class UserSkinQuestion(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	question = models.ForeignKey(SkinQuestion, on_delete=models.CASCADE)
	option = models.ForeignKey(Options, on_delete=models.CASCADE)

class BodyParts(models.Model):
	name = models.CharField(max_length=250)
	category = models.CharField(max_length=250)

class UserBodyParts(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	body_part = models.ForeignKey(BodyParts, on_delete=models.CASCADE)
	image = models.ImageField(upload_to="media/")

# TO DELETE AFTER APP IS COMPLETE
class SampleImage(models.Model):
	image = models.ImageField(upload_to="media/")


