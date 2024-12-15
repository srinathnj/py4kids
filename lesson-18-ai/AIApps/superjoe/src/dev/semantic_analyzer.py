"""
Semantic Comparison Tool
----------------------
A streamlit app for analyzing semantic relationships between languages.

Requirements:
    pip install streamlit sentence-transformers numpy pandas plotly
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict

# Available languages
LANGUAGES = {
    'English': 'en',
    'Chinese': 'zh',
    'Spanish': 'es',
    'French': 'fr',
    'Japanese': 'ja'
}

# Dynamic semantic fields based on common categories
SEMANTIC_CONTEXT = {
    # Animals and pets
    'animal': {
        'English': ['animal', 'pet', 'creature', 'mammal', 'wildlife', 'companion'],
        'Chinese': ['动物', '宠物', '生物', '哺乳动物', '野生动物', '伙伴'],
        'Spanish': ['animal', 'mascota', 'criatura', 'mamífero', 'fauna', 'compañero'],
        'French': ['animal', 'animal de compagnie', 'créature', 'mammifère', 'faune', 'compagnon'],
        'Japanese': ['動物', 'ペット', '生き物', '哺乳類', '野生動物', '仲間']
    },
    # Human-related
    'human': {
        'English': ['person', 'human', 'individual', 'people', 'adult', 'being'],
        'Chinese': ['人', '人类', '个人', '人们', '成人', '生命'],
        'Spanish': ['persona', 'humano', 'individuo', 'gente', 'adulto', 'ser'],
        'French': ['personne', 'humain', 'individu', 'gens', 'adulte', 'être'],
        'Japanese': ['人', '人間', '個人', '人々', '大人', '存在']
    },
    # Objects and things
    'object': {
        'English': ['thing', 'object', 'item', 'material', 'substance', 'matter'],
        'Chinese': ['东西', '物体', '物品', '材料', '物质', '事物'],
        'Spanish': ['cosa', 'objeto', 'elemento', 'material', 'sustancia', 'materia'],
        'French': ['chose', 'objet', 'article', 'matériel', 'substance', 'matière'],
        'Japanese': ['物', '物体', '品物', '材料', '物質', '事物']
    }
}

# Example pairs for quick testing
EXAMPLE_PAIRS = {
    'Gender': {'English': 'man', 'Chinese': '男人', 'Spanish': 'hombre', 'French': 'homme', 'Japanese': '男'},
    'Family': {'English': 'family', 'Chinese': '家庭', 'Spanish': 'familia', 'French': 'famille', 'Japanese': '家族'},
    'Person': {'English': 'person', 'Chinese': '人', 'Spanish': 'persona', 'French': 'personne', 'Japanese': '人'}
}

@st.cache_resource
def load_model():
    """Load the multilingual model"""
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def compute_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors"""
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    return dot_product / (norm1 * norm2)

def get_similarity_display(score: float) -> str:
    """Create visual representation of similarity score"""
    stars = int(score * 10)
    return "⭐" * stars + "☆" * (10 - stars)

def get_semantic_category(text: str, model: SentenceTransformer) -> str:
    """Dynamically determine the semantic category of the input text"""
    # Category probe words
    probes = {
        'animal': 'animal pet creature',
        'human': 'human person people',
        'object': 'thing object item'
    }
    
    # Get embeddings
    text_embedding = model.encode(text)
    similarities = {}
    
    # Compare with each category
    for category, probe in probes.items():
        probe_embedding = model.encode(probe)
        similarity = compute_similarity(text_embedding, probe_embedding)
        similarities[category] = similarity
    
    # Return the most similar category
    return max(similarities.items(), key=lambda x: x[1])[0]

def get_semantic_field(text: str, lang: str, model: SentenceTransformer) -> List[Tuple[str, float]]:
    """Get semantic field (related words) for given text using dynamic context"""
    # First determine the general category
    category = get_semantic_category(text, model)
    
    # Get context words for the category
    context_words = SEMANTIC_CONTEXT[category][lang]
    
    # Get embeddings and similarities
    text_embedding = model.encode(text)
    similarities = []
    
    # Add the category-specific context words
    for word in context_words:
        word_embedding = model.encode(word)
        similarity = compute_similarity(text_embedding, word_embedding)
        similarities.append((word, similarity))
    
    return sorted(similarities, key=lambda x: x[1], reverse=True)

def plot_semantic_comparison(similarities1: List[Tuple[str, float]], 
                           similarities2: List[Tuple[str, float]],
                           lang1: str, lang2: str) -> plotly.graph_objs.Figure:
    """Create a comparison plot of semantic similarities"""
    df = pd.DataFrame({
        f'{lang1}': [s[1] for s in similarities1],
        f'{lang2}': [s[1] for s in similarities2],
        'Words': [f'{s1[0]}/{s2[0]}' for s1, s2 in zip(similarities1, similarities2)]
    })
    
    fig = px.bar(df, x='Words', y=[f'{lang1}', f'{lang2}'],
                 title='Semantic Field Comparison',
                 barmode='group',
                 color_discrete_sequence=['#FF4B4B', '#0068C9'])
    
    fig.update_layout(
        xaxis_title="Word Pairs",
        yaxis_title="Semantic Similarity",
        height=400
    )
    return fig

