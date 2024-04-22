import base64
import io
import json
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

def select_algorithm(operation_type, algorithm_name='AUTO_ML', **kwargs):
    # print(algorithm_name)
    if algorithm_name == 'AUTO_ML':
        if operation_type.upper() == "PREDICTION":
            tpot_regressor = TPOTRegressor(generations=2, population_size=20, verbosity=2)
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
        # print(selected_algorithms)
        algo= selected_algorithms.get(algorithm_name.upper())
        # print(algo)
        return algo

def display_results(operation_type, y_test=None, y_pred=None, model=None, features=None, df=None):
    if operation_type.upper() == "PREDICTION":
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred,alpha=0.6)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k-o', lw=4)
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
    url = os.path.join(os.path.dirname(__file__), f"../graph/graph_.png")
    plt.savefig(url, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close() 
    return plot_data

def generate(command):  
    '''GENERATE DISPLAY OF PREDICTION MonthlySales ALGORITHM GB WITH ACCURACY 100 LABEL ProductID FEATURES Age,Price,StockLevel FROM retail OVER retailTestData'''
    command_parts = [part for part in command.split(" ") if part.strip()]
    try:
        operation_types = ["PREDICTION", "CLASSIFICATION", "CLUSTERING"]
        operation_type = next((word for word in operation_types if word in command), "PREDICTION") ###
        dataset_train_name = command_parts[command_parts.index("FROM") + 1].split(';')[0]
        features=command_parts[command_parts.index("FEATURES") + 1].split(',')
        algorithm_name = command_parts[command_parts.index("ALGORITHM")+ 1] if "ALGORITHM" in command_parts else None  ####
    except:
        pass
    # print(command_parts)
    # df = pd.read_csv(dataset_train_name)
    url = os.path.join(os.path.dirname(__file__), f"../../data/files/{dataset_train_name}.db")
    conn = sqlite3.connect(url)
    query = f"SELECT * FROM {dataset_train_name}"
    df = pd.read_sql_query(query, conn)
    X = df[features]
    y = None
    global model,accuracy,label_name,response
    response={'text':'','graph':'','table':''}
    model=None 
    accuracy = None
    if operation_type !=  "CLUSTERING":
            if operation_type.upper() == "CLASSIFICATION":
                target = command_parts[command_parts.index("CLASSIFICATION") + 1]
            elif operation_type.upper() == "PREDICTION":
                target = command_parts[command_parts.index("PREDICTION") + 1]
            y = df[target]
    if "OVER" in command:
        url = os.path.join(os.path.dirname(__file__), f"../../data/{command_parts[command_parts.index('OVER') + 1]}.csv")
        df = pd.read_csv(url)
        if "USING MODEL" in command.upper():
            model_name=command_parts[command_parts.index("MODEL") + 1] if "MODEL" in command_parts  else "iris_knn"
            url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
            try:
                with open(url, 'rb') as file:
                    model= pickle.load(file)
            except:
                response["text"]=f"Model: [{model_name}] Not found"
                return response
        else:
            test_s= float(command_parts[command_parts.index("TEST") + 2]) if "TEST" in command_parts  else 20
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_s/100, random_state=42)
            # print(operation_type,algorithm_name)
            model = select_algorithm(operation_type, algorithm_name.upper())
            # print(model)
            model.fit(X_train, y_train)
        
        X=df[features]
        y_test=df[target]
        y_pred = model.predict(df[features])
        print(y_pred)
        output_file = command_parts[command_parts.index("OVER") + 1] + "_predictions.csv"
        if y is not None:
            df["prediction"] = y_pred
        if "LABEL" in command_parts:
            label=command_parts[command_parts.index("LABEL") + 1]
            df.insert(0, label, range(1,len(df)+1))
        response['table']=df.to_dict(orient="records")
        url = os.path.join(os.path.dirname(__file__), f"../table/table_.csv")
        df.to_csv(url, index=False)
        if operation_type.upper() == "CLASSIFICATION" and y_test is not None:
            # ex_ac=command_parts[command_parts.index("ACCURACY") + 1] if "ACCURACY" in command_parts else 0
            accuracy = accuracy_score(y_test, y_pred)*100
            response['text']+=f"Accuracy is {accuracy}"
        elif operation_type.upper() == "PREDICTION" and y_test is not None:
            # ex_ac=command_parts[command_parts.index("ACCURACY") + 1] if "ACCURACY" in command_parts else 0
            accuracy = r2_score(y_test, y_pred)*100
            response['text']+=f"r2_score is  {accuracy}"
        print(f"Predictions saved to {output_file}")
    elif "USING MODEL" in command.upper() and y is not None:
        '''GENERATE DISPLAY OF CLASSIFICATION Species USING MODEL iris_knn  WITH ACCURACY 10 LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;'''
        model_name=command_parts[command_parts.index("MODEL") + 1] if "MODEL" in command_parts  else "iris_knn"
        test_s= float(command_parts[command_parts.index("TEST") + 2]) if "TEST" in command_parts  else 20
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_s/100, random_state=42)
        url = os.path.join(os.path.dirname(__file__), f"../model/{model_name}.pkl")
        try:
            with open(url, 'rb') as file:
                model= pickle.load(file)
        except:
            response["text"]=f"Model [{model_name}] Not found"
            return response
        y_pred = model.predict(X_test)
        y_pred_df = pd.DataFrame(y_pred, index=y_test.index, columns=["Predicted"])
        # print(X_test,X_test.shape)
        # print(y_pred,y_pred.shape)
        df_combined = pd.concat([X_test,y_test,y_pred_df], axis=1)
        # print(df_combined)
        if "LABEL" in command_parts:
            label=command_parts[command_parts.index("LABEL") + 1]
            df_combined.insert(0, label, range(1,len(df_combined)+1))
        df_combined=pd.DataFrame(df_combined)
        response['table']= df_combined.to_dict(orient="records")
        url = os.path.join(os.path.dirname(__file__), f"../table/table_.csv")
        df_combined.to_csv(url, index=False)
        ex_ac=command_parts[command_parts.index("ACCURACY") + 1] if "ACCURACY" in command_parts else 0
        if operation_type.upper() == "CLASSIFICATION" and y_test is not None:
            accuracy = accuracy_score(y_test, y_pred)*100
            if accuracy < float(ex_ac):
                response['text']=f"accuracy is less than {accuracy}"
                return response
            response['text']=f"accuracy is {accuracy}"
            print("Accuracy:", accuracy)
        elif operation_type.upper() == "PREDICTION" and y_test is not None:
            accuracy = r2_score(y_test, y_pred)*100
            print("R2 Score:", accuracy)
            if accuracy < float(ex_ac):
                response['text']=f"r2_score is less than {accuracy}"
                return response
            response['text']=f"r2_score is {accuracy}"
            print(response['text'],ex_ac)   
            print("r2_score:", accuracy)
        # print(response)
    elif y is not None and operation_type !="CLUSTERING":
        test_s= float(command_parts[command_parts.index("TEST") + 2]) if "TEST" in command_parts  else 20
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_s/100, random_state=42)
        if not algorithm_name:   algorithm_name='AUTO_ML'
        model = select_algorithm(operation_type, algorithm_name.upper())
        # print(model)
        model.fit(X_train, y_train)
        if "TPOT" in str(model): 
            # print(model,"======")
            # print(model.fitted_pipeline_.steps,"*********")
            response['text']+=f"{json.dumps( str(model.fitted_pipeline_.steps[0]))}\n"
            # print(response["text"])
        y_pred = model.predict(X_test)
        y_pred_df = pd.DataFrame(y_pred, index=y_test.index, columns=["Predicted"])
        df_combined = pd.concat([X_test,y_test, y_pred_df], axis=1)
        if "LABEL" in command_parts:
            label=command_parts[command_parts.index("LABEL") + 1]
            df_combined.insert(0, label, range(1,len(df_combined)+1))
        response['table']=df_combined.to_dict(orient="records")
        url = os.path.join(os.path.dirname(__file__), f"../table/table_.csv")
        df_combined.to_csv(url, index=False)
        if operation_type.upper() == "CLASSIFICATION" and y_test is not None:
            ex_ac=command_parts[command_parts.index("ACCURACY") + 1] if "ACCURACY" in command_parts else 0
            accuracy = accuracy_score(y_test, y_pred)*100
            response['text']+=f"Accuracy is {accuracy}"
            # print(response['text'])
            if accuracy < float(ex_ac):
                response['text']=f"Accuracy is less than {accuracy}. "
                if algorithm_name!="AUTO_ML":
                    response['text']+=f" Trying another model "
                    model = select_algorithm(operation_type, "AUTO_ML")
                    model.fit(X_train, y_train)
                    response['text']+=f"{json.dumps( str(model.fitted_pipeline_.steps[0]))} \n"
                    y_pred = model.predict(X_test)
                    y_pred_df = pd.DataFrame(y_pred, index=y_test.index, columns=["Predicted"])
                    df_combined = pd.concat([X_test,y_test, y_pred_df], axis=1)
                    response['table']=df_combined.to_dict(orient="records")
        elif operation_type.upper() == "PREDICTION" and y_test is not None:
            ex_ac=command_parts[command_parts.index("ACCURACY") + 1] if "ACCURACY" in command_parts else 0
            accuracy = r2_score(y_test, y_pred)*100
            response['text']+=f"R-squared is  {accuracy}"
            print("R-squared Score:", accuracy)
            if accuracy < float(ex_ac):
                response['text']=f"R-squared_score is less than  {accuracy}"
                if algorithm_name!="AUTO_ML":
                    response['text']+=f"Trying another model"
                    model = select_algorithm(operation_type, "AUTO_ML")
                    model.fit(X_train, y_train)
                    response['text']+=f"{json.dumps( str(model.fitted_pipeline_.steps[0]))}\n"
                    y_pred = model.predict(X_test)
                    y_pred_df = pd.DataFrame(y_pred, index=y_test.index, columns=["Predicted"])
                    df_combined = pd.concat([X_test,y_test, y_pred_df], axis=1)
                    response['table']=df_combined.to_dict(orient="records")
                # return response
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
        model = select_algorithm(operation_type, algorithm_name.upper(),n_clusters=n_cluster)
        X = pd.DataFrame(X.select_dtypes(include=[np.number]))
        model.fit(X)
        y_pred = model.labels_
        df = df[features]
        # y_pred_df = pd.DataFrame(y_pred, index=y_test.index, columns=["Predicted"])
        df['Class'] = y_pred.tolist()
        df=pd.DataFrame(df)
        response['table']=df.to_dict(orient='records')
        url = os.path.join(os.path.dirname(__file__), f"../table/table_.csv")
        df.to_csv(url, index=False)
    # print(command_parts)

    if "DISPLAY" in command_parts:
        print(features,len(features))
        response['graph']=display_results(operation_type, y_test if y is not None else None, y_pred, model, features, df)
        # print(operation_type, y_test if y is not None else None, y_pred, model, features, df)
        if (response['graph']):
            print("graph generatd")
    # print(response)
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