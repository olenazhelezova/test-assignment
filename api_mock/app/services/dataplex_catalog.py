from asyncio import sleep

storage = {}


def check_resouce_is_valid(type: str, id: str, data: dict) -> None:  # for transfer
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
    storage[id] = data
    storage[id]["transfer_finished"] = False


async def mark_as_transferred_after_timeout(id):
    await sleep(10)
    storage[id]["transfer_finished"] = True


def get_resource_data(type: str, id: str) -> dict:
    if id not in storage:
        raise Exception("Not Found.")

    resource = storage[id]

    if resource["type"] != type:
        raise Exception("Not Found.")

    return resource
