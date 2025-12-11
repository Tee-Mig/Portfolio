from git import Repo
import os

repo_dir = r'C:\Users\migue\OneDrive\Bureau\ULTIMATE_PORTFOLIO\Portfolio_git\mini-data-lake\my_git'

file_path = r'C:\Users\migue\OneDrive\Bureau\ULTIMATE_PORTFOLIO\Portfolio_git\mini-data-lake\lake\air_pollution.parquet'
if os.path.exists(file_path):
    print(f"File exists: {file_path}")
else:
    print(f"File does NOT exist at: {file_path}")

repo = Repo(repo_dir)

if os.path.exists(file_path):
    repo.index.add([file_path])

    commit_message = 'Add air_pollution.parquet file'
    repo.index.commit(commit_message)

    origin = repo.remotes.origin
    origin.push()
    
    print("File pushed successfully!")
else:
    print(f"Error: The file {file_path} does not exist.")