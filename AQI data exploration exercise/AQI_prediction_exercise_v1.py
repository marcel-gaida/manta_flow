import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import io
from datetime import datetime, timedelta
import os

# --- 1. Load Data ---
# This section now asks the user to choose the data source.

# Define the sample data string
csv_data_string = """Date,Time,City,State,Country,AQI (US),Temperature (°C),Pressure (hPa),Humidity (%),Wind Speed (m/s)
08/01/2023,17:14:28,New York City,New York,USA,16,25,1019,42,6.26
08/01/2023,17:15:29,New York City,New York,USA,16,25,1019,42,6.26
08/01/2023,19:14:56,New York City,New York,USA,16,25,1020,45,6.26
08/01/2023,21:15:27,New York City,New York,USA,16,22,1021,51,4.02
08/01/2023,22:26:21,New York City,New York,USA,16,22,1021,52,4.02
08/01/2023,23:15:22,New York City,New York,USA,16,21,1022,51,4.47
08/02/2023,00:17:50,New York City,New York,USA,16,20,1022,51,4.12
08/02/2023,01:13:53,New York City,New York,USA,12,20,1022,52,4.47
08/02/2023,02:19:35,New York City,New York,USA,12,19,1022,54,3.6
08/02/2023,03:13:55,New York City,New York,USA,12,18,1021,59,2.68
08/02/2023,04:18:45,New York City,New York,USA,12,18,1022,60,4.63
08/02/2023,05:14:44,New York City,New York,USA,12,18,1022,59,3.6
08/02/2023,06:15:56,New York City,New York,USA,8,17,1022,62,3.58
08/02/2023,07:12:21,New York City,New York,USA,12,18,1023,64,4.02
08/02/2023,08:31:48,New York City,New York,USA,12,19,1024,58,3.6
08/02/2023,09:18:45,New York City,New York,USA,12,21,1024,51,4.47
08/02/2023,10:14:09,New York City,New York,USA,12,22,1024,44,4.92
08/02/2023,11:14:46,New York City,New York,USA,12,23,1024,42,5.14
08/02/2023,12:20:12,New York City,New York,USA,12,24,1023,40,4.63
08/02/2023,13:13:01,New York City,New York,USA,12,25,1023,39,3.13
08/02/2023,14:18:43,New York City,New York,USA,12,25,1023,39,1.54
08/02/2023,15:11:51,New York City,New York,USA,16,26,1022,39,5.66
08/02/2023,16:15:28,New York City,New York,USA,16,26,1021,41,4.92
08/02/2023,17:12:47,New York City,New York,USA,16,25,1021,43,3.6
08/02/2023,18:13:43,New York City,New York,USA,16,25,1022,44,4.63
08/02/2023,19:14:26,New York City,New York,USA,16,23,1021,51,6.71
08/02/2023,21:16:50,New York City,New York,USA,16,21,1022,58,4.92
08/02/2023,22:28:18,New York City,New York,USA,16,21,1022,59,4.92
08/02/2023,23:15:23,New York City,New York,USA,12,20,1022,61,5.14
08/03/2023,00:17:56,New York City,New York,USA,12,20,1023,62,4.12
"""

df = None
while df is None:
    print("Please choose the data source for modeling and prediction:")
    print("  1: Use sample data")
    print("  2: Use CSV file (e.g., 'data_export_June05_2025.csv')")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        print("\nLoading sample data...")
        df = pd.read_csv(io.StringIO(csv_data_string))
        print("Sample data loaded successfully.")
    elif choice == '2':
        csv_filename = 'data_export_June05_2025.csv'
        print(f"\nLoading CSV file: '{csv_filename}'...")
        try:
            df = pd.read_csv(csv_filename)
            print(f"Full dataset loaded successfully from '{csv_filename}'.")
        except FileNotFoundError:
            print(f"Error: '{csv_filename}' not found.")
            print("Please make sure the script and the CSV file are in the same directory.\n")
    else:
        print("Invalid choice. Please enter 1 or 2.\n")

# --- ADD DayOfYear to original df for seasonal forecasting ---
try:
    temp_timestamp = pd.to_datetime(df['Date'], errors='coerce')
    df['DayOfYear_lookup'] = temp_timestamp.dt.dayofyear
    print("\nAdded 'DayOfYear_lookup' to the original DataFrame for better forecasting placeholders.")
except Exception as e:
    df['DayOfYear_lookup'] = None
    print(f"\nWarning: Could not create 'DayOfYear_lookup' for forecasting. Will use overall average. Error: {e}")

