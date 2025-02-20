import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

def convert_single_file(filename, folder_path):
    if filename.endswith('.doc'):
        new_filename = filename[:-4] + '.docx'
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_filename)
        try:
            os.rename(old_file, new_file)
            return f"Converted: {filename} -> {new_filename}"
        except Exception as e:
            return f"Error converting {filename}: {str(e)}"
    return None

def convert_doc_to_docx(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist")
        return
    
    # Get list of .doc files
    doc_files = [f for f in os.listdir(folder_path) if f.endswith('.doc')]
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        # Create a partial function with folder_path
        convert_func = partial(convert_single_file, folder_path=folder_path)
        # Map the conversion function to all files
        results = executor.map(convert_func, doc_files)
        
        # Print results
        for result in results:
            if result:
                print(result)

# Example usage
if __name__ == "__main__":
    folder_path = r"/Users/shyam/Downloads/foo2"  # Replace with your folder path
    convert_doc_to_docx(folder_path)
