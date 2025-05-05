from typing import Dict, Any, List, Literal, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import asyncio
from agents.sql_agent import SQLQueryAgent
from agents.rag_agent import RAGAgent
from database.db_utils import get_tables_info
from typing import Annotated
import operator

# Load environment variables from .env file
load_dotenv()

# Access your API key
google_api_key = os.getenv("API_KEY")

class AgentState(BaseModel):
    """State for the multi-agent system."""
    # The user's original query
    query: str = Field(default="", description="The user's original query")
    current_agent: Literal["none", "sql", "rag", "supervisor"] = Field(default="none")
    sql_result: str = Field(default="")
    rag_result: str = Field(default="")
    final_answer: str = Field(default="")
    db_info: Dict = Field(default_factory=dict)
    error: str = Field(default="")

class SupervisorAgent:
    def __init__(self):
        self.llm = None
        self.sql_agent = None
        self.rag_agent = None
        self.graph = None
        self.setup_complete = False
        
    def setup(self, db_path=None):
        """Set up the supervisor agent and the agent graph."""
        # Ensure an event loop is available in the current thread
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        try:
            # Initialize the LLM
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                convert_system_message_to_human=True,
                google_api_key=google_api_key
            )
            
            # Initialize the SQL and RAG agents
            self.sql_agent = SQLQueryAgent(db_path)
            sql_setup = self.sql_agent.setup()
            
            self.rag_agent = RAGAgent()
            rag_setup = self.rag_agent.setup()
            
            if sql_setup["status"] == "error":
                return sql_setup
                
            if rag_setup["status"] == "error":
                return rag_setup
                
            # Get database information for context
            if db_path:
                db_info = get_tables_info(db_path)
            else:
                db_info = {"status": "error", "message": "No database path provided"}
            
            # Define the agent graph
            self.graph = StateGraph(AgentState)
            
            # Add nodes
            self.graph.add_node("supervisor", self.route_query)
            self.graph.add_node("sql_agent", self.run_sql_agent)
            self.graph.add_node("rag_agent", self.run_rag_agent)
            self.graph.add_node("generate_answer", self.generate_final_answer)
            
            # Add edges
            self.graph.add_edge(START, "supervisor")
            
            # Route to ONLY one of the agent nodes depending on what `route_query` decided.
            def _route(state: "AgentState"):
                """Return branch key so the graph knows which edge to follow (sql / rag)."""
                return state.current_agent  # either "sql" or "rag"
            
            # Use conditional edges to avoid running both agents concurrently.
            self.graph.add_conditional_edges(
                "supervisor",
                _route,
                {
                    "sql": "sql_agent",
                    "rag": "rag_agent",
                },
            )
            
            self.graph.add_edge("sql_agent", "generate_answer")
            self.graph.add_edge("rag_agent", "generate_answer")
            self.graph.add_edge("generate_answer", END)
            
            # Compile the graph
            self.graph_app = self.graph.compile()
            
            self.setup_complete = True
            
            return {
                "status": "success",
                "message": "Supervisor agent set up successfully",
                "db_info": db_info
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error setting up supervisor agent: {str(e)}"
            }
    
    def route_query(self, state: AgentState) -> AgentState:
        """Determine which agent should handle the query."""
        try:
            # Create a prompt to determine if the query is SQL-related
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a query router that determines if a query should be handled by an SQL agent or a RAG agent. "
                         "SQL agent handles structured database queries. RAG agent handles general questions about databases. "
                         "Respond with only 'sql' or 'rag'."),
                ("human", "Database tables: {db_info}\n\nQuery: {query}\n\nWhich agent should handle this query? Respond with only 'sql' or 'rag'.")
            ])
            
            chain = prompt | self.llm
            result = chain.invoke({
                "db_info": str(state.db_info),
                "query": state.query
            })
            
            agent_type = result.content.strip().lower()
            
            # Update the state
            state.current_agent = "sql" if "sql" in agent_type else "rag"
            
            return state
        except Exception as e:
            state.error = f"Error routing query: {str(e)}"
            state.current_agent = "rag"  # Default to RAG if there's an error
            return state
    
    def run_sql_agent(self, state: AgentState) -> AgentState:
        """Run the SQL agent on the query."""
        try:
            result = self.sql_agent.run(state.query)
            
            if result["status"] == "success":
                state.sql_result = result["result"]
            else:
                state.error = result["message"]
                state.sql_result = f"Error: {result['message']}"
            
            return state
        except Exception as e:
            state.error = f"Error running SQL agent: {str(e)}"
            state.sql_result = f"Error: {str(e)}"
            return state
    
    def run_rag_agent(self, state: AgentState) -> AgentState:
        """Run the RAG agent on the query."""
        try:
            # Provide database info as context
            context = f"Database tables and columns: {state.db_info}"
            
            result = self.rag_agent.run(state.query, context)
            
            if result["status"] == "success":
                state.rag_result = result["result"]
            else:
                state.error = result["message"]
                state.rag_result = f"Error: {result['message']}"
            
            return state
        except Exception as e:
            state.error = f"Error running RAG agent: {str(e)}"
            state.rag_result = f"Error: {str(e)}"
            return state
    
    def generate_final_answer(self, state: AgentState) -> AgentState:
        """Generate the final answer based on the results from both agents."""
        try:
            # Create a prompt to generate the final answer
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant that generates final answers based on the results from SQL and RAG agents. "
                         "Combine the information from both agents to provide a comprehensive answer."),
                ("human", "Original query: {query}\n\nSQL agent result: {sql_result}\n\nRAG agent result: {rag_result}\n\n"
                         "Generate a final answer that combines the information from both agents.")
            ])
            
            chain = prompt | self.llm
            result = chain.invoke({
                "query": state.query,
                "sql_result": state.sql_result,
                "rag_result": state.rag_result
            })
            
            state.final_answer = result.content
            
            return state
        except Exception as e:
            state.error = f"Error generating final answer: {str(e)}"
            state.final_answer = f"Error: {str(e)}"
            return state
    
    def run(self, query, db_path=None):
        """Run the multi-agent system on a query."""
        if not self.setup_complete:
            setup_result = self.setup(db_path)
            if setup_result["status"] == "error":
                return setup_result
        
        try:
            # Get database information
            if db_path:
                db_info = get_tables_info(db_path)
                if db_info["status"] == "error":
                    return db_info
                db_tables = db_info["tables"]
            else:
                db_tables = {}
            
            # Initialize the state
            initial_state = AgentState(
                query=query,
                db_info=db_tables
            )
            
            # Run the graph
            result = self.graph_app.invoke(initial_state)
            
            return {
                "status": "success",
                "result": result["final_answer"],
                "sql_result": result["sql_result"],
                "rag_result": result["rag_result"],
                "error": result["error"] if result.get("error") else None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error running supervisor agent: {str(e)}"
            }