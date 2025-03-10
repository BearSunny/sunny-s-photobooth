from flask import Flask, render_template, request, jsonify, url_for, send_file
from PIL import Image, ImageDraw
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
    if 'photos' not in data:
        return jsonify({'success': False, 'message': 'No images received'}), 400

    try:
        images = []
        for img_data in data['photos']:
            if "," in img_data:
                img_data = img_data.split(",")[1]
            
            image_data = base64.b64decode(img_data)
            image = Image.open(io.BytesIO(image_data))
            images.append(image)

        if not images:
            return jsonify({'success': False, 'message': 'No images received'})

        bg_color = data.get('backgroundColor', '#FFE5E6')
        # Convert hex to RGB for PIL
        if bg_color.startswith("#"):
            bg_color = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))

        # Define strip dimensions
        padding = 20
        border_thickness = 10
        strip_width = max(img.width for img in images) + 2 * padding
        strip_height = sum(img.height for img in images) + (len(images) - 1) * padding + 2 * padding

        # Determine strip size
        strip_image = Image.new('RGB', (strip_width, strip_height), bg_color)
        draw = ImageDraw.Draw(strip_image)

        draw.rectangle(
            [border_thickness, border_thickness, strip_width - border_thickness, strip_height - border_thickness],
            outline="black",
            width=border_thickness
        )

        # Merge images into a single strip
        y_offset = padding
        for img in images:
            x_offset = (strip_width - img.width) // 2
            strip_image.paste(img, (x_offset, y_offset))
            y_offset += img.height + padding

        # Ensure the upload directory exists
        upload_dir = os.path.join('static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Save the final strip
        downloads_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"photostrip_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        filepath = os.path.join(upload_dir, filename)
        strip_image.save(filepath)

        print(f"✅ Photo strip saved at: {filepath}")
        
        # Return the file as a downloadable response
        return send_file(filepath, mimetype="image/png", as_attachment=True)

    except Exception as e:
        print("❌ Error generating photo strip:", str(e))
        return jsonify({'success': False, 'message': f'Error processing strip: {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True)