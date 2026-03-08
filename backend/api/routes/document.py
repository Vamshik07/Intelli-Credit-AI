from pathlib import Path
import shutil

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.models.mongo_client import store


router = APIRouter(tags=["document"])
UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/api/document/upload")
async def upload_document(
    company_id: str = Form(...),
    document_type: str = Form("auto"),
    files: list[UploadFile] = File(default_factory=list),
    file: UploadFile | None = File(default=None),
):
    upload_list = list(files)
    if file is not None:
        upload_list.append(file)

    if not upload_list:
        raise HTTPException(status_code=400, detail="No files were provided")

    target_dir = UPLOAD_DIR / company_id
    target_dir.mkdir(parents=True, exist_ok=True)
    uploaded: list[dict[str, str]] = []

    for current_file in upload_list:
        target_path = target_dir / current_file.filename
        with open(target_path, "wb") as f:
            shutil.copyfileobj(current_file.file, f)

        document_id = store.add_document(company_id, str(target_path), document_type)
        uploaded.append(
            {
                "document_id": document_id,
                "file_path": str(target_path),
                "document_type": document_type,
                "filename": current_file.filename,
            }
        )

    first = uploaded[0]
    return {
        "uploaded": uploaded,
        "uploaded_count": len(uploaded),
        # Backward-compatible fields used by older UI code.
        "document_id": first["document_id"],
        "file_path": first["file_path"],
        "document_type": first["document_type"],
    }
