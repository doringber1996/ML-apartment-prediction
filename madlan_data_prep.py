# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 21:53:06 2023

@author: user
"""
import pandas as pd
import numpy as np
import re
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math

path="C:/Users/user/Desktop/dor-university/3rd_year/2_simester/data_maining/matala_5/output_all_students_Train_v10.xlsx"
train_data=pd.read_excel(path)

path_test="C:/Users/user/Desktop/dor-university/3rd_year/2_simester/data_maining/matala_5/Dataset_for_test.xlsx"
test_data=pd.read_excel(path_test)

def prepare_data(data):
    
    data=data.iloc[np.where(data['price'].isna() == False)]
    
    def get_price(price_str):
        if type(price_str) == int:
            return price_str
        else:
            try:
                price_match = re.search(r'₪([\d,]+)', price_str)
                if price_match == None:
                     price = int(price_str.replace(',', ''))
                else:
                    price = price_match.group(1)
                    price = int(price.replace(',', ''))
            except:
                return None
        return price

    data['price']=data['price'].apply(lambda x: get_price(x))
    data=data.iloc[np.where(data['price'].isna() == False)]
    
    def get_area(area_str):
        if type(area_str) == int or type(area_str) == float:
            return area_str
        else:
            try:
                area_match = re.findall(r'\d+', area_str)
                area_match = int(area_match[0])
            except:
                return None
        return area_match

    data['Area']=data['Area'].apply(lambda x: get_area(x))
    data=data.iloc[np.where(data['Area']!=1000)]
    
    def clean_commas(string):
        if string == None or string == "nan" or string == "None":
            return 'not defined'
        string=str(string)
        words = re.findall(r'\b\w+\b', string)
        result = ' '.join(words)
        return result

    data['Street']=data['Street'].apply(lambda x: clean_commas(x))
    data['city_area']=data['city_area'].apply(lambda x: clean_commas(x))
    data['city_area']=data['city_area'].apply(lambda x: 'not defined' if 'מ ר' in x else x)
    data['description ']=data['description '].apply(lambda x: clean_commas(x))
    
    def creat_floors_cloumns(floor_out_of): 
        try:
            numbers = re.findall(r'\d+', floor_out_of)
            total_floors=int(max(numbers))
            floor=int(min(numbers))
        except:
                if floor_out_of =='קומת קרקע':
                    total_floors=0
                    floor=0
                elif floor_out_of == 'קומת מרתף':
                    total_floors=0
                    floor=-1
                else:
                    total_floors=None
                    floor=None
        return total_floors,floor

    data['total_floors']=data['floor_out_of'].apply(lambda x: creat_floors_cloumns(x)[0])
    data['floor']=data['floor_out_of'].apply(lambda x: creat_floors_cloumns(x)[1])
    data=data.iloc[np.where(data['floor'].isna() == False)]
    data['type'] = data['type'].replace('מיני פנטהאוז','פנטהאוז')
    data['type'] = data['type'].replace("קוטג' טורי","קוטג'")
    data['type'] = data['type'].replace("בניין","אחר")
    data['type'] = data['type'].replace("דירת נופש","דירה")
    data['type'] = data['type'].replace("מגרש","אחר")
    data['type'] = data['type'].replace("טריפלקס","אחר")
    data['type'] = data['type'].replace("נחלה","אחר")
    data=data.drop(data[data['type'] == "אחר"].index)
    
    data['floor'] = data['floor'].astype(float)
    
    def fix_entrance_date(val):
        try:
            entrance_time = (val-datetime.now()).days
            if entrance_time < 0:
                return "immediate"
            elif entrance_time < 183:
                return 'less_than_6_months'
            elif entrance_time >365:
                return 'above_year'
            else:
                return 'months_6_12'
        except:
            if 'None' in val or "לא צויין" in val or val == False:
                return "not_defined"
            if  "גמיש" in val or "flexible" in val:
                return "flexible"
            if "מיידי" in val or "immediate" in val:
                return "immediate"

    data['entranceDate ']=data['entranceDate '].apply(lambda x: fix_entrance_date(x))
    
    def boll_to_1_0(val):
        list_of_true=["1","True","yes","נגיש",'יש',"כן","TRUE"]
        list_of_false=["None","0","אין","False",'לא','no',"FALSE"]
        string=str(val)
        if string in list_of_true:
            val=1
        else:
            val=0
        return val

    test=data.loc[:,['hasElevator ','hasParking ','hasBars ','hasStorage ','hasAirCondition ','hasBalcony ','hasMamad ','handicapFriendly ']]
    
    for i in range(0,test.shape[1]):
        col=test.iloc[:,i].name
        data[col]=data[col].apply(lambda x: boll_to_1_0(x))

    def fix_condition(val):
        try:
            if val == False or val == None or 'None' in val:
                val = 'לא צויין'
            elif "חדש" in val:
                val = "חדש"
        except:
            return val
        return val

    data['condition ']=data['condition '].apply(lambda x: fix_condition(x))
    data=data.iloc[np.where(data['condition '].isna() == False)]
    data['room_number']=data['room_number'].apply(lambda x: get_area(x))
    test_appartment=data.iloc[np.where((data['room_number'].isna() == True) & (data['type'] == 'דירה'))]
    test_privat=data.iloc[np.where((data['room_number'].isna() == True) & (data['type'] != 'דירה'))]
    
    def fill_room_appartment(Area):
        room = Area/25
        room = round(room * 2) / 2
        return room

    def fill_room_privat(Area):
        room = Area/35
        room = round(room * 2) / 2
        return room

    test_appartment['room_number']=test_appartment['room_number'].fillna(test_appartment['Area'].apply(lambda x: fill_room_appartment(x)))
    test_privat['room_number']=test_privat['room_number'].fillna(test_privat['Area'].apply(lambda x: fill_room_privat(x)))
    data.loc[(data['room_number'].isna() == True) & (data['type'] == 'דירה'), 'room_number'] = test_appartment['room_number']
    data.loc[(data['room_number'].isna() == True) & (data['type'] != 'דירה'), 'room_number'] = test_privat['room_number']
    data=data.iloc[np.where(data['room_number'] != 35)]

    def fill_Area_appartment(room):
        Area = room*25
        return Area

    def fill_Area_privat(room):
        Area = room*35
        return Area

    test_appartment=data.iloc[np.where(((data['Area'].isna() == True)|(data['Area'] == 0)) & (data['type'] == 'דירה'))]
    test_privat=data.iloc[np.where(((data['Area'].isna() == True)|(data['Area'] == 0)) & (data['type'] != 'דירה'))]
    test_appartment['Area']=test_appartment['Area'].fillna(test_appartment['room_number'].apply(lambda x: fill_Area_appartment(x)))
    test_privat['Area']=test_privat['Area'].fillna(test_privat['room_number'].apply(lambda x: fill_Area_privat(x)))
    data.loc[(((data['Area'].isna() == True)|(data['Area'] == 0)) & (data['type'] == 'דירה')), 'Area'] = test_appartment['Area']
    data.loc[(((data['Area'].isna() == True)|(data['Area'] == 0)) & (data['type'] != 'דירה')), 'Area'] = test_privat['Area']
    data['City'].replace([" נהרייה"," נהריה","נהריה ","נהרייה"],"נהריה" ,inplace=True)
    data['City'].replace(["שוהם "," שוהם"],"שוהם" ,inplace=True)
    data['ratio_room_Area'] = data.loc[:,'Area']/data.loc[:,'room_number']
    data.drop(['Street','city_area','floor_out_of','description ','number_in_street','publishedDays ','num_of_images','furniture ','hasElevator ','hasParking ','hasBars ','hasStorage ','hasAirCondition ','hasBalcony ','hasMamad ','handicapFriendly '], axis=1, inplace=True)

    data = data.drop_duplicates()
    
    s = data.groupby('City')['price']
    quartiles = s.quantile([0.25, 0.75])
    q1 = quartiles.loc[:, 0.25]
    q3 = quartiles.loc[:, 0.75]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outlier_values = {}
    for group in s.groups:
        outliers = s.get_group(group)[(s.get_group(group) < lower_bound[group]) | (s.get_group(group) > upper_bound[group])]
        outlier_values[group] = outliers
    for group, outliers in outlier_values.items():
        for i in outliers:
            try:
                data=data.drop(data[data['price'] == i].index & data[data['City'] == group].index)
            except:
                continue

    s = data.groupby('City')['price']
    quartiles = s.quantile([0.25, 0.75])
    q1 = quartiles.loc[:, 0.25]
    q3 = quartiles.loc[:, 0.75]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outlier_values = {}
    for group in s.groups:
        outliers = s.get_group(group)[(s.get_group(group) < lower_bound[group]) | (s.get_group(group) > upper_bound[group])]
        outlier_values[group] = outliers
    for group, outliers in outlier_values.items():
        for i in outliers:
            try:
                data=data.drop(data[data['price'] == i].index & data[data['City'] == group].index)
            except:
                continue

    return data
