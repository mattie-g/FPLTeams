import requests, json, csv
from discordwebhook import Discord
from timecheck import check_new_gw
import os
from datetime import datetime
os.chdir('/Users/matthewgoodsell/PycharmProjects/FPL')
TEAM_IDS = {'George': 2007048, 'Adam': 403082, 'Matt': 2413634, 'Ashbourne': 2598415, 'Gaz': 2999484, 'Rothwell': 216665, 'Butler': 773116}
BASE_URL = 'https://fantasy.premierleague.com/api/entry/'

with open('transfers.json') as user_file:
    parsed_json = json.load(user_file)


def get_gw_transfers_raw(id):
    x = f"https://fantasy.premierleague.com/api/entry/{id}/transfers/"
    full_tran = requests.get(x).json()

    return full_tran


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


def transfer_out_check(player,gw,transfer_list):
    in_count = 0
    out_count = 0
    for transfer in transfer_list:
        if transfer["event"] == gw:
            if transfer["element_in"] == player:
                in_count += 1
            elif transfer["element_out"] == player:
                out_count += 1

    if in_count > out_count:
        return False
    else:
        return True


def full_gw_load(tnsf_json, new_json,curr_player):

    raw_data = get_full_data()

    full_player_data = get_full_player_data(raw_data)

    for i in range(1,8):
        for x in tnsf_json:
            if x["event"] == i:
                new_player = False
                for player in new_json:
                    if x["element_in"] == player["player"]:
                        abcd = player["transfers"]
                        new_player = True
                        new_gw = False
                        for gw in abcd:
                            if gw["gw"] == i:
                                new_gw = True
                                transfer_out = transfer_out_check(x["element_in"], i, tnsf_json)

                                if not (curr_player in gw["players"]) and not transfer_out:
                                    gw["players"].append(curr_player)
                                    break

                        transfer_out = transfer_out_check(x["element_in"], i, tnsf_json)
                        if not new_gw and not transfer_out:
                            new_gw_temp = {
                                        "gw": i,
                                        "players": [
                                            curr_player
                                        ]
                                    }
                            abcd.append(new_gw_temp)

                transfer_out = transfer_out_check(x["element_in"], i, tnsf_json)
                if not new_player and not transfer_out:
                    new_player_temp = {
                        "player": x["element_in"],
                        "transfers": [
                            {
                                "gw": i,
                                "players": [
                                    curr_player
                                ]
                            }

                        ]
                    }
                    new_json.append(new_player_temp)


def transfer_update(fpl_json,curr_player, gameweek):
    os.chdir('/Users/matthewgoodsell/PycharmProjects/FPL')
    with open('transfers.json') as user_file:
        new_json = json.load(user_file)

    for x in fpl_json:
        if x["event"] == gameweek:
            new_player = False
            for player in new_json:
                if x["element_in"] == player["player"]:
                    abcd = player["transfers"]
                    new_player = True
                    new_gw = False
                    for gw in abcd:
                        if gw["gw"] == gameweek:
                            new_gw = True
                            transfer_out = transfer_out_check(x["element_in"], gameweek, fpl_json)
                            if not (curr_player in gw["players"]) and not transfer_out:
                                gw["players"].append(curr_player)
                                break

                    transfer_out = transfer_out_check(x["element_in"], gameweek, fpl_json)
                    if not new_gw and not transfer_out:
                        new_gw_temp = {
                                    "gw": gameweek,
                                    "players": [
                                        curr_player
                                    ]
                                }
                        abcd.append(new_gw_temp)

            transfer_out = transfer_out_check(x["element_in"], gameweek, fpl_json)

            if not new_player and not transfer_out:
                new_player_temp = {
                    "player": x["element_in"],
                    "transfers": [
                        {
                            "gw": gameweek,
                            "players": [
                                curr_player
                            ]
                        }

                    ]
                }
                new_json.append(new_player_temp)

    with open('transfers.json', 'w') as f:
        json.dump(new_json, f)


