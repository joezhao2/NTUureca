from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Album, Image, SampleImage, LesionQuestion, ImageLesionQuestion, LesionQuestion, RiskQuestion, UserRiskQuestion, SkinQuestion, Options, UserSkinQuestion, BodyParts, UserBodyParts
from dermaproBE.settings import BASE_DIR

from django.core.files.base import ContentFile
import base64
import six
import uuid
import imghdr
import os

class CreateUserSerializer(serializers.ModelSerializer):
	username = serializers.CharField()
	password = serializers.CharField(write_only=True, style={'input_type': 'password'})
	
	class Meta:
		model = get_user_model()
		fields = ('username', 'password', 'first_name', 'last_name')
		write_only_fields = ('password')
		read_only_fields = ('is_staff', 'is_superuser', 'is_active',)

	def create(self, validated_data):
		user = super(CreateUserSerializer, self).create(validated_data)
		user.set_password(validated_data['password'])
		user.save()
		return user

class Base64ImageField(serializers.ImageField):
	def to_internal_value(self, data):
		# Check if this is a base64 string
		if isinstance(data, six.string_types):
			# Check if the base64 string is in the "data:" format
			if 'data:' in data and ';base64,' in data:
				# Break out the header from the base64 content
				header, data = data.split(';base64,')
			# Try to decode the file. Return validation error if it fails.
			try:
				decoded_file = base64.b64decode(data)
			except TypeError:
				self.fail('invalid_image')
			# Generate file name:
			file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
			# Get the file name extension:
			file_extension = self.get_file_extension(file_name, decoded_file)
			complete_file_name = "%s.%s" % (file_name, file_extension, )
			data = ContentFile(decoded_file, name=complete_file_name)
		return super(Base64ImageField, self).to_internal_value(data)

	def get_file_extension(self, file_name, decoded_file):
		extension = imghdr.what(file_name, decoded_file)
		extension = "jpg" if extension == "jpeg" else extension
		return extension

class CreateImageSerializer(serializers.HyperlinkedModelSerializer):
	image = Base64ImageField(max_length=None, use_url=True,)
	album_id = serializers.IntegerField()
	comments = serializers.CharField(allow_blank=True)

	class Meta:
		model = Image
		fields = ('id','image', 'album_id', 'created_at', 'updated_at', 'comments')
	
	def create(self, validated_data):
		album = Album.objects.get(pk=validated_data["album_id"])
		image_object = Image.objects.create(**validated_data, album=album)
		return image_object

class CreateAlbumSerializer(serializers.ModelSerializer):
	user = serializers.HiddenField(default=serializers.CurrentUserDefault())
	images = CreateImageSerializer(many=True, read_only=True, source='image_set')
	
	class Meta:
		model = Album
		fields = ('id','title', 'user', 'created_at', 'updated_at', 'images', 'next_reminder', 'reminder_frequency')

class UpdateAlbumSerializer(serializers.ModelSerializer):
	reminder_frequency = serializers.IntegerField()
	next_reminder = serializers.DateField(allow_null=True)	
	class Meta:
		model = Album
		fields = ('id','title', 'created_at', 'updated_at','next_reminder', 'reminder_frequency')
	
	def update(self, instance, validated_data):
		print(validated_data)
		instance.reminder_frequency = validated_data.get("reminder_frequency", instance.reminder_frequency)
		instance.next_reminder = validated_data.get("next_reminder", instance.next_reminder)
		instance.save()
		return instance

class LesionQuestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = LesionQuestion
		fields = ('id', 'question', 'points', 'has_image')

class ImageLesionQuestionSerializer(serializers.ModelSerializer):
	question_id = serializers.IntegerField()
	image_id = serializers.IntegerField()
	answer = serializers.BooleanField()
	
	class Meta:
		model = ImageLesionQuestion
		fields = ('id', 'image_id', 'question_id', 'answer')
	
	def create(self, validated_data):
		question =  LesionQuestion.objects.get(pk=validated_data["question_id"])
		image = Image.objects.get(pk=validated_data["image_id"])
		image_lesion_question = ImageLesionQuestion.objects.create(**validated_data, question=question, image=image)
		return image_lesion_question
	
class RiskQuestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = RiskQuestion
		fields = ('id', 'question')

class UserRiskQuestionSerializer(serializers.ModelSerializer):
	user_id = serializers.IntegerField()
	question_id = serializers.IntegerField()
	answer = serializers.BooleanField()
	class Meta:
		model = UserRiskQuestion
		fields = ('id', 'question_id', 'user_id', 'answer')
	
	def create(self, validated_data):
		question = RiskQuestion.objects.get(pk=validated_data["question_id"])
		user = get_user_model().objects.get(pk=validated_data["user_id"])
		user_risk_question = UserRiskQuestion.objects.create(**validated_data, question=question, user=user)
		return user_risk_question
	
	def update(self, instance, validated_data):
		instance.answer = validated_data.get("answer", instance.answer)
		instance.save()
		return instance

class OptionsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Options
		fields = ('id', 'option', 'point')

class SkinQuestionSerializer(serializers.ModelSerializer):
	options_set = OptionsSerializer(many=True, read_only=True)
	class Meta:
		model = SkinQuestion
		fields = ('id', 'question', 'options_set')


class UserSkinQuestionSerializer(serializers.ModelSerializer):
	user_id = serializers.IntegerField()
	question_id = serializers.IntegerField()
	option_id = serializers.IntegerField()
	class Meta:
		model = UserRiskQuestion
		fields = ('id', 'question_id', 'user_id', 'option_id')

	def create(self, validated_data):
		question = SkinQuestion.objects.get(pk=validated_data["question_id"])
		user = get_user_model().objects.get(pk=validated_data["user_id"])
		option = Options.objects.get(pk=validated_data["option_id"])
		user_skin_question = UserSkinQuestion.objects.create(**validated_data, question=question, user=user, option=option)
		return user_skin_question
	
	def update(self, instance, validated_data):
		new_option = Options.objects.get(pk=validated_data.get("option_id"))
		instance.option = new_option
		instance.save()
		return instance

class BodyPartsSerializer(serializers.ModelSerializer):
	name = serializers.CharField()
	category = serializers.CharField()

	class Meta:
		model = BodyParts
		fields = ('id', 'name', 'category')


class UserBodyPartsSerializer(serializers.ModelSerializer):
	user_id = serializers.IntegerField()
	body_part_id = serializers.IntegerField()
	image = Base64ImageField(max_length=None, use_url=True,)
	
	class Meta:
		model = UserBodyParts
		fields = ('id', 'user_id', 'body_part_id', 'image')
	
	def create(self, validated_data):
		user = get_user_model().objects.get(pk=validated_data["user_id"])
		body_part = BodyParts.objects.get(pk=validated_data["body_part_id"])
		user_body_part = UserBodyParts.objects.create(**validated_data, user=user, body_part=body_part)
		return user_body_part

	def update(self, instance, validated_data):
		instance.image = validated_data.get("image", instance.image)
		instance.save()
		return instance
	