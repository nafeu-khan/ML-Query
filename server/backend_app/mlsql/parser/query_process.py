import pandas as pd

from .operation.construct import construct

from .operation.Generate import generate

from .operation.cluster import cluster
from ..parser.parser import _parser
import sqlite3
import os
from peewee import *
def query_process(data):
    global type_name, model_table_name, target_var, other_ftr, response,currentDB

    if data.upper().startswith("USE"):
        splitted_data = data.split()
        currentDB = splitted_data[1].split(';')[0]
        response = _parser(f"USE 'data/{currentDB}.db';")
        yield response
    elif data.upper().startswith("CONSTRUCT"):
        '''CONSTRUCT PREDICTION MonthlySales ALGORITHM GB WITH  LABEL ProductID FEATURES Age Price StockLevel FROM retail OVER retailTestData ;
           CONSTRUCT CLASSIFICATION Species ALGORITHM KNN WITH  LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;
            '''
        yield construct(data)
    elif data.upper().startswith("GENERATE"):
        '''GENERATE DISPLAY OF PREDICTION MonthlySales ALGORITHM GB WITH ACCURACY 100 LABEL ProductID FEATURES Age Price StockLevel FROM retail OVER retailTestData ;
           GENERATE DISPLAY OF CLASSIFICATION Species ALGORITHM KNN WITH ACCURACY 100 LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;
            '''
        yield generate(data)
    elif data.upper().startswith("GENERATE") and  len(data.split())<=9:
        '''GENERATE PREDICTION USING MODEL homesnew FROM Boston;            
        TABLE Boston; '''
        try:
            temp=data
            data = data.split()
            # table_name = data[data.index("TABLE") + 1].strip()
            currentDB = data[data.index("FROM") + 1].strip()
            if ("MODEL") in data:
                model_table_name = data[data.index("MODEL") + 1].rstrip(';')
            else:
                model_table_name ="homesnew"
            # abc = _parser(f"CREATE TRAINING PROFILE oneshotSalary WITH [SELECT * FROM {table_name}];")
            abc = _parser(f"USE 'data/{currentDB}.db';")
            result = _parser(f"PREDICT WITH TRAINING PROFILE oneshotSalary BY ESTIMATOR {model_table_name};")
            if "DISPLAY OF" not in temp:
                result['graph']= ''
            yield result
        except Exception as e:
            yield {'text': e}

    elif data.upper().startswith("GENERATE") and "LABEL" in data.upper():
        '''GENERATE PREDICTION <target> LABEL home_No FEATURES <CRIM,ZN> ALGORITHM LR FROM bostonDB OVER homesnew;
           GENERATE PREDICTION tax LABEL home_No FEATURES rad,age ALGORITHM LR FROM Boston OVER homesnew;
           GENERATE PREDICTION tax LABEL home_No FEATURES rad,age ALGORITHM LR FROM Boston OVER homesnew;
        '''
        try:
            temp =data
            data = data.split()
            currentDB=data[data.index("FROM") + 1].strip()
            target_var = data[data.index("PREDICTION") + 1].strip()
            other_ftr = data[data.index("FEATURES") + 1].strip().split(',')
            table_name = data[data.index("FROM") + 1].strip()
            model_table_name = data[data.index("OVER") + 1].strip()
            type_name=data[data.index("ALGORITHM") + 1].strip()
            label=data[data.index("LABEL") + 1].strip()
            temp_ = _parser(f"USE 'data/{currentDB}.db';")
            temp_ = _parser(f"CREATE ESTIMATOR {model_table_name} MODEL_TYPE {type_name} FORMULA ${target_var}~{'+'.join(var for var in other_ftr)}$;")
            temp_ = _parser(f"CREATE TRAINING PROFILE oneshotSalary WITH [SELECT * FROM {table_name}];")
            temp_ = _parser(f"TRAIN {model_table_name} WITH TRAINING PROFILE oneshotSalary;")
            result = _parser(f"PREDICT WITH TRAINING PROFILE oneshotSalary BY ESTIMATOR {model_table_name};")
            result['text'] = f"target variable is {target_var} and independent variable is {other_ftr}"
            df=pd.DataFrame(result['table'])
            df.insert(0, label, range(1,len(df)+1))

             # Connect to the SQLite database
            current_directory = os.path.dirname(__file__)
            currentDBURL = os.path.join(current_directory,f'../data/{currentDB}.db')
            conn = sqlite3.connect(currentDBURL)
            # Add DataFrame as a table to the database
            df.to_sql(name=model_table_name, con=conn, if_exists='replace', index=False)
            conn.close()

            if "DISPLAY OF" not in temp:
                result['graph']= ''
            result['table']=df.to_dict(orient='records')
            yield result
        except IndexError:
            yield {'text': "Please provide all necessary data in the correct format."}

        # except Exception as e:
        #     yield {'text': f"An error occurred: {str(e)}"}

    elif data.upper().startswith("CREATE MODEL"):
        data = data.split()
        model_table_name = data[2]
        type_name = data[4].split(';')[0]
        yield {'text': f'{type_name} Model created Successfully'}
    elif data.upper().startswith('PREDICT'):
        try:
            data = data.split()
            target_var = data[1]
            other_ftr = data[3].split(',')
            table_name = data[-1].split(';')[0]
            model_table_name = data[-3]
            abc = _parser(f"CREATE ESTIMATOR salaryPredictor MODEL_TYPE {type_name} FORMULA ${target_var}~{'+'.join(var for var in other_ftr)}$;")
            abc = _parser(f"CREATE TRAINING PROFILE oneshotSalary WITH [SELECT * FROM {table_name}];")
            abc = _parser(f"TRAIN salaryPredictor WITH TRAINING PROFILE oneshotSalary;")
            result = _parser(f"PREDICT WITH TRAINING PROFILE oneshotSalary BY ESTIMATOR salaryPredictor;")
            result['text'] = f"target variable is {target_var} and independent variable is {other_ftr}"
            yield result
        except:
            yield {'text': "Please use proper query by order. Database is not set yet"}


    elif data.upper().startswith("INSPECT") and "CHECKNULL" in data.upper():
        table = data.split()[1]
        # print(table)
        response = ['']

        def check_null_values_in_db(db_file, table_name):
            global response
            connection = sqlite3.connect(db_file)
            cursor = connection.cursor()

            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            column_names = [col_info[1] for col_info in columns_info]
            print(column_names)

            # Fetch all rows
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            u = 1

            # Check for null values in each column
            for column_name in column_names:
                null_rows = [row for row in rows if row[column_names.index(column_name)] is None]
                if null_rows and u:
                    response = ["null value exist in column ", " : "]
                    u = 0
                if null_rows:
                    print(f"Null values found in {column_name} column:")
                    response.append(f" {column_name},")
                    for row in null_rows:
                        print(row)
                else:
                    print(f" in {column_name} column.")
            if u:
                response.append(f"No null values found {table_name}")

            connection.close()

        url = os.path.join(os.path.dirname(__file__), f"../data/{currentDB}.db")
        # print("url is", url)

        check_null_values_in_db(url, table)
        # print("response is ", response)
        yield {'text': response}

    elif data.upper().startswith("CONSTRUCT"):                
        '''
            command="GENERATE DISPLAY OF CLASSIFICATION Species ALGORITHM KNN WITH ACCURACY 100 LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris"      
            command = "GENERATE DISPLAY OF PREDICTION MonthlySales ALGORITHM GB WITH ACCURACY 100 LABEL ProductID FEATURES Age Price StockLevel FROM retail OVER retailTestData"
            CONSTRUCT ModelName AS SUPERVISED FOR CLUSTERING USING KMeans WITH CLUSTER OF 5 FROM Boston;
        '''
        data = data.split()
        currentDB=data[data.index("FROM") + 1].strip()
        model_name=data[data.index("CONSTRUCT") + 1].strip()
        operation =data[data.index("FOR") + 1].strip()
        algo =  data[data.index("USING") + 1].strip() 
        if operation=="CLUSTERING":
            n_cluster=data[data.index("WITH") + 3].strip()
            
            url = os.path.join(os.path.dirname(__file__), f"../data/{currentDB}.db")
            conn = sqlite3.connect(url)
            yield cluster(currentDB,conn,n_cluster)


    # elif data.upper().startswith("GENERATE DISPLAY"):
    #     '''GENERATE DISPLAY OF PREDICTION <target> LABEL home_No FEATURES <CRIM,ZN> ALGO LR FROM bostonDB OVER homesnew;
    #     GENERATE DISPLAY OF PREDICTION tax LABEL home_No FEATURES rad,age ALGORITHM LR FROM Boston OVER homesnew;
    #     GENERATE DISPLAY OF PREDICTION tax LABEL home_No FEATURES rad,age ALGO LR FROM Boston OVER homesnew;
    #     '''
    #     try:
    #         data = data.split()
    #         currentDB=data[12]
    #         target_var = data[4]
    #         other_ftr = data[8].split(',')
    #         table_name = data[12]
    #         model_table_name = data[-1]
    #         type_name=data[10]
    #         label=data[6]
    #         abc = _parser(f"USE 'data/{currentDB}.db';")

    #         abc = _parser(f"CREATE ESTIMATOR {model_table_name} MODEL_TYPE {type_name} FORMULA ${target_var}~{'+'.join(var for var in other_ftr)}$;")
    #         abc = _parser(f"CREATE TRAINING PROFILE oneshotSalary WITH [SELECT * FROM {table_name}];")
    #         abc = _parser(f"TRAIN {model_table_name} WITH TRAINING PROFILE oneshotSalary;")
    #         result = _parser(f"PREDICT WITH TRAINING PROFILE oneshotSalary BY ESTIMATOR {model_table_name};")
    #         result['text'] = f"target variable is {target_var} and independent variable is {other_ftr}"
    #         df=pd.DataFrame(result['table'])
    #         df.insert(0, label, range(1,len(df)+1))

    #          # Connect to the SQLite database
    #         current_directory = os.path.dirname(__file__)
    #         currentDBURL = os.path.join(current_directory,f'..c/data/{currentDB}.db')
    #         conn = sqlite3.connect(currentDBURL)
    #         # Add DataFrame as a table to the database
    #         df.to_sql(name=model_table_name, con=conn, if_exists='replace', index=False)
    #         conn.close()

    #         result['table']=pd.DataFrame(df).to_dict(orient='records')
    #         yield result
    #     except IndexError:
    #         yield {'text': "Please provide all necessary data in the correct format."}

    #     # except Exception as e:
    #     #     yield {'text': f"An error occurred: {str(e)}"}
    #     #         # except:
    #             #     yield {'text': "Please use proper query by order. Database is not set yet"}
            
   

