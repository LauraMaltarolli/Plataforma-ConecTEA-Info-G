$(document).ready(function() {
    // Pega os elementos da página
    const selectionStrip = $('#selection-strip');
    const clearButton = $('#clear-selection-btn');

    // Função para falar um texto em voz alta
    function speakText(text) {
        // Cria um objeto de fala
        var utterance = new SpeechSynthesisUtterance(text);
        // Define a linguagem (opcional, mas recomendado)
        utterance.lang = 'pt-BR';
        // Pede ao navegador para falar
        window.speechSynthesis.speak(utterance);
    }

    // Quando um cartão de crise é clicado
    $('.crisis-pecs-card').on('click', function() {
        // Pega os dados do cartão clicado
        var card = $(this);
        var text = card.data('text');
        var imageUrl = card.data('img-url');

        // Cria o HTML para o novo item na barra de seleção
        var selectedItemHtml = `
            <div class="selected-pecs-item">
                <img src="${imageUrl}" alt="${text}">
                <span>${text}</span>
            </div>
        `;

        // Adiciona o item à barra
        selectionStrip.append(selectedItemHtml);
        
        // Mostra o botão de limpar, caso esteja escondido
        clearButton.show();

        // Fala o texto do cartão
        speakText(text);
    });

    // Quando o botão de limpar é clicado
    clearButton.on('click', function() {
        // Esvazia a barra de seleção
        selectionStrip.empty();
        // Esconde o botão de limpar novamente
        $(this).hide();
    });
});