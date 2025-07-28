# query_img_to_parquet.py

from datasets import Dataset, Features, Value, Image
import uuid
import os
import gc



def save_data_to_parquet(data_list, output_path):
    """
    Saves query-image pairs to a parquet file.

    Args:
        data_list: List of dictionaries with query and image data.
        output_path: Output file path.
        
    Returns:
        The saved Dataset object.
    """
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        features = Features({
            "id": Value("string"),
            "query": Value("string"),
            "image": Image(),
            "language": Value("string")
        })
        
        processed_data = []
        for item in data_list:
            item_id = str(uuid.uuid4()) + str(uuid.uuid4())[:14]
            
            processed_item = {
                "id": item_id,
                "query": item.get("query", ""),
                "image": item.get("image", {}),
                "language": item.get("language", "")
            }
            processed_data.append(processed_item)
        
        dataset = Dataset.from_list(processed_data, features=features)
        dataset.to_parquet(output_path)
        
        # Force flush to disk on Windows
        gc.collect()
        
        print(f"Successfully saved: {output_path}")
        return dataset
        
    except Exception as e:
        print(f"ERROR saving parquet to {output_path}: {str(e)}")
        raise