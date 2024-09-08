from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List, Literal
import json
from utils import openai_utils
import os
from retriever import profile_fetcher as profile_fetcher


class EducationReference(BaseModel):
        school: str
        startDate:str
        endDate: str
        percentage: str
        degree: str
        specialization: str
        location: str
        cgpa: str

class WorkReference(BaseModel):
    companyName: str
    location: str
    industry: str
    title: str
    startDate: str
    endDate: str
    job_description: str



class ResumeFormat(BaseModel):

    name: str = Field(
        description=dedent(
            "name of the candidate from the provided resume."
        )
    )

    summary: str = Field(
         description=dedent(
              "a brief summary of the candidates work experience."
         )
    )

    gender: str = Field(
        description=dedent(
            "gender of the candidate from the provided resume."
        )
    )

    total_experience: str = Field(
        description=dedent(
            "total experience of the candidate from the provided resume."
        )
    )

    currentemployer: str = Field(
        description=dedent(
            "the current employer of the candidate from the provided resume."
        )
    )

    role: str = Field(
        description=dedent(
            "the current role of the candidate from the provided resume."
        )
    )
    emails: list = Field(
        description=dedent(
            "list mail ids of the candidate from the provided resume."
        )
    )
    linkedin_url: str = Field(
         description=dedent("""\
                            The linkedin url of the candidate from the provided resume.
                            The url has linkedin.com in it.
                    """)
        )

    currentLocation: str = Field(
        description=dedent(
            "Current working location of the candidate from the provided resume."
        )
    )

    addresses: list = Field(
        description=dedent("""\
            The list of addresses of the candidate worked in from the provided resume.
            """)
    )

    phones: list = Field(
        description=dedent("""\
            The list of phone numbers of the candidate from the provided resume.
            """)
    )

    keySkills: list = Field(
        description=dedent("""\
            The list of skills of the candidate from the provided resume.
            """)
    )

    education: List[EducationReference] = Field(
        description=dedent("""\
            The list of education background from the provided resume.
            """)
    )
    workbackground: List[WorkReference] = Field(
        description=dedent("""\
        The list of all work backgrounds / projects from the provided resume.
        """)
        )



def construct_response_data(resume, container, blob):
    # STEP 1: Send the question and context to LLM
    system_content = dedent("""
        You are an expert in parsing resume. extract all the relevant fields only from the provided information.
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
         "connection_string": os.environ['AzureWebJobsStorage'],
         "container":container,
         "blob":blob 
    }

    llm_answer["blob_details"]=blob_details
    candidate_name = llm_answer['name']
    candidate_title = llm_answer['role']

    if llm_answer["linkedin_url"] == '':
         llm_answer["linkedin_verified"] = False
         llm_answer['top_linkedin_suggestions'] = profile_fetcher.fetch_profile(candidate_name, candidate_title)
    else:
         llm_answer["linkedin_verified"] = True


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