"""


CONSTRUCT ModelName AS SUPERVISED FOR <PREDICTION | CLASSIFICATION | CLUSTERING>
[USING AlgorithmName]
[WITH ACCURACY P]
TRAIN ON N TEST ON M
FEATURES A1, A2, ..., An
FROM r1, r2,...,rn
WHERE c


GENERATE DISPLAY OF PREDICTION <target> LABEL home No
FEATURES <CRIM,ZN,NOX,DISL,TAX,PTRATIO> FROM bostonDB


INSPECT Iris CHECKNULL;
"""



""" CREATE ESTIMATOR salaryPredictor MODEL_TYPE KNN FORMULA $Species~SepalLengthCm$;
    CREATE TRAINING PROFILE oneshotSalary WITH [SELECT * FROM Iris];
    USE 'data/Iris.db';
    TRAIN salaryPredictor WITH TRAINING PROFILE oneshotSalary;
    PREDICT WITH TRAINING PROFILE oneshotSalary BY ESTIMATOR salaryPredictor; """

'''
USE salarydb;
CREATE MODEL model_table_name MODEL_TYPE LR;
PREDICT salary for  years by model_table_name with salary;

USE Iris;
CREATE MODEL model_table_name MODEL_TYPE KNN;
PREDICT Species FOR SepalLengthCm by model_table_name with Iris;
PetalLengthCm

USE Iris;
CREATE MODEL model_table_name MODEL_TYPE KNN;
PREDICT PetalLengthCm FOR SepalLengthCm,SepalWidthCm by model_table_name with Iris;
'''

'''
USE Boston;
CREATE MODEL model_table_name TYPE LR;
PREDICT tax for rad,age by model_table_name with Boston;
'''