from pdf2image import convert_from_path
import os

# Function to convert PDF to JPEG
def pdf_to_jpeg(pdf_path, output_folder):
    # Convert PDF to list of images
    images = convert_from_path(pdf_path)
    
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Save each image as a JPEG
    for i, image in enumerate(images):
        image.save(os.path.join(output_folder, f'page_{i+1}.jpeg'), 'JPEG')

# Specify the PDF file path and the output folder
pdf_path = 'images.pdf'
output_folder = './'

# Convert PDF to JPEG
pdf_to_jpeg(pdf_path, output_folder)
