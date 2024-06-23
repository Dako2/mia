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
import autogen
from autogen import AssistantAgent, UserProxyAgent
from jamba_autogen import JambaModelClient



api_key = "6uLGd9BlDczVhorg0PCBBCiHKbuF8YJ8" #os.getenv("AI21_API_KEY")

#In order to speed up the answer to the questions, we will call AI21 Contextual Answers in Parallel
def call_ca_parallel(args):
    article, question, category = args
    response = ai21_client.answer.create(
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
    response = oai_client.chat.completion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": f"{prompt}"},
        ],
        max_tokens=1000,
        temperature=temperature,
        top_p=1,
    )
    return response.choices[0].message.content

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
    response = ai21_client.library.files.create(
        file_path=path,
        labels=labels,
        path=path_meta
    )
    print(response)

def query_library(query, labels=None, path=None):
    response = ai21_client.library.answer.create(
        question=query,
        path=path,
        #labels=labels
    )
    if response.answer_in_context:
      print(response.answer)
      print(response.sources)
    else:
      print("No answer found")

ai21_client = AI21Client(api_key=api_key)
oai_client = OpenAI()

PROMPTS_TEMPLATE = """you are a helpful and delightful AI assistant helping the first time parent having a baby at each time step. The expected due date is

{query_time} 
You are always respond a colorful response. 

""" #with the state of situation based on the timeline. 

question = "hi"
prompt = PROMPTS_TEMPLATE.format(query_time="August 30, 2024") + question 

#upload_rag("2023-Pregnancy-Purplebook_19Jan2024.pdf", labels=["hr"], path_meta="2023-Pregnancy-Purplebook_19Jan2024.pdf")
query_library(prompt, labels=["hr"])

config_list_custom = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={"model_client_cls": ["JambaModelClient"]},
)

assistant = AssistantAgent("assistant", llm_config={"config_list": config_list_custom})
user_proxy = UserProxyAgent(
    "user_proxy",
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    },
)
assistant.register_model_client(model_client_cls=JambaModelClient)
user_proxy.initiate_chat(assistant, message="Write python code to print Hello World!")

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4", "gpt-4-turbo", "gpt-4o"], # , "jamba"
    },
)

llm_config = {"config_list": config_list, "cache_seed": 42}
mia = autogen.UserProxyAgent(
    name="mia",
    system_message="A human admin.",
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "groupchat",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    human_input_mode="TERMINATE",
)

alice = autogen.AssistantAgent(
    name="alice",
    system_message="Provide emotional support.",
    llm_config=llm_config,
)

ob = autogen.AssistantAgent(
    name="ob",
    system_message="Provide medical information.",
    llm_config=llm_config,
)

alex = autogen.AssistantAgent(
    name="alex",
    system_message="Provide scheduling information and help schedule appointments.",
    llm_config=llm_config,
)

groupchat = autogen.GroupChat(agents=[mia, alice, ob, alex], messages=[], max_round=12)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

mia.initiate_chat(
    manager, message="Find when I should schedule a B-mode ultrasonography scan."
)

mia.initiate_chat(
    manager, message="I feel too tired and depressed."
)