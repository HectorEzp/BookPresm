-- Ejecutar con el usuario maestro (admin) desde MySQL Workbench (vía túnel SSH)
CREATE DATABASE IF NOT EXISTS biblioteca CHARACTER SET utf8mb4;
USE biblioteca;

CREATE TABLE IF NOT EXISTS libros (
    id_libro INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    ejemplares_disponibles INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS prestamos (
    id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_libro INT NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_devolucion DATE NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    CONSTRAINT fk_prestamo_libro FOREIGN KEY (id_libro)
        REFERENCES libros (id_libro)
);

-- Datos de ejemplo
INSERT INTO libros (titulo, autor, isbn, ejemplares_disponibles) VALUES
('Cien años de soledad', 'Gabriel García Márquez', '9780307474728', 3),
('Los ríos profundos', 'José María Arguedas', '9788437604947', 2),
('Conversación en La Catedral', 'Mario Vargas Llosa', '9788420471839', 1);

INSERT INTO prestamos (id_libro, nombre_usuario, fecha_prestamo, estado) VALUES
(1, 'Ana Torres', CURDATE(), 'ACTIVO');

-- Usuarios con mínimo privilegio (reemplazar las contraseñas antes de ejecutar)
CREATE USER IF NOT EXISTS 'app_web'@'%' IDENTIFIED BY 'CAMBIAR_PASSWORD_WEB';
CREATE USER IF NOT EXISTS 'app_desktop'@'%' IDENTIFIED BY 'CAMBIAR_PASSWORD_DESKTOP';

GRANT SELECT, INSERT, UPDATE, DELETE ON biblioteca.* TO 'app_web'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON biblioteca.* TO 'app_desktop'@'%';
FLUSH PRIVILEGES;
