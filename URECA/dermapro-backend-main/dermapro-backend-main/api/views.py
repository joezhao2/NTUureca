from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.views import APIView
from datetime import datetime
from datetime import timedelta
from django.http import Http404

import base64
from io import BytesIO
from datetime import date
import json
import requests
import os

from api.serializers import CreateUserSerializer, CreateAlbumSerializer, CreateImageSerializer, LesionQuestionSerializer, ImageLesionQuestionSerializer, RiskQuestionSerializer, UserRiskQuestionSerializer, SkinQuestionSerializer, UserSkinQuestionSerializer, BodyPartsSerializer, UserBodyPartsSerializer, UpdateAlbumSerializer
from .apps import ApiConfig

from .utils import model_predict
from .models import Album, Image, LesionQuestion, ImageLesionQuestion, RiskQuestion, UserRiskQuestion, SkinQuestion, Options, UserSkinQuestion, UserBodyParts, BodyParts

"""
prediction_class = {
	0: "Actinic Keratoses",
	1: "Basal Cell Carcinoma",
	2: "Benign Keratoses",
	3: "Dermatofibroma",
	4: "Melanocytic Nevus",
	5: "Vascular Lesion",
	6: "Melanoma"
}
"""

prediction_class = {
    0: "Potentially Harmless Lesion",
    1: "Harmful Lesion"
}


