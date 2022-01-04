import json
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from xhtml2pdf import context


from base import mods

from django.shortcuts import get_object_or_404
from visualizer.utils import generate_pdf
from voting.models import *
import random


class VisualizerView(TemplateView):

    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        return context

class VisualizerGetAll(TemplateView):

    def get(self, request):

        data  = list(Voting.objects.all())
        responseData = {}
        for voting in data:

            responseData[voting.id] = {
                'name': voting.name,
                'description': voting.desc,
                'fecha_inicio': voting.start_date,
                'fecha_fin': voting.end_date,
                'postproc': voting.postproc,
            }

        return JsonResponse(responseData)

class VisualizerView2(TemplateView):
    template_name = 'visualizer/graficos.html'

    def grafica_votos(self, id):

        voting = get_object_or_404(Voting, pk=id)
        opcion = []
        voto = []
        puntuacion = []
        color = []
        dataPieVotos = []
        dataPiePuntuaciones = []
        
        i = 0 #esta variable servirá para definir las dimensiones de los ejes en la gráfica

        if(voting.postproc is not None):
            for item in voting.postproc:
                objeto = list(item.items())
                opcion.append(objeto[2][1]) #se coge el valor de la tupla (option, opcion x), que ocupa la posición 2 en la lista de tuplas
                voto.append(objeto[0][1]) #se hace lo mismo con la tupla (votos, x)
                puntuacion.append(objeto[3][1])
                #generamos el color que tendrá cada objeto en la gráfica de forma aleatoria
                r = lambda: random.randint(0,255)
                r = lambda: random.randint(0,255)
                color.append('#%02X%02X%02X' % (r(),r(),r()))
                i += 1
                #Datos para el gráfico de sectores
                dataVoto = {
                    'name': objeto[2][1],
                    'y': objeto[0][1]
                }
                dataPieVotos.append(dataVoto)

                dataPuntuaciones = {
                    'name': objeto[2][1],
                    'y': objeto[3][1]
                }
                dataPiePuntuaciones.append(dataPuntuaciones)
        context = {
            'opcion':opcion,
            'voto':voto,
            'color':color,
            'puntuacion':puntuacion,
            'i':i,
            'dataVotos':dataPieVotos,
            'dataPuntuaciones':dataPiePuntuaciones
        }
        
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        context_grafica_votos = VisualizerView2.grafica_votos(self, vid)
        
        try:
            r = mods.get('voting', params={'id': vid})
            voting = r[0]
            #context principal
            context = {
                'voting':voting
            }
            context.update(context_grafica_votos)
            
        except:
            raise Http404

        return context

class VisualizerView3(TemplateView):

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            voting = r[0]
            context = {
                'voting':voting
            }
        except:
            raise Http404
        
        pdf = generate_pdf('visualizer/pdf.html', context)
        return HttpResponse(pdf, content_type = 'application/pdf')
    