import { Routes, Route } from "react-router-dom";
import Login from "./pages/login";
import Inicio from "./pages/Inicio";
import GestionUsuarios from "./pages/GestionUsuarios";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/inicio" element={<Inicio />} />
      <Route path="/gestion-usuarios" element={<GestionUsuarios />} />
    </Routes>
  );
}

export default App;
