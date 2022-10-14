import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os.path


def Create_Database():
    if not os.path.exists('InferenceSystem.db'):
        connect = sqlite3.connect('InferenceSystem.db')
        Feature = pd.read_excel('./Data/Data.xlsx', sheet_name='Feature', index_col='FeatureNo')
        Individual = pd.read_excel('./Data/Data.xlsx', sheet_name='Individual', index_col='IndividualNo')
        Rule = pd.read_excel('./Data/Data.xlsx', sheet_name='Rule', index_col='RuleNo')
        IndexCount = pd.read_excel('./Data/Data.xlsx', sheet_name='IndexCount', index_col='TableName')
        engine = create_engine('sqlite:///InferenceSystem.db')
        Feature.to_sql('Feature', engine)
        Individual.to_sql('Individual', engine)
        Rule.to_sql('Rule', engine)
        IndexCount.to_sql('IndexCount', engine)


def Reset_Database():
    if os.path.exists('InferenceSystem.db'):
        connect = sqlite3.connect('InferenceSystem.db')
        conn = connect.cursor()
        conn.execute('''DROP TABLE Feature;''')
        conn.execute('''DROP TABLE Individual;''')
        conn.execute('''DROP TABLE IndexCount;''')
        conn.execute('''DROP TABLE Rule;''')
        connect.commit()
        Feature = pd.read_excel('./Data/Data.xlsx', sheet_name='Feature', index_col='FeatureNo')
        Individual = pd.read_excel('./Data/Data.xlsx', sheet_name='Individual', index_col='IndividualNo')
        Rule = pd.read_excel('./Data/Data.xlsx', sheet_name='Rule', index_col='RuleNo')
        IndexCount = pd.read_excel('./Data/Data.xlsx', sheet_name='IndexCount', index_col='TableName')
        engine = create_engine('sqlite:///InferenceSystem.db')
        Feature.to_sql('Feature', engine)
        Individual.to_sql('Individual', engine)
        Rule.to_sql('Rule', engine)
        IndexCount.to_sql('IndexCount', engine)
    else:
        Create_Database()

def Query(SQLCode):
    engine = create_engine('sqlite:///InferenceSystem.db')
    Data = pd.read_sql_query(SQLCode, engine)
    return Data


def Add_Feature(Feature):
    connect = sqlite3.connect('InferenceSystem.db')
    conn = connect.cursor()
    conn.execute("UPDATE IndexCount SET IndexNo=IndexNo+1 WHERE TableName = 'Feature';")
    FeatureNo = 'F' + str(Query("""SELECT IndexNo FROM IndexCount WHERE TableName = 'Feature'""")['IndexNo'][0] + 1)
    conn.execute(f"""INSERT INTO Feature (FeatureNo, FeatureName) VALUES('{FeatureNo}', '{Feature}');""")
    connect.commit()


def Delete_Feature(FeatureNo):
    connect = sqlite3.connect('InferenceSystem.db')
    conn = connect.cursor()
    conn.execute(f"DELETE FROM Rule WHERE Condition LIKE '%{FeatureNo}%';")
    conn.execute(f"DELETE FROM Rule WHERE Result LIKE '%{FeatureNo}%';")
    conn.execute(f"DELETE FROM Feature WHERE FeatureNo = '{FeatureNo}';")
    connect.commit()


def Get_Name(TableName, Index):
    return Query(f"SELECT {TableName}Name FROM {TableName} WHERE {TableName}No = '{Index}';")[TableName + 'Name'][0]


def Get_No(TableName, Index):
    return Query(f"SELECT {TableName}No FROM {TableName} WHERE {TableName}Name = '{Index}';")[TableName + 'No'][0]


def Add_Individual(Individual):
    connect = sqlite3.connect('InferenceSystem.db')
    conn = connect.cursor()
    conn.execute("UPDATE IndexCount SET IndexNo=IndexNo+1 WHERE TableName = 'Individual';")
    IndividualNo = 'I' + str(
        Query("""SELECT IndexNo FROM IndexCount WHERE TableName = 'Individual'""")['IndexNo'][0] + 1)
    conn.execute(f"""INSERT INTO Individual (IndividualNo, IndividualName) VALUES('{IndividualNo}', '{Individual}');""")
    connect.commit()


def Delete_Individual(IndividualNo):
    connect = sqlite3.connect('InferenceSystem.db')
    conn = connect.cursor()
    conn.execute(f"DELETE FROM Rule WHERE Result = '{IndividualNo}';")
    conn.execute(f"DELETE FROM Individual WHERE IndividualNo = '{IndividualNo}';")
    connect.commit()


def Add_Rule(Condition, Result):
    connect = sqlite3.connect('InferenceSystem.db')
    conn = connect.cursor()
    conn.execute("UPDATE IndexCount SET IndexNo=IndexNo+1 WHERE TableName = 'Rule';")
    RuleNo = 'R' + str(Query("""SELECT IndexNo FROM IndexCount WHERE TableName = 'Rule'""")['IndexNo'][0] + 1)
    conn.execute(f"""INSERT INTO Rule (RuleNo, Condition, Result) VALUES('{RuleNo}', '{Condition}','{Result}');""")
    connect.commit()


def Delete_Rule(RuleNo):
    connect = sqlite3.connect('InferenceSystem.db')
    conn = connect.cursor()
    conn.execute(f"DELETE FROM Rule WHERE RuleNo='{RuleNo}';")
    connect.commit()
