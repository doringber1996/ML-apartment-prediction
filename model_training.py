import pandas as pd
import numpy as np
import re
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, KFold, cross_val_predict
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder, MaxAbsScaler, StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNetCV
from madlan_data_prep import prepare_data
import pickle


file_name = "output_all_students_Train_v10.xlsx"
train_data=pd.read_excel(file_name)

train_data=prepare_data(train_data)
y = train_data['price']
X = train_data.loc[:,['City', 'type', 'room_number', 'Area']]

num_cols = [col for col in X.columns if X[col].dtype == 'float64']
cat_cols = [col for col in X.columns if X[col].dtype == 'object']
numerical = StandardScaler()
categorical = OneHotEncoder()
column_transformer = ColumnTransformer([
        ('numerical_preprocessing', numerical, num_cols),
        ('categorical_preprocessing', categorical, cat_cols)], remainder='passthrough')
X_transformed = column_transformer.fit_transform(X)
feature_names = list(column_transformer.get_feature_names_out())
feature_names = [x.split('_')[-1] for x in feature_names]
final_l1_ratio = 0.1 
final_alpha = 0.00014174741629268049
model=ElasticNet(l1_ratio=final_l1_ratio,alpha=final_alpha,random_state=42)
cv=KFold(n_splits=10,shuffle=True,random_state=42)
sc_scores=cross_val_score(model,X_transformed,y,cv=cv,scoring='neg_mean_squared_error')
X_transformed = pd.DataFrame(X_transformed.toarray(),columns=feature_names)
model.fit(X_transformed,y)


pickle.dump(column_transformer, open('column_transformer.pkl', 'wb'))
pickle.dump(model, open('trained_model.pkl', 'wb'))