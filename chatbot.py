from langchain.agents import create_csv_agent, create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from dotenv import load_dotenv
from sqlalchemy import create_engine
import duckdb

import os
import streamlit as st


load_dotenv()

# Load the OpenAI API key from the environment variable
if os.getenv("OPENAI_API_KEY") is None or os.getenv(
        "OPENAI_API_KEY") == "":
    print("OPENAI_API_KEY is not set")
else:
    print("OPENAI_API_KEY is set")

st.set_page_config(page_title="Ask your CSV")
st.header("Ask your CSV 📈")

csv_file = st.file_uploader("Upload a CSV file", type="csv")
ai_api_key = st.text_input(label="OpenAI API Key")

if ai_api_key is not None:
    os.environ['OPENAI_API_KEY'] = ai_api_key
    load_dotenv()
    print(os.getenv("OPENAI_API_KEY"))
    if csv_file is not None:
        with open(csv_file.name, "wb") as f:
            f.write(csv_file.getbuffer())

        con = duckdb.connect(database='csv.duck', read_only=False)
        con.execute(
            "create or replace table csv as select * from read_csv_auto('{}')".
            format(csv_file.name))
        con.close()

        db_uri = 'duckdb:///csv.duck'
        db = SQLDatabase.from_uri(db_uri)
        print(db)
        toolkit = SQLDatabaseToolkit(db=db,
                                        llm=OpenAI(model_name="gpt-3.5-turbo",
                                                temperature=0))
        agent = create_sql_agent(llm=OpenAI(model_name="gpt-3.5-turbo",
                                            temperature=0),
                                    toolkit=toolkit,
                                    verbose=True,
                                    debug=True)
        # agent = create_csv_agent(OpenAI(temperature=0),
        #                          csv_file,
        #                          verbose=True,
        #                          debug=True)

        user_question = st.text_input("Ask a question about your CSV: ")

        if user_question is not None and user_question != "":
            with st.spinner(text="In progress..."):
                st.write(
                    agent.run(
                        "There is only one table in the database named csv. Try to answer all questions using this table. Be careful with column names, some may contain IDs, some just texts."
                        + user_question))


