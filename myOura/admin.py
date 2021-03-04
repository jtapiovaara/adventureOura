from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.forms import CheckboxSelectMultiple

from .models import Ourauser, Sportdays, Hqmessages


class OurauserAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    Sportdays.get_days_display.short_description = 'days'
    fieldsets = [
        ('Nimi', {'fields': ['firstname', 'lastname']}),
        ('Urheilupäivät, merkitse milloin teet rasittavaa urheilua 3 min tai kauemmin. '
         '0 = Maanantai ja siitä eteenpäin.', {'fields': ['sportdays']}),
        ('Kun urheilet, jossain vaiheessa suoritus on ns. Kova, esim. 4 minuutin jälkeen.', {'fields': ['tintensity']}),
        (_('Oura Tiedot'), {
            'classes': ('collapse',),
            'fields': (
                'username',
                'ourakey',
            ),
        }),
        # ('Oura Tiedot',  {'fields': ['username', 'ourakey']})
    ]

    list_display = ['firstname']


class HqmessagesAdmin(admin.ModelAdmin):
    list_display = ('shortdesc', 'meaning')


admin.site.register(Ourauser, OurauserAdmin)
admin.site.register(Sportdays)
admin.site.register(Hqmessages, HqmessagesAdmin)
