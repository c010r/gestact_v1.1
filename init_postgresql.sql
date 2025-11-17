
    -- Crear base de datos ASSE-GestACT
    DROP DATABASE IF EXISTS asse_gestit_db;
    CREATE DATABASE asse_gestit_db
            WITH ENCODING 'UTF8'
            LC_COLLATE = 'es_ES.UTF-8'
            LC_CTYPE = 'es_ES.UTF-8'
            TEMPLATE template0;
        
        -- Crear usuario para la aplicación
    DROP USER IF EXISTS asse_gestit_user;
    CREATE USER asse_gestit_user WITH PASSWORD 'asse_gestit_password';
    GRANT ALL PRIVILEGES ON DATABASE asse_gestit_db TO asse_gestit_user;
        