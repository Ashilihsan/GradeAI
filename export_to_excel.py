import pandas as pd

def export_grades_to_excel(question_numbers, marks_awarded, output_file="graded_answers.xlsx"):
    """
    Exports question numbers and awarded marks to an Excel sheet with additional calculations.

    Parameters:
    - question_numbers (list): List of question numbers.
    - marks_awarded (list): List of awarded marks.
    - output_file (str): Name of the output Excel file.
    """

    # Creating initial DataFrame
    data = {
        "Question Number": question_numbers,
        "Marks Awarded": marks_awarded
    }
    df = pd.DataFrame(data)

    # Creating additional columns as per logic
    new_question_numbers = []
    new_marks_awarded = []

    # Copy first 10 questions or available ones
    for i in range(min(10, len(question_numbers))):
        new_question_numbers.append(question_numbers[i])
        new_marks_awarded.append(marks_awarded[i])

    # Process remaining questions by summing adjacent question marks
    new_q_no = 11  # Starting from question 11
    for i in range(10, len(question_numbers), 2):
        if i + 1 < len(question_numbers):
            sum_marks = marks_awarded[i] + marks_awarded[i + 1]
        else:
            sum_marks = marks_awarded[i]
        new_question_numbers.append(new_q_no)
        new_marks_awarded.append(sum_marks)
        new_q_no += 1

    # Ensure all columns have the same length
    max_len = max(len(question_numbers), len(new_question_numbers))
    question_numbers.extend([None] * (max_len - len(question_numbers)))
    marks_awarded.extend([None] * (max_len - len(marks_awarded)))
    new_question_numbers.extend([None] * (max_len - len(new_question_numbers)))
    new_marks_awarded.extend([None] * (max_len - len(new_marks_awarded)))

    # Create final DataFrame with 6 columns
    extended_data = {
        "Question Number": question_numbers,
        "Marks Awarded": marks_awarded,
        "Processed Question Number": new_question_numbers,
        "Processed Marks Awarded": new_marks_awarded,
        "Total Marks": [None] * max_len,   # Column E
        "Result": [None] * max_len         # Column F
    }
    final_df = pd.DataFrame(extended_data)

    # Save to Excel and insert formulas into E2 and F2
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        final_df.to_excel(writer, sheet_name="Grading Results", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Grading Results"]

        # Write formula in E2: total marks (sum of D2 to D21)
        worksheet.write_formula("E2", "=SUM(D2:D21)")

        # Write formula in F2: PASS or FAIL based on E2
        worksheet.write_formula("F2", '=IF(E2>=40, "PASS", "FAIL")')

    print(f"Grading results successfully saved to {output_file}")
