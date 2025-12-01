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
from .mixins import UserTypeRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin


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

class RotinaListView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'rotina_list.html'
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        perfil_id = kwargs.get('pk')
        # Busca o perfil, garantindo que o usuário logado é o 'gerente' dele
        perfil = get_object_or_404(PerfilApoio, pk=perfil_id, gerente=request.user)
        
        # Filtra as rotinas que pertencem a este perfil específico
        rotinas_do_perfil = Rotina.objects.filter(perfil_apoio=perfil)
        
        context = {
            'rotinas': rotinas_do_perfil,
            'perfil': perfil  # Passa o objeto do perfil para o template
        }
        return render(request, self.template_name, context)

class RotinaCreateView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']

    def post(self, request, *args, **kwargs):
        perfil_id = kwargs.get('pk')
        perfil = get_object_or_404(PerfilApoio, pk=perfil_id, gerente=request.user)
        
        data = json.loads(request.body)
        
        rotina = Rotina.objects.create(
            perfil_apoio=perfil, # <--- CORREÇÃO: Associa ao perfil correto
            titulo=data.get('titulo'),
            descricao=data.get('descricao')
        )
        
        return JsonResponse({'status': 'success', 'id': rotina.id}, status=201)

class RotinaUpdateView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        # Correção do caminho do usuário
        rotina = get_object_or_404(Rotina, pk=pk, perfil_apoio__gerente=request.user)
        
        # Retorna os dados para preencher o modal via JavaScript
        data = {
            'id': rotina.id,
            'titulo': rotina.titulo,
            'descricao': rotina.descricao
        }
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        # Correção do caminho do usuário
        rotina = get_object_or_404(Rotina, pk=pk, perfil_apoio__gerente=request.user)
        
        # Lê os dados enviados pelo JavaScript (JSON)
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

class RotinaDeleteView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        # Correção do caminho do usuário
        rotina = get_object_or_404(Rotina, pk=pk, perfil_apoio__gerente=request.user)
        rotina.delete()
        # Retorna JSON para o JavaScript saber que deu certo
        return JsonResponse({'status': 'success', 'message': 'Rotina excluída com sucesso!'})

class RotinaDetailView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'rotina_detail.html'
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        # CORREÇÃO DO ERRO: Busca a rotina através do perfil do gerente
        rotina = get_object_or_404(Rotina, pk=pk, perfil_apoio__gerente=request.user)
        
        context = {'rotina': rotina}
        return render(request, self.template_name, context)

class ItemRotinaCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            rotina_id = kwargs.get('pk')
            # Busca a rotina ligada ao perfil do gerente
            rotina = get_object_or_404(Rotina, pk=rotina_id, perfil_apoio__gerente=request.user)
            
            descricao = request.POST.get('descricao')
            imagem = request.FILES.get('imagem')

            if not descricao:
                return JsonResponse({'status': 'error', 'message': 'Descrição é obrigatória.'}, status=400)

            # Verifica quantos itens existem para definir a ordem
            # Se 'related_name' não estiver definido no model, usa 'itemrotina_set'
            if hasattr(rotina, 'itens'):
                ordem = rotina.itens.count()
            else:
                ordem = rotina.itemrotina_set.count()

            item = ItemRotina.objects.create(
                rotina=rotina,
                descricao=descricao,
                imagem=imagem,
                ordem=ordem
            )
            
            return JsonResponse({
                'status': 'success',
                'id': item.id,
                'descricao': item.descricao,
                'imagem_url': item.imagem.url if item.imagem else None,
            }, status=201)

        except Exception as e:
            # ISSO VAI IMPRIMIR O ERRO REAL NO SEU TERMINAL
            print(f"ERRO AO CRIAR ITEM ROTINA: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class ItemRotinaDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        
        # 1. Busca o item apenas pelo ID (sem tentar filtrar por usuário ainda)
        item = get_object_or_404(ItemRotina, pk=item_id)

        # 2. Verificação de Segurança Manual
        # Navegamos: Item -> Rotina -> PerfilApoio -> Gerente
        # Se o gerente do perfil NÃO for o usuário logado, bloqueia.
        if item.rotina.perfil_apoio.gerente != request.user:
            raise PermissionDenied("Você não tem permissão para excluir este item.")

        # 3. Se chegou aqui, tem permissão. Realiza a exclusão.
        rotina_id = item.rotina.id
        item.delete()
        messages.success(request, 'Item excluído com sucesso!')
        
        return redirect('rotina_detail', pk=rotina_id)

class SalvarOrdemItensView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']
    def post(self, request, *args, **kwargs):
        try:
            # Pega a lista de IDs enviada pelo JavaScript
            data = json.loads(request.body)
            item_ids = data.get('item_ids', [])
            
            # Debug: Mostra no seu terminal o que chegou (para conferir)
            print(f"Salvando ordem para os itens: {item_ids}")

            # Transaction atomic garante que ou salva tudo, ou não salva nada (segurança)
            with transaction.atomic():
                for index, item_id in enumerate(item_ids):
                    # ATENÇÃO: AQUI ESTAVA O PROVÁVEL ERRO
                    # Agora filtramos pelo caminho correto: Item -> Rotina -> Perfil -> Gerente
                    ItemRotina.objects.filter(
                        id=item_id, 
                        rotina__perfil_apoio__gerente=request.user
                    ).update(ordem=index)
            
            return JsonResponse({'status': 'success', 'message': 'Ordem salva com sucesso!'})

        except Exception as e:
            # Se der erro, ele vai aparecer no seu terminal do VS Code
            print(f"ERRO AO SALVAR ORDEM: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class PostagemListView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'postagem_list.html'
    allowed_types = ['EDUCADOR', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        postagens = Postagem.objects.all()
        
        # Filtro por categoria (opcional)
        categoria = request.GET.get('categoria')
        if categoria:
            postagens = postagens.filter(categoria=categoria)
            
        return render(request, self.template_name, {'postagens': postagens})

class PostagemCreateView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'postagem_form.html'
    allowed_types = ['EDUCADOR', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        form = PostagemForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = PostagemForm(request.POST)
        if form.is_valid():
            postagem = form.save(commit=False)
            postagem.usuario = request.user
            postagem.save()
            messages.success(request, 'Postagem criada com sucesso!')
            return redirect('postagem_list')
        return render(request, self.template_name, {'form': form})

class PostagemDetailView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'postagem_detail.html'
    allowed_types = ['EDUCADOR', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        postagem = get_object_or_404(Postagem, pk=pk)
        form_comentario = ComentarioForm()
        return render(request, self.template_name, {
            'postagem': postagem, 
            'form_comentario': form_comentario
        })

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        postagem = get_object_or_404(Postagem, pk=pk)
        form = ComentarioForm(request.POST)
        
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.postagem = postagem
            comentario.usuario = request.user
            comentario.save()
            messages.success(request, 'Comentário adicionado!')
            return redirect('postagem_detail', pk=pk)
            
        return render(request, self.template_name, {
            'postagem': postagem, 
            'form_comentario': form
        })

class PostagemUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'postagem_form.html'

    def test_func(self):
        # Apenas o dono do post ou um Superusuário pode editar
        postagem = get_object_or_404(Postagem, pk=self.kwargs['pk'])
        return self.request.user == postagem.usuario or self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        postagem = get_object_or_404(Postagem, pk=pk)
        form = PostagemForm(instance=postagem)
        return render(request, self.template_name, {'form': form, 'titulo_pagina': 'Editar Postagem'})

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        postagem = get_object_or_404(Postagem, pk=pk)
        form = PostagemForm(request.POST, instance=postagem)
        if form.is_valid():
            form.save()
            messages.success(request, 'Postagem atualizada!')
            return redirect('postagem_detail', pk=pk)
        return render(request, self.template_name, {'form': form, 'titulo_pagina': 'Editar Postagem'})

class PostagemDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        # Apenas o dono do post ou um Superusuário pode excluir
        postagem = get_object_or_404(Postagem, pk=self.kwargs['pk'])
        return self.request.user == postagem.usuario or self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        postagem = get_object_or_404(Postagem, pk=pk)
        postagem.delete()
        messages.success(request, 'Postagem excluída com sucesso!')
        return redirect('postagem_list')

class GuiaInformativoListView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'guia_list.html'
    # Apenas estes perfis podem ver a lista
    allowed_types = ['EDUCADOR', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        # Busca todos os guias, do mais recente para o mais antigo
        guias = GuiaInformativo.objects.all().order_by('-data_criacao')
        
        # Lógica simples de busca (opcional, mas útil)
        termo_busca = request.GET.get('q')
        if termo_busca:
            guias = guias.filter(titulo__icontains=termo_busca)

        context = {'guias': guias}
        return render(request, self.template_name, context)

class GuiaDetailView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'guia_detail.html'
    allowed_types = ['EDUCADOR', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        guia = get_object_or_404(GuiaInformativo, pk=pk)
        context = {'guia': guia}
        return render(request, self.template_name, context)

class GuiaCreateView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'guia_form.html'
    allowed_types = ['EDUCADOR', 'ADM'] # Apenas estes podem criar

    def get(self, request, *args, **kwargs):
        form = GuiaInformativoForm()
        return render(request, self.template_name, {'form': form, 'titulo_pagina': 'Criar Novo Guia'})

    def post(self, request, *args, **kwargs):
        form = GuiaInformativoForm(request.POST, request.FILES)
        if form.is_valid():
            guia = form.save(commit=False)
            guia.autor = request.user
            form.save()
            messages.success(request, 'Guia publicado com sucesso!')
            return redirect('guia_list')
        return render(request, self.template_name, {'form': form, 'titulo_pagina': 'Criar Novo Guia'})

class GuiaUpdateView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'guia_form.html'
    allowed_types = ['EDUCADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        guia = get_object_or_404(GuiaInformativo, pk=pk)
        form = GuiaInformativoForm(instance=guia)
        return render(request, self.template_name, {'form': form, 'titulo_pagina': f'Editar: {guia.titulo}'})

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        guia = get_object_or_404(GuiaInformativo, pk=pk)
        form = GuiaInformativoForm(request.POST, request.FILES, instance=guia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Guia atualizado com sucesso!')
            return redirect('guia_list')
        return render(request, self.template_name, {'form': form, 'titulo_pagina': f'Editar: {guia.titulo}'})

class GuiaDeleteView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'guia_confirm_delete.html'
    allowed_types = ['EDUCADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        guia = get_object_or_404(GuiaInformativo, pk=pk)
        return render(request, self.template_name, {'guia': guia})

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        guia = get_object_or_404(GuiaInformativo, pk=pk)
        guia.delete()
        messages.success(request, 'Guia excluído com sucesso!')
        return redirect('guia_list')

class PECsView(LoginRequiredMixin, View):
    template_name = 'pecs.html'

    def get(self, request, *args, **kwargs):
        Usuario = get_user_model()
        base_query = Q(usuario=request.user)
        try:
            usuario_padrao = Usuario.objects.get(username='usuario_padrao')
            base_query |= Q(usuario=usuario_padrao)
        except Usuario.DoesNotExist:
            pass

        if request.user.is_superuser:
            pecs_a_exibir = PECs.objects.filter(base_query).order_by('texto')
        else:
            pecs_a_exibir = PECs.objects.filter(base_query).order_by('texto')
        
        context = {'pecs_list': pecs_a_exibir}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        texto = request.POST.get('texto')
        imagem = request.FILES.get('imagem')
        
        # NOVA LÓGICA: Verifica se o checkbox foi marcado (apenas se for admin)
        is_crisis = False
        if request.user.is_superuser:
            # Checkboxes HTML enviam 'on' se marcados, ou nada se desmarcados
            is_crisis = request.POST.get('is_crisis_card') == 'on'

        if texto and imagem:
            PECs.objects.create(
                usuario=request.user,
                texto=texto,
                imagem=imagem,
                is_crisis_card=is_crisis # Salva o status de crise
            )
            messages.success(request, 'Cartão PECS adicionado com sucesso!')
        else:
            messages.error(request, 'Erro: Texto e imagem são obrigatórios.')
        
        return redirect('pecs')

class PECsDeleteView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']
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
        pk = kwargs.get('pk')
        pec = get_object_or_404(PECs, pk=pk)

        if not (pec.usuario == request.user or request.user.is_superuser):
            raise PermissionDenied("Você não tem permissão para editar este cartão.")

        data = { 
            'id': pec.id, 
            'texto': pec.texto, 
            'imagem_url': pec.imagem.url,
            'is_crisis_card': pec.is_crisis_card # Envia o status atual para o JS
        }
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        pec = get_object_or_404(PECs, pk=pk)

        if not (pec.usuario == request.user or request.user.is_superuser):
            raise PermissionDenied("Você não tem permissão para editar este cartão.")

        pec.texto = request.POST.get('texto', pec.texto)
        if request.FILES.get('imagem'):
            pec.imagem = request.FILES.get('imagem')
        
        # NOVA LÓGICA: Atualiza o status de crise (apenas se for admin)
        if request.user.is_superuser:
            pec.is_crisis_card = request.POST.get('is_crisis_card') == 'on'
        
        pec.save()

        return JsonResponse({
            'status': 'success',
            'id': pec.id,
            'texto': pec.texto,
            'imagem_url': pec.imagem.url,
            'is_crisis_card': pec.is_crisis_card
        })

class PerfilHubView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'perfil_hub.html'
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']

    def get(self, request, *args, **kwargs):
        perfis = PerfilApoio.objects.filter(gerente=request.user)
        
        # LÓGICA DE RESTRIÇÃO VISUAL:
        # Define se o botão 'Criar' deve aparecer
        pode_criar_perfil = True
        
        # Se for usuário TEA e já tiver um perfil, NÃO pode criar outro
        if request.user.tipo_usuario == 'TEA' and perfis.exists():
            pode_criar_perfil = False
            
        context = {
            'perfis_list': perfis,
            'pode_criar_perfil': pode_criar_perfil # Passamos essa variável para o template
        }
        return render(request, self.template_name, context)

class PerfilCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # LÓGICA DE RESTRIÇÃO DE SEGURANÇA:
        # Antes de criar, verifica se o usuário TEA já tem um perfil
        if request.user.tipo_usuario == 'TEA':
            if PerfilApoio.objects.filter(gerente=request.user).exists():
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Usuários TEA podem ter apenas um perfil.'
                }, status=403)

        data = json.loads(request.body)
        
        perfil = PerfilApoio.objects.create(
            gerente=request.user,
            nome_perfil=data.get('nome_perfil'),
            contato_emergencia=data.get('contato_emergencia', ''),
            informacoes_medicas=data.get('informacoes_medicas', ''),
            gostos_interesses=data.get('gostos_interesses', ''),
            comportamentos_sensoriais=data.get('comportamentos_sensoriais', '')
        )
        
        return JsonResponse({
            'status': 'success',
            'id': perfil.id,
            'nome_perfil': perfil.nome_perfil
        }, status=201)

class PerfilUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        perfil = get_object_or_404(PerfilApoio, pk=pk, gerente=request.user)
        
        data = {
            'id': perfil.id,
            'nome_perfil': perfil.nome_perfil,
            'contato_emergencia': perfil.contato_emergencia,
            'informacoes_medicas': perfil.informacoes_medicas,
            'gostos_interesses': perfil.gostos_interesses,
            'comportamentos_sensoriais': perfil.comportamentos_sensoriais,
        }
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        perfil = get_object_or_404(PerfilApoio, pk=pk, gerente=request.user)
        data = json.loads(request.body)
        
        perfil.nome_perfil = data.get('nome_perfil', perfil.nome_perfil)
        perfil.contato_emergencia = data.get('contato_emergencia', perfil.contato_emergencia)
        perfil.informacoes_medicas = data.get('informacoes_medicas', perfil.informacoes_medicas)
        perfil.gostos_interesses = data.get('gostos_interesses', perfil.gostos_interesses)
        perfil.comportamentos_sensoriais = data.get('comportamentos_sensoriais', perfil.comportamentos_sensoriais)
        perfil.save()
        
        return JsonResponse({'status': 'success', 'id': perfil.id, 'nome_perfil': perfil.nome_perfil})

class PerfilDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        perfil = get_object_or_404(PerfilApoio, pk=pk, gerente=request.user)
        perfil.delete()
        return JsonResponse({'status': 'success', 'message': 'Perfil excluído com sucesso!'})

class ModoCriseView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    template_name = 'modo_crise.html'
    allowed_types = ['TEA', 'CUIDADOR', 'ADM']

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