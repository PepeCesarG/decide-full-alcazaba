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

def censusName():
#    Crear nombre único para el censo
    current_time = datetime.datetime.now()
    name = 'V'+str(current_time.day)+'/'+str(current_time.month)+'/'+str(current_time.year)+'-'+str(current_time.minute)+str(current_time.second)
    logging.debug("Census ID: " + name)
    return name

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption


# class QuestionBinaryInLine(admin.TabularInline):
    # model = QuestionBinary


class QuestionAdmin(admin.ModelAdmin):
    # TODO: Crear javascript que cambie el valor del InLine
    inlines = [QuestionOptionInline]

class VotingAdminForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = "__all__"
        
    incl_census = forms.ModelMultipleChoiceField(queryset=Census.objects.exclude(name__in=[provincia[0] for provincia in PROVINCIAS]), label="Inclusive Census", to_field_name="name", required=False)
    excl_census = forms.ModelMultipleChoiceField(queryset=Census.objects.exclude(name__in=[provincia[0] for provincia in PROVINCIAS]), label="Exclusive Census", to_field_name="name", required=False)
        
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
        
        excl_censuses = request.POST.getlist("excl_census")
        excl_voters = []
        incl_censuses = request.POST.getlist("incl_census")
        incl_voters = []
#        Censo final con las personas que pueden votar
        final_census = Census.objects.create(name=censusName())
        final_census.save()
        
        if location == '':
            logging.debug("No se ha seleccionado provincia")
        else:
            logging.debug("Se ha seleccionado la provincia de " + location)
            try:
                censo = Census.objects.get(name=location)
                censo.save()
            except:
                censo = Census(name = location)
                censo.save()
#           añadir el censo de localidad a la lista de votantes de censos inclusivos
            incl_voters += censo.voter_ids.all()
#       votantes de los censos inclusivos
        logging.debug("Añadiendo censos inclusivos")
        for c in incl_censuses:
            census = Census.objects.get(name=c)
            logging.debug("Censo: " + str(census))
            incl_voters += census.voter_ids.all()
        incl_voters = set(incl_voters)
#        votantes de los censos exclusivos
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
                
#        borramos el censo anterior para que no se acumulen
        try:
            old_census = Census.objects.filter(voting_ids=voting).first()
            old_census.delete()
        except:
            pass
        
#        añadimos las relaciones con voting y voters al censo final
        for voter in voters:
            final_census.voter_ids.add(voter)
        final_census.voting_ids.add(Voting.objects.get(id=voting_id))
        final_census.save()
        
        
        super(VotingAdmin, self).save_related(request, form, formsets, change)


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
