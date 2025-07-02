import os

def remove_prefix(directory, text, file_ext):
    for filename in os.listdir(directory):
        if filename.endswith(file_ext) and filename.startswith(text):
            new_filename = filename[len(text):]
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            print(f"Renamed: {filename} -> {new_filename}")

def remove_postfix(directory, text, file_ext):
    for filename in os.listdir(directory):
        if filename.endswith(file_ext) and filename[:-len(file_ext)].endswith(text):
            new_filename = filename[:-len(text + file_ext)] + file_ext
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            print(f"Renamed: {filename} -> {new_filename}")

def add_prefix(directory, text, file_ext):
    for filename in os.listdir(directory):
        if filename.endswith(file_ext):
            new_filename = text + filename
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            print(f"Renamed: {filename} -> {new_filename}")

def add_postfix(directory, text, file_ext):
    for filename in os.listdir(directory):
        if filename.endswith(file_ext):
            name, ext = os.path.splitext(filename)
            if ext == file_ext:
                new_filename = name + text + ext
                os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
                print(f"Renamed: {filename} -> {new_filename}")

if __name__ == "__main__":
    directory = input("Enter the directory path: ").strip()
    action = input("Do you want to 'add' or 'remove' text from filenames? ").strip().lower()
    position = input("Should it be a 'prefix' or 'postfix'? ").strip().lower()
    text = input("Enter the text to add/remove: ").strip()
    file_ext = input("Enter the file extension to match (e.g. .txt, .jpg): ").strip().lower()

    if not file_ext.startswith('.'):
        file_ext = '.' + file_ext  # Ensure dot is present

    if action == "remove":
        if position == "prefix":
            remove_prefix(directory, text, file_ext)
        elif position == "postfix":
            remove_postfix(directory, text, file_ext)
        else:
            print("Invalid position choice. Use 'prefix' or 'postfix'.")
    elif action == "add":
        if position == "prefix":
            add_prefix(directory, text, file_ext)
        elif position == "postfix":
            add_postfix(directory, text, file_ext)
        else:
            print("Invalid position choice. Use 'prefix' or 'postfix'.")
    else:
        print("Invalid action choice. Use 'add' or 'remove'.")

