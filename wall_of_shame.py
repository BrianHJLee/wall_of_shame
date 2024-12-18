import requests
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# prompt user for league ID
#league_id = input("Enter your league ID: ")

league_id = 1049423434511474688

response = requests.get("https://api.sleeper.app/v1/state/nfl")
body = response.json()
current_week = body['week']
current_year = int(body['season'])

all_matchups = pd.DataFrame(columns=['season', 'week', 'user_name', 'team_name', 'score'])

while True:
    response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/rosters")
    body = response.json()

    # roster_id: (owner_id)
    roster_id_to_owner = {}

    for roster in body:
        roster_id_to_owner[roster['roster_id']] = roster['owner_id']
    
    response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/users")
    body = response.json()

    owner_id_to_name = {}
    onwer_id_to_team = {}

    for user in body:
        owner_id_to_name[user['user_id']] = user['display_name']

        if 'team_name' in user['metadata']:
            onwer_id_to_team[user['user_id']] = user['metadata']['team_name']
        else: 
            onwer_id_to_team[user['user_id']] = "Team " + user['display_name']


    for week in range(1, current_week):
        response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}")
        body = response.json()

        for matchup in body:
            all_matchups = pd.concat([all_matchups, pd.DataFrame([{
                'season': current_year,
                'week': week,
                'user_name': owner_id_to_name[roster_id_to_owner[matchup['roster_id']]],
                'team_name': onwer_id_to_team[roster_id_to_owner[matchup['roster_id']]],
                'score': matchup['points']
            }])], ignore_index=True)

    response = requests.get(f"https://api.sleeper.app/v1/league/{league_id}")
    body = response.json()
    
    league_id = body['previous_league_id']

    if league_id is None:
        break

    current_week = 18
    current_year -= 1

all_matchups = all_matchups.sort_values(by='score', ascending=True)

# label top 10
all_matchups['rank'] = all_matchups['score'].rank(method='min', ascending=True)

# move rank to front
all_matchups = all_matchups[['rank', 'season', 'week', 'user_name', 'team_name', 'score']]

print(all_matchups.head(10).to_markdown(index=False))