import requests, json, csv
from discordwebhook import Discord
from timecheck import check_new_gw
import os
from transferLoad import sheep_finder, transfer_update,get_gw_transfers_raw, transfer_out_check
from datetime import datetime

os.chdir('/Users/matthewgoodsell/PycharmProjects/FPL')


TEAM_IDS = {'George': 2007048, 'Adam': 403082, 'Matt': 2413634, 'Ashbourne': 2598415, 'Gaz': 2999484, 'Rothwell': 216665, 'Butler': 773116}
BASE_URL = 'https://fantasy.premierleague.com/api/entry/'


def test_flag(test):
    if test:
        return 'https://discord.com/api/webhooks/1149327519577817232/mS_-aOUXJ1RBkCBGPg6z6ZrIU0IciR2NeN-L_WAQoD6cxyt4V_bGNPj8Jd78soLgmnp9', 'https://discord.com/api/webhooks/1149327519577817232/mS_-aOUXJ1RBkCBGPg6z6ZrIU0IciR2NeN-L_WAQoD6cxyt4V_bGNPj8Jd78soLgmnp9'
    else:
        return 'https://discord.com/api/webhooks/1154941840408199249/m6z0m_eVwuTz8dQLTKCEOtSQ3UwX61jrqEiEPMqJ-rFCJfr_kh4Wxi19Ige8wd7ByYMZ', 'https://discord.com/api/webhooks/1149327519577817232/mS_-aOUXJ1RBkCBGPg6z6ZrIU0IciR2NeN-L_WAQoD6cxyt4V_bGNPj8Jd78soLgmnp9'


def send_to_discord(p_name,p_url,p_gk,p_def,p_mid,p_att,p_ben,p_trans,trans_costs,chip, tval, itb, tot):

    discord = Discord(url=DISCORD_URL)
    discord.post(
        embeds=[
                {
                "author": {
                    "name": "Team Update",
                    "url": p_url
                    },
                "color": 5177219,
                "title": f"__**{p_name}s Team**__",
                "fields": [
                    {"name": f"Team Val: {tval}m // ITB: {itb}m // Total: {tot}m", "value": ''},
                    {"name": chip, "value": ''},
                    {"name": f"**Transfers{trans_costs}**", "value": p_trans},
                    {"name": "**GKs**", "value": p_gk},
                    {"name": "**Defenders**", "value": p_def},
                    {"name": "**Midfielders**", "value": p_mid},
                    {"name": "**Forwards**", "value": p_att},
                    {"name": "**Bench**", "value": p_ben},
                    ]

                # "footer": {
                #     "text": "League Link",
                #     "icon_url": "https://fantasy.premierleague.com/leagues/730431/standings/c",
                # },
            }
        ]
    )


def test_to_discord():
    discord = Discord(url=DISCORD_URL1)
    discord.post(content="Check")


def get_full_data():

    full_data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()

    return full_data


def get_full_player_data(full_data):

    full_player_id = {}
    full_team_list = {}

    for team in full_data['teams']:
        full_team_list[team['id']] = {}
        full_team_list[team['id']]['short_name'] = team['short_name']
        full_team_list[team['id']]['name'] = team['name']

    for item in full_data['elements']:

        p_name = item['web_name']
        p_team = full_team_list[item['team']]['short_name']
        p_pos = item['element_type']

        p_id = item['id']
        full_player_id[p_id] = {}
        full_player_id[p_id]['player_name'] = p_name
        full_player_id[p_id]['team_name'] = p_team
        full_player_id[p_id]['position'] = p_pos

    return full_player_id


def get_team_gw_data(team_id, gw):

    x = f"{BASE_URL}{team_id}/event/{gw}/picks/"
    y = requests.get(x).json()

    return y


def get_latest_gw(full_data):

    for gws in full_data['events']:
        if gws['is_current']:
            return gws['id']


def sheep_master(gw,full_data):

    for key in TEAM_IDS:
        y = get_gw_transfers_raw(TEAM_IDS[key])
        transfer_update(y, key, gw)

    sheep_str = sheep_finder(gw,full_data)

    return sheep_str


# def player_percentage(all_gw_team_data):
#     player_picked11 = []
#     player_picked15 = []
#     for keys in all_gw_team_data:
#         y = all_gw_team_data[keys]['picks']
#         for player in y:
#             if player['position'] < 12:
#
#                 if x['player_name'] in player11_count:
#                     player[x['player_name']]['count'] += 1
#                     player[x['player_name']]['lads'].append(keys)
#                 else:
#                     player[x['player_name']] = {}
#                     player[x['player_name']]['count'] = 1
#                     lads = [keys]
#                     player[x['player_name']]['lads'] = lads
#
#             # else:
#             #     if x['player_name'] in player15_count:
#             #         player15_count[x['player_name']] += 1
#             #     else:
#             #         player15_count[x['player_name']] = 1
#
#     print(all_gw_team_data)
#     #
#     # for keys in all_gw_team_data:
#     #     y = all_gw_team_data[keys]['picks']
#     #
#     #     # adding percentage and diff flag to gw data
#     #     for p in y:
#     #         times_picked11 = player11_count[p['player_name']]
#     #
#     #         times_picked15 = player15_count[p['player_name']]
#


