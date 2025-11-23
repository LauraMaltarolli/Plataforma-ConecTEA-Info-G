$(document).ready(function() {
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // Ação para o botão "Criar Novo Perfil"
    $('#btn-criar-perfil').on('click', function() {
        $('#perfil-form')[0].reset();
        $('#perfil-id').val(''); 
        $('#perfilModalLabel').text('Novo Perfil de Apoio');
        $('#perfilFormModal').modal('show');
    });

    // Ação para o botão "Editar Perfil"
    $('#perfil-list').on('click', '.edit-perfil-btn', function() {
        var perfilId = $(this).data('id');
        
        $.ajax({
            url: `/perfis/${perfilId}/update/`,
            method: 'GET',
            success: function(data) {
                // Preenche o formulário com os dados do perfil
                $('#perfil-id').val(data.id);
                $('#nome_perfil').val(data.nome_perfil);
                $('#contato_emergencia').val(data.contato_emergencia);
                $('#informacoes_medicas').val(data.informacoes_medicas);
                $('#gostos_interesses').val(data.gostos_interesses);
                $('#comportamentos_sensoriais').val(data.comportamentos_sensoriais);
                
                $('#perfilModalLabel').text('Editar Perfil de Apoio');
                $('#perfilFormModal').modal('show');
            }
        });
    });

    // Ação para o SUBMIT do formulário (Criar e Editar)
    $('#perfil-form').on('submit', function(event) {
        event.preventDefault();
        
        var perfilId = $('#perfil-id').val();
        var url = perfilId ? `/perfis/${perfilId}/update/` : '/perfis/criar/';
        
        var data = {
            nome_perfil: $('#nome_perfil').val(),
            contato_emergencia: $('#contato_emergencia').val(),
            informacoes_medicas: $('#informacoes_medicas').val(),
            gostos_interesses: $('#gostos_interesses').val(),
            comportamentos_sensoriais: $('#comportamentos_sensoriais').val()
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
                location.reload(); // Recarrega a página para mostrar o resultado
            },
            error: function() {
                alert('Ocorreu um erro. Verifique se o Nome do Perfil foi preenchido.');
            }
        });
    });

    // Ação para o botão "Excluir Perfil"
    var perfilIdToDelete = null;
    $('#perfil-list').on('click', '.delete-perfil-btn', function() {
        perfilIdToDelete = $(this).data('id');
        $('#deletePerfilConfirmModal').modal('show');
    });

    // Ação para o botão de confirmação "Sim, Excluir"
    $('#confirm-delete-perfil-btn').on('click', function() {
        if (perfilIdToDelete) {
            $.ajax({
                url: `/perfis/${perfilIdToDelete}/delete/`,
                method: 'POST',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                success: function(response) {
                    location.reload(); // Recarrega a página para mostrar o resultado
                }
            });
        }
    });
});