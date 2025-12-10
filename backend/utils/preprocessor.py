import io
import requests
from typing import Dict, Any, Optional, List
from fastapi import UploadFile
from pypdf import PdfReader


async def extract_pdf_text(resume_file: UploadFile) -> str:
    """
    Extract text from a PDF file uploaded via FastAPI.
    
    Args:
        resume_file: The uploaded PDF file
    
    Returns:
        Extracted text from all pages of the PDF
    """
    try:
        # Read the uploaded file into bytes
        file_bytes = await resume_file.read()
        pdf_file = io.BytesIO(file_bytes)
        
        # Parse the PDF
        reader = PdfReader(pdf_file)
        text = ""
        
        # Extract text from all pages
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")


async def fetch_github_repos(github_url: str) -> tuple[str, List[Dict[str, Any]]]:
    """
    Fetch GitHub repositories for a user from the GitHub API.
    
    Args:
        github_url: GitHub profile URL or username
    
    Returns:
        Tuple of (username, repo_list with filtered data)
    """
    try:
        # Extract username from URL
        # Handles: https://github.com/username or just username
        if "github.com/" in github_url:
            username = github_url.split("github.com/")[-1].rstrip("/")
        else:
            username = github_url.strip()
        
        # Fetch repos from GitHub API
        api_url = f"https://api.github.com/users/{username}/repos"
        
        # Add timeout and headers to avoid rate limiting
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MultiAgentHiringSystem"
        }
        
        response = requests.get(api_url, headers=headers, timeout=5)
        
        if response.status_code == 404:
            return username, []
        
        if response.status_code != 200:
            # Handle rate limiting or other errors gracefully
            return username, []
        
        repos_data = response.json()
        
        # Extract relevant fields from each repo
        repos = []
        for repo in repos_data:
            repos.append({
                "name": repo.get("name", ""),
                "description": repo.get("description", ""),
                "language": repo.get("language", "Unknown"),
                "stars": repo.get("stargazers_count", 0),
                "last_updated": repo.get("updated_at", ""),
                "url": repo.get("html_url", "")
            })
        
        # Sort by stars descending
        repos = sorted(repos, key=lambda x: x["stars"], reverse=True)
        
        return username, repos
    
    except requests.Timeout:
        # GitHub API timeout
        return github_url, []
    except requests.RequestException as e:
        # Network error or other request issues
        return github_url, []
    except Exception as e:
        # Any other error
        return github_url, []


def parse_job_description(jd_text: str) -> Dict[str, Any]:
    """
    Parse raw job description text into structured fields.
    
    In a production system, you might use LLM to parse this.
    For now, we extract basic info and leave detailed parsing to agents.
    
    Args:
        jd_text: Raw job description text
    
    Returns:
        Parsed job description dict
    """
    jd_lower = jd_text.lower()
    
    # Basic role extraction
    role_title = "Unknown Role"
    if "senior" in jd_lower:
        role_title = "Senior Engineer"
    elif "junior" in jd_lower:
        role_title = "Junior Engineer"
    elif "engineer" in jd_lower:
        role_title = "Engineer"
    
    # Basic location detection
    location_type = "Unknown"
    if "remote" in jd_lower:
        location_type = "Remote"
    elif "on-site" in jd_lower or "onsite" in jd_lower:
        location_type = "On-site"
    elif "hybrid" in jd_lower:
        location_type = "Hybrid"
    
    return {
        "raw_text": jd_text,
        "role_title": role_title,
        "location_type": location_type,
        "description": jd_text,
        "skills_required": [],  # Agents will extract these
        "skills_nice_to_have": [],
        "company_name": "Unknown Company",
        "seniority_level": "Mid-Level"
    }


async def enrich_candidate_data(
    resume_file: UploadFile,
    github_url: str,
    cover_letter_text: str,
    jd_text: str
) -> Dict[str, Any]:
    """
    Convert uploaded files and text into the Master JSON format.
    
    This is the central preprocessing function that transforms raw inputs
    into the structured format expected by the agent graph.
    
    Args:
        resume_file: Uploaded PDF resume file
        github_url: GitHub profile URL or username
        cover_letter_text: Cover letter text
        jd_text: Job description text
    
    Returns:
        Dictionary matching AgentGraphState structure
    """
    
    # Extract resume text from PDF
    resume_text = await extract_pdf_text(resume_file)
    
    # Fetch GitHub data
    github_username, github_repos = await fetch_github_repos(github_url)
    
    # Parse job description
    parsed_jd = parse_job_description(jd_text)
    
    # Construct the Master JSON
    structured_data = {
        "personal_info": {
            "name": "Candidate",  # Will be extracted from resume if possible
            "email": "candidate@example.com",
            "location": {
                "city": "Unknown",
                "country": "Unknown"
            },
            "github_url": github_url,
            "willing_to_relocate": False,
            "gender": "Not disclosed",
            "age": "Not disclosed"
        },
        "resume": {
            "text": resume_text,
            "file_name": resume_file.filename
        },
        "cover_letter": {
            "text": cover_letter_text
        },
        "github": {
            "username": github_username,
            "url": github_url,
            "repo_list": github_repos
        },
        "job_description": parsed_jd
    }
    
    return structured_data
