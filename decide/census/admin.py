from django.contrib import admin

from .models import Census,Voter


class CensusAdmin(admin.ModelAdmin):
    list_display = ('name', 'votings', 'voters')
    list_filter = ('name', )

    search_fields = ('name', )

class VoterAdmin(admin.ModelAdmin):
    list_display = ('user','location','edad','genero')
admin.site.register(Census, CensusAdmin)
admin.site.register(Voter, VoterAdmin)
