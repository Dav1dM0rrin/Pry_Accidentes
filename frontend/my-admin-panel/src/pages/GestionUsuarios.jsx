// src/pages/GestionUsuarios.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, NavLink} from "react-router-dom"; // NavLink y useLocation añadidos
import Spinner from '../components/Spinner';
import Breadcrumbs from '../components/Breadcrumbs';
import { toast } from 'react-toastify';

// Importar CSS para la barra de navegación y para el contenido específico
import '../styles/inicio.css'; // Para la barra de navegación
import '../styles/GestionUsuarios.css'; // Estilos principales de la página

const API_URL = 'http://127.0.0.1:8000';
const APP_NAME = "Sistema de Accidentes Bquilla";

function GestionUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
  const [newUserData, setNewUserData] = useState({
    username: "", email: "", primer_nombre: "", primer_apellido: "", password: "",
  });

  const [isEditUserModalOpen, setIsEditUserModalOpen] = useState(false);
  const [currentUserData, setCurrentUserData] = useState(null);

  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    toast.success("Sesión cerrada exitosamente.");
    navigate('/'); 
  };

  // Función para clases de NavLink activo
  const getNavLinkClass = ({ isActive }) => isActive ? "nav-link active" : "nav-link";
  
  useEffect(() => {
    document.title = `Gestión de Usuarios - ${APP_NAME}`;
    const token = localStorage.getItem('token');
    if (!token) {
      toast.info("Por favor, inicie sesión para acceder a esta página.");
      navigate('/');
    } else {
      fetchUsuarios();
    }
  }, [navigate]); // Solo navigate como dependencia para el chequeo inicial del token

  const fetchUsuarios = async () => {
    setIsLoading(true);
    const token = localStorage.getItem('token');
    // No es necesario verificar el token aquí de nuevo si ya se hizo en useEffect
    try {
      const response = await axios.get(`${API_URL}/usuarios/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (Array.isArray(response.data)) {
        setUsuarios(response.data);
      } else {
        toast.error("Error: Formato de datos de usuarios inesperado.");
        setUsuarios([]);
      }
    } catch (err) {
      let errorMsg = "Error al cargar la lista de usuarios.";
      if (err.response && err.response.status === 401) {
        errorMsg = "No autorizado. Redirigiendo al login.";
        handleLogout(); // Forzar logout si es error 401
      } else if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail);
      }
      toast.error(errorMsg);
      setUsuarios([]);
    } finally {
      setIsLoading(false);
    }
  };

  const breadcrumbCrumbs = [
    { label: 'Inicio', path: '/inicio' },
    { label: 'Gestión de Usuarios' }
  ];

  const handleOpenAddUserModal = () => {
    setNewUserData({ username: "", email: "", primer_nombre: "", primer_apellido: "", password: "" });
    setIsAddUserModalOpen(true);
  };

  const handleCloseAddUserModal = () => setIsAddUserModalOpen(false);

  const handleNewUserChange = (e) => {
    const { name, value } = e.target;
    setNewUserData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) { toast.error("No autenticado."); navigate('/'); return; }
    setIsSubmitting(true);
    if (!newUserData.username || !newUserData.email || !newUserData.primer_nombre || !newUserData.primer_apellido || !newUserData.password) {
        toast.error("Todos los campos son obligatorios para agregar un usuario.");
        setIsSubmitting(false);
        return;
    }
    try {
      await axios.post(`${API_URL}/usuarios/`, newUserData, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      toast.success("Usuario agregado exitosamente.");
      fetchUsuarios();
      handleCloseAddUserModal();
    } catch (err) {
      let errorMsg = "Error al agregar usuario.";
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') errorMsg = err.response.data.detail;
        else if (Array.isArray(err.response.data.detail)) errorMsg = err.response.data.detail.map(el => `${el.loc.join(' -> ')}: ${el.msg}`).join('; ');
        else errorMsg = JSON.stringify(err.response.data.detail);
      }
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenEditUserModal = (usuario) => {
    setCurrentUserData({
      id: usuario.id, username: usuario.username, email: usuario.email,
      primer_nombre: usuario.primer_nombre || "", primer_apellido: usuario.primer_apellido || "",
      password: "" // Dejar contraseña vacía para edición, solo se envía si se cambia
    });
    setIsEditUserModalOpen(true);
  };

  const handleCloseEditUserModal = () => { setIsEditUserModalOpen(false); setCurrentUserData(null); };

  const handleCurrentUserChange = (e) => {
    const { name, value } = e.target;
    setCurrentUserData(prev => ({ ...prev, [name]: value }));
  };

  const handleEditUser = async (e) => {
    e.preventDefault();
    if (!currentUserData || !currentUserData.id) return;
    const token = localStorage.getItem('token');
    if (!token) { toast.error("No autenticado."); navigate('/'); return; }
    setIsSubmitting(true);

    const { id, ...updateDataPayload } = currentUserData;
    // Solo incluir la contraseña en el payload si se ha ingresado una nueva
    if (!updateDataPayload.password || updateDataPayload.password.trim() === "") {
        delete updateDataPayload.password;
    }

    try {
      await axios.put(`${API_URL}/usuarios/${id}`, updateDataPayload, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      toast.success("Usuario actualizado exitosamente.");
      fetchUsuarios();
      handleCloseEditUserModal();
    } catch (err) {
      let errorMsg = "Error al actualizar usuario.";
       if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') errorMsg = err.response.data.detail;
        else if (Array.isArray(err.response.data.detail)) errorMsg = err.response.data.detail.map(el => `${el.loc.join(' -> ')}: ${el.msg}`).join('; ');
        else errorMsg = JSON.stringify(err.response.data.detail);
      }
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteUser = async (usuarioId) => {
    if (!window.confirm(`¿Estás seguro de que quieres eliminar al usuario con ID ${usuarioId}? Esta acción no se puede deshacer.`)) return;
    const token = localStorage.getItem('token');
    if (!token) { toast.error("No autenticado."); navigate('/'); return; }
    try {
      await axios.delete(`${API_URL}/usuarios/${usuarioId}`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success("Usuario eliminado exitosamente.");
      fetchUsuarios();
    } catch (err) {
      let errorMsg = "Error al eliminar usuario.";
      if (err.response?.data?.detail) errorMsg = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail);
      toast.error(errorMsg);
    }
  };
  
  // Estilo para el contenedor de la página completa
   const pageContainerStyle = {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column'
  };

  return (
    <div className="inicio-page-container" style={pageContainerStyle}> {/* Clase de inicio.css */}
      {/* Barra de navegación principal */}
      <div className="main-top-bar"> 
        <div className="container main-top-bar-content"> 
          <span className="app-title">{APP_NAME}</span>
          <button onClick={handleLogout} className="btn btn-logout">
            Cerrar Sesión
          </button>
        </div>
      </div>
      {/* Barra de navegación secundaria */}
      <nav className="secondary-nav-bar"> 
        <div className="container"> 
          <div className="nav-links-container"> 
            <NavLink to="/inicio" className={getNavLinkClass}>Inicio (Mapa)</NavLink>
            <NavLink to="/tablero-accidentes" className={getNavLinkClass}>Tablero PBI</NavLink>
            <NavLink to="/reportar-accidente" className={getNavLinkClass}>Reportar Accidente</NavLink> 
            <NavLink to="/gestion-usuarios" className={getNavLinkClass}>Gestión Usuarios</NavLink>
            <NavLink to="/lectura-sensor" className={getNavLinkClass}>Lecturas IoT</NavLink>
          </div>
        </div>
      </nav>

      {/* Contenido principal de la página */}
      <main className="main-content container"> {/* Clases de inicio.css */}
        {/* gestion-container-card es la tarjeta blanca que envuelve el contenido específico */}
        <div className="gestion-container-card"> {/* Clase de GestionUsuarios.css */}
          <Breadcrumbs crumbs={breadcrumbCrumbs} />
          <div className="gestion-header">
            <h1 className="gestion-title">Gestión de Usuarios</h1>
            <div className="gestion-actions">
              {/* El botón de volver a inicio no es necesario si ya está en la barra de nav */}
              <button onClick={handleOpenAddUserModal} className="btn btn-primary btn-fixed-width">
                Agregar Usuario
              </button>
            </div>
          </div>

          {isLoading ? (
            <Spinner text="Cargando usuarios..." size="lg" />
          ) : usuarios.length === 0 ? (
            <p className="no-data-message">No hay usuarios registrados para mostrar.</p>
          ) : (
            <div className="table-responsive-container">
              <table className="user-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre de Usuario</th>
                    <th>Nombre Completo</th>
                    <th>Email</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {usuarios.map((usuario) => (
                    <tr key={usuario.id}>
                      <td>{usuario.id}</td>
                      <td>{usuario.username}</td>
                      <td>{`${usuario.primer_nombre || ''} ${usuario.primer_apellido || ''}`.trim()}</td>
                      <td>{usuario.email}</td>
                      <td className="actions-cell">
                        <button onClick={() => handleOpenEditUserModal(usuario)} className="btn btn-action btn-edit" disabled={isSubmitting}>Editar</button>
                        <button onClick={() => handleDeleteUser(usuario.id)} className="btn btn-action btn-delete" disabled={isSubmitting}>Eliminar</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {isAddUserModalOpen && (
            <div className="user-form-modal"> 
              <div className="user-form-modal-content"> 
                <h3>Agregar Nuevo Usuario</h3>
                <form onSubmit={handleAddUser}>
                  <div className="form-group"> <label htmlFor="add-username">Nombre de Usuario:</label> <input type="text" id="add-username" name="username" value={newUserData.username} onChange={handleNewUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-group"> <label htmlFor="add-email">Email:</label> <input type="email" id="add-email" name="email" value={newUserData.email} onChange={handleNewUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-group"> <label htmlFor="add-primer_nombre">Primer Nombre:</label> <input type="text" id="add-primer_nombre" name="primer_nombre" value={newUserData.primer_nombre} onChange={handleNewUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-group"> <label htmlFor="add-primer_apellido">Primer Apellido:</label> <input type="text" id="add-primer_apellido" name="primer_apellido" value={newUserData.primer_apellido} onChange={handleNewUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-group"> <label htmlFor="add-password">Contraseña:</label> <input type="password" id="add-password" name="password" value={newUserData.password} onChange={handleNewUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-actions"> <button type="submit" className="btn btn-primary" disabled={isSubmitting}> {isSubmitting ? <Spinner size="sm" showText={false}/> : "Guardar"} </button> <button type="button" className="btn btn-secondary" onClick={handleCloseAddUserModal} disabled={isSubmitting}> Cancelar </button> </div>
                </form>
              </div>
            </div>
          )}

          {isEditUserModalOpen && currentUserData && (
            <div className="user-form-modal"> 
               <div className="user-form-modal-content"> 
                <h3>Editar Usuario: {currentUserData.username}</h3>
                <form onSubmit={handleEditUser}>
                  <div className="form-group"> <label htmlFor="edit-username">Nombre de Usuario:</label> <input type="text" id="edit-username" name="username" value={currentUserData.username} onChange={handleCurrentUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-group"> <label htmlFor="edit-email">Email:</label> <input type="email" id="edit-email" name="email" value={currentUserData.email} onChange={handleCurrentUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-group"> <label htmlFor="edit-primer_nombre">Primer Nombre:</label> <input type="text" id="edit-primer_nombre" name="primer_nombre" value={currentUserData.primer_nombre} onChange={handleCurrentUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-group"> <label htmlFor="edit-primer_apellido">Primer Apellido:</label> <input type="text" id="edit-primer_apellido" name="primer_apellido" value={currentUserData.primer_apellido} onChange={handleCurrentUserChange} required disabled={isSubmitting} /> </div>
                  <div className="form-group"> <label htmlFor="edit-password">Nueva Contraseña (dejar en blanco para no cambiar):</label> <input type="password" id="edit-password" name="password" value={currentUserData.password || ""} onChange={handleCurrentUserChange} disabled={isSubmitting} /> </div>
                  <div className="form-actions"> <button type="submit" className="btn btn-primary" disabled={isSubmitting}> {isSubmitting ? <Spinner size="sm" showText={false}/> : "Actualizar"} </button> <button type="button" className="btn btn-secondary" onClick={handleCloseEditUserModal} disabled={isSubmitting}> Cancelar </button> </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default GestionUsuarios;
