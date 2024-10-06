import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos desde CSV
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("colegio_sena.csv")
        print("Datos cargados exitosamente")
        return data
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# Gráfico de barras de edades de estudiantes
def grafico_edades(df):
    fig = px.histogram(df, x='Edad', title='Distribución de Edades de los Estudiantes')
    return fig

# Gráfico de barras de promedio por grado
def grafico_promedio_grado(df):
    promedio_por_grado = df.groupby('Grado')['Promedio'].mean().reset_index()
    fig = px.bar(promedio_por_grado, x='Grado', y='Promedio', title='Promedio por Grado')
    return fig

# Gráfico de pie de distribución de estudiantes por grado
def grafico_distribucion_grado(df):
    conteo_por_grado = df['Grado'].value_counts().reset_index()
    conteo_por_grado.columns = ['Grado', 'Cantidad']
    fig = px.pie(conteo_por_grado, values='Cantidad', names='Grado', title='Distribución de Estudiantes por Grado')
    return fig

# Gráfico de barras de los dos mejores promedios por grado
def grafico_mejores_promedios(df):
    mejores_promedios = df.groupby('Grado').apply(lambda x: x.nlargest(2, 'Promedio')).reset_index(drop=True)
    fig = px.bar(mejores_promedios, x='Grado', y='Promedio', color='Nombre',
                 title='Dos Mejores Promedios por Grado', barmode='group')
    return fig

# Gráfico de rendimiento (pasaron/no pasaron)
def grafico_rendimiento(df):
    df['Estado'] = df['Promedio'].apply(lambda x: 'Pasó' if x >= 3.0 else 'No Pasó')
    conteo_estado = df['Estado'].value_counts().reset_index()
    conteo_estado.columns = ['Estado', 'Cantidad']
    fig = px.bar(conteo_estado, x='Estado', y='Cantidad', title='Estudiantes que Pasaron y No Pasaron el Periodo')
    return fig

# Aplicación Streamlit
def main():
    st.title('Visualizador de Datos del Colegio SENA')

    # Cargar datos
    df = load_data()

    if df.empty:
        st.error("No se pudieron cargar los datos. Por favor, verifica el archivo CSV.")
        return

    # Mostrar datos en una tabla
    st.subheader('Datos del Colegio')
    st.dataframe(df)

    # Gráfico de edades
    st.subheader('Distribución de Edades de los Estudiantes')
    st.plotly_chart(grafico_edades(df))

    # Gráfico de promedio por grado
    st.subheader('Promedio por Grado')
    st.plotly_chart(grafico_promedio_grado(df))

    # Gráfico de distribución de estudiantes por grado
    st.subheader('Distribución de Estudiantes por Grado')
    st.plotly_chart(grafico_distribucion_grado(df))

    # Gráfico de los dos mejores promedios por grado
    st.subheader('Dos Mejores Promedios por Grado')
    st.plotly_chart(grafico_mejores_promedios(df))

    # Gráfico de rendimiento
    st.subheader('Rendimiento Estudiantil')
    st.plotly_chart(grafico_rendimiento(df))

    # Filtro de estudiantes
    st.subheader('Filtro de Estudiantes')
    nombre_buscar = st.text_input('Buscar estudiante por nombre:')

    if nombre_buscar:
        estudiantes_filtrados = df[df['Nombre'].str.contains(nombre_buscar, case=False)]
        if not estudiantes_filtrados.empty:
            st.dataframe(estudiantes_filtrados)
        else:
            st.write('No se encontraron estudiantes con ese nombre.')

if __name__ == '__main__':
    main()