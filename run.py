from flask import Flask, render_template, request, jsonify, session
import os
from werkzeug.utils import secure_filename
from agents.supervisor import SupervisorAgent
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the supervisor agent
supervisor = SupervisorAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/connect', methods=['POST'])
def connect_db():
    if 'dbFile' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'})
    
    file = request.files['dbFile']
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'})
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Set up the supervisor agent with the new database
        setup_result = supervisor.setup(file_path)
        
        if setup_result['status'] == 'success':
            # Store the database path in session
            session['db_path'] = file_path
            
            # Get database info for display
            db_info = setup_result.get('db_info', {})
            tables = db_info.get('tables', {}).keys()
            
            return jsonify({
                'status': 'success',
                'message': 'Database connected successfully',
                'db_name': os.path.basename(file_path),
                'tables': list(tables)
            })
        else:
            return jsonify({
                'status': 'error',
                'message': setup_result.get('message', 'Failed to connect to database')
            })
    
    return jsonify({'status': 'error', 'message': 'Failed to upload file'})

@app.route('/query', methods=['POST'])
def process_query():
    query = request.form.get('query', '')
    
    if not query:
        return jsonify({'status': 'error', 'message': 'No query provided'})
    
    # Get database path from session
    db_path = session.get('db_path')
    
    if not db_path:
        return jsonify({'status': 'error', 'message': 'No database connected. Please connect a database first.'})
    
    # Run the query through the supervisor agent
    result = supervisor.run(query, db_path)
    
    if result['status'] == 'success':
        # Extract SQL query if available (from raw_result if present)
        sql_query = None
        if 'sql_result' in result and result['sql_result']:
            # Try to extract SQL query from the result
            # This is a simplified approach - you may need to adjust based on your actual result structure
            try:
                # Look for SQL patterns in the result
                import re
                sql_matches = re.findall(r'```sql\n(.*?)\n```', result['sql_result'], re.DOTALL)
                if sql_matches:
                    sql_query = sql_matches[0]
            except:
                pass
        
        return jsonify({
            'status': 'success',
            'result': result['result'],
            'sql_query': sql_query
        })
    else:
        return jsonify({
            'status': 'error',
            'message': result.get('message', 'Failed to process query')
        })

if __name__ == '__main__':
    app.run(debug=True)