import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import random


# Path to the ChromeDriver executable
chrome_driver_path = 

try:
    # Set up the WebDriver
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    
    # NRL URLs 
    sharks = 'https://www.nrl.com/players/?competition=111&team=500028'
    bulldogs = 'https://www.nrl.com/players/?competition=111&team=500010'
    dolphins = 'https://www.nrl.com/players/?competition=111&team=500723'
    eels = 'https://www.nrl.com/players/?competition=111&team=500031'
    panthers = 'https://www.nrl.com/players/?competition=111&team=500014'
    raiders = 'https://www.nrl.com/players/?competition=111&team=500013'
    sea_eagles = 'https://www.nrl.com/players/?competition=111&team=500002'
    storm = 'https://www.nrl.com/players/?competition=111&team=500021'
    warriors = 'https://www.nrl.com/players/?competition=111&team=500032'
    broncos = 'https://www.nrl.com/players/?competition=111&team=500011'
    cowboys = 'https://www.nrl.com/players/?competition=111&team=500012'
    dragons = 'https://www.nrl.com/players/?competition=111&team=500022'
    knights = 'https://www.nrl.com/players/?competition=111&team=500003'
    rabbitohs = 'https://www.nrl.com/players/?competition=111&team=500005'
    roosters = 'https://www.nrl.com/players/?competition=111&team=500001'
    titans = 'https://www.nrl.com/players/?competition=111&team=500004'
    west_tigers = 'https://www.nrl.com/players/?competition=111&team=500023'
    NRL_URL = [sharks, bulldogs, dolphins, eels, panthers, raiders, sea_eagles, storm, warriors, broncos, cowboys, dragons, knights, rabbitohs, roosters, titans, west_tigers]
    
    
    # Initialize an empty list to store player URLs
    hrefs = []

    try:
        # Loop through each team URL
        for url in NRL_URL:
                # Open the URL
            driver.get(url)

            # Wait for the page to load and JavaScript to execute
            time.sleep(random.uniform(2, 5))  # Adjust based on your connection speed

            # Find all elements with the specified class name
            player_links = driver.find_elements(By.CLASS_NAME, 'card-themed-hero-profile')

            # Extract href attributes
            hrefs.extend([link.get_attribute('href') for link in player_links])

            time.sleep(random.uniform(1, 3))

        if hrefs:
            print(f'{len(hrefs)} URLs found')
        else:
            print('No href attributes found in the player links.')

    finally:
        # Close the WebDriver
        driver.quit()

except Exception as e:
    print(f"An error occurred: {e}")

# Define headers to mimic a browser request
headers_browser = {
    'User-Agent': 
}

# Connect to the database
database_type = 'mysql'
database_driver = 'mysqlconnector'
username = 'root'
password = 
host = 'localhost'
port = '3306'
database_name = 'nrl_data'

create_table_query = '''
CREATE TABLE IF NOT EXISTS playerattributes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UrlID VARCHAR(200),
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    TeamName VARCHAR(100),
    Position VARCHAR(100),
    Height VARCHAR(50),
    DateofBirth VARCHAR(50),
    Weight VARCHAR(50),
    BirthPlace VARCHAR(100),
    Age VARCHAR(50),
    Nickname VARCHAR(100),
    DebutClub VARCHAR(50),
    DebutDate VARCHAR(50),
    OppositionClub VARCHAR(100),
    RoundDebut VARCHAR(100),
    PreviousClub VARCHAR(100),
    JuniorClub VARCHAR(100), 
    UNIQUE (UrlID)
);'''
engine = create_engine(f'{database_type}+{database_driver}://{username}:{password}@{host}:{port}/{database_name}')

with engine.connect() as connection:
    connection.execute(text(create_table_query))


