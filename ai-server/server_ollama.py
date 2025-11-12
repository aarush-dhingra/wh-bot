"""
Alternative server using Ollama for easier setup
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_response_ollama(message, sender):
    """Generate response using Ollama"""
    try:
        prompt = f"""You are replying to a WhatsApp message from {sender}. Give ONLY your direct response - nothing else.Before starting each reply tag yourself as "A_V:" and begin the message that you are typing after the ":"  Keep it brief (1-2 sentences maximum). Do NOT continue the conversation or generate additional dialogue.

Message: {message}

Your response:"""

        payload = {
            "model": "phi3",  # or "llama3.2", "mistral", etc.
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 50,  # Reduced from 100 to prevent long responses
                "stop": ["\n\n", "Message:", "Response:", sender + ":"]  # Stop generation at these tokens
            }
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result.get('response', '').strip()

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process that message."

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint to receive messages and return AI responses"""
    try:
        data = request.json
        message = data.get('message', '')
        sender = data.get('sender', 'Unknown')

        logger.info(f"Received from {sender}: {message}")

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        response = generate_response_ollama(message, sender)
        logger.info(f"Response: {response}")

        return jsonify({'response': response})

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    try:
        # Check if Ollama is running
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        ollama_status = resp.status_code == 200
    except:
        ollama_status = False

    return jsonify({
        'status': 'online',
        'ollama_running': ollama_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({'message': 'Ollama server is running!'})

if __name__ == '__main__':
    logger.info("Starting Ollama-based server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
