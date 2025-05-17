from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import fitz  # PyMuPDF
import io
from pyzbar.pyzbar import decode
import numpy as np
import cv2
from PIL import Image

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/upload_pdf": {"origins": "*"}})
  # This will enable CORS for the entire app

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    pdf_file = request.files.get('file')

    if pdf_file:
        try:
            # Load PDF from bytes
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")

            results = []

            for page_index in range(len(doc)):
                page = doc[page_index]
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Load image using PIL
                    image = Image.open(io.BytesIO(image_bytes))

                    # Convert PIL image to OpenCV format
                    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                    # Decode barcodes/QR codes
                    decoded_objects = decode(cv_img)

                    if decoded_objects:
                        page_data = []
                        for obj in decoded_objects:
                            page_data.append({
                                "type": obj.type,
                                "data": obj.data.decode('utf-8')
                            })
                        results.append({
                            "page": page_index + 1,
                            "images": page_data
                        })

            if results:
                return jsonify({"status": "success", "data": results}), 200
            else:
                return jsonify({"status": "no_barcodes", "message": "No barcodes found"}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    else:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

if __name__ == '__main__':
    app.run(debug=True)
