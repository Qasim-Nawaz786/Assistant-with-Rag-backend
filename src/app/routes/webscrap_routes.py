import os
from fastapi import APIRouter, HTTPException
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore
from bs4 import BeautifulSoup
import pdfkit

router = APIRouter()


@router.get("/")
async def get_data_through_webscrap() -> dict[str, str]:
    """Scrapes data from a URL, cleans it, creates a PDF, and uploads it to OpenAI (placeholder).

    Raises:
        HTTPException: If data fetching from the URL fails.
    """
    url: str = "https://duet.edu.pk/"

    try:
        response = await scrap_webtest(url)
        if response:
            cleaned_data = clean_data(response)
            pdf_filepath = text_to_pdf(cleaned_data)

            if pdf_filepath:
                return {"success": f"PDF created successfully! File path: {pdf_filepath}"}
            else:
                return {"error": "Failed to create PDF"}
        else:
            raise HTTPException(status_code=404, detail="Failed to fetch data from the URL")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Updated function with retry logic
async def scrap_webtest(url):
    """Fetches and parses content from a URL with retry logic.

    Args:
        url (str): The URL to scrape data from.

    Returns:
        str: The scraped and parsed text content, or None if fetching fails.
    """

    def fetch_url_with_retry(url, max_retries=3, backoff_factor=0.3):
        session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=backoff_factor,
                        status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch URL: {e}")
            return None
        finally:
            session.close()

    content = fetch_url_with_retry(url)
    if content:
        soup = BeautifulSoup(content, "html.parser")
        return soup.get_text()
    else:
        return None


def clean_data(data):
    """Cleans the scraped data by removing whitespace and replacing newlines with spaces.

    Args:
        data (str): The scraped data to clean.

    Returns:
        str: The cleaned data.
    """

    cleaned_data = data.strip()  # Remove leading and trailing whitespace
    cleaned_data = cleaned_data.replace('\n', ' ')  # Replace newline characters with spaces
    return cleaned_data


def text_to_pdf(text):
    """Generates a PDF from the provided text.

    Args:
        text (str): The text content to convert to PDF.

    Returns:
        str: The path to the generated PDF file, or None if creation fails.
    """

    try:
        file_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'data.pdf')
        path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'  # Path to the wkhtmltopdf binary
        pdfkit.from_string(text, file_path, configuration=pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf))
        return file_path
    except Exception as e:
        print(f"Failed to create PDF: {e}")
        return None





# async def upload_to_openai(file_path, client, vector_store_id):
#     """
#     Uploads a file to OpenAI's vector store asynchronously.

#     Args:
#         file_path (str): Path to the file to upload.
#         client (OpenAI): OpenAI client object.
#         vector_store_id (str): ID of the vector store to upload to.

#     Returns:
#         file_batch (object, optional): Object containing upload details from OpenAI
#                                       or None if an error occurs.
#     """

#     if not os.path.exists(file_path):
#         print(f"Error: File not found: {file_path}")
#         return None

#     try:
#         file_path = [file_path]
#         file_stream = [open(path, 'rb') for path in file_path]

#         # Now pass the file_content to the API
#         file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#             vector_store_id=vector_store_id,
#             files=file_stream
#         )

#         print({'file counts: ': file_batch.file_counts})
#         print({'file status: ': file_batch.status})

#         return file_batch

#     except Exception as e:
#         print(f"Upload error: {e}")
#         return None  # Or handle the error differently (e.g., retry)