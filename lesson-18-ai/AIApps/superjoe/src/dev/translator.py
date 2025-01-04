"""
Simple Translation Tool
---------------------
A streamlit app for quick translations between languages.

Requirements:
    pip install streamlit deep-translator
"""

import streamlit as st
from deep_translator import GoogleTranslator
import socket
from typing import Optional

# Constants
LANGUAGES = {
    'English': 'en',
    'Chinese': 'zh-CN',
    'Spanish': 'es',
    'French': 'fr',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Russian': 'ru',
    'Arabic': 'ar',
    'Hindi': 'hi',
    'German': 'de'
}

def check_internet() -> bool:
    """Check if internet connection is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def translate_text(text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """Translate text with error handling"""
    if not text:
        return None
        
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        result = translator.translate(text)
        return result
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Translation Tool", page_icon="🌐")
    
    # Title and description
    st.title("🌐 Translation Tool")
    st.markdown("Quick and easy translation between languages!")

    # Network status check
    is_online = check_internet()
    if not is_online:
        st.error("⚠️ Internet connection required for translations")
        st.stop()

    # Language selection
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("From:", options=list(LANGUAGES.keys()), key='source')
    with col2:
        target_lang = st.selectbox("To:", options=list(LANGUAGES.keys()), 
                                 index=1 if len(LANGUAGES) > 1 else 0, key='target')

    # Quick language swap
    if st.button("🔄 Swap Languages"):
        # Get current indexes
        source_idx = list(LANGUAGES.keys()).index(source_lang)
        target_idx = list(LANGUAGES.keys()).index(target_lang)
        # Store in session state
        st.session_state['source'] = target_idx
        st.session_state['target'] = source_idx
        st.rerun()

    # Text input and translation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Enter text in {source_lang}:**")
        source_text = st.text_area("Source text", height=200, key='source_text')
        
        # Word count
        if source_text:
            word_count = len(source_text.split())
            st.caption(f"Word count: {word_count}")

    with col2:
        st.markdown(f"**Translation in {target_lang}:**")
        if source_text:
            with st.spinner("Translating..."):
                translation = translate_text(
                    source_text,
                    LANGUAGES[source_lang],
                    LANGUAGES[target_lang]
                )
                if translation:
                    st.text_area("Translation", value=translation, height=200, disabled=True)
                    # Word count for translation
                    trans_word_count = len(translation.split())
                    st.caption(f"Word count: {trans_word_count}")
        else:
            st.text_area("Translation", value="", height=200, disabled=True)
            st.caption("Word count: 0")

    # Tips section
    with st.expander("💡 Tips"):
        st.markdown("""
        - Use clear, simple sentences for better translations
        - Check word counts to verify translation completeness
        - Use the swap button to quickly reverse languages
        - Translations are powered by Google Translate
        """)

if __name__ == "__main__":
    main()