#create a list
all_player_data = []
# Loop through each player URL
for player_url in hrefs:
    response = requests.get(player_url, headers=headers_browser)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the player's name
        player_name_element = soup.find('h1', class_='club-card__title club-card__title--alt club-card__title--pt-large')
        if player_name_element:
            full_name = player_name_element.text.strip()
            names = full_name.split()
            if len(names) > 1:
                first_name = names[0]
                last_name = ' '.join(names[1:])
            else:
                first_name = names[0]
                last_name = ''
        else:
            first_name = None
            last_name = None

        # Extract position
        player_position_element = soup.find('p', class_='club-card__position')
        player_position = player_position_element.text.strip() if player_position_element else None
        
        # Extract team name
        img_tag = soup.find('img', class_='club-card__logo-svg')
        team_name = img_tag['alt'] if img_tag and 'alt' in img_tag.attrs else None

        headers_player_attributes = ['Height:', 'Date of Birth:', 'Weight:', 'Birthplace:', 'Age:', 'Nickname:', 
           'Debut Club:', 'Date:', 'Opposition:', 'Round:', 'Previous Club:', 'Junior Club:']

        default_values = { 
        'Height:': None,
        'Date of Birth:': None,
        'Weight:': None,
        'Birthplace:': None,
        'Age:': None,
        'Nickname:': None,
        'Debut Club:': None,
        'Date:': None,
        'Opposition:': None,
        'Round:': None,
        'Previous Club:': None,
        'Junior Club:': None
        }

        # Simulate extracted player attributes data
        player_attributes_data = [dd for dd in soup.find_all('dd') if 'card-profile-stat__value' not in dd.get('class', [])]
        player_attributes_data_list = [attr.text.strip() for attr in player_attributes_data] if player_attributes_data else []

        if len(player_attributes_data_list) < 12:
            # Populate the dictionary with extracted data, using default values for the rest
            player_data = {
                'UrlID': player_url,
                'FirstName': first_name if len(first_name) <= 100 else None,
                'LastName': last_name if len(last_name) <= 100 else None,
                'Position': player_position if len(player_position) <= 100 else None,
                'TeamName': team_name if len(team_name) <= 100 else None,
                'Height': None,
                'DateofBirth': None,
                'Weight': None,
                'BirthPlace': None,
                'Age': None,
                'Nickname': None,
                'DebutClub': None,
                'DebutDate': None,
                'OppositionClub': None,
                'RoundDebut': None,
                'PreviousClub': None,
                'JuniorClub': None
            } 
        # Create a dictionary for the player's data
        else:
            # Update the default values with actual data if available
            for key, value in zip(headers_player_attributes, player_attributes_data_list):
                default_values[key] = value
                #print(default_values)
            # Populate the dictionary with extracted data, using default values where applicable
            # Populate the dictionary with checked values
            def replace_dash_with_none(value):
                return None if value == '-' else value
            player_data = {
                'UrlID': player_url,
                'FirstName': replace_dash_with_none(first_name) if len(first_name) <= 100 else None,
                'LastName': replace_dash_with_none(last_name) if len(last_name) <= 100 else None,
                'Position': replace_dash_with_none(player_position) if len(player_position) <= 100 else None,
                'TeamName': replace_dash_with_none(team_name) if len(team_name) <= 100 else None,
                'Height': replace_dash_with_none(default_values['Height:']) if len(default_values['Height:']) <= 100 else None,
                'DateofBirth': replace_dash_with_none(default_values['Date of Birth:']) if len(default_values['Date of Birth:']) <= 100 else None,
                'Weight': replace_dash_with_none(default_values['Weight:']) if len(default_values['Weight:']) <= 100 else None,
                'BirthPlace': replace_dash_with_none(default_values['Birthplace:']) if len(default_values['Birthplace:']) <= 100 else None,
                'Age': replace_dash_with_none(default_values['Age:']) if len(default_values['Age:']) <= 100 else None,
                'Nickname': replace_dash_with_none(default_values['Nickname:']) if len(default_values['Nickname:']) <= 100 else None,
                'DebutClub': replace_dash_with_none(default_values['Debut Club:']) if len(default_values['Debut Club:']) <= 100 else None,
                'DebutDate': replace_dash_with_none(default_values['Date:']) if len(default_values['Date:']) <= 100 else None,
                'OppositionClub': replace_dash_with_none(default_values['Opposition:']) if len(default_values['Opposition:']) <= 100 else None,
                'RoundDebut': replace_dash_with_none(default_values['Round:']) if len(default_values['Round:']) <= 100 else None,
                'PreviousClub': replace_dash_with_none(default_values['Previous Club:']) if len(default_values['Previous Club:']) <= 100 else None,
                'JuniorClub': replace_dash_with_none(default_values['Junior Club:']) if len(default_values['Junior Club:']) <= 100 else None
                }

            # Check if the player already exists in the database
        with engine.connect() as connection:
            query = text('SELECT COUNT(*) FROM playerattributes WHERE UrlID = :url AND FirstName = :first AND LastName = :last AND TeamName = :team')
            result = connection.execute(query, {'url':player_url, 'first': first_name, 'last': last_name, 'team': team_name})
            player_exists = result.scalar() > 0

        if player_exists:
            print(f'Player {full_name} already exists in the database.')
        else:
            print(f'Successfully created player profile for {full_name}.')
            all_player_data.append(player_data)


#Create Data frame for player data   
player_df = pd.DataFrame(all_player_data)

# Insert into database
if not player_df.empty:
    try:
        player_df.to_sql('playerattributes', engine, if_exists='append', index=False)
        print(f"Inserted data for {full_name}")
    except SQLAlchemyError as e:
        print(f'Error inserting data for {full_name}: {e}')
else:
    print('No new player data to insert')

