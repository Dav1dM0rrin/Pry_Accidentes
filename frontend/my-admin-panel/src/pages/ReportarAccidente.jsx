// src/pages/ReportarAccidente.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import '../styles/reportaracc.css';

const API_URL = 'http://127.0.0.1:8000';

function ReportarAccidente() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fecha: new Date().toISOString().slice(0, 16), 
    sexo_victima: '', 
    edad_victima: '', 
    cantidad_victima: 1, 
    condicion_victima_id: '', 
    gravedad_victima_id: '',
    tipo_accidente_id: '',
    ubicacion_id: '',
  });

  const [condicionesVictima, setCondicionesVictima] = useState([]);
  const [gravedades, setGravedades] = useState([]);
  const [tiposAccidente, setTiposAccidente] = useState([]);
  const [ubicaciones, setUbicaciones] = useState([]);
  
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const token = localStorage.getItem('token');

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(''); 
      try {
        const config = {
          headers: { Authorization: `Bearer ${token}` }
        };

        const [condRes, gravRes, tipoRes, ubiRes] = await Promise.all([
          axios.get(`${API_URL}/condiciones-victima/`, config),
          axios.get(`${API_URL}/gravedades/`, config),
          axios.get(`${API_URL}/tipos-accidente/`, config),
          axios.get(`${API_URL}/ubicaciones/`, config),
        ]);

        console.log("Datos de /condiciones-victima:", condRes.data);
        console.log("Datos de /gravedades:", gravRes.data);
        console.log("Datos de /tipos-accidente:", tipoRes.data);
        console.log("Datos de /ubicaciones:", ubiRes.data);

        setCondicionesVictima(condRes.data);
        setGravedades(gravRes.data);        
        setTiposAccidente(tipoRes.data);
        setUbicaciones(ubiRes.data);

        setFormData(prev => {
          const newFormData = { ...prev };

          // Condicion Victima
          if (condRes.data && condRes.data.length > 0 && condRes.data[0] && typeof condRes.data[0].id !== 'undefined' && condRes.data[0].id !== null) {
            newFormData.condicion_victima_id = condRes.data[0].id.toString();
          } else {
            if (condRes.data && condRes.data.length > 0 && condRes.data[0]) {
                console.warn("condRes.data[0] ('Condicion Victima') existe pero su 'id' es undefined o null:", condRes.data[0]);
            }
            newFormData.condicion_victima_id = ''; // Default a vacío si no se puede setear
          }

          // Gravedad Victima (Línea 56 original)
          if (gravRes.data && gravRes.data.length > 0 && gravRes.data[0] && typeof gravRes.data[0].id !== 'undefined' && gravRes.data[0].id !== null) {
            newFormData.gravedad_victima_id = gravRes.data[0].id.toString();
          } else {
            if (gravRes.data && gravRes.data.length > 0 && gravRes.data[0]) {
                console.warn("gravRes.data[0] ('Gravedad Victima') existe pero su 'id' es undefined o null:", gravRes.data[0]);
            }
            newFormData.gravedad_victima_id = '';
          }

          // Tipo Accidente
          if (tipoRes.data && tipoRes.data.length > 0 && tipoRes.data[0] && typeof tipoRes.data[0].id !== 'undefined' && tipoRes.data[0].id !== null) {
            newFormData.tipo_accidente_id = tipoRes.data[0].id.toString();
          } else {
             if (tipoRes.data && tipoRes.data.length > 0 && tipoRes.data[0]) {
                console.warn("tipoRes.data[0] ('Tipo Accidente') existe pero su 'id' es undefined o null:", tipoRes.data[0]);
            }
            newFormData.tipo_accidente_id = '';
          }

          // Ubicacion
          if (ubiRes.data && ubiRes.data.length > 0 && ubiRes.data[0] && typeof ubiRes.data[0].id !== 'undefined' && ubiRes.data[0].id !== null) {
            newFormData.ubicacion_id = ubiRes.data[0].id.toString();
          } else {
            if (ubiRes.data && ubiRes.data.length > 0 && ubiRes.data[0]) {
                console.warn("ubiRes.data[0] ('Ubicacion') existe pero su 'id' es undefined o null:", ubiRes.data[0]);
            }
            newFormData.ubicacion_id = '';
          }
          
          console.log("Nuevo estado de formData después de cargar datos:", newFormData);
          return newFormData;
        });

      } catch (err) {
        console.error("Error fetching data for form:", err);
        let fetchError = 'Error al cargar datos para el formulario.';
        if (err.response && err.response.status === 401) {
            fetchError = "No autorizado para cargar datos. Por favor, inicie sesión de nuevo.";
        } else if (err.message) {
            fetchError += ` Detalles: ${err.message}`;
        }
        setError(fetchError);
      } finally {
        setIsLoading(false);
      }
    };

    if (token) {
      fetchData();
    } else {
      setError("No autenticado. Por favor, inicie sesión.");
      navigate('/'); 
    }
  }, [token, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target; 
    setFormData({
      ...formData,
      [name]: value, 
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setIsLoading(true);

    if (!token) {
      setError("No autenticado. No se puede reportar el accidente.");
      setIsLoading(false);
      return;
    }
    
    if (!formData.fecha || !formData.condicion_victima_id || !formData.gravedad_victima_id || !formData.tipo_accidente_id || !formData.ubicacion_id) {
        setError("Por favor, complete todos los campos obligatorios marcados con * (Fecha, Condición, Gravedad, Tipo Accidente, Ubicación).");
        setIsLoading(false);
        return;
    }

    const parsedCondicionId = parseInt(formData.condicion_victima_id, 10);
    const parsedGravedadId = parseInt(formData.gravedad_victima_id, 10);
    const parsedTipoAccidenteId = parseInt(formData.tipo_accidente_id, 10);
    const parsedUbicacionId = parseInt(formData.ubicacion_id, 10);

    if (isNaN(parsedCondicionId) || isNaN(parsedGravedadId) || isNaN(parsedTipoAccidenteId) || isNaN(parsedUbicacionId)) {
        setError("Uno o más IDs de selección (Condición, Gravedad, Tipo, Ubicación) no son válidos. Asegúrese de seleccionar una opción válida de cada lista.");
        setIsLoading(false);
        return;
    }
    
    const edadVictima = formData.edad_victima === '' ? null : parseInt(formData.edad_victima, 10);
    let cantidadVictima = formData.cantidad_victima === '' ? 1 : parseInt(formData.cantidad_victima, 10); // Default a 1 si está vacío

    if (formData.edad_victima !== '' && isNaN(edadVictima)) {
        setError("La edad de la víctima debe ser un número válido.");
        setIsLoading(false);
        return;
    }
    
    if (formData.cantidad_victima !== '' && (isNaN(cantidadVictima) || (cantidadVictima !== null && cantidadVictima < 1)) ) {
        setError("La cantidad de víctimas debe ser un número válido mayor o igual a 1.");
        setIsLoading(false);
        return;
    }
    // Si cantidad_victima era '' y se seteó a 1, y el usuario realmente quería 0 o null (si el backend lo permite)
    // esta lógica debe ser revisada según los requisitos del backend para cantidad_victima.
    // Por ahora, si está vacío, se asume 1. Si tiene un valor no numérico, da error.


    const payload = {
        fecha: formData.fecha, 
        sexo_victima: formData.sexo_victima === '' ? null : formData.sexo_victima,
        edad_victima: edadVictima,
        cantidad_victima: cantidadVictima, 
        condicion_victima_id: parsedCondicionId,
        gravedad_victima_id: parsedGravedadId,
        tipo_accidente_id: parsedTipoAccidenteId,
        ubicacion_id: parsedUbicacionId,
    };
    
    console.log("Enviando payload:", payload);

    try {
      const response = await axios.post(`${API_URL}/accidentes/`, payload, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });
      setSuccessMessage(`Accidente reportado con éxito! ID: ${response.data.id}. Redirigiendo a Inicio...`);
      setFormData({ 
        fecha: new Date().toISOString().slice(0, 16),
        sexo_victima: '',
        edad_victima: '',
        cantidad_victima: 1, 
        condicion_victima_id: condicionesVictima.length > 0 && condicionesVictima[0].id ? condicionesVictima[0].id.toString() : '',
        gravedad_victima_id: gravedades.length > 0 && gravedades[0].id ? gravedades[0].id.toString() : '',
        tipo_accidente_id: tiposAccidente.length > 0 && tiposAccidente[0].id ? tiposAccidente[0].id.toString() : '',
        ubicacion_id: ubicaciones.length > 0 && ubicaciones[0].id ? ubicaciones[0].id.toString() : '',
      });
      setTimeout(() => {
        navigate('/inicio');
      }, 3000); 
    } catch (err) {
      console.error("Error reporting accident:", err.response ? err.response : err);
      let detailedErrorMessage = 'Error al reportar el accidente.';
      if (err.response) {
        if (err.response.status === 401) {
          detailedErrorMessage = "No autorizado. Por favor, inicie sesión de nuevo.";
        } else if (err.response.data && err.response.data.detail) {
          if (typeof err.response.data.detail === 'string') {
            detailedErrorMessage = err.response.data.detail;
          } 
          else if (Array.isArray(err.response.data.detail)) {
            detailedErrorMessage = err.response.data.detail.map(e => {
              const field = e.loc && e.loc.length > 1 ? e.loc[1] : "Campo desconocido";
              return `${field}: ${e.msg}`;
            }).join('; ');
          }
          else if (typeof err.response.data.detail === 'object') {
             detailedErrorMessage = JSON.stringify(err.response.data.detail);
          }
        } else if (err.response.status) {
            detailedErrorMessage += ` (Código: ${err.response.status})`;
        }
      } else if (err.message) {
        detailedErrorMessage = err.message;
      }
      setError(detailedErrorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="report-page-container">
      <div className="report-form-container">
        <button
          onClick={() => navigate('/inicio')}
          className="btn btn-secondary btn-back" 
        >
          &larr; Volver a Inicio
        </button>
        <h1 className="report-form-title">Reportar Nuevo Accidente</h1>
        
        {error && <div className="form-message error-message">{error}</div>}
        {successMessage && <div className="form-message success-message">{successMessage}</div>}

        <form onSubmit={handleSubmit} className="report-form">
          {/* Fecha */}
          <div className="form-group">
            <label htmlFor="fecha" className="form-label">Fecha y Hora del Accidente <span className="required-asterisk">*</span>:</label>
            <input
              type="datetime-local"
              name="fecha"
              id="fecha"
              value={formData.fecha}
              onChange={handleChange}
              required
              className="form-input"
              disabled={isLoading}
            />
          </div>

          {/* Ubicación */}
          <div className="form-group">
            <label htmlFor="ubicacion_id" className="form-label">Ubicación <span className="required-asterisk">*</span>:</label>
            <select name="ubicacion_id" id="ubicacion_id" value={formData.ubicacion_id} onChange={handleChange} required className="form-select" disabled={isLoading || ubicaciones.length === 0}>
              <option value="">{isLoading ? "Cargando..." : (ubicaciones.length === 0 ? "No hay ubicaciones" : "Seleccione ubicación")}</option>
              {ubicaciones.map(ubi => ubi && typeof ubi.id !== 'undefined' && ubi.id !== null ? (
                <option key={ubi.id} value={ubi.id.toString()}>
                  {`ID: ${ubi.id} - ${ubi.complemento || 'Sin complemento'} (Barrio ID: ${ubi.barrio_id})`}
                </option>
              ): null)}
            </select>
          </div>

          {/* Tipo Accidente */}
          <div className="form-group">
            <label htmlFor="tipo_accidente_id" className="form-label">Tipo de Accidente <span className="required-asterisk">*</span>:</label>
            <select name="tipo_accidente_id" id="tipo_accidente_id" value={formData.tipo_accidente_id} onChange={handleChange} required className="form-select" disabled={isLoading || tiposAccidente.length === 0}>
              <option value="">{isLoading ? "Cargando..." : (tiposAccidente.length === 0 ? "No hay tipos" : "Seleccione tipo")}</option>
              {tiposAccidente.map(tipo => tipo && typeof tipo.id !== 'undefined' && tipo.id !== null ? (
                <option key={tipo.id} value={tipo.id.toString()}>{tipo.nombre}</option>
              ) : null)}
            </select>
          </div>
          
          {/* Grid: Condición y Gravedad */}
          <div className="form-grid"> 
            <div className="form-group">
              <label htmlFor="condicion_victima_id" className="form-label">Condición Víctima <span className="required-asterisk">*</span>:</label>
              <select name="condicion_victima_id" id="condicion_victima_id" value={formData.condicion_victima_id} onChange={handleChange} required className="form-select" disabled={isLoading || condicionesVictima.length === 0}>
                <option value="">{isLoading ? "Cargando..." : (condicionesVictima.length === 0 ? "No hay condiciones" : "Seleccione condición")}</option>
                {condicionesVictima.map(cond => cond && typeof cond.id !== 'undefined' && cond.id !== null ? (
                  <option key={cond.id} value={cond.id.toString()}>{cond.rol_victima}</option>
                ) : null)}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="gravedad_victima_id" className="form-label">Gravedad Víctima <span className="required-asterisk">*</span>:</label>
              <select name="gravedad_victima_id" id="gravedad_victima_id" value={formData.gravedad_victima_id} onChange={handleChange} required className="form-select" disabled={isLoading || gravedades.length === 0}>
                <option value="">{isLoading ? "Cargando..." : (gravedades.length === 0 ? "No hay gravedades" : "Seleccione gravedad")}</option>
                {gravedades.map(grav => grav && typeof grav.id !== 'undefined' && grav.id !== null ? (
                  <option key={grav.id} value={grav.id.toString()}>{grav.nivel_gravedad}</option>
                ) : null)}
              </select>
            </div>
          </div>

          {/* Grid: Sexo, Edad, Cantidad */}
          <div className="form-grid three-columns"> 
            <div className="form-group">
              <label htmlFor="sexo_victima" className="form-label">Sexo Víctima:</label>
              <select name="sexo_victima" id="sexo_victima" value={formData.sexo_victima} onChange={handleChange} className="form-select" disabled={isLoading}>
                <option value="">No especificado</option>
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
                <option value="O">Otro</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="edad_victima" className="form-label">Edad Víctima:</label>
              <input type="number" name="edad_victima" id="edad_victima" value={formData.edad_victima} onChange={handleChange} min="0" className="form-input" disabled={isLoading} placeholder="Ej: 25"/>
            </div>
            <div className="form-group">
              <label htmlFor="cantidad_victima" className="form-label">Cantidad Víctimas:</label>
              <input type="number" name="cantidad_victima" id="cantidad_victima" value={formData.cantidad_victima} onChange={handleChange} min="1" className="form-input" disabled={isLoading} placeholder="Ej: 1"/>
            </div>
          </div>
          
          {/* Acciones */}
          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              {isLoading ? 'Reportando...' : 'Reportar Accidente'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ReportarAccidente;
