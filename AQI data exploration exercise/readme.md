# AQI & Temperature Forecasting Model

This project contains an interactive Python script that builds and evaluates a sophisticated machine learning model to forecast both the Air Quality Index (AQI) and Temperature for the next five days. It leverages historical data to produce intelligent, seasonally-aware predictions.

## Features

- **Interactive Data Loading:** Allows the user to choose between running on a built-in sample dataset or a local CSV file.
- **Multi-Output Prediction:** A single `RandomForestRegressor` model is trained to predict both AQI and Temperature simultaneously, learning the complex relationships between weather, time, and air quality.
- **Advanced Feature Engineering:** Automatically creates time-based features (Hour, DayOfWeek, Month, DayOfYear) from standard date/time columns to capture seasonal and daily patterns.
- **Intelligent Forecasting with Seasonal Baseline:** The 5-day forecast is generated using a superior method for placeholder data:
    - It uses **seasonal averages** from historical data, calculating the average weather conditions for the specific day of the year being forecasted (e.g., using all previous June 10ths to forecast the next June 10th).
    - It produces a **Blended AQI Forecast**, a weighted average that combines the model's pattern-based prediction with the stable, historical AQI average for that specific day. This makes the final prediction more robust and reliable.
- **Model Evaluation:** Provides key performance metrics (MAE, MSE, R-squared) for both AQI and Temperature predictions, allowing you to gauge the model's accuracy on historical data.
- **Feature Importance:** Shows which factors (e.g., `DayOfYear`, `Pressure`) the model found most influential in its predictions, averaged across both targets.

## How to Use

1.  **Prerequisites:** Ensure you have Python and the following libraries installed:
    - `pandas`
    - `numpy`
    - `scikit-learn`

    You can install them using pip:
    ```bash
    pip install pandas numpy scikit-learn
    ```

2.  **Prepare Your Data:**
    - Place your historical data CSV file in the same directory as the script.
    - The script defaults to looking for `data_export_June05_2025.csv`. You can change this filename in the script if needed.
    - Your CSV should have columns similar to the sample data, including `Date`, `Time`, `AQI (US)`, `Temperature (°C)`, `Pressure (hPa)`, `Humidity (%)`, and `Wind Speed (m/s)`.

3.  **Run the Script:**
    - Open a terminal or command prompt in the project's directory.
    - Run the script (assuming you've named it `aqi_prediction_script_v1.py`):
      ```bash
      python aqi_prediction_script_v1.py
      ```
    - Follow the prompt to select your data source (sample data or your CSV file).
    - The script will then train the model and print the evaluation and the 5-day forecast.

## Understanding the Limitations

This script is an excellent educational tool and a solid framework for time-series forecasting. However, for real-world, mission-critical use, it's important to understand its limitations:

-   **Placeholder Forecast Data:** The future weather data is generated using historical averages. For a true forecast, this data should be replaced with an actual professional weather forecast from an API or other service.
-   **Blindness to External Events:** The model is only aware of the data in the CSV file. It cannot account for unpredictable, major events that heavily influence air quality, such as:
    -   **Wildfire Smoke:** A smoke plume from a distant fire can drastically increase the AQI, but the model will be unaware of it.
    -   **Dust Storms or Industrial Accidents:** Similar to wildfires, these external events are not captured in the input features.

To overcome these limitations, the model would need to be integrated with live, external data sources for weather forecasts and real-time pollutant/smoke data.

## Future Improvements

-   **Integrate a Live Weather API:** Replace placeholder data with real-time weather forecasts.
-   **Incorporate Smoke/Pollutant Data:** Add a feature for smoke concentration (e.g., from the NOAA or a commercial API) to make the model aware of events like wildfires.
-   **Hyperparameter Tuning:** Use techniques like `GridSearchCV` to find the optimal settings for the `RandomForestRegressor` and potentially improve accuracy.
-   **Web Interface:** Build a simple web front-end using a framework like Flask or Streamlit to make the tool easier to use and visualize the results.
