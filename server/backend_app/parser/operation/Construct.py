import base64
import io
import json
import sqlite3
import uuid
from altair import X2Datum
import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
import category_encoders as ce
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
import matplotlib.pyplot as plt
import seaborn as sns
from sympy import plot
import dill
from tpot import TPOTRegressor, TPOTClassifier

def select_algorithm(operation_type, algorithm_name='AUTO_ML', **kwargs):
    if algorithm_name == 'AUTO_ML':
        if operation_type.upper() == "PREDICTION":
            tpot_regressor = TPOTRegressor(generations=5, population_size=20, verbosity=2)
            return tpot_regressor
        elif operation_type.upper() == "CLASSIFICATION":
            tpot_classifier = TPOTClassifier(generations=5, population_size=20, verbosity=2)
            return tpot_classifier
    else:
        prediction_algorithms = {
            "LR": LinearRegression(),
            "RF": RandomForestRegressor(),
            "SVR": SVR(),
            "KNN": KNeighborsRegressor(),
            "GB": GradientBoostingRegressor(),
        }
        classification_algorithms = {
            "LOG": LogisticRegression(),
            "RFC": RandomForestClassifier(),
            "SVC": SVC(),
            "KNN": KNeighborsClassifier(),
            "GBC": GradientBoostingClassifier(),
        }
        clustering_algorithms = {
            "KMEANS": KMeans(n_clusters=int(kwargs.get('n_clusters', 3))),
            "AGGLOMERATIVE": AgglomerativeClustering(),
            "DBSCAN": DBSCAN(),
        }
        algorithms = {
            "PREDICTION": prediction_algorithms,
            "CLASSIFICATION": classification_algorithms,
            "CLUSTERING": clustering_algorithms
        }
        selected_algorithms = algorithms.get(operation_type.upper(), prediction_algorithms)
        return selected_algorithms.get(algorithm_name.upper())

def construct(command):
    '''  
    CONSTRUCT LR_retail AS SUPERVISED FOR PREDICTION on TARGET MonthlySales FEATURES Age,Price,StockLevel ALGORITHM LR  TEST ON .3 FROM retail;
    '''
    command_parts = [part for part in command.split(" ") if part.strip()]
    operation_types = ["PREDICTION", "CLASSIFICATION", "CLUSTERING"]
    operation_type = command_parts[command_parts.index("FOR")+ 1]
    dataset_train_name = command_parts[command_parts.index("FROM") + 1].split(';')[0]
    model_name=command_parts[command_parts.index("CONSTRUCT") + 1]
    if "ALGORITHM" in command_parts:
        algorithm_name = command_parts[command_parts.index("ALGORITHM")+ 1] 
    else :
        algorithm_name='AUTO_ML'
    features=command_parts[command_parts.index("FEATURES") + 1].split(',')    
    print(command_parts)
    connection_string = os.getenv("POSTGES_URL")
    query = f'SELECT * FROM "{dataset_train_name}"'
    conn = create_engine(connection_string)
    # url = os.path.join(os.path.dirname(__file__), f"../../data/files/{dataset_train_name}.db")
    # conn = sqlite3.connect(url)
    # query = f"SELECT * FROM {dataset_train_name}"
    df = pd.read_sql_query(query, conn)
    X = df[features]
    y = None
    global model,accuracy,label_name,response
    response={'text':'','graph':'','table':''}
    model=None 
    accuracy = None
    if operation_type !=  "CLUSTERING":
            target = command_parts[command_parts.index("TARGET") + 1]
            y = df[target]
    if y is not None and operation_type !="CLUSTERING":
        test_s= float(command_parts[command_parts.index("TEST") + 2]) if "TEST" in command_parts  else 20
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_s/100, random_state=42)
        model = select_algorithm(operation_type, algorithm_name.upper())
        if not algorithm_name:   algorithm_name='AUTO_ML'
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        try:
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
            with open(url, 'wb') as file:
                pickle.dump(model, file)
                response['text']+=f"Model {model_name} is created as name {model_name}.pkl. "
        except:
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.dill")
            with open(url, 'wb') as file:
                dill.dump(model, file)
                response['text']+=f"Model {model_name} is created {model_name}.dill. "
        if "TPOT" in str(model): 
            print(model,"======")
            print(model.fitted_pipeline_.steps,"*********")
            response['text']+=f"{json.dumps( str(model.fitted_pipeline_.steps[0]))}. "
        if operation_type.upper() == "CLASSIFICATION" :
            accuracy = accuracy_score(y_test, y_pred)*100
            response['text']+=f"Accuracy of model {model_name} is {accuracy} ."
            print(response['text'])
        elif operation_type.upper() == "PREDICTION":
            accuracy = r2_score(y_test, y_pred)*100
            response['text']+=f"R-squared value of model {model_name} is {accuracy} ."
            print("R^2 Score:", accuracy)
  
    else:
        n_cluster =command_parts[command_parts.index("CLUSTER")+2] if "CLUSTER"  in command_parts else 3
        if algorithm_name == 'default':
            algorithm_name = KMeans
        model = select_algorithm(operation_type, algorithm_name.upper(),n_clusters=n_cluster)
        X = pd.DataFrame(X.select_dtypes(include=[np.number]))
        model.fit(X)
        try:
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
            with open(url, 'wb') as file:
                pickle.dump(model, file)
                response['text']=f"Model {model_name} is created as name {model_name}.pkl. "
        except:
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.dill")
            with open(url, 'wb') as file:
                dill.dump(model, file)
            response['text']=f"Model {model_name} is created {model_name}.dill. "

    return response



'''
CONSTRUCT KMeans_Boston AS SUPERVISED FEATURES age,rad  ALGORITHM KMeans OF CLUSTERING WITH CLASS 5 FROM Boston;

CONSTRUCT LR_Boston AS SUPERVISED FOR medv FEATURES age,rad ALGORITHM LR OF PREDICTION TEST ON .3 FROM Boston;

CONSTRUCT KNN_Combined AS SUPERVISED FOR Class FEATURES CAtomCount,TotalAtomCount,HAtomCount ALGORITHM KNN OF CLASSIFICATION TEST ON .3 FROM combined;

'''