# main.py

import os, asyncio, base64, time
from pathlib import Path

from config import REQUESTS_PER_SECOND, PARQUET_SIZE, INPUT_FOLDER, OUTPUT_FOLDER, FILE_NAMES
from img_txt_to_query import generate_technical_queries
from query_img_to_parquet import save_data_to_parquet
from pdf_to_img_txt import pdf_to_image_and_text
from rate_limiter import RateLimiter



async def process_one_pdf_file_streaming(pdf_path: str, rate_limiter: RateLimiter, data_queue: asyncio.Queue) -> None:
    """Processes a PDF file and streams individual entries to queue."""
    print(f"Processing PDF: {pdf_path}")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    images_bytes, texts = await pdf_to_image_and_text(pdf_bytes)
    
    for i, (img_bytes, text) in enumerate(zip(images_bytes, texts)):
        try:
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            queries = await generate_technical_queries(img_b64, rate_limiter)
            detected_language = queries.language
            
            entries = [
                {"query": queries.main_query, "image": {"bytes": img_bytes}, "language": detected_language},
                {"query": queries.secondary_query, "image": {"bytes": img_bytes}, "language": detected_language},
                {"query": queries.visual_query, "image": {"bytes": img_bytes}, "language": detected_language},
                {"query": queries.multimodal_query, "image": {"bytes": img_bytes}, "language": detected_language}
            ]
            
            for entry in entries:
                await data_queue.put(entry)
            
            print(f"  Processed page {i+1} of {len(images_bytes)}")
        except Exception as e:
            print(f"  Error processing page {i+1}: {str(e)}")
            continue



async def pdf_batch_to_parquet_part(input_folder: str, output_folder: str, batch_size: int) -> None:
    """Processes multiple PDFs and saves resulting datasets to parquet files."""
    os.makedirs(output_folder, exist_ok=True)
    rate_limiter = RateLimiter(requests_per_second=REQUESTS_PER_SECOND)
    
    pdf_files = [str(f) for f in Path(input_folder).glob("*.pdf")]
    if not pdf_files:
        print(f"No PDF files found in {input_folder}")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    
    data_queue = asyncio.Queue()  # No maxsize limit
    processing_done = False
    concurrency_limit = min(8, os.cpu_count() * 2)

    async def process_pdf(pdf_file: str):
        async with semaphore:
            try:
                await process_one_pdf_file_streaming(pdf_file, rate_limiter, data_queue)
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")

    async def parquet_writer():
        nonlocal processing_done
        buffer = []
        file_counter = 0
        
        while True:
            try:
                # No timeout - get entries as they come
                if not data_queue.empty():
                    entry = await data_queue.get()
                    buffer.append(entry)
                    
                    if len(buffer) >= batch_size:
                        output_path = os.path.join(output_folder, f"{FILE_NAMES}-{file_counter:05d}-of-n.parquet")
                        save_data_to_parquet(buffer[:batch_size], output_path)
                        print(f"Saved batch {file_counter} ({batch_size} entries)")
                        file_counter += 1
                        buffer = buffer[batch_size:]
                elif processing_done:
                    break
                else:
                    await asyncio.sleep(0.1)  # Short sleep when queue empty
                    
            except Exception as e:
                print(f"Parquet writer error: {str(e)}")
                continue
        
        # Handle remaining buffer
        if buffer:
            output_path = os.path.join(output_folder, f"{FILE_NAMES}-{file_counter:05d}-of-n.parquet")
            save_data_to_parquet(buffer, output_path)
            print(f"Saved final batch with {len(buffer)} entries")

    semaphore = asyncio.Semaphore(concurrency_limit)
    
    writer_task = asyncio.create_task(parquet_writer())
    
    processing_tasks = [
        asyncio.create_task(process_pdf(pdf_file))
        for pdf_file in pdf_files
    ]

    try:
        await asyncio.gather(*processing_tasks)
    finally:
        processing_done = True
        await writer_task



if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(pdf_batch_to_parquet_part(INPUT_FOLDER, OUTPUT_FOLDER, PARQUET_SIZE))
    elapsed = time.time() - start_time
    print(f"\nProcessing completed in {elapsed:.2f} seconds")