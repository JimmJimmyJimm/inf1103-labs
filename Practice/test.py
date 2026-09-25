

import os
import time
from google import genai
from google.genai import types

API_KEY = ""

client = genai.Client(api_key=API_KEY)

# Read prompt from another file
with open("prompt.txt", "r", encoding="utf-8") as file:
    prompt = file.read()

for attempt in range(5):
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
        )

        print("Gemini answer:")
        print(response.text)
        break

    except Exception as e:
        if "503" in str(e):
            print(f"Gemini busy. Retrying... ({attempt + 1}/5)")
            time.sleep(2 ** attempt)
        else:
            print("Error:", e)
            break