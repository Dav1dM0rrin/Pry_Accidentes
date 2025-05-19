// src/pages/ReportarAccidente.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, NavLink} from 'react-router-dom'; // NavLink y useLocation añadidos
import Breadcrumbs from '../components/Breadcrumbs';
import { toast } from 'react-toastify'; 
import Spinner from '../components/Spinner';

// Importar CSS para la barra de navegación y para el contenido específico
import '../styles/inicio.css'; // Para la barra de navegación
import '../styles/ReportarAccidente.css'; // Para el contenido específico

const API_URL = 'http://127.0.0.1:8000';
const APP_NAME = "Sistema de Accidentes Bquilla";

function ReportarAccidente() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    fecha: new Date().toISOString().slice(0, 16), sexo_victima: '', edad_victima: '', cantidad_victima: 1, condicion_victima_id: '', gravedad_victima_id: '', tipo_accidente_id: '', ubicacion_id: '',
  });
  const [condicionesVictima, setCondicionesVictima] = useState([]);
  const [gravedades, setGravedades] = useState([]);
  const [tiposAccidente, setTiposAccidente] = useState([]);
  const [ubicaciones, setUbicaciones] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true); // Iniciar en true para la carga inicial
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    toast.success("Sesión cerrada exitosamente.");
    navigate('/'); 
  };

  // Función para clases de NavLink activo
  const getNavLinkClass = ({ isActive }) => isActive ? "nav-link active" : "nav-link";

  useEffect(() => {
    document.title = `Reportar Accidente - ${APP_NAME}`;
    const token = localStorage.getItem('token');
    if (!token) {
      toast.info("Por favor, inicie sesión para acceder a esta página.");
      navigate('/');
    } else {
      fetchSelectData(token);
    }
  }, [navigate]); // Solo navigate para el chequeo inicial

  const fetchSelectData = async (token) => {
    setIsLoadingData(true);
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      const [condRes, gravRes, tipoRes, ubiRes] = await Promise.all([
        axios.get(`${API_URL}/condiciones-victima/`, config),
        axios.get(`${API_URL}/gravedades/`, config),
        axios.get(`${API_URL}/tipos-accidente/`, config),
        axios.get(`${API_URL}/ubicaciones/`, config),
      ]);
      setCondicionesVictima(condRes.data || []);
      setGravedades(gravRes.data || []);        
      setTiposAccidente(tipoRes.data || []);
      setUbicaciones(ubiRes.data || []);
      
      setFormData(prev => ({ 
          ...prev,
          condicion_victima_id: (condRes.data && condRes.data.length > 0 && condRes.data[0]?.id) ? condRes.data[0].id.toString() : '',
          gravedad_victima_id: (gravRes.data && gravRes.data.length > 0 && gravRes.data[0]?.id) ? gravRes.data[0].id.toString() : '',
          tipo_accidente_id: (tipoRes.data && tipoRes.data.length > 0 && tipoRes.data[0]?.id) ? tipoRes.data[0].id.toString() : '',
          ubicacion_id: (ubiRes.data && ubiRes.data.length > 0 && ubiRes.data[0]?.id) ? ubiRes.data[0].id.toString() : '',
      }));
    } catch (err) {
      let fetchError = 'Error al cargar datos para el formulario.';
      if (err.response && err.response.status === 401){
         fetchError = "No autorizado. Redirigiendo al login.";
         handleLogout(); // Forzar logout
      } else if (err.message) fetchError += ` Detalles: ${err.message}`;
      toast.error(fetchError);
    } finally {
      setIsLoadingData(false);
    }
  };
  
  const breadcrumbCrumbs = [
    { label: 'Inicio', path: '/inicio' },
    { label: 'Reportar Nuevo Accidente' } 
  ];

  const handleChange = (e) => { 
    const { name, value } = e.target; 
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => { 
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) { toast.error("No autenticado."); navigate('/'); return; }
    setIsSubmitting(true);
    
    if (!formData.fecha || !formData.condicion_victima_id || !formData.gravedad_victima_id || !formData.tipo_accidente_id || !formData.ubicacion_id) {
        toast.error("Complete campos obligatorios (*)."); setIsSubmitting(false); return;
    }
    // ... (resto de la lógica de validación y payload como la tenías)
    const parsedCondicionId = parseInt(formData.condicion_victima_id, 10);
    const parsedGravedadId = parseInt(formData.gravedad_victima_id, 10);
    const parsedTipoAccidenteId = parseInt(formData.tipo_accidente_id, 10);
    const parsedUbicacionId = parseInt(formData.ubicacion_id, 10);

    if (isNaN(parsedCondicionId) || isNaN(parsedGravedadId) || isNaN(parsedTipoAccidenteId) || isNaN(parsedUbicacionId)) {
        toast.error("IDs de selección no válidos."); setIsSubmitting(false); return;
    }
    const edadVictima = formData.edad_victima === '' ? null : parseInt(formData.edad_victima, 10);
    let cantidadVictima = formData.cantidad_victima === '' ? 1 : parseInt(formData.cantidad_victima, 10); 
    if (formData.edad_victima !== '' && isNaN(edadVictima)) { toast.error("Edad debe ser número."); setIsSubmitting(false); return; }
    if (formData.cantidad_victima !== '' && (isNaN(cantidadVictima) || (cantidadVictima !== null && cantidadVictima < 1)) ) {
        toast.error("Cantidad de víctimas debe ser >= 1."); setIsSubmitting(false); return;
    }
    const payload = {
        fecha: formData.fecha, sexo_victima: formData.sexo_victima === '' ? null : formData.sexo_victima,
        edad_victima: edadVictima, cantidad_victima: cantidadVictima, 
        condicion_victima_id: parsedCondicionId, gravedad_victima_id: parsedGravedadId,
        tipo_accidente_id: parsedTipoAccidenteId, ubicacion_id: parsedUbicacionId,
    };

    try {
      const response = await axios.post(`${API_URL}/accidentes/`, payload, { headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` } });
      toast.success(`Accidente reportado! ID: ${response.data.id}`);
      setFormData({ 
        fecha: new Date().toISOString().slice(0, 16), sexo_victima: '', edad_victima: '', cantidad_victima: 1, 
        condicion_victima_id: (condicionesVictima.length > 0 && condicionesVictima[0]?.id) ? condicionesVictima[0].id.toString() : '',
        gravedad_victima_id: (gravedades.length > 0 && gravedades[0]?.id) ? gravedades[0].id.toString() : '',
        tipo_accidente_id: (tiposAccidente.length > 0 && tiposAccidente[0]?.id) ? tiposAccidente[0].id.toString() : '',
        ubicacion_id: (ubicaciones.length > 0 && ubicaciones[0]?.id) ? ubicaciones[0].id.toString() : '',
      });
      setTimeout(() => navigate('/inicio'), 2000); 
    } catch (err) {
      let detailedErrorMessage = 'Error al reportar accidente.';
      if (err.response) {
        if (err.response.status === 401) {
            detailedErrorMessage = "No autorizado. Redirigiendo al login.";
            handleLogout();
        } else if (err.response.data && err.response.data.detail) {
          if (typeof err.response.data.detail === 'string') detailedErrorMessage = err.response.data.detail;
          else if (Array.isArray(err.response.data.detail)) detailedErrorMessage = err.response.data.detail.map(e => `${e.loc[1]}: ${e.msg}`).join('; ');
          else detailedErrorMessage = JSON.stringify(err.response.data.detail);
        } else if (err.response.status) detailedErrorMessage += ` (Código: ${err.response.status})`;
      } else detailedErrorMessage = err.message;
      toast.error(detailedErrorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Estilo para el contenedor de la página completa
   const pageContainerStyle = {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column'
  };

  return (
    <div className="inicio-page-container" style={pageContainerStyle}> {/* Clase de inicio.css */}
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
        {/* report-form-container es la tarjeta blanca que envuelve el formulario */}
        <div className="report-form-container"> {/* Clase de ReportarAccidente.css */}
          <Breadcrumbs crumbs={breadcrumbCrumbs} />
          {/* El botón de volver a inicio no es necesario si ya está en la barra de nav */}
          <h1 className="report-form-title">Reportar Nuevo Accidente</h1>
          
          {isLoadingData ? (
            <Spinner text="Cargando datos del formulario..." size="lg" />
          ) : (
            <form onSubmit={handleSubmit} className="report-form">
              <div className="form-group"> <label htmlFor="fecha" className="form-label">Fecha y Hora <span className="required-asterisk">*</span>:</label> <input type="datetime-local" name="fecha" id="fecha" value={formData.fecha} onChange={handleChange} required className="form-input" disabled={isSubmitting}/> </div>
              <div className="form-group"> <label htmlFor="ubicacion_id" className="form-label">Ubicación <span className="required-asterisk">*</span>:</label> <select name="ubicacion_id" id="ubicacion_id" value={formData.ubicacion_id} onChange={handleChange} required className="form-select" disabled={isSubmitting || ubicaciones.length === 0}> <option value="">{isLoadingData ? "Cargando..." : (ubicaciones.length === 0 ? "No hay ubicaciones" : "Seleccione ubicación")}</option> {ubicaciones.map(ubi => ubi && typeof ubi.id !== 'undefined' ? (<option key={ubi.id} value={ubi.id.toString()}>{`ID: ${ubi.id} - ${ubi.complemento || 'Sin compl.'} (B° ID: ${ubi.barrio_id})`}</option>) : null)} </select> </div>
              <div className="form-group"> <label htmlFor="tipo_accidente_id" className="form-label">Tipo Accidente <span className="required-asterisk">*</span>:</label> <select name="tipo_accidente_id" id="tipo_accidente_id" value={formData.tipo_accidente_id} onChange={handleChange} required className="form-select" disabled={isSubmitting || tiposAccidente.length === 0}> <option value="">{isLoadingData ? "Cargando..." : (tiposAccidente.length === 0 ? "No hay tipos" : "Seleccione tipo")}</option> {tiposAccidente.map(tipo => tipo && typeof tipo.id !== 'undefined' ? (<option key={tipo.id} value={tipo.id.toString()}>{tipo.nombre}</option>) : null)} </select> 
              </div>
              <div className="form-grid">
                <div className="form-group"> <label htmlFor="condicion_victima_id" className="form-label">Condición Víctima <span className="required-asterisk">*</span>:</label> <select name="condicion_victima_id" id="condicion_victima_id" value={formData.condicion_victima_id} onChange={handleChange} required className="form-select" disabled={isSubmitting || condicionesVictima.length === 0}> <option value="">{isLoadingData ? "Cargando..." : (condicionesVictima.length === 0 ? "No hay condiciones" : "Seleccione condición")}</option> {condicionesVictima.map(cond => cond && typeof cond.id !== 'undefined' ? (<option key={cond.id} value={cond.id.toString()}>{cond.rol_victima}</option>) : null)} </select> </div>
                <div className="form-group"> <label htmlFor="gravedad_victima_id" className="form-label">Gravedad Víctima <span className="required-asterisk">*</span>:</label> <select name="gravedad_victima_id" id="gravedad_victima_id" value={formData.gravedad_victima_id} onChange={handleChange} required className="form-select" disabled={isSubmitting || gravedades.length === 0}> <option value="">{isLoadingData ? "Cargando..." : (gravedades.length === 0 ? "No hay gravedades" : "Seleccione gravedad")}</option> {gravedades.map(grav => grav && typeof grav.id !== 'undefined' ? (<option key={grav.id} value={grav.id.toString()}>{grav.nivel_gravedad}</option>) : null)} </select> </div>
              </div>
              <div className="form-grid three-columns">
                <div className="form-group"> <label htmlFor="sexo_victima" className="form-label">Sexo Víctima:</label> <select name="sexo_victima" id="sexo_victima" value={formData.sexo_victima} onChange={handleChange} className="form-select" disabled={isSubmitting}> <option value="">No especificado</option><option value="M">Masculino</option><option value="F">Femenino</option><option value="O">Otro</option> </select> </div>
                <div className="form-group"> <label htmlFor="edad_victima" className="form-label">Edad Víctima:</label> <input type="number" name="edad_victima" id="edad_victima" value={formData.edad_victima} onChange={handleChange} min="0" className="form-input" disabled={isSubmitting} placeholder="Ej: 25"/> </div>
                <div className="form-group"> <label htmlFor="cantidad_victima" className="form-label">Cantidad Víctimas:</label> <input type="number" name="cantidad_victima" id="cantidad_victima" value={formData.cantidad_victima} onChange={handleChange} min="1" className="form-input" disabled={isSubmitting} placeholder="Ej: 1"/> </div>
              </div>
              <div className="form-actions"> 
                <button type="submit" className="btn btn-primary" disabled={isSubmitting || isLoadingData}> 
                  {isSubmitting ? <Spinner size="sm" showText={false} /> : 'Reportar Accidente'} 
                </button> 
              </div>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}

export default ReportarAccidente;
