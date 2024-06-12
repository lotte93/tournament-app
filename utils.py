import yaml
import os
import streamlit as st

COLS = ['match_time', 'pitch', 'referee', 'home_team', 'away_team', 'group', 'tournament']


def get_language_dict(language):
    assert os.path.isfile(f'language_configs/{language}.yaml'), "There is no language file for this language"
    with open(f'language_configs/{language}.yaml') as f:
        language_dict = yaml.safe_load(f)
    return language_dict
