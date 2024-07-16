import os
from PyPDF2 import PdfReader
from docx import Document

def read_text_file(filepath):
  """
  Reads text content from a file.

  Args:
      filepath (str): The path to the file.

  Returns:
      str: The text content of the file, or None if an error occurs.
  """
  try:
    with open(filepath, 'r', encoding='utf-8') as file:
      text = file.read()
      return text
  except FileNotFoundError:
    print(f"Error: File not found: {filepath}")
    return None
  except Exception as e:
    print(f"Error reading file: {filepath} - {e}")
    return None

def read_pdf_file(filepath):
  """
  Reads text content from a PDF file using PyPDF2 library.

  Args:
      filepath (str): The path to the PDF file.

  Returns:
      str: The extracted text from the PDF, or None if an error occurs.
  """
  try:


    with open(filepath, 'rb') as file:
      reader = PdfReader(file)
      text = ""
      for page in reader.pages:
        text += page.extract_text()
      return text
  except ImportError:
    print("Error: PyPDF2 library not installed. Please install using 'pip install PyPDF2'")
    return None
  except Exception as e:
    print(f"Error reading PDF file: {filepath} - {e}")
    return None

def read_word_file(filepath):
  """
  Reads text content from a Word document using docx library.

  Args:
      filepath (str): The path to the Word document (.docx file).

  Returns:
      str: The extracted text from the Word document, or None if an error occurs.
  """
  try:
    print("insidde")


    document = Document(filepath)
    text = ""
    for paragraph in document.paragraphs:
      text += paragraph.text
    return text
  except ImportError:
    print("Error: docx library not installed. Please install using 'pip install docx'")
    return None
  except Exception as e:
    print(f"Error reading Word document: {filepath} - {e}")
    return None

def read_text(filepath):
  """
  Reads text content from a file based on its extension.

  Args:
      filepath (str): The path to the file.

  Returns:
      str: The extracted text content of the file, or None if an error occurs.
  """
  extension = os.path.splitext(filepath)[1].lower()
  print(extension)
  
  if extension == '.txt':
    return read_text_file(filepath)
  elif extension == '.pdf':
    return read_pdf_file(filepath)
  elif extension == '.docx':
    return read_word_file(filepath)
  else:
    print(f"Unsupported file format: {filepath}")
    return None