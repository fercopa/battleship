from django.contrib import admin
from . import models

admin.site.register(models.Room)
admin.site.register(models.Player)
admin.site.register(models.Table)
admin.site.register(models.Boat)
admin.site.register(models.Cell)

