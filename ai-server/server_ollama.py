"""
Alternative server using Ollama for easier setup
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
from datetime import datetime
import importlib
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"

# Import prompt configuration
import prompt_config

class PromptConfigReloader(FileSystemEventHandler):
    """Watches prompt_config.py and reloads it when changed"""
    def __init__(self):
        self.last_reload = datetime.now()

    def on_modified(self, event):
        if event.src_path.endswith('prompt_config.py'):
            # Debounce - only reload if 1 second has passed
            if (datetime.now() - self.last_reload).seconds < 1:
                return

            try:
                logger.info("🔄 Prompt configuration changed, reloading...")
                importlib.reload(prompt_config)
                self.last_reload = datetime.now()
                logger.info("✓ Prompt configuration reloaded successfully!")
            except Exception as e:
                logger.error(f"Failed to reload prompt config: {e}")

# Start file watcher
observer = Observer()
config_dir = Path(__file__).parent
observer.schedule(PromptConfigReloader(), str(config_dir), recursive=False)
observer.start()
logger.info(f"📁 Watching {config_dir / 'prompt_config.py'} for changes...")

def generate_response_ollama(message, sender):
    """Generate response using Ollama"""
    try:
        # Use the current prompt template from config
        prompt = prompt_config.PROMPT_TEMPLATE.format(sender=sender, message=message)

        # Add sender-specific stop token
        stop_tokens = prompt_config.GENERATION_OPTIONS.get("stop", []).copy()
        stop_tokens.append(sender + ":")

        payload = {
            "model": prompt_config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                **prompt_config.GENERATION_OPTIONS,
                "stop": stop_tokens
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
    logger.info("Starting Ollama-based server with auto-reload...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        observer.stop()
        observer.join()
