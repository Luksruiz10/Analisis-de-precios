import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

meses_es = {
    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
    'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
    'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
    'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
}

def calcular_variacion_porcentual(valor_inicial, valor_final):
    return round(((valor_final - valor_inicial) / abs(valor_inicial)) * 100, 2)
def categorias():
    
    conn = sqlite3.connect('Mercadona.db')
    cursor = conn.cursor()

    query = """
    SELECT * FROM Principal"""
    df = pd.read_sql_query(query, conn)
    #st.dataframe(df)

    conn.close()

    Productos_Por_Categoria = df.pivot_table(values='Precio',
                                                    index=['Nombre_Cat', 'Fecha'],
                                                    aggfunc='sum').reset_index()
    #st.dataframe(Productos_Por_Categoria)
    fig = px.line(Productos_Por_Categoria, x="Fecha", y="Precio", color="Nombre_Cat", title="Evolución de precios")
    #st.plotly_chart(fig)
        
    Productos_Por_Categoria['Variacion'] = Productos_Por_Categoria.groupby('Nombre_Cat')['Precio'].transform(lambda x: calcular_variacion_porcentual(x.shift(1), x))
    #st.dataframe(Productos_Por_Categoria)
        
    Productos_Por_Categoria['Fecha'] = pd.to_datetime(Productos_Por_Categoria['Fecha'])
    Productos_Por_Categoria['Mes'] = Productos_Por_Categoria['Fecha'].dt.to_period('M')
    #Productos_Por_Categoria['Mes'] = Productos_Por_Categoria['Fecha'].dt.month_name()
    #Productos_Por_Categoria["Mes"] = Productos_Por_Categoria["Mes"].replace(meses_es, regex=True)
    #st.dataframe(Productos_Por_Categoria)
        
    Variacion_Mensual = Productos_Por_Categoria.groupby(['Nombre_Cat', 'Mes'])['Precio']
    Variacion_Mensual = Variacion_Mensual.agg(['first', 'last'])
    Variacion_Mensual.reset_index(inplace=True)
    #Variacion_Mensual["Mes"] = Variacion_Mensual["Mes"].dt.month_name()
    Variacion_Mensual["variacion"] = calcular_variacion_porcentual(Variacion_Mensual["first"], Variacion_Mensual["last"])
    Variacion_Mensual
    
    mes = st.selectbox('Selecciona un mes', Variacion_Mensual['Mes'].unique())
    df_mes = Variacion_Mensual[Variacion_Mensual['Mes'] == mes]
    fig = px.bar(df_mes, x='Nombre_Cat', y='variacion', title=f'Variación de precios en {mes}', color=df_mes['variacion'] > 0,  # True si es mayor a 0, False si es menor
    color_discrete_map={True: 'red', False: 'green'})
    fig.update_traces(showlegend=False)
    fig.update_layout(
    xaxis_title="Categoría", 
    yaxis_title="Variación (%)"
    )
    st.plotly_chart(fig)
    
    
    top_3_ascendente = df_mes.nlargest(3, 'variacion')
    top_3_descendente = df_mes.nsmallest(3, 'variacion')

    # Crear 2 columnas para los carteles
    col1, col2 = st.columns(2)

    # Mostrar carteles de las categorías que más subieron
    with col1:
        st.markdown("### Top 3 Categorías que más aumentaron")
        for i, row in top_3_ascendente.iterrows():
            st.metric(label=row['Nombre_Cat'], value=f"{row['variacion']:.2f}%", delta=f"{row['variacion']:.2f}%", delta_color="inverse")

    # Mostrar carteles de las categorías que más bajaron
    with col2:
        st.markdown("### Top 3 Categorías que más bajaron")
        for i, row in top_3_descendente.iterrows():
            st.metric(label=row['Nombre_Cat'], value=f"{row['variacion']:.2f}%", delta=f"{row['variacion']:.2f}%", delta_color="inverse")
    
    
    
    Variacion_hasta_actualidad = Productos_Por_Categoria.groupby('Nombre_Cat')['Precio']
    Variacion_hasta_actualidad = Variacion_hasta_actualidad.agg(['first', 'last'])
    Variacion_hasta_actualidad.reset_index(inplace=True)
    Variacion_hasta_actualidad["variacion"] = calcular_variacion_porcentual(Variacion_hasta_actualidad["first"], Variacion_hasta_actualidad["last"])
    fig = px.bar(Variacion_hasta_actualidad, 
                x='Nombre_Cat',
                y='variacion', 
                title='Variación de precios desde el 1 de noviembre de 2024 hasta la actualidad',
                color=Variacion_hasta_actualidad['variacion'] > 0,  # True si es mayor a 0, False si es menor
                color_discrete_map={True: 'red', False: 'green'},
                labels={'variacion': 'Variación (%)', 'Nombre_Cat': 'Categoria', True: 'Aumento', False: 'Bajo'}
                )
    fig.update_traces(showlegend=False)
    st.plotly_chart(fig)

        