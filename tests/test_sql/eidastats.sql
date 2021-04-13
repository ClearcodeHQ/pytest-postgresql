--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2 (Debian 13.2-1.pgdg100+1)
-- Dumped by pg_dump version 13.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: hll; Type: EXTENSION; Schema: -; Owner: -
--

-- CREATE EXTENSION IF NOT EXISTS hll WITH SCHEMA public;


--
-- Name: EXTENSION hll; Type: COMMENT; Schema: -; Owner:
--

-- COMMENT ON EXTENSION hll IS 'type for storing hyperloglog data';


-- SET default_tablespace = '';
--
-- SET default_table_access_method = heap;

--
-- Name: dataselect_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dataselect_stats (
    node_id integer,
    date date,
    network character varying(6),
    station character varying(5),
    location character varying(2),
    channel character varying(3),
    country character varying(2),
    bytes bigint,
    nb_reqs integer,
    nb_successful_reqs integer,
    nb_failed_reqs integer,
--     clients public.hll,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.dataselect_stats OWNER TO postgres;

--
-- Name: nodes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nodes (
    id serial,
    name text,
    contact text
);


ALTER TABLE public.nodes OWNER TO postgres;

--
-- Name: tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tokens (
    id serial,
    node_id integer,
    value character varying(32),
    valid_from timestamp with time zone NOT NULL,
    valid_until timestamp with time zone NOT NULL,
    create_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.tokens OWNER TO postgres;

--
-- Name: nodes nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_pkey PRIMARY KEY (id);


--
-- Name: dataselect_stats fk_nodes; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataselect_stats
    ADD CONSTRAINT fk_nodes FOREIGN KEY (node_id) REFERENCES public.nodes(id);

ALTER TABLE ONLY public.dataselect_stats
    ADD CONSTRAINT uniq_stat UNIQUE (date,network,station,location,channel,country);

--
-- Name: tokens fk_nodes; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tokens
    ADD CONSTRAINT fk_nodes FOREIGN KEY (node_id) REFERENCES public.nodes(id);


--
-- PostgreSQL database dump complete
--
