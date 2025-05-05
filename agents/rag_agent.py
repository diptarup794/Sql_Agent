import os
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

google_api_key = os.getenv("API_KEY")

class RAGAgent:
    def __init__(self):
        self.llm = None
        self.setup_complete = False
        
    def setup(self):
        """Set up the RAG agent."""
        try:
            # Initialize the LLM
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                convert_system_message_to_human=True,
                google_api_key=google_api_key
            )
            
            self.setup_complete = True
            
            return {
                "status": "success",
                "message": "RAG agent set up successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error setting up RAG agent: {str(e)}"
            }
    
    def run(self, query, context=None):
        """Run a query through the RAG agent with optional context."""
        if not self.setup_complete:
            return {
                "status": "error",
                "message": "RAG agent not set up. Call setup() first."
            }
            
        try:
            # Create a prompt template that includes database context
            if context:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a helpful assistant that answers questions about databases. "
                             "Use the provided database context to answer the question."),
                    ("human", "Database context: {context}\n\nQuestion: {query}")
                ])
                
                chain = prompt | self.llm
                result = chain.invoke({"context": context, "query": query})
            else:
                # If no context is provided, just use the query directly
                result = self.llm.invoke(query)
                
            return {
                "status": "success",
                "result": result.content,
                "raw_result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error running RAG query: {str(e)}"
            }