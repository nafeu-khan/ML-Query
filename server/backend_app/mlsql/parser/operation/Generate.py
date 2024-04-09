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
        algo= selected_algorithms.get(algorithm_name.upper())
        print(algo)
        return algo

def display_results(operation_type, y_test=None, y_pred=None, model=None, features=None, df=None):
    if operation_type.upper() == "PREDICTION":
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.6)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=4)
        plt.xlabel('Measured')
        plt.ylabel('Predicted')
        plt.title('Actual vs Predicted Values')
    elif operation_type.upper() == "CLASSIFICATION":
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
    elif operation_type.upper() == "CLUSTERING":
        if len(features) >= 2:
            print("iN----------------------------")
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=pd.DataFrame(df), x=features[0], y=features[1], hue=f'Class', palette='viridis')
            plt.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], s=200, c='red', label='Centroids')
            plt.title('Clustering Results')
            # plt.title(f'Clustering Results (Features: {", ".join(features)})')
            plt.legend(title="Cluster")
                    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close() 
    return plot_data

def generate(command):
    '''GENERATE DISPLAY OF PREDICTION MonthlySales ALGORITHM GB WITH ACCURACY 100 LABEL ProductID FEATURES Age,Price,StockLevel FROM retail OVER retailTestData'''
    command_parts = command.split(" ")
    try:
        operation_types = ["PREDICTION", "CLASSIFICATION", "CLUSTERING"]
        operation_type = next((word for word in operation_types if word in command), "PREDICTION") ###
        dataset_train_name = command_parts[command_parts.index("FROM") + 1].split(';')[0]
        features=command_parts[command_parts.index("FEATURES") + 1].split(',')
        algorithm_name = command_parts[command_parts.index("ALGORITHM")+ 1] if "ALGORITHM" in command_parts else None  ####
    except:
        pass
    print(command_parts)
    # df = pd.read_csv(dataset_train_name)
    url = os.path.join(os.path.dirname(__file__), f"../../data/files/{dataset_train_name}.db")
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
            if operation_type.upper() == "CLASSIFICATION":
                target = command_parts[command_parts.index("CLASSIFICATION") + 1]
            elif operation_type.upper() == "PREDICTION":
                target = command_parts[command_parts.index("PREDICTION") + 1]
            y = df[target]
    if "OVER" in command:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        url = os.path.join(os.path.dirname(__file__), f"../../data/{command_parts[command_parts.index("OVER") + 1]}.csv")
        df = pd.read_csv(url)
        if "USING MODEL" in command.upper():
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
            with open(url, 'rb') as file:
                model= pickle.load(file)
        else:
            model = select_algorithm(operation_type, algorithm_name)
            model.fit(X_train, y_train)
        
        X=df[features]
        y_test=df[target]
        y_pred = model.predict(df[features])
        output_file = command_parts[command_parts.index("OVER") + 1] + "_predictions.csv"
        if y is not None:
            df["prediction"] = y_pred
        # df.to_csv(output_file, index=False)
        print(df)
        response["table"]=df.to_dict(orient="records")
        print(f"Predictions saved to {output_file}")
    elif "USING MODEL" in command.upper() and y is not None:
        '''GENERATE DISPLAY OF CLASSIFICATION Species USING MODEL iris_knn  WITH ACCURACY 10 LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;'''
        model_name=command_parts[command_parts.index("MODEL") + 1] if "MODEL" in command_parts  else "iris_knn"
        print(model_name)
        test_s= int(command_parts.index("TEST") + 2) if "TEST" in command_parts  else 0.2
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_s, random_state=42)
        url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
        with open(url, 'rb') as file:
            model= pickle.load(file)
        y_pred = model.predict(X_test)
        y_pred_df = pd.DataFrame(y_pred, index=y_test.index, columns=["Predicted"])
        df_combined = pd.concat([X,y_test, y_pred_df], axis=1)
        if "LABEL" in command_parts:
            label=command_parts[command_parts.index("LABEL") + 1]
            df_combined.insert(0, label, range(1,len(df_combined)+1))
        response['table']= pd.DataFrame(df_combined).to_dict(orient="records")
        ex_ac=command_parts[command_parts.index("ACCURACY") + 1] if "ACCURACY" in command_parts else 0
        if operation_type.upper() == "CLASSIFICATION" and y_test is not None:
            accuracy = accuracy_score(y_test, y_pred)*100
            if accuracy < float(ex_ac):
                response['text']=f"accuracy is less than {accuracy}"
                return response
            response['text']=f"accuracy is {accuracy}"
            print("Accuracy:", accuracy)
        elif operation_type.upper() == "PREDICTION" and y_test is not None:
            accuracy = r2_score(y_test, y_pred)
            print("R2 Score:", accuracy)
            if accuracy < float(ex_ac):
                response['text']=f"r2_score is less than {accuracy}"
                return response
            response['text']=f"r2_score is {accuracy}"
            print(response['text'],ex_ac)   
            print("r2_score:", accuracy)
        # print(response)
    elif y is not None and operation_type !="CLUSTERING":
        test_s= int(command_parts.index("TEST") + 2) if "TEST" in command_parts  else 0.2
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_s, random_state=42)
        model = select_algorithm(operation_type, algorithm_name)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_pred_df = pd.DataFrame(y_pred, index=y_test.index, columns=["Predicted"])
        df_combined = pd.concat([X_test,y_test, y_pred_df], axis=1)
        url = os.path.join(os.path.dirname(__file__), f"../table/table_.csv")
        df_combined.to_csv(url, index=False)
        if "LABEL" in command_parts:
            label=command_parts[command_parts.index("LABEL") + 1]
            df_combined.insert(0, label, range(1,len(df_combined)+1))
        response['table']=df_combined.to_dict(orient="records")
        if operation_type.upper() == "CLASSIFICATION" and y_test is not None:
            ex_ac=command_parts[command_parts.index("ACCURACY") + 1] if "ACCURACY" in command_parts else 0
            accuracy = accuracy_score(y_test, y_pred)*100
            response['text']=f"Accuracy is {accuracy}"
            print(response['text'])
            if accuracy < float(ex_ac):
                response['text']=f"Accuracy is less than {accuracy}"
                # url = os.path.join(os.path.dirname(__file__), f"../model/{algorithm_name}_{dataset_train_name}.pkl")
                # with open(url, 'wb') as file:
                #     pickle.dump(model, file)
                return response
            
        elif operation_type.upper() == "PREDICTION" and y_test is not None:
            ex_ac=command_parts[command_parts.index("ACCURACY") + 1] if "ACCURACY" in command_parts else 0
            accuracy = r2_score(y_test, y_pred)*100
            response['text']=f"r2_score is  {accuracy}"
            print("R^2 Score:", accuracy)
            if accuracy < float(ex_ac):
                response['text']=f"r2_score is less than  {accuracy}"
                return response
                # url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
            #     with open(url, 'wb') as file:
            #         pickle.dump(model, file)
            #     return response
            # url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
            # with open(url, 'wb') as file:
            #     pickle.dump(model, file)
    else:
        n_cluster =command_parts[command_parts.index("CLUSTER")+2] if "CLUSTER"  in command_parts else 3
        if algorithm_name == 'default':
            algorithm_name = KMeans
        model = select_algorithm(operation_type, algorithm_name,n_clusters=n_cluster)
        X = pd.DataFrame(X.select_dtypes(include=[np.number]))
        model.fit(X)
        y_pred = model.labels_
        df = df[features]
        # y_pred_df = pd.DataFrame(y_pred, index=y_test.index, columns=["Predicted"])
        df['Class'] = y_pred.tolist()
        df=pd.DataFrame(df)
        df=df.to_dict(orient='records')
        response['table']=df
    print(command_parts)

    if "DISPLAY" in command_parts:
        print("graph=======")
        print(features,len(features))
        response['graph']=display_results(operation_type, y_test if y is not None else None, y_pred, model, features, df)
        # print(operation_type, y_test if y is not None else None, y_pred, model, features, df)
        # print(response['graph'])
    print(response)
    return response



