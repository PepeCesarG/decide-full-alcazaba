from django.contrib import admin
from django.utils import timezone
from django import forms

from .models import QuestionOption
from .models import Question
from .models import Voting
from census.models import Census

from .filters import StartedFilter

PROVINCIAS = [
    ('Alava', 'Álava'),
    ('Albacete', 'Albacete'),
    ('Alicante', 'Alicante'),
    ('Almeria', 'Almería'),
    ('Asturias', 'Asturias'),
    ('Avila', 'Ávila'),
    ('Badajoz', 'Badajoz'),
    ('Barcelona', 'Barcelona'),
    ('Burgos', 'Burgos'),
    ('Caceres', 'Cáceres'),
    ('Cadiz', 'Cádiz'),
    ('Cantabria', 'Cantabria'),
    ('Castellon', 'Castellón'),
    ('Ciudad Real', 'Ciudad Real'),
    ('Cordoba', 'Córdoba'),
    ('Cuenca', 'Cuenca'),
    ('Gerona', 'Gerona'),
    ('Granada', 'Granada'),
    ('Guadalajara', 'Guadalajara'),
    ('Guipuzcoa', 'Guipúzcoa'),
    ('Huelva', 'Huelva'),
    ('Huesca', 'Huesca'),
    ('Islas Baleares', 'Islas Baleares'),
    ('Jaen', 'Jaén'),
    ('La Coruna', 'La Coruña'),
    ('La Rioja', 'La Rioja'),
    ('Las Palmas', 'Las Palmas'),
    ('Leon', 'León'),
    ('Lerida', 'Lérida'),
    ('Lugo', 'Lugo'),
    ('Madrid', 'Madrid'),
    ('Malaga', 'Málaga'),
    ('Murcia', 'Murcia'),
    ('Navarra', 'Navarra'),
    ('Orense', 'Orense'),
    ('Palencia', 'Palencia'),
    ('Pontevedra', 'Pontevedra'),
    ('Salamanca', 'Salamanca'),
    ('Santa Cruz de Tenerife', 'Santa Cruz de Tenerife'),
    ('Segovia', 'Segovia'),
    ('Sevilla', 'Sevilla'),
    ('Soria', 'Soria'),
    ('Tarragona', 'Tarragona'),
    ('Teruel', 'Teruel'),
    ('Toledo', 'Toledo'),
    ('Valencia', 'Valencia'),
    ('Valladolid', 'Valladolid'),
    ('Vizcaya', 'Vizcaya'),
    ('Zamora', 'Zamora'),
    ('Zaragoza', 'Zaragoza'),
]

def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]

class VotingAdminForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = "__all__"
        
    location = forms.ChoiceField(widget=forms.Select, choices=PROVINCIAS)
    
    def insert_in_census(self):
        if self.cleaned_data["location"] == "":
            print("No se ha seleccionado provincia")
            return
        else:
            print("Se ha seleccionado la provincia de " + self.cleaned_data["location"])
            censo = Census.objects.get(name=self.cleaned_data["location"])
            return
    


class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally ]
    
    form = VotingAdminForm


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
