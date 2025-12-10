import json
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from backend.state import AgentGraphState
from backend.utils.llm import initialize_llm


def resume_analyst(state: AgentGraphState) -> Dict[str, Any]:
    """
    Resume Analyst Agent
    
    Role: Evaluates resume for strengths, weaknesses, and seniority fit.
    Input: Resume text and Job Description
    Output: resume_score dict with score, analysis, and thought_process
    """
    llm = initialize_llm()
    
    job_application = state["job_application"]
    resume_text = job_application.get("resume", {}).get("text", "")
    jd = job_application.get("job_description", {})
    jd_text = jd.get("description", "")
    jd_seniority = jd.get("seniority_level", "Mid-Level")
    
    prompt_template = PromptTemplate(
        input_variables=["resume_text", "jd_text", "jd_seniority"],
        template="""You are an expert Resume Analyst. Analyze the following resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Required Seniority Level: {jd_seniority}

Provide a JSON response with the following structure:
{{
    "score": <0-100 numeric score>,
    "strengths": [<list of key strengths found in the resume>],
    "weaknesses": [<list of gaps or concerns>],
    "seniority_fit": "<Junior/Mid-Level/Senior/Executive - match with JD requirement>",
    "experience_years": <estimated years from resume>,
    "thought_process": "<First-person explanation, e.g., 'I analyzed the resume and found...'>"
}}

Return ONLY valid JSON, no other text."""
    )
    
    chain = prompt_template | llm
    
    try:
        response = chain.invoke({
            "resume_text": resume_text,
            "jd_text": jd_text,
            "jd_seniority": jd_seniority
        })
        
        # Parse JSON from response
        result = json.loads(response.content)
        
        return {
            "resume_score": result
        }
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "resume_score": {
                "score": 0,
                "strengths": [],
                "weaknesses": ["Failed to parse resume"],
                "seniority_fit": "Unknown",
                "experience_years": 0,
                "thought_process": "I encountered an error while analyzing the resume. Please check the format."
            }
        }
    except Exception as e:
        return {
            "resume_score": {
                "score": 0,
                "strengths": [],
                "weaknesses": [f"Error: {str(e)}"],
                "seniority_fit": "Unknown",
                "experience_years": 0,
                "thought_process": f"I encountered an error: {str(e)}"
            }
        }
