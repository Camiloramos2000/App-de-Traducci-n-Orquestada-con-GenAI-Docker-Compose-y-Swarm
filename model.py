from google import genai
from google.genai import types
import time
import os

class Model:
    @staticmethod
    def use(prompt):
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la variable de entorno GENAI_API_KEY")
        
        client = genai.Client(api_key=api_key)

        time_start = time.time()
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a translator"
                )
            )
            answer = response.text
        except Exception as e:
            return f"Error: {e}", 0, 0.0

        time_end = time.time()
        time_taken = time_end - time_start
        len_answer = len(answer)

        return answer, len_answer, time_taken
