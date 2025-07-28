# Streamlit component for letter preview
import streamlit as st

def render_letter_preview(letter_data):
    """Render letter preview component"""
    
    if not letter_data:
        return
    
    st.subheader("📄 Generated Letter Preview")
    
    tabs = st.tabs(["Formal Letter", "Legal Arguments", "Supporting Sections"])
    
    with tabs[0]:
        st.markdown("### Formal Legal Letter")
        st.text_area(
            "Letter Content",
            value=letter_data.get("formal_letter", ""),
            height=400,
            key="letter_preview"
        )
    
    with tabs[1]:
        st.markdown("### Legal Arguments")
        st.text_area(
            "Arguments",
            value=letter_data.get("legal_arguments", ""),
            height=300,
            key="arguments_preview"
        )
    
    with tabs[2]:
        st.markdown("### Supporting Legal Sections")
        for i, section in enumerate(letter_data.get("supporting_sections", []), 1):
            st.write(f"{i}. {section}")
