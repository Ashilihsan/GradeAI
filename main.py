import streamlit as st
from textract_utils import initialize_textract_client, extract_handwritten_answers_from_pdf
from question_processing import extract_part_a_questions, extract_part_b_questions
from answer_generation import generate_answer
from similarity_grading import calculate_similarity, grade_part_a, grade_part_b
from export_to_excel import export_grades_to_excel
import pdfplumber
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit app
st.title("KTU Question Paper Processor with Grading System")

# Sidebar for uploads
st.sidebar.header("Upload Files")
uploaded_question_paper = st.sidebar.file_uploader("Upload Question Paper (PDF)", type=["pdf"])
uploaded_answer_sheet = st.sidebar.file_uploader("Upload Answer Sheet (PDF with one answer per page)", type=["pdf"])

# Global variables to store state
if "part_a_questions" not in st.session_state:
    st.session_state["part_a_questions"] = []
if "part_a_ai_answers" not in st.session_state:
    st.session_state["part_a_ai_answers"] = []
if "part_b_questions" not in st.session_state:
    st.session_state["part_b_questions"] = []
if "part_b_ai_answers" not in st.session_state:
    st.session_state["part_b_ai_answers"] = []
if "marks_awarded_part_a" not in st.session_state:
    st.session_state["marks_awarded_part_a"] = []
if "marks_awarded_part_b" not in st.session_state:
    st.session_state["marks_awarded_part_b"] = []

# Section 1: Question Paper Processing
if uploaded_question_paper:
    st.header("Extracted Questions and AI Answers")
    pdf_text = ""
    with pdfplumber.open(uploaded_question_paper) as pdf:
        for page in pdf.pages:
            pdf_text += page.extract_text()

    # Extract Part A and Part B questions
    st.session_state["part_a_questions"] = extract_part_a_questions(pdf_text).split("\n")
    st.session_state["part_b_questions"] = extract_part_b_questions(pdf_text).split("\n")

    # Display extracted questions
    st.subheader("Extracted Part A Questions")
    st.text_area("Questions (Part A)", "\n".join(st.session_state["part_a_questions"]), height=200)

    st.subheader("Extracted Part B Questions")
    st.text_area("Questions (Part B)", "\n".join(st.session_state["part_b_questions"]), height=200)

# Generate AI answers for Part A
if st.session_state["part_a_questions"]:
    question_blocks = []
    current_question = ""

    for line in st.session_state["part_a_questions"]:
        if re.match(r"^\d+\.", line.strip()):
            if current_question:
                question_blocks.append(current_question.strip())
            current_question = line
        else:
            current_question += " " + line

    if current_question:
        question_blocks.append(current_question.strip())

    st.subheader("AI-Generated Answers for Part A")
    for i, question in enumerate(question_blocks, start=1):
        ai_answer = generate_answer(question, marks=3)
        st.session_state["part_a_ai_answers"].append(ai_answer)
        st.write(f"**Q{i} (Part A):** {question}")
        st.write(f"**AI Answer {i}:** {ai_answer}")

# Generate AI answers for Part B
if st.session_state["part_b_questions"]:
    st.subheader("AI-Generated Answers for Part B")

    question_blocks = []
    current_question = ""
    marks_per_question = []
    marks = 0

    for line in st.session_state["part_b_questions"]:
        if re.match(r"^\d+\.\s*[a-z]*\)", line.strip()):
            if current_question:
                question_blocks.append(current_question.strip())
                marks_per_question.append(marks)
            current_question = line

            marks = re.findall(r"\((\d+)\)", line)
            if marks:
                marks = int(marks[0])
            else:
                marks = 8
        else:
            current_question += " " + line

    if current_question:
        question_blocks.append(current_question.strip())
        marks_per_question.append(marks)

    for i, question in enumerate(question_blocks, start=1):
        question_marks = marks_per_question[i - 1]
        ai_answer = generate_answer(question, marks=question_marks)
        st.session_state["part_b_ai_answers"].append(ai_answer)
        st.write(f"**Q{i} (Part B):** {question}")
        st.write(f"**AI Answer {i}:** {ai_answer}")
        

