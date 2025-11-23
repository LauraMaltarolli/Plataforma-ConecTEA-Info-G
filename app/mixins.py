from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class UserTypeRequiredMixin(AccessMixin):
    """
    Verifica se o usuário logado tem um dos tipos de usuário permitidos.
    Caso não tenha, redireciona para a página de 'permissão negada'.
    """
    allowed_types = [] # A View que herdar deve definir esta lista

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # A verificação principal: o tipo do usuário está na lista de permitidos?
        if request.user.tipo_usuario not in self.allowed_types:
            return redirect('permissao_negada')
        
        # Se passou nas verificações, continue
        return super().dispatch(request, *args, **kwargs)