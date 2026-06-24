import io
import httpx
from fastapi import HTTPException, status
from pypdf import PdfReader
from bs4 import BeautifulSoup

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from TXT or PDF file bytes."""
    lower_filename = filename.lower()
    if lower_filename.endswith(".pdf"):
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            extracted_text = "\n".join(text_parts).strip()
            if not extracted_text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from the PDF file. It might be empty or scanned images."
                )
            return extracted_text
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF file: {str(e)}"
            )
    elif lower_filename.endswith(".txt") or lower_filename.endswith(".md"):
        try:
            return file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to decode text file: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only PDF and TXT/MD files are supported."
        )

def extract_text_from_url(url: str) -> str:
    """Scrape and extract clean text from a URL."""
    try:
        # Standard user-agent to avoid simple scraping blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=15.0)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch URL. Server returned status code {response.status_code}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request to URL failed: {str(e)}"
        )

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unwanted tag elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
            
        # Extract text and clean up whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = "\n".join(chunk for chunk in chunks if chunk)
        
        if not cleaned_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scraped web page is empty or has no readable text content."
            )
            
        return cleaned_text.strip()
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse web page content: {str(e)}"
        )
