import json
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, AsyncGenerator
from backend.graph import app as hiring_graph
from backend.state import AgentGraphState
from backend.utils.preprocessor import enrich_candidate_data

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Hiring System",
    description="Real-time streaming hiring analysis with 7 AI agents",
    version="1.0.0"
)


class JobApplication(BaseModel):
    """
    Request model for job applications.
    Contains all candidate information and job requirements.
    """
    job_application: Dict[str, Any]
    hiring_criteria: Dict[str, Any] = {
        "weights": {
            "resume": 0.2,
            "cover_letter": 0.15,
            "jd_match": 0.3,
            "github": 0.2,
            "location": 0.15
        },
        "strictness": "medium"
    }


async def stream_agent_analysis(job_application: Dict[str, Any], hiring_criteria: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
    """
    Stream agent analysis results in real-time using SSE format.
    
    This generator:
    1. Invokes the LangGraph hiring system with dynamic criteria
    2. Streams events as agents complete their work
    3. Extracts "thought_process" from each agent's JSON output
    4. Yields SSE-formatted data for frontend consumption
    5. Sends final verdict when referee completes
    
    Args:
        job_application: The job application data dict
        hiring_criteria: Dynamic weights and strictness settings
    
    Yields:
        SSE formatted strings with agent thoughts and final verdict
    """
    
    # Set default criteria if not provided
    if hiring_criteria is None:
        hiring_criteria = {
            "weights": {
                "resume": 0.2,
                "cover_letter": 0.15,
                "jd_match": 0.3,
                "github": 0.2,
                "location": 0.15
            },
            "strictness": "medium"
        }
    
    # Prepare the initial state with hiring criteria
    initial_state = {
        "job_application": job_application,
        "hiring_criteria": hiring_criteria,
        "resume_score": {},
        "cover_letter_score": {},
        "jd_match_score": {},
        "github_score": {},
        "location_score": {},
        "fairness_audit": {},
        "final_verdict": {}
    }
    
    # Agent display names for frontend
    agent_display_names = {
        "resume_analyst": "Resume Analyst",
        "cover_letter_analyst": "Cover Letter Expert",
        "jd_match_analyst": "JD Match Manager",
        "github_analyst": "GitHub Analyst",
        "location_coordinator": "Location Coordinator",
        "fairness_auditor": "Fairness Auditor",
        "referee_agent": "Referee Agent"
    }
    
    # Track which agents have completed
    completed_agents = set()
    final_verdict = None
    
    try:
        # Stream events from the LangGraph application
        # Using async iteration with stream_events
        async for event in hiring_graph.astream_events(
            initial_state,
            version="v1"
        ):
            event_type = event.get("event")
            
            # We're interested in 'on_chain_end' events that mark agent completion
            if event_type == "on_chain_end":
                data = event.get("data", {})
                metadata = event.get("metadata", {})
                
                # Get the node/agent name
                langgraph_node = metadata.get("langgraph_node", "")
                
                if langgraph_node and langgraph_node in agent_display_names:
                    agent_name = agent_display_names[langgraph_node]
                    completed_agents.add(langgraph_node)
                    
                    # Extract the output from this agent
                    output = data.get("output", {})
                    
                    # Determine which score key to look for based on agent
                    score_key = None
                    if langgraph_node == "resume_analyst":
                        score_key = "resume_score"
                    elif langgraph_node == "cover_letter_analyst":
                        score_key = "cover_letter_score"
                    elif langgraph_node == "jd_match_analyst":
                        score_key = "jd_match_score"
                    elif langgraph_node == "github_analyst":
                        score_key = "github_score"
                    elif langgraph_node == "location_coordinator":
                        score_key = "location_score"
                    elif langgraph_node == "fairness_auditor":
                        score_key = "fairness_audit"
                    elif langgraph_node == "referee_agent":
                        score_key = "final_verdict"
                    
                    # Extract agent's analysis from output
                    if score_key and score_key in output:
                        agent_output = output[score_key]
                        thought_process = agent_output.get("thought_process", "")
                        
                        # For referee, include final verdict
                        if langgraph_node == "referee_agent":
                            final_verdict = agent_output
                            
                            # Yield the complete verdict
                            verdict_message = {
                                "agent": agent_name,
                                "message": thought_process,
                                "status": "complete",
                                "type": "verdict",
                                "verdict": final_verdict.get("verdict", "UNKNOWN"),
                                "final_score": final_verdict.get("final_score", 0),
                                "full_verdict": agent_output
                            }
                            
                            yield f"data: {json.dumps(verdict_message)}\n\n"
                        else:
                            # Yield regular agent completion
                            agent_message = {
                                "agent": agent_name,
                                "message": thought_process,
                                "status": "done",
                                "type": "analysis",
                                "score": agent_output.get("score", 0)
                            }
                            
                            yield f"data: {json.dumps(agent_message)}\n\n"
        
        # Yield final completion signal
        completion_message = {
            "agent": "System",
            "message": "All agents have completed analysis.",
            "status": "complete",
            "type": "system"
        }
        yield f"data: {json.dumps(completion_message)}\n\n"
        
    except Exception as e:
        # Yield error message
        error_message = {
            "agent": "System",
            "message": f"Error during analysis: {str(e)}",
            "status": "error",
            "type": "error"
        }
        yield f"data: {json.dumps(error_message)}\n\n"


@app.post("/analyze")
async def analyze_candidate(
    resume_file: UploadFile = File(...),
    github_url: str = Form(...),
    cover_letter: str = Form(...),
    jd_text: str = Form(...),
    hiring_criteria: str = Form(default=None)
):
    """
    Endpoint to analyze a job candidate with streaming agent responses.
    
    Accepts multipart form data (file + text) with optional hiring criteria.
    Preprocesses the raw inputs into structured JSON, then streams analysis.
    
    Args:
        resume_file: PDF resume file uploaded from frontend
        github_url: GitHub profile URL or username
        cover_letter: Cover letter text
        jd_text: Job description text
        hiring_criteria: Optional JSON string with custom weights and strictness
    
    Returns:
        StreamingResponse with text/event-stream media type (SSE)
    """
    
    try:
        # Validate file
        if not resume_file:
            raise HTTPException(status_code=400, detail="Resume file is required")
        
        if not resume_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Resume must be a PDF file")
        
        # Parse hiring criteria if provided
        criteria = {
            "weights": {
                "resume": 0.2,
                "cover_letter": 0.15,
                "jd_match": 0.3,
                "github": 0.2,
                "location": 0.15
            },
            "strictness": "medium"
        }
        
        if hiring_criteria:
            try:
                criteria = json.loads(hiring_criteria)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid hiring_criteria JSON")
        
        # Preprocess the inputs into structured JSON
        job_application = await enrich_candidate_data(
            resume_file=resume_file,
            github_url=github_url,
            cover_letter_text=cover_letter,
            jd_text=jd_text
        )
        
        # Create streaming response with criteria
        return StreamingResponse(
            stream_agent_analysis(job_application, criteria),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/analyze-json")
async def analyze_application(application: JobApplication):
    """
    Legacy endpoint to analyze a job application using JSON input.
    
    For testing purposes - accepts pre-formatted JSON directly with optional criteria.
    Use /analyze for normal file-based submissions.
    
    Args:
        application: JobApplication object containing candidate, job data, and optional criteria
    
    Returns:
        StreamingResponse with text/event-stream media type (SSE)
    """
    try:
        # Validate that job_application has required fields
        if not application.job_application:
            raise HTTPException(
                status_code=400,
                detail="job_application field is required"
            )
        
        # Extract hiring criteria (uses defaults if not provided)
        criteria = application.hiring_criteria if hasattr(application, 'hiring_criteria') else {
            "weights": {
                "resume": 0.2,
                "cover_letter": 0.15,
                "jd_match": 0.3,
                "github": 0.2,
                "location": 0.15
            },
            "strictness": "medium"
        }
        
        # Create streaming response with criteria
        return StreamingResponse(
            stream_agent_analysis(application.job_application, criteria),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        {"status": "healthy"}
    """
    return {"status": "healthy", "service": "Multi-Agent Hiring System"}


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Multi-Agent Hiring System",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /analyze - Stream job application analysis",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation (Swagger UI)",
            "redoc": "GET /redoc - API documentation (ReDoc)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI server
    # Change host to "0.0.0.0" to expose externally
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
