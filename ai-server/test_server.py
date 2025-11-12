"""
Test script to verify the AI server is working
"""
import requests
import json

SERVER_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{SERVER_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat(message, sender="TestUser"):
    """Test chat endpoint"""
    print(f"\nTesting /chat endpoint...")
    print(f"Sending: {message}")
    try:
        payload = {
            "message": message,
            "sender": sender
        }
        response = requests.post(f"{SERVER_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"AI Response: {result.get('response', 'No response')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AI Server Test Script")
    print("=" * 50)

    # Test health
    if test_health():
        print("\n✓ Health check passed")
    else:
        print("\n✗ Health check failed")
        exit(1)

    # Test chat
    test_messages = [
        "Hello, how are you?",
        "What's the weather like?",
        "Can you help me with something?"
    ]

    for msg in test_messages:
        if test_chat(msg):
            print("✓ Test passed")
        else:
            print("✗ Test failed")
        print("-" * 50)
