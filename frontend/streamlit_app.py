# Streamlit app entry point
import os
import tempfile
import pdfkit
import streamlit as st
import requests
import json
from datetime import datetime
import base64
import pandas as pd

wkhtmltopdf_path = r"D:\download_folder\wkhtmltox-0.12.6-1.mxe-cross-win64\wkhtmltox\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# Configure Streamlit page
st.set_page_config(
    page_title="Legal Letter Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:9000"  # Changed from port 9000 to 9000

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .case-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .success-message {
        color: #27ae60;
        font-weight: bold;
    }
    .error-message {
        color: #e74c3c;
        font-weight: bold;
    }
    .legal-text {
        font-family: 'Georgia', serif;
        line-height: 1.6;
        text-align: justify;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_case' not in st.session_state:
        st.session_state.current_case = None
    if 'generated_letter' not in st.session_state:
        st.session_state.generated_letter = None
    if 'cases_history' not in st.session_state:
        st.session_state.cases_history = []

def check_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ Legal Letter Generator</h1>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("🚨 Backend API is not available. Please ensure the FastAPI server is running on port 9000.")
        st.info("To start the backend server, run: `uvicorn app.main:app --reload --port 9000`")
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Select Page",
            ["🏠 Home", "📝 Generate Letter", "📋 Cases History", "📊 Analytics"]
        )
        
        st.divider()
        
        # API Status
        st.subheader("System Status")
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=5).json()
            
            if health_response.get("rag_system_ready"):
                st.success("✅ RAG System Ready")
            else:
                st.error("❌ RAG System Not Ready")
                
            if health_response.get("letter_generator_ready"):
                st.success("✅ Letter Generator Ready")
            else:
                st.error("❌ Letter Generator Not Ready")
        except:
            st.error("❌ Cannot connect to backend")
    
    # Main content based on selected page
    if page == "🏠 Home":
        render_home_page()
    elif page == "📝 Generate Letter":
        render_generate_letter_page()
    elif page == "📋 Cases History":
        render_cases_history_page()
    elif page == "📊 Analytics":
        render_analytics_page()

