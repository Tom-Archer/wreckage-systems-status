import os
import random
import tweepy
import urllib.request
from datetime import datetime
from yaml import load, Loader

TWEET = False

def get_current_system():
    """Returns the currently playing system name."""  
    req = urllib.request.Request('https://data.65daysofstatic.com/wreckage/log.txt')
    req.headers['Range'] = 'bytes=%s-%s' % (0, 150)
    
    try:
        with urllib.request.urlopen(req) as resp:
            lines = resp.readlines()
            system_raw = lines[3].decode('ascii').strip()
            system_pos = system_raw.find('|') + 2
            return system_raw[system_pos:]
    except:
        return ""

def get_system_meta_data(system_data, system):
    """Returns the specified system's meta-data."""
    if system in system_data.keys():
        
        meta_data_list = system_data[system]
        
        if len(meta_data_list) > 0:
            meta_data_index = random.randrange(len(meta_data_list))
            meta_data_string = meta_data_list[meta_data_index]
            return "// {0}".format(meta_data_string)

    return ""

def send_tweet(dir, system, meta_data):
    # Construct the tweet    
    tweet_string = """{0} // Now playing the '{1}' system {2}

https://www.youtube.com/65PROPAGANDA/LIVE"""
    tweet_string = tweet_string.format(datetime.now().strftime("%H:%M"), system, meta_data)        
    print(tweet_string)
        
    # Load Config
    with open(os.path.join(dir, "config.yaml"), "r") as config_file:
        config_data = load(config_file, Loader=Loader)
    
        try:
            # Authenticate Tweepy
            auth = tweepy.OAuth1UserHandler(
               config_data["consumer_key"],
               config_data["consumer_secret"],
               config_data["access_token"],
               config_data["access_token_secret"]
            )

            api = tweepy.API(auth)
            api.verify_credentials()
            
            # Tweet
            if (TWEET):
                status = api.update_status(tweet_string)
        except:
            print("Error attempting to tweet")

if __name__ == "__main__":
    # Get CWD
    dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load Systems
    system_data = {}
    with open(os.path.join(dir, "systems.yaml"), "r") as systems_file:
        system_data = load(systems_file, Loader=Loader)
        
    # Get the current system and its meta-data (if available)
    system = get_current_system()
    meta_data = get_system_meta_data(system_data, system)
    
    if system != "":
        # Get the last reported system
        last_reported_system = ""
        with open(os.path.join(dir, "system.txt"), "r") as last_system_file:
            last_reported_system = last_system_file.readline()

        if system != last_reported_system:    
            # Send the tweet
            send_tweet(dir, system, meta_data)

        # Write the current system to file
        with open(os.path.join(dir, "system.txt"), "w") as last_system_file:
            last_system_file.write(system)
