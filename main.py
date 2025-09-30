"""
Main Entry Point - Development server
"""
from inventory_app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
