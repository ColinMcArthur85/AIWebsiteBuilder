from app import create_app
import openai
import logging

app = create_app()

if __name__ == '__main__':
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG)

    # Set OpenAI API key

    app.run(debug=app.config['DEBUG'])