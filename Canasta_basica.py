import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

meses_es = {
    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
    'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
    'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
    'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
}

def canasta_basica():

    lista_cb = [83203.1,5063.0,6250.0,16807,8280,3824,3277,69166,69975,69586,69122,69495,10380,22313,51191,3724,2900,31504,5330,5219,4640,20716,13810,19897,19731,11172,52967,34171,86656,5598]
    conn = sqlite3.connect('Mercadona.db')
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in lista_cb)

    query = f'''
            SELECT * FROM Principal
            WHERE Id_Producto IN ({placeholders})
        '''
        
    df_producto = pd.read_sql_query(query, conn,params=lista_cb)
    df_producto[df_producto["Id_Producto"]==4640.0]
    df_producto.sort_values('Fecha', inplace=True)

    conn.close()

    #Canasta basica del dia actual
    #df_canasta_basica_dia = df_producto[df_producto["Fecha"]==datetime.now().strftime("%Y-%m-%d")]
    df_canasta_basica_dia = df_producto[df_producto["Fecha"]=="2025-01-06"]
    #Grafico   
    total = df_canasta_basica_dia["Precio"].sum().round(2)  # Aquí pondrías el total calculado de tu tabla
    # HTML y CSS para la tarjeta
    st.markdown(
        f"""
        <div style="
            background-color: #f0f8ff;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h1 style="color: #2e86c1;">Total</h1>
            <h2 style="color: #1e8449; font-size: 36px;">{total}€</h2>
        </div>
        """,
        unsafe_allow_html=True
    )



    #Historial de precio de la canasta basica
    df_canasta_basica = df_producto.pivot_table(
        index="Fecha",
        values="Precio",
        aggfunc="sum"
    )
    #Grafico
    fig1 = px.line(df_canasta_basica, x=df_canasta_basica.index, y="Precio")
    st.plotly_chart(fig1)
    
    

    #Variacion de precio de los productos la canasta basica individualmente
    opciones_productos = ["Todos"] + sorted(df_producto["Nombre"].drop_duplicates().tolist())

    # Crear el selectbox
    producto_seleccionado = st.selectbox("Selecciona un producto:", opciones_productos)

    # Filtrar el DataFrame según la selección
    if producto_seleccionado == "Todos":
        df_filtrado = df_producto
        fig = px.line(df_filtrado, x="Fecha", y="Precio", color="Nombre", title="Evolución de precios")
        st.plotly_chart(fig)
    else:
        df_filtrado = df_producto[df_producto["Nombre"] == producto_seleccionado]
        fig = px.line(df_filtrado, x="Fecha", y="Precio", color="Nombre", title="Evolución de precios")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
    
    
    
    #Variacion de precio de los productos la canasta basica porcentualmente
    # Convertir la columna "Fecha" a tipo datetime
    df_canasta_basica.index = pd.to_datetime(df_canasta_basica.index)
    df_canasta_basica["Mes_Ajustado"] = (df_canasta_basica.index - pd.Timedelta(days=1)).to_period("M")
    df_canasta_basica["Mes_Nombre"] = df_canasta_basica["Mes_Ajustado"].dt.strftime('%B %Y')
    df_canasta_basica["Mes_Nombre"] = df_canasta_basica["Mes_Nombre"].replace(meses_es, regex=True)
    # Filtrar el primer día de cada mes
    primer_dia_mes = df_canasta_basica.groupby(df_canasta_basica.index.to_period("M")).first()

    # Calcular la variación porcentual
    primer_dia_mes["Variacion_Porcentual"] = (
        primer_dia_mes["Precio"].pct_change() * 100
    )
    primer_dia_mes = primer_dia_mes.sort_values("Mes_Ajustado", ascending=False)
    primer_dia_mes.dropna(inplace=True)
    primer_dia_mes["Variacion_Porcentual"] = primer_dia_mes["Variacion_Porcentual"].apply(lambda x: f"{x * 1:.1f}")
    primer_dia_mes["Variacion_Porcentual"] = pd.to_numeric(primer_dia_mes["Variacion_Porcentual"], errors="coerce")
    
    
    url = "https://datosmacro.expansion.com/ipc-paises/espana?sector=IPC+General&sc=IPC-IG"  # Reemplaza con la URL de la página que contiene la tabla
    # Leer las tablas HTML
    tables = pd.read_html(url)

    # Si hay más de una tabla, 'tables' será una lista de DataFrames
    # Si solo hay una tabla, puedes acceder directamente al primer elemento de la lista
    df_inflacion = tables[0]  # Accede a la primera tabla

    # Mostrar el DataFrame resultante
    df_inflacion = df_inflacion[['Unnamed: 0','Variación mensual']]
    df_inflacion.rename(columns={'Unnamed: 0':'Mes', 'Variación mensual':'Inflacion Mensual' },inplace=True)
    df_inflacion = df_inflacion.iloc[0:6]
    
    # Combinar ambos DataFrames por la columna "Mes_Nombre"
    variacion_porcentual_mercadona = primer_dia_mes["Variacion_Porcentual"].reset_index()
    variacion_porcentual_mercadona = variacion_porcentual_mercadona["Variacion_Porcentual"]
    df_combined = pd.concat([df_inflacion, variacion_porcentual_mercadona], axis=1)
    df_combined.sort_index(ascending=False, inplace=True)
    df_combined["Inflacion Mensual"] = df_combined["Inflacion Mensual"].str.replace('%', '').str.replace(',', '.')
    df_combined["Inflacion Mensual"] = pd.to_numeric(df_combined["Inflacion Mensual"], errors="coerce")
    
    # Mostrar el DataFrame combinado
    st.subheader("Variación de Precios mensual Vs. Inflación Mensual")
    df_combined.rename(columns={'Variacion_Porcentual':'Variacion de Precios(%)'},inplace=True)

    fig = px.bar(df_combined, x="Mes", y=["Inflacion Mensual", "Variacion de Precios(%)"], labels={'value': 'Variación (%)', 'variable': 'Tipo de variación'})
    fig.update_layout(barmode='group')
    #fig.update_yaxes(range=[-0.5, max(df_combined["Variacion mensual"].max(), 0) * 1.1], 
    #zeroline=True, zerolinewidth=2, zerolinecolor='gray')
    st.plotly_chart(fig)
    
    st.dataframe(df_combined)