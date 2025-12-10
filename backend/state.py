from typing import TypedDict, Dict, Any


class AgentGraphState(TypedDict):
    """
    Shared state for the Multi-Agent Hiring System.
    
    All agents read from job_application and write to their respective scoring keys.
    The Fairness Agent reads all scores and outputs fairness_audit.
    The Referee Agent reads all and outputs final_verdict.
    """
    
    # Input: Read-only job application data
    job_application: Dict[str, Any]
    
    # Dynamic hiring criteria (custom weights and strictness)
    hiring_criteria: Dict[str, Any]
    
    # Layer 1 (Parallel Analysts) - Scoring Outputs
    resume_score: Dict[str, Any]
    cover_letter_score: Dict[str, Any]
    jd_match_score: Dict[str, Any]
    github_score: Dict[str, Any]
    location_score: Dict[str, Any]
    
    # Layer 2 (Fairness Auditor)
    fairness_audit: Dict[str, Any]
    
    # Layer 3 (Final Verdict)
    final_verdict: Dict[str, Any]
