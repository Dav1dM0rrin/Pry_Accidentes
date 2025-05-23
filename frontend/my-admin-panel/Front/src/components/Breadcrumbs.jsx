// src/components/Breadcrumbs.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Breadcrumbs.css'; // Crearemos este archivo CSS

/**
 * Componente Breadcrumbs para mostrar la ruta de navegación.
 * @param {Array<Object>} crumbs - Un array de objetos, donde cada objeto tiene 'label' y 'path'.
 * La última miga puede no tener 'path' si es la página actual.
 * Ejemplo de crumbs:
 * [
 * { label: 'Inicio', path: '/inicio' },
 * { label: 'Reportar Accidente', path: '/reportar-accidente' }, // o sin path si es la actual
 * ]
 */
function Breadcrumbs({ crumbs }) {
  if (!crumbs || crumbs.length === 0) {
    return null;
  }

  return (
    <nav aria-label="breadcrumb" className="breadcrumbs-container">
      <ol className="breadcrumbs-list">
        {crumbs.map((crumb, index) => {
          const isLast = index === crumbs.length - 1;
          return (
            <li key={index} className={`breadcrumb-item ${isLast ? 'active' : ''}`}>
              {!isLast && crumb.path ? (
                <Link to={crumb.path} className="breadcrumb-link">
                  {crumb.label}
                </Link>
              ) : (
                <span className="breadcrumb-current" aria-current={isLast ? "page" : undefined}>
                  {crumb.label}
                </span>
              )}
              {!isLast && <span className="breadcrumb-separator">&gt;</span>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export default Breadcrumbs;
