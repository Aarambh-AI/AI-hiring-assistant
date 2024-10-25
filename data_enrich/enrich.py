from utils.mongo_utils import CosmosMongoUtil
from textwrap import dedent
from pydantic import BaseModel, Field
from typing import List, Literal
import utils.openai_utils as openai_utils
import requests
import os
from bson.objectid import ObjectId

mongo_client = CosmosMongoUtil(collection="candidate_data")

def scrape_data(linkedin_url):
    url = os.environ["OSINT_URL"]
    
    params = {
        "apikey": os.environ["OSINT_KEY"],
    "linkedInUrl": linkedin_url,
}
    response = requests.request("GET", url, params=params)

    print(response.text)
    return response.text

def process(id):
    objInstance = ObjectId(id)
    doc = mongo_client.find_document({"_id":objInstance})
    doc.pop('_id', None)  # Removes _id, if present
    doc.pop('embeddings', None)  # Removes embeddings, if present
    doc.pop('blob_details', None)
    doc.pop('top_linkedin_suggestions', None)

    profile_url = doc["linkedin_url"]
    linkedin_data = scrape_data(profile_url)

    response = ai_enrich(doc, linkedin_data)
    return response

def pending_profile_validation():
    mongo_client

class ResumeFormat(BaseModel):

    enriched_data: dict = Field(
        description=dedent(
            "Enriched resume data"
        )
    )

    changed_data: str = Field(
         description=dedent(
              "a brief description of the changes made to existing data"
         )
    )


def ai_enrich(resume, linkedin_data):
    
    # STEP 1: Send the question and context to LLM
    system_content = dedent(f"""
        You are an expert in enriching user profile. 
        Enrich the existing resume json data using some of his new data fetched from linkedin.
        
        json resume data:
        {resume}

        instructions:
        1. enrich data and follow the same json structure.
        2. do not hallucinate and add new information to the existin resume which is not part of the linkedin data provided.
        3. Mention what changes are made to the resume.
        4. Ouput should be strict json.

        Sample Ouput Response Fields:
        enriched_data(Type:Dict) = "This should be the enriched json"
        changed_data(Type:String) = "Brief description about the changes made."
                            
        """)

    user_content = dedent(f"""
        linkedin data of the candidate:
        {linkedin_data}

                          """)

    messages = [
        {
            "role": "system",
            "content": system_content,
        },
        {"role": "user", "content": user_content},
    ]

    llm_answer = openai_utils.generate_llm_response(
        messages,
        response_model=ResumeFormat
    ).model_dump()

    return llm_answer