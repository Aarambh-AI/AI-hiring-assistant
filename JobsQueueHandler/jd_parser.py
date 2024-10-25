from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List, Literal
from utils import openai_utils
import os




class ResumeFormat(BaseModel):

    description: str = Field(
        description=dedent(
            "Complete description of the Job from the job description."
        )
    )

    key_responsibilities: str = Field(
         description=dedent(
              "Key responsibilities and requirements from the provided job description."
         )
    )

    skills: list = Field(
        description=dedent(
            "List of Required skills for the provided job description, If you cannot find anything return null."
        )
    )

    job_role: str = Field(
        description=dedent(
            "The role of the job mentioned in the job description"
        )
    )




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
        messages, response_model=ResumeFormat
    ).model_dump()

    blob_details = {
         "connection_string": os.environ['AzureWebJobsStorage'],
         "container":container,
         "blob":blob 
    }

    llm_answer["blob_details"]=blob_details
    llm_answer.update(meta_data)

    # json_data = generate_embeddings(llm_answer)

    
    return llm_answer

