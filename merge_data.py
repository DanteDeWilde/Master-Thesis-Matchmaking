import pandas as pd

folders = ['data_america', 'data_asia', 'data_europe', 'data_sea']
merged_tables = []

if __name__ == '__main__':
    for folder in folders:
        # merge the 3 tables with each other into one table
        df_matches = pd.read_csv(f'{folder}/matches.csv',sep=';',decimal='.', dtype=str)
        df_player_match_info = pd.read_csv(f'{folder}/player_match_info.csv',sep=';',decimal='.',dtype=str)
        df_team_match_info = pd.read_csv(f'{folder}/team_match_info.csv', sep=';', decimal='.',dtype=str)

        # remove duplicates
        df_matches.drop_duplicates(subset=['gameId'], inplace=True)
        df_player_match_info.drop_duplicates(subset=['gameId', 'puuid'], inplace=True)
        df_team_match_info.drop_duplicates(subset=['match_UUID', 'teamId'], inplace=True)

        merged = pd.merge(df_player_match_info, df_matches, how='left', on='match_UUID')
        merged = pd.merge(merged, df_team_match_info, how='left', on=['match_UUID', 'teamId'])

        merged_tables.append(merged)

    pd.concat(merged_tables).to_excel(f'merged.xlsx', index=False)
