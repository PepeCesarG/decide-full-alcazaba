from django.contrib import admin
from django import forms
from django.urls import path
from django.shortcuts import render, redirect

from .models import Census
import csv

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
            reader = csv.reader(csv_file)

            census = Census(name="csv-test") #TODO: CSV parsing (this line is temporal)
            census.save()

            self.message_user(request, "Your csv file has been imported")
            return redirect("..")

        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "csv_form.html", payload)

admin.site.register(Census, CensusAdmin)
