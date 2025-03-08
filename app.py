from flask import Flask, render_template, request, jsonify, url_for, send_file
from PIL import Image
import io
import os
import base64
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/save-strip', methods=['POST'])
def save_strip():
    data = request.json
    if 'photos' in data:
        try:
            images = []
            for img_data in data['photos']:
                image_data = img_data.split(",")[1] if "," in img_data else img_data
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                images.append(image)

            if not images:
                return jsonify({'success': False, 'message': 'No images received'})

            # Ensure the upload directory exists
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            # Determine strip size
            width = max(img.width for img in images)
            height = sum(img.height for img in images)
            strip_image = Image.new('RGB', (width, height), (255, 255, 255))

            # Merge images into a single strip
            y_offset = 0
            for img in images:
                strip_image.paste(img, (0, y_offset))
                y_offset += img.height

            # Save the final strip
            downloads_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = f"photostrip_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            filepath = os.path.join(upload_dir, filename)
            strip_image.save(filepath)

            print(f"✅ Photo strip saved at: {filepath}")
            
            # Return the file as a downloadable response
            return send_file(filepath, as_attachment=True)

        except Exception as e:
            return jsonify({'success': False, 'message': f'Error processing strip: {str(e)}'})

    return jsonify({'success': False, 'message': 'No photo data received'})


if __name__ == '__main__':
    app.run(debug=True)