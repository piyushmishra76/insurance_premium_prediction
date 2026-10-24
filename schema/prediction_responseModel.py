from pydantic import BaseModel,Field,computed_field,field_validator
from typing import Dict

class PredictionResponse(BaseModel):
    predicted_category: str = Field(..., description="The predicted category of the insurance premium",example="medium")
    confidence: float = Field(..., description="The confidence score of the prediction",example=0.85)
    probabilities: Dict[str, float] = Field(..., description="The probabilities of each class",example={"low": 0.1, "medium": 0.85, "high": 0.05})
    