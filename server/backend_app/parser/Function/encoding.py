import sqlite3,os
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, LabelEncoder
from sqlalchemy import create_engine

def encoding(url, table_name, cmd):
    ''' INSPECT ENCODING USING ONE-HOT feature medv from boston '''
    # conn = sqlite3.connect(url)
    connection_string = os.getenv("POSTGES_URL")
    query = f'SELECT * FROM "{table_name}"'
    conn = create_engine(connection_string)
    data = pd.read_sql_query(query, conn)
    features = cmd[cmd.index("INSPECT") + 1]
    method = cmd[cmd.index("METHOD")+ 1] if "METHOD" in cmd else "Ordinal"
    print(method)
    response={}
    print(method.upper())
    if method.upper() == "ORDINAL":
        response['text']= ordinal_encoding(data, features, cmd, conn, table_name)
    elif method.upper() == "ONE-HOT":
        response['text']= onehot_encoding(data, features, cmd, conn, table_name)
    elif method.upper() == "LABEL":
        response['text']= label_encoding(data, features, cmd, conn, table_name)
    elif method.upper() == "TARGET":
        response['text']= target_encoding(data, features, cmd, conn, table_name)
    return response
def ordinal_encoding(data, var, cmd, conn, table_name):
    """INSPECT ENCODING USING Ordinal FEATURE Species FROM Iris;"""
    unique_val = data[var].unique()  
    enc_val = range(len(unique_val)) 
    order = cmd[cmd.index("ORDER") + 1].split(',') if "ORDER" in cmd else data[var].unique()
    ordinal_enc_dict = {val: new_val for val, new_val in zip(order, enc_val)}
    
    if len(ordinal_enc_dict) == len(unique_val):
        encoder = OrdinalEncoder(categories=[list(ordinal_enc_dict.keys())])
        data[var] = encoder.fit_transform(data[[var]])
        data.to_sql(table_name, conn, if_exists='replace', index=False)
        print(data)
        return f"Ordinal Encoding Succcessfully Done!"
    else:
        return None

def onehot_encoding(data, var, cmd, conn, table_name):
    """INSPECT ENCODING USING One-Hot ENCODING FEATURE Species FROM Iris;"""
    # data = pd.get_dummies(data[var]) it will also return one hot encoded data
    encoder = OneHotEncoder()
    encoded_data = encoder.fit_transform(data[[var]])
    encoded_df = pd.DataFrame(encoded_data.toarray(), columns=encoder.get_feature_names_out([var]))
    data = pd.concat([data, encoded_df], axis=1)
    data.drop(columns=[var], inplace=True)
    data.to_sql(table_name, conn, if_exists='replace', index=False)
    print(data)
    return f"One-hot Encoding Succcessfully Done!"

def label_encoding(data, var, cmd, conn, table_name):
    """INSPECT ENCODING USING Label ENCODING FEATURE Species FROM Iris;"""
    print('label encode')
    label_encoder = LabelEncoder()
    data[var] = label_encoder.fit_transform(data[var])
    data.to_sql(table_name, conn, if_exists='replace', index=False)
    print(data)
    return f"Label Encoding Succcessfully Done!"


def target_encoding(data, cat_var, cmd, conn, table_name):
    """INSPECT ENCODING USING TARGET ENCODING FEATURE Species  TARGET-FEATURE SepalLengthCm FROM Iris;"""
    try: target_var = cmd[cmd.index("TARGET-FEATURE") + 1] if "TARGET-FEATURE" in cmd else None
    except ValueError as ve: return None
    # data = {
    #     "Make": ["Toyota", "Honda", "Toyota", "Ford", "Honda", "Ford"],
    #     # "Price Range": ["High", "Medium", "Low", "Medium", "Low", "High"],
    #     "Mileage": [50000, 60000, 30000, 70000, 40000, 80000],
    #     "Age": [5, 3, 7, 2, 4, 6],
    #     "Price": [15000, 18000, 12000, 20000, 17000, 22000]
    # }
    # data = pd.DataFrame(data)
    # print(data)
    # target_var = "Price"

    # cat_var = "Make"
    target_mean = data.groupby(cat_var)[target_var].mean()
    print(target_mean)
    data[target_var+"_target_encoded"] = data[cat_var].map(target_mean)
    data.to_sql(table_name, conn, if_exists='replace', index=False)
    print(data)
    return f" Target Encoding Succcessfully Done!"


