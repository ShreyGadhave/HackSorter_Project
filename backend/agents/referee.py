import json
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from backend.state import AgentGraphState
from backend.utils.llm import initialize_llm


def referee_agent(state: AgentGraphState) -> Dict[str, Any]:
    """
    Referee Agent (VP of Engineering - Final Decision Maker)
    
    Role: Makes the final hiring decision based on all agent inputs.
    Input: All agent scores + fairness audit + dynamic hiring criteria
    Output: final_verdict dict with final_score, verdict, and detailed reasoning
    """
    llm = initialize_llm()
    
    # Collect all scores
    resume_score = state.get("resume_score", {}).get("score", 0)
    cover_letter_score = state.get("cover_letter_score", {}).get("score", 0)
    jd_match_score = state.get("jd_match_score", {}).get("score", 0)
    github_score = state.get("github_score", {}).get("score", 0)
    location_score = state.get("location_score", {}).get("score", 0)
    
    # Get dynamic hiring criteria with fallback defaults
    hiring_criteria = state.get("hiring_criteria", {})
    weights = hiring_criteria.get("weights", {
        "resume": 0.2,
        "cover_letter": 0.15,
        "jd_match": 0.3,
        "github": 0.2,
        "location": 0.15
    })
    strictness = hiring_criteria.get("strictness", "medium")
    
    # Normalize weights to ensure they sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}
    
    # Fairness adjustments
    fairness_audit = state.get("fairness_audit", {})
    adjustments = fairness_audit.get("score_adjustments", {})
    total_fairness_adjustment = fairness_audit.get("total_adjustment", 0)
    bias_detected = fairness_audit.get("bias_detected", False)
    
    # All detailed information
    job_application = state["job_application"]
    candidate_name = job_application.get("personal_info", {}).get("name", "Unknown")
    job_role = job_application.get("job_description", {}).get("role", "Unknown")
    company_name = job_application.get("job_description", {}).get("company_name", "Unknown")
    
    # Format weights for prompt
    weights_str = "\n".join([
        f"- {k.replace('_', ' ').title()}: {v:.0%} (Score: {state.get(f'{k}_score', {}).get('score', 0)})"
        for k, v in weights.items()
    ])
    
    prompt_template = PromptTemplate(
        input_variables=[
            "candidate_name",
            "company_name",
            "job_role",
            "weights_str",
            "jd_match_score",
            "github_score",
            "resume_score",
            "cover_letter_score",
            "location_score",
            "fairness_adjustment",
            "bias_detected",
            "fairness_details",
            "strictness"
        ],
        template="""You are the VP of Engineering making the final hiring decision.

CANDIDATE: {candidate_name}
POSITION: {job_role} at {company_name}

CUSTOM HIRING CRITERIA (Company-Defined Weights):
{weights_str}

STRICTNESS LEVEL: {strictness} (high=>85 threshold, medium=>75, low=>60)

AGENT SCORES:
- JD Match: {jd_match_score}
- GitHub Portfolio: {github_score}
- Resume: {resume_score}
- Cover Letter: {cover_letter_score}
- Location Fit: {location_score}

FAIRNESS AUDIT:
- Bias Detected: {bias_detected}
- Total Score Adjustment (from bias mitigation): {fairness_adjustment}
- Details: {fairness_details}

DECISION RULES (Based on Strictness):
- HIGH: Score > 85 = SHORTLISTED, 70-85 = MAYBE, < 70 = REJECTED
- MEDIUM: Score > 75 = SHORTLISTED, 60-75 = MAYBE, < 60 = REJECTED
- LOW: Score > 60 = SHORTLISTED, 45-60 = MAYBE, < 45 = REJECTED

Provide a JSON response:
{{
    "final_score": <0-100 numeric final score after fairness adjustment>,
    "verdict": "<SHORTLISTED/MAYBE/REJECTED>",
    "weighted_scores": {{
        "jd_match_weighted": <jd_match_score * weight>,
        "github_weighted": <github_score * weight>,
        "resume_weighted": <resume_score * weight>,
        "cover_letter_weighted": <cover_letter_score * weight>,
        "location_weighted": <location_score * weight>
    }},
    "fairness_adjustment_applied": {fairness_adjustment},
    "decision_reasoning": "<Explanation of weighted scores and why this verdict>",
    "key_strengths": [<top 2-3 strengths>],
    "key_concerns": [<top 2-3 concerns if any>],
    "next_steps": "<Action if SHORTLISTED, concern if MAYBE, explanation if REJECTED>",
    "thought_process": "<First-person explanation of the decision based on custom weights and strictness level>"
}}

Return ONLY valid JSON, no other text."""
    )
    
    chain = prompt_template | llm
    
    # Calculate weighted score for reference using dynamic weights
    weighted_before_fairness = (
        (jd_match_score * weights.get("jd_match", 0.3)) +
        (github_score * weights.get("github", 0.2)) +
        (resume_score * weights.get("resume", 0.2)) +
        (cover_letter_score * weights.get("cover_letter", 0.15)) +
        (location_score * weights.get("location", 0.15))
    )
    
    try:
        response = chain.invoke({
            "candidate_name": candidate_name,
            "company_name": company_name,
            "job_role": job_role,
            "weights_str": weights_str,
            "jd_match_score": jd_match_score,
            "github_score": github_score,
            "resume_score": resume_score,
            "cover_letter_score": cover_letter_score,
            "location_score": location_score,
            "fairness_adjustment": total_fairness_adjustment,
            "bias_detected": str(bias_detected),
            "fairness_details": json.dumps(fairness_audit, indent=2),
            "strictness": strictness
        })
        
        result = json.loads(response.content)
        
        return {
            "final_verdict": result
        }
    except json.JSONDecodeError:
        return {
            "final_verdict": {
                "final_score": weighted_before_fairness + total_fairness_adjustment,
                "verdict": "MAYBE",
                "weighted_scores": {
                    "jd_match_weighted": jd_match_score * weights.get("jd_match", 0.3),
                    "github_weighted": github_score * weights.get("github", 0.2),
                    "resume_weighted": resume_score * weights.get("resume", 0.2),
                    "cover_letter_weighted": cover_letter_score * weights.get("cover_letter", 0.15),
                    "location_weighted": location_score * weights.get("location", 0.15)
                },
                "fairness_adjustment_applied": total_fairness_adjustment,
                "decision_reasoning": "Unable to parse full reasoning due to data format error.",
                "key_strengths": [],
                "key_concerns": ["Data format error in analysis"],
                "next_steps": "Please review data and rerun analysis.",
                "thought_process": "I encountered an error while making the final decision using the custom weights. The preliminary weighted score is approximately the calculated value, but please check the data format."
            }
        }
    except Exception as e:
        return {
            "final_verdict": {
                "final_score": weighted_before_fairness + total_fairness_adjustment,
                "verdict": "MAYBE",
                "weighted_scores": {
                    "jd_match_weighted": jd_match_score * weights.get("jd_match", 0.3),
                    "github_weighted": github_score * weights.get("github", 0.2),
                    "resume_weighted": resume_score * weights.get("resume", 0.2),
                    "cover_letter_weighted": cover_letter_score * weights.get("cover_letter", 0.15),
                    "location_weighted": location_score * weights.get("location", 0.15)
                },
                "fairness_adjustment_applied": total_fairness_adjustment,
                "decision_reasoning": f"Error: {str(e)}",
                "key_strengths": [],
                "key_concerns": [f"Error: {str(e)}"],
                "next_steps": "Please review the error and rerun analysis.",
                "thought_process": f"I encountered an error while applying custom weights: {str(e)}"
            }
        }
