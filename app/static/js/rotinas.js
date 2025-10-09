$(document).ready(function() {
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // Ação para o botão "Criar Nova Rotina" (inalterado)
    $('#btn-criar-rotina').on('click', function() {
        $('#rotina-form')[0].reset();
        $('#rotina-id').val(''); 
        $('#rotinaModalLabel').text('Nova Rotina');
        $('#rotinaFormModal').modal('show');
    });

    // Ação para o botão "Editar" (inalterado)
    $('#rotina-list').on('click', '.edit-rotina-btn', function() {
        var rotinaId = $(this).data('id');
        
        $.ajax({
            url: `/rotinas/${rotinaId}/update/`,
            method: 'GET',
            success: function(data) {
                $('#rotina-id').val(data.id);
                $('#titulo').val(data.titulo);
                $('#descricao').val(data.descricao);
                $('#rotinaModalLabel').text('Editar Rotina');
                $('#rotinaFormModal').modal('show');
            }
        });
    });

    // Lida com o SUBMIT do formulário (CRIAR e EDITAR)
    $('#rotina-form').on('submit', function(event) {
        event.preventDefault();
        
        var rotinaId = $('#rotina-id').val();
        var url = rotinaId ? `/rotinas/${rotinaId}/update/` : '/rotinas/criar/';
        var method = 'POST';

        var data = {
            titulo: $('#titulo').val(),
            descricao: $('#descricao').val()
        };

        $.ajax({
            url: url,
            method: method,
            data: JSON.stringify(data),
            contentType: 'application/json',
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            success: function(response) {
                // MUDANÇA AQUI: Em vez de manipular o HTML,
                // simplesmente recarregamos a página para ver o resultado.
                location.reload();
            },
            error: function() {
                alert('Ocorreu um erro ao salvar a rotina.');
            }
        });
    });

    // Lida com a EXCLUSÃO da rotina
    var rotinaIdToDelete = null;
    $('#rotina-list').on('click', '.delete-rotina-btn', function() {
        rotinaIdToDelete = $(this).data('id');
        $('#deleteRotinaConfirmModal').modal('show');
    });

    $('#confirm-delete-rotina-btn').on('click', function() {
        if (rotinaIdToDelete) {
            $.ajax({
                url: `/rotinas/${rotinaIdToDelete}/delete/`,
                method: 'POST',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                success: function(response) {
                    // MUDANÇA AQUI: Também recarregamos a página
                    // após a exclusão bem-sucedida.
                    location.reload();
                },
                error: function() {
                    alert('Ocorreu um erro ao excluir a rotina.');
                }
            });
        }
    });
});