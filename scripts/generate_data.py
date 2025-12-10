"""
Synthetic Data Generator for Multi-Agent Hiring System

Generates realistic candidate profiles for testing the hiring system.
Outputs to test_candidates.json in the project root.
"""

import json
import os
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate


def generate_synthetic_candidates() -> list:
    """
    Generate 5 distinct, realistic candidate profiles using LLM.
    
    If LLM fails or API key is missing, uses fallback hardcoded data.
    
    Returns:
        List of candidate profile dictionaries
    """
    
    # Try to use LLM if API key is available
    api_key = os.getenv("GROQ_API_KEY")
    
    if api_key:
        try:
            # Initialize ChatGroq
            llm = ChatGroq(
                model="llama3-70b-8192",
                temperature=0.7,  # Higher temp for creative variety
                groq_api_key=api_key
            )
            
            prompt_template = PromptTemplate(
                input_variables=["role_title"],
                template="""You are a hiring data generator. Create 5 distinct, realistic candidate profiles for the role: {role_title}

Generate the following 5 profiles:
1. "The Rockstar" - Perfect technical match with excellent communication and recent experience
2. "The Junior" - Good fundamentals, willing to learn, but lacks experience
3. "The Mismatch" - Skilled in wrong tech stack (e.g., Java dev for Python role)
4. "The Red Flag" - Right skills but employment gaps, negative attitude in cover letter
5. "The Remote" - Excellent candidate but in a different country, requires relocation

For each candidate, return a JSON object with this structure:
{{
    "name": "Full Name",
    "profile_type": "The Rockstar|The Junior|The Mismatch|The Red Flag|The Remote",
    "resume": "Detailed 200-300 word resume text with experience, skills, education",
    "cover_letter": "100-150 word cover letter that reflects their profile type",
    "github_url": "https://github.com/username",
    "location": {{
        "city": "City Name",
        "country": "Country"
    }},
    "willing_to_relocate": true/false,
    "years_of_experience": 3-15,
    "primary_skills": ["skill1", "skill2", "skill3"],
    "notes": "Brief notes about this profile"
}}

Return ONLY a valid JSON array with 5 objects, no other text."""
            )
            
            chain = prompt_template | llm
            
            response = chain.invoke({"role_title": "Senior Python Engineer"})
            
            # Parse JSON from response
            candidates = json.loads(response.content)
            return candidates
        
        except Exception as e:
            print(f"⚠️  LLM generation failed: {e}. Using fallback data...")
            return get_fallback_candidates()
    else:
        print("ℹ️  GROQ_API_KEY not set. Using fallback synthetic data...")
        return get_fallback_candidates()


