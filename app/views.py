from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import *

class IndexView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class RotinaListView(LoginRequiredMixin, View):
    template_name = 'rotina_list.html'

    def get(self, request, *args, **kwargs):
        rotinas = Rotina.objects.filter(usuario=request.user)
        context = {
            'rotinas': rotinas,
        }
        return render(request, self.template_name, context)

class PostagemListView(View):
    template_name = 'postagem_list.html'

    def get(self, request, *args, **kwargs):
        postagens = Postagem.objects.all()
        context = {
            'postagens': postagens,
        }
        return render(request, self.template_name, context)

class GuiaInformativoListView(View):
    template_name = 'guia_list.html'

    def get(self, request, *args, **kwargs):
        guias = GuiaInformativo.objects.all()
        context = {
            'guias': guias,
        }
        return render(request, self.template_name, context)

class PECsView(LoginRequiredMixin, View):
    template_name = 'pecs.html'

    def get(self, request, *args, **kwargs):
        pecs_usuario = PECs.objects.filter(usuario=request.user)
        context = {
            'pecs_list': pecs_usuario,
        }
        return render(request, self.template_name, context)

class PerfilApoioView(LoginRequiredMixin, View):
    template_name = 'perfil_apoio.html'

    def get(self, request, *args, **kwargs):
        perfil, created = PerfilApoio.objects.get_or_create(usuario=request.user)
        context = {
            'perfil': perfil,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        perfil = PerfilApoio.objects.get(usuario=request.user)
        
        perfil.contato_emergencia = request.POST.get('contato_emergencia')
        perfil.informacoes_medicas = request.POST.get('informacoes_medicas')
        perfil.gostos_interesses = request.POST.get('gostos_interesses')
        perfil.comportamentos_sensoriais = request.POST.get('comportamentos_sensoriais')
        perfil.save()

        messages.success(request, 'Perfil de Apoio atualizado com sucesso!')
        return redirect('app:perfil_apoio')

class ModoCriseView(LoginRequiredMixin, View):
    template_name = 'modo_crise.html'

    def get(self, request, *args, **kwargs):
        # A lógica para buscar mídias calmantes ou PECs de crise viria aqui
        context = {}
        return render(request, self.template_name, context)