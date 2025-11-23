$(document).ready(function() {
    // Pega o token CSRF do primeiro formulário da página
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // Ação para o botão "Criar Nova Rotina"
    $('#btn-criar-rotina').on('click', function() {
        $('#rotina-form')[0].reset();
        $('#rotina-id').val(''); 
        $('#rotinaModalLabel').text('Nova Rotina');
        $('#rotinaFormModal').modal('show');
    });

    // Ação para o botão "Editar" (que abre o modal)
    $('#rotina-list').on('click', '.edit-rotina-btn', function() {
        var rotinaId = $(this).data('id');
        
        // Busca os dados da rotina no servidor
        $.ajax({
            url: `/rotinas/${rotinaId}/update/`, // URL para buscar dados (GET)
            method: 'GET',
            success: function(data) {
                // Preenche o formulário com os dados
                $('#rotina-id').val(data.id);
                $('#titulo').val(data.titulo);
                $('#descricao').val(data.descricao);
                
                $('#rotinaModalLabel').text('Editar Rotina');
                $('#rotinaFormModal').modal('show');
            },
            error: function() {
                alert('Erro ao buscar dados da rotina.');
            }
        });
    });

    // Ação para o SUBMIT do formulário (Criar e Editar)
    $('#rotina-form').on('submit', function(event) {
        event.preventDefault();
        
        var rotinaId = $('#rotina-id').val();
        
        // A URL de criação agora é dinâmica, baseada no ID do perfil
        var url = rotinaId ? `/rotinas/${rotinaId}/update/` : `/perfis/${PERFIL_ID}/rotinas/criar/`;
        
        var data = {
            titulo: $('#titulo').val(),
            descricao: $('#descricao').val()
        };

        $.ajax({
            url: url,
            method: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            success: function(response) {
                location.reload(); // Recarrega a página após o sucesso
            },
            error: function() {
                alert('Ocorreu um erro. Verifique se o Título foi preenchido.');
            }
        });
    });

    // Ação para o botão "Excluir" (que abre o modal de confirmação)
    var rotinaIdToDelete = null;
    $('#rotina-list').on('click', '.delete-rotina-btn', function() {
        rotinaIdToDelete = $(this).data('id');
        $('#deleteRotinaConfirmModal').modal('show');
    });

    // Ação para o botão de confirmação "Sim, Excluir"
    $('#confirm-delete-rotina-btn').on('click', function() {
        if (rotinaIdToDelete) {
            $.ajax({
                url: `/rotinas/${rotinaIdToDelete}/delete/`,
                method: 'POST',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                success: function(response) {
                    location.reload(); // Recarrega a página após o sucesso
                }
            });
        }
    });
});