from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, PerfilApoio, Rotina, ItemRotina,
    GuiaInformativo, Postagem, Comentario, PECs
)

class PerfilApoioInline(admin.StackedInline):
    model = PerfilApoio
    can_delete = False
    verbose_name_plural = 'Perfil de Apoio'
    fk_name = 'usuario'
    extra = 1

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
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

class ItemRotinaInline(admin.TabularInline):
    model = ItemRotina
    extra = 1

@admin.register(Rotina)
class RotinaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'data_criacao')
    search_fields = ('titulo', 'usuario__username')
    list_filter = ('usuario',)
    inlines = [ItemRotinaInline]

class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ('usuario', 'texto', 'data')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Postagem)
class PostagemAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'data')
    search_fields = ('titulo', 'usuario__username')
    inlines = [ComentarioInline]

@admin.register(GuiaInformativo)
class GuiaInformativoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'publico_alvo')
    search_fields = ('titulo',)

@admin.register(PECs)
class PECsAdmin(admin.ModelAdmin):
    list_display = ('texto', 'usuario')
    search_fields = ('texto', 'usuario__username')