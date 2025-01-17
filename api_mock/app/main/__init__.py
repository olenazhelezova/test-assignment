from flask import Flask
from app.main.data_catalog import routes as data_catalog_routes
from app.main.dataplex_catalog import routes as dataplex_catalog_routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(data_catalog_routes)
    app.register_blueprint(dataplex_catalog_routes)
    return app
