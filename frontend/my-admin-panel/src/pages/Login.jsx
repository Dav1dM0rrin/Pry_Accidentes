import React from "react";
import LoginForm from "../components/LoginForm";
import "../styles/login.css"; // Asegúrate de que esté enlazado correctamente

const Login = () => {
  return (
    <div className="login-page">
      <div className="login-container">
        {/* Contenedor del formulario de login */}
        <div className="login-box bg-gradient-to-r from-blue-500 via-indigo-600 to-purple-700">
          <div className="text-center mb-6 animate__animated animate__fadeIn animate__delay-1s">
            <img
              src="/escudo_quilla.avif"
              alt="Escudo"
              className="logo animate__animated animate__zoomIn"
            />
            <h1 className="titulo text-white font-extrabold text-4xl mt-4 animate__animated animate__fadeIn animate__delay-1s">
              Sistema de Accidentes
            </h1>
            <p className="subtitulo text-white opacity-80 mb-4 animate__animated animate__fadeIn animate__delay-1s">
              Municipio de Barranquilla
            </p>
          </div>

          <LoginForm />

          <p className="copyright text-center text-white mt-6 animate__animated animate__fadeIn animate__delay-2s">
            © {new Date().getFullYear()} Alcaldía de Barranquilla. Todos los derechos reservados.
          </p>
        </div>

        {/* Contenedor del cuadro de bienvenida */}
        <div className="welcome-box animate__animated animate__fadeInRight">
          <h2>Bienvenido al Sistema de Control de Accidentalidad</h2>
          <p>
            Consulta y reporta la accidentalidad en las diferentes áreas de Barranquilla. <br />
            Ayúdanos a mejorar la seguridad vial y a reducir los riesgos en las zonas más críticas.
          </p>
        </div>
      </div>
    </div>

    
  );
};

export default Login;
