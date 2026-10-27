import os
import shutil

def copy_cpp_h_to_txt(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".cpp") or filename.endswith(".h"):
            new_filename = filename + ".txt"
            src = os.path.join(directory, filename)
            dst = os.path.join(directory, new_filename)
            shutil.copy2(src, dst)
            print(f"Copied: {filename} -> {new_filename}")

if __name__ == "__main__":
    directory = input("Enter the directory path: ").strip()
    copy_cpp_h_to_txt(directory)