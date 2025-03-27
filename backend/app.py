import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from query_engine import get_query_engine

# Define the port to run on
PORT = int(os.getenv('PORT', 8000))

class RegulationAPIHandler(BaseHTTPRequestHandler):
    def _set_response(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_response()

    def do_GET(self):
        if self.path == '/health':
            self._set_response()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "vector_db": "initialized" if get_query_engine().documents else "not initialized"
            }).encode('utf-8'))
        elif self.path == '/' or self.path == '/index.html':
            # Serve the static HTML file
            try:
                # Path to the HTML file
                html_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        "frontend", "src", "index.html")
                
                # Fallback to a basic HTML if the file doesn't exist
                if not os.path.exists(html_file):
                    self._serve_basic_html()
                    return
                
                # Read and serve the HTML file
                with open(html_file, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
            except Exception as e:
                print(f"Error serving HTML: {e}")
                self._serve_basic_html()
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))
    
    def _serve_basic_html(self):
        """Serve a basic HTML interface if no frontend file is found."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = '''<!DOCTYPE html>
<html>
<head>
    <title>AI Regulatory Query System</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .container { margin-top: 20px; }
        #results { margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        input[type="text"] { width: 70%; padding: 8px; margin-right: 10px; }
        button { padding: 8px 15px; background-color: #4285f4; color: white; border: none; border-radius: 3px; cursor: pointer; }
        .sources { margin-top: 15px; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>AI Regulatory Query System</h1>
    <p>Ask questions about ESG regulations, CSRD, ESRS, or other sustainability reporting requirements.</p>
    
    <div class="container">
        <input type="text" id="query-input" placeholder="Type your regulatory query here...">
        <button onclick="sendQuery()">Ask</button>
    </div>
    
    <div id="results"></div>
    
    <script>
        async function sendQuery() {
            const query = document.getElementById('query-input').value;
            if (!query) return;
            
            document.getElementById('results').innerHTML = 'Searching...';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        messages: [{ role: 'user', content: query }] 
                    })
                });
                
                const data = await response.json();
                
                let html = `<h3>Answer:</h3><p>${data.response}</p>`;
                
                if (data.sources && data.sources.length > 0) {
                    html += '<div class="sources"><h4>Sources:</h4><ul>';
                    for (const source of data.sources) {
                        const filename = source.filename || source.source.split('/').pop();
                        html += `<li>${source.document_type || 'Document'} (${source.publisher || 'Unknown'}): ${filename}</li>`;
                    }
                    html += '</ul></div>';
                }
                
                document.getElementById('results').innerHTML = html;
                
            } catch (error) {
                document.getElementById('results').innerHTML = `<p>Error: ${error.message}</p>`;
            }
        }
        
        // Enable Enter key
        document.getElementById('query-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendQuery();
        });
    </script>
</body>
</html>'''
        
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            self._set_response(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
            return

        if self.path == '/chat':
            # Get the query from the request
            if 'messages' not in data:
                self._set_response(400)
                self.wfile.write(json.dumps({"error": "Missing 'messages' field"}).encode('utf-8'))
                return
            
            messages = data.get('messages', [])
            
            # Get the last user message
            user_query = None
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    user_query = msg.get('content')
                    break
            
            if not user_query:
                self._set_response(400)
                self.wfile.write(json.dumps({"error": "No user message found"}).encode('utf-8'))
                return
            
            # Get the query engine and process the query
            query_engine = get_query_engine()
            result = query_engine.answer_query(user_query)
            
            # Format sources for the response
            formatted_sources = []
            for source in result.get('sources', []):
                # Extract filename from the source path
                filename = os.path.basename(source.get('source', ''))
                
                # Format document info
                doc_type = source.get('document_type', 'Unknown')
                designation = source.get('designation', 'Unknown')
                publisher = source.get('publisher', 'Unknown')
                
                formatted_sources.append({
                    "title": f"{doc_type} {designation} ({publisher})",
                    "filename": filename,
                    "link": f"/data/{filename}"
                })
            
            # Build the response
            response = {
                "response": result.get('answer', ''),
                "sources": formatted_sources,
                "model": "Vector Search"
            }
            
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

def run_server(port=PORT):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RegulationAPIHandler)
    print(f"Starting server on port {port}...")
    print(f"Web interface available at http://localhost:{port}/")
    
    # Initialize the query engine
    print("Initializing query engine...")
    engine = get_query_engine()
    if engine.documents:
        print(f"Loaded {len(engine.documents)} document chunks.")
    else:
        print("No documents loaded. Please check the data directory.")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run_server() 