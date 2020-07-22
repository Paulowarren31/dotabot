import discord
import requests

client = discord.Client()

# maps discord account ID to steam32 ID
discord_steam_mapping = {81786922485153792 : '69264271', 81787338308452352 : '78187819', 81887508924731392: '104785056', 161935984542482432: '326513851', 175439973288247296: '209646309'}

def get_last_hits_per_ten(last_hits_per_min):
  idx = 10
  result = []
  while idx < len(last_hits_per_min):
      result.append(last_hits_per_min[idx])
      idx += 10
  return result

def add_steam_mapping(discord_id, steam_id):
    discord_steam_mapping[discord_id] = steam_id

def get_match_info(match_id):
    link = 'https://api.opendota.com/api/matches/' + match_id
    res = requests.get(link)
    if res:
        json_res = res.json()
        return json_res
    return None

def create_result_string(mentioned_user, game):
    kills = str(game['kills'])
    deaths = str(game['deaths'])
    assists = str(game['assists'])

    xpm = str(game['xp_per_min'])
    gpm = str(game['gold_per_min'])

    match_info = get_match_info(str(game['match_id']))
    player_match_info = match_info['players'][game['player_slot']]
    
    gold = str(player_match_info['gold'] + player_match_info['gold_spent'])
    hero_damage = str(player_match_info['hero_damage'])
    last_hits = str(player_match_info['last_hits'])

    last_hits_per_ten = get_last_hits_per_ten(player_match_info['lh_t'])

    seconds = abs(player_match_info['duration'])
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    result_string = mentioned_user.display_name + '\n' # + ' DID THEY FEED? \n'
    #result_string += str(hours) + ':' + str(minutes) + ':' + str(seconds) + '\n'
    result_string += kills + '/' + deaths + '/' + assists + '\n'
    result_string += 'Gold: ' + gold + '\n'
    result_string += 'GPM: ' + gpm + ' XPM: ' + xpm + '\n'
    result_string += 'LH: ' + last_hits_per_ten.join('/') + '\n'
    #result_string += 'Hero Damage: ' + hero_damage + '\n'

    return result_string

def get_latest_game(steam_id):
    link = 'https://api.opendota.com/api/players/' + steam_id + '/recentMatches'
    res = requests.get(link)
    if res:
        json_res = res.json()
        return json_res[0]
    return None

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.endswith('feed?'):
        if '@' in message.content and len(message.mentions) == 1:
            mentioned_user = message.mentions[0]
            game = get_latest_game(discord_steam_mapping[mentioned_user.id])
            if (game):
                await message.channel.send(create_result_string(mentioned_user, game))

#client.run('NzM1NTM4MTg1NTk3MDkxOTcx.XxiZLw.0-VjH7eYBOnbhIUZMUQcEUyMAWc')

