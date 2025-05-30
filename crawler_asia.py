import json
import sys
from enum import Enum
import atexit
import time

import requests

amount_of_players = 25

def save_state():
    if state:
        with open(f"{data_path}/state.json", "w") as f:
            json.dump(state, f, indent=4)

    print(f"Code ran for {time.time()-start_time} seconds.")

def do_request(url):
    succesfull_request = False
    while not succesfull_request:
        response = requests.get(url)
        if response.status_code == 200:
            succesfull_request = True
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 1)
            print(f"Rate limited, retrying after {retry_after} seconds")
            time.sleep(int(retry_after))
        else:
            raise Exception(f"Request failed with status code {response.status_code}")
    return response.json()

region_mapping = {
        "BR1":"AMERICAS",
        "EUN1":"EUROPE",
        "EUW1":"EUROPE",
        "JP1":"ASIA",
        "KR":"ASIA",
        "LA1":"AMERICAS",
        "LA2":"AMERICAS",
        "ME1":"EUROPE",
        "NA1":"AMERICAS",
        "OC1":"SEA",
        "RU":"EUROPE",
        "SG2":"SEA",
        "TR1":"EUROPE",
        "TW2":"SEA",
        "VN2":"SEA"
}

def get_player_ids():
    save_state()
    global state

    if len(state["todo_regions"]) == 0:
        # we have done all regions
        print("All regions done!!!, exiting program...")
        sys.exit()

    tier = state["todo_tiers"][0]
    division = state["todo_divisions"][0]
    region = state["todo_regions"][0]

    queue_type = "RANKED_SOLO_5x5"
    url = f"https://{region.lower()}.api.riotgames.com/lol/league-exp/v4/entries/{queue_type}/{tier}/{division}?page=1&api_key={api_key}"

    data = do_request(url)

    puuid_set = set()
    for event in data:
        puuid_set.add(event["puuid"])
        if len(puuid_set) == amount_of_players:
            break

    print(f"Retrieved {len(puuid_set)} players from tier {tier} division {division} region {region}")

    tmp_state = state.copy()
    tmp_state["players"] = list(puuid_set)
    tmp_state["current_region"] = region

    # remove first element in tier
    tmp_state["todo_divisions"] = tmp_state["todo_divisions"][1:]
    if len(tmp_state["todo_divisions"]) == 0:
        tmp_state["todo_tiers"] = tmp_state["todo_tiers"][1:]
        tmp_state["todo_divisions"] = tmp_state["divisions"]
    if len(tmp_state["todo_tiers"]) == 0:
        tmp_state["todo_regions"] = tmp_state["todo_regions"][1:]
        tmp_state["todo_tiers"] = tmp_state["tiers"]
    state = tmp_state