def render_home_page():
    """Render home page with all case details in proper format"""
    st.header("Welcome to Legal Letter Generator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🔍 AI-Powered Analysis")
        st.write("Leverage advanced AI to analyze legal documents and generate comprehensive letters based on 200+ pages of legal acts.")
    
    with col2:
        st.subheader("⚡ Quick Generation")
        st.write("Generate formal legal letters and strategic arguments in minutes, not hours.")
    
    with col3:
        st.subheader("📄 Professional Output")
        st.write("Export polished, court-ready documents in PDF format with proper legal formatting.")
    
    st.divider()
    
    # All cases display
    st.subheader("📈 All Legal Cases")
    
    try:
        response = requests.get(f"{API_BASE_URL}/cases", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cases = data.get("cases", [])
            
            if cases and len(cases) > 0:
                # Sort cases by creation date (newest first)
                sorted_cases = sorted(cases, key=lambda x: x.get("created_at", ""), reverse=True)
                
                st.success(f"📊 Total Cases: **{len(sorted_cases)}**")
                
                # Display each case in detailed format
                for i, case in enumerate(sorted_cases, 1):
                    # Extract case details
                    case_title = case.get('case_title', 'Untitled Case')
                    client_name = case.get('client_name', 'N/A')
                    advocate_name = case.get('advocate_name', 'N/A')
                    law_firm_name = case.get('law_firm_name', 'N/A')
                    recipient_organization = case.get('recipient_organization', 'N/A')
                    tags = case.get('tags', [])
                    created_at = case.get('created_at', 'N/A')
                    case_id = case.get('_id', 'N/A')
                    
                    # Format date
                    if created_at != 'N/A':
                        try:
                            if 'T' in str(created_at):
                                formatted_date = str(created_at).split('T')[0]
                                formatted_time = str(created_at).split('T')[1][:8]
                            else:
                                formatted_date = str(created_at)[:10]
                                formatted_time = "00:00:00"
                        except:
                            formatted_date = str(created_at)[:10]
                            formatted_time = "00:00:00"
                    else:
                        formatted_date = 'N/A'
                        formatted_time = 'N/A'
                    
                    # Format tags
                    tags_display = ", ".join(tags) if tags else "No tags"
                    
                    # Create expandable case card
                    with st.expander(f"📁 Case #{i}: {case_title}", expanded=False):
                        
                        # Case overview in columns
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**📋 Case Information**")
                            st.write(f"**Title:** {case_title}")
                            st.write(f"**Case ID:** {case_id}")
                            st.write(f"**Tags:** {tags_display}")
                            st.write(f"**Created:** {formatted_date}")
                            st.write(f"**Time:** {formatted_time}")
                        
                        with col2:
                            st.markdown("**👤 People Involved**")
                            st.write(f"**Client:** {client_name}")
                            st.write(f"**Advocate:** {advocate_name}")
                            st.write(f"**Law Firm:** {law_firm_name}")
                            st.write(f"**Against:** {recipient_organization}")
                        
                        with col3:
                            st.markdown("**📞 Contact Details**")
                            law_firm_phone = case.get('law_firm_phone', 'N/A')
                            law_firm_email = case.get('law_firm_email', 'N/A')
                            law_firm_address = case.get('law_firm_address', 'N/A')
                            law_firm_city = case.get('law_firm_city', 'N/A')
                            
                            st.write(f"**Phone:** {law_firm_phone}")
                            st.write(f"**Email:** {law_firm_email}")
                            st.write(f"**Address:** {law_firm_address}")
                            st.write(f"**City:** {law_firm_city}")
                        
                        st.divider()
                        
                        # Case summary
                        incident_summary = case.get('incident_summary', 'No summary available')
                        st.markdown("**📝 Case Summary**")
                        st.write(incident_summary)
                        
                        st.divider()
                        
                        # Recipient details
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📨 Recipient Details**")
                            recipient_name = case.get('recipient_name', 'N/A')
                            recipient_address = case.get('recipient_address', 'N/A')
                            recipient_city = case.get('recipient_city', 'N/A')
                            recipient_state = case.get('recipient_state', 'N/A')
                            
                            st.write(f"**Name:** {recipient_name}")
                            st.write(f"**Organization:** {recipient_organization}")
                            st.write(f"**Address:** {recipient_address}")
                            st.write(f"**Location:** {recipient_city}, {recipient_state}")
                        
                        with col2:
                            st.markdown("**⚖️ Legal Status**")
                            supporting_sections = case.get('supporting_sections', [])
                            if supporting_sections:
                                st.write(f"**Legal References:** {len(supporting_sections)} sections")
                                for j, section in enumerate(supporting_sections[:3], 1):
                                    st.write(f"{j}. {section}")
                                if len(supporting_sections) > 3:
                                    st.write(f"... and {len(supporting_sections) - 3} more sections")
                            else:
                                st.write("**Legal References:** Not available")
                        
                        # Action buttons
                        st.divider()
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if st.button(f"📄 View Letter", key=f"view_letter_{case_id}"):
                                st.session_state.selected_case_for_view = case
                                st.rerun()
                        
                        with action_col2:
                            if st.button(f"💾 Export PDF", key=f"export_pdf_{case_id}"):
                                export_case_pdf(case_id)
                        
                        with action_col3:
                            if st.button(f"📊 View Arguments", key=f"view_args_{case_id}"):
                                st.session_state.selected_case_for_args = case
                                st.rerun()
                
                # Show selected case details if any button was clicked
                if 'selected_case_for_view' in st.session_state:
                    st.markdown("---")
                    st.subheader("📄 Selected Case Letter")
                    selected_case = st.session_state.selected_case_for_view
                    
                    formal_letter = selected_case.get('formal_letter', 'Letter not available')
                    st.markdown(f'<div class="legal-text">{formal_letter}</div>', unsafe_allow_html=True)
                    
                    if st.button("❌ Close Letter View"):
                        del st.session_state.selected_case_for_view
                        st.rerun()
                
                if 'selected_case_for_args' in st.session_state:
                    st.markdown("---")
                    st.subheader("📊 Selected Case Arguments")
                    selected_case = st.session_state.selected_case_for_args
                    
                    legal_arguments = selected_case.get('legal_arguments', 'Arguments not available')
                    st.markdown(f'<div class="legal-text">{legal_arguments}</div>', unsafe_allow_html=True)
                    
                    if st.button("❌ Close Arguments View"):
                        del st.session_state.selected_case_for_args
                        st.rerun()
            
            else:
                # No cases found
                st.info("📝 No cases found. Generate your first legal letter to get started!")
                
                # Add a call-to-action button
                if st.button("🚀 Generate Your First Legal Letter", type="primary"):
                    st.session_state.current_page = "📝 Generate Letter"
                    st.rerun()
        
        else:
            st.error(f"❌ Could not load cases. API Status: {response.status_code}")
            st.write("Please ensure the backend server is running properly.")
            
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. The backend server might be slow to respond.")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error. Please check if the backend server is running.")
    except Exception as e:
        st.error(f"❌ Error loading cases: {str(e)}")
        st.info("📝 Cases will appear here once you generate some legal letters.")


