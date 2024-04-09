import base64
import io
import sqlite3
import uuid
from altair import X2Datum
import pandas as pd
import numpy as np
import os
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

def select_algorithm(operation_type, algorithm_name='default', **kwargs):
    print(algorithm_name)
    if algorithm_name == 'default':
        if operation_type.upper() == "PREDICTION":
            return TPOTRegressor(generations=5, population_size=20, verbosity=2)
        elif operation_type.upper() == "CLASSIFICATION":
            return TPOTClassifier(generations=5, population_size=20, verbosity=2)
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
        CONSTRUCT ModelName AS SUPERVISED  ALGORITHM KMeans OF CLUSTERING WITH CLASS 5 FROM Boston;
        CONSTRUCT ModelName AS SUPERVISED FOR medv FEATURES age,rad ALGORITHM LR OF PREDICTION TEST ON .3 FROM Boston;
    '''

    command_parts = command.split()
    operation_types = ["PREDICTION", "CLASSIFICATION", "CLUSTERING"]
    operation_type = command_parts[command_parts.index("OF")+ 1]
    dataset_train_name = command_parts[command_parts.index("FROM") + 1].split(';')[0]
    model_name=command_parts[command_parts.index("CONSTRUCT") + 1]
    if "ALGORITHM" in command_parts:
        algorithm_name = command_parts[command_parts.index("ALGORITHM")+ 1] 
    else :
        algorithm_name='default'
    features=command_parts[command_parts.index("FEATURES") + 1].split(',')    
    print(command_parts)
    # df = pd.read_csv(dataset_train_name)
    url = os.path.join(os.path.dirname(__file__), f"../../data/files/{dataset_train_name}.db")
    print(url)
    conn = sqlite3.connect(url)
    query = f"SELECT * FROM {dataset_train_name}"
    df = pd.read_sql_query(query, conn)
    X = df[features]
    y = None
    global model,accuracy,label_name,response
    response={}
    model=None 
    accuracy = None
    if operation_type !=  "CLUSTERING":
            target = command_parts[command_parts.index("FOR") + 1]
            y = df[target]
    if y is not None and operation_type !="CLUSTERING":
        test_s= int(command_parts.index("TEST") + 2) if "TEST" in command_parts  else 0.2
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_s, random_state=42)
        model = select_algorithm(operation_type, algorithm_name)
        print(model,operation_type,algorithm_name)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        try:
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
            with open(url, 'wb') as file:
                pickle.dump(model, file)
                response['text']=f"Model {model_name} is created as name {model_name}.pkl"
        except:
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.dill")
            with open(url, 'wb') as file:
                dill.dump(model, file)
            response['text']=f"Model {model_name} is created {model_name}.dill"
        if operation_type.upper() == "CLASSIFICATION" :
            accuracy = accuracy_score(y_test, y_pred)*100
            response['text']=f"Model {model_name} is created.Accuracy is {accuracy}"
            print(response['text'])
        elif operation_type.upper() == "PREDICTION":
            accuracy = r2_score(y_test, y_pred)*100
            response['text']=f"Model {model_name} is created.r2_score is  {accuracy}"
            print("R^2 Score:", accuracy)
  
    else:
        n_cluster =command_parts[command_parts.index("CLUSTER")+2] if "CLUSTER"  in command_parts else 3
        if algorithm_name == 'default':
            algorithm_name = KMeans
        model = select_algorithm(operation_type, algorithm_name,n_clusters=n_cluster)
        X = pd.DataFrame(X.select_dtypes(include=[np.number]))
        model.fit(X)
        try:
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
            with open(url, 'wb') as file:
                pickle.dump(model, file)
                response['text']=f"Model {model_name} is created as name {model_name}.pkl"
        except:
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.dill")
            with open(url, 'wb') as file:
                dill.dump(model, file)
            response['text']=f"Model {model_name} is created {model_name}.dill"

        
    return response



'''
CONSTRUCT KMeans_Boston AS SUPERVISED FEATURES age,rad  ALGORITHM KMeans OF CLUSTERING WITH CLASS 5 FROM Boston;

CONSTRUCT LR_Boston AS SUPERVISED FOR medv FEATURES age,rad ALGORITHM LR OF PREDICTION TEST ON .3 FROM Boston;

CONSTRUCT KNN_Combined AS SUPERVISED FOR Class FEATURES CAtomCount,TotalAtomCount,HAtomCount ALGORITHM KNN OF CLASSIFICATION TEST ON .3 FROM combined;

'''