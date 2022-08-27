
#special thanks to knowledge bas ehttps://dev.to/arvindmehairjan/how-to-play-spotify-songs-and-show-the-album-art-using-spotipy-library-and-python-5eki
# Import libraries
import os
import sys
import json
import spotipy
import webbrowser
import random
from datetime import datetime
import time
import spotipy.util as util
import numpy as np
import wave
import pyaudio
from json.decoder import JSONDecodeError

#prints all info on current user playlists
# def print_playlists():
#     playlists = so.current_user_playlists()
#     while playlists:
#         for i, playlist in enumerate(playlists['items']):
#             print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
#         if playlists['next']:
#             playlists = so.next(playlists)
#         else:
#             playlists = None

# USER TODO
#[name, uri, weight, curr #of songs (-1) for unknown]
playlists_w_weights = [ 
["El Cubano", "7qikzKfqJdOQgP0YHlFSls", 0.1, -1],
["Americana", "2G7FjozlMIAir9S9ZFyGIG", 0.2, -1],
["Of Rock and Cock", "57UfI4zdo2Y9kxCoD6NUbI", 0.2, -1],
["Bang Boopidy", "6KlZBvTVRrbyZaffKQkqgt", 0.15, -1 ],
["Nick Sick Jams", "0JxK9Ppv4HgYR6aFn1AdpI", 0.35, -1],
]

#creates an array that is filled with indexs of playlists, then it shuffles it
def get_weighted_vector(playlists):
    arr = []
    for pl_index in range(0, len(playlists)):
        for i in range(0, int(playlists_w_weights[pl_index][2]*100)):
            arr.append(pl_index)
    random.shuffle(arr)
    return arr;
def get_wait_time(queue, num_songs_to_play):
    # TODO this is so bad
    curr_info = so.current_playback()
    #seconds into the song
    progress = int(curr_info["progress_ms"] / 1000)
    song_len = int(curr_info["item"]["duration_ms"] / 1000)
    remaining = song_len - progress
    mult_fact = -1
    for i in range(0,num_songs_to_play):
        if ( queue[i]["uri"] ==  curr_info ["item"]["uri"]):
            mult_fact = (num_songs_to_play - 1) - i
    if mult_fact == -1:
        print("Unecpected error bub, shihh")
        return 0
    # a song is at least 2 mins so if first song, wait 3 (songs) * 120 (mins) until next tally
    return remaining  + (120 * mult_fact)

def play_four_songs(device, playlist):
    num_songs_to_play = 2
    # #FIX ME : Add timer to know when a song ends/ add to queue/ figure out when 4 songs play and exit this function
    # #so.start_playback(device, context_uri=playlist[1])
    # #tracks = (tracks['items'])[:]['track']['uri']
    #how much time are u willin to sacrifice boy!
    # fr tho is a sleep timer, if the time left in queued is less than this then we will exit the funciton and go to commercial TODO this bad
    min_cutoff_time = 10
    print("Playing " + playlist[0])
    # pl = so.playlist(playlist[1], fields='name, total')

    #gets size of playlist if not done previously
    if playlist[3] == -1:
        print("Getting size of playlist:" + playlist[0])
        playlist[3] = so.playlist_items(playlist[1], fields='total')['total']
    total_tracks = playlist[3]
    # while results['next']:
    #     results = so.next(results)
    #     tracks.extend(results['items'])
    #print(json.dumps(tracks[2], sort_keys=True, indent=4))
    print("TOTAL TRACKS IN " + playlist[0] + " = " + str(total_tracks) + ". selecting " + str(num_songs_to_play))
    #get four random tracks:
    queue = []
    for i in range(0,num_songs_to_play):
        randTrack = so.playlist_tracks(playlist[1], fields='items.track.uri, items.track.name', offset=random.randint(0,total_tracks), limit=1)["items"][0]["track"]
        print(json.dumps(randTrack, sort_keys=True, indent=4))
        queue.append(randTrack)
        print("adding uri" + randTrack["uri"])
        so.add_to_queue(randTrack["uri"])
        #this is the least efficient thing in the world lmao 
        print("new queue = " + str (queue[i]["name"]))
    # set timout to many seconds
    timeout = min_cutoff_time + 42 #teehee
    curr_song = so.current_playback()["item"]
    while curr_song["uri"] != queue[0]["uri"]:
        print(" found " +  curr_song["name"] +" wanted " + queue[0]["name"] )
        so.next_track()
        time.sleep(1)
        #make sure we don't skip past it by waiting for 'next' to update
        new_curr = so.current_playback()["item"]
        while new_curr["uri"] == curr_song["uri"]:
            time.sleep(1)
            new_curr = so.current_playback()["item"]
        curr_song = new_curr
    while timeout > min_cutoff_time:
        timeout = get_wait_time(queue, num_songs_to_play)
        now = datetime.now()
        print("time is " + now.strftime("%H:%M:%S") + " going to sleep for " + str(timeout) + " secs")
        time.sleep(timeout)
        now = datetime.now()
        print("time is "+ now.strftime("%H:%M:%S") + " welcome back! yes this is return msg" )
    so.pause_playback()

    #print(json.dumps(pl, sort_keys=True, indent=4))

   # print(json.dumps(pl, sort_keys=True, indent=4))


    # results = so.playlist_items(playlist[1], fields="tracks.items(track(name,uri))")
    # print(json.dumps(results, sort_keys=True, indent=4))
def play_audio(path):
    wf=wave.open(path)
    p=pyaudio.PyAudio()
    stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)
    data=wf.readframes(1024)
    
    while len(data)>0:
        stream.write(data)
        data=wf.readframes(1024)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    return

# Get the username from terminal
# USER TODO
username = "22wzwygbnvq6kdhjhrh4oajhy"
scope = 'user-read-private user-read-playback-state user-modify-playback-state'

try:
    token = util.prompt_for_user_token(username, scope)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope)


# Create Spotify object
so = spotipy.Spotify(auth=token)
weighted_vector = get_weighted_vector(playlists_w_weights)
print(weighted_vector)

#get device
#devices
devices = so.devices()
print(json.dumps(devices, sort_keys=True, indent=4))
deviceID = devices['devices'][0]['id']
#so.shuffle(True, deviceID)
# for i in range(0, len(weighted_vector)):
ads_dir = "./sample_ads"
for i in range(0, len(weighted_vector)):
    play_audio(ads_dir + "/" +random.choice(os.listdir(ads_dir)))
    play_four_songs(deviceID, playlists_w_weights[weighted_vector[i]])
    play_audio(ads_dir + "/" + random.choice(os.listdir(ads_dir)))

