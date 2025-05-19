// src/pages/DetalleAccidente.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, NavLink} from 'react-router-dom'; // NavLink y useLocation añadidos
import axios from 'axios';
import Breadcrumbs from '../components/Breadcrumbs';
import { toast } from 'react-toastify'; 
import Spinner from '../components/Spinner';

// Importar CSS para la barra de navegación y para el contenido específico
import '../styles/inicio.css'; // Para la barra de navegación
import '../styles/DetalleAccidente.css'; // Para el contenido específico

const API_URL = 'http://127.0.0.1:8000';
const APP_NAME = "Sistema de Accidentes Bquilla";

function DetalleAccidente() {
  const { accidenteId } = useParams(); 
  const navigate = useNavigate();
  const [accidente, setAccidente] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    toast.success("Sesión cerrada exitosamente.");
    navigate('/'); 
  };

  // Función para clases de NavLink activo
  const getNavLinkClass = ({ isActive }) => isActive ? "nav-link active" : "nav-link";

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
        toast.info("Por favor, inicie sesión para acceder a esta página.");
        navigate('/'); 
        return; // Detener ejecución si no hay token
    }

    if (isLoading) {
      document.title = `Cargando... - ${APP_NAME}`;
    } else if (accidente) {
      document.title = `Detalle Acc. #${accidente.id} - ${APP_NAME}`;
    } else {
      document.title = `Detalle no Encontrado - ${APP_NAME}`;
    }
  }, [isLoading, accidente, navigate]); // navigate añadido a dependencias

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return; // Ya manejado arriba, pero buena práctica

    const fetchAccidenteDetalle = async () => {
      setIsLoading(true);
      if (!accidenteId) { 
        toast.error('ID de accidente no proporcionado.'); 
        setIsLoading(false); 
        return; 
      }
      try {
        const config = { headers: { Authorization: `Bearer ${token}` } };
        const response = await axios.get(`${API_URL}/accidentes/${accidenteId}`, config);
        setAccidente(response.data);
      } catch (err) {
        let errorMsg = 'Error al cargar los detalles del accidente.';
        if (err.response && err.response.status === 404) errorMsg = 'Accidente no encontrado.';
        else if (err.response && err.response.status === 401) {
          errorMsg = 'No autorizado. Redirigiendo al login.';
          handleLogout(); // Forzar logout si es error 401
        }
        toast.error(errorMsg); 
        setAccidente(null);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAccidenteDetalle();
  }, [accidenteId, navigate]); // navigate añadido

  const breadcrumbCrumbs = [
    { label: 'Inicio', path: '/inicio' },
    { label: accidenteId ? `Detalles del Accidente #${accidente?.id || accidenteId}` : 'Detalles del Accidente' } 
  ];

  const renderData = (label, value, isLink = false, linkTo = "#") => { 
    if (value === null || typeof value === 'undefined' || value === '') return ( <div className="detalle-item"> <span className="detalle-label">{label}:</span> <span className="detalle-value muted">No disponible</span> </div> );
    return ( <div className="detalle-item"> <span className="detalle-label">{label}:</span> {isLink ? (<Link to={linkTo} className="detalle-value link">{String(value)}</Link>) : (<span className="detalle-value">{String(value)}</span>)} </div> );
  };
  
  const formatDate = (dateString) => { 
    if (!dateString) return "No disponible";
    // eslint-disable-next-line no-unused-vars
    try { const date = new Date(dateString); return date.toLocaleString('es-CO', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true }); } catch (e) { return dateString; }
  };

  // Contenido de la página de carga
  const loadingPageContent = (
    <div className="detalle-card-loading" style={{padding: '2rem', textAlign: 'center'}}> 
      <Breadcrumbs crumbs={breadcrumbCrumbs} /> 
      <Spinner text="Cargando detalles del accidente..." size="lg" /> 
    </div>
  );

  // Contenido si no hay accidente
  const noAccidentContent = (
    <div className="detalle-card error-page" style={{padding: '2rem', textAlign: 'center'}}> {/* Usar clase de CSS específico */}
      <Breadcrumbs crumbs={breadcrumbCrumbs} /> 
      <p className="error-message" style={{color: 'var(--danger-color)', fontSize: '1.1rem', margin: '2rem 0'}}>No se pudieron cargar los detalles o el accidente no existe.</p> 
      <button onClick={() => navigate('/inicio')} className="btn btn-primary">Volver a Inicio</button> 
    </div> 
  );
  
  // Contenido principal cuando el accidente está cargado
  const accidentDetailsContent = accidente && (
    <div className="detalle-card"> {/* Clase de DetalleAccidente.css */}
      <Breadcrumbs crumbs={[ { label: 'Inicio', path: '/inicio' }, { label: `Detalles del Accidente #${accidente.id || accidenteId}` } ]} /> 
      <div className="detalle-header"> 
        <h1 className="detalle-title">Detalles Accidente ID: {accidente.id}</h1> 
        <button onClick={() => navigate(-1)} className="btn btn-secondary btn-back-detalle"> &larr; Volver </button> 
      </div>
      <div className="detalle-section"> <h2 className="detalle-section-title">Información General</h2> {renderData("Fecha y Hora", formatDate(accidente.fecha))} {renderData("Tipo", accidente.tipo_accidente?.nombre)} {renderData("Gravedad", accidente.gravedad?.nivel_gravedad)} </div>
      <div className="detalle-section"> <h2 className="detalle-section-title">Ubicación</h2> {renderData("Dirección", `${accidente.ubicacion?.primer_via?.nombre_via || ''} ${accidente.ubicacion?.primer_via?.sufijo_via || ''} ${accidente.ubicacion?.segunda_via ? `con ${accidente.ubicacion?.segunda_via.nombre_via || ''} ${accidente.ubicacion?.segunda_via.sufijo_via || ''}` : ''}`.trim() || accidente.ubicacion?.complemento || "No disponible")} {renderData("Complemento", accidente.ubicacion?.complemento)} {renderData("Barrio", accidente.ubicacion?.barrio?.nombre)} {renderData("Zona", accidente.ubicacion?.barrio?.zona?.nombre)} {renderData("Latitud", accidente.ubicacion?.latitud)} {renderData("Longitud", accidente.ubicacion?.longitud)} </div>
      <div className="detalle-section"> <h2 className="detalle-section-title">Víctima(s)</h2> {renderData("Condición", accidente.condicion_victima?.rol_victima)} {renderData("Sexo", accidente.sexo_victima === 'M' ? 'Masculino' : (accidente.sexo_victima === 'F' ? 'Femenino' : accidente.sexo_victima))} {renderData("Edad", accidente.edad_victima)} {renderData("Cantidad", accidente.cantidad_victima)} </div>
      {accidente.usuario && ( <div className="detalle-section"> <h2 className="detalle-section-title">Reportado por</h2> {renderData("Usuario", accidente.usuario.username)} {renderData("Nombre", `${accidente.usuario.primer_nombre} ${accidente.usuario.primer_apellido}`)} {renderData("Email", accidente.usuario.email)} </div> )}
    </div>
  );

  return (
    <div className="inicio-page-container"> {/* Clase de inicio.css */}
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
        {isLoading ? loadingPageContent : (!accidente ? noAccidentContent : accidentDetailsContent)}
      </main>
    </div>
  );
}

export default DetalleAccidente;
