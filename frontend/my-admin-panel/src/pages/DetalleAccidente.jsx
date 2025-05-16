// src/pages/DetalleAccidente.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import Breadcrumbs from '../components/Breadcrumbs';
import { toast } from 'react-toastify'; 
import Spinner from '../components/Spinner'; // Importar Spinner
import '../styles/DetalleAccidente.css'; 

const API_URL = 'http://127.0.0.1:8000';
const APP_NAME = "Sistema de Accidentes Bquilla";

function DetalleAccidente() {
  const { accidenteId } = useParams(); 
  const navigate = useNavigate();
  const [accidente, setAccidente] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Efecto para el título de la página
  useEffect(() => {
    if (isLoading) {
      document.title = `Cargando... - ${APP_NAME}`;
    } else if (accidente) {
      document.title = `Detalle Acc. #${accidente.id} - ${APP_NAME}`;
    } else {
      document.title = `Detalle no Encontrado - ${APP_NAME}`;
    }
  }, [isLoading, accidente, accidenteId]);

  // Definición de breadcrumbs
  const breadcrumbCrumbs = [
    { label: 'Inicio', path: '/inicio' },
    { label: accidenteId ? `Detalles del Accidente #${accidenteId}` : 'Detalles del Accidente' } 
  ];

  // Efecto para obtener detalles del accidente
  useEffect(() => {
    const fetchAccidenteDetalle = async () => {
      setIsLoading(true);
      const token = localStorage.getItem('token'); 
      if (!accidenteId) { 
        toast.error('ID de accidente no proporcionado.'); 
        setIsLoading(false); 
        return; 
      }
      try {
        const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
        const response = await axios.get(`${API_URL}/accidentes/${accidenteId}`, config);
        setAccidente(response.data);
      } catch (err) {
        let errorMsg = 'Error al cargar los detalles del accidente.';
        if (err.response && err.response.status === 404) errorMsg = 'Accidente no encontrado.';
        else if (err.response && err.response.status === 401) errorMsg = 'No autorizado.';
        toast.error(errorMsg); 
        setAccidente(null); // Asegurar que no se muestren datos viejos si hay error
      } finally {
        setIsLoading(false);
      }
    };
    fetchAccidenteDetalle();
  }, [accidenteId]);

  // Función para renderizar datos
  const renderData = (label, value, isLink = false, linkTo = "#") => { 
    if (value === null || typeof value === 'undefined' || value === '') return ( <div className="detalle-item"> <span className="detalle-label">{label}:</span> <span className="detalle-value muted">No disponible</span> </div> );
    return ( <div className="detalle-item"> <span className="detalle-label">{label}:</span> {isLink ? (<Link to={linkTo} className="detalle-value link">{String(value)}</Link>) : (<span className="detalle-value">{String(value)}</span>)} </div> );
  };
  // Función para formatear fecha
  const formatDate = (dateString) => { 
    if (!dateString) return "No disponible";
    // eslint-disable-next-line no-unused-vars
    try { const date = new Date(dateString); return date.toLocaleString('es-CO', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true }); } catch (e) { return dateString; }
  };

  // Renderizado condicional durante la carga
  if (isLoading) {
    return (
      <div className="detalle-page-container">
        <div className="detalle-card-loading"> 
          <Breadcrumbs crumbs={breadcrumbCrumbs} /> 
          {/* Usar Spinner */}
          <Spinner text="Cargando detalles del accidente..." size="lg" /> 
        </div>
      </div>
    );
  }
  
  // Renderizado si no hay accidente (después de cargar y no encontrarlo o por error)
  if (!accidente) { 
    return ( 
      <div className="detalle-page-container error-page"> 
        <Breadcrumbs crumbs={breadcrumbCrumbs} /> 
        <p className="error-message">No se pudieron cargar los detalles o el accidente no existe.</p> 
        <button onClick={() => navigate('/inicio')} className="btn btn-primary">Volver a Inicio</button> 
      </div> 
    );
  }
  
  // Preparar breadcrumbs finales con el ID del accidente cargado
  const finalBreadcrumbCrumbs = [ { label: 'Inicio', path: '/inicio' }, { label: `Detalles del Accidente #${accidente.id || accidenteId}` } ];
  // Desestructuración de datos del accidente
  const { fecha, sexo_victima, edad_victima, cantidad_victima, usuario, tipo_accidente, condicion_victima, gravedad, ubicacion } = accidente;
  const direccionCompleta = ubicacion ? `${ubicacion.primer_via?.nombre_via || ''} ${ubicacion.primer_via?.sufijo_via || ''} ${ubicacion.segunda_via ? `con ${ubicacion.segunda_via.nombre_via || ''} ${ubicacion.segunda_via.sufijo_via || ''}` : ''}`.trim() : "No disponible";

  return (
    <div className="detalle-page-container">
      <div className="detalle-card">
        <Breadcrumbs crumbs={finalBreadcrumbCrumbs} /> 
        {/* Encabezado de detalles */}
        <div className="detalle-header"> 
          <h1 className="detalle-title">Detalles Accidente ID: {accidente.id}</h1> 
          <button onClick={() => navigate(-1)} className="btn btn-secondary btn-back-detalle"> &larr; Volver </button> 
        </div>
        {/* Secciones de detalles */}
        <div className="detalle-section"> <h2 className="detalle-section-title">Información General</h2> {renderData("Fecha y Hora", formatDate(fecha))} {renderData("Tipo", tipo_accidente?.nombre)} {renderData("Gravedad", gravedad?.nivel_gravedad)} </div>
        <div className="detalle-section"> <h2 className="detalle-section-title">Ubicación</h2> {renderData("Dirección", direccionCompleta || ubicacion?.complemento)} {renderData("Complemento", ubicacion?.complemento)} {renderData("Barrio", ubicacion?.barrio?.nombre)} {renderData("Zona", ubicacion?.barrio?.zona?.nombre)} {renderData("Latitud", ubicacion?.latitud)} {renderData("Longitud", ubicacion?.longitud)} {renderData("Vía Principal", `${ubicacion?.primer_via?.tipo_via?.nombre || ''} ${ubicacion?.primer_via?.nombre_via || ''}`)} {renderData("Vía Secundaria", ubicacion?.segunda_via ? `${ubicacion?.segunda_via?.tipo_via?.nombre || ''} ${ubicacion?.segunda_via?.nombre_via || ''}` : "N/A")} </div>
        <div className="detalle-section"> <h2 className="detalle-section-title">Víctima(s)</h2> {renderData("Condición", condicion_victima?.rol_victima)} {renderData("Sexo", sexo_victima === 'M' ? 'Masculino' : (sexo_victima === 'F' ? 'Femenino' : sexo_victima))} {renderData("Edad", edad_victima)} {renderData("Cantidad", cantidad_victima)} </div>
        {usuario && ( <div className="detalle-section"> <h2 className="detalle-section-title">Reportado por</h2> {renderData("Usuario", usuario.username)} {renderData("Nombre", `${usuario.primer_nombre} ${usuario.primer_apellido}`)} {renderData("Email", usuario.email)} </div> )}
      </div>
    </div>
  );
}

export default DetalleAccidente;
