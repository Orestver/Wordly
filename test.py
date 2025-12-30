import json
import re
from pdfminer.high_level import extract_text
from docx import Document

# --- 1. Очищення рядка ---
def parse_line_to_dict(line):
    """
    Парсить рядок формату: англійська - українська
    Автоматично обробляє багатослівні англійські терміни та тире всередині.
    """
    line = line.strip()
    if not line:
        return None, None

    # прибираємо цифри на початку
    line = re.sub(r"^\d+[\.\)]?\s*", "", line)

    # приводимо всі тире до одного виду
    line = line.replace("–", "-").replace("—", "-")

    # шукаємо останній дефіс, який відокремлює англійське слово від перекладу
    if "-" not in line:
        return None, None

    parts = line.rsplit("-", 1)
    if len(parts) != 2:
        return None, None

    eng, ukr = parts
    eng = eng.strip().lower()  # англійська
    ukr = ukr.strip()          # українська
    return eng, ukr

# --- 2. PDF ---
def pdf_to_words(pdf_path):
    text = extract_text(pdf_path)
    words_dict = {}
    for line in text.splitlines():
        eng, ukr = parse_line_to_dict(line)
        if eng and ukr:
            words_dict[eng] = ukr
    return words_dict

# --- 3. DOCX ---
def docx_to_words(docx_path):
    doc = Document(docx_path)
    words_dict = {}
    for paragraph in doc.paragraphs:
        eng, ukr = parse_line_to_dict(paragraph.text)
        if eng and ukr:
            words_dict[eng] = ukr
    return words_dict

# --- 4. Об’єднання PDF та DOCX ---
def build_words_list(pdf_path=None, docx_path=None):
    words_list = {}

    # PDF
    if pdf_path:
        words_list.update(pdf_to_words(pdf_path))

    # DOCX
    if docx_path:
        words_list.update(docx_to_words(docx_path))

    return words_list

# --- 5. Збереження у файл ---
def save_words_to_file(words_dict, filename="words.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(words_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # --- 6. Приклад використання ---
    pdf_file = "words.pdf"  # ваш PDF
    docx_file = "sources/words 2_2 year st.docx"  # ваш DOCX

    words_list = build_words_list(None, docx_file)
    save_words_to_file(words_list)

    print("Готовий словник:", words_list)


