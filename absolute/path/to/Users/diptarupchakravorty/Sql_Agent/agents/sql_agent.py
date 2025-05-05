def run(self, query):
    """Run a query through the SQL agent."""
    if not self.setup_complete:
        return {
            "status": "error",
            "message": "SQL agent not set up. Call setup() first."
        }
        
    try:
        result = self.agent.invoke({"input": query})
        
        # Extract SQL query from the agent's execution steps
        sql_query = ""
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                # Look for SQL query in tool inputs
                if len(step) >= 2 and hasattr(step[0], "tool") and step[0].tool == "query_sql_database":
                    sql_query = step[0].tool_input
                    break
        
        return {
            "status": "success",
            "result": result["output"],
            "sql_query": sql_query,
            "raw_result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error running SQL query: {str(e)}"
        }