import streamlit as st
from authentication import check_password
from sheet_connection import get_schema, get_results
from ui import UpcomingMatchesTab, WriteResultsTab, StandingsTab, FinalsTab
from utils import get_language_dict

st.set_page_config(layout='wide')

st.title('Zomer Avond Toernooi 2024')
language = 'dutch'
language_dict = get_language_dict(language)

# if not check_password(language_dict):
#     st.stop()  # Do not continue if correct password not provided.

if 'df_schema' not in st.session_state:
    st.session_state.df_schema = get_schema()

if 'df_results' not in st.session_state:
    st.session_state.df_results = get_results()

upcoming_matches_tab = UpcomingMatchesTab(language_dict, show_current_time=False)
write_results_tab = WriteResultsTab(language_dict, show_per_date=True)
standings_tab = StandingsTab(language_dict)

tabs_to_show = [upcoming_matches_tab, standings_tab, write_results_tab]

tabs = st.tabs([tab.name for tab in tabs_to_show])

for i, tab in enumerate(tabs):
    with tab:
        if tabs_to_show[i].name == language_dict.get('write_results_title'):
            if check_password(language_dict):
                tabs_to_show[i].generate_ui()
        else:
            tabs_to_show[i].generate_ui()
