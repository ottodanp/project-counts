import os
from sys import argv
from typing import List, Dict, Any, Union

from tabulate import tabulate


def crawl_file_path(start_path: str, exclusions: List[str]):
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if all([exclusion not in root for exclusion in exclusions]):
                yield os.path.join(root, file)


def count_file(file_path: str) -> Dict[str, int]:
    with open(file_path, 'r') as file:
        try:
            lines = file.read().splitlines()
        except UnicodeDecodeError:
            print(f"Error reading file: {file_path}")
            return {
                "lines": 0,
                "lines_code": 0
            }
        lines_code = [line for line in lines if line.strip() != '']
        return {
            "lines": len(lines),
            "lines_code": len(lines_code)
        }


def count_project(project_directory: str, exclusions: List[str]) -> Dict[
    str, Union[int, Dict[str, Union[int, Dict[str, int]]]]]:
    counts = {
        "total_lines": 0,
        "total_lines_code": 0,
        "total_files": 0,
        "total_directories": 0,
        "file_types": {}
    }

    for file_path in crawl_file_path(project_directory, exclusions):
        counts["total_files"] += 1
        file_counts = count_file(file_path)
        extension = file_path.split('.')[-1]
        if extension not in counts["file_types"]:
            counts["file_types"][extension] = {
                "lines": 0,
                "lines_code": 0,
                "files": 0
            }

        counts["total_lines"] += file_counts["lines"]
        counts["total_lines_code"] += file_counts["lines_code"]

        counts["file_types"][extension]["lines"] += file_counts["lines"]
        counts["file_types"][extension]["lines_code"] += file_counts["lines_code"]
        counts["file_types"][extension]["files"] += 1

    return counts


def display(counts: dict):
    data = sorted(counts["file_types"].items(), key=lambda x: x[1]["lines_code"], reverse=True)
    print(tabulate([
        ["Total", counts["total_files"], counts["total_lines"], counts["total_lines_code"], "100%"],
        *[[key, value["files"], value["lines"], value["lines_code"],
           f'{round(value["lines_code"] / counts["total_lines_code"] * 100, 3)}%'] for key, value in data]
    ], headers=["File Type", "Files", "Lines", "Lines of Code", "Percentage of Code"]))


if __name__ == '__main__':
    if len(argv) != 2:
        print("Usage: python3 main.py <project_directory>")
        exit(1)

    directory = argv[1]

    display(count_project(project_directory=directory,
                          exclusions=['node_modules', 'build', 'dist', 'venv', '.git', ".idea", ".vscode",
                                      "__pycache__"]))
