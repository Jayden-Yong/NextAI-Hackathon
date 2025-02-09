from openai import OpenAI
from config import api_key
from database import load_employees
import json

client = OpenAI(api_key = api_key ,base_url = "https://api.deepseek.com")


def generate(prompt):
    employees,desks,booking,department = load_employees()
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

    try:
        # Call the API
        response = client.chat.completions.create(
            model="deepseek-reasoner",  
            messages=messages,
            response_format={"type": "json_object"} ,
            max_tokens=50
        )

        response_json = json.loads(response.choices[0].message.content)
        return response_json

    except Exception as e:
        # Handle errors
        print(f"An error occurred: {e}")
        return {"error": str(e)}

    # returns 
    # {
    #     "recommendations" : "response"
    # }