import requests
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm
import time
from pytz import timezone


class MLB_Scrape:

    # def __init__(self):
    #     # Initialize your class here if needed
    #     pass

    def get_sport_id(self):
        df = pd.DataFrame(requests.get(url=f'https://statsapi.mlb.com/api/v1/sports').json()['sports']).set_index('id')
        return df

    def get_sport_id_check(self,sport_id):
        sport_id_df = self.get_sport_id()
        if sport_id not in sport_id_df.index:
            print('Please Select a New Sport ID from the following')
            print(sport_id_df)
            return False
        return True

    def get_schedule(self,year_input: int,
                     sport_id:int,
                     start_date='YYYY-MM-DD',
                     end_date='YYYY-MM-DD',
                     final=True,
                     regular=True,
                     spring=False):
        # Get MLB Schedule

        if not self.get_sport_id_check(sport_id=sport_id):
            return
        if regular == True:
            game_call = requests.get(url=f'https://statsapi.mlb.com/api/v1/schedule/?sportId={sport_id}&gameTypes=R&season={year_input}&hydrate=lineup,players').json()
            print(f'https://statsapi.mlb.com/api/v1/schedule/?sportId={sport_id}&gameTypes=R&season={year_input}&hydrate=lineup,players')
        elif spring == True:
            print('spring')
            game_call = requests.get(url=f'https://statsapi.mlb.com/api/v1/schedule/?sportId={sport_id}&gameTypes=S&season={year_input}&hydrate=lineup,players').json()
            print(f'https://statsapi.mlb.com/api/v1/schedule/?sportId={sport_id}&gameTypes=S&season={year_input}&hydrate=lineup,players')
        else:
            game_call = requests.get(url=f'https://statsapi.mlb.com/api/v1/schedule/?sportId={sport_id}&season={year_input}&hydrate=lineup,players').json()

        # Grab data from MLB Schedule (game id, away, home, state)
        game_list = [item for sublist in [[y['gamePk'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        time_list = [item for sublist in [[y['gameDate'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        date_list = [item for sublist in [[y['officialDate'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        away_team_list = [item for sublist in [[y['teams']['away']['team']['name'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        away_score_list = [item for sublist in [[y['teams']['away']['score'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        home_team_list = [item for sublist in [[y['teams']['home']['team']['name'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        home_score_list = [item for sublist in [[y['teams']['home']['score'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        state_list = [item for sublist in [[y['status']['codedGameState'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        venue_id = [item for sublist in [[y['venue']['id'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        venue_name = [item for sublist in [[y['venue']['name'] for y in x['games']] for x in game_call['dates']] for item in sublist]

        game_df = pd.DataFrame(data={'game_id':game_list,
                                     'time':time_list,
                                     'date':date_list,
                                     'away':away_team_list,
                                     'away_score':away_score_list,
                                     'home':home_team_list,
                                     'home_score':home_score_list,
                                     'state':state_list,
                                     'venue_id':venue_id,
                                     'venue_name':venue_name})

        # game_list = [item for sublist in [[y['gamePk'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        # date_list = [item for sublist in [[y['officialDate'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        # cancel_list = [item for sublist in [[y['status']['codedGameState'] for y in x['games']] for x in game_call['dates']] for item in sublist]
        # game_df = pd.DataFrame(data={'game_id':game_list,'date':date_list,'state':cancel_list})
        #game_df = pd.concat([game_df,game_df])
        if len(game_df) == 0:
            return 'Schedule Length of 0, please select different parameters.'

        game_df['date'] = pd.to_datetime(game_df['date']).dt.date
        #game_df['time'] = game_df['time'].dt.tz_localize('UTC')
        #game_df['time'] = game_df['time'].dt.tz_localize('UTC')
        game_df['time'] = pd.to_datetime(game_df['time'])
        eastern = timezone('US/Eastern')
        game_df['time'] = game_df['time'].dt.tz_convert(eastern)
        game_df['time'] = game_df['time'].dt.strftime("%I:%M  %p EST")#.dt.time

        if not start_date == 'YYYY-MM-DD' or not end_date == 'YYYY-MM-DD':
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                game_df = game_df[(game_df['date'] >= start_date) & (game_df['date'] <= end_date)]

            except ValueError:
                return 'Please use YYYY-MM-DD Format for Start and End Dates'
        if final:
            game_df = game_df[game_df['state'] == 'F'].drop_duplicates(subset='game_id').reset_index(drop=True)

        game_df = game_df.drop_duplicates(subset='game_id').reset_index(drop=True)

        if len(game_df) == 0:
            return 'Schedule Length of 0, please select different parameters.'

        return game_df

    def get_game_type(self):
        data = requests.get(f'https://statsapi.mlb.com/api/v1/gameTypes').json()
        return pd.DataFrame(data)


    def get_data(self,game_list_input: list):
        data_total = []
        #n_count = 0
        print('This May Take a While. Progress Bar shows Completion of Data Retrieval.')
        for i in tqdm(range(len(game_list_input)), desc="Processing", unit="iteration"):
        #for game_id_select in game_list:
            # if n_count%50 == 0:
            #     print(n_count)
            r = requests.get(f'https://statsapi.mlb.com/api/v1.1/game/{game_list_input[i]}/feed/live')
            data_total.append(r.json())
            #n_count = n_count + 1
        return data_total

    def get_data_df(self,data_list):

        swing_list = ['X','F','S','D','E','T','W']
        whiff_list = ['S','T','W']
        print('Converting Data to Dataframe.')
        game_id = []
        game_date = []
        batter_id = []
        batter_name = []
        batter_hand = []
        batter_team = []
        batter_team_id = []
        pitcher_id = []
        pitcher_name = []
        pitcher_hand = []
        pitcher_team = []
        pitcher_team_id = []

        play_description = []
        play_code = []
        in_play = []
        is_strike = []
        is_swing = []
        is_whiff = []
        is_out = []
        is_ball = []
        is_review = []
        pitch_type = []
        pitch_description = []
        strikes = []
        balls = []
        outs = []

        start_speed = []
        end_speed = []
        sz_top = []
        sz_bot = []
        x = []
        y = []
        ax = []
        ay = []
        az = []
        pfxx = []
        pfxz = []
        px = []
        pz = []
        vx0 = []
        vy0 = []
        vz0 = []
        x0 = []
        y0 = []
        z0 = []
        zone = []
        type_confidence = []
        plate_time = []
        extension = []
        spin_rate = []
        spin_direction = []
        ivb = []
        hb = []

        launch_speed = []
        launch_angle = []
        launch_distance = []
        launch_location = []
        trajectory = []
        hardness = []
        hit_x = []
        hit_y = []

        index_play = []
        play_id = []
        start_time = []
        end_time = []
        is_pitch = []
        type_type = []


        type_ab = []
        ab_number = []
        event = []
        event_type = []
        rbi = []
        away_score = []
        home_score = []

#data[0]['liveData']['plays']['allPlays'][32]['playEvents'][-1]['details']['call']['code'] in ['VP']

        for data in data_list:
            for ab_id in range(len(data['liveData']['plays']['allPlays'])):
                ab_list = data['liveData']['plays']['allPlays'][ab_id]
                for n in range(len(ab_list['playEvents'])):
                    if ab_list['playEvents'][n]['isPitch'] == True or 'call' in ab_list['playEvents'][n]['details']:

                        game_id.append(data['gamePk'])
                        game_date.append(data['gameData']['datetime']['officialDate'])
                        if 'matchup' in ab_list:
                          batter_id.append(ab_list['matchup']['batter']['id'] if 'batter' in ab_list['matchup'] else np.nan)
                          if 'batter' in ab_list['matchup']:
                            batter_name.append(ab_list['matchup']['batter']['fullName'] if 'fullName' in ab_list['matchup']['batter'] else np.nan)
                          else:
                            batter_name.append(np.nan)

                          batter_hand.append(ab_list['matchup']['batSide']['code'] if 'batSide' in ab_list['matchup'] else np.nan)
                          pitcher_id.append(ab_list['matchup']['pitcher']['id'] if 'pitcher' in ab_list['matchup'] else np.nan)
                          if 'pitcher' in ab_list['matchup']:
                            pitcher_name.append(ab_list['matchup']['pitcher']['fullName'] if 'fullName' in ab_list['matchup']['pitcher'] else np.nan)
                          else:
                            pitcher_name.append(np.nan)
                          #pitcher_name.append(ab_list['matchup']['pitcher']['fullName'] if 'pitcher' in ab_list['matchup'] else np.nan)
                          pitcher_hand.append(ab_list['matchup']['pitchHand']['code'] if 'pitchHand' in ab_list['matchup'] else np.nan)


                        # batter_id.append(ab_list['matchup']['batter']['id'] if 'batter' in ab_list['matchup'] else np.nan)
                        # batter_name.append(ab_list['matchup']['batter']['fullName'] if 'batter' in ab_list['matchup'] else np.nan)
                        # batter_hand.append(ab_list['matchup']['batSide']['code'] if 'batSide' in ab_list['matchup'] else np.nan)
                        # pitcher_id.append(ab_list['matchup']['pitcher']['id'] if 'pitcher' in ab_list['matchup'] else np.nan)
                        # pitcher_name.append(ab_list['matchup']['pitcher']['fullName'] if 'pitcher' in ab_list['matchup'] else np.nan)
                        # pitcher_hand.append(ab_list['matchup']['pitchHand']['code'] if 'pitchHand' in ab_list['matchup'] else np.nan)

                        if ab_list['about']['isTopInning']:
                            batter_team.append(data['gameData']['teams']['away']['abbreviation'] if 'away' in data['gameData']['teams'] else np.nan)
                            batter_team_id.append(data['gameData']['teams']['away']['id'] if 'away' in data['gameData']['teams'] else np.nan)
                            pitcher_team.append(data['gameData']['teams']['home']['abbreviation'] if 'home' in data['gameData']['teams'] else np.nan)
                            pitcher_team_id.append(data['gameData']['teams']['away']['id'] if 'away' in data['gameData']['teams'] else np.nan)

                        else:
                            batter_team.append(data['gameData']['teams']['home']['abbreviation'] if 'home' in data['gameData']['teams'] else np.nan)
                            batter_team_id.append(data['gameData']['teams']['home']['id'] if 'home' in data['gameData']['teams'] else np.nan)
                            pitcher_team.append(data['gameData']['teams']['away']['abbreviation'] if 'away' in data['gameData']['teams'] else np.nan)
                            pitcher_team_id.append(data['gameData']['teams']['home']['id'] if 'home' in data['gameData']['teams'] else np.nan)

                        play_description.append(ab_list['playEvents'][n]['details']['description'] if 'description' in ab_list['playEvents'][n]['details'] else np.nan)
                        play_code.append(ab_list['playEvents'][n]['details']['code'] if 'code' in ab_list['playEvents'][n]['details'] else np.nan)
                        in_play.append(ab_list['playEvents'][n]['details']['isInPlay'] if 'isInPlay' in ab_list['playEvents'][n]['details'] else np.nan)
                        is_strike.append(ab_list['playEvents'][n]['details']['isStrike'] if 'isStrike' in ab_list['playEvents'][n]['details'] else np.nan)

                        if 'details' in ab_list['playEvents'][n]:
                            is_swing.append(True if ab_list['playEvents'][n]['details']['code'] in swing_list else np.nan)
                            is_whiff.append(True if ab_list['playEvents'][n]['details']['code'] in whiff_list else np.nan)
                        else:
                            is_swing.append(np.nan)
                            is_whiff.append(np.nan)

                        #is_out.append(ab_list['playEvents'][n]['details']['isBall'] if 'isBall' in ab_list['playEvents'][n]['details'] else np.nan)
                        is_ball.append(ab_list['playEvents'][n]['details']['isOut'] if 'isOut' in ab_list['playEvents'][n]['details'] else np.nan)
                        is_review.append(ab_list['playEvents'][n]['details']['hasReview'] if 'hasReview' in ab_list['playEvents'][n]['details'] else np.nan)
                        pitch_type.append(ab_list['playEvents'][n]['details']['type']['code'] if 'type' in ab_list['playEvents'][n]['details'] else np.nan)
                        pitch_description.append(ab_list['playEvents'][n]['details']['type']['description'] if 'type' in ab_list['playEvents'][n]['details'] else np.nan)

                        #if ab_list['playEvents'][n]['isPitch'] == True:
                        if ab_list['playEvents'][n]['pitchNumber'] == 1:
                            ab_number.append(ab_list['playEvents'][n]['atBatIndex'] if 'atBatIndex' in ab_list['playEvents'][n] else np.nan)
                            strikes.append(0)
                            balls.append(0)
                            outs.append(ab_list['playEvents'][n]['count']['outs'] if 'outs' in ab_list['playEvents'][n]['count'] else np.nan)

                        else:
                            ab_number.append(ab_list['playEvents'][n]['atBatIndex'] if 'atBatIndex' in ab_list['playEvents'][n] else np.nan)
                            strikes.append(ab_list['playEvents'][n-1]['count']['strikes'] if 'strikes' in ab_list['playEvents'][n-1]['count'] else np.nan)
                            balls.append(ab_list['playEvents'][n-1]['count']['balls'] if 'balls' in ab_list['playEvents'][n-1]['count'] else np.nan)
                            outs.append(ab_list['playEvents'][n-1]['count']['outs'] if 'outs' in ab_list['playEvents'][n-1]['count'] else np.nan)

                        if 'pitchData' in ab_list['playEvents'][n]:

                            start_speed.append(ab_list['playEvents'][n]['pitchData']['startSpeed'] if 'startSpeed' in ab_list['playEvents'][n]['pitchData'] else np.nan)
                            end_speed.append(ab_list['playEvents'][n]['pitchData']['endSpeed'] if 'endSpeed' in ab_list['playEvents'][n]['pitchData'] else np.nan)

                            sz_top.append(ab_list['playEvents'][n]['pitchData']['strikeZoneTop'] if 'strikeZoneTop' in ab_list['playEvents'][n]['pitchData'] else np.nan)
                            sz_bot.append(ab_list['playEvents'][n]['pitchData']['strikeZoneBottom'] if 'strikeZoneBottom' in ab_list['playEvents'][n]['pitchData'] else np.nan)
                            x.append(ab_list['playEvents'][n]['pitchData']['coordinates']['x'] if 'x' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            y.append(ab_list['playEvents'][n]['pitchData']['coordinates']['y'] if 'y' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)

                            ax.append(ab_list['playEvents'][n]['pitchData']['coordinates']['aX'] if 'aX' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            ay.append(ab_list['playEvents'][n]['pitchData']['coordinates']['aY'] if 'aY' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            az.append(ab_list['playEvents'][n]['pitchData']['coordinates']['aZ'] if 'aZ' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            pfxx.append(ab_list['playEvents'][n]['pitchData']['coordinates']['pfxX'] if 'pfxX' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            pfxz.append(ab_list['playEvents'][n]['pitchData']['coordinates']['pfxZ'] if 'pfxZ' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            px.append(ab_list['playEvents'][n]['pitchData']['coordinates']['pX'] if 'pX' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            pz.append(ab_list['playEvents'][n]['pitchData']['coordinates']['pZ'] if 'pZ' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            vx0.append(ab_list['playEvents'][n]['pitchData']['coordinates']['vX0'] if 'vX0' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            vy0.append(ab_list['playEvents'][n]['pitchData']['coordinates']['vY0'] if 'vY0' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            vz0.append(ab_list['playEvents'][n]['pitchData']['coordinates']['vZ0'] if 'vZ0' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            x0.append(ab_list['playEvents'][n]['pitchData']['coordinates']['x0'] if 'x0' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            y0.append(ab_list['playEvents'][n]['pitchData']['coordinates']['y0'] if 'y0' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)
                            z0.append(ab_list['playEvents'][n]['pitchData']['coordinates']['z0'] if 'z0' in ab_list['playEvents'][n]['pitchData']['coordinates'] else np.nan)

                            zone.append(ab_list['playEvents'][n]['pitchData']['zone'] if 'zone' in ab_list['playEvents'][n]['pitchData'] else np.nan)
                            type_confidence.append(ab_list['playEvents'][n]['pitchData']['typeConfidence'] if 'typeConfidence' in ab_list['playEvents'][n]['pitchData'] else np.nan)
                            plate_time.append(ab_list['playEvents'][n]['pitchData']['plateTime'] if 'plateTime' in ab_list['playEvents'][n]['pitchData'] else np.nan)
                            extension.append(ab_list['playEvents'][n]['pitchData']['extension'] if 'extension' in ab_list['playEvents'][n]['pitchData'] else np.nan)

                            if 'breaks' in ab_list['playEvents'][n]['pitchData']:
                                spin_rate.append(ab_list['playEvents'][n]['pitchData']['breaks']['spinRate'] if 'spinRate' in ab_list['playEvents'][n]['pitchData']['breaks'] else np.nan)
                                spin_direction.append(ab_list['playEvents'][n]['pitchData']['breaks']['spinDirection'] if 'spinDirection' in ab_list['playEvents'][n]['pitchData']['breaks'] else np.nan)
                                ivb.append(ab_list['playEvents'][n]['pitchData']['breaks']['breakVerticalInduced'] if 'breakVerticalInduced' in ab_list['playEvents'][n]['pitchData']['breaks'] else np.nan)
                                hb.append(ab_list['playEvents'][n]['pitchData']['breaks']['breakHorizontal'] if 'breakHorizontal' in ab_list['playEvents'][n]['pitchData']['breaks'] else np.nan)

                        else:
                            start_speed.append(np.nan)
                            end_speed.append(np.nan)

                            sz_top.append(np.nan)
                            sz_bot.append(np.nan)
                            x.append(np.nan)
                            y.append(np.nan)

                            ax.append(np.nan)
                            ay.append(np.nan)
                            az.append(np.nan)
                            pfxx.append(np.nan)
                            pfxz.append(np.nan)
                            px.append(np.nan)
                            pz.append(np.nan)
                            vx0.append(np.nan)
                            vy0.append(np.nan)
                            vz0.append(np.nan)
                            x0.append(np.nan)
                            y0.append(np.nan)
                            z0.append(np.nan)

                            zone.append(np.nan)
                            type_confidence.append(np.nan)
                            plate_time.append(np.nan)
                            extension.append(np.nan)
                            spin_rate.append(np.nan)
                            spin_direction.append(np.nan)
                            ivb.append(np.nan)
                            hb.append(np.nan)

                        if 'hitData' in ab_list['playEvents'][n]:
                            launch_speed.append(ab_list['playEvents'][n]['hitData']['launchSpeed'] if 'launchSpeed' in ab_list['playEvents'][n]['hitData'] else np.nan)
                            launch_angle.append(ab_list['playEvents'][n]['hitData']['launchAngle'] if 'launchAngle' in ab_list['playEvents'][n]['hitData'] else np.nan)
                            launch_distance.append(ab_list['playEvents'][n]['hitData']['totalDistance'] if 'totalDistance' in ab_list['playEvents'][n]['hitData'] else np.nan)
                            launch_location.append(ab_list['playEvents'][n]['hitData']['location'] if 'location' in ab_list['playEvents'][n]['hitData'] else np.nan)

                            trajectory.append(ab_list['playEvents'][n]['hitData']['trajectory'] if 'trajectory' in ab_list['playEvents'][n]['hitData'] else np.nan)
                            hardness.append(ab_list['playEvents'][n]['hitData']['hardness'] if 'hardness' in ab_list['playEvents'][n]['hitData'] else np.nan)
                            hit_x.append(ab_list['playEvents'][n]['hitData']['coordinates']['coordX'] if 'coordX' in ab_list['playEvents'][n]['hitData']['coordinates'] else np.nan)
                            hit_y.append(ab_list['playEvents'][n]['hitData']['coordinates']['coordY'] if 'coordY' in ab_list['playEvents'][n]['hitData']['coordinates'] else np.nan)
                        else:
                            launch_speed.append(np.nan)
                            launch_angle.append(np.nan)
                            launch_distance.append(np.nan)
                            launch_location.append(np.nan)
                            trajectory.append(np.nan)
                            hardness.append(np.nan)
                            hit_x.append(np.nan)
                            hit_y.append(np.nan)

                        index_play.append(ab_list['playEvents'][n]['index'] if 'index' in ab_list['playEvents'][n] else np.nan)
                        play_id.append(ab_list['playEvents'][n]['playId'] if 'playId' in ab_list['playEvents'][n] else np.nan)
                        start_time.append(ab_list['playEvents'][n]['startTime'] if 'startTime' in ab_list['playEvents'][n] else np.nan)
                        end_time.append(ab_list['playEvents'][n]['endTime'] if 'endTime' in ab_list['playEvents'][n] else np.nan)
                        is_pitch.append(ab_list['playEvents'][n]['isPitch'] if 'isPitch' in ab_list['playEvents'][n] else np.nan)
                        type_type.append(ab_list['playEvents'][n]['type'] if 'type' in ab_list['playEvents'][n] else np.nan)



                        if n == len(ab_list['playEvents']) - 1 :

                            type_ab.append(data['liveData']['plays']['allPlays'][ab_id]['result']['type'] if 'type' in data['liveData']['plays']['allPlays'][ab_id]['result'] else np.nan)
                            event.append(data['liveData']['plays']['allPlays'][ab_id]['result']['event'] if 'event' in data['liveData']['plays']['allPlays'][ab_id]['result'] else np.nan)
                            event_type.append(data['liveData']['plays']['allPlays'][ab_id]['result']['eventType'] if 'eventType' in data['liveData']['plays']['allPlays'][ab_id]['result'] else np.nan)
                            rbi.append(data['liveData']['plays']['allPlays'][ab_id]['result']['rbi'] if 'rbi' in data['liveData']['plays']['allPlays'][ab_id]['result'] else np.nan)
                            away_score.append(data['liveData']['plays']['allPlays'][ab_id]['result']['awayScore'] if 'awayScore' in data['liveData']['plays']['allPlays'][ab_id]['result'] else np.nan)
                            home_score.append(data['liveData']['plays']['allPlays'][ab_id]['result']['homeScore'] if 'homeScore' in data['liveData']['plays']['allPlays'][ab_id]['result'] else np.nan)
                            is_out.append(data['liveData']['plays']['allPlays'][ab_id]['result']['isOut'] if 'isOut' in data['liveData']['plays']['allPlays'][ab_id]['result'] else np.nan)

                        else:

                            type_ab.append(np.nan)
                            event.append(np.nan)
                            event_type.append(np.nan)
                            rbi.append(np.nan)
                            away_score.append(np.nan)
                            home_score.append(np.nan)
                            is_out.append(np.nan)

                    elif ab_list['playEvents'][n]['count']['balls'] == 4:

                        event.append(data['liveData']['plays']['allPlays'][ab_id]['result']['event'])
                        event_type.append(data['liveData']['plays']['allPlays'][ab_id]['result']['eventType'])


                        game_id.append(data['gamePk'])
                        game_date.append(data['gameData']['datetime']['officialDate'])
                        batter_id.append(ab_list['matchup']['batter']['id'] if 'batter' in ab_list['matchup'] else np.nan)
                        batter_name.append(ab_list['matchup']['batter']['fullName'] if 'batter' in ab_list['matchup'] else np.nan)
                        batter_hand.append(ab_list['matchup']['batSide']['code'] if 'batSide' in ab_list['matchup'] else np.nan)
                        pitcher_id.append(ab_list['matchup']['pitcher']['id'] if 'pitcher' in ab_list['matchup'] else np.nan)
                        pitcher_name.append(ab_list['matchup']['pitcher']['fullName'] if 'pitcher' in ab_list['matchup'] else np.nan)
                        pitcher_hand.append(ab_list['matchup']['pitchHand']['code'] if 'pitchHand' in ab_list['matchup'] else np.nan)
                        if ab_list['about']['isTopInning']:
                            batter_team.append(data['gameData']['teams']['away']['abbreviation'] if 'away' in data['gameData']['teams'] else np.nan)
                            batter_team_id.append(data['gameData']['teams']['away']['id'] if 'away' in data['gameData']['teams'] else np.nan)
                            pitcher_team.append(data['gameData']['teams']['home']['abbreviation'] if 'home' in data['gameData']['teams'] else np.nan)
                            pitcher_team_id.append(data['gameData']['teams']['away']['id'] if 'away' in data['gameData']['teams'] else np.nan)
                        else:
                            batter_team.append(data['gameData']['teams']['home']['abbreviation'] if 'home' in data['gameData']['teams'] else np.nan)
                            batter_team_id.append(data['gameData']['teams']['home']['id'] if 'home' in data['gameData']['teams'] else np.nan)
                            pitcher_team.append(data['gameData']['teams']['away']['abbreviation'] if 'away' in data['gameData']['teams'] else np.nan)
                            pitcher_team_id.append(data['gameData']['teams']['home']['id'] if 'home' in data['gameData']['teams'] else np.nan)

                        play_description.append(np.nan)
                        play_code.append(np.nan)
                        in_play.append(np.nan)
                        is_strike.append(np.nan)
                        is_ball.append(np.nan)
                        is_review.append(np.nan)
                        pitch_type.append(np.nan)
                        pitch_description.append(np.nan)
                        strikes.append(ab_list['playEvents'][n]['count']['balls'] if 'balls' in ab_list['playEvents'][n]['count'] else np.nan)
                        balls.append(ab_list['playEvents'][n]['count']['strikes'] if 'strikes' in ab_list['playEvents'][n]['count'] else np.nan)
                        outs.append(ab_list['playEvents'][n]['count']['outs'] if 'outs' in ab_list['playEvents'][n]['count'] else np.nan)
                        index_play.append(ab_list['playEvents'][n]['index'] if 'index' in ab_list['playEvents'][n] else np.nan)
                        play_id.append(ab_list['playEvents'][n]['playId'] if 'playId' in ab_list['playEvents'][n] else np.nan)
                        start_time.append(ab_list['playEvents'][n]['startTime'] if 'startTime' in ab_list['playEvents'][n] else np.nan)
                        end_time.append(ab_list['playEvents'][n]['endTime'] if 'endTime' in ab_list['playEvents'][n] else np.nan)
                        is_pitch.append(ab_list['playEvents'][n]['isPitch'] if 'isPitch' in ab_list['playEvents'][n] else np.nan)
                        type_type.append(ab_list['playEvents'][n]['type'] if 'type' in ab_list['playEvents'][n] else np.nan)



                        is_swing.append(np.nan)
                        is_whiff.append(np.nan)
                        start_speed.append(np.nan)
                        end_speed.append(np.nan)
                        sz_top.append(np.nan)
                        sz_bot.append(np.nan)
                        x.append(np.nan)
                        y.append(np.nan)
                        ax.append(np.nan)
                        ay.append(np.nan)
                        az.append(np.nan)
                        pfxx.append(np.nan)
                        pfxz.append(np.nan)
                        px.append(np.nan)
                        pz.append(np.nan)
                        vx0.append(np.nan)
                        vy0.append(np.nan)
                        vz0.append(np.nan)
                        x0.append(np.nan)
                        y0.append(np.nan)
                        z0.append(np.nan)
                        zone.append(np.nan)
                        type_confidence.append(np.nan)
                        plate_time.append(np.nan)
                        extension.append(np.nan)
                        spin_rate.append(np.nan)
                        spin_direction.append(np.nan)
                        ivb.append(np.nan)
                        hb.append(np.nan)
                        launch_speed.append(np.nan)
                        launch_angle.append(np.nan)
                        launch_distance.append(np.nan)
                        launch_location.append(np.nan)
                        trajectory.append(np.nan)
                        hardness.append(np.nan)
                        hit_x.append(np.nan)
                        hit_y.append(np.nan)
                        type_ab.append(np.nan)
                        ab_number.append(np.nan)

                        rbi.append(np.nan)
                        away_score.append(np.nan)
                        home_score.append(np.nan)
                        is_out.append(np.nan)
        print({
            'game_id':len(game_id),
            'game_date':len(game_date),
            'batter_id':len(batter_id),
            'batter_name':len(batter_name),
            'batter_hand':len(batter_hand),
            'batter_team':len(batter_team),
            'batter_team_id':len(batter_team_id),
            'pitcher_id':len(pitcher_id),
            'pitcher_name':len(pitcher_name),
            'pitcher_hand':len(pitcher_hand),
            'pitcher_team':len(pitcher_team),
            'pitcher_team_id':len(pitcher_team_id),
            'play_description':len(play_description),
            'play_code':len(play_code),
            'in_play':len(in_play),
            'is_strike':len(is_strike),
            'is_swing':len(is_swing),
            'is_whiff':len(is_whiff),
            'is_out':len(is_out),
            'is_ball':len(is_ball),
            'is_review':len(is_review),
            'pitch_type':len(pitch_type),
            'pitch_description':len(pitch_description),
            'strikes':len(strikes),
            'balls':len(balls),
            'outs':len(outs),
            'start_speed':len(start_speed),
            'end_speed':len(end_speed),
            'sz_top':len(sz_top),
            'sz_bot':len(sz_bot),
            'x':len(x),
            'y':len(y),
            'ax':len(ax),
            'ay':len(ay),
            'az':len(az),
            'pfxx':len(pfxx),
            'pfxz':len(pfxz),
            'px':len(px),
            'pz':len(pz),
            'vx0':len(vx0),
            'vy0':len(vy0),
            'vz0':len(vz0),
            'x0':len(x0),
            'y0':len(y0),
            'z0':len(z0),
            'zone':len(zone),
            'type_confidence':len(type_confidence),
            'plate_time':len(plate_time),
            'extension':len(extension),
            'spin_rate':len(spin_rate),
            'spin_direction':len(spin_direction),
            'ivb':len(ivb),
            'hb':len(hb),
            'launch_speed':len(launch_speed),
            'launch_angle':len(launch_angle),
            'launch_distance':len(launch_distance),
            'launch_location':len(launch_location),
            'trajectory':len(trajectory),
            'hardness':len(hardness),
            'hit_x':len(hit_x),
            'hit_y':len(hit_y),
            'index_play':len(index_play),
            'play_id':len(play_id),
            'start_time':len(start_time),
            'end_time':len(end_time),
            'is_pitch':len(is_pitch),
            'type_type':len(type_type),
            'type_ab':len(type_ab),
            'event':len(event),
            'event_type':len(event_type),
            'rbi':len(rbi),
            'away_score':len(away_score),
            'home_score':len(home_score),
            }


        )
        df  = pd.DataFrame(data={
            'game_id':game_id,
            'game_date':game_date,
            'batter_id':batter_id,
            'batter_name':batter_name,
            'batter_hand':batter_hand,
            'batter_team':batter_team,
            'batter_team_id':batter_team_id,
            'pitcher_id':pitcher_id,
            'pitcher_name':pitcher_name,
            'pitcher_hand':pitcher_hand,
            'pitcher_team':pitcher_team,
            'pitcher_team_id':pitcher_team_id,
            'play_description':play_description,
            'play_code':play_code,
            'in_play':in_play,
            'is_strike':is_strike,
            'is_swing':is_swing,
            'is_whiff':is_whiff,
            'is_out':is_out,
            'is_ball':is_ball,
            'is_review':is_review,
            'pitch_type':pitch_type,
            'pitch_description':pitch_description,
            'strikes':strikes,
            'balls':balls,
            'outs':outs,
            'start_speed':start_speed,
            'end_speed':end_speed,
            'sz_top':sz_top,
            'sz_bot':sz_bot,
            'x':x,
            'y':y,
            'ax':ax,
            'ay':ay,
            'az':az,
            'pfxx':pfxx,
            'pfxz':pfxz,
            'px':px,
            'pz':pz,
            'vx0':vx0,
            'vy0':vy0,
            'vz0':vz0,
            'x0':x0,
            'y0':y0,
            'z0':z0,
            'zone':zone,
            'type_confidence':type_confidence,
            'plate_time':plate_time,
            'extension':extension,
            'spin_rate':spin_rate,
            'spin_direction':spin_direction,
            'ivb':ivb,
            'hb':hb,
            'launch_speed':launch_speed,
            'launch_angle':launch_angle,
            'launch_distance':launch_distance,
            'launch_location':launch_location,
            'trajectory':trajectory,
            'hardness':hardness,
            'hit_x':hit_x,
            'hit_y':hit_y,
            'index_play':index_play,
            'play_id':play_id,
            'start_time':start_time,
            'end_time':end_time,
            'is_pitch':is_pitch,
            'type_type':type_type,
            'type_ab':type_ab,
            'event':event,
            'event_type':event_type,
            'rbi':rbi,
            'away_score':away_score,
            'home_score':home_score,

            }
            )
        return df

    def get_players(self,sport_id=1):
        player_data = requests.get(url=f'https://statsapi.mlb.com/api/v1/sports/{sport_id}/players').json()

        #Select relevant data that will help distinguish players from one another
        fullName_list = [x['fullName'] for x in player_data['people']]
        id_list = [x['id'] for x in player_data['people']]
        position_list = [x['primaryPosition']['abbreviation'] for x in player_data['people']]
        team_list = [x['currentTeam']['id']for x in player_data['people']]
        age_list = [x['currentAge']for x in player_data['people']]

        player_df = pd.DataFrame(data={'player_id':id_list,
                        'name':fullName_list,
                        'position':position_list,
                        'team':team_list,
                        'age':age_list})
        return player_df

    def get_teams(self):
        teams =  requests.get(url='https://statsapi.mlb.com/api/v1/teams/').json()
        #Select only teams that are at the MLB level
        # mlb_teams_city = [x['franchiseName'] for x in teams['teams'] if x['sport']['name'] == 'Major League Baseball']
        # mlb_teams_name = [x['teamName'] for x in teams['teams'] if x['sport']['name'] == 'Major League Baseball']
        # mlb_teams_franchise = [x['name'] for x in teams['teams'] if x['sport']['name'] == 'Major League Baseball']
        # mlb_teams_id = [x['id'] for x in teams['teams'] if x['sport']['name'] == 'Major League Baseball']
        # mlb_teams_abb = [x['abbreviation'] for x in teams['teams'] if x['sport']['name'] == 'Major League Baseball']

        mlb_teams_city = [x['franchiseName']  if 'franchiseName' in x else None for x in teams['teams']]
        mlb_teams_name = [x['teamName']  if 'franchiseName' in x else None for x in teams['teams']]
        mlb_teams_franchise = [x['name']  if 'franchiseName' in x else None for x in teams['teams']]
        mlb_teams_id = [x['id']  if 'franchiseName' in x else None for x in teams['teams']]
        mlb_teams_abb = [x['abbreviation']  if 'franchiseName' in x else None for x in teams['teams']]
        mlb_teams_parent_id = [x['parentOrgId']  if 'parentOrgId' in x else None for x in teams['teams']]
        mlb_teams_parent = [x['parentOrgName']  if 'parentOrgName' in x else None for x in teams['teams']]
        mlb_teams_league_id = [x['league']['id']  if 'id' in x['league'] else None for x in teams['teams']]
        mlb_teams_league_name = [x['league']['name']  if 'name' in x['league'] else None for x in teams['teams']]



        #Create a dataframe of all the teams
        mlb_teams_df = pd.DataFrame(data={'team_id':mlb_teams_id,
                                          'city':mlb_teams_franchise,
                                          'name':mlb_teams_name,
                                          'franchise':mlb_teams_franchise,
                                          'abbreviation':mlb_teams_abb,
                                          'parent_org_id':mlb_teams_parent_id,
                                          'parent_org':mlb_teams_parent,
                                          'league_id':mlb_teams_league_id,
                                          'league_name':mlb_teams_league_name

                                          }).drop_duplicates().dropna(subset=['team_id']).reset_index(drop=True).sort_values('team_id')

        mlb_teams_df.loc[mlb_teams_df['parent_org_id'].isnull(),'parent_org_id'] = mlb_teams_df.loc[mlb_teams_df['parent_org_id'].isnull(),'team_id']
        mlb_teams_df.loc[mlb_teams_df['parent_org'].isnull(),'parent_org'] = mlb_teams_df.loc[mlb_teams_df['parent_org'].isnull(),'franchise']


        mlb_teams_df['parent_org_abbreviation'] = mlb_teams_df['parent_org_id'].map(mlb_teams_df.set_index('team_id')['abbreviation'].to_dict())


        #mlb_teams_df.loc[mlb_teams_df.franchise.isin(mlb_teams_df.parent_org.unique()),'parent_org'] = mlb_teams_df.loc[mlb_teams_df.franchise.isin(mlb_teams_df.parent_org.unique()),'franchise']

        return mlb_teams_df

    def get_leagues(self):
        leagues = requests.get(url='https://statsapi.mlb.com/api/v1/leagues/').json()

        sport_id = [x['sport']['id'] if 'sport' in x else None for x in leagues['leagues']]
        league_id = [x['id']  if 'id' in x else None for x in leagues['leagues']]
        league_name = [x['name']  if 'name' in x else None for x in leagues['leagues']]
        league_abbreviation = [x['abbreviation']  if 'abbreviation' in x else None for x in leagues['leagues']]



        leagues_df = pd.DataFrame(data= {
                                    'league_id':league_id,
                                    'league_name':league_name,
                                    'league_abbreviation':league_abbreviation,
                                    'sport_id':sport_id,
                                    })

        return leagues_df

    def get_player_games_list(self,player_id=691587):
        player_game_list = [x['game']['gamePk'] for x in requests.get(url=f'http://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=stats(type=gameLog,season=2023),hydrations').json()['people'][0]['stats'][0]['splits']]
        return player_game_list

    def get_team_schedule(self,year=2023,sport_id=1,mlb_team='Toronto Blue Jays'):
        if not self.get_sport_id_check(sport_id=sport_id):
            print('Please Select a New Sport ID from the following')
            print(self.get_sport_id())
            return False, False

        schedule_df = self.get_schedule(year_input=year,sport_id=sport_id)
        teams_df = self.get_teams().merge(self.get_leagues()).merge(self.get_sport_id(),left_on=['sport_id'],right_index=True,suffixes=['','_sport'])
        teams_df = teams_df[teams_df['sport_id'] == sport_id]
        team_abb_select = teams_df[teams_df['parent_org'] == mlb_team]['abbreviation'].values[0]
        team_name_select = teams_df[teams_df['parent_org'] == mlb_team]['franchise'].values[0]
        schedule_df = schedule_df[((schedule_df.away == team_name_select) | (schedule_df.home == team_name_select)) & (schedule_df.state == 'F')].reset_index(drop=True)
        return schedule_df,teams_df

    def get_team_game_data(self,year=2023,sport_id=1,mlb_team='Toronto Blue Jays'):
        schedule_df,teams_df = self.get_team_schedule(year=year,sport_id=sport_id,mlb_team=mlb_team)
        if not schedule_df:
            return
        data = self.get_data(schedule_df['game_id'][:])
        df = self.get_data_df(data_list = data)
        df['mlb_team'] = teams_df[teams_df['parent_org'] == mlb_team]['parent_org_abbreviation'].values[0]
        df['level'] = teams_df[teams_df['parent_org'] == mlb_team]['abbreviation_sport'].values[0]

        return df
