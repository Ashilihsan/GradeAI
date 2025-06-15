from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Extract Part A questions
def extract_part_a_questions(pdf_text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "Extract only Part A questions. Ignore all other content."
            },
                {"role": "user", "content": pdf_text}],
            model="llama3-70b-8192",
        )
        raw_output = chat_completion.choices[0].message.content.strip()
        return "\n".join(raw_output.split("\n")[2:])  # Skip first two lines
    except Exception as e:
        return f"Error extracting Part A questions: {e}"

# Extract Part B questions
def extract_part_b_questions(pdf_text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "Extract only Part B questions along with their marks. "
                            "Ensure each question is extracted separately. "
                            "If a question has multiple sub-questions (like 11a, 11b), "
                            "split them into two separate questions. "
                            "Do not merge them. Read the full question, even if marks appear in between. "
                            "Ignore all other content and do not modify the numbering."},
                {"role": "user", "content": pdf_text}],
            model="llama3-70b-8192",
        )
        raw_output = chat_completion.choices[0].message.content.strip()
        return "\n".join(raw_output.split("\n")[2:])  # Skip first two lines (headers or irrelevant data)
    except Exception as e:
        return f"Error extracting Part B questions: {e}"
