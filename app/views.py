from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied


class IndexView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class CadastroView(View):
    template_name = 'registration/cadastro.html'

    def get(self, request, *args, **kwargs):
        form = UsuarioCreationForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = UsuarioCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado com sucesso! Por favor, faça o login.')
            return redirect('login')
        else:
            # ADICIONANDO MENSAGEM DE ERRO GENÉRICA
            messages.error(request, 'Houve um erro no seu cadastro. Por favor, verifique os campos abaixo.')
            context = {'form': form}
            return render(request, self.template_name, context)

class LoginView(View):
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Se o formulário for válido, o Django já verificou o usuário e a senha
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bem-vindo(a) de volta, {user.username}!')
            return redirect('index')
        else:
            # Se o formulário for inválido, a senha ou o usuário estão errados
            messages.error(request, 'Nome de usuário ou senha inválidos. Por favor, tente novamente.')
            context = {'form': form}
            return render(request, self.template_name, context)

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Você saiu da sua conta com sucesso.')
        return redirect('index')

class RotinaListView(LoginRequiredMixin, View):
    template_name = 'rotina_list.html'

    def get(self, request, *args, **kwargs):
        rotinas = Rotina.objects.filter(usuario=request.user)
        context = {
            'rotinas': rotinas,
        }
        return render(request, self.template_name, context)

class RotinaCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Carrega os dados enviados via AJAX
        data = json.loads(request.body)
        titulo = data.get('titulo')
        descricao = data.get('descricao')

        if titulo:
            # Cria a nova rotina associada ao usuário logado
            rotina = Rotina.objects.create(
                usuario=request.user,
                titulo=titulo,
                descricao=descricao
            )
            # Retorna os dados da rotina criada em formato JSON
            return JsonResponse({
                'status': 'success',
                'id': rotina.id,
                'titulo': rotina.titulo,
                'descricao': rotina.descricao
            }, status=201)
        
        # Se o título estiver faltando, retorna um erro
        return JsonResponse({'status': 'error', 'message': 'Título é obrigatório.'}, status=400)

class RotinaUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Esta parte é chamada quando clicamos em "Editar" para buscar os dados
        pk = kwargs.get('pk')
        rotina = get_object_or_404(Rotina, pk=pk, usuario=request.user)
        data = {
            'id': rotina.id,
            'titulo': rotina.titulo,
            'descricao': rotina.descricao
        }
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        # Esta parte é chamada quando salvamos o formulário de edição
        pk = kwargs.get('pk')
        rotina = get_object_or_404(Rotina, pk=pk, usuario=request.user)
        data = json.loads(request.body)
        
        rotina.titulo = data.get('titulo', rotina.titulo)
        rotina.descricao = data.get('descricao', rotina.descricao)
        rotina.save()
        
        return JsonResponse({
            'status': 'success',
            'id': rotina.id,
            'titulo': rotina.titulo,
            'descricao': rotina.descricao
        })

class RotinaDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        rotina = get_object_or_404(Rotina, pk=pk, usuario=request.user)
        rotina.delete()
        return JsonResponse({'status': 'success', 'message': 'Rotina excluída com sucesso!'})

class RotinaDetailView(LoginRequiredMixin, View):
    template_name = 'rotina_detail.html'

    def get(self, request, *args, **kwargs):
        # Usamos o 'pk' (primary key) da URL para buscar a rotina exata
        pk_da_rotina = kwargs.get('pk')
        rotina = get_object_or_404(Rotina, pk=pk_da_rotina, usuario=request.user)
        
        context = {
            'rotina': rotina
        }
        return render(request, self.template_name, context)

class ItemRotinaCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        rotina_id = kwargs.get('pk')
        rotina = get_object_or_404(Rotina, pk=rotina_id, usuario=request.user)
        
        descricao = request.POST.get('descricao')
        imagem = request.FILES.get('imagem')

        if not descricao:
            return JsonResponse({'status': 'error', 'message': 'Descrição é obrigatória.'}, status=400)

        ordem = rotina.itens.count()
        item = ItemRotina.objects.create(
            rotina=rotina,
            descricao=descricao,
            imagem=imagem,
            ordem=ordem
        )
        
        # Retorna os dados do novo item como JSON para o JavaScript
        return JsonResponse({
            'status': 'success',
            'id': item.id,
            'descricao': item.descricao,
            'imagem_url': item.imagem.url if item.imagem else None,
        }, status=201)

class ItemRotinaDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        item = get_object_or_404(ItemRotina, pk=item_id, rotina__usuario=request.user)
        rotina_id = item.rotina.id
        item.delete()
        messages.success(request, 'Item excluído com sucesso!')
        
        # Redireciona de volta para a página de detalhes, causando o recarregamento
        return redirect('rotina_detail', pk=rotina_id)

