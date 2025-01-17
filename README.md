# Test assignment

## Problem description

API Data Transfer and Analysis
Objective:
Build a simple version of the data migration between one source to another
Tasks:
1. Create mock APIs (using Flask or FastAPI) for:

    a. Data Catalog: Provides metadata about resources (e.g., Entry Groups, Tag Templates).

    b. Dataplex Catalog: Accepts resources and provides feedback on transfer success.

2. Implement the following features:

    a. Fetch a list of resources (e.g., Entry Groups, Tag Templates) from the mock Data Catalog API.

    b. Perform a pre-transfer analysis by listing all resources and identifying duplicates or missing dependencies.

    c. Transfer the resources to the mock Dataplex API, logging progress and handling errors.

    d. Add a dry-run option to simulate the transfer without actually migrating resources.
    
3. Document your code and include a short README on how to run the program.

### Sample data
```
[
    {
        "id": "entry_group_1",
        "type": "EntryGroup",
        "dependencies": ["tag_template_1"]
    },
    {
        "id": "entry_group_2",
        "type": "EntryGroup",
        "dependencies": []
    },
    {
        "id": "tag_template_1",
        "type": "TagTemplate",
        "dependencies": []
    },
    {
        "id": "tag_template_2",
        "type": "TagTemplate",
        "dependencies": ["entry_group_3"]
    }
]
```

## Assumptions taken

Before starting the implementation, I've had a quick look at process of Data Catalog -> Dataplex Catalog migration in GCP (with REST API).
It consists of stages:
1. Mark resources as read-only in Data Catalog
2. Send a PATCH request to Data Catalog endpoints of resources to be transferred
3. After some delay, resources will appear in Dataplex Catalog and their status in Dataplex will include a transfered to dataplex flag.

Since the process in GCP can seemingly be done using DataCatalog API endpoints only, but according to problem description we need to mock 2 apis and manage dependencies between resources following assumptions were taken:
- Data Catalog API mock is not paginated (original includes next page tokens)
- Resource ID is globally unique, e.g. EntryGroup cannot have the same ID as TagTemplate (to be able to identify the needed resource when mentioned in `dependencies`)
- Transfering the data is more reliant on client and not internal Data Catalog <-> Dataplex Catalog connections. 
- In order to transfer the metadata resources, a POST request needs to be submitted to Dataplex Catalog API. It will act asyncronously, responding with 202 Accepted HTTP status code if validation is passed. It does not allow POST request for a resource that was already posted once. It does not allow POST request if it doesn't have all the required dependencies already transferred.
- Resource will be available in Dataplex Catalog API straight away 
- After a short delay, the state of `transfer_finished` flag will become true.

## How to run this project:

### Clone the repo:

```
git clone 
```
### Change directory:
```
cd test_assignment 
```

### Create the virtual environment in project and activate:

```
python3 -m venv venv
source ./venv/bin/activate
```

### Install project requirements:

```
pip install -r requirements.txt
```

## CLI for Data Transfer

This command-line interface (CLI) allows you to simulate data transfer operations with flexible options for controlling the execution behavior.

Usage:
```
transfer.py [-h] [-d] [-v] [-i]
```

Options:
```
- -h, --help: Show this help message and exit.
- -d, --dry-run: Perform a dry run of the operation without making any actual changes.
- -v, --verbose: Enable verbose output for detailed logging in console. 
- -i, --ignore-validation-errors: Skip validation errors and continue with the operation.
```

The app always writes log into `data_catalog_transfer.log`

### Example of successful execution output in verbose mode

```
$ python transfer.py -i -v 
HTTP Request: GET http://127.0.0.1:5000/data_catalog/EntryGroup "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/data_catalog/TagTemplate "HTTP/1.1 200 OK"
Missing dependencies: {'tag_template_2', 'entry_group_3'}
Valid resources acceptable for transfer: {'entry_group_1', 'entry_group_2', 'tag_template_1'}
Validation for some of the resources has failed.
Starting layered transfer
Transferring layer 1 ...
HTTP Request: POST http://127.0.0.1:5000/dataplex_catalog/TagTemplate/tag_template_1 "HTTP/1.1 202 ACCEPTED"
HTTP Request: POST http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_2 "HTTP/1.1 202 ACCEPTED"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_2 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/TagTemplate/tag_template_1 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_2 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/TagTemplate/tag_template_1 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_2 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/TagTemplate/tag_template_1 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_2 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/TagTemplate/tag_template_1 "HTTP/1.1 200 OK"
Layer data successfully transfered! 🐒
Transferring layer 2 ...
HTTP Request: POST http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_1 "HTTP/1.1 202 ACCEPTED"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_1 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_1 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_1 "HTTP/1.1 200 OK"
HTTP Request: GET http://127.0.0.1:5000/dataplex_catalog/EntryGroup/entry_group_1 "HTTP/1.1 200 OK"
Layer data successfully transfered! 🐒
```