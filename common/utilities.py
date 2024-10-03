import csv
from typing import IO, List


def parse_csv_file_to_json(csv_file: IO) -> List[dict]:
    """
    Parse the content of an uploaded CSV file and convert it to a JSON structure.

    Argumentss:
        csv_file (IO): a file-like object representing the uploaded CSV file

    Returns:
        str: a JSON string representing the parsed CSV content, where each row is an object
        with key-value pairs based on the header and row values

    Raises:
        ValueError: if the CSV content is invalid or can't be parsed
    """
    try:
        if hasattr(csv_file, 'readable') and csv_file.readable():
            content = csv_file.read()

            if isinstance(content, bytes):
                content = content.decode('utf-8')

            reader = csv.DictReader(content.splitlines())
            return [dict(row) for row in reader]

    except Exception as error:
        raise ValueError(f'Error parsing CSV file: {str(error)}')
