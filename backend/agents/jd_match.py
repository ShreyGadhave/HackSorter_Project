import json
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from backend.state import AgentGraphState
from backend.utils.llm import initialize_llm


def jd_match_analyst(state: AgentGraphState) -> Dict[str, Any]:
    """
    JD Match Agent (Tech Hiring Manager)
    
    Role: Strict line-by-line skill comparison between resume and JD.
    Input: Resume text and required skills list
    Output: jd_match_score dict with score, matched/missing skills, and thought_process
    """
    llm = initialize_llm()
    
    job_application = state["job_application"]
    resume_text = job_application.get("resume", {}).get("text", "")
    jd = job_application.get("job_description", {})
    required_skills = jd.get("skills_required", [])
    nice_to_have = jd.get("skills_nice_to_have", [])
    
    # Format skills for prompt
    required_str = ", ".join(required_skills) if required_skills else "None specified"
    nice_to_have_str = ", ".join(nice_to_have) if nice_to_have else "None specified"
    
    prompt_template = PromptTemplate(
        input_variables=["resume_text", "required_skills", "nice_to_have_skills"],
        template="""You are a strict Tech Hiring Manager evaluating technical fit.

RESUME:
{resume_text}

REQUIRED SKILLS (Must Have):
{required_skills}

NICE TO HAVE SKILLS:
{nice_to_have_skills}

Perform a line-by-line comparison. For each required skill, determine if it's clearly mentioned in the resume.

Provide a JSON response:
{{
    "score": <0-100 numeric score based on skill match>,
    "required_skills_matched": [<skills found in resume>],
    "required_skills_missing": [<required skills NOT in resume>],
    "nice_to_have_matched": [<nice-to-have skills found>],
    "match_percentage": <0-100 percentage of required skills found>,
    "skill_depth_assessment": "<Novice/Intermediate/Expert level inferred from resume>",
    "thought_process": "<First-person explanation, e.g., 'I checked each required skill and found Python, Java, but no Kubernetes. The match is...'"
}}

Return ONLY valid JSON, no other text."""
    )
    
    chain = prompt_template | llm
    
    try:
        response = chain.invoke({
            "resume_text": resume_text,
            "required_skills": required_str,
            "nice_to_have_skills": nice_to_have_str
        })
        
        result = json.loads(response.content)
        
        return {
            "jd_match_score": result
        }
    except json.JSONDecodeError:
        return {
            "jd_match_score": {
                "score": 0,
                "required_skills_matched": [],
                "required_skills_missing": required_skills,
                "nice_to_have_matched": [],
                "match_percentage": 0,
                "skill_depth_assessment": "Unknown",
                "thought_process": "I encountered an error while analyzing the skill match. Please check the format."
            }
        }
    except Exception as e:
        return {
            "jd_match_score": {
                "score": 0,
                "required_skills_matched": [],
                "required_skills_missing": required_skills,
                "nice_to_have_matched": [],
                "match_percentage": 0,
                "skill_depth_assessment": "Unknown",
                "thought_process": f"I encountered an error: {str(e)}"
            }
        }
