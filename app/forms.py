from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, GuiaInformativo, Comentario, Postagem
from django import forms

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'imagem_perfil')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Loop para adicionar a classe 'form-control' a todos os campos
        for field_name, field in self.fields.items():
            # O campo de imagem é estilizado de forma diferente, então o pulamos
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control-file'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Lógica que já tínhamos para remover a opção 'ADM'
        choices = list(self.fields['tipo_usuario'].choices)
        choices = [choice for choice in choices if choice[0] != 'ADM']
        self.fields['tipo_usuario'].choices = choices

class GuiaInformativoForm(forms.ModelForm):
    class Meta:
        model = GuiaInformativo
        fields = ['titulo', 'descricao', 'link', 'publico_alvo', 'imagem']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'publico_alvo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Pais, Professores, Todos'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class PostagemForm(forms.ModelForm):
    class Meta:
        model = Postagem
        fields = ['titulo', 'categoria', 'conteudo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resuma o assunto...'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Escreva sua dúvida ou relato aqui...'}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Escreva um comentário de apoio ou resposta...'}),
        }