import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import DiseasePrediction, User
from backend.app.schemas.disease import DiseasePredictionResponse
from backend.app.ml.disease_model import disease_engine
from backend.app.auth.dependencies import get_optional_current_user
from backend.app.config import settings

router = APIRouter(prefix="/api/disease", tags=["Crop Disease Detection"])

@router.post("/predict", response_model=DiseasePredictionResponse)
async def predict_disease(
    file: UploadFile = File(...),
    crop_hint: Optional[str] = Form(None),
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a leaf/plant image to predict disease with symptoms, treatment, and prevention.
    """
    image_bytes = await file.read()
    filename = file.filename or "leaf.jpg"

    # Validate image security, size, and MIME
    err = disease_engine.validate_image_bytes(image_bytes, filename)
    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    # Save image securely with unique filename
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(filename)[1] or ".jpg"
    safe_filename = f"disease_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    # Run computer vision analysis
    prediction = disease_engine.analyze(image_bytes, hint_crop=crop_hint)

    # Store in database
    prediction_record = DiseasePrediction(
        user_id=current_user.id if current_user else None,
        image_path=file_path,
        crop=prediction["crop"],
        disease=prediction["disease"],
        confidence=prediction["confidence"],
        symptoms=prediction["symptoms"],
        treatment=prediction["treatment"],
        prevention=prediction["prevention"]
    )
    db.add(prediction_record)
    db.commit()

    return DiseasePredictionResponse(**prediction)
