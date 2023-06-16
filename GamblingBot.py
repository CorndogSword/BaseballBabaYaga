import xgboost as xgb
import tensorflow as tf
import requests
import pandas as pd
import baseball_scraper as bs
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from sklearn.preprocessing import LabelEncoder

stadiums = {

    "New York Yankees": {
        "FieldName" : "Yankee Stadium",
        "Type": "Outdoor",
        "Latitude": 40.8296,
        "Longitude": -73.9262
    },
    "Boston Red Sox": {
        "FieldName" : "Fenway Park",
        "Type": "Outdoor",
        "Latitude": 42.3467,
        "Longitude": -71.0972
    },
    "Los Angeles Dodgers": {
        "FieldName" : "Dodger Stadium",
        "Type": "Outdoor",
        "Latitude": 34.0739,
        "Longitude": -118.2390
    },
    "Chicago Cubs": {
        "FieldName" : "Wrigley Field",
        "Type": "Outdoor",
        "Latitude": 41.9484,
        "Longitude": -87.6553
    },
    "Tampa Bay Rays": {
        "FieldName" : "Tropicana Field",
        "Type": "Indoor",
        "Latitude": 27.7681,
        "Longitude": -82.6534
    },
    "Toronto Blue Jays": {
        "FieldName" : "Rogers Centre",
        "Type": "Indoor",
        "Latitude": 43.6414,
        "Longitude": -79.3894
    },
    "St. Louis Cardinals": {
        "FieldName" : "Busch Stadium",
        "Type": "Indoor",
        "Latitude": 38.6226,
        "Longitude": -90.1928,
    },
    "Arizona Diamondbacks": {
        "FieldName" : "Chase Field",
        "Type": "Outdoor",
        "Latitude": 33.4453,
        "Longitude": -112.0667,
    },
    "Atlanta Braves": {
        "FieldName" : "Truist Park",
        "Type": "Outdoor",
        "Latitude": 33.8911,
        "Longitude": -84.4684,
    },
    "Baltimore Orioles": {
        "FieldName" : "Oriole Park at Camden Yards",
        "Type": "Outdoor",
        "Latitude": 39.2838,
        "Longitude": -76.6217,
    },
    "Chicago White Sox": {
        "FieldName" : "Guaranteed Rate Field",
        "Type": "Outdoor",
        "Latitude": 41.8300,
        "Longitude": -87.6339,
    },
    "Cincinnati Reds": {
        "FieldName" : "Great American Ball Park",
        "Type": "Outdoor",
        "Latitude": 39.0974,
        "Longitude": -84.5071,
    },
    "Cleveland Guardians": {
        "FieldName" : "Progressive Field",
        "Type": "Outdoor",
        "Latitude": 41.4962,
        "Longitude": -81.6852,
    },
    "Colorado Rockies": {
        "FieldName" : "Coors Field",
        "Type": "Outdoor",
        "Latitude": 39.7559,
        "Longitude": -104.9942,
    },
    "Detroit Tigers": {
        "FieldName" : "Comerica Park",
        "Type": "Outdoor",
        "Latitude": 42.3390,
        "Longitude": -83.0485,
    },
    "Houston Astros": {
        "FieldName" : "Minute Maid Park",
        "Type": "Outdoor",
        "Latitude": 29.7572,
        "Longitude": -95.3552,
    },
    "Kansas City Royals": {
        "FieldName" : "Kauffman Stadium",
        "Type": "Outdoor",
        "Latitude": 39.0517,
        "Longitude": -94.4803,
    },
    "Los Angeles Angels": {
        "FieldName" : "Angel Stadium",
        "Type": "Outdoor",
        "Latitude": 33.8003,
        "Longitude": -117.8827,
    },
    "Miami Marlins": {
        "FieldName" : "Marlins Park",
        "Type": "Outdoor",
        "Latitude": 25.778,
        "Longitude": -80.2196,
    },
    "Milwaukee Brewers": {
        "FieldName" : "Miller Park",
        "Type": "Outdoor",
        "Latitude": 43.0282,
        "Longitude": -87.9713,
    },
    "Minnesota Twins": {
        "FieldName" : "Target Field",
        "Type": "Outdoor",
        "Latitude": 44.9817,
        "Longitude": -93.2776,
    },
    "New York Mets": {
        "FieldName" : "Citi Field",
        "Type": "Outdoor",
        "Latitude": 40.7571,
        "Longitude": -73.8458,
    },
    "Oakland Athletics": {
        "FieldName" : "RingCentral Coliseum",
        "Type": "Outdoor",
        "Latitude": 37.7516,
        "Longitude": -122.2005,
    },
    "Philadelphia Phillies": {
        "FieldName" : "Citizens Bank Park",
        "Type": "Outdoor",
        "Latitude": 39.9061,
        "Longitude": -75.1665,
    },
    "Pittsburgh Pirates": {
        "FieldName" : "PNC Park",
        "Type": "Outdoor",
        "Latitude": 40.4475,
        "Longitude": -80.0072,
    },
    "San Diego Padres": {
        "FieldName" : "Petco Park",
        "Type": "Outdoor",
        "Latitude": 32.7076,
        "Longitude": -117.1570,
    },
    "San Francisco Giants": {
        "FieldName" : "Oracle Park",
        "Type": "Outdoor",
        "Latitude": 37.7786,
        "Longitude": -122.3893,
    },
    "Seattle Mariners": {
        "FieldName" : "T-Mobile Park",
        "Type": "Outdoor",
        "Latitude": 47.5913,
        "Longitude": -122.3325,
    },
    "Texas Rangers": {
        "FieldName" : "Globe Life Field",
        "Type": "Outdoor",
        "Latitude": 32.7475,
        "Longitude": -97.0838,
    },
    "Washington Nationals": {
        "FieldName" : "Nationals Park",
        "Type": "Outdoor",
        "Latitude": 38.8730,
        "Longitude": -77.0074,
    },
}
date = str(date.today())
sportsbook = input("Enter Sports Books: ")
start_date = start_season=date.year-3
end_date = end_season=date.year-1
API_KEY = "YOUR_API_KEY"


