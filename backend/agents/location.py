import json
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from backend.state import AgentGraphState
from backend.utils.llm import initialize_llm


def location_coordinator(state: AgentGraphState) -> Dict[str, Any]:
    """
    Location Coordinator Agent (Logistics Manager)
    
    Role: Evaluates location fit between candidate and job requirements.
    Input: Applicant location, job location requirement, willingness to relocate
    Output: location_score dict with score, feasibility, and thought_process
    """
    llm = initialize_llm()
    
    job_application = state["job_application"]
    
    # Applicant location info
    applicant_location = job_application.get("personal_info", {}).get("location", {})
    applicant_city = applicant_location.get("city", "Unknown")
    applicant_country = applicant_location.get("country", "Unknown")
    willing_to_relocate = job_application.get("personal_info", {}).get("willing_to_relocate", False)
    
    # Job location requirement
    job_description = job_application.get("job_description", {})
    job_location_type = job_description.get("location_type", "Unknown")  # Remote, On-site, Hybrid
    job_location = job_description.get("location", {})
    job_city = job_location.get("city", "Unknown")
    job_country = job_location.get("country", "Unknown")
    
    prompt_template = PromptTemplate(
        input_variables=[
            "applicant_city",
            "applicant_country",
            "willing_to_relocate",
            "job_location_type",
            "job_city",
            "job_country"
        ],
        template="""You are a Logistics Coordinator evaluating location fit for a job placement.

APPLICANT LOCATION:
- City: {applicant_city}
- Country: {applicant_country}
- Willing to Relocate: {willing_to_relocate}

JOB REQUIREMENT:
- Location Type: {job_location_type}
- City: {job_city}
- Country: {job_country}

Evaluation Rules:
1. If job is REMOTE: Location is irrelevant, score is high unless other issues
2. If job is ON-SITE:
   - Same city/country: Ideal, highest score
   - Different city, same country: Feasible if willing to relocate
   - Different country: Requires visa sponsorship (major concern)
   - NOT willing to relocate: Score is low
3. If job is HYBRID: Similar logic as on-site but slightly more flexible

Provide a JSON response:
{{
    "score": <0-100 numeric score>,
    "location_match": "<Exact Match/Same Country/Different Country/Remote OK>",
    "feasibility": "<Ideal/Feasible/Challenging/Not Feasible>",
    "relocation_required": <true/false>,
    "visa_sponsorship_needed": <true/false>,
    "commute_feasibility": "<Not applicable/Short/Moderate/Long>",
    "risk_factors": [<any concerns like visa complexity, long commute>],
    "thought_process": "<First-person explanation, e.g., 'I see the applicant is in {applicant_city} and the job is in {job_city}. Since it's {job_location_type}, ...'"
}}

Return ONLY valid JSON, no other text."""
    )
    
    chain = prompt_template | llm
    
    try:
        response = chain.invoke({
            "applicant_city": applicant_city,
            "applicant_country": applicant_country,
            "willing_to_relocate": str(willing_to_relocate),
            "job_location_type": job_location_type,
            "job_city": job_city,
            "job_country": job_country
        })
        
        result = json.loads(response.content)
        
        return {
            "location_score": result
        }
    except json.JSONDecodeError:
        return {
            "location_score": {
                "score": 50,
                "location_match": "Unknown",
                "feasibility": "Unknown",
                "relocation_required": False,
                "visa_sponsorship_needed": False,
                "commute_feasibility": "Unknown",
                "risk_factors": ["Failed to parse location data"],
                "thought_process": "I encountered an error while analyzing location fit. Please check the data format."
            }
        }
    except Exception as e:
        return {
            "location_score": {
                "score": 50,
                "location_match": "Unknown",
                "feasibility": "Unknown",
                "relocation_required": False,
                "visa_sponsorship_needed": False,
                "commute_feasibility": "Unknown",
                "risk_factors": [f"Error: {str(e)}"],
                "thought_process": f"I encountered an error: {str(e)}"
            }
        }
