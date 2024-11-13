from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List
import json
from utils import openai_utils
import os
from retriever import profile_fetcher as profile_fetcher
from datetime import datetime

class EducationReference(BaseModel):
    school: str = Field(default="")
    startDate: str = Field(default="")
    endDate: str = Field(default="")
    percentage: str = Field(default="")
    degree: str = Field(default="")
    specialization: str = Field(default="")
    location: str = Field(default="")
    cgpa: str = Field(default="")

class WorkReference(BaseModel):
    companyName: str = Field(default="")
    location: str = Field(default="")
    industry: str = Field(default="")
    title: str = Field(default="")
    startDate: str = Field(default="")
    endDate: str = Field(default="")
    job_description: str = Field(default="")

class ResumeFormat(BaseModel):
    name: str = Field(default="", description=dedent("Name of the candidate from the provided resume."))
    summary: str = Field(default="", description=dedent("A brief summary of the candidate's work experience."))
    gender: str = Field(default="", description=dedent("Gender of the candidate from the provided resume."))
    total_experience: int = Field(default=0, description=dedent("Total experience of the candidate in years."))
    currentemployer: str = Field(default="", description=dedent("The current employer of the candidate from the provided resume."))
    role: str = Field(default="", description=dedent("The current role of the candidate from the provided resume."))
    emails: list = Field(default_factory=list, description=dedent("List of email IDs of the candidate from the provided resume."))
    linkedin_url: str = Field(default="", description=dedent("The LinkedIn URL of the candidate from the provided resume."))
    currentLocation: str = Field(default="", description=dedent("Current working location of the candidate from the provided resume."))
    addresses: list = Field(default_factory=list, description=dedent("List of addresses the candidate has worked in from the provided resume."))
    phones: list = Field(default_factory=list, description=dedent("List of phone numbers of the candidate from the provided resume."))
    keySkills: list = Field(default_factory=list, description=dedent("List of skills of the candidate from the provided resume."))
    education: List[EducationReference] = Field(default_factory=list, description=dedent("List of education background from the provided resume."))
    workbackground: List[WorkReference] = Field(default_factory=list, description=dedent("List of all work backgrounds / projects from the provided resume."))

def construct_response_data(resume, container, blob, meta_data=None):
    # STEP 1: Send the question and context to LLM
    system_content = dedent("""
        You are an expert in parsing resumes. Extract all the relevant fields only from the provided information.
        
        Instructions:
        1. If you do not find any field in the resume, leave the field empty (use empty string for strings, empty list for lists, and 0 for integers).
        """)

    user_content = dedent(f"""
        Resume of the candidate:
        {resume}
    """)

    messages = [
        {
            "role": "system",
            "content": system_content,
        },
        {"role": "user", "content": user_content},
    ]

    llm_answer = openai_utils.generate_llm_response(
        messages, response_model=ResumeFormat
    ).model_dump()

    blob_details = {
         "container":container,
         "blob":blob 
    }
    # Get the current date and time
    current_datetime = datetime.now()
    llm_answer["created_timestamp"] = current_datetime
    llm_answer["modified_timestamp"] = current_datetime
    llm_answer["blob_details"]=blob_details
    candidate_name = llm_answer['name']
    candidate_title = llm_answer['role']
    llm_answer.update(meta_data)

    if llm_answer["linkedin_url"] == '':
         llm_answer["linkedin_verified"] = False
         llm_answer['top_linkedin_suggestions'] = profile_fetcher.fetch_profile(candidate_name, candidate_title)
    else:
         llm_answer["linkedin_verified"] = True

    if not llm_answer['workbackground']:
        return llm_answer
    else:
        json_data = generate_embeddings(llm_answer)
        return json_data
    
    

def concatenate_work_background(work_background):
    return " ".join(
        [f"{job['companyName']} {job['location']} {job['industry']} {job['title']} {job['startDate']} {job['endDate']} {job['job_description']}"
         for job in work_background]
    )
 

def generate_embeddings(resume_data):
    text = concatenate_work_background(resume_data['workbackground'])
    embeddings = openai_utils.generate_text_embeddings(text)
    resume_data["embeddings"] = embeddings
    return resume_data
