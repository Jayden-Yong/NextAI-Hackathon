from flask import Flask
from vanna.flask import VannaFlaskApp
from documentation_vanna import ddl,documentation
from config import DB_CONFIG,vanna_api_key,vanna_model_name
from vanna.remote import VannaDefault

app = Flask(__name__)
# this format
# DB_CONFIG = {
#     'host':'',
#     'user':'',
#     'password':'',
#     'database': ''
# }

host = DB_CONFIG.get('host')
dbname = DB_CONFIG.get('database')
user = DB_CONFIG.get('user')
password = DB_CONFIG.get('password')

# ddl statements and documentations prompt to train the model for better understanding of the relationship and structure of the data 
ddl_statements = ddl
documentation = documentation

api_key = vanna_api_key 
vanna_model_name = vanna_model_name
vn = VannaDefault(model=vanna_model_name, api_key=api_key)

def vanna_connect_db():
    vn.connect_to_mysql(host=host, dbname=dbname, user=user, password=password, port=3306)

def vanna_train():
    df_information_schema = vn.run_sql(f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{dbname}'") 
    plan = vn.get_training_plan_generic(df_information_schema)
    vn.train(plan=plan)
    vn.train(ddl=ddl_statements)
    vn.train(documentation=documentation)

  
vanna_connect_db()
# please uncomment the code below for the first time , and whenever u wanted to retrain the model / can do it in the UI as well
vanna_train()

 
app = VannaFlaskApp(vn)
if __name__ == '__main__':
    app.run()
