import os
from dotenv import load_dotenv

# Load .env variables before anything else
load_dotenv()

from website import create_app
from flask_migrate import upgrade

app = create_app()

# Optional: auto-upgrade the database in production
if os.getenv('FLASK_ENV') == 'production':
    with app.app_context():
        upgrade()

if __name__ == "__main__":
    # Run with debug mode based on environment
    app.run(debug=(os.getenv('FLASK_ENV') != 'production'))