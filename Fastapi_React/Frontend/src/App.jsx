import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Inicio from "./pages/Inicio";
import GestionUsuarios from "./pages/GestionUsuarios";
import TableroAccidentes from "./pages/TableroAccidentes";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/inicio" element={<Inicio />} />
      <Route path="/gestion-usuarios" element={<GestionUsuarios />} />
      <Route path="/tablero-accidentes" element={<TableroAccidentes />} /> 
    </Routes>
  );
}

export default App;
