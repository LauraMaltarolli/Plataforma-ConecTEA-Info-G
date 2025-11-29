"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('perfis/<int:pk>/rotinas/', RotinaListView.as_view(), name='rotina_list'),
    path('perfis/<int:pk>/rotinas/criar/', RotinaCreateView.as_view(), name='rotina_create'),
    path('rotinas/<int:pk>/', RotinaDetailView.as_view(), name='rotina_detail'),
    path('rotinas/<int:pk>/update/', RotinaUpdateView.as_view(), name='rotina_update'),
    path('rotinas/<int:pk>/delete/', RotinaDeleteView.as_view(), name='rotina_delete'),
    path('rotinas/<int:pk>/add-item/', ItemRotinaCreateView.as_view(), name='item_create'),
    path('itens/<int:pk>/delete/', ItemRotinaDeleteView.as_view(), name='item_delete'),
    path('rotinas/salvar-ordem-itens/', SalvarOrdemItensView.as_view(), name='salvar_ordem_itens'),
    path('comunidade/', PostagemListView.as_view(), name='postagem_list'),
    path('comunidade/nova/', PostagemCreateView.as_view(), name='postagem_create'),
    path('comunidade/<int:pk>/', PostagemDetailView.as_view(), name='postagem_detail'),
    path('comunidade/<int:pk>/editar/', PostagemUpdateView.as_view(), name='postagem_update'),
    path('comunidade/<int:pk>/deletar/', PostagemDeleteView.as_view(), name='postagem_delete'),
    path('guias/', GuiaInformativoListView.as_view(), name='guia_list'),
    path('guias/criar/', GuiaCreateView.as_view(), name='guia_create'),
    path('guias/<int:pk>/', GuiaDetailView.as_view(), name='guia_detail'),
    path('guias/<int:pk>/editar/', GuiaUpdateView.as_view(), name='guia_update'),
    path('guias/<int:pk>/deletar/', GuiaDeleteView.as_view(), name='guia_delete'),
    path('pecs/', PECsView.as_view(), name='pecs'),
    path('pecs/<int:pk>/delete/', PECsDeleteView.as_view(), name='pecs_delete'),
    path('pecs/<int:pk>/update/', PECsUpdateView.as_view(), name='pecs_update'),
    path('perfis/', PerfilHubView.as_view(), name='perfil_hub'),
    path('perfis/criar/', PerfilCreateView.as_view(), name='perfil_create'),
    path('perfis/<int:pk>/update/', PerfilUpdateView.as_view(), name='perfil_update'),
    path('perfis/<int:pk>/delete/', PerfilDeleteView.as_view(), name='perfil_delete'),
    path('modo-crise/', ModoCriseView.as_view(), name='modo_crise'),
    path('permissao-negada/', TemplateView.as_view(template_name='permissao_negada.html'), name='permissao_negada'),
    
    # URLs de Autenticação
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('login/', LoginView.as_view(), name='login'),  
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
