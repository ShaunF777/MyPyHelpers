import os

def remove_prefix_from_files(directory, prefix):
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            new_filename = filename[len(prefix):]
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            print(f'Renamed: {filename} -> {new_filename}')

if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    prefix = input("Enter the prefix to remove: ")
    remove_prefix_from_files(directory, prefix) 