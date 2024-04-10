from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from model_utils import load_model, prediction
import pandas as pd

app = FastAPI()

class FeaturesInput(BaseModel):
    State: str 
    Bank: str 
    BankState: str
    Term: int
    NoEmp: int
    NewExist: str
    FranchiseCode: str 
    UrbanRural: str
    RevLineCr: str 
    LowDoc: str 
    GrAppv: int
    SBA_Appv: int 
    Zip2: str 
    NAICS2: str 
    RealEstate: str 

class PredictionOutput(BaseModel):
    category: int

model = load_model()

@app.post('/predict')
def prediction_model(feature_input: FeaturesInput):
    # Création d'un dictionnaire à partir des valeurs de l'objet FeaturesInput
    feature_input_dict = {
        'budget': feature_input.budget,
        'franchise': feature_input.franchise,
        'genre': feature_input.genre,
        'remake': feature_input.remake,
        'studio': feature_input.studio,
        'is_compositeur': feature_input.is_compositeur,
        'annee': feature_input.annee,
        'origine': feature_input.origine
    }

    # Création du DataFrame à partir du dictionnaire
    feature_input_df = pd.DataFrame([feature_input_dict])

    # Conversion des types des colonnes
    feature_input_df = feature_input_df.astype({
        'budget': 'int64',
        'franchise': 'category',
        'genre': 'category',
        'remake': 'category',
        'studio': 'object',
        'is_compositeur': 'category',
        'annee': 'category',
        'origine': 'category'
    })

    # Appel à la fonction de prédiction avec le DataFrame
    pred = prediction(model, feature_input_df)
    
    # Retour de la prédiction sous forme de réponse JSON
    return PredictionOutput(category=pred)