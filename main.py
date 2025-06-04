from website import create_app

from dotenv import load_dotenv
load_dotenv()  # Load variables from .env before anything else


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)