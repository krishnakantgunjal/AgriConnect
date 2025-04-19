from flask import Flask, request, render_template, jsonify
import numpy as np
import joblib
import heapq

# Creating Flask app
app = Flask(__name__)

# Load the model and scalers using joblib
model = joblib.load("model.pkl")
sc = joblib.load('standscaler.pkl')
ms = joblib.load('minmaxscaler.pkl')

# Dictionary to map prediction to crop
crop_dict = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
    8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
    14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
    19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}

# Define crop groupings based on similarity
crop_groups = {
    "cereals": [1, 2],                       # Rice, Maize
    "fibers": [3, 4],                        # Jute, Cotton
    "fruits": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],  # Coconut, Papaya, Orange, Apple, etc.
    "pulses": [15, 16, 17, 18, 19, 20, 21],  # Lentil, Blackgram, etc.
    "beverages": [22]                        # Coffee
}

# Function to get the group of a crop
def get_crop_group(crop_id):
    for group, ids in crop_groups.items():
        if crop_id in ids:
            return group
    return None

# Function to get top 3 crop recommendations
def get_top_three_recommendations(prediction_id, probabilities=None):
    # If we have probabilities, use them to find top 3
    if probabilities is not None and len(probabilities) > 0:
        # Get the indices of the 3 highest probabilities
        top_indices = heapq.nlargest(3, range(len(probabilities)), key=probabilities.__getitem__)
        return [{"crop_id": int(i+1), "crop_name": crop_dict.get(i+1), "confidence": round(probabilities[i] * 100, 2)} 
                for i in top_indices]
    
    # Otherwise, use the crop grouping approach
    main_crop_name = crop_dict.get(prediction_id)
    main_crop_group = get_crop_group(prediction_id)
    
    # Get all crops in the same group
    same_group_crops = [crop_id for crop_id in crop_groups.get(main_crop_group, []) 
                      if crop_id != prediction_id]
    
    # Start with the main prediction
    result = [{"crop_id": prediction_id, "crop_name": main_crop_name, "confidence": 90}]
    
    # Add up to 2 more from the same group
    if len(same_group_crops) >= 2:
        result.append({"crop_id": same_group_crops[0], "crop_name": crop_dict.get(same_group_crops[0]), "confidence": 80})
        result.append({"crop_id": same_group_crops[1], "crop_name": crop_dict.get(same_group_crops[1]), "confidence": 70})
        return result
    
    # Add whatever crops we have from the same group
    for i, crop_id in enumerate(same_group_crops):
        result.append({"crop_id": crop_id, "crop_name": crop_dict.get(crop_id), "confidence": 80 - (i * 10)})
    
    # If we still need more, take from other groups
    if len(result) < 3:
        # Get a crop from each other group until we have 3
        for group, crop_ids in crop_groups.items():
            if len(result) >= 3:
                break
            if group != main_crop_group and crop_ids:
                result.append({"crop_id": crop_ids[0], 
                              "crop_name": crop_dict.get(crop_ids[0]),
                              "confidence": 70 - ((len(result) - 1) * 10)})
    
    return result[:3]

# Define routes
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/recommendation')
def recommendation():
    return render_template("recommendation.html")

@app.route("/predict", methods=['POST'])
def predict():
    try:
        # Check if request is JSON
        if request.is_json:
            data = request.get_json()
            N = data.get('Nitrogen')
            P = data.get('Phosporus') 
            K = data.get('Potassium')
            temp = data.get('Temperature')
            humidity = data.get('Humidity')
            ph = data.get('Ph')
            rainfall = data.get('Rainfall')
        else:
            # Extracting data from the form
            N = request.form.get('Nitrogen')
            P = request.form.get('Phosporus')
            K = request.form.get('Potassium')
            temp = request.form.get('Temperature')
            humidity = request.form.get('Humidity')
            ph = request.form.get('Ph')
            rainfall = request.form.get('Rainfall')

        # Convert inputs to float
        feature_list = [float(N), float(P), float(K), float(temp), float(humidity), float(ph), float(rainfall)]
        single_pred = np.array(feature_list).reshape(1, -1)

        # Scale the features
        scaled_features = ms.transform(single_pred)
        final_features = sc.transform(scaled_features)

        # Make prediction
        prediction = model.predict(final_features)
        
        # Get prediction probabilities if the model supports it
        top_crops = []
        try:
            probabilities = model.predict_proba(final_features)[0]
            top_crops = get_top_three_recommendations(prediction[0], probabilities)
        except:
            # If the model doesn't support probabilities, use the grouping approach
            top_crops = get_top_three_recommendations(prediction[0])

        # Generate result message
        predicted_crop = crop_dict.get(prediction[0], "Unknown Crop")
        
        # Prepare response
        response = {
            'status': 'success',
            'prediction': predicted_crop,
            'prediction_id': int(prediction[0]),
            'top_crops': top_crops,
            'input_data': {
                'Nitrogen': N,
                'Phosporus': P,
                'Potassium': K,
                'Temperature': temp,
                'Humidity': humidity,
                'Ph': ph,
                'Rainfall': rainfall
            }
        }
        
        # Return JSON if it was a JSON request, otherwise render template
        if request.is_json:
            return jsonify(response)
        else:
            return render_template('recommendation.html', result=predicted_crop, top_crops=top_crops)
            
    except Exception as e:
        error_response = {'status': 'error', 'message': str(e)}
        if request.is_json:
            return jsonify(error_response), 400
        else:
            return render_template('recommendation.html', error=str(e))


if __name__ == '__main__':
    app.run(debug=True)