print("\n--- Initial Data Head ---")
print(df.head())
print("\n--- Data Info ---")
df.info()
print("\n--- Descriptive Statistics ---")
print(df.describe(include='all'))
print("\n--- Missing Values ---")
print(df.isnull().sum())

# --- 2. Preprocessing & Feature Engineering ---
target_columns = ['AQI (US)', 'Temperature (°C)']
original_numerical_features = ['Pressure (hPa)', 'Humidity (%)', 'Wind Speed (m/s)']
original_categorical_features = ['City', 'State', 'Country']
datetime_cols = ['Date', 'Time']
time_engineered_features = ['Hour', 'DayOfWeek', 'Month', 'DayOfYear']

df_processed = df.copy()

# --- Handle Datetime Features ---
try:
    df_processed['Timestamp'] = pd.to_datetime(df_processed['Date'] + ' ' + df_processed['Time'],
                                               format='%m/%d/%Y %H:%M:%S', errors='coerce')
    df_processed.dropna(subset=['Timestamp'], inplace=True)
    df_processed['Hour'] = df_processed['Timestamp'].dt.hour
    df_processed['DayOfWeek'] = df_processed['Timestamp'].dt.dayofweek
    df_processed['Month'] = df_processed['Timestamp'].dt.month
    df_processed['DayOfYear'] = df_processed['Timestamp'].dt.dayofyear
    processed_numerical_features = original_numerical_features + time_engineered_features
    df_processed.drop(columns=datetime_cols + ['Timestamp'], inplace=True)
    print("\n--- Datetime features processed ---")
except Exception as e:
    print(f"\nError processing datetime features: {e}.")
    processed_numerical_features = original_numerical_features
    df_processed.drop(columns=[col for col in datetime_cols if col in df_processed.columns], inplace=True,
                      errors='ignore')

# --- Handle Categorical Features ---
final_categorical_features_for_encoding = []
for col in original_categorical_features:
    if col in df_processed.columns:
        if df_processed[col].nunique() == 1:
            print(f"Dropping categorical feature '{col}' as it has only one unique value.")
            df_processed.drop(columns=[col], inplace=True)
        else:
            final_categorical_features_for_encoding.append(col)
if not final_categorical_features_for_encoding:
    print("No multi-value categorical features to one-hot encode.")

# --- Define X and y ---
for col in target_columns:
    df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
df_processed.dropna(subset=target_columns, inplace=True)
X = df_processed.drop(columns=target_columns, errors='ignore')
y = df_processed[target_columns]
processed_numerical_features = [nf for nf in processed_numerical_features if nf in X.columns]

# --- Create Preprocessing Pipelines ---
numerical_pipeline = Pipeline([('imputer', SimpleImputer(strategy='mean')), ('scaler', StandardScaler())])
categorical_pipeline = Pipeline([('imputer', SimpleImputer(strategy='most_frequent')),
                                 ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
preprocessor = ColumnTransformer(transformers=[('num', numerical_pipeline, processed_numerical_features),
                                               ('cat', categorical_pipeline, final_categorical_features_for_encoding)],
                                 remainder='drop')

# --- 3. Model Training ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = Pipeline([('preprocessor', preprocessor),
                  ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))])

print("\n--- Training the model to predict AQI and Temperature ---")
if X_train.empty:
    print("X_train is empty. Cannot train the model.")
