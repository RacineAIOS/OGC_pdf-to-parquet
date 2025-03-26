# pdf_to_img_txt.py

from typing import List, Tuple
import io, fitz, asyncio

from config import ZOOM_FACTOR, CHUNK_SIZE, OUTPUT_FORMAT



async def process_one_page(page) -> Tuple[bytes, str]:
    """
    Extracts both image and text from a PDF page.

    Args:
        page: A PDF page object.

    Returns:
        Tuple of (image_bytes, text_string).
    """

    loop = asyncio.get_running_loop()
    mat = fitz.Matrix(ZOOM_FACTOR, ZOOM_FACTOR)

    def get_image():
        pix = page.get_pixmap(matrix=mat)
        return pix.tobytes(OUTPUT_FORMAT)

    def get_text():
        return page.get_text()
    
    img_bytes, text = await asyncio.gather(
        loop.run_in_executor(None, get_image),
        loop.run_in_executor(None, get_text)
    )
    return img_bytes, text



async def pdf_to_image_and_text(pdf_bytes: bytes) -> Tuple[List[bytes], List[str]]:
    """
    Converts a PDF document to lists of images and texts.

    Args:
        pdf_bytes: Binary PDF data.
        
    Returns:
        Tuple of (list_of_image_bytes, list_of_text_strings).
    """

    pdf_stream = io.BytesIO(pdf_bytes)
    
    with fitz.open(stream=pdf_stream, filetype="pdf") as doc:
        pages = list(doc)  # Convert to list to avoid iterator issues
        
        chunk_size = CHUNK_SIZE
        results = []
        for i in range(0, len(pages), chunk_size):
            chunk = pages[i:i + chunk_size]
            chunk_results = await asyncio.gather(*[process_one_page(page) for page in chunk])
            results.extend(chunk_results)
        
        images, texts = zip(*results) if results else ([], [])
    
    pdf_stream.close()
    return list(images), list(texts)