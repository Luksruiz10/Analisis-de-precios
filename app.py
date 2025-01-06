import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
from Precio_ofertas import precio_ofertas
from Canasta_basica import canasta_basica
from Categorias import categorias

st.title('Proyecto Mercadona')
menu = ['Precios y ofertas', 'Canasta basica', 'Catergorias']
choice = st.sidebar.selectbox('Menu', menu)

if choice == 'Precios y ofertas':
    precio_ofertas()
elif choice == 'Canasta basica':
    canasta_basica()
elif choice == 'Catergorias':
    categorias()
