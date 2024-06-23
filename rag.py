import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text

pdf_path = "data/2023-Pregnancy-Purplebook_19Jan2024.pdf"
pdf_text = extract_text_from_pdf(pdf_path)
