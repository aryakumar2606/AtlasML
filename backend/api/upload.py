from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.csv_services import read_csv, get_dataset_summary
from backend.services.file_service import save_uploaded_file
from backend.config import (UPLOAD_FOLDER,ALLOWED_EXTENSIONS,MAX_FILE_SIZE_MB)


router = APIRouter()


@router.post(
    "/upload",
    tags=["Dataset"],
    summary="Upload CSV Dataset",
    description="Upload a CSV dataset and generate a complete dataset profile."
)
async def upload_dataset(file: UploadFile = File(...)):

    # Validate file type
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
      raise HTTPException(
        status_code=400,
        detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed."
     )
         
    contents = await file.read()

    if len(contents) == 0:
       raise HTTPException(
        status_code=400,
        detail="Uploaded file is empty."
    )

    await file.seek(0)
    
    file_size_mb = len(contents) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
      raise HTTPException(
        status_code=400,
        detail=f"Maximum allowed file size is {MAX_FILE_SIZE_MB} MB."
    )

    try:
        # Read CSV
        saved_path = save_uploaded_file(file, UPLOAD_FOLDER)
        dataframe = read_csv(saved_path)

        # Generate dataset summary
        summary = get_dataset_summary(dataframe)

        # Return response
        return {
         "original_filename": file.filename,
         "saved_path": saved_path,
         **summary
       }
    except Exception as e:
      raise HTTPException(
        status_code=500,
        detail=f"Unable to process the uploaded CSV. Error: {str(e)}"
    )


