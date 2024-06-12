import datetime
import pandas as pd
import streamlit as st

from standings import compute_standings
from utils import COLS
from sheet_connection import write_results


class Tab:
    def __init__(self, name: str, subheader: str):
        self.name = name
        self.subheader = subheader

    def generate_header_and_subheader(self):
        st.header(self.name)
        st.caption(self.subheader)

    def generate_ui(self):
        ...


class UpcomingMatchesTab(Tab):
    def __init__(self, language_dict: dict, show_current_time: bool = True):
        self.show_current_time = show_current_time
        self.language_dict = language_dict
        super().__init__(name=self.language_dict.get('upcoming_matches_title'),
                         subheader=self.language_dict.get('upcoming_matches_sh'))

    def generate_ui(self):
        self.generate_header_and_subheader()
        if self.show_current_time:
            self._show_current_time_matches()
        self._show_all_matches()

    def _show_current_time_matches(self):
        current_time = datetime.datetime.now()
        if st.button(self.language_dict.get('new_timeslot')):
            current_time = datetime.datetime.now()
        st.write(f"{self.language_dict.get('the_time_is')} {current_time.strftime('%H:%M')}.")
        match_times = pd.to_datetime(st.session_state.df_schema['match_time'])
        minutes_difference = match_times.apply(
            lambda x: (x.hour - current_time.hour) * 60 + (x.minute - current_time.minute)
        )
        st.dataframe(st.session_state.df_schema[minutes_difference.between(0, 25)], hide_index=True)

    def _show_all_matches(self):
        if st.checkbox(self.language_dict.get('show_matches')):
            st.dataframe(st.session_state.df_schema, hide_index=True)


class WriteResultsTab(Tab):
    def __init__(self, language_dict: dict, show_per_tournament: bool = True):
        super().__init__(name=language_dict.get('write_results_title'),
                         subheader=language_dict.get('write_results_sh'))
        self.language_dict = language_dict
        self.show_per_tournament = show_per_tournament

    def generate_ui(self):
        self.generate_header_and_subheader()
        if self.show_per_tournament:
            tab_a, tab_b = st.tabs(
                [
                    f"Per {self.language_dict.get('timeslot')}",
                    f"Per {self.language_dict.get('tournament')}"
                 ]
            )
            with tab_a:
                self._per_time_slot()
            with tab_b:
                self._per_tournament()
        else:
            self._per_time_slot()

    def _show_and_write_results(self, df_results, edited_data, button_key):
        if st.button(self.language_dict.get('store_results'), key=button_key):
            new_data = pd.concat([df_results, edited_data]).drop_duplicates(
                ['match_time', 'home_team', 'away_team'],
                keep='last'
            ).sort_values('match_time')
            write_results(new_data)
            st.success(self.language_dict.get('store_results_success'))
            st.balloons()
            st.session_state.df_results = new_data  # also update in session state

    def _edit_results(self, data_to_show):
        return st.data_editor(
            data_to_show,
            disabled=COLS,
            column_config={
                'score_home': st.column_config.NumberColumn(self.language_dict.get('score_home'),
                                                            min_value=0,
                                                            max_value=20),
                'score_away': st.column_config.NumberColumn(self.language_dict.get('score_away'),
                                                            min_value=0,
                                                            max_value=20)
            },
            hide_index=True
        )

    def _per_time_slot(self):
        match_times_list = st.session_state.df_results['match_time'].unique().tolist()
        selected_time = st.selectbox(self.language_dict.get('timeslot'), match_times_list)
        data_to_show = st.session_state.df_results[st.session_state.df_results['match_time'] == selected_time]
        edited_data = self._edit_results(data_to_show)
        self._show_and_write_results(st.session_state.df_results, edited_data, button_key='per_timeslot')

    def _per_tournament(self):
        tournaments_list = st.session_state.df_results['tournament'].unique().tolist()
        selected_tournament = st.selectbox(self.language_dict.get('tournament'), tournaments_list)
        data_to_show = st.session_state.df_results[st.session_state.df_results['tournament'] == selected_tournament]
        edited_data = self._edit_results(data_to_show)
        self._show_and_write_results(st.session_state.df_results, edited_data, button_key='per_tournament')


class StandingsTab(Tab):
    def __init__(self, language_dict: dict, show_compute_button: bool=True):
        self.show_compute_button = show_compute_button
        self.language_dict = language_dict
        super().__init__(name=self.language_dict.get('standings_title'),
                         subheader=self.language_dict.get('standings_sh'))

    def generate_ui(self):
        self.generate_header_and_subheader()
        if self.show_compute_button:
            if st.button(self.language_dict.get('compute_standings')):
                self._compute_and_show_standings()
        else:
            self._compute_and_show_standings()

    def _compute_and_show_standings(self):
        df_team_scores = compute_standings(st.session_state.df_results)
        tournaments_list = df_team_scores['tournament'].unique().tolist()
        tabs = st.tabs(tournaments_list)
        for i, tab in enumerate(tabs):
            with tab:
                df_scores_tournament = df_team_scores[df_team_scores['tournament'] == tournaments_list[i]]
                for group, data in df_scores_tournament.groupby('group'):
                    st.subheader(group)
                    st.dataframe(data[['team', 'total_points', 'goals_for', 'goals_against', 'goal_difference']],
                                 hide_index=True)


class FinalsTab(Tab):
    def __init__(self, language_dict: dict):
        self.language_dict = language_dict
        super().__init__(name=self.language_dict.get('finals_title'),
                         subheader=self.language_dict.get('finals_sh'))

    def generate_ui(self):
        self.generate_header_and_subheader()
        # st.dataframe(st.session_state.df_schema[~(st.session_state.df_schema['group'].astype(str).startswith('Poule'))])
