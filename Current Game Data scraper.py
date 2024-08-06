import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError	
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import random

#connect to database
database_type = 'mysql'
database_driver = 'mysqlconnector'
username = 'root'
password = 'hokeyP0key1'
host = 'localhost'
port = '3306'
database_name = 'nrl_data'

create_table = ''' CREATE TABLE IF NOT EXISTS currentgamedata (
    gameid SERIAL PRIMARY KEY,
    UrlID VARCHAR (200),
    round VARCHAR(10),
    opponent VARCHAR(50),
    score VARCHAR(10),
    position VARCHAR(20),
    minutes_played INT,
    tries INT,
    goals VARCHAR(200),
    one_point_field_goals INT,
    two_point_field_goals INT,
    points INT,
    kicking_metres INT,
    forced_dropouts INT,
    try_assists INT,
    linebreaks INT,
    tackle_breaks INT,
    post_contact_metres INT,
    offloads INT,
    receipts INT,
    tackles_made INT,
    missed_tackles INT,
    total_running_metres INT,
    hit_up_running_metres INT,
    kick_return_metres INT,
    FOREIGN KEY (UrlID) REFERENCES playerattributes(UrlID)
);'''
engine = create_engine(f'{database_type}+{database_driver}://{username}:{password}@{host}:{port}/{database_name}')

with engine.connect() as connection:
    connection.execute(text(create_table))


chrome_driver_path = "C:/Users/Natha/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"

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


headers_browser = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
required_headers = ['UrlID',
    'Round', 'Opponent', 'Score', 'Position', 'Minutes_Played', 'Tries', 'Goals', 
    'One_Point_Field_Goals', 'Two_Point_Field_Goals', 'Points', 'Kicking_Metres', 
    'Forced_Dropouts', 'Try_Assists', 'Linebreaks', 'Tackle_Breaks', 
    'Post_Contact_Metres', 'Offloads', 'Receipts', 'Tackles_Made', 
    'Missed_Tackles', 'Total_Running_Metres', 'Hit_Up_Running_Metres', 
    'Kick_Return_Metres'
]
# Initialize an empty DataFrame to hold all player data
all_player_data_df = pd.DataFrame(columns=required_headers)

#Loop through all player URLs to extract data
for url in hrefs:
    response = requests.get(url, headers=headers_browser)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        target_header_text = " 2024 Season - By Round "

# Find all sections (or other container elements) in the page
        sections = soup.find_all('section')

        # Loop through each section to check if it contains the target header text
        for section in sections:
            header = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if header and target_header_text in header.get_text():
                table_current2024_game_data = soup.find('table')
                if table_current2024_game_data:
                    tbody = table_current2024_game_data.find('tbody')
                    rows = []
                    for tr in tbody.find_all('tr'):
                        cells = [td.get_text(strip=True) for td in tr.find_all('td') if 'table-tbody__td--divider' not in td['class'] and 
                        ('aria-hidden' not in td.attrs or td['aria-hidden'] != 'true') and 
                        not (td.find('span', class_='o-team-form-icon') and 'aria-hidden' in td.find('span', class_='o-team-form-icon').attrs)]
                        #Change'-' to none
                        cells = ['0' if cell == '-' else cell for cell in cells]
                        cells.insert(0, url)
                        #Correct tables with missing data
                        if len(cells) == 23:
                            cells.insert(13, '0')
                        
                        if len(cells) == 22:
                            cells.insert(12, '0')
                            cells.insert(13, '0')
                        
                        if len(cells) == 24:
                            rows.append(cells)
                        else:
                            print(f'{url} is missing current table data')
                        
                    try:
                        current_player_data_df = pd.DataFrame(rows, columns=required_headers)
                        
                        # Append the current URL's data to the main DataFrame
                        all_player_data_df = pd.concat([all_player_data_df, current_player_data_df], ignore_index=True)
                    
                    except ValueError as e:
                        print(f"Error creating DataFrame for {url}: {e}")

print(all_player_data_df)
if not all_player_data_df.empty:
    try:
        all_player_data_df.to_sql('currentgamedata', engine, if_exists='append', index=False)
        print(f'Successfully inserted data to currentgamedata. {len(rows)} inserted into table.')
    except SQLAlchemyError as e:
        print(f'Error inserting data {e} {url}')
else:
    print('No new data to insert')