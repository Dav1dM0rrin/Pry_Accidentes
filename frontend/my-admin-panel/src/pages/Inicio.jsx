import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios'; // Asegúrate de tener axios instalado (npm install axios o yarn add axios)
import '../styles/inicio.css';

// Iconos de Leaflet
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

function Inicio() {
  const [accidents, setAccidents] = useState([]);
  const [barrios, setBarrios] = useState([]); // Estado para almacenar la lista de barrios
  const [selectedBarrio, setSelectedBarrio] = useState(""); // Estado para el barrio seleccionado en el filtro

  // Efecto para cargar los accidentes cuando el componente se monta o cuando cambia el barrio seleccionado
  useEffect(() => {
    // Construir la URL de la API. Si hay un barrio seleccionado, añade el parámetro de consulta.
    const apiUrl = selectedBarrio
      ? `http://127.0.0.1:8000/api/accidentes/mapa?barrio_id=${selectedBarrio}`
      : "http://127.0.0.1:8000/api/accidentes/mapa";

    axios.get(apiUrl)
      .then((response) => {
        console.log("Accidentes recibidos:", response.data);
        // Asegúrate de que response.data es un array antes de actualizar el estado
        if (Array.isArray(response.data)) {
          setAccidents(response.data);
        } else {
          console.error("La respuesta de la API no es un array:", response.data);
          setAccidents([]); // Establecer a un array vacío para evitar errores
        }
      })
      .catch((error) => {
        console.error("Hubo un error al obtener los accidentes:", error);
        setAccidents([]); // En caso de error, vaciar la lista de accidentes
      });

  }, [selectedBarrio]); // Este efecto se ejecuta cuando selectedBarrio cambia

  // Efecto para cargar la lista de barrios una vez que el componente se monta
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/barrios/") // Endpoint para obtener barrios
      .then((response) => {
        console.log("Barrios recibidos:", response.data);
         // Asegúrate de que response.data es un array antes de actualizar el estado
        if (Array.isArray(response.data)) {
            setBarrios(response.data);
        } else {
            console.error("La respuesta de la API de barrios no es un array:", response.data);
            setBarrios([]); // Establecer a un array vacío
        }
      })
      .catch((error) => {
        console.error("Hubo un error al obtener los barrios:", error);
        setBarrios([]); // En caso de error, vaciar la lista de barrios
      });
  }, []); // Este efecto solo se ejecuta una vez al montar el componente

  // Manejador para el cambio en la selección del barrio
  const handleBarrioChange = (event) => {
    // Actualiza el estado con el ID del barrio seleccionado
    setSelectedBarrio(event.target.value);
  };

  return (
    <div className="container">
      <div className="top-bar">
        <span className="top-bar-title">Sistema de Control de Accidentes</span>
      </div>

      <div className="navbar">
        <a href="/tablero-accidentes">Tablero de Accidentes</a>
        <a href="/monitoreo-iot">Monitoreo IoT</a>
        <a href="/gestion-usuarios">Gestión de Usuarios</a>
        <a href="/gestion-accidentes">Gestión de Accidentes</a>
        <a href="/chatbot">Chatbot</a>
      </div>

      {/* Nuevo control para filtrar por barrio */}
      <div className="filter-container">
          <label htmlFor="barrio-select">Filtrar por Barrio:</label>
          <select
              id="barrio-select"
              value={selectedBarrio}
              onChange={handleBarrioChange}
          >
              <option value="">Todos los Barrios</option> {/* Opción por defecto para no filtrar */}
              {/* Mapea la lista de barrios para crear las opciones del select */}
              {barrios.map((barrio) => (
                  <option key={barrio.id} value={barrio.id}>
                      {barrio.nombre}
                  </option>
              ))}
          </select>
      </div>


      <div className="map-container">
        <h2 className="map-title">🗺️ Mapa de Barranquilla</h2>
        {/* Asegúrate de que la URL del TileLayer sea correcta */}
        <MapContainer center={[10.9631, -74.7963]} zoom={12} style={{ height: "500px", width: "100%" }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          {/* Mapea los accidentes y crea un Marker para cada uno */}
          {Array.isArray(accidents) &&
            accidents
              // Filtra accidentes con lat/lng válidos antes de mapear
              .filter(acc => acc && !isNaN(parseFloat(acc.lat)) && !isNaN(parseFloat(acc.lng)))
              .map(accident => (
                <Marker key={accident.id} position={[parseFloat(accident.lat), parseFloat(accident.lng)]}>
                  <Popup>{accident.descripcion}</Popup>
                </Marker>
              ))
          }
        </MapContainer>
      </div>

      <div className="info-container">
        <h2 className="last-accidents-title">Últimos Accidentes</h2>
        <div className="accident-list">
          <ul>
            {/* Muestra una lista de los accidentes (quizás los primeros 5 de la lista filtrada) */}
            {Array.isArray(accidents) && accidents.slice(0, 5).map(accident => (
              <li key={accident.id}>{accident.descripcion}</li>
            ))}
          </ul>
        </div>
        <div className="copyright">
          &copy; {new Date().getFullYear()} Barranquilla Smart City. Todos los derechos reservados.
        </div>
      </div>
    </div>
  );
}

export default Inicio;