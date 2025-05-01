import os
import shutil

def organize_files(directory, method="type"):
    try:
        directory = os.path.expanduser(directory) # Handle ~ for home directory
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist.")
            return

        for filename in os.listdir(directory):
            src = os.path.join(directory, filename)
            if os.path.isfile(src):
                if method == "type":
                    ext = os.path.splitext(filename)[1].lower()
                    if ext:
                        folder = os.path.join(directory, ext[1:]) # e.g., 'pdf' folder
                    else:
                        folder = os.path.join(directory, 'no_extension')
                        os.makedirs(folder, exist_ok=True)
                        dst = os.path.join(folder, filename)
                        shutil.move(src, dst)
                        print(f"Moved {filename} to {folder}")
                        print("File organization complete.")
    except Exception as e:
        print(f"Error organizing files: {e}")