from app import create_app
import openai
import logging

app = create_app()

if __name__ == '__main__':
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG)

    # Set OpenAI API key from the loaded configuration so that OpenAI
    # requests succeed when the server starts.
    openai.api_key = app.config.get('OPENAI_API_KEY')

    app.run(debug=app.config['DEBUG'])

