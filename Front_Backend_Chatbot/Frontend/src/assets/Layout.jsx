// src/assets/Layout.jsx
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import GlobalNavbar from '../components/GlobalNavbar'; // Importa la Navbar Global
// Asegúrate de que globalStyles.css se importa en App.jsx o main.jsx

const Layout = () => {
  const location = useLocation();

  // No mostrar GlobalNavbar en la página de login (ruta '/')
  if (location.pathname === '/') {
    return <Outlet />;
  }

  return (
    <div className="app-layout">
      <GlobalNavbar />
      {/* La clase main-page-content recibirá padding-top desde globalStyles.css */}
      <main className="main-page-content container"> {/* Añadido .container para centrar contenido */}
        <Outlet />
      </main>
      {/* Puedes añadir un footer global aquí si lo deseas */}
      {/* <footer className="app-footer">
        &copy; {new Date().getFullYear()} Alcaldía de Barranquilla - Smart City.
      </footer> */}
    </div>
  );
};

export default Layout;
