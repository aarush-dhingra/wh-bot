from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables for model
model = None
tokenizer = None
pipe = None

def load_model():
    """Load the Phi-3 Mini model - optimized for RTX 4060"""
    global model, tokenizer, pipe

    try:
        logger.info("Loading Phi-3 Mini model...")
        model_name = "microsoft/Phi-3-mini-4k-instruct"

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

        # Load model with GPU support
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use FP16 for faster inference
            device_map="cuda",  # Use GPU
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        # Create pipeline for easier inference
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0,  # GPU
            max_new_tokens=150,  # Limit response length
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

        logger.info("Model loaded successfully!")
        logger.info(f"Using device: {model.device}")

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def generate_response(message, sender):
    """Generate AI response using Phi-3"""
    try:
        # Create a conversational prompt
        prompt = f"""<|system|>
You are a helpful AI assistant replying to WhatsApp messages. Keep responses brief, friendly, and natural (1-3 sentences max).
<|end|>
<|user|>
{sender} sent you: {message}
<|end|>
<|assistant|>
"""

        # Generate response
        outputs = pipe(prompt)
        response_text = outputs[0]['generated_text']

        # Extract only the assistant's response
        if "<|assistant|>" in response_text:
            response_text = response_text.split("<|assistant|>")[-1].strip()

        # Clean up any remaining special tokens
        response_text = response_text.replace("<|end|>", "").strip()

        # Limit to first paragraph/sentence if too long
        if len(response_text) > 300:
            response_text = response_text[:300].rsplit('.', 1)[0] + '.'

        return response_text

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process that message right now."

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint to receive messages and return AI responses"""
    try:
        data = request.json
        message = data.get('message', '')
        sender = data.get('sender', 'Unknown')

        logger.info(f"Received message from {sender}: {message}")

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Generate AI response
        response = generate_response(message, sender)

        logger.info(f"Generated response: {response}")

        return jsonify({'response': response})

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return jsonify({'message': 'Server is running!', 'gpu_available': torch.cuda.is_available()})

if __name__ == '__main__':
    # Check GPU availability
    if torch.cuda.is_available():
        logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        logger.warning("No GPU detected! Model will run on CPU (slower)")

    # Load model on startup
    load_model()

    # Start Flask server
    # Use 0.0.0.0 to allow connections from other devices on network
    app.run(host='0.0.0.0', port=5000, debug=False)
