-- init-db.sql
CREATE DATABASE claim_user;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'claim') THEN
        CREATE DATABASE claim;
    END IF;
END $$;
