"""
WSGI Entry Point - Production deployment
"""
import os
from inventory_app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)