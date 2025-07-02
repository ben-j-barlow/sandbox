import PyPDF2

# Path to the original PDF
original_pdf_path = "/Users/benbarlow/Downloads/This_is_the_Project_Title.pdf"

# Path to the new PDF to be created
new_pdf_path = "/Users/benbarlow/Downloads/This_is_the_Project_Title_Extracted.pdf"

# Open the original PDF
with open(original_pdf_path, "rb") as original_pdf_file:
    reader = PyPDF2.PdfReader(original_pdf_file)
    writer = PyPDF2.PdfWriter()

    # Pages to extract (0-based index, so 1-4 are pages 0-3)
    pages_to_extract = [6,7,8,9]

    # Add each page to the writer object
    for page_num in pages_to_extract:
        page = reader.pages[page_num]
        writer.add_page(page)

    # Write the pages to the new PDF
    with open(new_pdf_path, "wb") as new_pdf_file:
        writer.write(new_pdf_file)

print(f"Extracted pages saved to {new_pdf_path}")