def get_gw_transfers(id, gw):
    x = f"https://fantasy.premierleague.com/api/entry/{id}/transfers/"

    return_list = []
    trans_disc = ''
    trans_count = 0

    data = requests.get(x).json()
    for trans in reversed(data):
        if trans['event'] == gw:
            trans_count += 1
            t_in_name = player_names[trans['element_in']]['player_name']
            t_in_team = player_names[trans['element_in']]['team_name']
            t_out_name = player_names[trans['element_out']]['player_name']
            t_out_team = player_names[trans['element_out']]['team_name']
            t_time = datetime.fromisoformat(trans['time'])
            str_time = t_time.strftime("%a ") + t_time.strftime("%I:%M%p").lower()
            trans_disc += f"{str_time} OUT {t_out_name} ({t_out_team}) - IN {t_in_name} ({t_in_team}) \n"

    if trans_disc == '':
        trans_disc = "None"

    return_list.append(trans_disc)
    return_list.append(trans_count)
    return return_list


def differentials(play_dict,full_team_data):
    diff_list = ''

    for x in play_dict:
        if play_dict[x] == 1:
            t_with = ''
            for keys in full_team_data:
                y = full_team_data[keys]['picks']
                for play in y:
                    if play['player_name'] == x and play['position'] < 12:
                        if t_with == '':
                            t_with += f"{keys} "
                        else:
                            t_with += f"& {keys}"

            diff_list += f"{x} - {t_with}\n"

    for x in play_dict:
        if play_dict[x] == 2:
            t_with = ''
            for keys in full_team_data:
                y = full_team_data[keys]['picks']
                for play in y:
                    if play['player_name'] == x and play['position'] < 12:
                        if t_with == '':
                            t_with += f"{keys} "
                        else:
                            t_with += f"& {keys}"

            diff_list += f"{x} - {t_with}\n"

    return diff_list


def discordiff(diff):
    discord = Discord(url=DISCORD_URL)
    discord.post(
        embeds=[
            {
                # "author": {
                #     "name": "Differentials",
                #     },
                "color": 5177219,
                # "title": "__**full list**__",
                "fields": [
                    {"name": f"**Differentials**", "value": diff},
                    ]
            }
        ]
    )


def boring_players(play_dict,full_team_data):
    diff_list = ''

    for x in play_dict:
        if play_dict[x] == 7:
            t_with = ''
            # for keys in full_team_data:
            #     y = full_team_data[keys]['picks']
            #     for play in y:
            #         if play['player_name'] == x and play['position'] < 12:
            #             if t_with == '':
            #                 t_with += f"{keys}"
            #             else:
            #                 t_with += f", {keys}"

            diff_list += f"{x}\n"

    if diff_list == '':
        diff_list = 'None'
    return diff_list


def discorboring(diff):
    discord = Discord(url=DISCORD_URL)
    discord.post(
        embeds=[
            {
                # "author": {
                #     "name": "Differentials",
                #     },
                "color": 5177219,
                # "title": "__**full list**__",
                "fields": [
                    {"name": f"**BORING PlAYERS**", "value": diff},
                    ]
            }
        ]
    )


def discorsheep(sheep):
    discord = Discord(url=DISCORD_URL)
    discord.post(
        embeds=[
            {
                # "author": {
                #     "name": "Sheep Hunter",
                #     },
                "color": 5177219,
                # "title": "__**full list**__",
                "fields": [
                    {"name": f"**BAAAAAAAAA**", "value": sheep},
                    ]
            }
        ]
    )


def check_for_active_chip(team_data):
    if team_data['active_chip'] is None:
        return ''
    else:
        x = team_data['active_chip']
        return f'Chip Active: {x}'


def clear_existing_json():
    open('teams.json', 'w').close()


def write_json(teams):
    json_object = json.dumps(teams, indent=4, ensure_ascii=False)

    with open("teams.json", "w") as outfile:
        outfile.write(json_object)


def transfer_count(lad, tfer_count, wc):

    return_list = []

    with open('teams.json') as user_file:
        parsed_json = json.load(user_file)

    for team in parsed_json:
        if team["lad_name"] == lad:
            team["transfer_count"] += 1
            if wc:
                new_count = team["transfer_count"]
            else:
                if team["transfer_count"] - tfer_count < 0:
                    new_count = 0
                else:
                    new_count = team["transfer_count"] - tfer_count


    new_count_str = str(new_count) + " Left"
    return_list.append(new_count)
    return_list.append(new_count_str)

    return return_list




