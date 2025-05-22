// src/pages/TableroAccidentes.jsx
import React, { useEffect } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import { toast } from 'react-toastify';
import { BarChart3, LayoutDashboard } from 'lucide-react'; // Iconos para el título

// Importar CSS para la barra de navegación y para el contenido específico
import "../styles/inicio.css";         // Para la barra de navegación
import "../styles/tablero_accidentes.css"; // Estilos específicos para esta página

const APP_NAME = "Sistema de Accidentes Barranquilla";

const TableroAccidentes = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        toast.success("Sesión cerrada exitosamente.");
        navigate('/'); 
    };

    const getNavLinkClass = ({ isActive }) => isActive ? "nav-link active" : "nav-link";

    useEffect(() => {
        document.title = `Tablero PBI - ${APP_NAME}`;
        const token = localStorage.getItem('token');
        if (!token) {
            toast.info("Por favor, inicie sesión para acceder a esta página.");
            navigate('/');
        }
    }, [navigate]);
    
    return (
        <div className="inicio-page-container tablero-pbi-page"> {/* Clase de inicio.css y clase específica */}
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
            <main className="main-content container"> 
                <div className="tablero-header">
                    <LayoutDashboard size={32} className="header-icon" />
                    <h1 className="tablero-title">Tablero Interactivo de Siniestralidad Vial</h1>
                </div>
                <p className="tablero-description">
                    Visualiza y analiza los datos de accidentalidad en Barranquilla a través de nuestro dashboard interactivo de Power BI. 
                    Filtra, explora y obtén insights valiosos para la toma de decisiones.
                </p>
                
                <div className="iframe-container">
                    <iframe 
                        title="Dashboard Siniestralidad Barranquilla PBI" 
                        className="powerbi-iframe"
                        src="https://app.powerbi.com/reportEmbed?reportId=fbd18a43-df60-4b59-890c-85e2f46a7596&autoAuth=true&ctid=740be6bd-fd36-470e-94d9-0f0c777fadb9"
                        allowFullScreen={true}>
                            Tu navegador no soporta iframes. Por favor, actualízalo o usa uno diferente.
                    </iframe>
                </div>
                 <div className="iframe-notes">
                    <BarChart3 size={18} />
                    <span>El tablero puede tardar unos segundos en cargar. Si tienes problemas para visualizarlo, asegúrate de tener conexión a internet y que tu navegador permita contenido de terceros.</span>
                </div>
            </main>
             {/* Pie de página (opcional, si quieres mantenerlo consistente con Inicio.jsx) */}
            <footer className="main-footer"> 
                &copy; {new Date().getFullYear()} Alcaldía de Barranquilla - Smart City. 
            </footer>
        </div>
    );
}
export default TableroAccidentes;
