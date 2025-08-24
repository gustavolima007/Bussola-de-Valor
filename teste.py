import streamlit as st
import json

# ==================================================
# CONFIGURAÇÃO DA PÁGINA DO STREAMLIT
# ==================================================
st.set_page_config(
    page_title="Filtro Amarelo Ouro - Personalizado",
    page_icon="🌟",
    layout="centered"
)

# Título principal da aplicação
st.title("🎚️ Barra de Filtro Amarelo Ouro Personalizada")

# ==================================================
# CSS PERSONALIZADO - ONDE DEFINIMOS A APARÊNCIA DA BARRA
# ==================================================
slider_html = """
<style>
    /* 
    ESTILO DA BARRA DESLIZANTE (A PARTE PRINCIPAL)
    Esta é a linha horizontal que mostra o range 0-100
    */
    .gold-slider {
        -webkit-appearance: none;  /* Remove aparência padrão do navegador */
        width: 100%;               /* Ocupa 100% da largura disponível */
        height: 5px;              /* ESPESSURA DA BARRA - 5px de altura */
        border-radius: 12px;       /* Bordas arredondadas */
        background: linear-gradient(90deg, #FFD700, #DAA520); /* Gradiente amarelo ouro */
        outline: none;             /* Remove contorno padrão */
        margin: 15px 0;           /* Espaçamento acima e abaixo da barra */
    }
    
    /* 
    ESTILO DO CONTROLE (BOLINHA) PARA NAVEGADORES WEBKIT (Chrome, Safari, Edge)
    Esta é a bolinha que o usuário arrasta
    */
    .gold-slider::-webkit-slider-thumb {
        -webkit-appearance: none;  /* Remove aparência padrão */
        appearance: none;          /* Remove aparência padrão */
        width: 15px;               /* LARGURA DA BOLINHA */
        height: 15px;              /* ALTURA DA BOLINHA */
        border-radius: 50%;        /* Torna circular */
        background: #FFD700;       /* Cor de fundo amarelo ouro */
        border: 3px solid #B8860B; /* Borda mais escura ao redor */
        box-shadow: 0 0 8px rgba(0,0,0,0.4); /* Sombra para destaque */
        cursor: pointer;           /* Cursor de mão ao passar por cima */
    }
    
    /* 
    ESTILO DO CONTROLE (BOLINHA) PARA NAVEGADORES MOZILLA (Firefox)
    Versão alternativa para Firefox
    */
    .gold-slider::-moz-range-thumb {
        width: 15px;               /* LARGURA DA BOLINHA */
        height: 15px;              /* ALTURA DA BOLINHA */
        border-radius: 50%;        /* Torna circular */
        background: #FFD700;       /* Cor de fundo amarelo ouro */
        border: 3px solid #B8860B; /* Borda mais escura */
        box-shadow: 0 0 8px rgba(0,0,0,0.4); /* Sombra */
        cursor: pointer;           /* Cursor de mão */
    }
    
    /* 
    CONTAINER PRINCIPAL - A "CAIXA" QUE ENVOLVE TODA A BARRA
    */
    .slider-container {
        padding: 15px;             /* Espaçamento interno */
        background: #FFF9C4;       /* Cor de fundo amarelo claro */
        border-radius: 15px;       /* Bordas arredondadas */
        border: 1px solid #FFD700; /* Borda fina amarela */
    }
</style>

<!-- 
HTML DA BARRA - A ESTRUTURA VISUAL
-->
<div class="slider-container">
    <!-- RÓTULO DA BARRA -->
    <label for="goldSlider" style="font-weight: bold; color: #8B7500; font-size: 18px;">
        Selecione um valor (0-100):
    </label>
    
    <!-- 
    A BARRA DESLIZANTE EM SI - ELEMENTO HTML <input type="range">
    - min="0": valor mínimo
    - max="100": valor máximo  
    - value="50": valor inicial padrão
    - class="gold-slider": aplica os estilos CSS
    - id="goldSlider": identificador único
    -->
    <input type="range" min="0" max="100" value="50" class="gold-slider" id="goldSlider">
    
    <!-- 
    DISPLAY DO VALOR - ONDE MOSTRAMOS O NÚMERO SELECIONADO
    -->
    <div id="sliderValue" style="margin-top: 15px; font-weight: bold; color: #8B7500; font-size: 20px;">
        Valor selecionado: 50
    </div>
</div>

<!-- 
JAVASCRIPT - PARA TORNAR A BARRA INTERATIVA
-->
<script>
    // Captura os elementos HTML
    const slider = document.getElementById('goldSlider');
    const valueDisplay = document.getElementById('sliderValue');
    
    // Adiciona um "ouvinte" para quando o valor mudar
    slider.addEventListener('input', function() {
        // Atualiza o texto com o valor atual
        valueDisplay.textContent = 'Valor selecionado: ' + this.value;
        
        // Enviar o valor para o Streamlit (para uso futuro)
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: this.value
        }, '*');
    });
</script>
"""

# ==================================================
# EXIBIÇÃO DA BARRA NO STREAMLIT
# ==================================================
# Esta linha renderiza o HTML personalizado na página
st.html(slider_html)

# ==================================================
# BOTÃO DO STREAMLIT - ELEMENTO SEPARADO DA BARRA
# ==================================================
# Usar session_state para armazenar o valor (variável temporária)
if 'slider_value' not in st.session_state:
    st.session_state.slider_value = 50

# 
# ESTE É O BOTÃO "OBTER VALOR DO SLIDER"
# Quando clicado, ele mostra o valor atual na tela
#
if st.button("Obter valor do slider"):
    # Em uma implementação real, isso viria do JavaScript
    # Por enquanto é apenas uma demonstração
    st.success(f"Valor do slider: {st.session_state.slider_value}")

# ==================================================
# INFORMAÇÕES ADICIONAIS
# ==================================================
st.divider()
st.info("💡 Esta é uma implementação personalizada com HTML/CSS/JavaScript para garantir a cor amarelo ouro!")