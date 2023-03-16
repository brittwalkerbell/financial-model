import pyodbc
import pandas as pd
import sqlalchemy
import urllib
import datetime


def type_curve_interpolator(curvedf):
    resampled_df = pd.DataFrame()

    daily_df = curvedf.loc[curvedf['type'] == 'daily']
    monthly_df = curvedf.loc[curvedf['type'] == 'monthly']
    monthly_df.reset_index(drop=True, inplace=True)

    for i in monthly_df.index:
        oil_list = [monthly_df.iloc[i, 1] / 30] * 30
        gas_list = [monthly_df.iloc[i, 2] / 30] * 30
        water_list = [monthly_df.iloc[i, 3] / 30] * 30

        result_df = pd.DataFrame({'oil': oil_list, 'gas': gas_list, 'water': water_list})
        resampled_df = resampled_df.append(result_df)

    total_df = daily_df.append(resampled_df)
    total_df.reset_index(drop=True, inplace=True)
    total_df = total_df.drop('type', axis=1)

    return total_df

def assign_gps_colors(welldf):
    one_year = datetime.datetime.today() + datetime.timedelta(days=365)
    two_years = datetime.datetime.today() + datetime.timedelta(days=730)
    for i in welldf.index:
        if welldf.iloc[i,1] < one_year:
            welldf.at[i, 'color'] = '#FF0000'
        if welldf.iloc[i,1] >= one_year and welldf.iloc[i,1] < two_years:
            welldf.at[i, 'color'] = '#FFC000'
        if welldf.iloc[i,1] >= two_years:
            welldf.at[i, 'color'] = '#92D050'

    return welldf


welldf = pd.read_excel(r'C:\Users\bbell\OneDrive - CrownQuest Operating\Desktop\seabee sample.xlsx',
                       sheet_name='Sheet1',)

#curvedf = pd.read_excel(r'C:\Users\bbell\Desktop\wilkinson curves v3.xlsx', sheet_name='JM-2-5800-5Y')

#gpsdf = pd.read_excel(r'C:\Users\bbell\Desktop\seabee wells.xlsx', usecols=['WID', 'wellName', 'lat', 'long', 'color'])


conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=SV-GEOSCADA\SQLEXPRESS;'
                      'DATABASE=OGW_Forecast;'
                      'Trusted_Connection=yes;')

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=SV-GEOSCADA\SQLEXPRESS;DATABASE=OGW_Forecast;Trusted_Connection=yes")

engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)


welldf = assign_gps_colors(welldf)
welldf.to_sql(name="Delayed Frac Schedule", con=engine, schema='dbo', index=False, if_exists='replace')

#gpsdf.to_sql(name="gps", con=engine, schema='dbo', index=False, if_exists='replace')

#curvedf = type_curve_interpolator(curvedf)
#print(curvedf)

#curvedf.to_sql(name="W-JM-2-5800-5Y", con=engine, schema='dbo', index=False, if_exists='replace')


conn.close()