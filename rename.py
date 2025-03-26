import os



def rename_files(folder_path):
    files = [f for f in os.listdir(folder_path) 
    if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith('.') and not f == '.DS_Store']
    
    files.sort()
    counter = 0
    
    for file in files:
        old_path = os.path.join(folder_path, file)
        new_name = f"train-{counter:05d}-of-00049.parquet"
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {file} -> {new_name}")
        counter += 1



folder_path = "out_train"
rename_files(folder_path)