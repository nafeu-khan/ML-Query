from ..parser.parser import _parser
from django.http import JsonResponse

def query_process(data):
    print(data)
    global type_name,model_name,target_var,other_ftr,response
    if "USE"  in data.upper():
        splitted_data=data.split()
        currentDB=splitted_data[1].split(';')[0];
        response =_parser(f"USE 'data/{currentDB}.db';")
        return response
    elif "CREATE MODEL" in data.upper():
        data = data.split()
        model_name =data[2]
        type_name =data[4].split(';')[0]
        print(f'{type_name} Model created Successfully')
        response={'text': f'{type_name} Model created Successfully'}
        return response
    elif 'PREDICT' in data.upper():
        try:
            data = data.split()
            target_var= data[1]
            other_ftr=[]
            i=3
            while 1:
                if(data[i].upper() != 'BY'):
                    other_ftr.append(data[i])
                    i+=1
                else :
                    break
            print("other feature",other_ftr)
            # print(f"CREATE ESTIMATOR {model_name} MODEL_TYPE {type_name} FORMULA ${target_var}~{'+'.join(var for var in other_ftr)}$;")
            table_name =data[-1].split(';')[0]
            model_name=data[-3]
            if table_name == None or type_name==None:
                return {'text': "Please use proper query by order. Database is not set yet"}
            #1st query
            abc=_parser(f"CREATE ESTIMATOR salaryPredictor MODEL_TYPE {type_name} FORMULA ${target_var}~{'+'.join(var for var in other_ftr)}$;")
            abc=_parser(f"CREATE TRAINING PROFILE oneshotSalary WITH [SELECT * FROM {table_name}];")
            abc= _parser(f"TRAIN salaryPredictor WITH TRAINING PROFILE oneshotSalary;")
            result=_parser(f"PREDICT WITH TRAINING PROFILE oneshotSalary BY ESTIMATOR salaryPredictor;")
            print(result)
            return result
        except:
            return {'text': "Please use proper query by order. Database is not set yet"}


        """ CREATE ESTIMATOR salaryPredictor MODEL_TYPE KNN FORMULA $Species~SepalLengthCm$;
            CREATE TRAINING PROFILE oneshotSalary WITH [SELECT * FROM Iris];
            USE 'data/Iris.db';
            TRAIN salaryPredictor WITH TRAINING PROFILE oneshotSalary;
            PREDICT WITH TRAINING PROFILE oneshotSalary BY ESTIMATOR salaryPredictor;"""

    '''
    USE salarydb;
    CREATE MODEL model_name MODEL_TYPE LR;
    PREDICT salary for  years by model_name with salary;
    '''

    '''
    USE salarydb;
    CREATE MODEL model_name MODEL_TYPE LR;
    PREDICT salary for years by model_name with salary;
    '''