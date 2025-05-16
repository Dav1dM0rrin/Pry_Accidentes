// src/pages/GestionUsuarios.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import Spinner from '../components/Spinner'; // Asumiendo que tienes el componente Spinner
import Breadcrumbs from '../components/Breadcrumbs'; // Asumiendo que tienes Breadcrumbs
import { toast } from 'react-toastify';
import '../styles/GestionUsuarios.css'; // Usaremos este archivo para los estilos

const API_URL = 'http://127.0.0.1:8000';
const APP_NAME = "Sistema de Accidentes Bquilla";

function GestionUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  // const [error, setError] = useState(''); // Usaremos toasts para errores
  
  // Para el formulario (lo mantendremos para el futuro, pero no se usa para listar)
  // const [primerNombre, setPrimerNombre] = useState("");
  // const [primerApellido, setPrimerApellido] = useState("");
  // const [email, setEmail] = useState("");
  // const [isFormVisible, setFormVisible] = useState(false);
  // const [userIdToEdit, setUserIdToEdit] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    document.title = `Gestión de Usuarios - ${APP_NAME}`;
    fetchUsuarios();
  }, []);

  const fetchUsuarios = async () => {
    setIsLoading(true);
    // setError(''); // Ya no se usa
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
      setUsuarios([]); // Limpiar usuarios en caso de error
    } finally {
      setIsLoading(false);
    }
  };

  const breadcrumbCrumbs = [
    { label: 'Inicio', path: '/inicio' },
    { label: 'Gestión de Usuarios' }
  ];

  // Las funciones para mostrar formulario, manejarlo y eliminar se comentan por ahora
  // Se implementarán o ajustarán cuando trabajemos en Crear/Editar/Eliminar usuarios.
  /*
  const mostrarFormulario = (id = null) => { ... };
  const ocultarFormulario = () => { ... };
  const manejarFormulario = (e) => { ... };
  const eliminarUsuario = (id) => { ... };
  */

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
            {/* El botón para agregar se mantiene, la funcionalidad se añadirá después */}
            <button 
              onClick={() => toast.info("Funcionalidad 'Agregar Usuario' pendiente.")} 
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
                        onClick={() => toast.info(`Editar usuario ${usuario.id} - Pendiente`)} 
                        className="btn btn-action btn-edit"
                      >
                        Editar
                      </button>
                      <button 
                        onClick={() => toast.info(`Eliminar usuario ${usuario.id} - Pendiente`)} 
                        className="btn btn-action btn-delete"
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

        {/* El formulario se comentará o eliminará si no se usa inmediatamente
        {isFormVisible && (
            <div className="user-form-popup"> // O un modal
                <h3>{userIdToEdit ? "Editar Usuario" : "Nuevo Usuario"}</h3>
                <form onSubmit={manejarFormulario}>
                    // ... inputs ...
                </form>
            </div>
        )}
        */}
      </div>
    </div>
  );
}

export default GestionUsuarios;
