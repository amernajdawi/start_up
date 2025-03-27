import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# Set your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
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
                "model": "gpt-4o-mini"
            }).encode('utf-8'))
        elif self.path == '/' or self.path == '/index.html':
            # Serve the static HTML file
            try:
                # Check if static directory exists, if not create it
                static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
                if not os.path.exists(static_dir):
                    os.makedirs(static_dir)
                
                # Path to the HTML file
                html_file = os.path.join(static_dir, "index.html")
                
                # If the HTML file doesn't exist, create a basic one
                if not os.path.exists(html_file):
                    with open(html_file, 'w') as f:
                        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Regulatory Query System - Simple Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #2c3e50;
        }
        .chat-container {
            margin-top: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
        }
        .user {
            background-color: #f1f0f0;
            text-align: right;
        }
        .assistant {
            background-color: #e3f2fd;
        }
        .sources {
            margin-top: 10px;
            font-size: 0.9em;
            border-top: 1px solid #ddd;
            padding-top: 5px;
        }
        .source-item {
            margin: 5px 0;
        }
        input[type="text"] {
            width: 70%;
            padding: 10px;
            margin-right: 10px;
        }
        button {
            padding: 10px 15px;
            background-color: #4285f4;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>AI Regulatory Query System</h1>
    <p>Ask questions about ESG regulations, CSRD, ESRS, or other sustainability reporting requirements.</p>
    
    <div class="chat-container" id="chat-container"></div>
    
    <div style="margin-top: 20px;">
        <input type="text" id="query-input" placeholder="Ask about regulations...">
        <button onclick="sendQuery()">Send</button>
    </div>

    <script>
        const messages = [];
        
        function addMessage(content, role, sources = []) {
            const message = { role, content };
            messages.push(message);
            
            const chatContainer = document.getElementById('chat-container');
            const messageElement = document.createElement('div');
            messageElement.className = `message ${role}`;
            messageElement.textContent = content;
            
            // Add sources if available
            if (sources.length > 0) {
                const sourcesElement = document.createElement('div');
                sourcesElement.className = 'sources';
                sourcesElement.innerHTML = '<strong>Sources:</strong>';
                
                const sourcesList = document.createElement('ul');
                sources.forEach(source => {
                    const sourceItem = document.createElement('li');
                    sourceItem.className = 'source-item';
                    sourceItem.textContent = source.title;
                    sourcesList.appendChild(sourceItem);
                });
                
                sourcesElement.appendChild(sourcesList);
                messageElement.appendChild(sourcesElement);
            }
            
            chatContainer.appendChild(messageElement);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        async function sendQuery() {
            const input = document.getElementById('query-input');
            const query = input.value.trim();
            
            if (!query) return;
            
            // Add user message to chat
            addMessage(query, 'user');
            input.value = '';
            
            try {
                // Send query to API
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        messages: messages
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`API returned status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Add assistant response to chat
                addMessage(data.response, 'assistant', data.sources || []);
                
            } catch (error) {
                console.error('Error:', error);
                addMessage(`Error: ${error.message}. Please check if the backend server is running.`, 'assistant');
            }
        }
        
        // Allow sending messages with Enter key
        document.getElementById('query-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendQuery();
            }
        });
    </script>
</body>
</html>''')
                
                # Read and serve the HTML file
                with open(html_file, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(f.read())
            except Exception as e:
                print(f"Error serving HTML: {e}")
                self._set_response(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

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
            if 'messages' not in data:
                self._set_response(400)
                self.wfile.write(json.dumps({"error": "Missing 'messages' field"}).encode('utf-8'))
                return
            
            messages = data.get('messages', [])
            
            # Check if this is a regulatory query
            is_regulatory = self.is_regulatory_query(messages)
            
            # Handle the query using simulated response
            if is_regulatory:
                response = self.handle_regulatory_query(messages)
            else:
                response = self.handle_regular_chat(messages)
            
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def is_regulatory_query(self, messages):
        """Simple check to see if this might be a regulatory query"""
        if not messages:
            return False
            
        # Get the most recent user message
        user_message = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '').lower()
                break
                
        if not user_message:
            return False
            
        # Check for regulatory keywords
        regulatory_keywords = [
            'regulation', 'directive', 'compliance', 'legal', 'esg', 'csrd', 
            'esrs', 'sustainability', 'reporting', 'eu', 'tax', 'ghg', 'protocol',
            'corporate', 'environment', 'social', 'governance'
        ]
        
        return any(keyword in user_message for keyword in regulatory_keywords)

    def handle_regulatory_query(self, messages):
        """Simulate response for regulatory queries"""
        # For the simplified version, we'll hardcode some example responses
        last_message = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_message = msg.get('content', '').lower()
                break
                
        # Simulate response with sources
        if 'esrs' in last_message or 'sustainability reporting' in last_message:
            return {
                "response": "The European Sustainability Reporting Standards (ESRS) are defined in Delegated Regulation (EU) 2023/2772. According to this regulation, companies must report on environmental, social, and governance aspects of their business. The ESRS include specific disclosure requirements for environmental impacts, social factors, and governance practices.",
                "sources": [
                    {
                        "title": "Delegated Regulation (EU) 2023/2772 (EU)",
                        "filename": "1_2023-07-31_DelVO_2023_2772_ESRS_EU.pdf",
                        "link": "/data/1_2023-07-31_DelVO_2023_2772_ESRS_EU.pdf"
                    }
                ],
                "model": "gpt-4o-mini",
                "is_regulatory": True
            }
        elif 'csrd' in last_message or 'corporate sustainability' in last_message:
            return {
                "response": "The Corporate Sustainability Reporting Directive (CSRD) is established in Directive (EU) 2022/2464. This directive expands sustainability reporting requirements to more companies, including large and listed companies. It requires detailed reporting on environmental and social impacts, with specific disclosures based on the ESRS.",
                "sources": [
                    {
                        "title": "Directive (EU) 2022/2464 (EU)",
                        "filename": "1_2022-12-14_RL_2022_2464_CSRD_EU.pdf",
                        "link": "/data/1_2022-12-14_RL_2022_2464_CSRD_EU.pdf"
                    }
                ],
                "model": "gpt-4o-mini",
                "is_regulatory": True
            }
        elif 'ghg' in last_message or 'greenhouse' in last_message:
            return {
                "response": "The Greenhouse Gas (GHG) Protocol provides standards and guidance for companies and organizations to measure and manage their greenhouse gas emissions. It includes specific protocols for different scopes of emissions and for various sectors.",
                "sources": [
                    {
                        "title": "GHG Protocol (WRI&WBCSD)",
                        "filename": "2_E1-6_2004-03_G_GHG-Prot_WRI&WBCSD.pdf",
                        "link": "/data/2_E1-6_2004-03_G_GHG-Prot_WRI&WBCSD.pdf"
                    }
                ],
                "model": "gpt-4o-mini",
                "is_regulatory": True
            }
        else:
            return {
                "response": "Based on regulatory frameworks like the EU's Corporate Sustainability Reporting Directive (CSRD) and the European Sustainability Reporting Standards (ESRS), companies must report on sustainability matters that are material to their business. This includes environmental impacts, social considerations, and governance practices.",
                "sources": [
                    {
                        "title": "Delegated Regulation (EU) 2023/2772 (EU)",
                        "filename": "1_2023-07-31_DelVO_2023_2772_ESRS_EU.pdf",
                        "link": "/data/1_2023-07-31_DelVO_2023_2772_ESRS_EU.pdf"
                    },
                    {
                        "title": "Directive (EU) 2022/2464 (EU)",
                        "filename": "1_2022-12-14_RL_2022_2464_CSRD_EU.pdf",
                        "link": "/data/1_2022-12-14_RL_2022_2464_CSRD_EU.pdf"
                    }
                ],
                "model": "gpt-4o-mini",
                "is_regulatory": True
            }

    def handle_regular_chat(self, messages):
        """Handle non-regulatory chat messages"""
        return {
            "response": "I'm a simplified version of the AI assistant. I can provide general information, but for detailed regulatory queries, please ask specific questions about ESG regulations, CSRD, ESRS, or sustainability reporting.",
            "sources": [],
            "model": "gpt-4o-mini",
            "is_regulatory": False
        }

def run_server(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    print(f"Web interface available at http://localhost:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    run_server(port=port) 