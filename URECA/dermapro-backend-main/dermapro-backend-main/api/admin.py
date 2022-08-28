from django.contrib import admin

from api.models import Album, Image, LesionQuestion,ImageLesionQuestion, RiskQuestion, UserRiskQuestion, SkinQuestion, Options, UserSkinQuestion, BodyParts, UserBodyParts, SampleImage

admin.site.register(Album)
admin.site.register(Image)
admin.site.register(LesionQuestion)
admin.site.register(ImageLesionQuestion)
admin.site.register(RiskQuestion)
admin.site.register(UserRiskQuestion)
admin.site.register(SkinQuestion)
admin.site.register(Options)
admin.site.register(UserSkinQuestion)
admin.site.register(BodyParts)
admin.site.register(UserBodyParts)
admin.site.register(SampleImage)

# Register your models here.
