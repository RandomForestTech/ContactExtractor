from django.contrib import admin
from nameextractor.models import *

# Register your models here.

admin.site.register(PersonDetails)
admin.site.register(Company)
admin.site.register(Role)
admin.site.register(UploadedFile)

