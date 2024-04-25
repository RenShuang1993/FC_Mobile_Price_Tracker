import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse
import schedule
import time
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

"""
PROGRAM_TOTY24,
PROGRAM_CENTURIONS24,
PROGRAM_HEROS8,
PROGRAM_MLS24,
PROGRAM_RIVALS24,
PROGRAM_ç,
PROGRAM_WINTERWILD24
"""

def read_players_data(filename):
    players = []
    with open(filename, 'r') as file:
        # Skip the header line
        next(file)
        for line in file:
            # Split each line by comma
            parts = line.strip().split(',')
            # Create a dictionary for each player
            player = {
                "name": parts[0],
                "project": parts[1],
                "ability": int(parts[2]),
                "low_price": int(parts[3]),
                "high_price": int(parts[4]),
                "previous_price": int(0)
            }
            players.append(player)
    return players
# Load player data from a file
players_data = read_players_data('players_data.txt')


def SendEmail(player_text):
    # Configure SMTP server and login credentials
    smtp_server = "smtp.gmail.com"
    port = 587  # Use port 587 for gmail with TLS
    sender_email = "your email"  # Sender's email address
    password = "your code"  # Email password or app-specific password
    # Add email body
    # Create an email object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = "Receiver's email address"  # Receiver's email address
    msg['Subject'] = "fc24 Notification"  # Email subject
    msg.attach(MIMEText(player_text, 'plain'))

    # Create SMTP connection
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Enable TLS
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, msg['To'], text)

    except Exception as e:
        print("email error")


def generate_url(year, query):
    # Base URL part
    base_url = "https://renderz.app/api/search"
    
    # Use urllib.parse.quote_plus to ensure the query string is correctly encoded
    encoded_query = urllib.parse.quote_plus(query)
    
    # Construct the full URL
    full_url = "{}?year={}&query={}".format(base_url, year, encoded_query)
    
    return full_url

def create_url(id_value):
    return "https://renderz.app/24/player/{}/__data.json?x-sveltekit-invalidated=101".format(id_value)

# Traverse the list, find the first dictionary containing 'timestamp'
def find_price(target_list):
    for index, item in enumerate(target_list):
        if isinstance(item, dict) and 'timestamp' in item:

            return index # Stop searching after finding the first one
              
   
def format_player_info(name, price, format_type=1):
    """
    Generate a message text based on the given name, price, and format type.

    Parameters:
    - name: Player's name
    - price: Player's price
    - format_type: Message format type (integer), default is 1

    Returns:
    - Formatted string
    """
    if format_type == 1:
        # Buy low
        return f"Alert: {name} is now priced at {price}!"
    elif format_type == 2:
        # Sell high
        return f"Price Update -> Player: {name}, Current High Price: {price}."
    elif format_type == 3:
        # Message format containing suggestions
        return f"Check out this player: {name}, whose market price has reached {price}. Consider buying now!"
    else:
        # Default message format, if an unknown format_type is passed
        return f"Player {name} has a new price tag of {price}."


def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return the parsed dictionary
    else:
        print("Failed to retrieve data:", response.status_code)
        return None



def check_player_prices():
    for player in players_data:
        year_input = 23
        query_input = player.get("name")
        url = generate_url(year_input, query_input)
        jason_doc = fetch_data(url)
        if jason_doc :
            for player_data in jason_doc:
                
                if player_data.get("name") == query_input and player_data.get("cardUiStyle")== player.get("project") and player_data.get("rating") == player.get("ability") and player_data.get("auctionable"):
                    player_id = player_data.get("id")
                    player_url = create_url(player_id)
                    price_data = fetch_data(player_url)
                    target_list = price_data['nodes'][2]['data']
                    price_index = find_price(target_list)
                    lowPrice_index = target_list[price_index]['lowPrice']
                    highPrice_index = target_list[price_index]['highPrice']
                    RefreshTime_index = target_list[price_index]['nextRefreshTime']
                    lowPrice = target_list[lowPrice_index]
                    highPrice = target_list[highPrice_index]
                    RefreshTime = target_list[RefreshTime_index]
                    schedule_task(RefreshTime)
                    

                    if lowPrice <= player.get("low_price") and lowPrice != player.get("previous_price"):
                        player_text = format_player_info(player.get("name"), lowPrice, format_type=1)
                        player["previous_price"] = lowPrice
                        SendEmail(player_text)
                    if highPrice >= player.get("high_price") and highPrice != player.get("previous_price") :
                        player_text = format_player_info(player.get("name"), lowPrice, format_type=2)
                        player["previous_price"] = highPrice
                        SendEmail(player_text)
                        
def schedule_task(refresh_time):
    # Convert timestamp
    run_time = datetime.fromtimestamp(refresh_time)

    schedule.every().day.at(run_time.strftime('%H:%M')).do(check_player_prices)

def everyday_emal():
    SendEmail("The system is operating normally")



schedule.every().day.at("00:00").do(everyday_emal)

# Schedule the task to run at a specific time every day
schedule.every().day.at("23:00").do(check_player_prices)


# Infinite loop to keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)
