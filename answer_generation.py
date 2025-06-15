from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Generate AI answers
def generate_answer(question, marks):
    prompt = f"The question carries {marks} marks. Generate an appropriate answer for each question"
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": question}],
            model="llama3-70b-8192",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating answer: {e}"
