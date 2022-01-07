import logging
import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from .models import Question, QuestionOption, Voting
from .serializers import SimpleVotingSerializer, VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth
from census.models import Census
from django.forms.models import inlineformset_factory

class SuccessView(TemplateView):
    template_name = 'voting/success.html'

QuestionOptionSet = inlineformset_factory(Question, QuestionOption, fields=('number','option',),can_delete=False, extra=6)

class QuestionFormView(CreateView):
    model = Question
    fields = "__all__"


    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["questionOption"] = QuestionOptionSet(self.request.POST)
        else:
            data["questionOption"] = QuestionOptionSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        questionOption = context["questionOption"]
        self.object = form.save()
        if questionOption.is_valid():
            questionOption.instance = self.object
            questionOption.save()
        return super().form_valid(form)

    def get_success_url(self):
        return "../success"


class VotingFormView(CreateView):
    model = Voting
    fields = "__all__"

    def create_census(self, form):
        location = form.cleaned_data['location']
        if location == '':
            logging.debug("No se ha seleccionado provincia")
        else:
            logging.debug("Se ha seleccionado la provincia de " + location)
            name = form.cleaned_data['name']
            voting = Voting.objects.get(name=name)
            try:
                censo = Census.objects.get(name=location)
                censo.voting_ids.add(voting)
                censo.save()
            except:
                censo = Census(name = location)
                censo.save()
                censo.voting_ids.add(voting)
                censo.save()

    def get_success_url(self):
        return "../success"

    def form_valid(self, form):
        self.object = form.save()
        self.create_census(form)
        return HttpResponseRedirect(self.get_success_url())   


class VotingView(generics.ListCreateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('id', )

    def get(self, request, *args, **kwargs):
        version = request.version
        if version not in settings.ALLOWED_VERSIONS:
            version = settings.DEFAULT_VERSION
        if version == 'v2':
            self.serializer_class = SimpleVotingSerializer

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        for data in ['name', 'desc', 'tipo','question', 'question_opt']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
        question = Question(desc=request.data.get('question'), tipo=request.data.get('tipo'))
        question.save()

        for idx, q_opt in enumerate(request.data.get('question_opt')):
            opt = QuestionOption(question=question, option=q_opt, number=idx)
            opt.save()
        voting = Voting(name=request.data.get('name'), desc=request.data.get('desc'),
                question=question)
        voting.save()

        auth, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        auth.save()
        voting.auths.add(auth)
        return Response({}, status=status.HTTP_201_CREATED)


class VotingUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (UserIsStaff,)

    def put(self, request, voting_id, *args, **kwars):
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = get_object_or_404(Voting, pk=voting_id)
        msg = ''
        st = status.HTTP_200_OK
        if action == 'start':
            if voting.start_date:
                msg = 'Voting already started'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.start_date = timezone.now()
                voting.save()
                msg = 'Voting started'
        elif action == 'stop':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.end_date:
                msg = 'Voting already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.end_date = timezone.now()
                voting.save()
                msg = 'Voting stopped'
        elif action == 'tally':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif not voting.end_date:
                msg = 'Voting is not stopped'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.tally:
                msg = 'Voting already tallied'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.tally_votes(request.auth.key)
                msg = 'Voting tallied'
        else:
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)
