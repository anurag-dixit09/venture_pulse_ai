import os
import sys
from google import genai
from google.genai import types

class ExecutiveAssistant:
    def __init__(self):
        """Initializes the Gemini client using a direct API key."""
        
        # Paste your actual key inside the quotes below:
        self.client = genai.Client(api_key="AQ.Ab8RN6IiiFHl1sqG9NQvDu3_KQ9YqE5bZXXJAKbVjH5Ehp6hJw")
        
        # Using gemini-2.5-flash
        self.model_name = "gemini-2.5-flash"

    def analyze_business_idea(self, idea_description: str) -> str:
        """Uses Gemini to evaluate a business idea's potential in India."""
        
        # System instructions define the 'persona' of the AI agent
        system_instruction = (
            "You are a ruthless venture capitalist and business strategist in India. "
            "Analyze the user's business idea. Give a brutal 3-bullet-point critique "
            "on how it can make money, potential legal hurdles in India, and how to scale it."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=idea_description,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7  # Balanced creativity and logic
                )
            )
            return response.text
        except Exception as e:
            return f"An error occurred while calling the API: {str(e)}"

# --- Script Execution ---
if __name__ == "__main__":
    # Instantiating the object
    bot = ExecutiveAssistant()
    
    print("\n==================================================")
    print("      AI BUSINESS STRATEGIST ENGINE ACTIVATED      ")
    print("==================================================\n")
    
    user_idea = input("Enter your business or app idea: ")
    
    print("\n[Processing] Analyzing market dynamics and feasibility...")
    verdict = bot.analyze_business_idea(user_idea)
    
    print("\n==================== VERDICT ====================")
    print(verdict)
    print("==================================================\n")