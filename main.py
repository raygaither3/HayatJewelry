from website import create_app
from flask_migrate import upgrade
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

# with app.app_context():
#     # Only auto-upgrade database in production (e.g., on Render)
#     if os.getenv('FLASK_ENV') == 'production':
#         upgrade()

if __name__ == "__main__":
    app.run(debug=True)