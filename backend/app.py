from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API key and model
openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/chat', methods=['POST'])
def chat():
    """
    Process chat messages and return AI response
    """
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({"error": "Invalid request. 'messages' field is required"}), 400
        
        messages = data.get('messages', [])
        temperature = data.get('temperature', 0.7)
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=temperature
        )
        
        # Extract the response content
        response_content = response.choices[0].message.content
        
        return jsonify({
            "response": response_content,
            "model": DEFAULT_MODEL
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "model": DEFAULT_MODEL
    })

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint with API information
    """
    return jsonify({
        "name": "AI Chat API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Send chat messages to get AI response",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    
    print(f"Starting backend API server on port {port}...")
    print(f"Using model: {DEFAULT_MODEL}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 