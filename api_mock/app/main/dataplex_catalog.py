from flask import Blueprint, jsonify, request
from app.services.dataplex_catalog import (
    check_resouce_is_valid,
    initiate_resource_transfer,
    mark_as_transferred_after_timeout,
    get_resource_data,
)
from app.services.delay import run_coroutine

# Define a Blueprint for dataplex catalog routes
routes = Blueprint("dataplex_catalog_routes", __name__, url_prefix="/dataplex_catalog")


@routes.route("/<string:resource_type>/<string:resource_id>", methods=["POST"])
def transfer_entry_group(resource_type, resource_id):
    """
    Initiate resource transfer.
    """
    resource_data = request.get_json(force=True)

    try:
        check_resouce_is_valid(resource_type, resource_id, resource_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        initiate_resource_transfer(resource_id, resource_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    run_coroutine(mark_as_transferred_after_timeout(resource_id))

    return jsonify({"error": False}), 202


@routes.route("/<string:resource_type>/<string:resource_id>", methods=["GET"])
def fetch_entry_group(resource_type, resource_id):
    """
    Fetch resource data.
    """
    try:
        return jsonify(get_resource_data(resource_type, resource_id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404
