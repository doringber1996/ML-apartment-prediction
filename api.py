from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle
import os

app = Flask(__name__)

with open('trained_model.pkl', 'rb') as file:
    model = pickle.load(file)

with open('column_transformer.pkl', 'rb') as file:
    column_transformer = pickle.load(file)

@app.route('/')
def home():
    print(model.feature_names_in_)
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    city = request.form.get('City')
    property_type = request.form.get('type')
    room_number = request.form.get('room_number')
    Area = request.form.get('Area')
    room_number = float(room_number)
    Area = float(Area)
    
    string_features = ['אילת', 'אריאל', 'באר שבע', 'בית שאן', 'בת ים', 'גבעת שמואל', 'דימונה', 'הוד השרון', 'הרצליה', 'זכרון יעקב', 'חולון', 'חיפה', 'יהוד מונוסון', 'ירושלים', 'כפר סבא', 'מודיעין מכבים רעות', 'נהריה', 'נוף הגליל', 'נס ציונה', 'נתניה', 'פתח תקווה', 'צפת', 'קרית ביאליק', 'ראשון לציון', 'רחובות', 'רמת גן', 'רעננה', 'שוהם', 'תל אביב', 'בית פרטי', 'דו משפחתי', 'דופלקס', 'דירה', 'דירת גג', 'דירת גן', 'פנטהאוז', "קוטג'"]

    input_data = pd.DataFrame({
        'City': [city],
        'type': [property_type],
        'room_number': [room_number],
        'Area': [Area]
    })
    
    for feature in string_features:
        input_data[feature] = 0
    
    input_data_encoded = column_transformer.transform(input_data)
    predicted_price = model.predict(input_data_encoded)[0]
    text_output = f"Predicted Property Value: {predicted_price:.2f}"

    return render_template('index.html', prediction_text=text_output)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
