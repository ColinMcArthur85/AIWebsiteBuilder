from flask import request, jsonify, render_template
import logging
import openai
from .config import Config
from .helpers import extract_background_color, enforce_immutable_rules, generate_button_html
import os
from PIL import Image
import pytesseract 
from werkzeug.utils import secure_filename
from flask_cors import CORS

def init_app(app):
    # Initialize OpenAI client with API key
    openai.api_key = Config.OPENAI_API_KEY

    # Enable CORS
    CORS(app)

    # Configure upload folder and allowed extensions
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Create the upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/')
    def index():
        return render_template('index.html')

    # Endpoint for generating code from the prompt
    @app.route('/generate_code', methods=['POST'])
    def generate_code_route():
        data = request.get_json()
        prompt = data.get('prompt', '')
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
    
        try:
            logging.debug(f"Received prompt: {prompt}")
    
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are an assistant that generates structured HTML code using Bootstrap 3 and Froala. "
                            "Avoid including full HTML boilerplate (e.g., <!DOCTYPE html>, <head>, <body>). "
                            "Focus only on generating sections and components with the proper structure for the page. "
                            "Use inline styles only for all styling, no external CSS. "
                            "Do not include any explanations, comments, or additional text outside of the HTML. "
                            "Ensure that the generated HTML is compatible with Froala editor and renders correctly inside it. "
                            "If a user requests to add an image to a section, use <img src=\"https://picsum.photos/300/300\" alt=\"Random Image\" class=\"img-responsive\"> as the default setting for each image. "
                            "However, if the user requests a specific image or size of image, update the image according to their request. For example if they ask for an image that is 500 x 500 then you should use use <img src=\"https://picsum.photos/500/500\" alt=\"Random Image\" class=\"img-responsive\">"
                            "All generated HTML should strictly adhere to Bootstrap 3's framework and Froala's requirements."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1024,
                temperature=0.0
            )
            logging.debug(f"OpenAI Response: {response}")
    
            generated_code = response.choices[0].message['content']
            generated_code = generated_code.replace("```html", "").replace("```", "")
            logging.debug(f"Generated code: {generated_code}")
    
            section_background_color = extract_background_color(generated_code) or extract_background_color(prompt)
            validated_code = enforce_immutable_rules(generated_code, section_background_color)
            
            # Ensure button background color is different from section background color
            button_background_color = "#007bff"  # Example button background color
            if button_background_color == section_background_color:
                button_background_color = "#00ff00"  # Change to a different color if they are the same
            
            button_html = generate_button_html(
                content="Click Me", 
                button_background_color=button_background_color,  
                border_color="#0056b3",      
                text_color="#ffffff"         
            )
            validated_code = validated_code.replace("</div></div></div></section>", f"{button_html}</div></div></div></section>")
    
            logging.debug(f"Validated code: {validated_code}")
    
            return jsonify({'code': validated_code})
        except Exception as e:
            logging.error(f"Error while generating code: {str(e)}")
            return jsonify({'error': 'An error occurred while generating the code.'}), 500

    # Endpoint for uploading an image and generating HTML
    @app.route('/upload_image', methods=['POST'])
    def upload_image():
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process the image and generate HTML code
            try:
                # Open the image for processing
                img = Image.open(filepath)

                # Step 1: Perform OCR on the image (optional)
                text_from_image = pytesseract.image_to_string(img)

                # Step 2: Use OpenAI to generate HTML based on the image description
                response = openai.Completion.create(
                    engine="gpt-4",
                    prompt=f"Generate HTML code based on this description: {text_from_image}",
                    max_tokens=500
                )
                
                # Extract the generated code
                generated_code = response.choices[0].text.strip()

                # Apply immutable rules by wrapping the generated content in the outer <section>
                validated_code = enforce_immutable_rules(generated_code, None)

                return jsonify({'code': validated_code})
            except Exception as e:
                logging.error(f"Error while processing image: {str(e)}")
                return jsonify({'error': 'An error occurred while processing the image.'}), 500
        else:
            return jsonify({'error': 'Invalid file type'}), 400

    @app.after_request
    def add_headers(response):
        response.cache_control.no_store = True
        response.cache_control.no_cache = True
        response.cache_control.must_revalidate = True
        response.cache_control.max_age = 0
        response.expires = 0
        return response