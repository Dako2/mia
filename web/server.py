from flask import Flask, request, jsonify, render_template
import os
os.environ["AI21_LOG_LEVEL"] = "DEBUG"
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json
import re
from docx import Document
from ai21 import AI21Client, AI21APIError, errors as ai21_errors
from ai21.models import ChatMessage
from openai import OpenAI

app = Flask(__name__)

api_key = "6uLGd9BlDczVhorg0PCBBCiHKbuF8YJ8"  # Replace with your actual API key
ai21_client = AI21Client(api_key=api_key)
oai_client = OpenAI()

PROMPTS_TEMPLATE = """you are a helpful and delightful AI assistant helping the first time parent having a baby at each time step. 
The expected due date is {birth_time}. Today is {query_time}, Week of {week}.
You are always respond a colorful response. 
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    week = request.json.get('week')
    date = request.json.get('current_date')

    prompt = PROMPTS_TEMPLATE.format(birth_time="August 30, 2024", query_time=date, week=week) + user_message
    bot_message = call_jamba(prompt)

    return jsonify({"message": bot_message})

def call_openai(prompt,temperature=.7):
    # using openAI client
    completion = oai_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "you are a helpful and delightful AI assistant helping the first time parent having a baby at each time step."},
        {"role": "user", "content": prompt}
    ]
    )
    return completion.choices[0].message.content


def call_jamba(prompt, temperature=.7):
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
                "content": prompt
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
    
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    reply = response_json["choices"][0]["message"]["content"]
    return reply

if __name__ == '__main__':
    app.run(debug=True)
