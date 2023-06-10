from git import Repo
from pathlib import Path
import os
import subprocess

def get_changed_files(repo: Repo) -> [str]:
    files = [os.path.abspath(item.a_path) for item in repo.index.diff(None)]
    return list(filter(lambda x: Path(x).suffix == '.swift', files))

if __name__ == '__main__':
    repo = Repo(os.getcwd(), search_parent_directories=True)
    file_paths = get_changed_files(repo)
    print(file_paths)
    for file in file_paths:
        swiftlint_output = subprocess.check_output(['swiftlint', 'autocorrect', '--path', file])
        print(swiftlint_output)
