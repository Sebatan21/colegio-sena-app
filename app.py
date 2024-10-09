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
with open('config.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Configuración del autenticador
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config.get('preauthorized', [])
)

# Función para cargar datos
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("colegio_sena.csv")
        return data
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# Gráfico de barras de edades de estudiantes
def grafico_edades(df):
    conteo_edades = df['Edad'].value_counts().reset_index()
    conteo_edades.columns = ['Edad', 'Cantidad']
    fig = px.bar(conteo_edades, x='Edad', y='Cantidad', title='Distribución de Edades de los Estudiantes',
                 color='Edad', color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

# Gráfico de promedio por grado
def grafico_promedio_grado(df):
    promedio_por_grado = df.groupby('Grado')['Promedio'].mean().reset_index()
    fig = px.bar(promedio_por_grado, x='Grado', y='Promedio', title='Promedio por Grado',
                 color='Grado', color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

# Gráfico de pie de distribución de estudiantes por grado
def grafico_distribucion_grado(df):
    conteo_por_grado = df['Grado'].value_counts().reset_index()
    conteo_por_grado.columns = ['Grado', 'Cantidad']
    fig = px.pie(conteo_por_grado, values='Cantidad', names='Grado', title='Distribución de Estudiantes por Grado',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

# Gráfico de los dos mejores promedios por grado
def grafico_mejores_promedios(df):
    mejores_promedios = df.groupby('Grado').apply(lambda x: x.nlargest(2, 'Promedio')).reset_index(drop=True)
    fig = px.bar(mejores_promedios, x='Grado', y='Promedio', color='Nombre',
                 title='Dos Mejores Promedios por Grado', barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

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
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

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
        
        # Obtener información sobre streamlit_authenticator
        st.write("Versión de streamlit_authenticator:", getattr(stauth, '__version__', 'Desconocida'))

        # Mostrar métodos disponibles en el autenticador
        st.write("Métodos disponibles en el autenticador:")
        st.write(dir(authenticator))
        
        # Autenticación
        auth_name, auth_status, auth_username = authenticator.login("Login", "main")

        if auth_status:
            # Autenticación exitosa
            authenticator.logout("Logout", "main", key="unique_key")
            st.write(f'Welcome *{auth_name}*')
            
            st.title('Visualizador de Datos del Colegio SENA')
            
            # Cargar datos
            df = load_data()
            
            if df.empty:
                st.warning("No se pudieron cargar los datos.")
                return

            # Filtro de estudiantes mejorado
            st.subheader('Filtro de Estudiantes')
            
            metodo_busqueda = st.radio("Selecciona el método de búsqueda:", ("Lista desplegable", "Búsqueda por nombre"))

            if metodo_busqueda == "Lista desplegable":
                estudiante_seleccionado = st.selectbox('Selecciona un estudiante:', df['Nombre'].tolist())
                if estudiante_seleccionado:
                    info_estudiante = df[df['Nombre'] == estudiante_seleccionado]
                    st.write(info_estudiante)
            else:
                nombre_buscar = st.text_input('Buscar estudiante por nombre:')
                if nombre_buscar:
                    estudiantes_filtrados = df[df['Nombre'].str.contains(nombre_buscar, case=False)]
                    if not estudiantes_filtrados.empty:
                        seleccion = st.selectbox('Selecciona un estudiante:', estudiantes_filtrados['Nombre'].tolist())
                        estudiante_seleccionado = estudiantes_filtrados[estudiantes_filtrados['Nombre'] == seleccion]
                        st.write(estudiante_seleccionado)
                    else:
                        st.write('No se encontraron estudiantes con ese nombre.')

            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader('Distribución de Edades de los Estudiantes')
                st.plotly_chart(grafico_edades(df), use_container_width=True)

                st.subheader('Distribución de Estudiantes por Grado')
                st.plotly_chart(grafico_distribucion_grado(df), use_container_width=True)

            with col2:
                st.subheader('Promedio por Grado')
                st.plotly_chart(grafico_promedio_grado(df), use_container_width=True)

                st.subheader('Dos Mejores Promedios por Grado')
                st.plotly_chart(grafico_mejores_promedios(df), use_container_width=True)

            # Gráfico sobre rendimiento detallado
            st.subheader('Rendimiento Estudiantil Detallado')
            st.plotly_chart(grafico_rendimiento_detallado(df), use_container_width=True)

        elif auth_status == False:
            st.error('Username/password is incorrect')
        elif auth_status == None:
            st.warning('Please enter your username and password')

        # Registro de nuevos usuarios
        if auth_status != True:
            with st.expander("Registrarse"):
                if authenticator.register_user('Register user', preauthorization=False):
                    st.success('User registered successfully')

    except Exception as e:
        st.error(f"Error en la aplicación: {str(e)}")
        st.exception(e)

if __name__ == '__main__':
    main()