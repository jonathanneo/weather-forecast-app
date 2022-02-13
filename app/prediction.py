import pandas as pd 
import joblib 

def predict(user_inputs):
    # load model binaries 
    model = joblib.load("static/py/model.sav")
    encoder = joblib.load("static/py/encoder.sav")
    X_scaler = joblib.load("static/py/x_scaler.sav")
    y_scaler  = joblib.load("static/py/y_scaler.sav")

    # get the user input data 
    pressure = user_inputs["pressure"]
    humidity = user_inputs["humidity"]
    city_name = user_inputs["city_name"]
    
    # store city names into a df 
    city_input_df = pd.DataFrame({
        "city_name": [city_name]
    })

    # use encoder to transform the city df 
    X_transformed = encoder.transform(city_input_df)
    city_df = pd.DataFrame(columns=[*encoder.categories_], data=X_transformed.toarray())
    
    # store pressure and humidty into df 
    input_df = pd.DataFrame({
        "pressure": [pressure],
        "humidity": [humidity]
    })

    # combine both df's using indexes 
    df = input_df.merge(city_df, left_index=True, right_index=True)

    # scale the X input df 
    X_scaled = X_scaler.transform(df)

    # obtain prediction (y) 
    prediction_scaled = model.predict(X_scaled)
    
    # scale prediction to human readable terms i.e. celcius 
    prediction = y_scaler.inverse_transform(prediction_scaled)
    return prediction[0][0]