import json
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from backend.state import AgentGraphState
from backend.utils.llm import initialize_llm


def cover_letter_analyst(state: AgentGraphState) -> Dict[str, Any]:
    """
    Cover Letter Expert Agent
    
    Role: Evaluates cover letter for clarity, motivation, and originality.
    Input: Cover letter text
    Output: cover_letter_score dict with score, findings, and thought_process
    """
    llm = initialize_llm()
    
    job_application = state["job_application"]
    cover_letter_text = job_application.get("cover_letter", {}).get("text", "")
    company_name = job_application.get("job_description", {}).get("company_name", "Unknown Company")
    role = job_application.get("job_description", {}).get("role", "Unknown Role")
    
    prompt_template = PromptTemplate(
        input_variables=["cover_letter_text", "company_name", "role"],
        template="""You are an expert Communication Specialist evaluating cover letters.

COVER LETTER:
{cover_letter_text}

TARGET COMPANY: {company_name}
TARGET ROLE: {role}

Evaluate the cover letter on:
1. Clarity and writing quality
2. Genuine motivation vs. generic copy-paste content
3. Specific company/role mention
4. Passion and enthusiasm for the role
5. Professionalism

Provide a JSON response:
{{
    "score": <0-100 numeric score>,
    "clarity_rating": <1-10>,
    "motivation_level": "<Low/Medium/High - is this genuine or generic?>",
    "company_mention_specificity": "<Generic/Somewhat Specific/Highly Specific>",
    "red_flags": [<any concerns like repetitive language, no research>],
    "strengths": [<what makes this letter stand out>],
    "thought_process": "<First-person explanation, e.g., 'I noticed the applicant specifically mentioned...'"
}}

Return ONLY valid JSON, no other text."""
    )
    
    chain = prompt_template | llm
    
    try:
        response = chain.invoke({
            "cover_letter_text": cover_letter_text,
            "company_name": company_name,
            "role": role
        })
        
        result = json.loads(response.content)
        
        return {
            "cover_letter_score": result
        }
    except json.JSONDecodeError:
        return {
            "cover_letter_score": {
                "score": 0,
                "clarity_rating": 0,
                "motivation_level": "Unknown",
                "company_mention_specificity": "Unknown",
                "red_flags": ["Failed to parse cover letter"],
                "strengths": [],
                "thought_process": "I encountered an error while analyzing the cover letter. Please check the format."
            }
        }
    except Exception as e:
        return {
            "cover_letter_score": {
                "score": 0,
                "clarity_rating": 0,
                "motivation_level": "Unknown",
                "company_mention_specificity": "Unknown",
                "red_flags": [f"Error: {str(e)}"],
                "strengths": [],
                "thought_process": f"I encountered an error: {str(e)}"
            }
        }
