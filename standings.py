import pandas as pd


def compute_standings(df_results):
    df_results = df_results[(df_results['group'].str.startswith('Poule'))]
    df_scores = pd.concat(
        [
            df_results[['tournament', 'group', 'home_team', 'score_home', 'score_away']].rename({
                'home_team': 'team',
                'score_home': 'score_team',
                'score_away': 'score_opponent'
            }, axis=1),
            df_results[['tournament', 'group', 'away_team', 'score_away', 'score_home']].rename({
                'away_team': 'team',
                'score_away': 'score_team',
                'score_home': 'score_opponent'
            }, axis=1)
        ],
        axis=0
    )
    df_scores['points'] = (
        (df_scores['score_team'] > df_scores['score_opponent']) * 3 +
        (df_scores['score_team'] == df_scores['score_opponent']) * 1
    )
    df_scores.loc[df_scores['score_team'].isna() | df_scores['score_opponent'].isna(), 'points'] = 0  # not played yet
    df_team_scores = df_scores.groupby(
        ['tournament', 'group', 'team'],
        as_index=False
    ).agg(
        total_points=('points', 'sum'),
        goals_for=('score_team', 'sum'),
        goals_against=('score_opponent', 'sum')
    )
    df_team_scores['goal_difference'] = df_team_scores['goals_for'] - df_team_scores['goals_against']

    df_team_scores = df_team_scores.sort_values(
        by=['total_points', 'goal_difference', 'goals_for'],
        ascending=[False, False, False]
    )

    return df_team_scores
