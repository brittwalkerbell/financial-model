import pyodbc
import pandas as pd
import sqlalchemy
import urllib


def fetch_data(q):
    return pd.read_sql(
        sql=q,
        con=engine
    )


conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=SV-GEOSCADA\SQLEXPRESS;'
                      'DATABASE=OGW_Forecast;'
                      'Trusted_Connection=yes;')

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=SV-GEOSCADA\SQLEXPRESS;DATABASE=OGW_Forecast;Trusted_Connection=yes")

engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)


typecurve = 'W-LS-1.5-5800-5Y'
typecurve_query = (
    f'''
    SELECT *
    FROM [{typecurve}]
    '''
)
curvedf = fetch_data(typecurve_query)

#curvedf.to_excel(r'C:\Users\bbell\Desktop\W-LS-1.5-5800-5Y.xlsx')


well_query = (
    f'''
    SELECT *
    FROM gps
    '''
)
welldf = fetch_data(well_query)

welldf.to_excel(r'C:\Users\bbell\OneDrive - CrownQuest Operating\Desktop\gps.xlsx')


conn.close()
