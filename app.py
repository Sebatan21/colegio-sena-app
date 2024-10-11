import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Visualizador de Datos del Colegio SENA", layout="wide")

# Cargar configuración desde el archivo YAML
@st.cache_resource
def load_config():
    with open('config.yml') as file:
        return yaml.load(file, Loader=SafeLoader)

# Función para cargar datos
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("colegio_sena.csv")
        return data
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

# Configuración global para los gráficos
def configure_plot(fig):
    fig.update_layout(
        dragmode=False,
        showlegend=True,
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True)
    )
    return fig

# Gráfico de barras de edades de estudiantes
def grafico_edades(df):
    conteo_edades = df['Edad'].value_counts().reset_index()
    conteo_edades.columns = ['Edad', 'Cantidad']
    fig = px.bar(conteo_edades, x='Edad', y='Cantidad', title='Distribución de Edades de los Estudiantes',
                 color='Edad', color_continuous_scale=px.colors.sequential.Viridis)
    return configure_plot(fig)

# Gráfico de promedio por grado
def grafico_promedio_grado(df):
    promedio_por_grado = df.groupby('Grado')['Promedio'].mean().reset_index()
    fig = px.bar(promedio_por_grado, x='Grado', y='Promedio', title='Promedio por Grado',
                 color='Grado', color_discrete_sequence=px.colors.qualitative.Set3)
    return configure_plot(fig)

# Gráfico de pie de distribución de estudiantes por grado
def grafico_distribucion_grado(df):
    conteo_por_grado = df['Grado'].value_counts().reset_index()
    conteo_por_grado.columns = ['Grado', 'Cantidad']
    fig = px.pie(conteo_por_grado, values='Cantidad', names='Grado', title='Distribución de Estudiantes por Grado',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    return configure_plot(fig)

# Gráfico de los dos mejores promedios por grado
def grafico_mejores_promedios(df):
    mejores_promedios = df.groupby('Grado').apply(lambda x: x.nlargest(2, 'Promedio')).reset_index(drop=True)
    fig = px.bar(mejores_promedios, x='Grado', y='Promedio', color='Nombre',
                 title='Dos Mejores Promedios por Grado', barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Bold)
    return configure_plot(fig)

# Gráfico de rendimiento detallado por estudiante y grado
def grafico_rendimiento_detallado(df):
    df['Estado'] = df['Promedio'].apply(lambda x: 'Pasó' if x >= 3.0 else 'No Pasó')
    df['Color'] = df['Estado'].map({'Pasó': 'green', 'No Pasó': 'red'})
    
    fig = go.Figure()
    
    for grado in df['Grado'].unique():
        df_grado = df[df['Grado'] == grado]
        fig.add_trace(go.Bar(
            x=df_grado['Nombre'],
            y=df_grado['Promedio'],
            name=grado,
            text=df_grado['Estado'],
            marker_color=df_grado['Color'],
            hoverinfo='text',
            hovertext=[f"Nombre: {nombre}<br>Grado: {grado}<br>Promedio: {promedio:.2f}<br>Estado: {estado}"
                       for nombre, grado, promedio, estado in zip(df_grado['Nombre'], df_grado['Grado'], df_grado['Promedio'], df_grado['Estado'])]
        ))
    
    fig.update_layout(
        title='Rendimiento Estudiantil por Grado',
        xaxis_title='Estudiantes',
        yaxis_title='Promedio',
        barmode='group'
    )
    return configure_plot(fig)

# Función principal de la aplicación
def main():
    try:
        # Estilo y fondo
        st.markdown(
            """
            <style>
            .stApp {
                background-image: linear-gradient(to right top, #d16ba5, #c777b9, #ba83ca, #aa8fd8, #9a9ae1, #8aa7ec, #79b3f4, #69bff8, #52cffe, #41dfff, #46eefa, #5ffbf1);
                background-attachment: fixed;
            }
            .stTitle, .stSubheader {
                color: #1E1E1E;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Cargar configuración
        config = load_config()
        
        # Configuración del autenticador
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config.get('preauthorized', [])
        )
        
        # Autenticación
        auth_name, auth_status, auth_username = authenticator.login("Login", "main")

        if auth_status == False:
            st.error('Username/password is incorrect')
        elif auth_status == None:
            st.warning('Please enter your username and password')

        if auth_status:
            # Autenticación exitosa
            authenticator.logout("Logout", "sidebar")
            st.sidebar.write(f'Welcome *{auth_name}*')
            
            st.title('Visualizador de Datos del Colegio SENA')
            
            # Cargar datos
            df = load_data()
            
            if df.empty:
                st.warning("No se pudieron cargar los datos.")
                return

            # Mostrar gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(grafico_edades(df), use_container_width=True, config={'displayModeBar': False})
                st.plotly_chart(grafico_distribucion_grado(df), use_container_width=True, config={'displayModeBar': False})

            with col2:
                st.plotly_chart(grafico_promedio_grado(df), use_container_width=True, config={'displayModeBar': False})
                st.plotly_chart(grafico_mejores_promedios(df), use_container_width=True, config={'displayModeBar': False})

            st.plotly_chart(grafico_rendimiento_detallado(df), use_container_width=True, config={'displayModeBar': False})

        # Registro de nuevos usuarios
        if auth_status != True:
            with st.expander("Registrarse"):
                if authenticator.register_user('Register user', preauthorization=False):
                    st.success('User registered successfully')

    except Exception as e:
        st.error(f"Error en la aplicación: {str(e)}")

if __name__ == '__main__':
    main()