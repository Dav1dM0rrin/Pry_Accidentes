// src/components/Spinner.jsx
import React from 'react';
import '../styles/Spinner.css'; // Crearemos este archivo CSS

/**
 * Componente Spinner para mostrar una animación de carga.
 * @param {string} [size='md'] - Tamaño del spinner: 'sm', 'md', 'lg'.
 * @param {string} [text='Cargando...'] - Texto opcional a mostrar debajo del spinner.
 * @param {boolean} [showText=true] - Si se debe mostrar el texto.
 */
function Spinner({ size = 'md', text = 'Cargando...', showText = true }) {
  const sizeClass = `spinner-${size}`;

  return (
    <div className="spinner-container">
      <div className={`spinner ${sizeClass}`}></div>
      {showText && text && <p className="spinner-text">{text}</p>}
    </div>
  );
}

export default Spinner;