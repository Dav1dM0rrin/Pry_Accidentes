import React from 'react';

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-64 bg-blue-800 text-white p-5">
        <h2 className="text-2xl font-semibold mb-6">Accidentes Barranquilla</h2>
        <ul>
          <li className="mb-4">
            <a href="/" className="text-lg hover:text-gray-300">Dashboard</a>
          </li>
          <li className="mb-4">
            <a href="/reportes" className="text-lg hover:text-gray-300">Reportes</a>
          </li>
          <li className="mb-4">
            <a href="/zonas" className="text-lg hover:text-gray-300">Zonas de Riesgo</a>
          </li>
          <li>
            <a href="/usuarios" className="text-lg hover:text-gray-300">Usuarios</a>
          </li>
        </ul>
      </div>

      {/* Main Content */}
      <div className="flex-1 bg-gray-100 p-6">
        {/* Navbar */}
        <div className="flex justify-between items-center bg-white p-4 shadow-md mb-6">
          <div className="text-2xl font-semibold">Panel de Administración</div>
          <button className="bg-red-500 text-white px-4 py-2 rounded">Cerrar Sesión</button>
        </div>

        {/* Contenido Principal */}
        <div className="container mx-auto">{children}</div>
      </div>
    </div>
  );
};

export default Layout;