# Helper functions to fetch data, perform analysis, and prepare data
def fetch_team_data(date):
    # Get the schedule and record for the specified date
    schedule = bs.schedule_and_record(date)
    
    if len(schedule) > 0:
        # Get the teams playing on the specified date
        teams = schedule['home_team'].tolist() + schedule['away_team'].tolist()

        # Fetch team batting and pitching data for the last 3 years
        team_data = {}
        for team in teams:
            team_batting_data = bs.team_batting(team, start_season=date.year-3, end_season=date.year-1)
            team_pitching_data = bs.team_pitching(team, start_season=date.year-3, end_season=date.year-1)
            team_data[team] = {"batting": team_batting_data, "pitching": team_pitching_data}

        return team_data
    else:
        print(f"No games found on {date}.")
        return None

def fetch_weather_data(api_key, latitude, longitude, start_date, end_date, date):

    # Code to fetch weather forecasting and analysis
    base_url = "https://api.climacell.co/v3/weather/historical/station"
    headers = {"apikey": api_key}
    
    # Create a list to store the weather data for each day
    weather_data = []
    
    # Generate a list of dates between the start and end date
    date_range = pd.date_range(start_date, end_date)
    
    for date in date_range:
        # Format the date as 'YYYY-MM-DD' string
        date_str = date.strftime(date)
        
        # Create the API URL for the specific date
        url = f"{base_url}/{latitude},{longitude}/daily/{date_str}"
        
        # Make the API request
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract the relevant weather data from the response
            data = response.json()
            
            # Append the weather data to the list
            weather_data.append(data)
    
    return weather_data
    pass

def clean_weather_data(weather_data):
    # Create an empty DataFrame to store the cleaned data
    cleaned_data = pd.DataFrame()
    
    # Extract the relevant weather attributes from each day's data
    for data in weather_data:
        date = data["observation_time"]["value"]
        temperature = data["temperature"]["value"]
        precipitation = data["precipitation"]["value"]
        humidity = data["humidity"]["value"]
        wind_speed = data["wind_speed"]["value"]
        
        # Create a dictionary for the day's weather data
        day_data = {
            "date": date,
            "temperature": temperature,
            "precipitation": precipitation,
            "humidity": humidity,
            "wind_speed": wind_speed
        }
        
        # Append the day's data to the DataFrame
        cleaned_data = cleaned_data.append(day_data, ignore_index=True)
    
    return cleaned_data
    pass

def clean_player_data(player_data):
    pass

def clean_betting_data(betting_lines):
    pass

def merge_data(data1, data2, data3):
    merged_data = pd.merge(data1, data2, data3, on='common_column')
    return merged_data

def clean_data(player_data, weather_data, betting_lines):
    
    clean_weather_data(weather_data)

    clean_betting_data(betting_lines)

    clean_player_data(player_data)

    pass

def fetch_betting_lines(sportsbook):
    # Code to fetch daily sports betting lines
    url = f"https://api.oddsshark.com/odds?source={sportsbook}&region=us"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Extract the betting lines from the response
        data = response.json()
        betting_lines = data.get('data')
        
        if betting_lines:
            # Convert the betting lines into a pandas DataFrame
            df = pd.DataFrame(betting_lines)
            
            # Drop irrelevant columns and clean the data
            df = df.drop(['updated', 'source', 'region'], axis=1)
            df = df.dropna()
            
            # Convert team names to categorical labels using LabelEncoder
            le = LabelEncoder()
            df['team1'] = le.fit_transform(df['team1'])
            df['team2'] = le.transform(df['team2'])
            
            return df
        else:
            print("No betting lines found.")
            return None
    else:
        print(f"Request failed with status code: {response.status_code}.")
        return None
    pass

def prepare_data(player_data, weather_data, betting_lines):
    # Code to preprocess and merge the data
    merge_data = merge_data(player_data, weather_data, betting_lines)
    # Code to clean the data
    clean_data = clean_data(player_data, weather_data, betting_lines)
    
    pass

def find_top_bets(predictions_xgb, predictions_tf, betting_lines):
    # Code to identify top bets based on predictions and betting lines
    pass

# Fetch team data for the games
team_data = fetch_team_data(date)

# Fetch weather forecasting and analysis for the games
schedule = bs.schedule_and_record(date)
    
if len(schedule) > 0:
    # Get the teams playing on the specified date
    teams = schedule['home_team'].tolist()
    api_key = "API_KEY"

    # Make a list to store the weather data
    weather_data = []
    # loop for all teams
    for team in teams:
        longitude = stadiums["team"]["longitude"]
        latitude = stadiums["team"]["latitude"]
        weather_data = weather_data.append(fetch_weather_data(api_key, latitude, longitude, start_date, end_date, date))
    


# Fetch daily sports betting lines from a web source
betting_lines = fetch_betting_lines(sportsbook)

# Clean data for preparation
cleaned_data = clean_data()

# Prepare the data for modeling
data = prepare_data(team_data, weather_data, betting_lines)

# Train XGBoost model
xgb_model = xgb.train(params, dtrain)

# Train TensorFlow model
tf_model = tf.train.Model(...)

# Make predictions
predictions_xgb = xgb_model.predict(data)
predictions_tf = tf_model.predict(data)

# Identify top bets based on predictions and betting lines
top_bets = find_top_bets(predictions_xgb, predictions_tf, betting_lines)

# Place bets or provide recommendations based on the top bets

