from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.csv_services import read_csv, get_dataset_summary

router = APIRouter()


@router.post(
    "/upload",
    tags=["Dataset"],
    summary="Upload CSV Dataset",
    description="Upload a CSV dataset and generate a complete dataset profile."
)
async def upload_dataset(file: UploadFile = File(...)):

    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed."
        )

    try:
        # Read CSV
        dataframe = read_csv(file.file)

        # Generate dataset summary
        summary = get_dataset_summary(dataframe)

        # Return response
        return {
            "filename": file.filename,
            **summary
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the uploaded CSV."
        )


