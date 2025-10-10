from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
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