def get_match_info():
    global state
    puuid = state["players"][0]
    mapped_region = region_mapping[state["current_region"]]
    queue_type = 420
    count_limit = 1
    start_count = 1
    match_type = "ranked"

    url = f"https://{mapped_region.lower()}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue_type}&type={match_type}&start={start_count}&count={count_limit}&api_key={api_key}"
    data = do_request(url)

    if len(data)==0:
        print(f"No match found for player {puuid}")
        state["players"] = state["players"][1:]

    match_id = data[0]

    url = f"https://{mapped_region.lower()}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    data = do_request(url)

    # save match info
    match = data['info']
    match_info = []
    match_info.append(match['gameId'])
    match_info.append(match_id)
    match_info.append(match['platformId'])
    match_info.append(match['gameDuration'])
    match_info.append(match['gameEndTimestamp'])
    match_info.append(match['gameMode'])
    match_info.append(match['gameStartTimestamp'])

    with open(f"{data_path}/matches.csv","a") as f:
        f.write(";".join(map(str, match_info))+"\n")

    # save participants info
    participants_info = []
    for participant in data['info']['participants']:
        participant_puuid = participant['puuid']

        participant_info = []

        participant_info.append(match_id)
        participant_info.append(match['gameId'])
        participant_info.append(participant['teamId'])
        participant_info.append(participant['puuid'])
        participant_info.append(participant['allInPings'])
        participant_info.append(participant['assistMePings'])
        participant_info.append(participant['basicPings'])
        participant_info.append(participant['challenges']['controlWardsPlaced'])
        participant_info.append(participant['challenges']['stealthWardsPlaced'])
        participant_info.append(participant['challenges']['twoWardsOneSweeperCount'])
        participant_info.append(participant['challenges'].get('visionScoreAdvantageLaneOpponent','NONE'))
        participant_info.append(participant['challenges']['visionScorePerMinute'])
        participant_info.append(participant['challenges']['wardTakedowns'])
        participant_info.append(participant['challenges']['wardTakedownsBefore20M'])
        participant_info.append(participant['challenges']['wardsGuarded'])
        participant_info.append(participant['commandPings'])
        participant_info.append(participant['dangerPings'])
        participant_info.append(participant['detectorWardsPlaced'])
        participant_info.append(participant['enemyMissingPings'])
        participant_info.append(participant['enemyVisionPings'])
        participant_info.append(participant['getBackPings'])
        participant_info.append(participant['holdPings'])
        participant_info.append(participant['needVisionPings'])
        participant_info.append(participant['onMyWayPings'])
        participant_info.append(participant['participantId'])
        participant_info.append(participant['pushPings'])
        participant_info.append(participant['retreatPings'])
        participant_info.append(participant['sightWardsBoughtInGame'])
        participant_info.append(participant['summonerLevel'])
        participant_info.append(participant['teamPosition'])
        participant_info.append(participant['visionClearedPings'])
        participant_info.append(participant['visionScore'])
        participant_info.append(participant['visionWardsBoughtInGame'])
        participant_info.append(participant['wardsKilled'])
        participant_info.append(participant['wardsPlaced'])

        participant_division_tier = get_participants_info(participant_puuid)
        participant_info.append(participant_division_tier[0])
        participant_info.append(participant_division_tier[1])


        participants_info.append(participant_info)

    with open(f"{data_path}/player_match_info.csv","a") as f:
        for participant_info in participants_info:
            f.write(";".join(map(str,participant_info))+"\n")

    # save team info
    teams_info = []
    for team in data['info']['teams']:
        team_info = []

        team_info.append(match_id)
        team_info.append(team['teamId'])
        team_info.append(match['gameId'])
        team_info.append(team['win'])

        teams_info.append(team_info)

    with open(f"{data_path}/team_match_info.csv","a") as f:
        for team_info in teams_info:
            f.write(";".join(map(str,team_info))+"\n")

    #match_participants = data_america["metadata"]["participants"]

    print(f"Retrieved second to last match for player {puuid}")

    tmp_state = state.copy()
    #tmp_state["match_participants"] = match_participants

    # remove first element in players
    tmp_state["players"] = tmp_state["players"][1:]
    state = tmp_state


def get_participants_info(puuid):
    # find the rank and division of the player
    global state
    region = state["current_region"]
    queue_type = "RANKED_SOLO_5x5"

    url = f'https://{region.lower()}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={api_key}'
    data = do_request(url)

    # get the tier and division of RANKED_SOLO_5x5 if they exist
    for league in data:
        if league['queueType'] == queue_type:
            return league['rank'], league['tier']
    # for some reason we didn't find a rank this season
    return "NONE", "NONE"


class State(Enum):
    RETRIEVING_PLAYER_IDS = get_player_ids
    RETRIEVING_MATCH_INFO = get_match_info

def get_next_step():
    # decide what to do based on what is in the state lists
    if len(state["players"]) != 0:
        current_step = State.RETRIEVING_MATCH_INFO
    else:
        current_step = State.RETRIEVING_PLAYER_IDS
    return current_step

state = None
atexit.register(save_state)
api_key = None
data_path = "data_asia"

start_time = time.time()

if __name__ == '__main__':
    # read api key
    with open("key.json","r") as f:
        api_key = json.load(f)["api_key"]

    # read todo state to continue from
    with open(f"{data_path}/state.json","r") as f:
        state = json.load(f)
    current_step = get_next_step()

    while True:
        current_step()
        current_step = get_next_step()