test = True
discords = test_flag(test)
DISCORD_URL = discords[0]
DISCORD_URL1 = discords[1]

full_data = get_full_data()
gw_trig = check_new_gw(full_data)
test_to_discord()
all_current_gw_data = {}
player11_count = {}
player15_count = {}
teams_full = []


if gw_trig:

    player_names = get_full_player_data(full_data)
    current_gw = get_latest_gw(full_data)
    disc_full = ''

    for key in TEAM_IDS:
        lad = key
        team_id = TEAM_IDS[key]
        curr_team_data = get_team_gw_data(team_id, current_gw)
        team_url = f"https://fantasy.premierleague.com/entry/{team_id}/event/{current_gw}"
        disc_gk = ''
        disc_def = ''
        disc_mid = ''
        disc_for = ''
        disc_sub = ''
        disc_full = ''
        chip = check_for_active_chip(curr_team_data)
        # chip = "Active: wildcard"

        tot = round(float(curr_team_data["entry_history"]["value"])/10, 1)
        itb = round(float(curr_team_data["entry_history"]["bank"])/10, 1)
        t_val = round(tot - itb, 1)


        trans_data = get_gw_transfers(team_id, current_gw)
        play_trans = trans_data[0]
        play_trans_count = trans_data[1]

        if chip == "":
            wc = False
        elif chip[-4:] == "card":
            wc = True
        else:
            wc = False

        play_trans_data = transfer_count(lad, play_trans_count, wc)
        play_trans_count_str = play_trans_data[1]
        play_trans_count_adj = play_trans_data[0]

        if curr_team_data['entry_history']['event_transfers_cost'] > 0:
            trans_costs = ' (-' + str(curr_team_data['entry_history']['event_transfers_cost']) + 'pts, )' + play_trans_count_str
        else:
            trans_costs = f" ({play_trans_count_str})"

        for x in curr_team_data['picks']:

            x['player_name'] = player_names[x['element']]['player_name']
            x['player_team'] = player_names[x['element']]['team_name']
            x['player_pos'] = player_names[x['element']]['position']

            # creating JSON for LIVE-FPL
            if x['position'] == 1:
                teams_full.append(
                    {"lad_name": lad,
                     "transfer_count" : play_trans_count_adj,
                     "team": {
                         "gk": {x['element']: x['player_name']},
                         "df": {},
                         "mf": {},
                         "fw": {},
                         "sub":{}
                     },
                     "captain": ""
                     }

                )
            else:
                for team in teams_full:
                    if team["lad_name"] == lad:
                        if x["position"] > 11:
                            team["team"]["sub"][x['element']] = x['player_name']
                        elif x["element_type"] == 2:
                            team["team"]["df"][x['element']] = x['player_name']
                            if x['is_captain']:
                                team["captain"] = x['player_name']
                        elif x["element_type"] == 3:
                            team["team"]["mf"][x['element']] = x['player_name']
                            if x['is_captain']:
                                team["captain"] = x['player_name']
                        elif x["element_type"] == 4:
                            team["team"]["fw"][x['element']] = x['player_name']
                            if x['is_captain']:
                                team["captain"] = x['player_name']

            if x['is_captain']:
                x['player_name_team'] = f"**{x['player_name']} (C) - {x['player_team']}**"
            elif x['is_vice_captain']:
                x['player_name_team'] = f"{x['player_name']} (VC) - {x['player_team']}"
            else:
                x['player_name_team'] = f"{x['player_name']} - {x['player_team']}"

            if x['position'] < 12:

                # adding player to count
                if x['player_name'] in player11_count:
                    player11_count[x['player_name']] += 1
                else:
                    player11_count[x['player_name']] = 1


                if x['player_pos'] == 1:
                    disc_gk += '\n'
                    disc_gk += x['player_name_team']
                elif x['player_pos'] == 2:
                    disc_def += '\n'
                    disc_def += x['player_name_team']
                elif x['player_pos'] == 3:
                    disc_mid += '\n'
                    disc_mid += x['player_name_team']
                elif x['player_pos'] == 4:
                    disc_for += '\n'
                    disc_for += x['player_name_team']
            else:
                disc_sub += '\n'
                disc_sub += x['player_name_team']


        all_current_gw_data[lad] = curr_team_data
        send_to_discord(lad,team_url,disc_gk,disc_def,disc_mid,disc_for,disc_sub,play_trans,trans_costs,chip, t_val, itb, tot)

    diff_players = differentials(player11_count, all_current_gw_data)
    boring = boring_players(player11_count, all_current_gw_data)
    discordiff(diff_players)
    discorboring(boring)
    discorsheep(sheep_master(current_gw,player_names))
    clear_existing_json()
    write_json(teams_full)


