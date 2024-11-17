from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List, Literal
from utils import openai_utils
import os
from datetime import datetime




class JDFormat(BaseModel):

    description: str = Field(
        default="",
        description=dedent(
            "Complete description of the Job from the job description."
        )
    )
    experience: int = Field(default=0, description=dedent("Minimum experience required for the job from the provided job description."))
    location: str = Field(default="", description=dedent("Location of the job from the provided job description."))
    key_responsibilities: str = Field(
        default="",
         description=dedent(
              "Key responsibilities and requirements from the provided job description."
         )
    )
    qualifications: str = Field(
        default="",
        description=dedent(
              "Qualifications required from the provided job description."
         )
    )

    skills: list = Field(
        default=list,
        description=dedent(
            "List of Required skills for the provided job description, If you cannot find anything return null."
        )
    )

    job_role: str = Field(
        default="",
        description=dedent(
            "The role of the job mentioned in the job description"
        )
    )

def generate_embeddings(jd_data, jd_text = None):
    embeddings = openai_utils.generate_text_embeddings(jd_text)
    jd_data["embeddings"] = embeddings
    return jd_data


def construct_response_data(jd_text, container, blob, meta_data = None):
    # STEP 1: Send the question and context to LLM
    system_content = dedent("""
        You are an expert in parsing Job Description. extract all the relevant fields only from the provided information.
        
        Instructions:
        1.Only extract information from the provided job description.
        2.Return Null if the data is not explicitely mentioned in the Job description.
        """)

    user_content = dedent(f"""
        Job Descripton:
        {jd_text}

                          """)

    messages = [
        {
            "role": "system",
            "content": system_content,
        },
        {"role": "user", "content": user_content},
    ]

    llm_answer = openai_utils.generate_llm_response(
        messages, response_model=JDFormat
    ).model_dump()

    blob_details = {
         "container":container,
         "blob":blob 
    }
    current_datetime = datetime.now()
    llm_answer["created_timestamp"] = current_datetime
    llm_answer["modified_timestamp"] = current_datetime
    llm_answer["jd_text"] = jd_text
    llm_answer["blob_details"]=blob_details
    llm_answer.update(meta_data)

    jd_data = generate_embeddings(llm_answer, jd_text)

    
    return jd_data

