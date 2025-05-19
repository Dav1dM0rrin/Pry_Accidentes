// src/pages/Inicio.jsx
import React, { useState, useEffect, useCallback } from "react";
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios'; 
import Spinner from '../components/Spinner';
import 'leaflet/dist/leaflet.css';
import '../styles/inicio.css'; 

// Importaciones de iconos de Leaflet
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Configuración de iconos por defecto de Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const API_URL = 'http://127.0.0.1:8000';
const APP_NAME = "Sistema de Accidentes Bquilla";

function Inicio() {
  const navigate = useNavigate();
  // Estados para datos y filtros
  const [accidents, setAccidents] = useState([]);
  const [barrios, setBarrios] = useState([]);
  const [tiposAccidente, setTiposAccidente] = useState([]); 
  const [gravedades, setGravedades] = useState([]);       
  const [filters, setFilters] = useState({
    barrio_id: "", fecha_desde: "", fecha_hasta: "", tipo_accidente_id: "", gravedad_id: ""
  });
  // Estados de carga
  const [isLoadingAccidents, setIsLoadingAccidents] = useState(false);
  const [isLoadingFiltersData, setIsLoadingFiltersData] = useState(false); 

  // Efecto para el título de la página y verificación de token
  useEffect(() => {
    document.title = `Inicio - ${APP_NAME}`;
    const token = localStorage.getItem('token');
    if (!token) {
        toast.info("Por favor, inicie sesión.");
        navigate('/'); 
    }
  }, [navigate]);

  // Construir parámetros para la API de accidentes
  const buildApiParams = useCallback(() => {
    const params = new URLSearchParams();
    if (filters.barrio_id) params.append("barrio_id", filters.barrio_id);
    if (filters.fecha_desde) params.append("fecha_desde", filters.fecha_desde);
    if (filters.fecha_hasta) params.append("fecha_hasta", filters.fecha_hasta);
    if (filters.tipo_accidente_id) params.append("tipo_accidente_id", filters.tipo_accidente_id);
    if (filters.gravedad_id) params.append("gravedad_id", filters.gravedad_id);
    return params.toString();
  }, [filters]); 

  // Efecto para obtener accidentes cuando cambian los filtros
  useEffect(() => {
    const fetchAccidents = async () => {
      setIsLoadingAccidents(true);
      const queryParams = buildApiParams();
      const apiUrl = `${API_URL}/api/accidentes/mapa?${queryParams}`;
      console.log(`Fetching accidents from: ${apiUrl}`);
      try {
        const response = await axios.get(apiUrl);
        if (Array.isArray(response.data)) {
          setAccidents(response.data);
        } else {
          toast.error("Formato de datos de accidentes inesperado.");
          setAccidents([]);
        }
      } catch (error) {
        toast.error(`Error al cargar accidentes: ${error.message}`);
        setAccidents([]);
      } finally {
        setIsLoadingAccidents(false);
      }
    };
    fetchAccidents();
  }, [buildApiParams]); 

  // Efecto para obtener datos de los filtros (barrios, tipos, gravedades)
  useEffect(() => {
    const fetchFiltersData = async () => {
      setIsLoadingFiltersData(true);
      try {
        const [barriosRes, tiposRes, gravedadesRes] = await Promise.all([
          axios.get(`${API_URL}/barrios/`),
          axios.get(`${API_URL}/tipos-accidente/`),
          axios.get(`${API_URL}/gravedades/`)
        ]);
        if (Array.isArray(barriosRes.data)) setBarrios(barriosRes.data); else toast.error("Error: Datos de barrios no es un array.");
        if (Array.isArray(tiposRes.data)) setTiposAccidente(tiposRes.data); else toast.error("Error: Datos de tipos de accidente no es un array.");
        if (Array.isArray(gravedadesRes.data)) setGravedades(gravedadesRes.data); else toast.error("Error: Datos de gravedades no es un array.");
      } catch (error) {
        toast.error(`Error al cargar datos de filtros: ${error.message}`);
      } finally {
        setIsLoadingFiltersData(false);
      }
    };
    fetchFiltersData();
  }, []);

  // Manejador para cambios en los filtros
  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prevFilters => ({ ...prevFilters, [name]: value }));
  };
  
  // Filtrar accidentes válidos para el mapa
  const validAccidentsForMap = accidents.filter(acc => {
    const isValid = acc && typeof acc.lat === 'number' && typeof acc.lng === 'number';
    if (acc && !isValid) console.warn("Accidente inválido para el mapa (lat/lng incorrectos):", acc);
    return isValid;
  });

  // Función para clases de NavLink activo
  const getNavLinkClass = ({ isActive }) => isActive ? "nav-link active" : "nav-link";

  // Función para manejar el logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    toast.success("Sesión cerrada exitosamente.");
    navigate('/');
  };

  return (
    <div className="inicio-page-container"> 
      {/* Barra de navegación principal */}
      <div className="main-top-bar"> 
        <div className="container main-top-bar-content"> 
          <span className="app-title">Sistema de Accidentes Bquilla</span>
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

      {/* Contenido principal */}
      <main className="main-content container"> 
        {/* Sección de filtros */}
        <div className="filter-section-container">
          <h3 className="filter-title">Filtrar Accidentes</h3>
          {isLoadingFiltersData ? <Spinner text="Cargando opciones de filtro..." /> : (
            <div className="filters-grid">
              {/* Filtro Barrio */}
              <div className="filter-group">
                <label htmlFor="barrio_id" className="filter-label">Barrio:</label>
                <select id="barrio_id" name="barrio_id" value={filters.barrio_id} onChange={handleFilterChange} className="filter-select" disabled={barrios.length === 0 && !isLoadingFiltersData}>
                  <option value="">Todos los Barrios</option>
                  {barrios.map((barrio) => ( barrio && typeof barrio.id !== 'undefined' && barrio.nombre ? <option key={barrio.id} value={barrio.id.toString()}>{barrio.nombre}</option> : null ))}
                </select>
              </div>
              {/* Filtro Tipo de Accidente */}
              <div className="filter-group">
                <label htmlFor="tipo_accidente_id" className="filter-label">Tipo Accidente:</label>
                <select id="tipo_accidente_id" name="tipo_accidente_id" value={filters.tipo_accidente_id} onChange={handleFilterChange} className="filter-select" disabled={tiposAccidente.length === 0 && !isLoadingFiltersData}>
                  <option value="">Todos los Tipos</option>
                  {tiposAccidente.map((tipo) => ( tipo && typeof tipo.id !== 'undefined' && tipo.nombre ? <option key={tipo.id} value={tipo.id.toString()}>{tipo.nombre}</option> : null ))}
                </select>
              </div>
              {/* Filtro Gravedad */}
              <div className="filter-group">
                <label htmlFor="gravedad_id" className="filter-label">Gravedad:</label>
                <select id="gravedad_id" name="gravedad_id" value={filters.gravedad_id} onChange={handleFilterChange} className="filter-select" disabled={gravedades.length === 0 && !isLoadingFiltersData}>
                  <option value="">Todas las Gravedades</option>
                  {gravedades.map((gravedad) => ( gravedad && typeof gravedad.id !== 'undefined' && gravedad.nivel_gravedad ? <option key={gravedad.id} value={gravedad.id.toString()}>{gravedad.nivel_gravedad}</option> : null ))}
                </select>
              </div>
              {/* Filtro Fecha Desde */}
              <div className="filter-group">
                <label htmlFor="fecha_desde" className="filter-label">Desde:</label>
                <input type="date" id="fecha_desde" name="fecha_desde" value={filters.fecha_desde} onChange={handleFilterChange} className="filter-input date-input"/>
              </div>
              {/* Filtro Fecha Hasta */}
              <div className="filter-group">
                <label htmlFor="fecha_hasta" className="filter-label">Hasta:</label>
                <input type="date" id="fecha_hasta" name="fecha_hasta" value={filters.fecha_hasta} onChange={handleFilterChange} className="filter-input date-input"/>
              </div>
            </div>
          )}
        </div>
        
        {isLoadingAccidents && <Spinner text="Cargando accidentes..." />}

        {/* Contenido del mapa y lista de reportes */}
        <div className="content-grid">
          {/* Tarjeta del Mapa */}
          <div className="map-card"> 
            <h2 className="card-title">🗺️ Mapa de Accidentes</h2>
            {!isLoadingAccidents && ( 
              <MapContainer center={[10.9878, -74.7889]} zoom={12} style={{ height: "500px", width: "100%", borderRadius: "0.5rem" }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap'/>
                {validAccidentsForMap.map(accident => ( <Marker key={accident.id} position={[accident.lat, accident.lng]}> <Popup> {accident.descripcion || "Detalles no disponibles"} <br /> <Link to={`/accidente/${accident.id}`} className="popup-link"> Ver Detalles &rarr; </Link> </Popup> </Marker> )) }
              </MapContainer>
            )}
          </div>

          {/* Tarjeta de Lista de Reportes */}
          <div className="reports-card"> 
            <h2 className="card-title">Lista de Reportes</h2>
            {!isLoadingAccidents && !accidents.length && (
              // 1. Mensaje "No hay datos" mejorado
              <div className="no-reports-message">
                <span className="no-reports-icon">⚠️</span> {/* Puedes usar un SVG o un icono de FontAwesome aquí */}
                <p>No se encontraron accidentes con los filtros aplicados.</p>
                <p>Intenta ajustar los criterios de búsqueda o ampliar el rango de fechas.</p>
              </div>
            )}
            {!isLoadingAccidents && accidents.length > 0 && (
                <ul className="reports-list">  
                  {accidents.map(accident => ( 
                    accident && accident.id ? 
                    <li key={accident.id} className="report-item"> 
                      <Link to={`/accidente/${accident.id}`} className="report-item-link"> 
                        <p>{accident.descripcion || "Sin descripción"}</p> 
                        <span className="view-details-prompt">Ver Detalles &rarr;</span> 
                      </Link> 
                    </li> 
                    : null 
                  ))} 
                </ul>
            )}
          </div>
        </div>
      </main>
      {/* Pie de página */}
      <footer className="main-footer"> &copy; {new Date().getFullYear()} Alcaldía de Barranquilla - Smart City. </footer>
    </div>
  );
}

export default Inicio;
