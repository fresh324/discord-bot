import discord
import os
import json
from keep_alive import keep_alive
keep_alive()

CHANNEL_NAME = "🐦┃листування"
REQUIRED_ROLE_ID = 1152566528907149342

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

config = load_config()
TRACKED_GAMES = config.get("tracked_games", [])
TRACKED_ARTISTS = config.get("tracked_artists", [])

user_activities = {}

intents = discord.Intents.default()
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

def check_artists(activity_artist):
    if activity_artist in TRACKED_ARTISTS:
        return activity_artist
    if ';' in activity_artist:
        activity_artist_list = activity_artist.split(';')
        for artist in activity_artist_list:
            if artist.strip() in TRACKED_ARTISTS:
                return artist.strip()
    return None
  
@client.event
async def on_ready():
    print(f'{client.user} is Online :)')

@client.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    required_role = discord.utils.get(after.roles, id=REQUIRED_ROLE_ID)
    if not required_role:
        return
        
    channel = discord.utils.get(after.guild.text_channels, name=CHANNEL_NAME)

    current_game = None
    current_music = None
    for activity in after.activities:
        if activity.type == discord.ActivityType.playing:
            current_game = activity.name
            break
        elif activity.type == discord.ActivityType.listening:
            current_music = check_artists(activity.artist)
            break

    previous_game = user_activities.get(after.id, {}).get('game')
    previous_music = user_activities.get(after.id, {}).get('music')
        
    if after.activities and channel is not None:
        for activity in after.activities:

            if current_music and current_music in TRACKED_ARTISTS:
                if current_music != previous_music and current_music is not None:
                    if after.id not in user_activities:
                        user_activities[after.id] = {}
                    user_activities[after.id]['music'] = current_music
                    await channel.send(f'{after.mention}, Ви слухаєте **{current_music}**!\n\n' +
                                        ':bangbang: ЦЯ МУЗИКА ВІД РОСІЙСЬКОГО ВИКОНАВЦЯ АБО ВІД ГРОМАДЯН ВОРОЖИХ ДЛЯ УКРАЇНИ ДЕРЖАВ! :bangbang:\n' + 
                                        ':bangbang: Слухати це неприйнятно та аморально по відношенню до ваших співгромадян, котрі гинуть під час російського вторгнення в Україну. :bangbang:')
                    break
            else:
                if after.id in user_activities and 'music' in user_activities[after.id]:
                    del user_activities[after.id]['music']
                    break

            if current_game and current_game in TRACKED_GAMES:
                if current_game != previous_game:
                    if after.id not in user_activities:
                        user_activities[after.id] = {}
                    user_activities[after.id]['game'] = current_game
                    await channel.send(f'{after.mention}, Ви граєте у **{current_game}**!\n\n' +
                                        ':bangbang: ЦЯ ГРА ВІД РОСІЙСЬКОГО ВИДАВЦЯ АБО ВІД ГРОМАДЯН ВОРОЖИХ ДЛЯ УКРАЇНИ ДЕРЖАВ! :bangbang:\n' +
                                        ':bangbang: Грати в це неприйнятно та аморально по відношенню до ваших співгромадян, котрі гинуть під час російського вторгнення в Україну. :bangbang:')
                    break
            else:
                if after.id in user_activities and 'game' in user_activities[after.id]:
                    del user_activities[after.id]['game']
                    break


client.run(os.environ.get('TOKEN'))
