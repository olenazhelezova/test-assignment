from app.main import create_app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    """
    Run the Flask application if this script is executed directly.
    """
    app.run(threaded=False)