'''
GENERATE DISPLAY OF CLUSTERING Species ALGORITHM KMeans WITH ClUSTER OF 3 LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;
GENERATE DISPLAY OF CLASSIFICATION Species ALGORITHM KNN WITH ACCURACY 100 LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;
GENERATE DISPLAY OF PREDICTION Species ALGORITHM KNN WITH ACCURACY 100 LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;

GENERATE DISPLAY OF CLUSTERING medv ALGORITHM KMeans WITH ClUSTER OF 3 LABEL ProductID FEATURES rad,age FROM Boston ;
GENERATE DISPLAY OF CLASSIFICATION medv ALGORITHM KNN WITH ACCURACY 100 LABEL ProductID FEATURES rad,age FROM Boston;
GENERATE DISPLAY OF PREDICTION medv ALGORITHM KNN WITH ACCURACY 10 LABEL ProductID FEATURES rad,age FROM Boston;



GENERATE DISPLAY OF CLUSTERING Epsilon ALGORITHM KMeans FEATURES CAtomCount,TotalAtomCount,HAtomCount FROM combined ;
GENERATE DISPLAY OF PREDICTION Epsilon ALGORITHM LR WITH ACCURACY 30 LABEL serialNo FEATURES CAtomCount,TotalAtomCount,HAtomCount FROM combined ;
GENERATE DISPLAY OF CLASSIFICATION Class ALGORITHM KNN WITH ACCURACY 100 LABEL ProductID FEATURES CAtomCount,TotalAtomCount,HAtomCount FROM combined ;



GENERATE DISPLAY OF PREDICTION MonthlySales ALGORITHM LR WITH ACCURACY 0 LABEL serialNo FEATURES Age,Price,StockLevel FROM retail OVER retailTestData ;
GENERATE DISPLAY OF CLASSIFICATION MonthlySales ALGORITHM KNN WITH ACCURACY 0 LABEL serialNo FEATURES Age,Price,StockLevel FROM retail OVER retailTestData ;
GENERATE DISPLAY OF CLUSTERING MonthlySales ALGORITHM KMeans WITH ACCURACY 0 LABEL serialNo FEATURES Age,Price,StockLevel FROM retail;

'''