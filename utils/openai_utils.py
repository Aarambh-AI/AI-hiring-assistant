from openai import AzureOpenAI
import instructor
import tiktoken
import json

openai_client = AzureOpenAI(
    api_key="12e9ae31c8d64f2fb754efdb9f7a8a52",
    api_version="2024-02-01",
    azure_endpoint="https://api-openai-service.openai.azure.com/",
)

# Patch the OpenAI client
openai_client = instructor.from_openai(openai_client)

def generate_llm_response(messages, response_model=None):
  response = openai_client.chat.completions.create(
              model="gpt-4o-mini",
              temperature=0,
              seed=123456789,
              messages=messages,
              response_model=response_model,
          )
  return response

def count_tokens(arr_data):
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(json.dumps(arr_data)))
    return num_tokens