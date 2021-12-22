import csv
from io import StringIO

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path

from .models import Census
from voting.models import Voting
from django.contrib.auth.models import User

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
                    next(reader)
                    for row in reader:
                        name = row[1]
                        votings = row[2][1:-1].split(":")
                        voters = row[3][1:-1].split(":")

                        census = Census(name=name)
                        census.save()

                        for nombre in votings:
                            id = Voting.objects.filter(name = nombre).first()
                            if (id):
                                census.voting_ids.add(id)

                        for nombre in voters:
                            id = User.objects.filter(username = nombre).first()
                            if (id):
                                census.voter_ids.add(id)
                    
                self.message_user(request, "Your csv file has been imported successfully")
                return redirect("..")

            except Exception as e:
                print(e)
                self.message_user(request, "Your csv file could not be imported", level = messages.ERROR)
                return redirect(".")
        
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "csv_form.html", payload)

admin.site.register(Census, CensusAdmin)
