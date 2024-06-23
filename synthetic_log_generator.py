import openai
import json
import re

def extract_json_from_text(text):
    # Regular expression to match JSON object
    json_pattern = re.compile(r'\{.*\}', re.DOTALL)
    
    # Search for JSON object in the text
    match = json_pattern.search(text)
    
    if match:
        json_str = match.group(0)
        try:
            # Parse JSON string
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError:
            print("Error: The extracted string is not valid JSON.")
            return None
    else:
        print("Error: No JSON object found in the text.")
        return None
    
def call_openai(prompt, temperature=.7):
    # using openAI client
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": f"{prompt}"},
        ]
    )
    return response.choices[0].message.content

for week in range(1, 40):
    prompt = '''The user is 47 years old lady, single mom, just pregnant. The date of prenancy is 1/8/2024. the date of knowing she's pregnant is 3/7/2024. She is not confident whether she shall have a baby or not. She has a boyfriend of 27 years old. Today is Week #{week}. Creating a log of week {week} in the following json format:
                I am feeling ...
                Describe your feelings...
                Symptoms ...
                Describe any symptoms...
                Highlights of the Week
                Highlight of the week...
                My Goal
                Your goal...
                To Do List
                Your to do list...
                Notes
            '''
    results = call_openai(prompt.format(week=week))
    json_result = extract_json_from_text(results)
    with open(f"week_{week}.json", 'w') as file:
        json.dump(json_result, file)