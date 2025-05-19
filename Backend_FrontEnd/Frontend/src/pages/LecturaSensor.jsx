// Frontend/src/pages/LecturaSensor.jsx
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import Spinner from '../components/Spinner'; 
import { Thermometer, Droplets, Zap, AlertTriangle, ListChecks, Clock, RefreshCw, LogOut, Home, BarChart2, FilePlus, Users, Wifi } from 'lucide-react'; // Iconos para la nueva barra
import { useNavigate, Link } from 'react-router-dom'; 
import '../styles/LecturaSensor.css'; 

const API_BASE_URL = "http://localhost:8000"; 
const API_ENDPOINT = "/lectura_sensor/"; 

const LecturaSensor = () => {
  const navigate = useNavigate();
  const [lecturas, setLecturas] = useState([]);
  const [latestLectura, setLatestLectura] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false); 
  const [lastFetched, setLastFetched] = useState(null);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    toast.info("Sesión cerrada exitosamente.");
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
        throw new Error("Token de autenticación no encontrado. Por favor, inicie sesión de nuevo.");
      }
      
      const apiUrl = `${API_BASE_URL}${API_ENDPOINT}`;
      const response = await axios.get(apiUrl, {
        headers: { Authorization: `Bearer ${token}` },
      });

      console.log("Datos crudos recibidos de la API:", response.data);

      let sortedLecturas = [];
      if (Array.isArray(response.data)) {
        // ***** CAMBIO POTENCIAL AQUÍ *****
        // Reemplaza 'a.timestamp' y 'b.timestamp' con el nombre real de tu campo de timestamp.
        // Por ejemplo, si tu campo se llama 'fecha_hora', usa 'a.fecha_hora' y 'b.fecha_hora'.
        const timestampKey = 'timestamp'; // <--- CAMBIA 'timestamp' SI ES NECESARIO

        sortedLecturas = response.data.sort((a, b) => {
            const dateA = new Date(a[timestampKey]); 
            const dateB = new Date(b[timestampKey]); 
            
            const timeA = !isNaN(dateA.getTime()) ? dateA.getTime() : 0;
            const timeB = !isNaN(dateB.getTime()) ? dateB.getTime() : 0;

            if (timeA === 0 && timeB === 0) return 0;
            if (timeA === 0) return 1; 
            if (timeB === 0) return -1;

            return timeB - timeA;
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
      toast.error(errorMessage, { position: "bottom-right" });
      setLatestLectura(null);
      setLecturas([]);
    } finally {
      if (!autoRefresh || isInitialLoad) { 
        setLoading(false);
      }
    }
  }, [autoRefresh]); 

  useEffect(() => {
    fetchLecturas(true); 
  }, [fetchLecturas]); 
  
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
    if (autoRefresh) {
      intervalId = setInterval(() => {
        fetchLecturas(false); 
        toast.info('Datos actualizados automáticamente.', { autoClose: 2000, position: "bottom-right" });
      }, 10000); 
    }
    return () => clearInterval(intervalId);
  }, [autoRefresh, fetchLecturas]);

  const handleManualRefresh = () => {
    toast.info('Actualizando datos...', { autoClose: 1000, position: "bottom-right" });
    fetchLecturas(false); 
  };

  const pageTitle = "Monitor de Sensores IoT";

  if (loading && lecturas.length === 0 && !latestLectura && !error) {
    return (
        <div className="lectura-iot-page-standalone-container">
            <nav className="app-navbar-standalone">
                <div className="app-navbar-level1">
                    <span className="app-navbar-brand">Sistema de Accidentes Bquilla</span>
                </div>
            </nav>
            <main className="page-content-area-standalone">
                <div className="loading-placeholder" style={{marginTop: "30px", fontSize: "1.1rem"}}>
                    <Spinner /> 
                    <p>Cargando datos iniciales del sensor...</p>
                </div>
            </main>
        </div>
    );
  }
  
  // ***** CAMBIO POTENCIAL AQUÍ (SI ES NECESARIO) *****
  // Asegúrate de que 'latestLectura.timestamp' y 'lectura.timestamp' usen el nombre correcto del campo.
  // La función formatTimestamp ya recibe el valor correcto si el objeto 'latestLectura' o 'lectura'
  // tiene la propiedad con el nombre correcto (ej. latestLectura.fecha_hora).
  // Si definiste `timestampKey` arriba, puedes usarlo aquí también para mayor consistencia,
  // aunque si el objeto ya tiene la propiedad con el nombre correcto, no es estrictamente necesario
  // cambiarlo aquí si la función `formatTimestamp` recibe el valor correcto.

  const timestampKey = 'timestamp'; // <--- USA LA MISMA CLAVE QUE DEFINISTE ARRIBA EN fetchLecturas

  return (
    <div className="lectura-iot-page-standalone-container"> 
      <nav className="app-navbar-standalone">
        <div className="app-navbar-level1">
            <span className="app-navbar-brand">Sistema de Accidentes Bquilla</span>
            <button onClick={handleLogout} className="app-navbar-logout" title="Cerrar Sesión">
                <LogOut size={18} /> Cerrar Sesión
            </button>
        </div>
        <div className="app-navbar-level2">
            <div className="app-nav-links">
                <Link to="/inicio" className="app-nav-link"> <Home size={16}/> Inicio (Mapa)</Link>
                <Link to="/tablero-accidentes" className="app-nav-link"><BarChart2 size={16}/> Tablero PBI</Link>
                <Link to="/reportar-accidente" className="app-nav-link"><FilePlus size={16}/> Reportar Accidente</Link>
                <Link to="/gestion-usuarios" className="app-nav-link"><Users size={16}/> Gestión Usuarios</Link>
                <Link to="/lectura-sensor" className="app-nav-link active"><Wifi size={16}/> Lecturas IoT</Link>
            </div>
        </div>
      </nav>

      <main className="page-content-area-standalone">
        <div className="page-header-iot">
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
          <div className="status-bar">
            <Clock size={15} />
            <span>Última actualización: {formatTimestamp(lastFetched, "Barra de estado")}</span>
          </div>
        )}
        
        {error && !latestLectura && lecturas.length === 0 && (
            <div className="error-container main-error">
                <AlertTriangle size={32} />
                <p className="error-title"><strong>Fallo al Cargar Datos del Sensor</strong></p>
                <p className="error-details">{error}</p>
                <small className="error-suggestion">Intente actualizar o verifique su conexión. Si el problema persiste, contacte soporte.</small>
            </div>
        )}

        <div className="main-content-grid">
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
                        <div className="card-icon-background">
                        <Thermometer size={28} className="card-icon" />
                        </div>
                        <div className="card-content">
                        <p className="card-label">Temperatura</p>
                        <p className="card-value">
                            {latestLectura.temperatura !== null && latestLectura.temperatura !== undefined 
                                ? latestLectura.temperatura.toFixed(1) 
                                : 'N/A'} °C
                        </p>
                        </div>
                    </div>
                    <div className="reading-card humidity-card">
                        <div className="card-icon-background">
                        <Droplets size={28} className="card-icon" />
                        </div>
                        <div className="card-content">
                        <p className="card-label">Humedad</p>
                        <p className="card-value">
                            {latestLectura.humedad !== null && latestLectura.humedad !== undefined 
                                ? latestLectura.humedad.toFixed(1) 
                                : 'N/A'} %
                        </p>
                        </div>
                    </div>
                    <div className="reading-card timestamp-card">
                        <div className="card-icon-background">
                            <Clock size={26} className="card-icon" />
                        </div>
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
                    <div className="error-container">
                    <AlertTriangle size={18} />
                    <p>Error al cargar historial: {error}</p>
                    </div>
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
                            <tr key={lectura.id_lectura}>
                            <td data-label="ID">{lectura.id_lectura}</td>
                            <td data-label="Temp.">
                                <Thermometer size={16} className="table-icon temp-icon" />
                                {lectura.temperatura !== null && lectura.temperatura !== undefined 
                                    ? lectura.temperatura.toFixed(1) 
                                    : 'N/A'}
                            </td>
                            <td data-label="Hum.">
                                <Droplets size={16} className="table-icon hum-icon" />
                                {lectura.humedad !== null && lectura.humedad !== undefined 
                                    ? lectura.humedad.toFixed(1) 
                                    : 'N/A'}
                            </td>
                            <td data-label="Fecha y Hora">{formatTimestamp(lectura[timestampKey], `Historial ID ${lectura.id_lectura}`)}</td>
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
      </main>
    </div>
  );
};

export default LecturaSensor;
