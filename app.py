from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field,field_validator
from typing import List, Optional,Literal,Annotated
from schema.user_input import InputData
from model.predict import predict_output,MODEL_VERSION,model
from schema.prediction_responseModel import PredictionResponse
from config.logger import logger
import pickle
import pandas as pd



app=FastAPI()


@app.get("/")
def home():
    logger.info("Home endpoint accessed")
    return {"message":"Welcome to the Insurance Premium Prediction API. Use the /predict endpoint to get predictions."}

#health check endpoint to tell the aws load balancer that the app is running fine or our api is working fine
#machine readable endpoint for health check
''' we are making this for the aws load balancer to check if the app is running fine or not. The load balancer will hit this endpoint and if it gets a 200 response, it will consider the app as healthy. If it gets a 500 response,
 it will consider the app as unhealthy and will not send traffic to it.
 basically helping us to deploy the app on aws and make it scalable. The load balancer will automatically scale the app based on the traffic and will also automatically replace any unhealthy instances of the app with healthy ones.'''
@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return {
        "status": "Ok",
        "Version": MODEL_VERSION,
        "model_loaded": model is not None
    }

from fastapi import HTTPException

@app.post("/predict", response_model=PredictionResponse)
def predict_premium(data: InputData):
    #of pydantic model type InputData
    #since the model expects a dataframe as input, we will convert the pydantic model to a dataframe
    # because the model was trained on a dataframe with specific columns, we will create a dataframe with the same columns
    #making the prediction endpoint

    logger.info("Prediction request received")

    user_input = {
        "bmi": data.bmi,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupation": data.occupation,
    }

    try:
        prediction = predict_output(user_input)

        logger.info("Prediction completed successfully")

        # Return fields matching PredictionResponse
        return prediction

    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check application logs."
        ) from e
