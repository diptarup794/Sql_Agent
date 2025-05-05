import os
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

google_api_key = os.getenv("API_KEY")

class SQLQueryAgent:
    def __init__(self, db_path=None):
        self.db_path = db_path
        self.llm = None
        self.db = None
        self.agent = None
        self.toolkit = None
        self.setup_complete = False
        
    def setup(self, db_path=None):
        """Set up the SQL agent with the specified database."""
        if db_path:
            self.db_path = db_path
            
        if not self.db_path:
            return {
                "status": "error",
                "message": "No database path provided"
            }
            
        try:
            # Initialize the LLM
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                convert_system_message_to_human=True,
                google_api_key=google_api_key
            )
            
            # Connect to the database
            self.db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")
            
            # Create the toolkit and agent
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            
            self.agent = create_sql_agent(
                llm=self.llm,
                toolkit=self.toolkit,
                verbose=True,
                agent_type="openai-tools",
            )
            
            self.setup_complete = True
            
            return {
                "status": "success",
                "message": f"SQL agent set up successfully with database {self.db_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error setting up SQL agent: {str(e)}"
            }
    
    def run(self, query):
        """Run a query through the SQL agent."""
        if not self.setup_complete:
            return {
                "status": "error",
                "message": "SQL agent not set up. Call setup() first."
            }
            
        try:
            result = self.agent.invoke({"input": query})
            return {
                "status": "success",
                "result": result["output"],
                "raw_result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error running SQL query: {str(e)}"
            }