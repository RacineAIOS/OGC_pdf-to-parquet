# img_txt_to_query.py

import asyncio

from custom_types import TechnicalQueries, ParallelInstructor
from config import PARALLEL_INSTANCES, GEMINI_MODEL, MAX_RETRIES, RETRY_BACKOFF
from rate_limiter import RateLimiter
from prompts import SYSTEM_PROMPT



parallel_client = ParallelInstructor(num_instances=PARALLEL_INSTANCES)



async def generate_technical_queries(
        image_b64: str,
        rate_limiter: RateLimiter
    ) -> TechnicalQueries:
    """
    Generates technical queries from an image using the Gemini API.

    Args:
        image_b64: Base64-encoded image string.
        rate_limiter: RateLimiter instance to control API request rates.

    Returns:
        TechnicalQueries object containing four types of generated queries.
    """

    for attempt in range(MAX_RETRIES + 1):
        try:
            async with rate_limiter:
                client = await parallel_client.get_client()
                response = await client.chat.completions.create(
                    model=GEMINI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "The page to analyze:"},
                                {"type": "image_url", "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }}
                            ]
                        }
                    ],
                    response_model=TechnicalQueries
                )
                if response is None:
                    raise Exception("Received null response from API")
                await rate_limiter.record_success()
                return TechnicalQueries(
                    main_query=response.main_query.strip(),
                    secondary_query=response.secondary_query.strip(),
                    visual_query=response.visual_query.strip(),
                    multimodal_query=response.multimodal_query.strip(),
                    language=response.language.strip().lower()
                )
        except Exception as e:
            if attempt < MAX_RETRIES:
                wait_time = RETRY_BACKOFF ** attempt
                print(f"Retry attempt {attempt + 1}/{MAX_RETRIES} for Gemini API. Waiting {wait_time}s... Error: {str(e)}")
                await asyncio.sleep(wait_time)
            else:
                print(f"Max retries ({MAX_RETRIES}) exceeded for Gemini API call: {str(e)}")
                raise