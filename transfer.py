
import sys
import asyncio
from client.data_catalog import DataCatalogClient
from client.dataplex_catalog import DataplexCatalogClient
from utils import parse_cli_args, get_logger
from exceptions import AppException

API_BASE_URL = "http://127.0.0.1:5000/"

# Parse CLI arguments
args = parse_cli_args()

# Initialize loggers
logger = get_logger(args.verbose)


def find_duplicates(resources: list[dict]) -> set:
    collector = set()
    duplicates = set()
    for resource in resources:
        if resource["id"] in collector:
            duplicates.add(resource["id"])
        collector.add(resource["id"])
    return duplicates


def deduplicate_resources(resources: list[dict], duplicates: set) -> None:
    if len(duplicates) > 0:
        logger.info("Resources before deduplication: ", resources)
        resources[:] = [r for r in resources if r["id"] not in duplicates]
        logger.info("Resources before deduplication: ", resources)


def validate_dependencies(resources: list[dict]):
    collector, ref_lookup = {}, {}

    # Collect all resources into an id-indexed dictionary collector
    # Count outbound dependencies and all dependant resources for each resource
    for resource in resources:
        collector[resource["id"]] = resource
        if resource["id"] not in ref_lookup:
            ref_lookup[resource["id"]] = {"outbound": 0, "backrefs": []}
        if "dependencies" not in resource:
            continue
        for dep in resource["dependencies"]:
            if dep not in ref_lookup:
                ref_lookup[dep] = {"outbound": 0, "backrefs": []}
            ref_lookup[dep]["backrefs"].append(resource["id"])
            ref_lookup[resource["id"]]["outbound"] += 1

    # Missing dependency list includes both resources that do not exist, and resources that exist but depend on non-existing ones
    missing_dependencies, layer, visited = set(), set(), set()
    
    # Build a first layer, checking for resource existence 
    for id in ref_lookup:
        if ref_lookup[id]["outbound"] == 0:
            layer.add(id)
        if id not in collector:
            missing_dependencies.add(id)

    # To avoid rewalking the tree when doing actual transfer, we save the layers
    layer_log = []

    # Process dependencies layer by layer
    while len(layer) > 0:
        next_layer = set()
        for resource_id in layer:
            # Update all the dependents
            for backref in ref_lookup[resource_id]["backrefs"]:
                # Propagate the reason of unability to transfer, if the dependency does not exist in resources
                if resource_id in missing_dependencies:
                    missing_dependencies.add(backref)
                # Decrease outbound reference counter for dependent
                ref_lookup[backref]["outbound"] -= 1

                # If current resource was the last unresolved dependency, the dependent can now be added the next layer
                if ref_lookup[backref]["outbound"] == 0:
                    next_layer.add(backref)
            # Only add the existing dependencies to visited
            if resource_id in collector:
                visited.add(resource_id)
        # Adding all the resource data to layer log, not only id
        layer_log.append(
            list(
                map(
                    lambda id: collector[id],
                    visited.intersection(layer) - missing_dependencies,
                )
            )
        )
        layer = next_layer

    # Visited does not include missing
    if len(visited) < len(resources):
        logger.info("Detected cyclical dependencies.")

    # Since existing resource may be in missing_dependencies because of it's dependency of non-existing one
    valid = visited - missing_dependencies

    # If there are resources left unprocessed, they still have outbound ref counter > 0
    cycle_elements = set(collector) - visited - missing_dependencies

    if len(missing_dependencies): 
        logger.info("Missing dependencies: " + str(missing_dependencies))

    if len(cycle_elements):
        logger.info("Elements forming cycles: " + str(cycle_elements))

    if len(valid):
        logger.info("Valid resources acceptable for transfer: " + str(valid))

    return layer_log


async def transfer_resource(resource):
    client = DataplexCatalogClient(API_BASE_URL)
    if resource["type"] == "EntryGroup":
        await client.initiate_entrygroup_transfer(resource)
        return await client.poll_for_entrygroup_transfer_completion(resource["id"])
    if resource["type"] == "TagTemplate":
        # just in case some other resource type was able to crawl here we will have explicit type check
        await client.initiate_tag_template_transfer(resource)
        return await client.poll_for_tag_template_transfer_completion(resource["id"])


async def transfer_layered_resources(layers):
    logger.info("Starting layered transfer")
    try:
        for i in range(len(layers)):
            logger.info(f"Transferring layer {i+1} ...")
            await asyncio.gather(
                *[transfer_resource(resource) for resource in layers[i]]
            )
            logger.info("Layer data successfully transfered! 🐒")
    except AppException as e:
        logger.error(f"Unable to transfer resources in layer: '{str(e)}'. Aborting.")


def main():
    data_catalog_client = DataCatalogClient(API_BASE_URL)

    try:
        entry_groups = data_catalog_client.get_entry_groups()
        tag_templates = data_catalog_client.get_tag_templates()
    except AppException as e:
        logger.critical("Unable to fetch data: " + str(e))
        sys.exit(1)

    resources = entry_groups + tag_templates

    dups = find_duplicates(resources)

    if len(dups) > 0:
        logger.warning(
            "Duplicate resource identifiers found in source data. Resources: "
            + ",".join(dups)
        )
        if not args.ignore_validation_errors:
            sys.exit(1)

    deduplicate_resources(resources, dups)

    layers = validate_dependencies(resources)

    valid_resource_count = sum([len(l) for l in layers])
    if valid_resource_count != len(resources):
        # Some resources validation has failed
        logger.warning("Validation for some of the resources has failed.")
        if not args.ignore_validation_errors:
            sys.exit(1)

    if args.dry_run:
        sys.exit(1)

    asyncio.run(transfer_layered_resources(layers))


if __name__ == "__main__":
    main()
