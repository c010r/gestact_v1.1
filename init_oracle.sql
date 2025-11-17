
        -- Crear usuario y tablespace para ASSE-GestACT
        CREATE TABLESPACE asse_gestit_data
            DATAFILE 'asse_gestit_data.dbf' SIZE 100M
            AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED;
        
        DROP USER asse_gestit_user CASCADE;
        CREATE USER asse_gestit_user
            IDENTIFIED BY asse_gestit_password
            DEFAULT TABLESPACE asse_gestit_data
            QUOTA UNLIMITED ON asse_gestit_data;
        
        GRANT CONNECT, RESOURCE, CREATE VIEW TO asse_gestit_user;
        