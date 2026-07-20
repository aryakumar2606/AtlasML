import os
import shutil
import uuid

def save_uploaded_file(file, upload_folder):
    os.makedirs(upload_folder, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(upload_folder, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path