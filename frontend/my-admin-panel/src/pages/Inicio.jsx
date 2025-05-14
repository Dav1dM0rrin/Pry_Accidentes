// src/pages/Inicio.jsx
import React, { useState, useEffect, useCallback } from "react";
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Link } from 'react-router-dom'; // <-- 1. Importar Link
import 'leaflet/dist/leaflet.css';
import axios from 'axios'; 
import '../styles/inicio.css'; 

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const API_URL = 'http://127.0.0.1:8000';

function Inicio() {
  const [accidents, setAccidents] = useState([]);
  const [barrios, setBarrios] = useState([]);
  const [tiposAccidente, setTiposAccidente] = useState([]); 
  const [gravedades, setGravedades] = useState([]);       

  const [filters, setFilters] = useState({
    barrio_id: "",
    fecha_desde: "",
    fecha_hasta: "",
    tipo_accidente_id: "",
    gravedad_id: ""
  });
  
  const [isLoadingAccidents, setIsLoadingAccidents] = useState(false);
  const [isLoadingFiltersData, setIsLoadingFiltersData] = useState(false); 
  const [apiError, setApiError] = useState(null); 

  const buildApiParams = useCallback(() => {
    const params = new URLSearchParams();
    if (filters.barrio_id) params.append("barrio_id", filters.barrio_id);
    if (filters.fecha_desde) params.append("fecha_desde", filters.fecha_desde);
    if (filters.fecha_hasta) params.append("fecha_hasta", filters.fecha_hasta);
    if (filters.tipo_accidente_id) params.append("tipo_accidente_id", filters.tipo_accidente_id);
    if (filters.gravedad_id) params.append("gravedad_id", filters.gravedad_id);
    return params.toString();
  }, [filters]); 

  useEffect(() => {
    const fetchAccidents = async () => {
      setIsLoadingAccidents(true);
      setApiError(null); 
      const queryParams = buildApiParams();
      const apiUrl = `${API_URL}/api/accidentes/mapa?${queryParams}`;

      console.log(`Fetching accidents from: ${apiUrl}`);
      try {
        const response = await axios.get(apiUrl);
        console.log("Respuesta de /api/accidentes/mapa:", response);
        if (Array.isArray(response.data)) {
          setAccidents(response.data);
          console.log("Accidentes establecidos en el estado:", response.data);
        } else {
          console.error("La respuesta de /api/accidentes/mapa no es un array:", response.data);
          setAccidents([]);
          setApiError("Formato de datos de accidentes inesperado.");
        }
      } catch (error) {
        console.error("Hubo un error al obtener los accidentes:", error.response || error.message);
        setAccidents([]);
        setApiError(`Error al cargar accidentes: ${error.message}`);
      } finally {
        setIsLoadingAccidents(false);
      }
    };

    fetchAccidents();
  }, [buildApiParams]); 

  useEffect(() => {
    const fetchFiltersData = async () => {
      setIsLoadingFiltersData(true);
      setApiError(null); 
      console.log("Fetching filter data (barrios, tipos, gravedades)...");
      try {
        const [barriosRes, tiposRes, gravedadesRes] = await Promise.all([
          axios.get(`${API_URL}/barrios/`),
          axios.get(`${API_URL}/tipos-accidente/`),
          axios.get(`${API_URL}/gravedades/`)
        ]);

        if (Array.isArray(barriosRes.data)) setBarrios(barriosRes.data);
        else console.error("Datos de barrios no es un array:", barriosRes.data);

        if (Array.isArray(tiposRes.data)) setTiposAccidente(tiposRes.data);
        else console.error("Datos de tipos de accidente no es un array:", tiposRes.data);
        
        if (Array.isArray(gravedadesRes.data)) setGravedades(gravedadesRes.data);
        else console.error("Datos de gravedades no es un array:", gravedadesRes.data);

      } catch (error) {
        console.error("Hubo un error al obtener los datos para los filtros:", error.response || error.message);
        setApiError(`Error al cargar datos de filtros: ${error.message}`);
      } finally {
        setIsLoadingFiltersData(false);
      }
    };
    fetchFiltersData();
  }, []);

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prevFilters => ({
      ...prevFilters,
      [name]: value
    }));
  };
  
  const validAccidentsForMap = accidents.filter(acc => {
    const isValid = acc && typeof acc.lat === 'number' && typeof acc.lng === 'number';
    if (acc && !isValid) {
      console.warn("Accidente inválido para el mapa (lat/lng incorrectos):", acc);
    }
    return isValid;
  });

  return (
    <div className="inicio-page-container"> 
      <div className="main-top-bar"> 
        <div className="container"> 
          <span>Sistema de Control de Accidentes Bquilla</span>
        </div>
      </div>

      <nav className="secondary-nav-bar"> 
        <div className="container"> 
          <div className="nav-links-container"> 
            <a href="/inicio" className="nav-link">Inicio (Mapa)</a>
            <a href="/tablero-accidentes" className="nav-link">Tablero PBI</a>
            <a href="/reportar-accidente" className="nav-link">Reportar Accidente</a> 
            <a href="/gestion-usuarios" className="nav-link">Gestión Usuarios</a>
          
          </div>
        </div>
      </nav>

      <main className="main-content container"> 
        
        {apiError && (
          <div className="api-error-message"> 
            Error: {apiError}
          </div>
        )}

        <div className="filter-section-container">
          <h3 className="filter-title">Filtrar Accidentes</h3>
          {isLoadingFiltersData ? <p className="loading-message">Cargando opciones de filtro...</p> : (
            <div className="filters-grid">
              <div className="filter-group">
                <label htmlFor="barrio_id" className="filter-label">Barrio:</label>
                <select id="barrio_id" name="barrio_id" value={filters.barrio_id} onChange={handleFilterChange} className="filter-select" disabled={barrios.length === 0}>
                  <option value="">Todos los Barrios</option>
                  {barrios.map((barrio) => (
                    barrio && typeof barrio.id !== 'undefined' && barrio.nombre ? 
                    <option key={barrio.id} value={barrio.id.toString()}>
                      {barrio.nombre}
                    </option>
                    : null
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="tipo_accidente_id" className="filter-label">Tipo de Accidente:</label>
                <select id="tipo_accidente_id" name="tipo_accidente_id" value={filters.tipo_accidente_id} onChange={handleFilterChange} className="filter-select" disabled={tiposAccidente.length === 0}>
                  <option value="">Todos los Tipos</option>
                  {tiposAccidente.map((tipo) => (
                    tipo && typeof tipo.id !== 'undefined' && tipo.nombre ?
                    <option key={tipo.id} value={tipo.id.toString()}>
                      {tipo.nombre}
                    </option>
                    : null
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="gravedad_id" className="filter-label">Gravedad:</label>
                <select id="gravedad_id" name="gravedad_id" value={filters.gravedad_id} onChange={handleFilterChange} className="filter-select" disabled={gravedades.length === 0}>
                  <option value="">Todas las Gravedades</option>
                  {gravedades.map((gravedad) => (
                    gravedad && typeof gravedad.id !== 'undefined' && gravedad.nivel_gravedad ?
                    <option key={gravedad.id} value={gravedad.id.toString()}>
                      {gravedad.nivel_gravedad}
                    </option>
                    : null
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="fecha_desde" className="filter-label">Desde:</label>
                <input type="date" id="fecha_desde" name="fecha_desde" value={filters.fecha_desde} onChange={handleFilterChange} className="filter-input date-input"/>
              </div>

              <div className="filter-group">
                <label htmlFor="fecha_hasta" className="filter-label">Hasta:</label>
                <input type="date" id="fecha_hasta" name="fecha_hasta" value={filters.fecha_hasta} onChange={handleFilterChange} className="filter-input date-input"/>
              </div>
            </div>
          )}
        </div>
        
        {isLoadingAccidents && <p className="loading-message">Cargando accidentes en el mapa...</p>}

        <div className="content-grid">
          <div className="map-card"> 
            <h2 className="card-title">🗺️ Mapa de Accidentes en Barranquilla</h2>
            {!isLoadingAccidents && (
              <MapContainer center={[10.9878, -74.7889]} zoom={12} style={{ height: "500px", width: "100%", borderRadius: "0.5rem" }}>
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {validAccidentsForMap.map(accident => (
                    <Marker key={accident.id} position={[accident.lat, accident.lng]}>
                      <Popup>
                        {accident.descripcion || "Detalles no disponibles"}
                        <br />
                        {/* 2. Añadir Link en el Popup del Marcador */}
                        <Link to={`/accidente/${accident.id}`} className="popup-link">
                          Ver Detalles &rarr;
                        </Link>
                      </Popup>
                    </Marker>
                  ))
                }
              </MapContainer>
            )}
          </div>

          <div className="reports-card"> 
            <h2 className="card-title">Lista de Reportes Filtrados</h2>
            {isLoadingAccidents ? <p className="loading-message">Cargando reportes...</p> : (
              accidents.length > 0 ? (
                <ul className="reports-list">  
                  {accidents.map(accident => ( 
                    accident && accident.id ? 
                    // 3. Envolver el <li> con un Link o añadir un Link dentro
                    <li key={accident.id} className="report-item"> 
                      <Link to={`/accidente/${accident.id}`} className="report-item-link">
                        <p>{accident.descripcion || "Sin descripción"}</p>
                        <span className="view-details-prompt">Ver Detalles &rarr;</span>
                      </Link>
                    </li>
                    : null
                  ))}
                </ul>
              ) : (
                <p className="no-reports-message">
                  {!apiError ? "No hay accidentes para mostrar según los filtros aplicados." : "No se pudieron cargar los accidentes."}
                </p>
              )
            )}
          </div>
        </div>
      </main>

      <footer className="main-footer">
        &copy; {new Date().getFullYear()} Alcaldía de Barranquilla - Smart City. Todos los derechos reservados.
      </footer>
    </div>
  );
}

export default Inicio;
