import re

def is_new_resume_page(text):
    score = 0

    if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text):
        score += 1
    if re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text):
        score += 1
    if re.search(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", text[:200]):
        score += 1

    return score >= 2  

def group_resume_pages(page_texts):
    groups = []
    current_group = [0]

    for i in range(1, len(page_texts)):
        if is_new_resume_page(page_texts[i]):
            groups.append(current_group)
            current_group = [i]
        else:
            current_group.append(i)

    groups.append(current_group)  
    return groups

