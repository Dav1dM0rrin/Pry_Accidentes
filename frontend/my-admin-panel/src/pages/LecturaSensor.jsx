// Frontend/src/pages/LecturaSensor.jsx
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import Spinner from '../components/Spinner'; 
// Iconos para el contenido de la página (no para la barra de navegación)
import { Thermometer, Droplets, Zap, AlertTriangle, ListChecks, Clock, RefreshCw } from 'lucide-react';
// Importaciones de React Router DOM
import { useNavigate, NavLink} from 'react-router-dom'; 


import '../styles/inicio.css'; // Para la barra de navegación
import '../styles/LecturaSensor.css'; // Para el contenido específico de esta página

const API_BASE_URL = "http://localhost:8000"; 
const API_ENDPOINT = "/lectura_sensor/";
const APP_NAME = "Sistema de Accidentes Bquilla"; // Coincidir con Inicio.jsx

const LecturaSensor = () => {
  const navigate = useNavigate();

  const [lecturas, setLecturas] = useState([]);
  const [latestLectura, setLatestLectura] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false); 
  const [lastFetched, setLastFetched] = useState(null);

  // Definición de timestampKey (asegúrate que coincida con tu backend)
  // Esta clave se usará para acceder al campo de fecha/hora en tus objetos de lectura.
  // Si tu backend envía 'fecha_hora', usa 'fecha_hora'. Si envía 'timestamp', usa 'timestamp'.
  const timestampKey = 'fecha_hora'; // AJUSTA ESTO SI ES NECESARIO

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user'); // Si también guardas info del usuario
    toast.success("Sesión cerrada exitosamente."); // Usar toast.success para consistencia
    navigate('/'); 
  };

  const formatTimestamp = (timestamp, context = "Lectura") => {
    if (!timestamp) return 'N/A'; 
    const dateObject = new Date(timestamp);
    if (isNaN(dateObject.getTime())) {
      console.warn(`Timestamp inválido recibido para ${context}: `, timestamp);
      return 'Fecha inválida';
    }
    return dateObject.toLocaleString('es-CO', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true,
    });
  };

  const fetchLecturas = useCallback(async (isInitialLoad = false) => {
    if (!isInitialLoad && !autoRefresh) { 
        setLoading(true);
    }
    setError(null);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        // No mostrar toast aquí, redirigir directamente o manejar en useEffect principal
        throw new Error("Token de autenticación no encontrado. Por favor, inicie sesión de nuevo.");
      }
      
      const apiUrl = `${API_BASE_URL}${API_ENDPOINT}`;
      const response = await axios.get(apiUrl, {
        headers: { Authorization: `Bearer ${token}` },
      });

      let sortedLecturas = [];
      if (Array.isArray(response.data)) {
        // Usar la variable timestampKey definida arriba
        sortedLecturas = response.data.sort((a, b) => {
            const dateA = new Date(a[timestampKey]); 
            const dateB = new Date(b[timestampKey]); 
            
            const timeA = !isNaN(dateA.getTime()) ? dateA.getTime() : 0;
            const timeB = !isNaN(dateB.getTime()) ? dateB.getTime() : 0;

            if (timeA === 0 && timeB === 0) return 0;
            if (timeA === 0) return 1; 
            if (timeB === 0) return -1;

            return timeB - timeA; // Más reciente primero
        });
      } else {
        console.warn("La respuesta de " + API_ENDPOINT + " no fue un array:", response.data);
        if (response.data && typeof response.data === 'object' && (response.data.message || response.data.detail)) {
          throw new Error(response.data.message || response.data.detail || "Respuesta inesperada del servidor.");
        }
      }
      
      setLecturas(sortedLecturas);
      setLatestLectura(sortedLecturas.length > 0 ? sortedLecturas[0] : null);
      setLastFetched(new Date());

    } catch (err) {
      console.error("Error fetching sensor data:", err);
      const errorMessage = err.response?.data?.detail || err.message || 'Error al cargar los datos del sensor.';
      setError(errorMessage);
      // Solo mostrar toast si no es un error de token que ya se maneja con redirección
      if (errorMessage !== "Token de autenticación no encontrado. Por favor, inicie sesión de nuevo.") {
        toast.error(errorMessage, { position: "bottom-right" });
      }
      setLatestLectura(null);
      setLecturas([]);
       if (err.message === "Token de autenticación no encontrado. Por favor, inicie sesión de nuevo.") {
        handleLogout(); // Forzar logout y redirección
      }
    } finally {
      if (!autoRefresh || isInitialLoad) { 
        setLoading(false);
      }
    }
  }, [autoRefresh, timestampKey, navigate]); // navigate añadido a dependencias

  useEffect(() => {
    document.title = `Lecturas IoT - ${APP_NAME}`;
    const token = localStorage.getItem('token');
    if (!token) {
        toast.info("Por favor, inicie sesión para acceder a esta página.");
        navigate('/'); 
    } else {
        fetchLecturas(true); 
    }
  }, [fetchLecturas, navigate]); 
  
  const handleToggleAutoRefresh = () => {
    setAutoRefresh(prev => {
      const newState = !prev;
      if (newState) {
        toast.success('Actualización automática activada (cada 10s)', { position: "bottom-right" });
      } else {
        toast.warn('Actualización automática desactivada', { position: "bottom-right" });
      }
      return newState;
    });
  };

  useEffect(() => {
    let intervalId = null;
    if (autoRefresh && localStorage.getItem('token')) { // Solo refrescar si hay token
      intervalId = setInterval(() => {
        fetchLecturas(false); 
        toast.info('Datos actualizados automáticamente.', { autoClose: 2000, position: "bottom-right" });
      }, 10000); 
    }
    return () => clearInterval(intervalId);
  }, [autoRefresh, fetchLecturas]);

  const handleManualRefresh = () => {
    if (!localStorage.getItem('token')) {
      toast.error("No autenticado. Por favor, inicie sesión.");
      handleLogout();
      return;
    }
    toast.info('Actualizando datos...', { autoClose: 1000, position: "bottom-right" });
    fetchLecturas(false); 
  };

  // Función para clases de NavLink activo (tomada de Inicio.jsx)
  const getNavLinkClass = ({ isActive }) => isActive ? "nav-link active" : "nav-link";

  const pageTitle = "Monitor de Sensores IoT"; // Título del contenido de la página

  // Estilos para el contenedor de contenido que estaban inline, ahora se pueden manejar en LecturaSensor.css si se prefiere
  // o mantenerlos aquí si son específicos y no conflictivos.
  const pageContentStyle = {
    maxWidth: '1200px', 
    margin: '0 auto', // Quitado margen superior/inferior para que lo maneje el padding del main-content
    backgroundColor: 'var(--iot-card-background, white)', 
    borderRadius: 'var(--iot-card-border-radius, 0.35rem)', 
    padding: '25px', 
    boxShadow: 'var(--iot-card-shadow, 0 0 1px rgba(0,0,0,.125),0 1px 3px rgba(0,0,0,.2))' 
  };

  // Estilo para el contenedor de la página completa
   const standaloneContainerStyle = {
    // backgroundColor: 'var(--iot-background-color)', // Esto vendrá de inicio.css como --light-gray-bg
    minHeight: '100vh',
    display: 'flex', // Asegurar que es flex container
    flexDirection: 'column' // Asegurar que es flex column
  };


  if (loading && lecturas.length === 0 && !latestLectura && !error && localStorage.getItem('token')) {
    return (
        // Usar clases de inicio.css para la estructura general
        <div className="inicio-page-container" style={standaloneContainerStyle}> 
            {/* Barra de navegación principal (Placeholder) */}
            <div className="main-top-bar">
                <div className="container main-top-bar-content">
                    <span className="app-title">{APP_NAME}</span>
                    <button className="btn btn-logout" disabled>Cerrar Sesión</button>
                </div>
            </div>
            {/* Barra de navegación secundaria (Placeholder) */}
            <nav className="secondary-nav-bar">
                <div className="container">
                    <div className="nav-links-container">
                        {/* Placeholder links */}
                        <span className="nav-link" style={{opacity: 0.5}}>Inicio (Mapa)</span>
                        <span className="nav-link" style={{opacity: 0.5}}>Tablero PBI</span>
                        <span className="nav-link" style={{opacity: 0.5}}>Reportar Accidente</span>
                        <span className="nav-link" style={{opacity: 0.5}}>Gestión Usuarios</span>
                        <span className="nav-link active" style={{opacity: 0.5}}>Lecturas IoT</span>
                    </div>
                </div>
            </nav>
            {/* Contenido principal con spinner */}
            <main className="main-content container"> {/* Usar clase de inicio.css */}
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '300px' }}>
                    <Spinner text="Cargando datos iniciales del sensor..." />
                </div>
            </main>
        </div>
    );
  }
  
  return (
    // Aplicar clase de contenedor de página de inicio.css
    <div className="inicio-page-container" style={standaloneContainerStyle}> 
      {/* Barra de navegación principal (tomada de Inicio.jsx) */}
      <div className="main-top-bar">
        <div className="container main-top-bar-content">
          <span className="app-title">{APP_NAME}</span>
          <button onClick={handleLogout} className="btn btn-logout">
            Cerrar Sesión
          </button>
        </div>
      </div>
      {/* Barra de navegación secundaria (tomada de Inicio.jsx) */}
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

      {/* Contenido principal de LecturaSensor */}
      {/* Usar la clase main-content de inicio.css para el padding y estructura general */}
      <main className="main-content container">
        {/* El div con pageContentStyle ahora es el contenedor principal del contenido específico de la página */}
        <div style={pageContentStyle}> 
            <div className="page-header-iot"> {/* Esta clase es de LecturaSensor.css */}
                <h1 className="page-title-iot">
                    <Zap size={26} className="title-icon-iot" />
                    {pageTitle}
                </h1>
                <div className="data-page-controls-iot">
                    <button onClick={handleManualRefresh} disabled={loading && !autoRefresh} className="control-button-iot refresh-button-iot">
                        <RefreshCw size={16} className={loading && !autoRefresh ? 'spin-animation' : ''} />
                        <span>{loading && !autoRefresh ? 'Cargando...' : 'Actualizar'}</span>
                    </button>
                    <div className="auto-refresh-control-iot">
                        <label htmlFor="autoRefreshToggleIoT" className="toggle-label-iot">Auto-Refresco</label>
                        <button id="autoRefreshToggleIoT" role="switch" aria-checked={autoRefresh} onClick={handleToggleAutoRefresh} className={`toggle-switch-iot ${autoRefresh ? 'active' : ''}`}>
                            <span className="toggle-slider-iot"></span>
                        </button>
                    </div>
                </div>
            </div>

            {lastFetched && !loading && !error && (
              <div className="status-bar"> {/* Esta clase es de LecturaSensor.css */}
                <Clock size={15} />
                <span>Última actualización: {formatTimestamp(lastFetched, "Barra de estado")}</span>
              </div>
            )}
            
            {error && !latestLectura && lecturas.length === 0 && (
                <div className="error-container main-error"> {/* Esta clase es de LecturaSensor.css */}
                    <AlertTriangle size={32} />
                    <p className="error-title"><strong>Fallo al Cargar Datos del Sensor</strong></p>
                    <p className="error-details">{error}</p>
                    <small className="error-suggestion">Intente actualizar o verifique su conexión. Si el problema persiste, contacte soporte.</small>
                </div>
            )}

            {/* El resto del contenido específico de LecturaSensor (tarjetas, tabla) va aquí, usando sus propias clases de LecturaSensor.css */}
            <div className="main-content-grid"> {/* Clase de LecturaSensor.css */}
                <div className="grid-column column-latest-readings">
                    {(!error || latestLectura) && (
                    <section className="latest-readings-section data-section-card">
                    <h2 className="section-heading">
                        Lecturas Actuales
                    </h2>
                    {loading && !latestLectura && !error && ( 
                        <div className="loading-placeholder"><Spinner /> <p>Obteniendo últimas lecturas...</p></div>
                    )}
                    
                    {latestLectura && (
                        <div className="latest-reading-cards-grid">
                        <div className="reading-card temperature-card">
                            <div className="card-icon-background"> <Thermometer size={28} className="card-icon" /> </div>
                            <div className="card-content">
                            <p className="card-label">Temperatura</p>
                            <p className="card-value"> {latestLectura.temperatura !== null && latestLectura.temperatura !== undefined  ? latestLectura.temperatura.toFixed(1)  : 'N/A'} °C </p>
                            </div>
                        </div>
                        <div className="reading-card humidity-card">
                            <div className="card-icon-background"> <Droplets size={28} className="card-icon" /> </div>
                            <div className="card-content">
                            <p className="card-label">Humedad</p>
                            <p className="card-value"> {latestLectura.humedad !== null && latestLectura.humedad !== undefined ? latestLectura.humedad.toFixed(1) : 'N/A'} % </p>
                            </div>
                        </div>
                        <div className="reading-card timestamp-card">
                            <div className="card-icon-background"> <Clock size={26} className="card-icon" /> </div>
                            <div className="card-content">
                            <p className="card-label">Último Registro</p>
                            <p className="card-value-small">{formatTimestamp(latestLectura[timestampKey], "Tarjeta Último Registro")}</p>
                            </div>
                        </div>
                        </div>
                    )}
                    {!loading && !latestLectura && !error && (
                        <p className="no-data-message">No hay lecturas actuales disponibles.</p>
                    )}
                    </section>
                    )}
                </div>

                <div className="grid-column column-history-log">
                    {(!error || lecturas.length > 0) && (
                    <section className="history-log-section data-section-card">
                    <h2 className="section-heading">
                        <ListChecks size={20} style={{ marginRight: '8px', verticalAlign: 'middle' }}/>
                        Historial de Datos
                    </h2>
                    {loading && lecturas.length === 0 && !latestLectura && !error && (
                        <div className="loading-placeholder"><Spinner /> <p>Consultando historial...</p></div>
                    )}
                    {error && lecturas.length === 0 && (
                        <div className="error-container"> <AlertTriangle size={18} /> <p>Error al cargar historial: {error}</p> </div>
                    )}
                    {!loading && !error && lecturas.length === 0 && (
                        <p className="no-data-message">No hay datos históricos para mostrar.</p>
                    )}
                    {lecturas.length > 0 && (
                        <div className="table-responsive-wrapper">
                        <table className="readings-history-table">
                            <thead>
                            <tr>
                                <th>ID</th>
                                <th>Temp. (°C)</th>
                                <th>Hum. (%)</th>
                                <th>Fecha y Hora</th>
                            </tr>
                            </thead>
                            <tbody>
                            {lecturas.map((lectura) => (
                                // CORRECCIÓN: Usar lectura.id si ese es el identificador único.
                                // Si el ID de la lectura es 'id_lectura', mantenerlo.
                                // Asumiendo que el backend envía 'id' como identificador único de la lectura.
                                <tr key={lectura.id || lectura.id_lectura}> 
                                <td data-label="ID">{lectura.id || lectura.id_lectura}</td>
                                <td data-label="Temp."> <Thermometer size={16} className="table-icon temp-icon" /> {lectura.temperatura !== null && lectura.temperatura !== undefined ? lectura.temperatura.toFixed(1) : 'N/A'} </td>
                                <td data-label="Hum."> <Droplets size={16} className="table-icon hum-icon" /> {lectura.humedad !== null && lectura.humedad !== undefined ? lectura.humedad.toFixed(1) : 'N/A'} </td>
                                <td data-label="Fecha y Hora">{formatTimestamp(lectura[timestampKey], `Historial ID ${lectura.id || lectura.id_lectura}`)}</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                        </div>
                    )}
                    </section>
                    )}
                </div>
            </div>
        </div>
      </main>
    </div>
  );
};

export default LecturaSensor;
