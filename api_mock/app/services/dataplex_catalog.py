from asyncio import sleep

storage = {}


def check_resouce_is_valid(type: str, id: str, data: dict) -> None:  # for transfer
    """
    Validates if the resource can be transferred based on the type, id, and dependencies.
    """
    if type not in ["TagTemplate", "EntryGroup"]:
        raise Exception("Type unrecognized.")
    if id in storage:
        raise Exception("Duplicate resource id.")
    if "type" not in data:
        raise Exception("Resource type not specified.")
    if "dependencies" in data:
        for dependency in data["dependencies"]:
            if dependency not in storage:
                raise Exception("Can not satisfy dependencies.")
            if not storage[dependency]["transfer_finished"]:
                raise Exception("Dependency not yet transferred.")


def initiate_resource_transfer(id: str, data: dict) -> None:
    """
    Initiates the transfer of a resource by adding it to the storage with a 'transfer_finished' flag set to False.
    """
    storage[id] = data
    storage[id]["transfer_finished"] = False


async def mark_as_transferred_after_timeout(id):
    """
    Marks a resource as transferred after waiting for 10 seconds. This simulates a delayed transfer process.
    """
    await sleep(10)
    storage[id]["transfer_finished"] = True


def get_resource_data(type: str, id: str) -> dict:
    """
    Retrieves the data for a specific resource identified by its type and id.
    """
    if id not in storage:
        raise Exception("Not Found.")

    resource = storage[id]

    if resource["type"] != type:
        raise Exception("Not Found.")

    return resource
