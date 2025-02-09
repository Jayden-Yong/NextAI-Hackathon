from openai import OpenAI
from config import api_key
from flask import jsonify,request
from database import load_data
import json

client = OpenAI(api_key = api_key ,base_url = "https://api.deepseek.com")


def generate(prompt):
    schema = load_data()
    # expect input like this
    # {
    #     "input_text": "desired inputs to ask "
    # }
    system_prompt = """
    The user will provide tuple with dataframe of employees,desks,booking,department. Please parse the "question" and "recommendation" and output them in JSON format. 

    EXAMPLE INPUT: 
    (a tuple with dataframe)analyse this data and give recommendations

    EXAMPLE JSON OUTPUT:
    {
        
        "recommendation": "recommendation......."
    }
    """

    user_prompt = prompt+" "+schema

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    return (json.loads(response.choices[0].message.content))
    # returns 
    # {
    #     "recommendations" : "response"
    # }