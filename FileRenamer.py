import os

def remove_prefix(directory, text):
    for filename in os.listdir(directory):
        if filename.startswith(text):
            new_filename = filename[len(text):]
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            print(f"Renamed: {filename} -> {new_filename}")

def remove_postfix(directory, text):
    for filename in os.listdir(directory):
        if filename.endswith(text):
            new_filename = filename[:-len(text)]
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
            print(f"Renamed: {filename} -> {new_filename}")

def add_prefix(directory, text):
    for filename in os.listdir(directory):
        new_filename = text + filename
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
        print(f"Renamed: {filename} -> {new_filename}")

def add_postfix(directory, text):
    for filename in os.listdir(directory):
        name, ext = os.path.splitext(filename)
        new_filename = name + text + ext
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
        print(f"Renamed: {filename} -> {new_filename}")

if __name__ == "__main__":
    directory = input("Enter the directory path: ").strip()
    action = input("Do you want to 'add' or 'remove' text from filenames? ").strip().lower()
    position = input("Should it be a 'prefix' or 'postfix'? ").strip().lower()
    text = input("Enter the text to add/remove: ").strip()

    if action == "remove":
        if position == "prefix":
            remove_prefix(directory, text)
        elif position == "postfix":
            remove_postfix(directory, text)
        else:
            print("Invalid position choice. Use 'prefix' or 'postfix'.")
    elif action == "add":
        if position == "prefix":
            add_prefix(directory, text)
        elif position == "postfix":
            add_postfix(directory, text)
        else:
            print("Invalid position choice. Use 'prefix' or 'postfix'.")
    else:
        print("Invalid action choice. Use 'add' or 'remove'.")
