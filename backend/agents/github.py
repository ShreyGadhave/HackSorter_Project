import json
from typing import Dict, Any
from datetime import datetime
from langchain.prompts import PromptTemplate
from backend.state import AgentGraphState
from backend.utils.llm import initialize_llm


def github_analyst(state: AgentGraphState) -> Dict[str, Any]:
    """
    GitHub Analyst Agent (Senior Engineer)
    
    Role: Analyzes GitHub profile and repositories for quality and activity.
    Input: GitHub data (repo_list with stars, last_updated, languages, etc.)
    Output: github_score dict with score, analysis, and thought_process
    """
    llm = initialize_llm()
    
    job_application = state["job_application"]
    github_data = job_application.get("github", {})
    repos = github_data.get("repo_list", [])
    github_username = github_data.get("username", "Unknown")
    
    # Format repos for analysis
    if repos:
        repos_str = json.dumps(repos, indent=2)
    else:
        repos_str = "No repositories found"
    
    prompt_template = PromptTemplate(
        input_variables=["github_username", "repos_data"],
        template="""You are a Senior Engineer evaluating a GitHub profile.

GITHUB USERNAME: {github_username}

REPOSITORIES:
{repos_data}

Evaluate based on:
1. Repository stars and popularity (community validation)
2. Recency of activity (last_updated date)
3. Language diversity and relevance
4. Project scale and complexity
5. Contribution consistency
6. Code quality indicators (forks, issues, pull requests)

Today's date for recency assessment: {today}

Provide a JSON response:
{{
    "score": <0-100 numeric score>,
    "total_repos": <count of repositories>,
    "high_quality_repos": [<list of repos with notable stars/activity>],
    "recent_activity": "<Inactive/Some activity/Very active - based on last_updated dates>",
    "language_diversity": [<languages found across repos>],
    "portfolio_strength": "<Weak/Moderate/Strong>",
    "red_flags": [<any concerns like all repos are old, low quality, etc.>],
    "thought_process": "<First-person explanation, e.g., 'I analyzed {github_username} repos and noticed high-quality projects in Python and TypeScript with recent commits...'"
}}

Return ONLY valid JSON, no other text."""
    )
    
    chain = prompt_template | llm
    
    try:
        response = chain.invoke({
            "github_username": github_username,
            "repos_data": repos_str,
            "today": datetime.now().strftime("%Y-%m-%d")
        })
        
        result = json.loads(response.content)
        
        return {
            "github_score": result
        }
    except json.JSONDecodeError:
        return {
            "github_score": {
                "score": 0,
                "total_repos": len(repos),
                "high_quality_repos": [],
                "recent_activity": "Unknown",
                "language_diversity": [],
                "portfolio_strength": "Unknown",
                "red_flags": ["Failed to parse GitHub data"],
                "thought_process": "I encountered an error while analyzing the GitHub profile. Please check the data format."
            }
        }
    except Exception as e:
        return {
            "github_score": {
                "score": 0,
                "total_repos": len(repos),
                "high_quality_repos": [],
                "recent_activity": "Unknown",
                "language_diversity": [],
                "portfolio_strength": "Unknown",
                "red_flags": [f"Error: {str(e)}"],
                "thought_process": f"I encountered an error: {str(e)}"
            }
        }
