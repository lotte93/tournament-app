import streamlit as st
from streamlit_gsheets import GSheetsConnection
from utils import COLS


@st.cache_resource(show_spinner='Connecting with Spreadsheet')
def get_sheet_connection():
    return st.connection("gsheets", type=GSheetsConnection)


@st.cache_data(show_spinner='Ophalen schema')
def get_schema():
    df_schema = get_sheet_connection().read(worksheet='schema', ttl=5)
    df_schema = df_schema[COLS]
    df_schema = df_schema[df_schema['match_time'].notnull()]
    return df_schema


@st.cache_data(ttl=5, show_spinner='Ophalen resultaten')
def get_results():
    df_results = get_sheet_connection().read(worksheet='resultaten', ttl=5)
    cols_to_keep = COLS + ['score_home', 'score_away']
    df_results = df_results[cols_to_keep]
    df_results = df_results[df_results['match_time'].notnull()]
    return df_results


def write_results(df):
    conn = get_sheet_connection()
    conn.update(worksheet="resultaten", data=df)
