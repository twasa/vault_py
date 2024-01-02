import os


def recursive_directory_walk(directory: str) -> list:
    if not os.path.isdir(directory):
        return []
    file_paths = list()
    for root, subdirs, files in os.walk(directory):
        if files:
            for file_name in files:
                file_paths.append(f'{root}/{file_name}')
    return file_paths
