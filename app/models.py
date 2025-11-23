from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('TEA', 'Pessoa com TEA'),
        ('CUIDADOR', 'Cuidador'),
        ('EDUCADOR', 'Educador'),
        ('ADM', 'Administrador'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        verbose_name="Tipo de Usuário"
    )
    imagem_perfil = models.ImageField(
        upload_to='usuarios/perfis/',
        null=True,
        blank=True,
        verbose_name="Imagem de Perfil"
    )
    # CORREÇÃO: Adicionando related_name para resolver conflitos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='app_usuario_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='app_usuario_permissions',
        blank=True
    )

class PerfilApoio(models.Model):
    gerente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='perfis_gerenciados')
    nome_perfil = models.CharField(max_length=100, verbose_name="Nome do Perfil")
    contato_emergencia = models.CharField(max_length=100, blank=True, verbose_name="Contato de Emergência")
    informacoes_medicas = models.TextField(blank=True, verbose_name="Informações Médicas")
    gostos_interesses = models.TextField(blank=True, verbose_name="Gostos e Interesses")
    comportamentos_sensoriais = models.TextField(blank=True, verbose_name="Comportamentos Sensoriais")

    class Meta:
        verbose_name = "Perfil de Apoio"
        verbose_name_plural = "Perfis de Apoio"

    def __str__(self):
        return f"Perfil de Apoio de {self.usuario.username}"

class Rotina(models.Model):
    perfil_apoio = models.ForeignKey(PerfilApoio, on_delete=models.CASCADE, related_name='rotinas')
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    # CORREÇÃO: Adicionando o campo que faltava
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rotina"
        verbose_name_plural = "Rotinas"

    def __str__(self):
        return self.titulo

class ItemRotina(models.Model):
    rotina = models.ForeignKey(Rotina, on_delete=models.CASCADE, related_name='itens', verbose_name="Rotina")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    imagem = models.ImageField(upload_to='rotinas/itens/', blank=True, null=True)
    ordem = models.PositiveIntegerField()

    class Meta:
        ordering = ['ordem']
        verbose_name = "Item de Rotina"
        verbose_name_plural = "Itens de Rotina"

    def __str__(self):
        return self.descricao

class PECs(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pecs', verbose_name="Usuário")
    imagem = models.ImageField(upload_to='pecs/')
    texto = models.CharField(max_length=100)
    is_crisis_card = models.BooleanField(default=False, verbose_name="É um cartão de crise?")

    class Meta:
        verbose_name = "PECs"
        verbose_name_plural = "PECs"

    def __str__(self):
        return self.texto

class GuiaInformativo(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descricao = models.TextField(verbose_name="Conteúdo do Guia")
    link = models.URLField(max_length=255, blank=True, null=True, verbose_name="Link Externo (Opcional)")
    publico_alvo = models.CharField(max_length=100, verbose_name="Público Alvo")
    
    # NOVOS CAMPOS PARA DEIXAR BONITO
    imagem = models.ImageField(upload_to='guias/', blank=True, null=True, verbose_name="Imagem de Capa")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Publicação")

    class Meta:
        verbose_name = "Guia Informativo"
        verbose_name_plural = "Guias Informativos"

    def __str__(self):
        return self.titulo

class Postagem(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='postagens', verbose_name="Usuário")
    titulo = models.CharField(max_length=100)
    conteudo = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data']
        verbose_name = "Postagem"
        verbose_name_plural = "Postagens"

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    postagem = models.ForeignKey(Postagem, on_delete=models.CASCADE, related_name='comentarios', verbose_name="Postagem")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comentarios', verbose_name="Usuário")
    texto = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data']
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"

    def __str__(self):
        return f"Comentário de {self.usuario.username} em '{self.postagem.titulo}'"