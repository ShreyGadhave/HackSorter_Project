from langgraph.graph import StateGraph, START, END
from backend.state import AgentGraphState
from backend.agents.resume import resume_analyst
from backend.agents.cover_letter import cover_letter_analyst
from backend.agents.jd_match import jd_match_analyst
from backend.agents.github import github_analyst
from backend.agents.location import location_coordinator
from backend.agents.fairness import fairness_auditor
from backend.agents.referee import referee_agent


def build_hiring_graph():
    """
    Build the Multi-Agent Hiring System Graph using LangGraph.
    
    Architecture:
    - Layer 1 (Parallel): 5 Analyst Agents run simultaneously
      * Resume Analyst
      * Cover Letter Expert
      * JD Match Manager
      * GitHub Analyst
      * Location Coordinator
    
    - Layer 2 (Sequential): Fairness Auditor reviews all Layer 1 outputs
    
    - Layer 3 (Final): Referee Agent makes final decision
    
    Flow:
    START -> [Resume, CoverLetter, JDMatch, GitHub, Location] (Parallel)
         -> Fairness (Sequential, waits for all 5)
         -> Referee (Sequential)
         -> END
    """
    
    # Create the state graph
    workflow = StateGraph(AgentGraphState)
    
    # Add all agent nodes
    workflow.add_node("resume_analyst", resume_analyst)
    workflow.add_node("cover_letter_analyst", cover_letter_analyst)
    workflow.add_node("jd_match_analyst", jd_match_analyst)
    workflow.add_node("github_analyst", github_analyst)
    workflow.add_node("location_coordinator", location_coordinator)
    workflow.add_node("fairness_auditor", fairness_auditor)
    workflow.add_node("referee_agent", referee_agent)
    
    # Layer 1: Connect START to all 5 parallel analysts (Fan-out)
    workflow.add_edge(START, "resume_analyst")
    workflow.add_edge(START, "cover_letter_analyst")
    workflow.add_edge(START, "jd_match_analyst")
    workflow.add_edge(START, "github_analyst")
    workflow.add_edge(START, "location_coordinator")
    
    # Layer 2: Wait for all 5 analysts to complete, then fairness (Fan-in)
    workflow.add_edge("resume_analyst", "fairness_auditor")
    workflow.add_edge("cover_letter_analyst", "fairness_auditor")
    workflow.add_edge("jd_match_analyst", "fairness_auditor")
    workflow.add_edge("github_analyst", "fairness_auditor")
    workflow.add_edge("location_coordinator", "fairness_auditor")
    
    # Layer 3: Fairness to Referee
    workflow.add_edge("fairness_auditor", "referee_agent")
    
    # Final: Referee to END
    workflow.add_edge("referee_agent", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Instantiate the compiled graph
app = build_hiring_graph()
