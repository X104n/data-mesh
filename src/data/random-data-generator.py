import pandas as pd
import random
import datetime

# Function to generate random weather data
def generate_weather_data(num_rows):
    data = []
    for _ in range(num_rows):
        date = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365))).date()
        temperature = random.uniform(-10, 40)  # Temperature in Celsius
        humidity = random.randint(20, 100)  # Humidity in percentage
        precipitation = random.uniform(0, 10)  # Precipitation in mm
        data.append([date, temperature, humidity, precipitation])
    return data

if __name__ == '__main__':

    number_of_files = 5
    number_of_rows = 10000

    for i in range(number_of_files):
        weather_data = generate_weather_data(number_of_rows)
        df = pd.DataFrame(weather_data, columns=["Date", "Temperature (°C)", "Humidity (%)", "Precipitation (mm)"])
        df.to_csv(f"weather_data_{i+1}.csv", index=False)

    print("CSV files have been generated!")