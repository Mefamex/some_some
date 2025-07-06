# -*- coding: utf-8 -*-
# author    : mefamex
# Created   : 2025-07-06-19:04
# file_name : ollama_chat.py
# version   : v0.1
#
# updates :
#   - 2025-07-06-19:04:00 -v0.1 : created -> Ollama_chat.py 
#

"""
[TR]
# Ollama Chat Modülü
Bu modül, Ollama servisini başlatır ve mesajları gönderir.
"""

import requests, subprocess 
from time import sleep

class OllamaChat:
    def __init__(self, model="deepseek-r1:14b", host="http://localhost:11434"):
        print("🔧 Initializing Ollama Chat...")
        self.model = model
        self.host = host
        if self.start_ollama_service(): 
            print("✅ Ollama service is running")
            with open("Temp_ollama_chat_history.txt", "w") as f: f.write("Ollama Chat History:\n\n")
        else: print("❌ Failed to start Ollama service. Please ensure Ollama is installed and configured correctly.")
        
    def is_ollama_running(self):
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except: return False
    
    def start_ollama_service(self) -> bool:
        """Start Ollama service if not running"""
        if not self.is_ollama_running():
            print("🚀 Starting Ollama service...")
            try:
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                sleep(5)
                return self.is_ollama_running()
            except Exception as e: 
                print(f"❌ Failed to start Ollama: {e}")
                return False
        return True
    
    def send_message(self, message, system_prompt=None) -> str:
        """Send message to Ollama with thinking enabled for deepseek-r1"""
        if not self.is_ollama_running(): return print("❌ Ollama service is not running!") or ""
        
        try:
            full_prompt = ""
            if system_prompt: full_prompt = f"System: {system_prompt}\n\nUser: {message}"
            else: full_prompt = message
            
            # Configure options for careful and thorough thinking
            options = {
                "temperature": 0.3,        # Lower temperature for more careful responses
                "top_p": 0.7,             # More focused sampling
                "top_k": 20,              # Reduced randomness
                "max_tokens": 6000,       # More space for detailed thinking
                "repeat_penalty": 1.2,    # Avoid repetition
                "stop": [],
                "num_ctx": 8192,          # Larger context window
                "num_predict": 2048       # Allow longer predictions
            }
            
            # Enable deep thinking for deepseek-r1
            if "deepseek-r1" in self.model or "deepseek-r1:14b" in self.model:
                options["thinking"] = True
                options["max_tokens"] = 8000      # Even more tokens for deep thinking
                options["temperature"] = 0.1      # Very careful and precise
                options["top_p"] = 0.5           # Highly focused responses
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": options
            }
            
            with open("Temp_ollama_chat_history.txt", "a") as f: f.write(f"\n\n\n\n\n===================================User: \n{message}\n")
            
            response = requests.post(f"{self.host}/api/generate", json=payload, timeout=180)  # Longer timeout for careful thinking
            
            def messageReturn():
                if response.status_code == 200: return response.json().get("response", "").strip()
                else: return print(f"❌ API Error: {response.status_code}") or "" 
            
            returned = messageReturn()
            with open("Temp_ollama_chat_history.txt", "a") as f: f.write(f"\n\n\n\n\n\n===================================Bot: \n{returned}\n")
            return returned
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return ""


# Simple usage example
if __name__ == "__main__":
    # Test the simplified chat
    chat = OllamaChat()
    
    if not chat.start_ollama_service():
        print("❌ Could not start Ollama service")
        exit(1)
    
    print("🤖 Ollama Chat Ready!")
    print("💭 Deep thinking mode enabled for deepseek-r1")
    print("🧠 Configured for careful and thorough responses")
    print("⚠️  Lower temperature for precision, higher token limit for detailed thinking")
    
    # Simple system prompt for careful command generation
    system_prompt = """You are assistant. """
    
    while True:
        user_input = input("\n👤 Enter message (or 'quit' to exit): ")
        if user_input.lower() in ['quit', 'exit']:
            break
        
        response = chat.send_message(user_input, system_prompt)
        if response:
            print(f"🤖 Response: {response}")
        else:
            print("❌ No response received")
    
    print("\n\n\n END OF CHAT")