import csv
from io import StringIO

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path
from .filters import StartedFilter

from django.http import HttpResponse
from django.contrib.auth.models import User
from voting.models import Voting
from .models import Census,Voter
import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

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

GENERO = [
    ('Hombre', 'Hombre'),
    ('Mujer', 'Mujer'),
    ('Otro','Otro')
]

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

class ExportCsv:
    def export_csv_call(self, request, queryset):
        meta = self.model._meta
        nombres_campos = [campo.name for campo in meta.fields]
        logging.debug(self.model.voters)
        logging.debug(queryset)
        respuesta = HttpResponse(content_type='text/csv')
        respuesta['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(respuesta, delimiter=';')
        primera_linea = 'id,name,votings,voters'
        writer.writerow([primera_linea])
        
        for obj in queryset:
            #Llamamos a la funcion de exportar el CSV
            id = getattr(obj, nombres_campos[0])
            name = getattr(obj, nombres_campos[1])
            votings = getattr(obj, 'voting_ids').all()
            votings_str = '['
            for voting in votings:
            #    votings_str += voting.name.split(':')[1].split('>')[0].trim()+','
                votings_str += str(voting) +':'
                logging.debug(votings_str)
            if(votings_str=="["):
                votings_str = votings_str+']'
            else:
                votings_str = votings_str[:-1]+']'
            voters = getattr(obj, 'voter_ids').all()
            voters_str = '['
            for voter in voters:
                voters_str += str(voter)+':'

                logging.debug(str(voter))
            if(voters_str=="["):
                voters_str = voters_str +']'
            else:
                voters_str = voters_str[:-1]+']'
            linea = str(id)+','+name+','+votings_str+','+voters_str
            fila = writer.writerow([linea])

        '''
        Se implementan para concenso con la importacion de censo que
        se anyadan en una lista separadas por ":" las distintas 
        votaciones y los distintos votantes en el caso de haber varios
        
        Se van a representar mensajes de error o confirmacion en funcion
        de importacion correcta o no.
        '''

        try:
            self.message_user(request, "Exportacion correcta", messages.SUCCESS)
            #En caso de que falle levantamos la excepcion:
        except Exception as e:
            print(e)
            self.message_user(request, "La exportacion no ha sido completada con exito", messages.ERROR)

        return respuesta
    export_csv_call.short_description = 'Exportar en csv los seleccionados'

class CensusAdmin(admin.ModelAdmin, ExportCsv):
    list_display = ('name', 'votings', 'voters')
    list_filter = ('name', )

    search_fields = ('name', )
    change_list_template = "entities/census_changelist.html"

    actions = ['export_csv_call']

    def get_urls(self):
        urls = super().get_urls()
        csv_url = [path('import-csv/', self.import_csv)]
        return csv_url + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            aux = csv_file.read()
            #Decodes file if encoded (normal use), not if not encoded (test use)
            csvf = StringIO(aux.decode()) if (type(aux) != type('str')) else StringIO(aux)
            reader = csv.reader(csvf, delimiter=',')
            try:
                #Allows rollback in case of exception while parsing CSVs
                with transaction.atomic():
                    next(reader)
                    for row in reader:
                        name = row[1]
                        votings = row[2][1:-1].split(":")
                        voters = row[3][1:-1].split(":")

                        census = Census(name=name)
                        census.save()

                        for nombre in votings:
                            voting = Voting.objects.filter(name = nombre).first()
                            if (voting):
                                census.voting_ids.add(voting)

                        for nombre in voters:
                            user = User.objects.filter(username = nombre).first()
                            voter = Voter.objects.filter(user = user).first()
                            if (voter):
                                census.voter_ids.add(voter)
                    
                self.message_user(request, "Your csv file has been imported successfully")
                #Redirects to census/census (list view)
                return redirect("..")
            except Exception as e:
                logging.warning(e)
                self.message_user(request, "Your csv file could not be imported", level = messages.ERROR)
                #Redirects to census/census/import-csv, which just reloads the same page
                return redirect(".")
                
        #If not accessed through a POST petition, load the CSV form view
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "csv_form.html", payload)

class VoterAdminForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = "__all__"
    edad = forms.IntegerField(required = True)    
    location = forms.ChoiceField(widget=forms.Select, choices=PROVINCIAS, required=False)
    genero = forms.ChoiceField(widget=forms.Select, choices=GENERO, required=False)

class VoterAdmin(admin.ModelAdmin):
    list_display = ('user','location','edad','genero')
    search_fields = ('user', )
    form = VoterAdminForm
    def save_related(self, request, form, formsets, change):
        location = request.POST.get("location")
        edad = request.POST.get("edad")
        genero = request.POST.get("genero")
        if location == '' or edad == None or genero == None:
            logging.debug("No se ha seleccionado la provincia, edad o genero" )
            
        else:
            user = request.POST.get("user")
            voter = Voter.objects.get(user=user)
            try:
                censo = Census.objects.get(name=location)
                censo.voter_ids.add(voter)
                censo.save()
            except:
                censo = Census(name = location)
                censo.save()
                censo.voter_ids.add(voter)
                censo.save()
            try:
                censo = Census.objects.get(name=edad)
                censo.voter_ids.add(voter)
                censo.save()
            except:
                censo = Census(name = edad)
                censo.save()
                censo.voter_ids.add(voter)
                censo.save()
            try:
                censo = Census.objects.get(name=genero)
                censo.voter_ids.add(voter)
                censo.save()
            except:
                censo = Census(name = genero)
                censo.save()
                censo.voter_ids.add(voter)
                censo.save()
                
        super(VoterAdmin, self).save_related(request, form, formsets, change)

admin.site.register(Census, CensusAdmin)
admin.site.register(Voter, VoterAdmin)
