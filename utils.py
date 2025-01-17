import sys
import logging
from argparse import ArgumentParser


def parse_cli_args():
    """
    Parses command-line arguments for the data transfer CLI.
    """
    parser = ArgumentParser(description="CLI for Data Transfer")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Perform a dry run of the operation without making any actual changes.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for detailed logging.")
    parser.add_argument("-i", "--ignore-validation-errors", action="store_true", help="Skip validation errors and continue with the operation.")
    return parser.parse_args()


def get_logger(use_stdout):
    """
    Configures and returns a logger with different handlers for output.
    """
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s : %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("data_catalog_transfer.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    logger.addHandler(stderr_handler)

    if use_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        logger.addHandler(stdout_handler)

    return logger
