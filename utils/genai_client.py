# utils/genai_client.py
import os
import google.generativeai as genai
from google.generativeai import tool

# In a real application, you would configure the API key and get the model
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def get_generative_model():
    return model

# Example of where to add ADK tool definitions for Generative AI
@tool
def get_spending_insights(receipt_data: dict):
    """Analyzes spending data to provide insights and budget forecasts."""
    model = get_generative_model()
    prompt = f"Analyze this receipt and provide spending insights: {receipt_data}"
    response = model.generate_content(prompt)
    return response.text