def total_player_count(sheep_list,shep_list):
    shep_dict={}
    sheep_dict = {}

    sheep_dict["Matt"] = sheep_list.count("Matt")
    sheep_dict["George"] = sheep_list.count("George")
    sheep_dict["Adam"] = sheep_list.count("Adam")
    sheep_dict["Rothwell"] = sheep_list.count("Rothwell")
    sheep_dict["Ashbourne"] = sheep_list.count("Ashbourne")
    sheep_dict["Gaz"] = sheep_list.count("Gaz")
    sheep_dict["Butler"] = sheep_list.count("Butler")

    shep_dict["Matt"] = shep_list.count("Matt")
    shep_dict["George"] = shep_list.count("George")
    shep_dict["Adam"] = shep_list.count("Adam")
    shep_dict["Rothwell"] = shep_list.count("Rothwell")
    shep_dict["Ashbourne"] = shep_list.count("Ashbourne")
    shep_dict["Gaz"] = shep_list.count("Gaz")
    shep_dict["Butler"] = shep_list.count("Butler")

    sheep_sorted_by_values = dict(sorted(sheep_dict.items(), key=lambda item: item[1]))
    shep_sorted_by_values = dict(sorted(shep_dict.items(), key=lambda item: item[1]))

    ret_str = ""
    for key in sheep_sorted_by_values:
        sheep_num = sheep_sorted_by_values[key]
        shep_num = shep_sorted_by_values[key]
        ret_str += f"**{key}** Sheep: {sheep_num} - Shepherd: {shep_num}\n"
    return ret_str


def sheep_finder(gw, full_data):
    os.chdir('/Users/matthewgoodsell/PycharmProjects/FPL')

    with open('transfers.json') as user_file:
        full_transfers = json.load(user_file)

    shep_str = ""
    gw_m2 = gw - 2
    gw_m1 = gw - 1
    gw_m3 = gw - 3
    tot_sheep = []
    tot_shephard = []
    for player in full_transfers:
        player_transfers = player["transfers"]
        gw_minus2 = False
        gw_minus3 = False
        is_sheep = False
        shepherd_potential1 = []
        shepherd_potential2 = []
        sheep = []
        shepherd = []
        shepherd_gw =[]
        shepherd_pot_gw1 = []
        shepherd_pot_gw2 = []
        sheep_gw = []
        for transfer in player_transfers:
            if transfer["gw"] == gw:
                for i in player_transfers:
                    if i["gw"] == gw_m1:
                        is_sheep = True
                        shepherd_potential1.extend(i["players"])

                        for j in shepherd_potential1:
                            shepherd_pot_gw1.extend(["GW" + str(gw_m1)])
                    elif i["gw"] == gw_m2:
                        gw_minus2 = True
                        is_sheep = True
                        shepherd_potential2.extend(i["players"])
                        for j in shepherd_potential2:
                            shepherd_pot_gw2.extend(["GW" + str(gw_m2)])

                    elif i["gw"] == gw_m3:
                        gw_minus3 = True
                        is_sheep = True
                        tot_shephard.extend(i["players"])
                        shepherd.extend(i["players"])
                        for j in shepherd:
                            shepherd_gw.extend(["GW" + str(gw_m3)])
                if is_sheep:
                    sheep.extend(transfer["players"])
                    tot_sheep.extend(transfer["players"])
                    for j in sheep:
                        sheep_gw.extend(["GW" + str(transfer['gw'])])


        if is_sheep:
            if gw_minus3:
                sheep.extend(shepherd_potential1)
                sheep_gw.extend(shepherd_pot_gw1)
                tot_sheep.extend(shepherd_potential1)

                sheep.extend(shepherd_potential2)
                sheep_gw.extend(shepherd_pot_gw2)
                tot_sheep.extend(shepherd_potential2)
            elif gw_minus2:
                sheep.extend(shepherd_potential1)
                sheep_gw.extend(shepherd_pot_gw1)
                tot_sheep.extend(shepherd_potential1)

                shepherd.extend(shepherd_potential2)
                shepherd_gw.extend(shepherd_pot_gw2)
                tot_shephard.extend(shepherd_potential2)
            else:
                shepherd.extend(shepherd_potential1)
                shepherd_gw.extend(shepherd_pot_gw1)
                tot_shephard.extend(shepherd_potential1)


            play_int = player["player"]
            player_name = full_data[play_int]["player_name"]
            shep_str += f"__**{player_name}**__\n**Shephard**\n"
            x = 0
            y = 0
            for i in shepherd:
                shep_str += f"{i} ({shepherd_gw[x]})\n"
                x += 1
            shep_str += f"\n**Sheep:**\n"
            for i in sheep:
                shep_str += f"{i} ({sheep_gw[y]})\n"
                y += 1
            shep_str += f"\n\n"
    lad_breakdown = total_player_count(tot_sheep,tot_shephard)
    shep_str += lad_breakdown
    return shep_str


# full_gw_load(y, parsed_json, "Adam")
for key in TEAM_IDS:
    y = get_gw_transfers_raw(TEAM_IDS[key])
    full_gw_load(y,parsed_json, key)
    # transfer_update(y,parsed_json, key, 6)

with open('transfers.json', 'w') as f:
    json.dump(parsed_json, f)


fd = get_full_player_data(get_full_data())

