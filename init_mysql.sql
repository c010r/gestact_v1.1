
        -- Crear base de datos ASSE-GestACT
        DROP DATABASE IF EXISTS asse_gestit_db;
        CREATE DATABASE asse_gestit_db
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci;
        
        -- Crear usuario para la aplicación
        DROP USER IF EXISTS 'asse_gestit_user'@'localhost';
        CREATE USER 'asse_gestit_user'@'localhost'
            IDENTIFIED BY 'asse_gestit_password';
        GRANT ALL PRIVILEGES ON asse_gestit_db.*
            TO 'asse_gestit_user'@'localhost';
        FLUSH PRIVILEGES;
        