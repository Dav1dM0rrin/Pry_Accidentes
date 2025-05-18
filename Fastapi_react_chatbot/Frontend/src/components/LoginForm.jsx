import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginForm = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    const loginData = {
      username: email,
      password: password,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(loginData),
      });

      const result = await response.json();

      if (response.ok) {
        localStorage.setItem("token", result.access_token); // ajusta esto si usas otro campo
        navigate("/inicio");
      } else {
        const errorDetail = typeof result.detail === "object" ? result.detail.msg : result.detail;
        setErrorMessage(errorDetail || "Error desconocido al intentar iniciar sesión.");
      }
    } catch (error) {
      console.error("Error en la solicitud:", error);
      setErrorMessage("Hubo un problema al conectar con el servidor.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <input
        type="text"
        id="email"
        placeholder="Correo electrónico"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        id="password"
        placeholder="Contraseña"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit" className="submit-button">
        Iniciar sesión
      </button>
      {errorMessage && <p className="error-message">{errorMessage}</p>}
    </form>
  );
};

export default LoginForm;
