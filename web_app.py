import streamlit as str_ui
from google import genai
from google.genai import types

class WebStrategist:
    def __init__(self):
        # Paste your working API key inside the quotes below
        self.client = genai.Client(api_key="AQ.Ab8RN6IiiFHl1sqG9NQvDu3_KQ9YqE5bZXXJAKbVjH5Ehp6hJw")
        self.model_name = "gemini-2.5-flash"

    def analyze(self, idea: str) -> str:
        system_instruction = (
            "You are a ruthless venture capitalist and business strategist in India. "
            "Analyze the user's business idea. Give a brutal 3-bullet-point critique "
            "on how it can make money, potential legal hurdles in India, and how to scale it. "
            "Format the output beautifully using markdown bullet points."
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=idea,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )
        return response.text

# --- Streamlit UI Configurations ---
str_ui.set_page_config(page_title="VenturePulse AI", page_icon="📈", layout="centered")
str_ui.title("📈 VenturePulse AI — Venture Capital Agent")

str_ui.write("Submit your startup or product idea for a brutal, realistic market viability critique.")

# Initialize our engine
engine = WebStrategist()

# User Input text box
user_input = str_ui.text_area("Enter your business idea here:", placeholder="e.g., A premium tiffin service for college students...")

if str_ui.button("Run Feasibility Analysis", type="primary"):
    if user_input.strip() == "":
        str_ui.warning("Please enter a valid idea first!")
    else:
        with str_ui.spinner("Analyzing market dynamics, legal hurdles, and capital efficiency..."):
            verdict = engine.analyze(user_input)
            
        str_ui.success("Analysis Complete!")
        str_ui.markdown("### 📊 Venture Capitalist Verdict")
        str_ui.info(verdict)