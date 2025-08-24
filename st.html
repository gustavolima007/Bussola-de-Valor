import streamlit as st
import json

# Configuração da página
st.set_page_config(
    page_title="Filtro Amarelo Ouro - Personalizado",
    page_icon="🌟",
    layout="centered"
)

st.title("🎚️ Barra de Filtro Amarelo Ouro Personalizada")

# CSS personalizado para o slider HTML
slider_html = """
<style>
    .gold-slider {
        -webkit-appearance: none;
        width: 100%;
        height: 15px;
        border-radius: 10px;
        background: linear-gradient(90deg, #FFD700, #DAA520);
        outline: none;
        margin: 20px 0;
    }
    
    .gold-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 25px;
        height: 25px;
        border-radius: 50%;
        background: #FFD700;
        border: 2px solid #B8860B;
        box-shadow: 0 0 5px rgba(0,0,0,0.3);
        cursor: pointer;
    }
    
    .gold-slider::-moz-range-thumb {
        width: 25px;
        height: 25px;
        border-radius: 50%;
        background: #FFD700;
        border: 2px solid #B8860B;
        box-shadow: 0 0 5px rgba(0,0,0,0.3);
        cursor: pointer;
    }
    
    .slider-container {
        padding: 20px;
        background: #FFF9C4;
        border-radius: 10px;
        border: 2px solid #FFD700;
    }
</style>

<div class="slider-container">
    <label for="goldSlider" style="font-weight: bold; color: #8B7500;">
        Selecione um valor (0-100):
    </label>
    <input type="range" min="0" max="100" value="50" class="gold-slider" id="goldSlider">
    <div id="sliderValue" style="margin-top: 10px; font-weight: bold; color: #8B7500;">
        Valor selecionado: 50
    </div>
</div>

<script>
    const slider = document.getElementById('goldSlider');
    const valueDisplay = document.getElementById('sliderValue');
    
    slider.addEventListener('input', function() {
        valueDisplay.textContent = 'Valor selecionado: ' + this.value;
        
        // Enviar o valor para o Streamlit
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: this.value
        }, '*');
    });
</script>
"""

# Exibir o slider personalizado
st.html(slider_html)

# Usar session_state para armazenar o valor
if 'slider_value' not in st.session_state:
    st.session_state.slider_value = 50

# Botão para capturar o valor (simulação)
if st.button("Obter valor do slider"):
    # Em uma implementação real, isso viria do JavaScript
    st.success(f"Valor do slider: {st.session_state.slider_value}")

st.divider()
st.info("💡 Esta é uma implementação personalizada com HTML/CSS/JavaScript para garantir a cor amarelo ouro!")