class CreateUserAPIView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            # We create a token than will be used for future auth
            token = Token.objects.create(user=serializer.instance)
            token_data = {"token": token.key}
            return Response(
                {**serializer.data, **token_data},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as error:
            print(error)
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutUserAPIView(APIView):
    queryset = get_user_model().objects.all()

    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class PredictImage(APIView):
    def post(self, request, format=None):
        image = request.data['image']
        confidence, prediction = model_predict(ApiConfig.model, image)
        print("PREDICTION:")
        print(prediction_class[prediction])
        return Response(
            {
                'confidence': confidence*100,
                'prediction': prediction_class[prediction]
            },
            status=status.HTTP_200_OK)


class GetAlbums(APIView):
    def get_object(self, pk):
        try:
            return Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        albums = Album.objects.filter(user=request.user)
        serialized_albums = [CreateAlbumSerializer(instance=o) for o in albums]
        serializer = [s.data for s in serialized_albums]
        return Response({
            "albums": serializer
        },
            status=status.HTTP_200_OK)

    def delete(self, request, pk):
        album = self.get_object(pk)
        album.delete()
        return(Response(status=status.HTTP_204_NO_CONTENT))


class CreateAlbum(CreateAPIView):
    serializer_class = CreateAlbumSerializer

    def create(self, request, *args, **kwargs):
        first_serializer = self.get_serializer(data=request.data)
        if first_serializer.is_valid():
            self.perform_create(first_serializer)
        else:
            print(first_serializer.errors)
            return Response(first_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sec_data = {
            "album_id": first_serializer.data["id"],
            "image": request.data["image"],
            "comments": request.data["comments"]
        }
        sec_serializer = CreateImageSerializer(data=sec_data)
        if sec_serializer.is_valid():
            sec_serializer.save()
        else:
            Album.objects.get(pk=first_serializer.data["id"]).delete()
            print(sec_serializer.errors)
            return Response(sec_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        third_data = [{
            "question_id": a["id"],
            "image_id": sec_serializer.data["id"],
            "answer": a["answer"]
        } for a in request.data["answers"]]

        third_serializer = [ImageLesionQuestionSerializer(
            data=d) for d in third_data]
        for t in third_serializer:
            if t.is_valid():
                t.save()
            else:
                # Rollback and Delete Image
                Image.objects.get(pk=sec_serializer.data["id"]).delete()
                Album.objects.get(pk=first_serializer.data["id"]).delete()
                print(third_serializer.errors)
                return Response(third_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "album": first_serializer.data
            },
            status=status.HTTP_201_CREATED,
        )


class SaveImage(CreateAPIView):
    serializer_class = CreateImageSerializer

    def create(self, request, *args, **kwargs):
        # Save Image
        first_serializer = CreateImageSerializer(data=request.data)
        if first_serializer.is_valid():
            first_serializer.save()
        else:
            print(first_serializer.errors)
            return Response(first_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = [{
                "question_id": a["id"],
                "image_id": first_serializer.data["id"],
                "answer": a["answer"]
                } for a in request.data["answers"]]

        # Save Image Question Answers
        sec_serializer = [ImageLesionQuestionSerializer(data=d) for d in data]
        for s in sec_serializer:
            if s.is_valid():
                s.save()
            else:
                # Rollback and Delete Image
                Image.objects.get(pk=first_serializer.data["id"]).delete()
                return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(first_serializer.data, status=status.HTTP_201_CREATED)


class GetNearestHospital(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        PARAMS = {'apikey': 'b8A8CwMH4unW1FAYHjZfEaXCv_aXPmBVRfwgQmrM4SM'}

        latitude = request.GET.get("lat", None)
        longitude = request.GET.get("long", None)

        if latitude == None or longitude == None:
            current_location_response = requests.get(
                "https://geocode.search.hereapi.com/v1/geocode?q=Singapore", params=PARAMS)
            current_location_data = current_location_response.json()

            latitude = current_location_data['items'][0]['position']['lat']
            longitude = current_location_data['items'][0]['position']['lng']
        response = requests.get(
            "https://discover.search.hereapi.com/v1/discover?at={},{}&in=countryCode:SGP&q=hospital&lang=en-US".format(latitude, longitude), params=PARAMS)
        data = json.loads(response.text)
        return Response({
            "data": data
        },
            status=status.HTTP_200_OK
        )


class GetAlbumImages(APIView):
    def get_im_object(self, pk):
        try:
            return Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            raise Http404

    def get(self, request, album_id):
        album = Album.objects.get(pk=album_id)
        images = Image.objects.filter(album=album)
        serialized_images = [CreateImageSerializer(i) for i in images]
        serializer = [s.data for s in serialized_images]
        return Response({
            "images": serializer
        },
            status=status.HTTP_200_OK)

    def delete(self, request, pk):
        image = self.get_im_object(pk)
        image.delete()
        return(Response(status=status.HTTP_204_NO_CONTENT))


class GetLesionQuestions(APIView):
    def get(self, request):
        questions = LesionQuestion.objects.all().order_by("id")
        serialized_questions = [LesionQuestionSerializer(q) for q in questions]
        serializer = [q.data for q in serialized_questions]
        return Response({
            "questions": serializer
        },
            status=status.HTTP_200_OK)


class GetLesionAnswers(APIView):
    def get(self, request, image_id):
        image = Image.objects.get(pk=image_id)
        answers = ImageLesionQuestion.objects.filter(image=image)
        serialized_answers = [
            ImageLesionQuestionSerializer(a) for a in answers]
        serializer = [s.data for s in serialized_answers]
        return Response({
            "answers": serializer,
        },
            status=status.HTTP_200_OK)


class GetRiskQuestions(APIView):
    def get(self, request):
        questions = RiskQuestion.objects.all()
        serialized_questions = RiskQuestionSerializer(questions, many=True)
        serializer = serialized_questions.data[:]
        return Response({
            "questions": serializer
        },
            status=status.HTTP_200_OK)


class SaveUserRiskQuestion(CreateAPIView):
    def create(self, request, *args, **kwargs):
        data = [{
                "question_id": i["id"],
                "answer": i["answer"],
                "user_id": request.user.id
                } for i in request.data["answers"]]

        retrieved_answers = UserRiskQuestion.objects.filter(user=request.user)
        if len(retrieved_answers) > 0:
            # Perform Update if data already exists
            serialized_answer = [UserRiskQuestionSerializer(
                a, data=data[i]) for i, a in enumerate(retrieved_answers)]
            for s in serialized_answer:
                if s.is_valid():
                    s.save()
                else:
                    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = [s.data for s in serialized_answer]
            return Response(serializer, status=status.HTTP_201_CREATED)
        else:
            # Perform create if data has not existed
            serialized_answer = [
                UserRiskQuestionSerializer(data=d) for d in data]
            for s in serialized_answer:
                if s.is_valid():
                    s.save()
                else:
                    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = [s.data for s in serialized_answer]
            return Response(serializer, status=status.HTTP_201_CREATED)


class GetUserRiskAnswers(APIView):
    def get(self, request):
        user = request.user
        answers = UserRiskQuestion.objects.filter(user=user)
        serialized_answers = UserRiskQuestionSerializer(answers, many=True)
        serializer = serialized_answers.data[:]
        return Response(serializer, status=status.HTTP_201_CREATED)


class GetSkinQuestion(APIView):
    def get(self, request):
        questions = SkinQuestion.objects.all()
        serialized_questions = SkinQuestionSerializer(questions, many=True)
        serializer = serialized_questions.data[:]
        return Response({
            "questions": serializer
        },
            status=status.HTTP_200_OK)


class SaveUserSkinQuestion(CreateAPIView):
    def create(self, request, *args, **kwargs):
        data = [{
                "question_id": i["id"],
                "option_id": i["option_id"],
                "user_id": request.user.id
                } for i in request.data["answers"]]

        retrieved_answers = UserSkinQuestion.objects.filter(
            user=request.user).order_by('question')
        if len(retrieved_answers) > 0:
            # Perform update if data already exists
            serialized_answer = [UserSkinQuestionSerializer(
                a, data=data[i]) for i, a in enumerate(retrieved_answers)]
            for s in serialized_answer:
                if s.is_valid():
                    s.save()
                else:
                    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer = [s.data for s in serialized_answer]
            return Response(serializer, status=status.HTTP_201_CREATED)
        else:
            # Perform create if data has not existed
            serialized_answer = [
                UserSkinQuestionSerializer(data=d) for d in data]
            for s in serialized_answer:
                if s.is_valid():
                    s.save()
                else:
                    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer = [s.data for s in serialized_answer]
            return Response(serializer, status=status.HTTP_201_CREATED)


class GetUserSkinAnswers(APIView):
    def get(self, request):
        user = request.user
        answers = UserSkinQuestion.objects.filter(user=user)
        serialized_answers = UserSkinQuestionSerializer(answers, many=True)
        data = serialized_answers.data[:]
        return Response(data, status=status.HTTP_200_OK)


class GetBodyParts(APIView):
    def get(self, request):
        parts_list = BodyParts.objects.all()
        serialized_parts = BodyPartsSerializer(parts_list, many=True)
        serializer = serialized_parts.data[:]
        return Response(serializer, status=status.HTTP_200_OK)


class GetUserBodyParts(APIView):
    def get(self, request):
        user = request.user
        body_parts = UserBodyParts.objects.filter(
            user=user).prefetch_related('body_part')

        serialized_user_parts = UserBodyPartsSerializer(body_parts, many=True)
        first_serializer = serialized_user_parts.data

        serialized_body_parts = [BodyPartsSerializer(
            b.body_part) for b in body_parts]
        second_serializer = [s.data for s in serialized_body_parts]
        data = {
            "user_body_part": first_serializer,
            "body_parts": second_serializer,
        }
        return Response(data, status=status.HTTP_200_OK)


class GetBodyPart(APIView):
    def get(self, request, body_part_id):
        user = request.user
        body_part = BodyParts.objects.get(pk=body_part_id)
        user_body_part = UserBodyParts.objects.filter(
            user=user, body_part=body_part)
        if len(user_body_part) > 0:
            serialized = UserBodyPartsSerializer(user_body_part[0])
            return Response(serialized.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_200_OK)


class SaveUserBodyPartsImage(CreateAPIView):
    serializer_class = UserBodyPartsSerializer

    def create(self, request, *args, **kwargs):
        # Save Image
        data = {
            "user_id": request.user.id,
            "body_part_id": request.data["body_part_id"],
            "image": request.data["image"],
        }
        body_part = BodyParts.objects.get(pk=request.data["body_part_id"])
        retrieved = UserBodyParts.objects.filter(
            user=request.user, body_part=body_part)
        if len(retrieved) > 0:
            # Perform Update if data already exists
            serialized_answer = [UserBodyPartsSerializer(
                a, data=data) for i, a in enumerate(retrieved)]
            for s in serialized_answer:
                if s.is_valid():
                    s.save()
                else:
                    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = [s.data for s in serialized_answer]
            return Response(serializer, status=status.HTTP_201_CREATED)
        else:
            first_serializer = UserBodyPartsSerializer(data=data)
            if first_serializer.is_valid():
                first_serializer.save()
            else:
                return Response(first_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(first_serializer.data, status=status.HTTP_201_CREATED)


class GetReminder(APIView):
    def get(self, request):
        reminder_today = Album.objects.filter(
            user=request.user, next_reminder__lte=datetime.now().date())
        serialized = [UpdateAlbumSerializer(a) for a in reminder_today]
        serialized_data = [s.data for s in serialized]
        return Response(serialized_data, status=status.HTTP_200_OK)


class SetReminder(CreateAPIView):
    def create(self, request, *args, **kwargs):
        next_reminder = None
        if request.data["reminder_frequency"] is not 0:
            next_reminder = datetime.now(
            ) + timedelta(days=request.data["reminder_frequency"])
            next_reminder = next_reminder.date()
        album_to_modify = Album.objects.get(pk=request.data["album_id"])
        data = {
            "title": album_to_modify.title,
            "reminder_frequency": request.data["reminder_frequency"],
            "next_reminder": next_reminder,
        }
        serialized = UpdateAlbumSerializer(album_to_modify, data=data)
        if serialized.is_valid():
            serialized.save()
        else:
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serialized.data, status=status.HTTP_201_CREATED)
