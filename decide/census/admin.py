import csv
from io import StringIO

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path
from .filters import StartedFilter
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

class CensusAdmin(admin.ModelAdmin):
    list_display = ('name', 'votings', 'voters')
    list_filter = ('name', )

    search_fields = ('name', )
    change_list_template = "entities/census_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        csv_url = [path('import-csv/', self.import_csv)]
        return csv_url + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            csvf = StringIO(csv_file.read().decode())
            reader = csv.reader(csvf, delimiter=',')
            try:
                with transaction.atomic():
                    for row in reader:
                        name = row[0]
                        voting_ids = row[1].split(" ")
                        voter_ids = row[2].split(" ")

                        census = Census(name=name)
                        census.save()

                        for id in voting_ids:
                            census.voting_ids.add(id)

                        for id in voter_ids:
                            census.voter_ids.add(id)
                    
                self.message_user(request, "Your csv file has been imported successfully")
                return redirect("..")
            except Exception as e:
                print(e)
                self.message_user(request, "Your csv file could not be imported",  level=messages.ERROR)
                return redirect(".")
        
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "csv_form.html", payload)

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
class VoterAdminForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = "__all__"
    edad = forms.IntegerField(required = True)    
    location = forms.ChoiceField(widget=forms.Select, choices=PROVINCIAS, required=False)
    genero = forms.ChoiceField(widget=forms.Select, choices=GENERO, required=False)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('user','location','edad','genero')
    actions = [ start, stop, tally ]
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