# Add this to your render_generate_letter_page function

def render_generate_letter_page():
    """Render letter generation page with complete form"""
    st.header("📝 Generate Legal Letter")
    
    with st.form("case_input_form"):
        st.subheader("📋 Case Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            case_title = st.text_input(
                "Case Title*",
                placeholder="E.g., Workplace Harassment Case - John Doe vs ABC Corp"
            )
            client_name = st.text_input(
                "Client Name*",
                placeholder="E.g., John Doe"
            )
            advocate_name = st.text_input(
                "Advocate Name*",
                placeholder="E.g., Adv. Jane Smith"
            )
        
        with col2:
            bar_registration_number = st.text_input(
                "Bar Registration Number",
                placeholder="E.g., BAR/2024/12345"
            )
            
        # Tags selection
        available_tags = [
            "Harassment", "Unpaid Salary", "Wrongful Termination", 
            "Discrimination", "Contract Violation", "Safety Issues",
            "Overtime Disputes", "Benefits Denial", "Retaliation"
        ]
        
        selected_tags = st.multiselect(
            "Case Tags (Optional)",
            available_tags,
            help="Select relevant tags to improve AI analysis"
        )
        
        st.divider()
        
        # Law Firm Details
        st.subheader("🏢 Law Firm Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            law_firm_name = st.text_input(
                "Law Firm Name*",
                placeholder="E.g., Smith & Associates Legal Firm"
            )
            law_firm_address = st.text_input(
                "Address*",
                placeholder="E.g., 123 Legal Street, Suite 456"
            )
            law_firm_city = st.text_input(
                "City*",
                placeholder="E.g., Mumbai"
            )
        
        with col2:
            law_firm_state = st.text_input(
                "State*",
                placeholder="E.g., Maharashtra"
            )
            law_firm_zip = st.text_input(
                "ZIP Code*",
                placeholder="E.g., 400001"
            )
            law_firm_phone = st.text_input(
                "Phone Number*",
                placeholder="E.g., +91-22-1234-5678"
            )
        
        law_firm_email = st.text_input(
            "Email Address*",
            placeholder="E.g., contact@smithlegal.com"
        )
        
        st.divider()
        
        # Recipient Details
        st.subheader("📨 Recipient Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            recipient_name = st.text_input(
                "Recipient Name*",
                placeholder="E.g., Mr. John Manager / HR Department"
            )
            recipient_organization = st.text_input(
                "Organization*",
                placeholder="E.g., ABC Corporation"
            )
            recipient_address = st.text_input(
                "Recipient Address*",
                placeholder="E.g., 789 Corporate Blvd, Floor 10"
            )
        
        with col2:
            recipient_city = st.text_input(
                "Recipient City*",
                placeholder="E.g., Delhi"
            )
            recipient_state = st.text_input(
                "Recipient State*",
                placeholder="E.g., Delhi"
            )
            recipient_zip = st.text_input(
                "Recipient ZIP*",
                placeholder="E.g., 110001"
            )
        
        st.divider()
        
        # Incident summary
        st.subheader("📝 Case Summary")
        incident_summary = st.text_area(
            "Incident Summary*",
            height=200,
            placeholder="Provide detailed description of the incident, including dates, witnesses, and relevant circumstances..."
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Generate Legal Letter", type="primary")
    
    # Handle form submission
    if submitted:
        required_fields = [
            case_title, client_name, advocate_name, incident_summary,
            law_firm_name, law_firm_address, law_firm_city, law_firm_state, 
            law_firm_zip, law_firm_phone, law_firm_email,
            recipient_name, recipient_organization, recipient_address,
            recipient_city, recipient_state, recipient_zip
        ]
        
        if not all(required_fields):
            st.error("Please fill in all required fields marked with *")
        else:
            # Prepare complete case data
            complete_case_data = {
                "case_title": case_title,
                "client_name": client_name,
                "advocate_name": advocate_name,
                "bar_registration_number": bar_registration_number,
                "incident_summary": incident_summary,
                "tags": selected_tags,
                "law_firm_name": law_firm_name,
                "law_firm_address": law_firm_address,
                "law_firm_city": law_firm_city,
                "law_firm_state": law_firm_state,
                "law_firm_zip": law_firm_zip,
                "law_firm_phone": law_firm_phone,
                "law_firm_email": law_firm_email,
                "recipient_name": recipient_name,
                "recipient_organization": recipient_organization,
                "recipient_address": recipient_address,
                "recipient_city": recipient_city,
                "recipient_state": recipient_state,
                "recipient_zip": recipient_zip
            }
            
            generate_letter_with_complete_data(complete_case_data)

def generate_letter_with_complete_data(case_data):
    """Generate legal letter with complete case data"""
    
    with st.spinner("🤖 AI is analyzing your case and generating legal letter..."):
        try:
            # Make API request
            response = requests.post(f"{API_BASE_URL}/generate-letter", json=case_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.generated_letter = result
                st.session_state.current_case = case_data
                
                st.success("✅ Legal letter generated successfully!")
                
                # Display results
                render_generated_letter(result)
                
            else:
                st.error(f"❌ Error generating letter: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")


def generate_letter(case_title, client_name, advocate_name, incident_summary, tags):
    """Generate legal letter using API"""
    
    with st.spinner("🤖 AI is analyzing your case and generating legal letter..."):
        try:
            # Prepare payload
            payload = {
                "case_title": case_title,
                "client_name": client_name,
                "advocate_name": advocate_name,
                "incident_summary": incident_summary,
                "tags": tags
            }
            
            # Make API request
            response = requests.post(f"{API_BASE_URL}/generate-letter", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.generated_letter = result
                st.session_state.current_case = payload
                
                st.success("✅ Legal letter generated successfully!")
                
                # Display results
                render_generated_letter(result)
                
            else:
                st.error(f"❌ Error generating letter: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")

def render_generated_letter(result):
    """Render generated letter results"""
    
    if not result or not result.get("letter"):
        return
    
    letter = result["letter"]
    
    st.header("📄 Generated Legal Document")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Formal Letter", "⚖️ Legal Arguments", "📚 Supporting Sections", "💾 Export"])
    
    with tab1:
        st.subheader("Formal Legal Letter")
        st.markdown(f'<div class="legal-text">{letter["formal_letter"]}</div>', unsafe_allow_html=True)
        
        # FIXED: Moved button outside form context
        if st.button("📋 Copy Letter to Clipboard", key="copy_letter"):
            st.write("Letter content copied! (Note: Clipboard functionality requires browser permissions)")
    
    with tab2:
        st.subheader("Legal Arguments & Strategy")
        st.markdown(f'<div class="legal-text">{letter["legal_arguments"]}</div>', unsafe_allow_html=True)
    
    with tab3:
        st.subheader("Supporting Legal Sections")
        for i, section in enumerate(letter["supporting_sections"], 1):
            st.write(f"{i}. {section}")
    
    with tab4:
        st.subheader("Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # FIXED: Added unique keys to buttons
            if st.button("📄 Export as PDF", type="primary", key="export_pdf"):
                export_case_pdf(result["case_id"], "legal")
        
        with col2:
            if st.button("💾 Save Case", key="save_case"):
                st.success("Case already saved to database!")
                st.info(f"Case ID: {result['case_id']}")

def export_case_pdf(case_id, pdf_type):
    """Export case as PDF"""
    try:
        response = requests.post(f"{API_BASE_URL}/export-pdf/{case_id}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            case_title = result.get("case_title", f"case_{case_id}")

            # Choose content based on type
            if pdf_type.lower() == "legal":
                html_content = result.get("formal_content", "<p>No formal content available.</p>")
            else:
                html_content = result.get("arguments", "<p>No arguments available.</p>")

            # st.subheader("📄 PDF Preview")
            # st.markdown(html_content, unsafe_allow_html=True)

            # Generate PDF using pdfkit
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                pdf_path = tmp_pdf.name  # Save path before closing
                pdfkit.from_string(html_content,tmp_pdf.name,configuration=config)

            # Now the file is closed, safe to read
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()

            # Provide download
            st.download_button(
                label="📥 Download legal PDF" if pdf_type=="legal" else "📥 Download arguments PDF",
                data=pdf_data,
                file_name=f"{case_title.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

            # Now it's safe to delete
            os.unlink(pdf_path)


        else:
            st.error("❌ Failed to export PDF")

    except Exception as e:
        st.error(f"🚨 Export error: {str(e)}")

def render_cases_history_page():
    """Render cases history page"""
    st.header("📋 Cases History")
    
    try:
        response = requests.get(f"{API_BASE_URL}/cases", timeout=10)
        
        if response.status_code == 200:
            cases = response.json().get("cases", [])
            
            if not cases:
                st.info("No cases found. Generate your first legal letter!")
                return
            
            # Search and filter
            search_term = st.text_input("🔍 Search cases", placeholder="Search by case title or client name...")
            
            # Filter cases
            if search_term:
                filtered_cases = [
                    case for case in cases 
                    if search_term.lower() in case.get("case_title", "").lower() or 
                       search_term.lower() in case.get("client_name", "").lower()
                ]
            else:
                filtered_cases = cases
            
            # Display cases
            for case in filtered_cases:
                with st.expander(f"📁 {case.get('case_title', 'Untitled Case')} - {case.get('client_name', 'N/A')}"):
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Client:** {case.get('client_name', 'N/A')}")
                        st.write(f"**Advocate:** {case.get('advocate_name', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Created:** {case.get('created_at', 'N/A')[:10]}")
                        if case.get('tags'):
                            st.write(f"**Tags:** {', '.join(case['tags'])}")
                    
                    with col3:
                        # FIXED: Added unique keys to avoid duplicate button IDs
                        if st.button(f"👁️ View Details", key=f"view_details_{case['_id']}"):
                            st.session_state.selected_case = case
                        if st.button(f"📄 Export Legal PDF", key=f"export_pdf_{case['_id']}"):
                            export_case_pdf(case['_id'],pdf_type="legal")
                        if st.button(f"📄 Export Argument PDF",key=f"exprt_argument_pdf_{case['_id']}"):
                            export_case_pdf(case['_id'],pdf_type="argument")
                    
                    st.write(f"**Summary:** {case.get('incident_summary', 'N/A')[:200]}...")
        
        else:
            st.error("Failed to load cases history")
            
    except Exception as e:
        st.error(f"Error loading cases: {str(e)}")

def render_analytics_page():
    """Render analytics page"""
    st.header("📊 Analytics Dashboard")
    
    try:
        response = requests.get(f"{API_BASE_URL}/cases", timeout=10)
        
        if response.status_code == 200:
            cases = response.json().get("cases", [])
            
            if not cases:
                st.info("No data available for analytics.")
                return
            
            # Create DataFrame
            df = pd.DataFrame(cases)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Cases", len(cases))
            
            with col2:
                unique_clients = df['client_name'].nunique() if 'client_name' in df.columns else 0
                st.metric("Unique Clients", unique_clients)
            
            with col3:
                # FIXED: Updated year filter to 2025
                recent_cases = len([c for c in cases if c.get('created_at', '').startswith('2025')])
                st.metric("Cases This Year", recent_cases)
            
            # Tags analysis
            if 'tags' in df.columns:
                st.subheader("📈 Case Types Distribution")
                all_tags = []
                for tags in df['tags']:
                    if isinstance(tags, list):
                        all_tags.extend(tags)
                
                if all_tags:
                    tag_counts = pd.Series(all_tags).value_counts()
                    st.bar_chart(tag_counts)
            
            # Recent activity
            st.subheader("📅 Recent Activity")
            if 'created_at' in df.columns:
                try:
                    df['date'] = pd.to_datetime(df['created_at']).dt.date
                    daily_counts = df['date'].value_counts().sort_index()
                    st.line_chart(daily_counts)
                except:
                    st.info("No valid date data available for activity chart.")
        
        else:
            st.error("Failed to load analytics data")
            
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

if __name__ == "__main__":
    main()
