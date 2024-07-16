from reader.file_reader import read_text
from retriever.resume_parser import construct_hailey_response_data


if __name__ == "__main__":
    # Example usage
    filepath = r"Uday_Kumar-K (1).pdf"
    print(filepath)  # Replace with the actual file path
    text = read_text(filepath)

    if text:
            json_data = construct_hailey_response_data(resume=text)
            print(json_data)
    else:
        print("Failed to read text from the file.")



