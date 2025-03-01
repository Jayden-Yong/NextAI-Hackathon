from flask import session
import pandas as pd
def get_user_details():
    return session.get('user_details',None)

def get_user_data_df(user_data):  
    if isinstance(user_data, list) and all(isinstance(i, dict) for i in user_data):
        # Convert list of dictionaries to a DataFrame
        user_data = pd.DataFrame(user_data)
        return user_data
    else:
        print("there is an error in getting the user details")
