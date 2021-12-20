from django.contrib import admin

from .models import Census


class CensusAdmin(admin.ModelAdmin):
    list_display = ('name', 'votings', 'voters')
    list_filter = ('name', )
    readonly_fields=('voting_ids',)

    search_fields = ('name', )

admin.site.register(Census, CensusAdmin)
