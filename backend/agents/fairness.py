import json
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from backend.state import AgentGraphState
from backend.utils.llm import initialize_llm


def fairness_auditor(state: AgentGraphState) -> Dict[str, Any]:
    """
    Fairness Agent (DEI & Ethics Officer)
    
    Role: Audits all previous agent scores for bias and discrimination.
    Input: All agent scores (resume, github, jd_match, etc.) + candidate personal_info
    Output: fairness_audit dict with bias detection and score adjustments
    """
    llm = initialize_llm()
    
    job_application = state["job_application"]
    personal_info = job_application.get("personal_info", {})
    candidate_name = personal_info.get("name", "Unknown")
    candidate_location = personal_info.get("location", {})
    gender = personal_info.get("gender", "Not disclosed")
    age = personal_info.get("age", "Not disclosed")
    
    # Collect all scores from previous agents
    resume_score = state.get("resume_score", {})
    cover_letter_score = state.get("cover_letter_score", {})
    jd_match_score = state.get("jd_match_score", {})
    github_score = state.get("github_score", {})
    location_score = state.get("location_score", {})
    
    # Format scores for analysis
    scores_summary = {
        "resume_score": resume_score.get("score", 0),
        "cover_letter_score": cover_letter_score.get("score", 0),
        "jd_match_score": jd_match_score.get("score", 0),
        "github_score": github_score.get("score", 0),
        "location_score": location_score.get("score", 0)
    }
    
    prompt_template = PromptTemplate(
        input_variables=["candidate_name", "candidate_location", "gender", "age", "scores_summary", "all_scores"],
        template="""You are a DEI & Ethics Officer auditing hiring decisions for bias.

CANDIDATE INFORMATION:
- Name: {candidate_name}
- Location: {candidate_location}
- Gender: {gender}
- Age: {age}

AGENT SCORES:
{scores_summary}

DETAILED SCORES:
{all_scores}

Audit for potential biases:
1. NAME BIAS: Does the name suggest ethnicity/gender that could introduce prejudice?
2. LOCATION BIAS: Is location being weighted unfairly? (e.g., remote job but scoring location heavily)
3. GENDER/AGE BIAS: Are scores inconsistent in ways that correlate with protected characteristics?
4. SCORE INCONSISTENCIES: For example, if GitHub score is high but Resume score is low (possible name bias?), flag this.
5. FAIRNESS OF WEIGHTING: Are all agents equally weighted or is one agent's bias dominating?

Provide a JSON response:
{{
    "bias_detected": <true/false - did you find potential bias patterns?>,
    "bias_types_found": [<list of bias types: name bias, location bias, etc.>],
    "score_adjustments": {{
        "resume_adjustment": <-10 to +10 adjustment if biased>,
        "github_adjustment": <-10 to +10 adjustment if biased>,
        "jd_match_adjustment": <-10 to +10 adjustment if biased>,
        "cover_letter_adjustment": <-10 to +10 adjustment if biased>,
        "location_adjustment": <-10 to +10 adjustment if biased>
    }},
    "total_adjustment": <sum of all adjustments>,
    "concerns": [<specific concerns identified>],
    "recommendations": [<recommendations to reduce bias>],
    "thought_process": "<First-person explanation, e.g., 'I reviewed all agent scores and noticed the Resume Agent gave a low score while GitHub Agent gave high. This could indicate name-based bias. I am recommending a +5 adjustment to the resume score...'"
}}

Return ONLY valid JSON, no other text."""
    )
    
    chain = prompt_template | llm
    
    try:
        response = chain.invoke({
            "candidate_name": candidate_name,
            "candidate_location": str(candidate_location),
            "gender": gender,
            "age": str(age),
            "scores_summary": json.dumps(scores_summary, indent=2),
            "all_scores": json.dumps({
                "resume_score": resume_score,
                "cover_letter_score": cover_letter_score,
                "jd_match_score": jd_match_score,
                "github_score": github_score,
                "location_score": location_score
            }, indent=2)
        })
        
        result = json.loads(response.content)
        
        return {
            "fairness_audit": result
        }
    except json.JSONDecodeError:
        return {
            "fairness_audit": {
                "bias_detected": False,
                "bias_types_found": [],
                "score_adjustments": {
                    "resume_adjustment": 0,
                    "github_adjustment": 0,
                    "jd_match_adjustment": 0,
                    "cover_letter_adjustment": 0,
                    "location_adjustment": 0
                },
                "total_adjustment": 0,
                "concerns": ["Failed to parse fairness audit"],
                "recommendations": ["Please check data format"],
                "thought_process": "I encountered an error while performing the fairness audit. Please check the data format."
            }
        }
    except Exception as e:
        return {
            "fairness_audit": {
                "bias_detected": False,
                "bias_types_found": [],
                "score_adjustments": {
                    "resume_adjustment": 0,
                    "github_adjustment": 0,
                    "jd_match_adjustment": 0,
                    "cover_letter_adjustment": 0,
                    "location_adjustment": 0
                },
                "total_adjustment": 0,
                "concerns": [f"Error: {str(e)}"],
                "recommendations": [],
                "thought_process": f"I encountered an error: {str(e)}"
            }
        }