class SalvarOrdemItensView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # Pega a lista de IDs ordenada enviada pelo JavaScript
            item_ids = json.loads(request.body).get('item_ids', [])
            
            for index, item_id in enumerate(item_ids):
                # Para cada item na lista, atualiza o campo 'ordem'
                ItemRotina.objects.filter(id=item_id, rotina__usuario=request.user).update(ordem=index)
            
            return JsonResponse({'status': 'success', 'message': 'Ordem salva com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class PostagemListView(LoginRequiredMixin,View):
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
        Usuario = get_user_model()
        
        # Prepara a base da consulta para pegar os cartões do usuário logado e do usuário padrão
        base_query = Q(usuario=request.user)
        try:
            usuario_padrao = Usuario.objects.get(username='usuario_padrao')
            base_query |= Q(usuario=usuario_padrao)
        except Usuario.DoesNotExist:
            pass # Continua sem o usuário padrão se ele não for encontrado

        # --- NOVA LÓGICA DE PERMISSÃO ---
        if request.user.is_superuser:
            # Se o usuário for um admin, busca TODOS os cartões (de crise ou não)
            pecs_a_exibir = PECs.objects.filter(base_query).order_by('texto')
        else:
            # Se for um usuário normal, busca apenas os cartões que NÃO são de crise
            pecs_a_exibir = PECs.objects.filter(base_query, is_crisis_card=False).order_by('texto')
        
        context = {
            'pecs_list': pecs_a_exibir
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # A lógica de criação de um novo cartão não muda.
        texto = request.POST.get('texto')
        imagem = request.FILES.get('imagem')

        if texto and imagem:
            PECs.objects.create(
                usuario=request.user,
                texto=texto,
                imagem=imagem
            )
            messages.success(request, 'Cartão PECS pessoal adicionado com sucesso!')
        else:
            messages.error(request, 'Erro: Texto e imagem são obrigatórios.')
        
        return redirect('pecs')

class PECsDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        pec = get_object_or_404(PECs, pk=pk)

        # LÓGICA DE PERMISSÃO:
        # Verifica se o usuário logado é o dono do cartão OU se é um superusuário (admin)
        if pec.usuario == request.user or request.user.is_superuser:
            pec.delete()
            messages.success(request, 'Cartão PECS excluído com sucesso!')
        else:
            # Se não tiver permissão, gera um erro.
            raise PermissionDenied("Você não tem permissão para excluir este cartão.")
        
        return redirect('pecs')

class PECsUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Busca os dados do PECS para preencher o formulário de edição
        pk = kwargs.get('pk')
        pec = get_object_or_404(PECs, pk=pk)

        # Verifica a permissão antes de enviar os dados
        if not (pec.usuario == request.user or request.user.is_superuser):
            raise PermissionDenied("Você não tem permissão para editar este cartão.")

        data = { 'id': pec.id, 'texto': pec.texto, 'imagem_url': pec.imagem.url }
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        # Salva as alterações enviadas pelo formulário
        pk = kwargs.get('pk')
        pec = get_object_or_404(PECs, pk=pk)

        # Verifica a permissão antes de salvar
        if not (pec.usuario == request.user or request.user.is_superuser):
            raise PermissionDenied("Você não tem permissão para editar este cartão.")

        pec.texto = request.POST.get('texto', pec.texto)
        if request.FILES.get('imagem'):
            pec.imagem = request.FILES.get('imagem')
        
        pec.save()

        return JsonResponse({
            'status': 'success',
            'id': pec.id,
            'texto': pec.texto,
            'imagem_url': pec.imagem.url
        })

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
        Usuario = get_user_model()
        crisis_pecs = PECs.objects.none()

        try:
            # Pega o usuário padrão para buscar os PECS de crise globais
            usuario_padrao = Usuario.objects.get(username='usuario_padrao')
            
            # Busca os PECS que são 'de crise' E que pertencem ao usuário logado OU ao usuário padrão
            crisis_pecs = PECs.objects.filter(
                Q(is_crisis_card=True) & (Q(usuario=request.user) | Q(usuario=usuario_padrao))
            ).order_by('texto')

        except Usuario.DoesNotExist:
            # Se o usuario_padrao não existir, mostra apenas os do usuário logado
            crisis_pecs = PECs.objects.filter(is_crisis_card=True, usuario=request.user).order_by('texto')

        context = {
            'crisis_pecs_list': crisis_pecs
        }
        return render(request, self.template_name, context)