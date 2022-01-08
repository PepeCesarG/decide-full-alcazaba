from django.contrib import admin
from django.utils import timezone
from django import forms
from census.models import Census

 
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

from .models import QuestionOption
from .models import Question
from .models import Voting

from .filters import StartedFilter

import datetime

PROVINCIAS = [
    ('', 'Seleccionar provincia...'),
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

def censusName(inclList, exclList):
#    Crear nombre para el censo
    inclList.sort()
    exclList.sort()
    name = 'Con: '
    for c in inclList:
        name = name + c + '|'
    name = name[:-1]
    name = name + ' Sin: '
    for c in exclList:
        name = name + c + '|'
    name = name[:-1]
    logging.debug("El censo a usar será: " + name)
    return name

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption

class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]

class VotingAdminForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = "__all__"
        
    incl_census = forms.ModelMultipleChoiceField(queryset=Census.objects.exclude(name__in=[provincia[0] for provincia in PROVINCIAS]).exclude(name__contains='Con: '), label="Inclusive Census", to_field_name="name", required=False)
    excl_census = forms.ModelMultipleChoiceField(queryset=Census.objects.exclude(name__in=[provincia[0] for provincia in PROVINCIAS]).exclude(name__contains='Con: '), label="Exclusive Census", to_field_name="name", required=False)
        
    location = forms.ChoiceField(widget=forms.Select, choices=PROVINCIAS, required=False)
    
    

class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally ]
    
    form = VotingAdminForm
    
    def save_related(self, request, form, formsets, change):
        voting_id = form.instance.id
        logging.debug("Voting ID: "+ str(voting_id))
        
        location = request.POST.get("location")
        name = request.POST.get("name")
        
        voting = Voting.objects.get(name=name)
        
        #Debemos quitar la votacion de todos los censos en los que estuviera previamente
        all_census = Census.objects.all()
        for c in all_census:
            if voting in c.voting_ids.all():
                voting_ids = c.voting_ids.exclude(name=name)
                c.voting_ids.set(voting_ids)
                c.save()
        
        excl_censuses = request.POST.getlist("excl_census")
        excl_voters = []
        incl_censuses = request.POST.getlist("incl_census")
        incl_voters = []
        
        censo_provincia = None
        
        if location == '':
            logging.debug("No se ha seleccionado provincia")
        else:
            logging.debug("Se ha seleccionado la provincia de " + location)
            try:
                censo_provincia = Census.objects.get(name=location)
            except:
                censo_provincia = Census(name = location)
                censo_provincia.save()
            incl_censuses.append(censo_provincia.name)
        
        
        
        if len(excl_censuses)==0:
            votacion_a_añadir = Voting.objects.get(id=voting_id)
            for c in incl_censuses:
                censo = Census.objects.get(name=c)
                votaciones_existentes = censo.voting_ids.all()
                if votacion_a_añadir not in votaciones_existentes:
                    censo.voting_ids.add(Voting.objects.get(id=voting_id))
        else:
            census_name = censusName(incl_censuses, excl_censuses)
            try:
                final_census = Census.objects.get(name=census_name)
                votaciones_existentes = final_census.voting_ids.all()
                votacion_a_añadir = Voting.objects.get(id=voting_id)
                if votacion_a_añadir not in votaciones_existentes:
                    final_census.voting_ids.add(votacion_a_añadir)
            except:
                final_census = Census(name=census_name)
                final_census.save()
            
                #votantes de los censos inclusivos
                logging.debug("Añadiendo censos inclusivos")
                for c in incl_censuses:
                    census = Census.objects.get(name=c)
                    logging.debug("Censo: " + str(census))
                    incl_voters += census.voter_ids.all()
                incl_voters = set(incl_voters)
                #votantes de los censos exclusivos
                logging.debug("Añadiendo censos exclusivos")
                for c in excl_censuses:
                    census = Census.objects.get(name=c)
                    logging.debug("Censo: " + str(census))
                    excl_voters += census.voter_ids.all()
                excl_voters = set(excl_voters)
                
                voters = list(incl_voters)
                for voter in excl_voters:
                    if voter in voters:
                        voters.remove(voter)
                    
                for voter in voters:
                    final_census.voter_ids.add(voter)
                final_census.voting_ids.add(Voting.objects.get(id=voting_id))
                final_census.save()
              
        super(VotingAdmin, self).save_related(request, form, formsets, change)


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
