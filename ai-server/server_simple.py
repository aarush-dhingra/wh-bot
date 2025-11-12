"""
Simplified server with better error handling and fallback responses
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
    """Generate response using Ollama with timeout and fallback"""
    try:
        prompt = f"Reply briefly to this WhatsApp message from {sender}: {message}"

        payload = {
            "model": "phi3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 50,  # Shorter responses
                "num_ctx": 512,     # Smaller context window
            }
        }

        logger.info(f"Sending to Ollama: {prompt[:50]}...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=20)

        if response.status_code != 200:
            logger.error(f"Ollama error: {response.status_code} - {response.text}")
            return get_fallback_response(message)

        result = response.json()
        reply = result.get('response', '').strip()

        if not reply:
            return get_fallback_response(message)

        return reply

    except requests.exceptions.Timeout:
        logger.error("Ollama timeout")
        return get_fallback_response(message)
    except Exception as e:
        logger.error(f"Error: {e}")
        return get_fallback_response(message)

def get_fallback_response(message):
    """Simple rule-based fallback responses"""
    message_lower = message.lower()

    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hey! How can I help you?"
    elif any(word in message_lower for word in ['how are you', 'whats up', 'wassup']):
        return "I'm good, thanks for asking!"
    elif '?' in message:
        return "That's a good question! Let me get back to you on that."
    else:
        return "Thanks for your message! I'll respond soon."

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
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        ollama_status = resp.status_code == 200
    except:
        ollama_status = False

    return jsonify({
        'status': 'online',
        'ollama_running': ollama_status,
        'fallback_mode': not ollama_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({'message': 'Server running! Use /chat endpoint to send messages.'})

if __name__ == '__main__':
    logger.info("Starting simplified server with fallback responses...")
    app.run(host='0.0.0.0', port=5000, debug=False)
