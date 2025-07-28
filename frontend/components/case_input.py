# Streamlit component for case input
import streamlit as st

def render_case_input():
    """Render case input form component"""
    
    st.subheader("📝 Enter Case Details")
    
    with st.form("case_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            case_title = st.text_input("Case Title*", key="case_title")
            client_name = st.text_input("Client Name*", key="client_name")
        
        with col2:
            advocate_name = st.text_input("Advocate Name*", key="advocate_name")
            case_type = st.selectbox(
                "Case Type",
                ["Employment Dispute", "Contract Violation", "Harassment", "Other"]
            )
        
        tags = st.multiselect(
            "Tags",
            ["Harassment", "Unpaid Salary", "Wrongful Termination", "Discrimination"],
            key="case_tags"
        )
        
        incident_summary = st.text_area(
            "Incident Summary*",
            height=150,
            key="incident_summary"
        )
        
        submitted = st.form_submit_button("Generate Letter", type="primary")
        
        if submitted:
            return {
                "case_title": case_title,
                "client_name": client_name,
                "advocate_name": advocate_name,
                "case_type": case_type,
                "tags": tags,
                "incident_summary": incident_summary
            }
    
    return None
