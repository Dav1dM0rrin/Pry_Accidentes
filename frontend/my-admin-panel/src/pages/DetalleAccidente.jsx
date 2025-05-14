// src/pages/DetalleAccidente.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import '../styles/detalleacc.css'; // Crearemos este archivo CSS

const API_URL = 'http://127.0.0.1:8000';

function DetalleAccidente() {
  const { accidenteId } = useParams(); // Obtiene el ID del accidente de la URL
  const navigate = useNavigate();
  const [accidente, setAccidente] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAccidenteDetalle = async () => {
      setIsLoading(true);
      setError('');
      const token = localStorage.getItem('token'); // Asumimos que se necesita token si el endpoint está protegido

      if (!accidenteId) {
        setError('ID de accidente no proporcionado.');
        setIsLoading(false);
        return;
      }

      try {
        const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
        const response = await axios.get(`${API_URL}/accidentes/${accidenteId}`, config);
        console.log("Detalle del accidente recibido:", response.data);
        setAccidente(response.data);
      } catch (err) {
        console.error("Error fetching accidente detalle:", err.response || err.message);
        if (err.response && err.response.status === 404) {
          setError('Accidente no encontrado.');
        } else if (err.response && err.response.status === 401) {
          setError('No autorizado. Por favor, inicie sesión.');
        } else {
          setError('Error al cargar los detalles del accidente.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchAccidenteDetalle();
  }, [accidenteId]);

  // Función auxiliar para mostrar datos o un placeholder
  const renderData = (label, value, isLink = false, linkTo = "#") => {
    if (value === null || typeof value === 'undefined' || value === '') {
      return (
        <div className="detalle-item">
          <span className="detalle-label">{label}:</span>
          <span className="detalle-value muted">No disponible</span>
        </div>
      );
    }
    return (
      <div className="detalle-item">
        <span className="detalle-label">{label}:</span>
        {isLink ? (
          <Link to={linkTo} className="detalle-value link">{String(value)}</Link>
        ) : (
          <span className="detalle-value">{String(value)}</span>
        )}
      </div>
    );
  };
  
  const formatDate = (dateString) => {
    if (!dateString) return "No disponible";
    try {
      const date = new Date(dateString);
      return date.toLocaleString('es-CO', { 
        year: 'numeric', month: 'long', day: 'numeric', 
        hour: '2-digit', minute: '2-digit', hour12: true 
      });
    // eslint-disable-next-line no-unused-vars
    } catch (err) {
      return dateString; // Devolver el string original si hay error
    }
  };


  if (isLoading) {
    return <div className="loading-container"><div className="loading-spinner"></div><p>Cargando detalles del accidente...</p></div>;
  }

  if (error) {
    return (
      <div className="detalle-page-container error-page">
        <p className="error-message">{error}</p>
        <button onClick={() => navigate('/inicio')} className="btn btn-primary">Volver a Inicio</button>
      </div>
    );
  }

  if (!accidente) {
    // Esto no debería ocurrir si isLoading es false y no hay error, pero es una salvaguarda
    return <div className="detalle-page-container"><p>No se encontraron datos del accidente.</p></div>;
  }

  // Desestructuración segura de datos anidados
  const {
    fecha,
    sexo_victima,
    edad_victima,
    cantidad_victima,
    usuario,
    tipo_accidente,
    condicion_victima,
    gravedad,
    ubicacion
  } = accidente;

  const direccionCompleta = ubicacion ? 
    `${ubicacion.primer_via?.nombre_via || ''} ${ubicacion.primer_via?.sufijo_via || ''} ${ubicacion.segunda_via ? `con ${ubicacion.segunda_via.nombre_via || ''} ${ubicacion.segunda_via.sufijo_via || ''}` : ''}`.trim()
    : "No disponible";

  return (
    <div className="detalle-page-container">
      <div className="detalle-card">
        <div className="detalle-header">
          <h1 className="detalle-title">Detalles del Accidente ID: {accidente.id}</h1>
          <button onClick={() => navigate(-1)} className="btn btn-secondary btn-back-detalle">
            &larr; Volver
          </button>
        </div>

        <div className="detalle-section">
          <h2 className="detalle-section-title">Información General del Accidente</h2>
          {renderData("Fecha y Hora", formatDate(fecha))}
          {renderData("Tipo de Accidente", tipo_accidente?.nombre)}
          {renderData("Gravedad", gravedad?.nivel_gravedad)}
        </div>

        <div className="detalle-section">
          <h2 className="detalle-section-title">Ubicación</h2>
          {renderData("Dirección Aproximada", direccionCompleta || ubicacion?.complemento)}
          {renderData("Complemento", ubicacion?.complemento)}
          {renderData("Barrio", ubicacion?.barrio?.nombre)}
          {renderData("Zona del Barrio", ubicacion?.barrio?.zona?.nombre)}
          {renderData("Latitud", ubicacion?.latitud)}
          {renderData("Longitud", ubicacion?.longitud)}
          {renderData("Vía Principal", `${ubicacion?.primer_via?.tipo_via?.nombre || ''} ${ubicacion?.primer_via?.nombre_via || ''} ${ubicacion?.primer_via?.numero_via || ''} ${ubicacion?.primer_via?.sufijo_via || ''}`.trim())}
          {renderData("Vía Secundaria", ubicacion?.segunda_via ? `${ubicacion?.segunda_via?.tipo_via?.nombre || ''} ${ubicacion?.segunda_via?.nombre_via || ''} ${ubicacion?.segunda_via?.numero_via || ''} ${ubicacion?.segunda_via?.sufijo_via || ''}`.trim() : "N/A")}
        </div>

        <div className="detalle-section">
          <h2 className="detalle-section-title">Información de la Víctima(s)</h2>
          {renderData("Condición de la Víctima", condicion_victima?.rol_victima)}
          {renderData("Sexo de la Víctima", sexo_victima === 'M' ? 'Masculino' : (sexo_victima === 'F' ? 'Femenino' : (sexo_victima === 'O' ? 'Otro' : sexo_victima)))}
          {renderData("Edad de la Víctima", edad_victima)}
          {renderData("Cantidad de Víctimas", cantidad_victima)}
        </div>
        
        {usuario && (
          <div className="detalle-section">
            <h2 className="detalle-section-title">Reportado por</h2>
            {renderData("Usuario", usuario.username)}
            {renderData("Nombre", `${usuario.primer_nombre} ${usuario.primer_apellido}`)}
            {renderData("Email", usuario.email)}
          </div>
        )}
      </div>
    </div>
  );
}

export default DetalleAccidente;
