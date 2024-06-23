import json
import os
os.environ["AI21_LOG_LEVEL"] = "DEBUG"
from ai21 import AI21Client
from ai21 import errors as ai21_errors
from ai21 import AI21Client, AI21APIError
from ai21.models import ChatMessage
import re
from docx import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from openai import OpenAI
client = OpenAI()

api_key = "6uLGd9BlDczVhorg0PCBBCiHKbuF8YJ8" #os.getenv("AI21_API_KEY")

#In order to speed up the answer to the questions, we will call AI21 Contextual Answers in Parallel
def call_ca_parallel(args):
    article, question, category = args
    response = client.answer.create(
        context=article,
        question=question
    )
    answer = response.answer if response.answer else "None"
    return category, answer

def get_answered_questions(user_input, questions):
    answered_questions = {}
    unanswered_questions = {}

    # Use ThreadPoolExecutor to parallelize the calls
    with ThreadPoolExecutor(max_workers=7) as executor:
        # Prepare a list of arguments for the call_ca_parallel function
        future_to_question = {executor.submit(call_ca_parallel, (user_input, q[category], category)): category for q in questions for category in q}

        for future in as_completed(future_to_question):
            # When a future is completed, get the results
            category, answer = future.result()
            if answer != "None":
                answered_questions[category] = answer
            else:
                unanswered_questions[category] = "None"

    return answered_questions, unanswered_questions

def call_openai(prompt,temperature=.7):
    # using openAI client
    response = client.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        temperature=temperature,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )  
    return response.choices[0].text

def call_jamba(prompt,temperature=.7):

    url = "https://api.ai21.com/studio/v1/chat/completions"

    payload = {
        "model": "jamba-instruct",
        "messages": [
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": f'''
        {prompt}
     '''
            }
        ],
        "system": "",
        "max_tokens": 1000,
        "temperature": temperature,
        "top_p": 1,
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    #print(headers)
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    #print(response_json)
    reply = response_json["choices"][0]["message"]["content"]
    return(reply)

def upload_rag(path, labels, path_meta):
    response = client.library.files.create(
        file_path=path,
        labels=labels,
        path=path_meta
    )
    print(response)

def query_library(query, labels=None, path=None):
    response = client.library.answer.create(
        question=query,
        path=path,
        #labels=labels
    )
    if response.answer_in_context:
      print(response.answer)
      print(response.sources)
    else:
      print("No answer found")


client = AI21Client(api_key=api_key)

PROMPTS_TEMPLATE = """you are a helpful and delightful AI assistant helping the first time parent having a baby at each time step. The expected due date is

{query_time} 
You are always respond a colorful response. 

""" #with the state of situation based on the timeline. 

question = "hi"
prompt = PROMPTS_TEMPLATE.format(query_time="August 30, 2024") + question 

#upload_rag("2023-Pregnancy-Purplebook_19Jan2024.pdf", labels=["hr"], path_meta="2023-Pregnancy-Purplebook_19Jan2024.pdf")
query_library(prompt, labels=["hr"])

