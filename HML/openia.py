import streamlit as st
import urllib.parse

st.title("🔍 Bússola de Valor com IA")

texto = st.text_area("Digite os dados da empresa")

if texto:
    chatgpt_url = "https://chat.openai.com"
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(texto)}"

    st.markdown(f"""
        <div style="display:flex;gap:10px;margin-top:20px;">
            <a href="{google_url}" target="_blank">
                <button style="background-color:#f8f9fa;border:1px solid #ccc;padding:8px 16px;border-radius:6px;font-size:14px;">
                    🔍 Ask Google
                </button>
            </a>
            <a href="{chatgpt_url}" target="_blank">
                <button style="background-color:#f8f9fa;border:1px solid #ccc;padding:8px 16px;border-radius:6px;font-size:14px;">
                    💬 Ask ChatGPT
                </button>
            </a>
        </div>
    """, unsafe_allow_html=True)

    st.write("📋 Copie os dados abaixo e cole na IA:")
    st.code(texto, language="text")
