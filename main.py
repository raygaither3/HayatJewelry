from website import create_app
from flask_migrate import upgrade
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        upgrade()
    app.run(debug=True)