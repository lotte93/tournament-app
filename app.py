import streamlit as st
from sheet_connection import get_schema, get_results
from ui import UpcomingMatchesTab, StandingsTab, FinalsTab
from utils import get_language_dict

st.set_page_config(layout='wide')

st.title('Amelisweerdcup 2024')
st.logo('amelisweerdcup_logo.png')
language = 'dutch'
language_dict = get_language_dict(language)

if 'df_schema' not in st.session_state:
    st.session_state.df_schema = get_schema()

if 'df_results' not in st.session_state:
    st.session_state.df_results = get_results()

upcoming_matches_tab = UpcomingMatchesTab(language_dict)
standings_tab = StandingsTab(language_dict, show_compute_button=False)
finals_tab = FinalsTab(language_dict)

tabs_to_show = [standings_tab, upcoming_matches_tab, finals_tab]

tabs = st.tabs([tab.name for tab in tabs_to_show])

for i, tab in enumerate(tabs):
    with tab:
        tabs_to_show[i].generate_ui()
