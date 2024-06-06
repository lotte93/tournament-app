import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd

AUTHORIZED_EMAILS = st.secrets.authorization.emails
is_authorized = st.experimental_user.email in AUTHORIZED_EMAILS

st.set_page_config(layout='wide')
st.title('Amelisweerdcup 2024')

st.logo('amelisweerdcup_logo.png')

cols = ['match_time', 'pitch', 'referee', 'home_team', 'away_team', 'group', 'tournament']

st.write(st.experimental_user.email)


@st.cache_resource(show_spinner='Connecting with Spreadsheet')
def get_sheet_connection():
    return st.connection("gsheets", type=GSheetsConnection)


@st.cache_data(show_spinner='Ophalen schema')
def get_schema():
    df_schema = get_sheet_connection().read(worksheet='schema', ttl=5)
    df_schema = df_schema[cols]
    df_schema = df_schema[df_schema['match_time'].notnull()]
    return df_schema


@st.cache_data(ttl=5, show_spinner='Ophalen resultaten')
def get_results():
    df_results = get_sheet_connection().read(worksheet='resultaten', ttl=5)
    cols_to_keep = ['match_time', 'pitch', 'referee', 'home_team', 'away_team', 'group', 'tournament', 'score_thuis', 'score_uit']
    df_results = df_results[cols_to_keep]
    df_results = df_results[df_results['match_time'].notnull()]
    return df_results


conn = get_sheet_connection()
df_schema = get_schema()
df_results = get_results()


def compute_standings(df_results):
    df_results = df_results[(df_results['group'].str.startswith('Poule'))]
    df_scores = pd.concat(
        [
            df_results[['tournament', 'group', 'home_team', 'score_thuis', 'score_uit']].rename({
                'home_team': 'team',
                'score_thuis': 'score_team',
                'score_uit': 'score_opponent'
            }, axis=1),
            df_results[['tournament', 'group', 'away_team', 'score_uit', 'score_thuis']].rename({
                'away_team': 'team',
                'score_uit': 'score_team',
                'score_thuis': 'score_opponent'
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


tab1, tab2, tab3, tab4 = st.tabs(
    ["Komende wedstrijden",
     "Uitslagen invullen",
     "Huidige stand",
     "Finales"])

match_times_list = df_schema['match_time'].unique().tolist()
tournaments_list = df_schema['tournament'].unique().tolist()

with tab1:
    st.header('Komende wedstrijden')
    current_time = datetime.datetime.now()
    if st.button('Nieuw tijdstip'):
        current_time = datetime.datetime.now()
    st.write(f'Het is nu {current_time.strftime("%H:%M")}. Aankomende wedstrijden:')
    match_times = pd.to_datetime(df_schema['match_time'])
    minutes_difference = match_times.apply(
        lambda x: (x.hour - current_time.hour) * 60 + (x.minute - current_time.minute)
    )
    st.dataframe(df_schema[minutes_difference.between(0, 25)], hide_index=True)

    if st.checkbox('Laat alle wedstrijden zien'):
        st.dataframe(df_schema, hide_index=True)


with tab2:
    st.header('Uitslagen invullen')
    if is_authorized:
        tab2a, tab2b = st.tabs(
            ["Per tijdstip",
             "Per toernooi"
             ]
        )
        with tab2a:
            selected_time = st.selectbox('Tijdstip', match_times_list)

            edited_data = st.data_editor(
                df_results[df_results['match_time'] == selected_time],
                disabled=cols,
                column_config={
                    'score_thuis': st.column_config.NumberColumn('Score thuisteam',
                                                                 min_value=0,
                                                                 max_value=20),
                    'score_uit': st.column_config.NumberColumn('Score uitteam',
                                                               min_value=0,
                                                               max_value=20)
                },
                hide_index=True
            )

            if st.button('Sla uitslagen op', key='per_timeslot'):
                new_data = pd.concat([df_results, edited_data]).drop_duplicates(
                    ['match_time', 'home_team', 'away_team'],
                    keep='last'
                ).sort_values('match_time')
                conn.update(worksheet="resultaten", data=new_data)
                st.success('Uitslagen opgeslagen!')

        with tab2b:
            selected_tournament = st.selectbox('Toernooi', tournaments_list)

            edited_data = st.data_editor(
                df_results[df_results['tournament'] == selected_tournament],
                disabled=cols,
                column_config={
                    'score_thuis': st.column_config.NumberColumn('Score thuisteam',
                                                                 min_value=0,
                                                                 max_value=20),
                    'score_uit': st.column_config.NumberColumn('Score uitteam',
                                                               min_value=0,
                                                               max_value=20)
                },
                hide_index=True
            )

            if st.button('Sla uitslagen op', key='per_tournament'):
                new_data = pd.concat([df_results, edited_data]).drop_duplicates(
                    ['match_time', 'home_team', 'away_team'],
                    keep='last'
                ).sort_values('match_time')
                conn.update(worksheet="resultaten", data=new_data)
                st.success('Uitslagen opgeslagen!')
    else:
        st.warning('Je bent niet bevoegd om uitslagen in te vullen.')

with tab3:
    st.header('Stand')
    if st.button('Bereken stand'):
        df_team_scores = compute_standings(df_results)

        tabs = st.tabs(tournaments_list)
        for i, tab in enumerate(tabs):
            with tab:
                df_scores_tournament = df_team_scores[df_team_scores['tournament'] == tournaments_list[i]]
                for group, data in df_scores_tournament.groupby('group'):
                    st.subheader(group)
                    st.dataframe(data[['team', 'total_points', 'goals_for', 'goals_against', 'goal_difference']],
                                 hide_index=True)


with tab4:
    st.header('Finales')
    st.dataframe(df_schema[~(df_schema['group'].str.startswith('Poule'))])
