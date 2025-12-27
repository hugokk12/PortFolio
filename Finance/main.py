import streamlit as st
import pandas as pd
import json
import os
from scripts.streamlit_functions import *
from tempfile import NamedTemporaryFile

st.set_page_config(page_title="Finance Dashboard", layout="wide")


category_file = './Finance/data/categories.json'
    
try:
    with open(category_file, 'r') as f:
        st.session_state.categories = json.load(f)

except Exception as e:
    st.error(f"Error no category file: {e}")

 
main()

