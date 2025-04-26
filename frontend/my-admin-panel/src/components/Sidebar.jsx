import React from "react";
import { Link } from "react-router-dom";

function Sidebar() {
  return (
    <div className="w-64 bg-gray-800 text-white p-6">
      <h2 className="text-xl font-semibold mb-8">Menú</h2>
      <ul>
        <li>
          <Link to="/dashboard" className="block py-2 px-4 hover:bg-gray-700 rounded">Tablero de Accidentes</Link>
        </li>
        <li>
          <Link to="#iot" className="block py-2 px-4 hover:bg-gray-700 rounded">Monitoreo IoT</Link>
        </li>
        <li>
          <Link to="#accidentes" className="block py-2 px-4 hover:bg-gray-700 rounded">Gestión de Accidentes</Link>
        </li>
        <li>
          <Link to="#chatbot" className="block py-2 px-4 hover:bg-gray-700 rounded">Chatbot</Link>
        </li>
      </ul>
    </div>
  );
}

export default Sidebar;
