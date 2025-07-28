from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CaseInput(BaseModel):
    case_title: str
    incident_summary: str
    tags: Optional[List[str]] = []
    advocate_name: str
    client_name: str
    
    # Law Firm Details
    law_firm_name: str
    law_firm_address: str
    law_firm_city: str
    law_firm_state: str
    law_firm_zip: str
    law_firm_phone: str
    law_firm_email: str
    bar_registration_number: Optional[str] = ""
    
    # Recipient Details
    recipient_name: str
    recipient_organization: str
    recipient_address: str
    recipient_city: str
    recipient_state: str
    recipient_zip: str
    
class GeneratedLetter(BaseModel):
    case_id: str
    case_title: str
    formal_letter: str
    legal_arguments: str
    supporting_sections: List[str]
    created_at: datetime
    
class CaseResponse(BaseModel):
    success: bool
    message: str
    case_id: Optional[str] = None
    letter: Optional[GeneratedLetter] = None
