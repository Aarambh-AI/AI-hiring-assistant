from openai import AzureOpenAI
import instructor
import tiktoken
import json
import os

openai_client = AzureOpenAI(
    api_key=os.environ["OAI_KEY_LLM"],
    api_version=os.environ["OAI_VERSION"],
    azure_endpoint=os.environ["OAI_BASE_LLM"],
)

# Patch the OpenAI client
openai_client = instructor.from_openai(openai_client)

def generate_llm_response(messages, response_model=None):
  response = openai_client.chat.completions.create(
              model=os.environ["LLM_MODEL_NAME"],
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