def get_fallback_candidates() -> list:
    """
    Fallback candidates if LLM generation fails.
    """
    return [
        {
            "name": "Alice Chen",
            "profile_type": "The Rockstar",
            "resume": """ALICE CHEN | Senior Python Engineer | alice.chen@email.com

EXPERIENCE:
Senior Software Engineer at TechCorp (2021-Present)
- Led architecture redesign of microservices, reducing latency by 40%
- Mentored team of 4 junior engineers
- Implemented CI/CD pipeline using Docker and Kubernetes

Senior Engineer at DataFlow Inc (2018-2021)
- Developed high-performance data processing systems in Python
- Managed project delivering $2M in value

SKILLS:
Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS, Redis, RabbitMQ

EDUCATION:
M.S. Computer Science, Stanford University
B.S. Computer Science, UC Berkeley""",
            "cover_letter": """Dear Hiring Team,

I am excited about the Senior Python Engineer position. With 8+ years of Python development experience and proven track record of leading successful projects, I'm confident I can make immediate impact. I'm particularly drawn to your company's focus on scalable systems, which aligns perfectly with my experience building enterprise-grade solutions. I'm ready to contribute from day one.

Best regards,
Alice Chen""",
            "github_url": "https://github.com/alicechen",
            "location": {"city": "San Francisco", "country": "USA"},
            "willing_to_relocate": True,
            "years_of_experience": 8,
            "primary_skills": ["Python", "FastAPI", "Kubernetes", "AWS", "PostgreSQL"],
            "notes": "Perfect match - strong experience, proven leadership, excellent communication"
        },
        {
            "name": "Bob Kumar",
            "profile_type": "The Junior",
            "resume": """BOB KUMAR | Python Developer | bob.kumar@email.com

EXPERIENCE:
Python Developer at StartupXYZ (2023-Present)
- Developed REST APIs using Flask
- Contributed to database optimization

Intern, DataTech Solutions (2022-2023)
- Learned Python and web development fundamentals

SKILLS:
Python, Flask, MySQL, Git, Linux

EDUCATION:
B.S. Information Technology, State University (2023)""",
            "cover_letter": """Hello,

I am interested in the Senior Python Engineer position. I have 1.5 years of experience with Python and am eager to learn and grow with your team. I'm a quick learner and committed to developing the skills needed for this role.

Regards,
Bob Kumar""",
            "github_url": "https://github.com/bobkumar",
            "location": {"city": "Austin", "country": "USA"},
            "willing_to_relocate": True,
            "years_of_experience": 1.5,
            "primary_skills": ["Python", "Flask", "MySQL"],
            "notes": "Good potential but lacks seniority and depth - suitable for mentoring"
        },
        {
            "name": "Carlos Rodriguez",
            "profile_type": "The Mismatch",
            "resume": """CARLOS RODRIGUEZ | Senior Java Developer | carlos.r@email.com

EXPERIENCE:
Senior Java Engineer at JavaCorp (2018-Present)
- 9 years of enterprise Java development
- Expert in Spring Boot, Hibernate, microservices architecture

SKILLS:
Java, Spring Boot, JavaScript, SQL, Maven, Jenkins

EDUCATION:
B.S. Computer Science, University of Mexico""",
            "cover_letter": """I have 9 years of enterprise development experience and am ready for new challenges. Python seems like an interesting language to explore.

Carlos Rodriguez""",
            "github_url": "https://github.com/carlos-j",
            "location": {"city": "Mexico City", "country": "Mexico"},
            "willing_to_relocate": False,
            "years_of_experience": 9,
            "primary_skills": ["Java", "Spring Boot", "JavaScript"],
            "notes": "Experienced but wrong tech stack - would require significant ramp-up"
        },
        {
            "name": "Diana Foster",
            "profile_type": "The Red Flag",
            "resume": """DIANA FOSTER | Software Engineer | diana.foster@email.com

EXPERIENCE:
Software Engineer at TechCorp (2020-2022)
[Employment Gap: 2022-2024]
Developer at CodeShop (2015-2020)

SKILLS:
Python, Django, PostgreSQL

EDUCATION:
B.S. Computer Science, Online University""",
            "cover_letter": """I can code in Python. I expect competitive salary and work-life balance. Let me know if you're interested.

Diana Foster""",
            "github_url": "https://github.com/diana-f",
            "location": {"city": "Portland", "country": "USA"},
            "willing_to_relocate": False,
            "years_of_experience": 6,
            "primary_skills": ["Python", "Django"],
            "notes": "2-year employment gap, dismissive tone in letter - potential concerns"
        },
        {
            "name": "Elena Ivanova",
            "profile_type": "The Remote",
            "resume": """ELENA IVANOVA | Senior Python Engineer | elena.ivanova@email.com

EXPERIENCE:
Senior Backend Engineer at CloudTech (2019-Present, Remote)
- 7+ years Python development, 4 years in remote roles
- Built scalable APIs serving 1M+ requests daily
- Led distributed team across 5 time zones

SKILLS:
Python, FastAPI, PostgreSQL, Docker, Redis, AWS, Distributed Systems

EDUCATION:
M.S. Computer Science, Technical University of Moscow
B.S. Physics, Moscow State University""",
            "cover_letter": """I am an experienced Python engineer with proven success in remote environments. My experience building and managing distributed systems aligns well with your company's goals. I'm located in Moscow but open to discussions about collaboration arrangements.

Best regards,
Elena Ivanova""",
            "github_url": "https://github.com/elena-ivan",
            "location": {"city": "Moscow", "country": "Russia"},
            "willing_to_relocate": False,
            "years_of_experience": 7,
            "primary_skills": ["Python", "FastAPI", "Distributed Systems", "AWS"],
            "notes": "Strong technical skills, but location/relocation is significant factor"
        }
    ]


def save_candidates_to_file(candidates: list, output_path: str = None) -> str:
    """
    Save generated candidates to a JSON file.
    
    Args:
        candidates: List of candidate dictionaries
        output_path: Path to save the file (default: test_candidates.json in project root)
    
    Returns:
        Path where file was saved
    """
    if output_path is None:
        # Save to project root
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_candidates.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)
    
    return output_path


def main():
    """
    Main entry point for the synthetic data generator.
    """
    print("🤖 Generating synthetic candidate data...")
    
    candidates = generate_synthetic_candidates()
    
    output_path = save_candidates_to_file(candidates)
    
    print(f"✅ Generated {len(candidates)} synthetic candidates")
    print(f"📄 Saved to: {output_path}")
    print()
    print("Candidates generated:")
    for i, candidate in enumerate(candidates, 1):
        print(f"  {i}. {candidate['name']} - {candidate['profile_type']}")
    
    return candidates


if __name__ == "__main__":
    main()
