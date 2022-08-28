from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token
from .views import (CreateUserAPIView, LogoutUserAPIView, PredictImage, CreateAlbum, 
GetAlbums, SaveImage, GetAlbumImages, GetNearestHospital, GetLesionQuestions, GetLesionAnswers, 
GetRiskQuestions, SaveUserRiskQuestion, GetUserRiskAnswers, GetSkinQuestion, SaveUserSkinQuestion, 
GetUserSkinAnswers, GetUserBodyParts, GetBodyParts, SaveUserBodyPartsImage, GetBodyPart, SetReminder, GetReminder)
 
urlpatterns = [
	url(r'^auth/login/$',	obtain_auth_token, name='auth_user_login'),
	url(r'^auth/register/$', CreateUserAPIView.as_view(), name='auth_user_create'),
	url(r'^auth/logout/$', LogoutUserAPIView.as_view(), name='auth_user_logout'),
	url(r'^predict/$', PredictImage.as_view(), name='scan_predict_image'),
	url(r'^album/create/$', CreateAlbum.as_view(), name='album_create'),
	url(r'^album/get/$', GetAlbums.as_view(), name='album_get'),
	url(r'^album/save/$', SaveImage.as_view(), name='album_save'),
	url(r'^images/get/(?P<album_id>[0-9]+)$', GetAlbumImages.as_view(), name='album_images'),
	url(r'^hospitals/get$', GetNearestHospital.as_view(), name='hospital_info'),
	url(r'^lesion-questions/$', GetLesionQuestions.as_view(), name='lesion_questions'),
	url(r'^lesion-answers/(?P<image_id>[0-9]+)$', GetLesionAnswers.as_view(), name='lesion_answers'),
	url(r'^risk-questions/$', GetRiskQuestions.as_view(), name='risk_questions'),
	url(r'^risk-answers/$', SaveUserRiskQuestion.as_view(), name='risk_answers'),	
	url(r'^risk-answers/get$', GetUserRiskAnswers.as_view(), name='risk_answers_get'),
	url(r'^skin-question/$', GetSkinQuestion.as_view(), name="skin_question"),
	url(r'^skin-answers/$', SaveUserSkinQuestion.as_view(), name='skin_answers'),
	url(r'^skin-answers/get$', GetUserSkinAnswers.as_view(), name='skin_answers_get'),
	url(r'^body-parts/get$', GetBodyParts.as_view(), name='body_parts_get'),
	url(r'^user-body-parts/(?P<body_part_id>[0-9]+)$', GetBodyPart.as_view(), name='body_part_get'),
	url(r'^user-body-parts/get$', GetUserBodyParts.as_view(), name='user_body_parts_get'),	
	url(r'^user-body-parts/save$', SaveUserBodyPartsImage.as_view(), name='user_body_parts_save'),
	url(r'^set-reminder/$', SetReminder.as_view(), name='set_reminder'),
	url(r'^get-reminder/$', GetReminder.as_view(), name='set_reminder'),
	url(r'^del_image/(?P<pk>[0-9]+)$', GetAlbumImages.as_view(), name='album_images_del'),
	url(r'^del_album/(?P<pk>[0-9]+)$', GetAlbums.as_view(), name='album_del'),
]