import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import { BrowserRouter } from "react-router-dom"; // 👈 Importamos BrowserRouter


ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter> {/* 👈 Envolvemos App */}
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
