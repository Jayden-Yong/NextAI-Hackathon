from llm_connection import generate

# function for suggestion on best day for f2f work
prompt_f2f = """
analyse the mysql schema first, then suggest the recommended day for working f2f for current user"""

recommendation_f2f = generate(prompt_f2f)

# function for suggestion on best day for team meeting
prompt_meeting = """
analyse the mysql schema first,then suggest the recommended day for team meeting for the current user"""
recommendation_meeting = generate(prompt_meeting)

