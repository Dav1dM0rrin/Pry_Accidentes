import axios from "axios";
import "../styles/gestion_usuarios.css";
import React, { useState, useEffect } from "react";

const GestionUsuarios = () => {
    // Se separan los estados para primer nombre y primer apellido
    const [usuarios, setUsuarios] = useState([]);
    const [primerNombre, setPrimerNombre] = useState("");
    const [primerApellido, setPrimerApellido] = useState("");
    const [email, setEmail] = useState("");
    const [isFormVisible, setFormVisible] = useState(false);
    const [userIdToEdit, setUserIdToEdit] = useState(null);

    useEffect(() => {
        axios.get("http://127.0.0.1:8000/usuarios/")
            .then((response) => {
                // Se asume que response.data es un array de objetos con: { id, primer_nombre, primer_apellido, email }
                setUsuarios(response.data);
                console.log("Usuarios registrados:", response.data);
            })
            .catch((error) => {
                console.error("Error al obtener los usuarios:", error);
            });
    }, []);

    // Mostrar el formulario de agregar/editar
    const mostrarFormulario = (id = null) => {
        if (id) {
            const usuario = usuarios.find((u) => u.id === id);
            if (usuario) {
                setPrimerNombre(usuario.primer_nombre);
                setPrimerApellido(usuario.primer_apellido);
                setEmail(usuario.email);
                setUserIdToEdit(id);
            }
        } else {
            setPrimerNombre("");
            setPrimerApellido("");
            setEmail("");
            setUserIdToEdit(null);
        }
        setFormVisible(true);
    };

    // Ocultar el formulario
    const ocultarFormulario = () => {
        setFormVisible(false);
    };

    // Manejo del formulario para agregar o editar
    const manejarFormulario = (e) => {
        e.preventDefault();
        if (userIdToEdit) {
            // Editar usuario
            setUsuarios(
                usuarios.map((usuario) =>
                    usuario.id === userIdToEdit
                        ? { ...usuario, primer_nombre: primerNombre, primer_apellido: primerApellido, email }
                        : usuario
                )
            );
        } else {
            // Agregar usuario
            const nuevoUsuario = {
                id: usuarios.length + 1,
                primer_nombre: primerNombre,
                primer_apellido: primerApellido,
                email,
            };
            setUsuarios([...usuarios, nuevoUsuario]);
        }
        ocultarFormulario();
    };

    // Función para eliminar usuario
    const eliminarUsuario = (id) => {
        const confirmDelete = window.confirm("¿Estás seguro de que deseas eliminar este usuario?");
        if (confirmDelete) {
            setUsuarios(usuarios.filter((usuario) => usuario.id !== id));
        }
    };

    return (
        <div className="gestion-container">
            <h2>Gestión de Usuarios</h2>
            
            {/* Tabla de usuarios */}
            <table className="user-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre Completo</th>
                        <th>Email</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {usuarios.map((usuario) => (
                        <tr key={usuario.id}>
                            <td>{usuario.id}</td>
                            <td>{usuario.primer_nombre + " " + usuario.primer_apellido}</td>
                            <td>{usuario.email}</td>
                            <td>
                                <button onClick={() => mostrarFormulario(usuario.id)} className="btn editar">
                                    Editar
                                </button>
                                <button onClick={() => eliminarUsuario(usuario.id)} className="btn eliminar">
                                    Eliminar
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Botón para agregar un nuevo usuario */}
            <div className="button-container">
                <button onClick={() => mostrarFormulario()} className="btn">
                    Agregar Usuario
                </button>
            </div>

            {/* Formulario para agregar o editar usuarios */}
            {isFormVisible && (
                <div className="user-form">
                    <h3>{userIdToEdit ? "Editar Usuario" : "Nuevo Usuario"}</h3>
                    <form onSubmit={manejarFormulario}>
                        <input
                            type="text"
                            placeholder="Primer Nombre"
                            value={primerNombre}
                            onChange={(e) => setPrimerNombre(e.target.value)}
                            required
                        />
                        <input
                            type="text"
                            placeholder="Primer Apellido"
                            value={primerApellido}
                            onChange={(e) => setPrimerApellido(e.target.value)}
                            required
                        />
                        <input
                            type="text"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <div className="button-container">
                            <button type="submit" className="btn">
                                {userIdToEdit ? "Guardar Cambios" : "Agregar Usuario"}
                            </button>
                            <button type="button" onClick={ocultarFormulario} className="btn cancelar">
                                Cancelar
                            </button>

                        </div>

                    </form>
                </div>
            )}
        </div>
    );
};

export default GestionUsuarios;
