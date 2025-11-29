from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, PerfilApoio, Rotina, ItemRotina,
    GuiaInformativo, Postagem, Comentario, PECs
)


class PerfilApoioInline(admin.TabularInline):
    model = PerfilApoio
    fk_name = 'gerente'
    extra = 0
    verbose_name = "Perfil de Apoio Gerenciado"
    verbose_name_plural = "Perfis de Apoio Gerenciados"

class ItemRotinaInline(admin.TabularInline):
    model = ItemRotina
    extra = 1

class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ('usuario', 'texto', 'data')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuração do Admin para o nosso Usuário customizado.
    """
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario', 'imagem_perfil')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario', 'imagem_perfil')}),
    )
    inlines = (PerfilApoioInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(Rotina)
class RotinaAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para Rotinas.
    Reflete a nova estrutura (ligada ao PerfilApoio).
    """
    model = Rotina
    list_display = ('titulo', 'perfil_apoio')
    list_filter = ('perfil_apoio',)
    search_fields = ('titulo', 'perfil_apoio__nome_perfil')
    inlines = [ItemRotinaInline]

@admin.register(PerfilApoio)
class PerfilApoioAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para Perfil de Apoio.
    Reflete a nova estrutura (ligada ao 'gerente').
    """
    model = PerfilApoio
    list_display = ('nome_perfil', 'gerente')
    list_filter = ('gerente',)
    search_fields = ('nome_perfil', 'gerente__username')

@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'data_criacao')
    search_fields = ('titulo', 'usuario__username')
    inlines = [ComentarioInline]

@admin.register(GuiaInformativo)
class GuiaInformativoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'publico_alvo')
    search_fields = ('titulo',)

@admin.register(PECs)
class PECsAdmin(admin.ModelAdmin):
    list_display = ('texto', 'usuario', 'is_crisis_card')
    list_filter = ('is_crisis_card', 'usuario')
    search_fields = ('texto', 'usuario__username')

admin.site.register(ItemRotina)
admin.site.register(Comentario)