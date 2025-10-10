$(document).ready(function() {
    console.log("pecs.js carregado e pronto.");
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // Lógica de abertura do modal de DETALHES (inalterada)
    $('#pecsDetailModal').on('show.bs.modal', function (event) {
        var card = $(event.relatedTarget);
        var deleteUrl = card.data('delete-url');
        var updateUrl = card.data('update-url');
        var owner = card.data('owner');
        var modal = $(this);
        var editBtn = modal.find('#open-edit-modal-btn');
        var deleteBtn = modal.find('#open-delete-confirm-btn');

        modal.find('#modal-pecs-img').attr('src', card.data('img-url'));
        modal.find('#modal-pecs-text').text(card.data('text'));
        
        var userHasPermission = (LOGGED_IN_USER === owner || IS_SUPERUSER);
        if (userHasPermission) {
            editBtn.data('update-url', updateUrl).show();
            deleteBtn.data('delete-url', deleteUrl).show();
        } else {
            editBtn.hide();
            deleteBtn.hide();
        }
    });

    // --- LÓGICA DE EDIÇÃO ---
    // 1. Quando o botão "Editar" do modal de detalhes é clicado (inalterado)
    $('#open-edit-modal-btn').on('click', function() {
        var updateUrl = $(this).data('update-url');
        $.ajax({
            url: updateUrl,
            method: 'GET',
            success: function(data) {
                $('#edit-pecs-form').attr('action', updateUrl);
                $('#edit-texto').val(data.texto);
                $('#pecsDetailModal').modal('hide');
                $('#pecsEditModal').modal('show');
            }
        });
    });

    // 2. CORREÇÃO: Quando o formulário de edição é ENVIADO
    $('#edit-pecs-form').on('submit', function(event) {
        // Esta é a linha mais importante! Impede a tela preta.
        event.preventDefault();
        
        console.log("Formulário de EDIÇÃO enviado! Impedindo recarregamento...");

        var form = $(this);
        var url = form.attr('action');
        var formData = new FormData(this);

        $.ajax({
            url: url,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function(xhr) {
                // Adicionando o CSRF Token manualmente para garantir
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            success: function(response) {
                console.log("Sucesso! Resposta do servidor:", response);

                // Atualiza o card na página principal sem recarregar
                var card = $('#pecs-card-' + response.id);
                card.find('.pecs-card-img').attr('src', response.imagem_url);
                card.find('.card-title').text(response.texto);

                card.data('img-url', response.imagem_url);
                card.data('text', response.texto);

                $('#pecsEditModal').modal('hide');
            },
            error: function(xhr) {
                console.error("ERRO ao salvar as alterações:", xhr.responseText);
                alert('Ocorreu um erro ao salvar as alterações.');
            }
        });
    });

    // --- LÓGICA DE EXCLUSÃO (inalterada) ---
    $('#open-delete-confirm-btn').on('click', function() {
        var deleteUrl = $(this).data('delete-url');
        $('#delete-pecs-confirm-form').attr('action', deleteUrl);
        $('#pecsDetailModal').modal('hide');
        $('#deletePecsConfirmModal').modal('show');
    });
});