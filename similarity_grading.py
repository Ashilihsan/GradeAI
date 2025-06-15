from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Calculate similarity
def calculate_similarity(text1, text2):
    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
        return similarity
    except Exception as e:
        return f"Error calculating similarity: {e}"

# Grading system for Part A
def grade_part_a(similarity):
    if similarity >= 0.8:
        return 3
    elif 0.43 <= similarity < 0.8:
        return 2
    elif 0.2 <= similarity < 0.42:
        return 1
    else:
        return 0

# Grading system for Part B
def grade_part_b(similarity,full_marks):
    if similarity >= 0.8:
        return full_marks
    elif 0.65 <= similarity < 0.8:
        return round(0.7142 * full_marks, 2)
    elif 0.55 <= similarity < 0.64:
        return round(0.5714 * full_marks, 2)
    elif 0.2 <= similarity < 0.55:
        return round(0.3571 * full_marks, 2)
    else:
        return 0
