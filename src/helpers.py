import pandas as pd
import re
import os
import requests
from fuzzywuzzy import fuzz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def load_properties(file_path='data/properties.csv'):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return None

def get_property_by_id(df, listing_id):
    result = df[df['listing_id'] == listing_id].to_dict('records')
    return result if result else None

def get_property_by_name(df, property_name):
    # Find the property name with the highest fuzzy match score
    best_match_score = 0
    best_match_prop = None
    for index, row in df.iterrows():
        score = fuzz.ratio(property_name.lower(), row['property_name'].lower())
        if score > best_match_score and score > 70:  # Use a threshold like 70
            best_match_score = score
            best_match_prop = row
    
    if best_match_prop is not None:
        return [best_match_prop.to_dict()]
    return None

def polish_with_llm(text_to_polish):
    if not GROQ_API_KEY:
        print("Warning: LLM_API_KEY not set. Returning unpolished text.")
        return text_to_polish
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "google/gemma-7b-it",
        "messages": [
            {"role": "user", "content": f"Rewrite this factual information into a polite, natural language chat response: {text_to_polish}"}
        ],
        "temperature": 0.5
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        polished_text = response.json()['choices'][0]['message']['content']
        return polished_text
    except requests.exceptions.RequestException as e:
        print(f"LLM API call failed: {e}")
        return text_to_polish