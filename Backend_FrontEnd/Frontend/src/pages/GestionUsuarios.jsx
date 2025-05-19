// src/pages/GestionUsuarios.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate }
from "react-router-dom";
import Spinner from '../components/Spinner';
import Breadcrumbs from '../components/Breadcrumbs';
import { toast } from 'react-toastify';
import '../styles/GestionUsuarios.css'; // Estilos principales de la página


const API_URL = 'http://127.0.0.1:8000';
const APP_NAME = "Sistema de Accidentes Bquilla";

function GestionUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
  const [newUserData, setNewUserData] = useState({
    username: "",
    email: "",
    primer_nombre: "",
    primer_apellido: "",
    password: "",
  });

  const [isEditUserModalOpen, setIsEditUserModalOpen] = useState(false);
  const [currentUserData, setCurrentUserData] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    document.title = `Gestión de Usuarios - ${APP_NAME}`;
    fetchUsuarios();
  }, []);

  const fetchUsuarios = async () => {
    setIsLoading(true);
    const token = localStorage.getItem('token');
    if (!token) {
      toast.error("No autenticado. Por favor, inicie sesión.");
      navigate('/');
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${API_URL}/usuarios/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (Array.isArray(response.data)) {
        setUsuarios(response.data);
      } else {
        console.error("La respuesta de /usuarios/ no es un array:", response.data);
        toast.error("Error: Formato de datos de usuarios inesperado.");
        setUsuarios([]);
      }
    } catch (err) {
      console.error("Error al obtener los usuarios:", err.response || err.message);
      let errorMsg = "Error al cargar la lista de usuarios.";
      if (err.response && err.response.status === 401) {
        errorMsg = "No autorizado para ver usuarios. Por favor, inicie sesión de nuevo.";
        navigate('/');
      } else if (err.response && err.response.data && err.response.data.detail) {
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

  const handleCloseAddUserModal = () => {
    setIsAddUserModalOpen(false);
  };

  const handleNewUserChange = (e) => {
    const { name, value } = e.target;
    setNewUserData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) {
      toast.error("No autenticado.");
      navigate('/');
      return;
    }
    setIsSubmitting(true);

    if (!newUserData.username || !newUserData.email || !newUserData.primer_nombre || !newUserData.primer_apellido || !newUserData.password) {
        toast.error("Todos los campos son obligatorios para agregar un usuario.");
        setIsSubmitting(false);
        return;
    }

    try {
      await axios.post(`${API_URL}/usuarios/`, newUserData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      toast.success("Usuario agregado exitosamente.");
      fetchUsuarios();
      handleCloseAddUserModal();
    } catch (err) {
      let errorMsg = "Error al agregar usuario.";
      if (err.response && err.response.data && err.response.data.detail) {
        if (typeof err.response.data.detail === 'string') {
            errorMsg = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
            errorMsg = err.response.data.detail.map(el => `${el.loc.join(' -> ')}: ${el.msg}`).join('; ');
        } else {
            errorMsg = JSON.stringify(err.response.data.detail);
        }
      }
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenEditUserModal = (usuario) => {
    setCurrentUserData({
      id: usuario.id,
      username: usuario.username,
      email: usuario.email,
      primer_nombre: usuario.primer_nombre || "",
      primer_apellido: usuario.primer_apellido || "",
    });
    setIsEditUserModalOpen(true);
  };

  const handleCloseEditUserModal = () => {
    setIsEditUserModalOpen(false);
    setCurrentUserData(null);
  };

  const handleCurrentUserChange = (e) => {
    const { name, value } = e.target;
    setCurrentUserData(prev => ({ ...prev, [name]: value }));
  };

  const handleEditUser = async (e) => {
    e.preventDefault();
    if (!currentUserData || !currentUserData.id) return;
    const token = localStorage.getItem('token');
    if (!token) {
      toast.error("No autenticado.");
      navigate('/');
      return;
    }
    setIsSubmitting(true);

    const { id, ...updateData } = currentUserData;
    if (updateData.password === "") {
        delete updateData.password;
    }

    try {
      await axios.put(`${API_URL}/usuarios/${id}`, updateData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      toast.success("Usuario actualizado exitosamente.");
      fetchUsuarios();
      handleCloseEditUserModal();
    } catch (err) {
      let errorMsg = "Error al actualizar usuario.";
       if (err.response && err.response.data && err.response.data.detail) {
        if (typeof err.response.data.detail === 'string') {
            errorMsg = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
            errorMsg = err.response.data.detail.map(el => `${el.loc.join(' -> ')}: ${el.msg}`).join('; ');
        } else {
            errorMsg = JSON.stringify(err.response.data.detail);
        }
      }
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteUser = async (usuarioId) => {
    if (!window.confirm(`¿Estás seguro de que quieres eliminar al usuario con ID ${usuarioId}? Esta acción no se puede deshacer.`)) {
      return;
    }
    const token = localStorage.getItem('token');
    if (!token) {
      toast.error("No autenticado.");
      navigate('/');
      return;
    }
    
    try {
      await axios.delete(`${API_URL}/usuarios/${usuarioId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success("Usuario eliminado exitosamente.");
      fetchUsuarios();
    } catch (err) {
      let errorMsg = "Error al eliminar usuario.";
      if (err.response && err.response.data && err.response.data.detail) {
         errorMsg = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail);
      }
      toast.error(errorMsg);
    }
  };

  return (
    <div className="gestion-page-container">
      <div className="gestion-container-card">
        <Breadcrumbs crumbs={breadcrumbCrumbs} />
        <div className="gestion-header">
          <h1 className="gestion-title">Gestión de Usuarios</h1>
          <div className="gestion-actions">
            <button
              onClick={() => navigate('/inicio')}
              className="btn btn-secondary btn-fixed-width"
            >
              &larr; Volver a Inicio
            </button>
            <button
              onClick={handleOpenAddUserModal}
              className="btn btn-primary btn-fixed-width"
            >
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
                      <button
                        onClick={() => handleOpenEditUserModal(usuario)}
                        className="btn btn-action btn-edit"
                        disabled={isSubmitting}
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDeleteUser(usuario.id)}
                        className="btn btn-action btn-delete"
                        disabled={isSubmitting}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {isAddUserModalOpen && (
          <div className="user-form-modal"> {/* Cambiado de user-form-popup a user-form-modal */}
            <div className="user-form-modal-content"> {/* Cambiado de user-form-popup-content a user-form-modal-content */}
              <h3>Agregar Nuevo Usuario</h3>
              <form onSubmit={handleAddUser}>
                <div className="form-group">
                  <label htmlFor="add-username">Nombre de Usuario:</label>
                  <input type="text" id="add-username" name="username" value={newUserData.username} onChange={handleNewUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-group">
                  <label htmlFor="add-email">Email:</label>
                  <input type="email" id="add-email" name="email" value={newUserData.email} onChange={handleNewUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-group">
                  <label htmlFor="add-primer_nombre">Primer Nombre:</label>
                  <input type="text" id="add-primer_nombre" name="primer_nombre" value={newUserData.primer_nombre} onChange={handleNewUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-group">
                  <label htmlFor="add-primer_apellido">Primer Apellido:</label>
                  <input type="text" id="add-primer_apellido" name="primer_apellido" value={newUserData.primer_apellido} onChange={handleNewUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-group">
                  <label htmlFor="add-password">Contraseña:</label>
                  <input type="password" id="add-password" name="password" value={newUserData.password} onChange={handleNewUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                    {isSubmitting ? <Spinner size="sm" showText={false}/> : "Guardar"}
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={handleCloseAddUserModal} disabled={isSubmitting}>
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {isEditUserModalOpen && currentUserData && (
          <div className="user-form-modal"> {/* Cambiado de user-form-popup a user-form-modal */}
             <div className="user-form-modal-content"> {/* Cambiado de user-form-popup-content a user-form-modal-content */}
              <h3>Editar Usuario: {currentUserData.username}</h3>
              <form onSubmit={handleEditUser}>
                <div className="form-group">
                  <label htmlFor="edit-username">Nombre de Usuario:</label>
                  <input type="text" id="edit-username" name="username" value={currentUserData.username} onChange={handleCurrentUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-group">
                  <label htmlFor="edit-email">Email:</label>
                  <input type="email" id="edit-email" name="email" value={currentUserData.email} onChange={handleCurrentUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-group">
                  <label htmlFor="edit-primer_nombre">Primer Nombre:</label>
                  <input type="text" id="edit-primer_nombre" name="primer_nombre" value={currentUserData.primer_nombre} onChange={handleCurrentUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-group">
                  <label htmlFor="edit-primer_apellido">Primer Apellido:</label>
                  <input type="text" id="edit-primer_apellido" name="primer_apellido" value={currentUserData.primer_apellido} onChange={handleCurrentUserChange} required disabled={isSubmitting} />
                </div>
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                    {isSubmitting ? <Spinner size="sm" showText={false}/> : "Actualizar"}
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={handleCloseEditUserModal} disabled={isSubmitting}>
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default GestionUsuarios;
