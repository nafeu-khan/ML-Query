import os

from sqlalchemy import create_engine

from .operation.query_manipulate import Query_manipulate
from .Function.Show_db import show_db
from .operation.Generate import generate
from .operation.Inspect import inspect
from .operation.Construct import construct

from .operation import *
from .Function.Imputer import impute


def query_process(data):
    global type_name, model_table_name, target_var, other_ftr, response,currentDB
    if data.upper().startswith("SHOW"):
        yield show_db(data)
    if data.upper().startswith("CONSTRUCT"):
        '''CONSTRUCT PREDICTION MonthlySales ALGORITHM GB WITH  LABEL ProductID FEATURES Age Price StockLevel FROM retail OVER retailTestData ;
           CONSTRUCT CLASSIFICATION Species ALGORITHM KNN WITH  LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;
            '''
        yield construct(data)
    elif data.upper().startswith("GENERATE"):
        '''GENERATE DISPLAY OF PREDICTION MonthlySales ALGORITHM GB WITH ACCURACY 100 LABEL ProductID FEATURES Age Price StockLevel FROM retail OVER retailTestData ;
           GENERATE DISPLAY OF CLASSIFICATION Species ALGORITHM KNN WITH ACCURACY 100 LABEL ProductID FEATURES SepalLengthCm SepalWidthCm FROM Iris ;
            '''
        yield generate(data)

    elif data.upper().startswith("INSPECT"):
        '''
            INSPECT CHECKNULL FEATURES medv FROM Boston
            INSPECT ENCODING USING ONE-HOT ENCODING feature medv from boston

        '''
        yield inspect(data)
    elif data.upper().startswith("IMPUTE"):
        '''
            IMPUTE medv FROM Boston;
            IMPUTE * FROM Boston;
        '''
        yield impute(data)
    else :
        query =f'{data};'
        yield Query_manipulate(query)
        