$(document).ready(function() {
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // --- LÓGICA DE DRAG AND DROP (inalterada) ---
    $('#item-list').sortable({
        handle: '.drag-handle',
        stop: function(event, ui) {
            var item_ids = [];
            $('#item-list .item-card').each(function() {
                item_ids.push($(this).attr('id').split('-')[1]);
            });
            $.ajax({
                url: '/rotinas/salvar-ordem-itens/',
                method: 'POST',
                data: JSON.stringify({ 'item_ids': item_ids }),
                contentType: 'application/json',
                beforeSend: function(xhr) { xhr.setRequestHeader("X-CSRFToken", csrfToken); },
                success: function(response) { console.log('Ordem salva com sucesso!'); },
                error: function() { console.error('Ocorreu um erro ao salvar a ordem.'); }
            });
        }
    });

    // --- LÓGICA PARA CRIAÇÃO DE ITEM VIA AJAX (inalterada) ---
    $('#add-item-form').on('submit', function(event) {
        event.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var formData = new FormData(this);

        $.ajax({
            url: url,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                var imagemHtml = response.imagem_url ? `<img src="${response.imagem_url}" alt="${response.descricao}">` : '';
                var newItemCard = `
                    <div class="item-card" id="item-${response.id}" style="display:none;">
                        <span class="drag-handle"><i class="fas fa-grip-vertical"></i></span>
                        ${imagemHtml}
                        <div class="flex-grow-1">${response.descricao}</div>
                        <button type="button" class="btn btn-sm text-danger delete-item-btn" data-toggle="modal" data-target="#deleteItemConfirmModal" data-url="/itens/${response.id}/delete/">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>`;
                $('#no-items-message').hide();
                $('#item-list').append(newItemCard);
                $('#item-' + response.id).fadeIn();
                form[0].reset();
            },
            error: function(response) {
                alert('Erro ao adicionar o item. A descrição é obrigatória.');
            }
        });
    });

    // --- NOVA LÓGICA PARA O MODAL DE EXCLUSÃO ---
    // Quando o usuário clica no botão 'X' de um item
    $('#item-list').on('click', '.delete-item-btn', function() {
        // Pega a URL de exclusão que está no botão
        var deleteUrl = $(this).data('url');
        // Coloca essa URL no 'action' do formulário que está dentro do modal
        $('#delete-item-confirm-form').attr('action', deleteUrl);
    });
});