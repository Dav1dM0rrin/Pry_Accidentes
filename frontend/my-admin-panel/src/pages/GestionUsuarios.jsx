import React, { useState, useEffect } from "react";

const GestionUsuarios = () => {
    const [usuarios, setUsuarios] = useState([]);
    const [nombre, setNombre] = useState("");
    const [email, setEmail] = useState("");
    const [isFormVisible, setFormVisible] = useState(false);
    const [userIdToEdit, setUserIdToEdit] = useState(null);

    // Simulamos una base de datos con un array
    useEffect(() => {
        // Aquí puedes hacer una solicitud a la API para cargar los usuarios
        setUsuarios([
            { id: 1, nombre: "Juan Pérez", email: "juan@example.com" },
            { id: 2, nombre: "Ana López", email: "ana@example.com" },
        ]);
    }, []);

    // Función para mostrar el formulario de agregar/editar
    const mostrarFormulario = (id = null) => {
        if (id) {
            const usuario = usuarios.find((user) => user.id === id);
            if (usuario) {
                setNombre(usuario.nombre);
                setEmail(usuario.email);
                setUserIdToEdit(id);
            }
        } else {
            setNombre("");
            setEmail("");
            setUserIdToEdit(null);
        }
        setFormVisible(true);
    };

    // Función para ocultar el formulario
    const ocultarFormulario = () => {
        setFormVisible(false);
    };

    // Función para manejar el formulario
    const manejarFormulario = (e) => {
        e.preventDefault();
        if (userIdToEdit) {
            // Editar usuario
            setUsuarios(
                usuarios.map((usuario) =>
                    usuario.id === userIdToEdit
                        ? { ...usuario, nombre, email }
                        : usuario
                )
            );
        } else {
            // Agregar usuario
            const nuevoUsuario = {
                id: usuarios.length + 1,
                nombre,
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
        <div className="container">
            <h2>Gestión de Usuarios</h2>

            {/* Botón para agregar un nuevo usuario */}
            <button onClick={() => mostrarFormulario()} className="btn">
                Agregar Usuario
            </button>

            {/* Tabla de usuarios */}
            <table className="user-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {usuarios.map((usuario) => (
                        <tr key={usuario.id}>
                            <td>{usuario.id}</td>
                            <td>{usuario.nombre}</td>
                            <td>{usuario.email}</td>
                            <td>
                                <button
                                    onClick={() => mostrarFormulario(usuario.id)}
                                    className="btn editar"
                                >
                                    Editar
                                </button>
                                <button
                                    onClick={() => eliminarUsuario(usuario.id)}
                                    className="btn eliminar"
                                >
                                    Eliminar
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Formulario para agregar o editar usuarios */}
            {isFormVisible && (
                <div className="user-form">
                    <h3>{userIdToEdit ? "Editar Usuario" : "Nuevo Usuario"}</h3>
                    <form onSubmit={manejarFormulario}>
                        <input
                            type="text"
                            placeholder="Nombre"
                            value={nombre}
                            onChange={(e) => setNombre(e.target.value)}
                            required
                        />
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <button type="submit" className="btn">
                            {userIdToEdit ? "Guardar Cambios" : "Agregar Usuario"}
                        </button>
                        <button type="button" onClick={ocultarFormulario} className="btn cancelar">
                            Cancelar
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default GestionUsuarios;