else:
    try:
        model.fit(X_train, y_train)
        print("Model training complete.")
    except Exception as e:
        print(f"Error during model training: {e}")
        exit()

    # --- 4. Model Evaluation ---
    print("\n--- Evaluating the model ---")
    y_pred = model.predict(X_test)
    for i, target_name in enumerate(target_columns):
        mae = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
        mse = mean_squared_error(y_test.iloc[:, i], y_pred[:, i])
        r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
        print(f"\nEvaluation for '{target_name}':")
        print(f"  Mean Absolute Error (MAE): {mae:.2f}")
        print(f"  Mean Squared Error (MSE): {mse:.2f}")
        print(f"  R-squared (R²): {r2:.2f}")

    # --- 5. Feature Importances ---
    try:
        feature_names_out = model.named_steps['preprocessor'].get_feature_names_out()
        importances = model.named_steps['regressor'].feature_importances_
        feature_importance_df = pd.DataFrame({'feature': feature_names_out, 'importance': importances}).sort_values(
            by='importance', ascending=False)
        print("\n--- Feature Importances (averaged over all targets) ---")
        print(feature_importance_df.head(10))
    except Exception as fe_e:
        print(f"Could not get feature importances: {fe_e}")

    # --- 6. 5-Day Forecast ---
    print("\n--- Generating 5-Day AQI & Temperature Forecast ---")

    forecast_start_date = datetime.now() + timedelta(days=1)
    future_dates = [forecast_start_date + timedelta(days=i) for i in range(5)]

    future_data_list = []
    historical_aqi_averages = []

    for date_val in future_dates:
        data_point = {'Date': date_val.strftime('%m/%d/%Y'), 'Time': '12:00:00'}
        future_day_of_year = date_val.timetuple().tm_yday

        historical_data_for_day = pd.DataFrame()
        if 'DayOfYear_lookup' in df.columns and df['DayOfYear_lookup'].notna().any():
            historical_data_for_day = df[df['DayOfYear_lookup'] == future_day_of_year]

        print(f"\nFor {date_val.strftime('%Y-%m-%d')} (Day {future_day_of_year}): "
              f"Found {len(historical_data_for_day)} historical records. "
              f"Using {'seasonal' if not historical_data_for_day.empty else 'overall'} average for placeholder data.")

        seasonal_aqi_avg = np.nan
        if not historical_data_for_day.empty and 'AQI (US)' in historical_data_for_day.columns:
            seasonal_aqi_avg = historical_data_for_day['AQI (US)'].mean()
        historical_aqi_averages.append(seasonal_aqi_avg)

        for col in original_numerical_features:
            if not historical_data_for_day.empty and col in historical_data_for_day.columns:
                data_point[col] = historical_data_for_day[col].mean()
            else:
                if col in X_train.columns:
                    data_point[col] = X_train[col].mean()
                else:
                    data_point[col] = np.nan

        for col in original_categorical_features:
            if col in X_train.columns:
                data_point[col] = X_train[col].mode()[0] if not X_train[col].empty else "Unknown"
        future_data_list.append(data_point)

    future_df_for_prediction = pd.DataFrame(future_data_list)
    print("\nPlaceholder data for 5-day forecast (before feature engineering):")
    print(future_df_for_prediction)

    try:
        future_df_for_prediction['Timestamp'] = pd.to_datetime(
            future_df_for_prediction['Date'] + ' ' + future_df_for_prediction['Time'], format='%m/%d/%Y %H:%M:%S',
            errors='coerce')
        future_df_for_prediction.dropna(subset=['Timestamp'], inplace=True)
        future_df_for_prediction['Hour'] = future_df_for_prediction['Timestamp'].dt.hour
        future_df_for_prediction['DayOfWeek'] = future_df_for_prediction['Timestamp'].dt.dayofweek
        future_df_for_prediction['Month'] = future_df_for_prediction['Timestamp'].dt.month
        future_df_for_prediction['DayOfYear'] = future_df_for_prediction['Timestamp'].dt.dayofyear
        future_df_for_prediction.drop(columns=datetime_cols + ['Timestamp'], inplace=True)
        print("\nDatetime features engineered successfully for forecast data.")
    except Exception as e:
        print(f"\nError engineering datetime features for forecast data: {e}")

    if not future_df_for_prediction.empty:
        try:
            future_predictions = model.predict(future_df_for_prediction)

            blended_aqi_predictions = []
            for i, prediction in enumerate(future_predictions):
                model_predicted_aqi = prediction[0]
                historical_avg_aqi = historical_aqi_averages[i]

                if pd.notna(historical_avg_aqi):
                    blended_aqi = (0.7 * model_predicted_aqi) + (0.3 * historical_avg_aqi)
                else:
                    blended_aqi = model_predicted_aqi
                blended_aqi_predictions.append(blended_aqi)

            forecast_output_df = pd.DataFrame({
                'Forecast Date': [d.strftime('%Y-%m-%d') for d in future_dates],
                'Model Predicted AQI': [f"{pred[0]:.2f}" for pred in future_predictions],
                'Blended Predicted AQI': [f"{pred:.2f}" for pred in blended_aqi_predictions],
                'Predicted Temperature (°C)': [f"{pred[1]:.2f}" for pred in future_predictions]
            })

            # This line forces pandas to display all columns
            pd.set_option('display.max_columns', None)

            print("\n--- 5-Day AQI & Temperature Forecast (using placeholder weather data) ---")
            print(forecast_output_df)
            print(
                "\nIMPORTANT: The 'Blended Predicted AQI' combines the model's prediction with the historical average for that day.")
            print("For a meaningful forecast, replace placeholder weather values with actual future weather forecasts.")
        except Exception as e_forecast:
            print(f"\nError during 5-day forecast prediction: {e_forecast}")

print("\n--- Script Finished ---")
