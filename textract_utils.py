import boto3
import os
from dotenv import load_dotenv
import io
import pdfplumber

# Load environment variables
load_dotenv()

# Initialize AWS Textract client
def initialize_textract_client():
    return boto3.client(
        'textract',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

# Extract handwritten answers from a multi-page PDF
def extract_handwritten_answers_from_pdf(textract_client, pdf_bytes):
    try:
        answers = []
        with pdfplumber.open(pdf_bytes) as pdf:
            for i, page in enumerate(pdf.pages):
                # Convert each page to an image
                img = page.to_image(resolution=300)
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                # Use Textract to analyze the image
                response = textract_client.analyze_document(
                    Document={'Bytes': img_bytes.getvalue()},
                    FeatureTypes=["TABLES", "FORMS"]
                )

                # Extract text from Textract response
                page_text = []
                for item in response["Blocks"]:
                    if item["BlockType"] == "LINE":
                        page_text.append(item["Text"])

                answers.append(" ".join(page_text))  # Combine lines into a single string

        return answers  # List of answers, one per page
    except Exception as e:
        return f"Error processing one or more pages of the answer sheet: {e}"