def main():
    st.set_page_config(page_title="Semantic Comparison", page_icon="🎯", layout="wide")
    
    st.title("🎯 Semantic Comparison Tool")
    st.markdown("""
    Explore how words and concepts relate across different languages! See the semantic relationships
    and understand cultural connections through AI-powered analysis.
    """)

    # Load model
    model = load_model()

    # Example selector
    st.sidebar.header("Quick Examples")
    if st.sidebar.button("Try an Example"):
        category = st.sidebar.selectbox("Choose category:", list(EXAMPLE_PAIRS.keys()))
        if category:
            st.session_state['example_pair'] = EXAMPLE_PAIRS[category]

    # Language and text input
    col1, col2 = st.columns(2)
    with col1:
        lang1 = st.selectbox("First Language", options=list(LANGUAGES.keys()), key='lang1')
        if 'example_pair' in st.session_state:
            default_text1 = st.session_state['example_pair'][lang1]
        else:
            default_text1 = ""
        text1 = st.text_area("Enter text", value=default_text1, height=100, key='text1')
        
    with col2:
        lang2 = st.selectbox("Second Language", options=list(LANGUAGES.keys()), key='lang2')
        if 'example_pair' in st.session_state:
            default_text2 = st.session_state['example_pair'][lang2]
        else:
            default_text2 = ""
        text2 = st.text_area("Enter text", value=default_text2, height=100, key='text2')

    # Analyze button
    if st.button("🔍 Analyze Semantic Relationship"):
        if text1 and text2:
            with st.spinner("Analyzing semantic relationships..."):
                try:
                    # Get embeddings and calculate similarity
                    embed1 = model.encode(text1)
                    embed2 = model.encode(text2)
                    similarity = compute_similarity(embed1, embed2)
                    
                    # Get semantic fields
                    field1 = get_semantic_field(text1, lang1, model)
                    field2 = get_semantic_field(text2, lang2, model)
                    
                    # Display results
                    st.header("Analysis Results")
                    
                    # Basic similarity metrics
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        st.metric("Similarity Score", f"{similarity:.2f}")
                    with col2:
                        st.write("Match Level:", get_similarity_display(similarity))
                    with col3:
                        if similarity > 0.8:
                            st.success("Strong match! 🎯")
                        elif similarity > 0.6:
                            st.success("Good match! 👍")
                        elif similarity > 0.4:
                            st.info("Partial match 🤔")
                        else:
                            st.warning("Weak match 🌈")

                    # Semantic fields
                    st.subheader("Semantic Field Analysis")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{lang1} semantic field:**")
                        for word, sim in field1[:5]:
                            st.write(f"- {word}: {sim:.2f} {get_similarity_display(sim)}")
                    with col2:
                        st.write(f"**{lang2} semantic field:**")
                        for word, sim in field2[:5]:
                            st.write(f"- {word}: {sim:.2f} {get_similarity_display(sim)}")

                    # Visualization
                    st.subheader("Comparative Analysis")
                    fig = plot_semantic_comparison(field1, field2, lang1, lang2)
                    st.plotly_chart(fig, use_container_width=True)

                    # Interpretation
                    with st.expander("📊 Interpretation Guide"):
                        st.markdown(f"""
                        **Similarity Score: {similarity:.2f}**
                        
                        This analysis shows:
                        1. **Direct Match:** {get_similarity_display(similarity)}
                        2. **Semantic Field Overlap:** How related concepts compare
                        3. **Cultural Context:** How the terms are used in each language
                        
                        {
                        "Strong match! These terms share very similar semantic spaces. They likely evoke similar concepts and uses in both languages." 
                        if similarity > 0.8 else 
                        "Good match! These terms are related but might have subtle differences in usage or connotation." 
                        if similarity > 0.6 else 
                        "Partial match. These terms share some meaning but might be used differently in each language." 
                        if similarity > 0.4 else 
                        "These terms show significant differences in meaning or usage between the languages."
                        }
                        """)
                except Exception as e:
                    st.error(f"Error in analysis: {str(e)}")
                    st.error("Please try different words or check your input")

    # Help section
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        1. **Select languages** for comparison
        2. **Enter words or phrases** in both languages
        3. **Click Analyze** to see:
           - Similarity scores
           - Related concepts
           - Visual comparison
           
        **Tips:**
        - Try similar concepts across languages
        - Compare cultural terms
        - Look for patterns in semantic fields
        - Use example pairs to explore
        """)

if __name__ == "__main__":
    main()