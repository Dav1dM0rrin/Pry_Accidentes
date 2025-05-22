// src/App.jsx
import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Inicio from "./pages/Inicio";
import GestionUsuarios from "./pages/GestionUsuarios";
import TableroAccidentes from "./pages/TableroAccidentes";
import ReportarAccidente from "./pages/ReportarAccidente";
import DetalleAccidente from "./pages/DetalleAccidente";


// 1. Importar react-toastify
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'; // Importar el CSS
import LecturaSensor from "./pages/LecturaSensor";

function App() {
  return (
    <> {/* Usar un Fragment para envolver Routes y ToastContainer */}
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/inicio" element={<Inicio />} />
        <Route path="/gestion-usuarios" element={<GestionUsuarios />} />
        <Route path="/tablero-accidentes" element={<TableroAccidentes />} /> 
        <Route path="/reportar-accidente" element={<ReportarAccidente />} /> 
        <Route path="/accidente/:accidenteId" element={<DetalleAccidente />} /> 
        <Route path="/lectura-sensor" element={<LecturaSensor />} /> 
      </Routes>
      {/* 2. Añadir ToastContainer aquí. Se puede configurar su posición, autoClose, etc. */}
      <ToastContainer
        position="top-right" // Posición de las notificaciones
        autoClose={5000} // Tiempo en ms para que se cierren automáticamente
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light" // o "dark" o "colored"
      />
    </>
  );
}

export default App;
