-- Roles init — safe for Docker entrypoint
--
-- NOTE: dev_user and postgres are created automatically by Docker
-- from POSTGRES_USER env var. Only analyst_bot needs to be created here.
-- Using DO blocks so this is idempotent (safe to re-run).
--

SET default_transaction_read_only = off;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- Create postgres role if it doesn't exist (dump was made with postgres as owner)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'postgres') THEN
        CREATE ROLE postgres SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS;
    END IF;
END
$$;

-- Create analyst_bot only if it doesn't already exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analyst_bot') THEN
        CREATE ROLE analyst_bot WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'root123';
    END IF;
END
$$;

-- Grant read-all-data to analyst_bot
GRANT pg_read_all_data TO analyst_bot;