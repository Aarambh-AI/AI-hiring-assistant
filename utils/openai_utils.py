from openai import AzureOpenAI
import instructor
import tiktoken
import json

openai_client = AzureOpenAI(
    api_key="e06832d6f27b43b1a53729ec3b95a91a",
    api_version="2023-12-01-preview",
    azure_endpoint="https://gpt-test-service.openai.azure.com/",
)

# Patch the OpenAI client
openai_client = instructor.from_openai(openai_client)

def generate_llm_response(messages, response_model=None):
  response = openai_client.chat.completions.create(
              model="gpt-35-turbo-16k",
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