import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.openai.openai_connectivity import OPENAI_API_KEY


def load_documents(folder_path):
    """Loads PDF documents from a specified folder.

    Args:
        folder_path (str): Path to the folder containing PDF files.

    Returns:
        list: A list of loaded documents or None if no PDFs found.

    Raises:
        FileNotFoundError: If the folder path doesn't exist.
    """

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The directory '{folder_path}' does not exist.")

    # List all PDF files in the folder
    pdf_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in the directory.")
        return None

    docs = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(pdf_path)
        try:
            loaded_docs = loader.load()
            if loaded_docs:
                docs.extend(loaded_docs)
                print(f"Loaded {len(loaded_docs)} documents from {pdf_path}")
        except Exception as e:
            print(f"Error loading document {pdf_path}: {e}")
    
    return docs if docs else None


def split_documents(documents):
    """Splits documents into chunks and generates embeddings.

    Args:
        documents (list): List of loaded documents.

    Returns:
        Chroma: A Chroma vectorstore containing document embeddings.
    """

    textsplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunk_docs = textsplitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(openai_api_type=OPENAI_API_KEY)
    persist_directory = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_store")

    try:
        database = Chroma.from_documents(
            documents=chunk_docs,
            embedding=embeddings,
            persist_directory=persist_directory
        )
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise  # Re-raise the exception for further handling

    print({"collection count": database._collection.count()})
    return database


# Example usage
folder_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets")  # Navigate up two directories
try:
    docs = load_documents(folder_path)
    if docs:
        num_docs = len(docs)
        print({"Number of docs: ": num_docs})
        print(docs[1].metadata)
        database = split_documents(docs)
        print(database)
except (FileNotFoundError, Exception) as e:
    print(f"An error occurred: {e}")
else:
    print("Processing completed successfully.")
