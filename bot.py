import os
import random
import tweepy
import urllib.request
from datetime import datetime
from yaml import load, Loader

TWEET = True

def get_most_recent_log_string():
    """Returns the most recent entry in the system log."""  
    req = urllib.request.Request('https://data.65daysofstatic.com/wreckage/log.txt')
    req.headers['Range'] = 'bytes=%s-%s' % (0, 150)
    
    try:
        with urllib.request.urlopen(req) as resp:
            lines = resp.readlines()
            if len(lines) > 3:
                return lines[3].decode('ascii').strip()
            else:
                print(datetime.now().strftime("%Y-%m-%d @ %H:%M"), "| Error retrieving log:", lines)
                return ""
    except Exception as e:
        print(datetime.now().strftime("%Y-%m-%d @ %H:%M"), "| Error attempting to connect:", e)
        return ""
    
def get_current_time(log_string):
    """Returns the current time from the log line."""
    time_pos = log_string.find('@') + 2
    return log_string[time_pos:time_pos + 5]
    
def get_current_system(log_string):
    """Returns the currently playing system name from the log line."""
    system_pos = log_string.find('|') + 2
    return log_string[system_pos:]

def get_system_meta_data(system_data, system):
    """Returns the specified system's meta-data."""
    if system in system_data.keys():
        
        meta_data_list = system_data[system]
        
        if len(meta_data_list) > 0:
            meta_data_index = random.randrange(len(meta_data_list))
            meta_data_string = meta_data_list[meta_data_index]
            return "// {0}".format(meta_data_string)

    return ""

def send_tweet(dir, log_time, system, meta_data):
    # Construct the tweet    
    tweet_string = """{0} // Now playing the '{1}' system {2}

https://www.youtube.com/65PROPAGANDA/LIVE"""
    tweet_string = tweet_string.format(log_time, system, meta_data)        
            
    # Load Config
    with open(os.path.join(dir, "config.yaml"), "r") as config_file:
        config_data = load(config_file, Loader=Loader)
     
        if (TWEET):
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
                status = api.update_status(tweet_string)
                return True
            except Exception as e:
                print(datetime.now().strftime("%Y-%m-%d @ %H:%M"), "| Error attempting to tweet:", e)
                print(tweet_string, "\n")
                return False                
        else:
            print(tweet_string, "\n")            
            return True
    
if __name__ == "__main__":
    # Get CWD
    dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load Systems
    system_data = {}
    with open(os.path.join(dir, "systems.yaml"), "r") as systems_file:
        system_data = load(systems_file, Loader=Loader)
        
    # Get the current system and its meta-data (if available)
    log_string = get_most_recent_log_string()
    system = get_current_system(log_string)
    log_time = get_current_time(log_string)
    meta_data = get_system_meta_data(system_data, system)
    
    if system != "":
        # Get the last reported system
        last_reported_system = ""
        with open(os.path.join(dir, "system.txt"), "r") as last_system_file:
            last_reported_system = last_system_file.readline()

        if system != last_reported_system:    
            # Send the tweet
            success = send_tweet(dir, log_time, system, meta_data)
            
            if success:
                # Write the current system to file
                with open(os.path.join(dir, "system.txt"), "w") as last_system_file:
                    last_system_file.write(system)
