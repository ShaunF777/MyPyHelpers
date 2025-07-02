import os

def remove_prefix(directory, text, file_ext):
    for filename in os.listdir(directory):
        if filename.endswith(file_ext) and filename.startswith(text): # Check if the filename starts with the specified text
            new_filename = filename[len(text):] # Remove the prefix text
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename)) # Rename the file
            print(f"Renamed: {filename} -> {new_filename}") 

def remove_postfix(directory, text, file_ext):
    for filename in os.listdir(directory):
        if filename.endswith(file_ext) and filename[:-len(file_ext)].endswith(text): # Check if the filename ends with the specified text before the file extension
            new_filename = filename[:-len(text + file_ext)] + file_ext # Remove the postfix text
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename)) # Rename the file
            print(f"Renamed: {filename} -> {new_filename}")

def add_prefix(directory, text, file_ext):
    for filename in os.listdir(directory): # Check each file in the directory
        if filename.endswith(file_ext): # Check if the file has the specified extension
            new_filename = text + filename # Add the prefix text to the filename
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename)) # Rename the file
            print(f"Renamed: {filename} -> {new_filename}")

def add_postfix(directory, text, file_ext):
    for filename in os.listdir(directory): # Check each file in the directory
        if filename.endswith(file_ext): # Check if the file has the specified extension
            name, ext = os.path.splitext(filename) # Split the filename into name and extension
            if ext == file_ext: # Ensure the extension matches the specified one
                new_filename = name + text + ext # Add the postfix text before the file extension
                os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename)) # Rename the file
                print(f"Renamed: {filename} -> {new_filename}")

if __name__ == "__main__":
    directory = input("Enter the directory path: ").strip() # Get the directory path from the user
    action = input("Do you want to 'add' or 'remove' text from filenames? ").strip().lower() # Ask user for action
    position = input("Should it be a 'prefix' or 'postfix'? ").strip().lower() # Ask user for position of text
    text = input("Enter the text to add/remove: ").strip() # Get the text to add or remove from filenames
    file_ext = input("Enter the file extension to match (e.g. .txt, .jpg): ").strip().lower() # Get the file extension from the user

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

