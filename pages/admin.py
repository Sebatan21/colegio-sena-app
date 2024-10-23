# Crea un nuevo archivo llamado pages/admin.py
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import pandas as pd

st.set_page_config(page_title="Administración - Colegio SENA", layout="wide")

def load_config():
    with open('config.yml') as file:
        return yaml.load(file, Loader=SafeLoader)

def save_config(config):
    with open('config.yml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def admin_dashboard():
    st.title("Panel de Administración")

    config = load_config()

    # Verificar si hay usuarios registrados
    if 'credentials' in config and 'usernames' in config['credentials']:
        users_data = []
        for username, data in config['credentials']['usernames'].items():
            users_data.append({
                'Usuario': username,
                'Nombre': data['name'],
                'Email': data['email'],
                'Fecha de Registro': data.get('registration_date', 'No disponible')
            })
        
        users_df = pd.DataFrame(users_data)
        
        # Mostrar estadísticas
        st.subheader("Estadísticas de Usuarios")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Usuarios", len(users_data))
        
        # Mostrar tabla de usuarios
        st.subheader("Lista de Usuarios Registrados")
        st.dataframe(users_df)
        
        # Opción para eliminar usuarios
        st.subheader("Gestión de Usuarios")
        usuario_a_eliminar = st.selectbox(
            "Seleccionar usuario para eliminar:",
            [user['Usuario'] for user in users_data if user['Usuario'] != 'sebomaro2103']  # Excluir al admin
        )
        
        if st.button("Eliminar Usuario"):
            if usuario_a_eliminar != 'sebomaro2103':  # Proteger la cuenta de admin
                del config['credentials']['usernames'][usuario_a_eliminar]
                save_config(config)
                st.success(f"Usuario {usuario_a_eliminar} eliminado correctamente")
                st.experimental_rerun()
            else:
                st.error("No se puede eliminar la cuenta de administrador")
                
    else:
        st.warning("No hay usuarios registrados en el sistema")

def main():
    # Verificar si el usuario está autenticado y es administrador
    if 'authentication_status' not in st.session_state:
        st.error("Por favor, inicia sesión desde la página principal")
        return
        
    if not st.session_state.authentication_status:
        st.error("Por favor, inicia sesión desde la página principal")
        return
        
    if st.session_state.username != 'sebomaro2103':  # Cambiar 'jsmith' por tu usuario administrador
        st.error("No tienes permisos para acceder a esta página")
        return
        
    admin_dashboard()

if __name__ == "__main__":
    main()