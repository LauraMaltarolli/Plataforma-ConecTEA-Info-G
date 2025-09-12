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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('rotinas/', RotinaListView.as_view(), name='rotina_list'),
    path('comunidade/', PostagemListView.as_view(), name='postagem_list'),
    path('guias/', GuiaInformativoListView.as_view(), name='guia_list'),
    path('pecs/', PECsView.as_view(), name='pecs'),
    path('perfil/', PerfilApoioView.as_view(), name='perfil_apoio'),
    path('modo-crise/', ModoCriseView.as_view(), name='modo_crise'),
    
    # URLs de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='app:index'), name='logout'),
]
