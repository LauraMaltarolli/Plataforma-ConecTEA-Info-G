from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('username','first_name', 'last_name', 'email', 'tipo_usuario', 'imagem_perfil')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(self.fields['tipo_usuario'].choices)
        choices.pop(4)
        self.fields['tipo_usuario'].choices = choices