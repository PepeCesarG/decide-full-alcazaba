import csv
from io import StringIO

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth.models import User

from .models import Census
from voting.models import Voting
import logging, sys

from voting.models import Voting
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

from .models import Census,Voter


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
        data=''
        with open(respuesta, 'w') as file:
            data = file.read().replace("@", "")
            file.write(data)
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
            csvf = StringIO(csv_file.read().decode())
            reader = csv.reader(csvf, delimiter=',')
            try:
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
                return redirect("..")
            except Exception as e:
                print(e)
                self.message_user(request, "Your csv file could not be imported", level = messages.ERROR)
                return redirect(".")
        
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "csv_form.html", payload)

class VoterAdmin(admin.ModelAdmin):
    list_display = ('user','location','edad','genero')
    
admin.site.register(Census, CensusAdmin)
admin.site.register(Voter, VoterAdmin)
