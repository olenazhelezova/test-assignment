from flask import Blueprint
from app.services.data_catalog import get_resource_metadata

# Define a Blueprint for data catalog routes
routes = Blueprint("data_catalog_routes", __name__, url_prefix="/data_catalog")


@routes.route("/<string:resource_type>", methods=["GET"])
def get_resource(resource_type):
    """
    Fetch metadata for the given resource type.
    """
    return get_resource_metadata(resource_type), 200
