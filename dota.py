import discord
import requests

client = discord.Client()

# maps discord account ID to steam32 ID
discord_steam_mapping = {81786922485153792 : '69264271', 81787338308452352 : '78187819'}

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
    
    gold = str(player_match_info['gold'])
    hero_damage = str(player_match_info['hero_damage'])
    last_hits = str(player_match_info['last_hits'])

    result_string = mentioned_user.display_name + ' DID THEY FEED? \n'
    result_string += '(K/D/A): ' +  kills + '/' + deaths + '/' + assists + '\n'
    result_string += 'GPM: ' + gpm + ' XPM: ' + xpm + '\n'
    result_string += 'Last hits: ' + last_hits + '\n'
    result_string += 'Hero damage: ' + hero_damage + '\n'
    result_string += 'gold: ' + gold + '\n'

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

client.run('NzM1NTM4MTg1NTk3MDkxOTcx.XxhuGQ.epwuuKhQUvhOnYZkifRy4HBP1Yg')