# Section 2: Handwriting Recognition and Grading
if uploaded_answer_sheet:
    st.header("Upload Answer for Grading")
    textract_client = initialize_textract_client()

    with st.spinner("Extracting handwritten answers from PDF..."):
        answers = extract_handwritten_answers_from_pdf(textract_client, uploaded_answer_sheet)

    if isinstance(answers, str):  # If an error message is returned
        st.error(answers)
    else:
        for i, extracted_answer in enumerate(answers, start=1):
            # ✅ Process Part A First (Exactly 10 Questions)
            if len(st.session_state["marks_awarded_part_a"]) < 10:  # Only process first 10 questions for Part A
                current_question_index = len(st.session_state["marks_awarded_part_a"])
                ai_answer = st.session_state["part_a_ai_answers"][current_question_index]  # Fetch AI answer for Part A
                similarity_score = calculate_similarity(extracted_answer, ai_answer)  # Compute similarity
                marks = grade_part_a(similarity_score)  # Grade answer
                st.session_state["marks_awarded_part_a"].append(marks)  # Store marks

                # Display Part A results
                st.write(f"**Q{current_question_index + 1} (Part A):**")
                st.write(f"- **AI Answer:** {ai_answer}")
                st.write(f"- **Student Answer (Page {i}):** {extracted_answer}")
                st.write(f"- **Similarity Score:** {similarity_score:.2f}")
                st.write(f"- **Marks Awarded:** {marks} / 3")

            # ✅ Ensure all 10 Part A questions are completed before processing Part B
            elif len(st.session_state["marks_awarded_part_b"]) < len(st.session_state["part_b_questions"]):
                current_question_index = len(st.session_state["marks_awarded_part_b"])  

                # Prevent out-of-range error
                if current_question_index >= len(st.session_state["part_b_questions"]):
                    st.error("Error: Trying to access an invalid Part B question index.")
                    break  # Exit loop if there's an error

                # Correctly determine whether it's 'a' or 'b' using even/odd index
                question_number = 11 + (current_question_index // 2)  # Question number: 11, 12, 13...
                sub_question = "a" if current_question_index % 2 == 0 else "b"  # Assign 'a' for even index, 'b' for odd index

                # Fetch correct Part B question and AI-generated answer
                ai_answer = st.session_state["part_b_ai_answers"][current_question_index]  
                question_text = st.session_state["part_b_questions"][current_question_index]  

                similarity_score = calculate_similarity(extracted_answer, ai_answer)  # Compute similarity

                # Extract marks from the question text (if available)
                question_marks = re.findall(r"\((\d+)\)", question_text)
                full_marks = int(question_marks[0]) if question_marks else 7 # Default to 14 marks if not specified

                marks = grade_part_b(similarity_score, full_marks)  # Grade answer
                st.session_state["marks_awarded_part_b"].append(marks)  # Store marks

                # Display Part B results
                st.write(f"**Q{question_number}{sub_question} (Part B):**")  # Displays Q11a, Q11b, Q12a, Q12b...
                st.write(f"- **AI Answer:** {ai_answer}")
                st.write(f"- **Student Answer (Page {i}):** {extracted_answer}")
                st.write(f"- **Similarity Score:** {similarity_score:.2f}")
                st.write(f"- **Marks Awarded:** {marks} / {full_marks}")



        st.success("Grading completed for all pages.")

# Display Total Marks
total_marks_a = sum(st.session_state["marks_awarded_part_a"])
total_marks_b = sum(st.session_state["marks_awarded_part_b"])
st.write(f"**Total Marks for Part A:** {total_marks_a} / {30}")
st.write(f"**Total Marks for Part B:** {total_marks_b} / {70}")

from export_to_excel import export_grades_to_excel

# Ensure correct list lengths before exporting
min_length = min(len(st.session_state["part_a_questions"]), len(st.session_state["marks_awarded_part_a"]))
min_length_b = min(len(st.session_state["part_b_questions"]), len(st.session_state["marks_awarded_part_b"]))

# Trim lists to the same length
part_a_questions = st.session_state["part_a_questions"][:min_length]
marks_awarded_part_a = st.session_state["marks_awarded_part_a"][:min_length]

part_b_questions = st.session_state["part_b_questions"][:min_length_b]
marks_awarded_part_b = st.session_state["marks_awarded_part_b"][:min_length_b]

# Create question numbers
question_numbers = [f"Q{i+1}" for i in range(len(part_a_questions) + len(part_b_questions))]

# Combine marks
marks_awarded = marks_awarded_part_a + marks_awarded_part_b

# Export to Excel
export_grades_to_excel(question_numbers, marks_awarded)

st.success("Grading results have been saved to 'graded_answers.xlsx'.")



