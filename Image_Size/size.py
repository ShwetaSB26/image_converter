from flask import Flask, render_template, request, send_file, make_response
import base64
from PIL import Image
import io

app = Flask(__name__, static_url_path='/static')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form['option']
        image = request.files['image'].read()
        img = Image.open(io.BytesIO(image))

        size_kb = float(request.form['size_kb']) 

        if option == 'increase':
            scale_factor = 1.5
        else:
            scale_factor = 0.5

        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        resized_img = img.resize((new_width, new_height))

        buffered = io.BytesIO()
        resized_img.save(buffered, format="PNG")
        resized_img_size_kb = len(buffered.getvalue()) / 1024.0

        while resized_img_size_kb > size_kb:
            scale_factor -= 0.05 
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            resized_img = img.resize((new_width, new_height))

            buffered = io.BytesIO()
            resized_img.save(buffered, format="PNG")
            resized_img_size_kb = len(buffered.getvalue()) / 1024.0

        resized_img_data = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return render_template('Size.html', resized_img_data=resized_img_data, option=option)

    return render_template('Size.html')


@app.route('/download/<option>', methods=['POST'])
def download(option):
    image_data = request.form.get('image', None)

    if not image_data:
        return "Image data not provided."

    image_bytes = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(image_bytes))

    if option == 'increase':
        scale_factor = 1.5
    else:
        scale_factor = 0.5

    new_width = int(img.width * scale_factor)
    new_height = int(img.height * scale_factor)
    resized_img = img.resize((new_width, new_height))

    buffered = io.BytesIO()
    resized_img.save(buffered, format="PNG")
    buffered.seek(0)

    response = make_response(buffered.getvalue())
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Disposition'] = f'attachment; filename=resized_image.png'
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
