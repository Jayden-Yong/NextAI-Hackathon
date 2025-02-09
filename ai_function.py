from llm_connection import generate
from current_user_details import user_data
import numpy
if user_data is not None:
    user_data = str(user_data)

# function for suggestion on best day for f2f work
prompt_f2f = f"""
analyse the mysql schema first, then suggest the recommended day for working f2f for user with details {user_data}"""

recommendation_f2f = generate(prompt_f2f)

# function for suggestion on best day for team meeting
prompt_meeting = f"""
analyse the mysql schema first,then suggest the recommended day for team meeting for the user with details {user_data}"""
recommendation_meeting = generate(prompt_meeting)

