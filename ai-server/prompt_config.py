"""
Prompt configuration file - Edit this to change AI behavior
This file is monitored for changes and reloaded automatically
"""

PROMPT_TEMPLATE = """You are replying to a WhatsApp message from {sender}. Give ONLY your direct response - nothing else.Before starting each reply tag yourself as "A_V:" and begin the message that you are typing after the ":"  Keep it brief (1-2 sentences maximum). Do NOT continue the conversation or generate additional dialogue.

Message: {message}

Your response:"""

OLLAMA_MODEL = "phi3"  # or "llama3.2", "mistral", etc.

GENERATION_OPTIONS = {
    "temperature": 0.7,
    "num_predict": 50,  # Reduced from 100 to prevent long responses
    "stop": ["\n\n", "Message:", "Response:"]  # Stop generation at these tokens
}
