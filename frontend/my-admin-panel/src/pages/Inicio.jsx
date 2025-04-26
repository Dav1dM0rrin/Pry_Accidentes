import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
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

function Inicio() {
  const [accidents, setAccidents] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/accidentes/mapa")
      .then((response) => {
        console.log(response.data);
        setAccidents(response.data);
      })
      .catch((error) => {
        console.error("Hubo un error al obtener los accidentes:", error);
      });
  }, []);

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

      <h2 className="map-title">🗺️ Mapa de Barranquilla</h2>

      <MapContainer center={[10.9631, -74.7963]} zoom={12} style={{ height: "500px", width: "100%" }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Mostrar solo 20 accidentes con coordenadas válidas */}
        {Array.isArray(accidents) &&
          accidents
            .slice(0, 20)
            .filter(acc => !isNaN(parseFloat(acc.lat)) && !isNaN(parseFloat(acc.lng)))
            .map(accident => (
              <Marker key={accident.id} position={[parseFloat(accident.lat), parseFloat(accident.lng)]}>
                <Popup>{accident.descripcion}</Popup>
              </Marker>
            ))
        }
      </MapContainer>

      <div className="accident-list">
        <h3>Últimos Accidentes</h3>
        <ul>
          {accidents.slice(0, 5).map(accident => (
            <li key={accident.id}>{accident.descripcion}</li>
          ))}
        </ul>
      </div>

      <div className="copyright">
        &copy; 2025 Barranquilla Smart City. Todos los derechos reservados.
      </div>
    </div>
  );
}

export default Inicio;
