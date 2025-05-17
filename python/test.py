import fitz  # PyMuPDF
import io
from PIL import Image
from pyzbar.pyzbar import decode
import cv2
import numpy as np

pdf_path = "77.pdf"  # Replace this with your PDF file path

# Open PDF
doc = fitz.open(pdf_path)

for page_index in range(len(doc)):
    page = doc[page_index]
    image_list = page.get_images(full=True)

    print(f"\nPage {page_index + 1} has {len(image_list)} image(s).")

    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        # Load image with PIL
        image = Image.open(io.BytesIO(image_bytes))

        # Convert PIL image to OpenCV format
        cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Try to decode barcode/QR code
        decoded = decode(cv_img)

        if decoded:
            print(f"✅ Barcode found in Page {page_index + 1}, Image {img_index + 1}:")
            for obj in decoded:
                print("  - Type:", obj.type)
                print("  - Data:", obj.data.decode('utf-8'))

            # Save the image with the detected barcode
            filename = f"barcode_page{page_index + 1}_img{img_index + 1}.{image_ext}"
            image.save(filename)
            print(f"📷 Saved image as: {filename}")
        else:
            print(f"❌ No barcode found in Page {page_index + 1}, Image {img_index + 1}")
