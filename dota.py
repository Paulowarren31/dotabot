import discord
import requests

client = discord.Client()

# maps discord account ID to steam32 ID
discord_steam_mapping = {81786922485153792 : '69264271', 81787338308452352 : '78187819', 81887508924731392: '104785056', 161935984542482432: '326513851', 175439973288247296: '209646309'}

hero_map = {}

def populate_hero_map():
  link = 'https://api.opendota.com/api/heroes'
  res = requests.get(link)
  if res:
    heroes = res.json()
    for hero in heroes:
      hero_map[hero['id']] = hero['localized_name']
    print('populated hero map')

def get_last_hits_per_ten(last_hits_per_min):
  if last_hits_per_min is not None:
    idx = 10
    result = []
    while idx < len(last_hits_per_min):
        result.append(last_hits_per_min[idx])
        idx += 10
    result = [str(val) for val in result]
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
    player_idx = game['player_slot']
    if player_idx >= 128:
        player_idx -= 123
    player_match_info = match_info['players'][player_idx]

    
    hero_id = player_match_info['hero_id']
    hero_name = hero_map[hero_id]
    
    gold = str(player_match_info['gold'] + player_match_info['gold_spent'])
    hero_damage = str(player_match_info['hero_damage'])
    last_hits = str(player_match_info['last_hits'])

    last_hits_per_ten = get_last_hits_per_ten(player_match_info['lh_t'])

    seconds = abs(player_match_info['duration'])
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    player_name = str(player_match_info['personaname'])

    result_string = player_name + ' (' + hero_name + ')' + '\n' # + ' DID THEY FEED? \n'
    #result_string += str(hours) + ':' + str(minutes) + ':' + str(seconds) + '\n'
    result_string += kills + '/' + deaths + '/' + assists + '\n'
    result_string += 'Gold: ' + gold + '\n'
    result_string += 'GPM: ' + gpm + ' XPM: ' + xpm + '\n'
    if last_hits_per_ten is not None:
      result_string += 'LH: ' + '/'.join(last_hits_per_ten)[:5] + '\n'
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

populate_hero_map()
client.run('PUT_TOKEN_HERE')

