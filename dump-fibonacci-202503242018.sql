--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

-- Started on 2025-03-24 20:18:57

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
-- TOC entry 6 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 5036 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 912 (class 1247 OID 49357)
-- Name: auth_provider; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.auth_provider AS ENUM (
    'telegram',
    'whatsapp',
    'google',
    'email'
);


ALTER TYPE public.auth_provider OWNER TO postgres;

--
-- TOC entry 906 (class 1247 OID 47415)
-- Name: authprovider; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.authprovider AS ENUM (
    'TELEGRAM',
    'WHATSAPP'
);


ALTER TYPE public.authprovider OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 230 (class 1259 OID 49727)
-- Name: admin_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admin_settings (
    id integer NOT NULL,
    key character varying NOT NULL,
    value character varying NOT NULL,
    description character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.admin_settings OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 49726)
-- Name: admin_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.admin_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admin_settings_id_seq OWNER TO postgres;

--
-- TOC entry 5037 (class 0 OID 0)
-- Dependencies: 229
-- Name: admin_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.admin_settings_id_seq OWNED BY public.admin_settings.id;


--
-- TOC entry 217 (class 1259 OID 49351)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 49372)
-- Name: auth_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider character varying NOT NULL,
    user_uuid uuid NOT NULL
);


ALTER TABLE public.auth_users OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 50030)
-- Name: credits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credits (
    id uuid NOT NULL,
    user_uuid uuid NOT NULL,
    credits integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.credits OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 49455)
-- Name: email_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_users (
    auth_id uuid NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    is_verified boolean DEFAULT false,
    verification_token character varying
);


ALTER TABLE public.email_users OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 49950)
-- Name: fillout_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fillout_data (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    form_id character varying NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    project_id uuid
);


ALTER TABLE public.fillout_data OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 49566)
-- Name: fillout_submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fillout_submissions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    fillout_id character varying NOT NULL,
    started_at timestamp without time zone NOT NULL,
    submitted_at timestamp without time zone,
    project_id uuid,
    requested_at timestamp without time zone,
    validated_at timestamp without time zone
);


ALTER TABLE public.fillout_submissions OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 49437)
-- Name: google_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.google_users (
    auth_id uuid NOT NULL,
    google_id character varying NOT NULL,
    email character varying NOT NULL
);


ALTER TABLE public.google_users OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 49423)
-- Name: invitations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invitations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    location character varying NOT NULL,
    role character varying NOT NULL,
    workplace character varying NOT NULL,
    birth_date character varying NOT NULL,
    goals character varying NOT NULL,
    education character varying NOT NULL,
    phone_number character varying NOT NULL,
    referral uuid,
    status character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.invitations OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 49710)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying NOT NULL,
    status character varying NOT NULL,
    payment_id character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    user_id uuid,
    total_amount double precision,
    currency character varying
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 49985)
-- Name: project_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_members (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    user_id uuid NOT NULL,
    role character varying(50) DEFAULT 'member'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.project_members OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 49969)
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_name character varying(255) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    owner_id uuid NOT NULL,
    allow_guests boolean DEFAULT false NOT NULL
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 49545)
-- Name: role_nodes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_nodes (
    id character varying NOT NULL,
    role character varying NOT NULL,
    fillout_id character varying,
    parent_id character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    project_id uuid,
    previous_sibling_id character varying
);


ALTER TABLE public.role_nodes OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 49385)
-- Name: telegram_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.telegram_users (
    auth_id uuid NOT NULL,
    telegram_id bigint NOT NULL
);


ALTER TABLE public.telegram_users OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 49581)
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id uuid NOT NULL,
    role text DEFAULT 'user'::text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 49580)
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_roles_id_seq OWNER TO postgres;

--
-- TOC entry 5038 (class 0 OID 0)
-- Dependencies: 226
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- TOC entry 218 (class 1259 OID 49363)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    uuid uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying,
    location character varying,
    role character varying,
    workplace character varying,
    birth_date character varying,
    goals character varying,
    education character varying,
    phone_number character varying,
    referral_code character varying NOT NULL,
    referral_id uuid,
    avatar_url character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    willing_to_contribute boolean
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 50448)
-- Name: waiting_list; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.waiting_list (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    status character varying DEFAULT 'pending'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    approved_at timestamp without time zone
);


ALTER TABLE public.waiting_list OWNER TO postgres;

--
-- TOC entry 4766 (class 2604 OID 49730)
-- Name: admin_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_settings ALTER COLUMN id SET DEFAULT nextval('public.admin_settings_id_seq'::regclass);


--
-- TOC entry 4760 (class 2604 OID 49584)
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- TOC entry 5025 (class 0 OID 49727)
-- Dependencies: 230
-- Data for Name: admin_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.admin_settings VALUES (1, 'filloutOnboardingId', '6DzLtyFsoXus', 'Fillout form ID used for user onboarding', '2025-03-02 01:52:30.744648+03', NULL);


--
-- TOC entry 5012 (class 0 OID 49351)
-- Dependencies: 217
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.alembic_version VALUES ('022_add_previous_sibling_id');


--
-- TOC entry 5014 (class 0 OID 49372)
-- Dependencies: 219
-- Data for Name: auth_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.auth_users VALUES ('8790abdf-4aa7-4dab-87e1-29e2224cd955', 'EMAIL', '5ef2163e-8827-4c68-b0f4-9f9bdc724af4');
INSERT INTO public.auth_users VALUES ('16194a0a-b66f-4f6a-8da1-4da2c03ec6aa', 'EMAIL', '8070e1a5-1a73-412a-9560-6fa08500f857');
INSERT INTO public.auth_users VALUES ('f77a0228-35a2-4256-9b50-84edda1bae98', 'EMAIL', '51235cb3-e1c4-4aa2-a1f5-569df2fe25ec');
INSERT INTO public.auth_users VALUES ('178f4e04-796c-48ef-896d-bf1c0f40f7d0', 'EMAIL', 'e8b6abbe-94ad-4bc3-8a66-fc5e66043286');
INSERT INTO public.auth_users VALUES ('8e043421-6e4a-4b4b-8b63-ccc579b527fc', 'EMAIL', '678e0d91-57cc-46a2-aa6f-938a3c5ec1dc');
INSERT INTO public.auth_users VALUES ('78dbb630-4cf0-4620-b608-4bcfc06c2ad6', 'EMAIL', 'd83c4d79-8149-44a9-80dd-3e62a696b759');
INSERT INTO public.auth_users VALUES ('08755bc1-2110-4b72-8596-3ed3d7d5f0e5', 'EMAIL', '0e21ea31-f70f-41ff-b8d7-37a759753ee8');
INSERT INTO public.auth_users VALUES ('138a73ff-d903-4f81-9136-d79c5f2dc14c', 'EMAIL', 'df043034-4604-48b0-ba80-f055f04f9fe3');
INSERT INTO public.auth_users VALUES ('3b416a18-e6e7-4b8b-8532-d9dcfdaf9033', 'EMAIL', '28f65606-645c-4f3e-bbf4-f0eea632ec14');


--
-- TOC entry 5029 (class 0 OID 50030)
-- Dependencies: 234
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.credits VALUES ('6b55d3d2-c2be-4e41-a128-9578502bf127', '8070e1a5-1a73-412a-9560-6fa08500f857', 6, '2025-03-10 20:22:18.035838', '2025-03-10 20:22:18.035838');


--
-- TOC entry 5018 (class 0 OID 49455)
-- Dependencies: 223
-- Data for Name: email_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.email_users VALUES ('8790abdf-4aa7-4dab-87e1-29e2224cd955', 'stask@viete.io', '$2b$12$s.Gqqp.4QeaiayNVQrK03.QIM8L.nbmDd4Mc5lrY5Gg48sH8OLH7W', false, '9yGPQZSNz4u9cCQ0b-5EySW5PhXXJOpfOuqAVz7bC3E');
INSERT INTO public.email_users VALUES ('16194a0a-b66f-4f6a-8da1-4da2c03ec6aa', 'kapulkin@gmail.com', '$2b$12$QvWiq85ZPwkSvHPzH2F6xOlALxkStZOq2O13FHQLRq2TITwxGcU.y', false, 'SPz5g2pRJB5ukHorzczV1wzbBCJnyFCL7J9lWZv58J8');
INSERT INTO public.email_users VALUES ('f77a0228-35a2-4256-9b50-84edda1bae98', 'test@test.com', '$2b$12$Ryl9rEPySzm3X.Ex2Yrn7.Jp2L8c6YBIvkTAbxx4iEXGmFXSQpNQy', false, 'jfv3NAMdr-sSfu5xqRtwa5Mx1s1-pIBBbRaW8I2_Ieg');
INSERT INTO public.email_users VALUES ('178f4e04-796c-48ef-896d-bf1c0f40f7d0', 'test2@test.com', '$2b$12$lFJKuM.wfFoj5TB6YYcoVeSD5XmiRt9QLXx22jOyWfaQkFyPEZ.sG', false, 'UB5r3YQpnpv4ChaM97RU1NYF2iUDrWuYck6Xp9gmwFQ');
INSERT INTO public.email_users VALUES ('8e043421-6e4a-4b4b-8b63-ccc579b527fc', 'test3@test.com', '$2b$12$q1JG2oiUnVXTjALiZs1USuHgP5TYVhdztLjpot5isQk7ezCMTsraC', false, 'fmfDICsW2993oBwv_kHKOq53E3m4T2fsDrGM73kc3i8');
INSERT INTO public.email_users VALUES ('78dbb630-4cf0-4620-b608-4bcfc06c2ad6', 'test4@test.com', '$2b$12$pnQNcdi/6qtf88pOpZR3Zu.rPV8AOJ85WoD5bz9y4/csYZdjGgh8W', false, 'NAis9PtFhcbfsDkIrmO5XgdiDnEilwJJg7XaGHWfgdQ');
INSERT INTO public.email_users VALUES ('08755bc1-2110-4b72-8596-3ed3d7d5f0e5', 'test6@test.com', '$2b$12$jjuTDrtH2uhk5aFtgwYBvumRxemprcx7/I5JisuL8PI1elgoNEFS.', false, 'B43ZKmPbM0zp1YNDb_TpIxb8TM39POZYMfvGkelR8yA');
INSERT INTO public.email_users VALUES ('138a73ff-d903-4f81-9136-d79c5f2dc14c', 'kapulkin2@gmail.com', '$2b$12$ef4KNJbGdsKLw58ACCGRy.bxBYd4wE9ZehaHhxWyPV6pVPbvC3R8.', false, 'uWKCE0QBHF0kaY5I-o1m-6XgGNq5P7Zd9qLsihgX-4Y');
INSERT INTO public.email_users VALUES ('3b416a18-e6e7-4b8b-8532-d9dcfdaf9033', 'kapulkin3@gmail.com', '$2b$12$BepZ6KeMLM8HqlrI7vGj4OkaVDhn1kuVIIo5RcHedOxpxV7efs1t6', false, 'xPyv5d__qSCbW95u2Vn858zDS0esV17Indmb9CkE4AE');


--
-- TOC entry 5026 (class 0 OID 49950)
-- Dependencies: 231
-- Data for Name: fillout_data; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5020 (class 0 OID 49566)
-- Dependencies: 225
-- Data for Name: fillout_submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.fillout_submissions VALUES ('c37d9182-93a3-4cc2-8771-b90d5b6dc824', '8070e1a5-1a73-412a-9560-6fa08500f857', 'mgmt-form-1', '2025-02-20 15:35:38.34832', NULL, NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('dda2dced-61b1-4def-93d1-af4e50d47626', '8070e1a5-1a73-412a-9560-6fa08500f857', 'i8uLkjbaAUus', '2025-02-26 02:20:40.772427', '2025-02-26 02:34:01.774314', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('6b0c49f4-edde-45b3-ab9e-5d80212531eb', '8070e1a5-1a73-412a-9560-6fa08500f857', 'i8uLkjbaAUus', '2025-02-26 02:21:37.687363', '2025-02-26 02:54:35.555639', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('a37d6d83-49a9-4e9d-b284-e1c3156f0999', '8070e1a5-1a73-412a-9560-6fa08500f857', 'i8uLkjbaAUus', '2025-02-26 02:23:18.596562', '2025-02-26 03:02:45.251491', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('89fe1bd2-b5f2-40c0-bb25-fcdb8e6075b3', '8070e1a5-1a73-412a-9560-6fa08500f857', 'i8uLkjbaAUus', '2025-02-26 02:23:43.850592', '2025-02-26 03:03:25.393491', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('694b75f2-6d3d-4873-9d88-ad641fb0dd00', '8070e1a5-1a73-412a-9560-6fa08500f857', 'i8uLkjbaAUus', '2025-02-26 02:25:00.64714', '2025-02-26 03:04:11.338494', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('0e4b8648-a8a7-4457-b9a2-cf845d2c7ff5', '8070e1a5-1a73-412a-9560-6fa08500f857', 'i8uLkjbaAUus', '2025-02-26 02:26:02.695873', '2025-02-26 03:04:48.166923', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('abd9559c-78cf-45c1-bd82-325ca67c6e1a', '8070e1a5-1a73-412a-9560-6fa08500f857', 'i8uLkjbaAUus', '2025-02-26 02:26:15.984198', '2025-02-26 03:04:57.898641', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('fe3f7f38-8c55-47a1-bbc5-bfbdf53cf6a3', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pnFVN8tU1mus', '2025-02-28 14:04:37.233688', '2025-02-28 14:04:37.233688', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('06c70a49-fc5a-4aa7-b37f-3165666d0b56', '8070e1a5-1a73-412a-9560-6fa08500f857', 'test', '2025-03-09 04:13:05.057463', NULL, NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('3943305b-12b3-4eaa-8554-8b44393abfb0', '8070e1a5-1a73-412a-9560-6fa08500f857', 'eZxt6FKmhZus', '2025-03-09 07:38:55.553236', '2025-03-09 07:39:19.465891', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('183b5740-f713-4181-a5ff-a6740322582f', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pnFVN8tU1mus', '2025-03-10 05:39:56.955064', NULL, NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('764c3a32-c5e8-4145-a565-4912e54a9f3e', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pnFVN8tU1mus', '2025-03-10 05:41:24.774166', NULL, NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('a3825201-ec05-47fc-9033-3867b866ef4d', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pnFVN8tU1mus', '2025-03-10 05:41:52.609195', NULL, NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('b31a41bd-6965-4822-b6e8-d1889f6f9752', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pnFVN8tU1mus', '2025-03-10 06:46:46.519845', NULL, NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('b05b5fa7-cb5a-4cb4-8474-9612c0cb4618', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pnFVN8tU1mus', '2025-03-10 05:39:39.299651', '2025-03-10 07:44:38.310153', NULL, NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('48a6e20f-5951-4bf9-91bb-8acdb7acee71', '8070e1a5-1a73-412a-9560-6fa08500f857', 'eZxt6FKmhZus', '2025-03-10 08:52:01.766877', NULL, '87bb2118-7fbf-4cd4-8db4-f2fd4f6eeea0', NULL, NULL);
INSERT INTO public.fillout_submissions VALUES ('f2572b63-47d9-4889-bce2-e1ec251ce433', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pnFVN8tU1mus', '2025-02-28 06:01:03.034872', '2025-02-28 06:01:32.495343', NULL, '2025-03-10 20:19:33.877115', NULL);


--
-- TOC entry 5017 (class 0 OID 49437)
-- Dependencies: 222
-- Data for Name: google_users; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5016 (class 0 OID 49423)
-- Dependencies: 221
-- Data for Name: invitations; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.invitations VALUES ('86597972-7804-4fc6-b681-3e5a7244f063', 's', 's', 's', 's', '1988-04-28', 's', 's', 's', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pending', '2025-02-17 22:11:33.634341');
INSERT INTO public.invitations VALUES ('ef577e94-6219-4fa5-92ee-06ec461b6d02', 'j', 'j', 'j', 'j', '1988-04-28', 'k', 'k', 'k', '8070e1a5-1a73-412a-9560-6fa08500f857', 'used', '2025-02-17 23:30:39.054436');
INSERT INTO public.invitations VALUES ('7d411682-a93f-4291-89a7-83b95345be4b', 'x', 'x', 'x', 'x', '1988-04-28', 'x', 'xx', 'x', '8070e1a5-1a73-412a-9560-6fa08500f857', 'used', '2025-02-17 23:55:32.558593');
INSERT INTO public.invitations VALUES ('73ed1d22-ffe7-483b-89ae-9bd0aef0bbab', 'j', 'j', 'j', 'j', '1988-04-28', 'h', 'h', 'h', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pending', '2025-02-18 00:10:26.214947');
INSERT INTO public.invitations VALUES ('1876607c-5303-4f4a-9177-a01e6a555e3a', 'A', 'A', 'A', 'A', '1988-04-28', 'A', 'sad', 'sada', '8070e1a5-1a73-412a-9560-6fa08500f857', 'pending', '2025-03-14 19:16:25.099145');


--
-- TOC entry 5023 (class 0 OID 49710)
-- Dependencies: 228
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5028 (class 0 OID 49985)
-- Dependencies: 233
-- Data for Name: project_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.project_members VALUES ('a1ab725f-ea95-415f-8c87-17ec0260dbd1', '87bb2118-7fbf-4cd4-8db4-f2fd4f6eeea0', '8070e1a5-1a73-412a-9560-6fa08500f857', 'member', '2025-03-09 06:32:09.803916');


--
-- TOC entry 5027 (class 0 OID 49969)
-- Dependencies: 232
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.projects VALUES ('87bb2118-7fbf-4cd4-8db4-f2fd4f6eeea0', 'Promptbuilder', '', '2025-03-07 11:33:33.479249', '2025-03-09 01:50:00.661477', '8070e1a5-1a73-412a-9560-6fa08500f857', false);


--
-- TOC entry 5019 (class 0 OID 49545)
-- Dependencies: 224
-- Data for Name: role_nodes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.role_nodes VALUES ('d08fa328-fa99-4e24-904a-3d6bf72b8abd', 'Stage 0: Newborn', NULL, NULL, '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('7c8bd800-1a4f-4c1f-a661-d07b7e4c18dd', 'Stage 55: Mid to Late Adult (35-55 years)', NULL, 'd08fa328-fa99-4e24-904a-3d6bf72b8abd', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('998c0248-afe7-47e2-9fd7-d9a2e6917b83', 'Advanced Career Path', NULL, '7c8bd800-1a4f-4c1f-a661-d07b7e4c18dd', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('198d279e-2dad-48c1-b333-d385a04107a1', 'Executive Education Courses', NULL, '998c0248-afe7-47e2-9fd7-d9a2e6917b83', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('e1d4b756-de45-40ff-82aa-23bb67764ed3', 'Senior Management / Leadership', NULL, '998c0248-afe7-47e2-9fd7-d9a2e6917b83', '2025-03-16 00:56:36.577842+03', NULL, NULL, '198d279e-2dad-48c1-b333-d385a04107a1');
INSERT INTO public.role_nodes VALUES ('593703d0-b261-48f9-9cc3-0f1e9322562d', 'Family & Personal Growth', NULL, '7c8bd800-1a4f-4c1f-a661-d07b7e4c18dd', '2025-03-16 00:56:36.577842+03', NULL, NULL, '998c0248-afe7-47e2-9fd7-d9a2e6917b83');
INSERT INTO public.role_nodes VALUES ('702c1c52-e6fb-440a-9f07-ad9579d12f5d', 'Raising Children (if any)', NULL, '593703d0-b261-48f9-9cc3-0f1e9322562d', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('d457d841-d420-4fcd-ae9b-24eb0ee84d14', 'Financial Planning & Investments', NULL, '593703d0-b261-48f9-9cc3-0f1e9322562d', '2025-03-16 00:56:36.577842+03', NULL, NULL, '702c1c52-e6fb-440a-9f07-ad9579d12f5d');
INSERT INTO public.role_nodes VALUES ('f27eced8-15e2-43bb-b551-1d674209aa76', 'Banking Upgrades (Wealth Management)', NULL, 'd457d841-d420-4fcd-ae9b-24eb0ee84d14', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('52ebe4ec-11b8-49be-95a2-060f77d324e9', 'Stage 21: Late Teen / Young Adult (16-21 years)', NULL, 'd08fa328-fa99-4e24-904a-3d6bf72b8abd', '2025-03-16 00:56:36.577842+03', NULL, NULL, '7c8bd800-1a4f-4c1f-a661-d07b7e4c18dd');
INSERT INTO public.role_nodes VALUES ('41f723bb-7152-45cd-b904-8392133a8221', 'High School (Grade 9-12)', NULL, '52ebe4ec-11b8-49be-95a2-060f77d324e9', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('7a66b307-b48e-44ec-9d95-083bc3eb562a', 'College Entrance', NULL, '41f723bb-7152-45cd-b904-8392133a8221', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('6e91a6a2-e314-432e-b1cf-53d427786639', 'Exam Preparations', NULL, '41f723bb-7152-45cd-b904-8392133a8221', '2025-03-16 00:56:36.577842+03', NULL, NULL, '7a66b307-b48e-44ec-9d95-083bc3eb562a');
INSERT INTO public.role_nodes VALUES ('d08527b0-d9e8-4d4a-87d4-e62b280e1b93', 'First Jobs / Internships', NULL, '52ebe4ec-11b8-49be-95a2-060f77d324e9', '2025-03-16 00:56:36.577842+03', NULL, NULL, '41f723bb-7152-45cd-b904-8392133a8221');
INSERT INTO public.role_nodes VALUES ('51dc9c0e-dbf7-4c3c-a643-d7d1caae5014', 'Open Bank Account', NULL, 'd08527b0-d9e8-4d4a-87d4-e62b280e1b93', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('ac161e44-9ed7-4452-9399-3965aac28e2f', 'Early Workplace Experience', NULL, 'd08527b0-d9e8-4d4a-87d4-e62b280e1b93', '2025-03-16 00:56:36.577842+03', NULL, NULL, '51dc9c0e-dbf7-4c3c-a643-d7d1caae5014');
INSERT INTO public.role_nodes VALUES ('f125ac8d-5c81-409a-848b-eeebaba8e5ce', 'Stage 34: Adult (22-34 years)', NULL, 'd08fa328-fa99-4e24-904a-3d6bf72b8abd', '2025-03-16 00:56:36.577842+03', NULL, NULL, '52ebe4ec-11b8-49be-95a2-060f77d324e9');
INSERT INTO public.role_nodes VALUES ('e55df799-e5d3-467c-ab62-e65db6f75a41', 'Career Development', NULL, 'f125ac8d-5c81-409a-848b-eeebaba8e5ce', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('b43bf6a2-f0c0-4bce-a840-9dcc1721ef75', 'Workplace (Company / Startup)', NULL, 'e55df799-e5d3-467c-ab62-e65db6f75a41', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('1503e07d-b266-419e-ae33-9556b5d25198', 'In-House Training Courses', NULL, 'b43bf6a2-f0c0-4bce-a840-9dcc1721ef75', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('286bfb30-3fc2-4f37-8947-7f7dd581737f', 'Job Roles & Promotions', NULL, 'b43bf6a2-f0c0-4bce-a840-9dcc1721ef75', '2025-03-16 00:56:36.577842+03', NULL, NULL, '1503e07d-b266-419e-ae33-9556b5d25198');
INSERT INTO public.role_nodes VALUES ('9bdcd344-79c2-4373-a7ce-e6d6677a65e8', 'Personal Milestones', NULL, 'f125ac8d-5c81-409a-848b-eeebaba8e5ce', '2025-03-16 00:56:36.577842+03', NULL, NULL, 'e55df799-e5d3-467c-ab62-e65db6f75a41');
INSERT INTO public.role_nodes VALUES ('3d2d1d71-aba1-446d-b1d7-6df9e721fbe1', 'Mortgage & Bank Loans', NULL, '9bdcd344-79c2-4373-a7ce-e6d6677a65e8', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('420dc9a0-de9d-4123-b913-51937e55d33d', 'Marriage / Partnership', NULL, '9bdcd344-79c2-4373-a7ce-e6d6677a65e8', '2025-03-16 00:56:36.577842+03', NULL, NULL, '3d2d1d71-aba1-446d-b1d7-6df9e721fbe1');
INSERT INTO public.role_nodes VALUES ('35a78b06-1170-487c-a8f8-ba6c5a41f3e5', 'University / Continuing Education', NULL, 'f125ac8d-5c81-409a-848b-eeebaba8e5ce', '2025-03-16 00:56:36.577842+03', NULL, NULL, '9bdcd344-79c2-4373-a7ce-e6d6677a65e8');
INSERT INTO public.role_nodes VALUES ('61f09399-0c4d-431a-86b9-23c9b951bd72', 'Masters or Specialized Courses', NULL, '35a78b06-1170-487c-a8f8-ba6c5a41f3e5', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('7591eed9-9c86-4ba3-b770-fa0c979c1820', 'Undergraduate Studies', NULL, '35a78b06-1170-487c-a8f8-ba6c5a41f3e5', '2025-03-16 00:56:36.577842+03', NULL, NULL, '61f09399-0c4d-431a-86b9-23c9b951bd72');
INSERT INTO public.role_nodes VALUES ('505fa382-bbe8-4e90-b4c7-6722b5218a92', 'Stage 89: Elderly (55+ years)', NULL, 'd08fa328-fa99-4e24-904a-3d6bf72b8abd', '2025-03-16 00:56:36.577842+03', NULL, NULL, 'f125ac8d-5c81-409a-848b-eeebaba8e5ce');
INSERT INTO public.role_nodes VALUES ('07bdf04e-ede4-463d-b1fe-497ffe98aa00', 'Retirement Planning', NULL, '505fa382-bbe8-4e90-b4c7-6722b5218a92', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('9990dbfc-04af-4c38-8edf-8c971331ef76', 'Elder Care Insurance / Banking', NULL, '07bdf04e-ede4-463d-b1fe-497ffe98aa00', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('790850a9-15a7-4d07-a2f4-5950ba83804b', 'Retirement Accounts / Pensions', NULL, '07bdf04e-ede4-463d-b1fe-497ffe98aa00', '2025-03-16 00:56:36.577842+03', NULL, NULL, '9990dbfc-04af-4c38-8edf-8c971331ef76');
INSERT INTO public.role_nodes VALUES ('c2619f0f-53c8-421c-b327-bf5a730676c7', 'Health & Leisure', NULL, '505fa382-bbe8-4e90-b4c7-6722b5218a92', '2025-03-16 00:56:36.577842+03', NULL, NULL, '07bdf04e-ede4-463d-b1fe-497ffe98aa00');
INSERT INTO public.role_nodes VALUES ('58939e68-16a9-42df-8cd1-fe72fc9b9523', 'Grandparent Role / Family Activities', NULL, 'c2619f0f-53c8-421c-b327-bf5a730676c7', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('2151ea33-9b38-400d-87f2-2702d4f0c27b', 'Senior Community Courses', NULL, 'c2619f0f-53c8-421c-b327-bf5a730676c7', '2025-03-16 00:56:36.577842+03', NULL, NULL, '58939e68-16a9-42df-8cd1-fe72fc9b9523');
INSERT INTO public.role_nodes VALUES ('9bd49a55-7932-461e-9270-3de36cf6a2c7', 'Stage 13: Early Teen (13-15 years)', NULL, 'd08fa328-fa99-4e24-904a-3d6bf72b8abd', '2025-03-16 00:56:36.577842+03', NULL, NULL, '505fa382-bbe8-4e90-b4c7-6722b5218a92');
INSERT INTO public.role_nodes VALUES ('d1499c10-f095-4845-bee7-725eedb49b33', 'Lower Secondary School', NULL, '9bd49a55-7932-461e-9270-3de36cf6a2c7', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('1095a49f-397b-4b31-8d6f-4c7028ad6d3d', 'Grade 7', NULL, 'd1499c10-f095-4845-bee7-725eedb49b33', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('1cf5a143-c0c6-4fb8-9c43-da1482c20232', 'Grade 8', NULL, 'd1499c10-f095-4845-bee7-725eedb49b33', '2025-03-16 00:56:36.577842+03', NULL, NULL, '1095a49f-397b-4b31-8d6f-4c7028ad6d3d');
INSERT INTO public.role_nodes VALUES ('8fb58980-3194-42ac-8641-2280f014a05e', 'Extracurricular Clubs', NULL, '9bd49a55-7932-461e-9270-3de36cf6a2c7', '2025-03-16 00:56:36.577842+03', NULL, NULL, 'd1499c10-f095-4845-bee7-725eedb49b33');
INSERT INTO public.role_nodes VALUES ('691dc37d-901c-49a6-bb71-95555ee4519b', 'Stage 1: Infancy (0-1 year)', 'pnFVN8tU1mus', 'd08fa328-fa99-4e24-904a-3d6bf72b8abd', '2025-03-16 00:56:36.577842+03', NULL, NULL, '9bd49a55-7932-461e-9270-3de36cf6a2c7');
INSERT INTO public.role_nodes VALUES ('5da57d7f-73da-4052-ab30-e3337a2879cd', 'Stage 1: Toddler (1-3 years)', NULL, '691dc37d-901c-49a6-bb71-95555ee4519b', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('0a38da09-bddd-4d83-a987-a2dc904e3e34', 'Stage 2: Early Childhood (3-5 years)', NULL, '5da57d7f-73da-4052-ab30-e3337a2879cd', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('1ade4913-f97c-4009-bc46-fad8c00af79b', 'Stage 3: Preschool (5-6 years)', NULL, '0a38da09-bddd-4d83-a987-a2dc904e3e34', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('b32d85fb-76c4-4188-b8b6-41df9822f325', 'Playgroup Activities', NULL, '1ade4913-f97c-4009-bc46-fad8c00af79b', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('71e97992-51b9-477d-a04f-76839d980a84', 'Pre-Kindergarten', NULL, '1ade4913-f97c-4009-bc46-fad8c00af79b', '2025-03-16 00:56:36.577842+03', NULL, NULL, 'b32d85fb-76c4-4188-b8b6-41df9822f325');
INSERT INTO public.role_nodes VALUES ('4b8a3292-1ca9-4028-83ff-f915b3bdc2ba', 'Stage 8: Age ~8-12 (Middle Primary)', NULL, 'd08fa328-fa99-4e24-904a-3d6bf72b8abd', '2025-03-16 00:56:36.577842+03', NULL, NULL, '691dc37d-901c-49a6-bb71-95555ee4519b');
INSERT INTO public.role_nodes VALUES ('1ae04628-b019-4f99-940e-7d0ffc335f0a', 'Grades 3-4', NULL, '4b8a3292-1ca9-4028-83ff-f915b3bdc2ba', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('300a6b15-8d45-4173-885e-762e68c7d73a', 'Basic Science', NULL, '1ae04628-b019-4f99-940e-7d0ffc335f0a', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('eb3a0ed6-9f01-42d5-95e7-f30ecc3dd4e3', 'Reading Comprehension', NULL, '1ae04628-b019-4f99-940e-7d0ffc335f0a', '2025-03-16 00:56:36.577842+03', NULL, NULL, '300a6b15-8d45-4173-885e-762e68c7d73a');
INSERT INTO public.role_nodes VALUES ('2dc95f67-ca2b-4352-bd17-1d1c096e9980', 'Grades 5-6', NULL, '4b8a3292-1ca9-4028-83ff-f915b3bdc2ba', '2025-03-16 00:56:36.577842+03', NULL, NULL, '1ae04628-b019-4f99-940e-7d0ffc335f0a');
INSERT INTO public.role_nodes VALUES ('f6f66126-836d-4772-a45f-8867378e911c', 'Social Studies', NULL, '2dc95f67-ca2b-4352-bd17-1d1c096e9980', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('54ecf187-50da-460c-86e0-673547737814', 'Intro to Geography', NULL, '2dc95f67-ca2b-4352-bd17-1d1c096e9980', '2025-03-16 00:56:36.577842+03', NULL, NULL, 'f6f66126-836d-4772-a45f-8867378e911c');
INSERT INTO public.role_nodes VALUES ('cc567551-cd18-4af3-bc1a-f2f11941f407', 'Stage 5: Age ~5-7 (Kindergarten & Early Primary)', NULL, 'd08fa328-fa99-4e24-904a-3d6bf72b8abd', '2025-03-16 00:56:36.577842+03', NULL, NULL, '4b8a3292-1ca9-4028-83ff-f915b3bdc2ba');
INSERT INTO public.role_nodes VALUES ('9d03d59b-ca73-4d45-a312-50a6fb47b244', 'Kindergarten', NULL, 'cc567551-cd18-4af3-bc1a-f2f11941f407', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('2716fe9c-88c4-4832-989f-e4ba9e0fd72f', 'Class K2', NULL, '9d03d59b-ca73-4d45-a312-50a6fb47b244', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('2a4117eb-25b8-46e0-8192-0c2a065ba730', 'Class K1', NULL, '9d03d59b-ca73-4d45-a312-50a6fb47b244', '2025-03-16 00:56:36.577842+03', NULL, NULL, '2716fe9c-88c4-4832-989f-e4ba9e0fd72f');
INSERT INTO public.role_nodes VALUES ('ba1152c1-4ed5-4e9c-b3cd-e16aea5b0c0a', 'Primary School Basics (up to Grade 2)', NULL, 'cc567551-cd18-4af3-bc1a-f2f11941f407', '2025-03-16 00:56:36.577842+03', NULL, NULL, '9d03d59b-ca73-4d45-a312-50a6fb47b244');
INSERT INTO public.role_nodes VALUES ('8f4f107b-4d0f-483f-8632-f85105dcc45d', 'Reading & Alphabet', NULL, 'ba1152c1-4ed5-4e9c-b3cd-e16aea5b0c0a', '2025-03-16 00:56:36.577842+03', NULL, NULL, NULL);
INSERT INTO public.role_nodes VALUES ('717446a3-cf62-4e79-83ff-eff49031f5fd', 'Math Foundations', NULL, 'ba1152c1-4ed5-4e9c-b3cd-e16aea5b0c0a', '2025-03-16 00:56:36.577842+03', NULL, NULL, '8f4f107b-4d0f-483f-8632-f85105dcc45d');
INSERT INTO public.role_nodes VALUES ('3721e870-faaf-4329-bcc9-81c5b41bd2a2', 'Second', NULL, NULL, '2025-03-16 00:56:36.577842+03', NULL, NULL, 'd08fa328-fa99-4e24-904a-3d6bf72b8abd');
INSERT INTO public.role_nodes VALUES ('5034e1ff-1003-4eb8-b59d-96d507855e69', 'Root', 'eZxt6FKmhZus', NULL, '2025-03-11 15:53:23.428636+03', NULL, '87bb2118-7fbf-4cd4-8db4-f2fd4f6eeea0', NULL);
INSERT INTO public.role_nodes VALUES ('ba5d920f-a29e-442f-bda3-868b50945304', 'Test', NULL, '5034e1ff-1003-4eb8-b59d-96d507855e69', '2025-03-11 15:53:23.428636+03', NULL, '87bb2118-7fbf-4cd4-8db4-f2fd4f6eeea0', NULL);


--
-- TOC entry 5015 (class 0 OID 49385)
-- Dependencies: 220
-- Data for Name: telegram_users; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5022 (class 0 OID 49581)
-- Dependencies: 227
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.user_roles VALUES (1, '8070e1a5-1a73-412a-9560-6fa08500f857', 'admin', '2025-02-20 13:08:40.405025', '2025-02-20 13:08:40.405025');


--
-- TOC entry 5013 (class 0 OID 49363)
-- Dependencies: 218
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users VALUES ('5ef2163e-8827-4c68-b0f4-9f9bdc724af4', '', '', '', '', '', '', '', '', 'WiUhBkJ4ww8', NULL, NULL, '2025-02-19 04:27:18.879727', NULL);
INSERT INTO public.users VALUES ('51235cb3-e1c4-4aa2-a1f5-569df2fe25ec', '', '', '', '', '', '', '', '', 'TYKXY2iziQA', NULL, NULL, '2025-02-19 04:27:18.879727', NULL);
INSERT INTO public.users VALUES ('e8b6abbe-94ad-4bc3-8a66-fc5e66043286', '', '', '', '', '', '', '', '', 'N-yjXy9sBYA', NULL, NULL, '2025-02-19 04:27:18.879727', NULL);
INSERT INTO public.users VALUES ('678e0d91-57cc-46a2-aa6f-938a3c5ec1dc', '', '', '', '', '', '', '', '', 'K_LZcC9dYHU', '8070e1a5-1a73-412a-9560-6fa08500f857', NULL, '2025-02-19 04:27:18.879727', NULL);
INSERT INTO public.users VALUES ('d83c4d79-8149-44a9-80dd-3e62a696b759', 'j', 'j', 'j', 'j', '1988-04-28', 'k', 'k', 'k', 'GU0DihYkbNk', '8070e1a5-1a73-412a-9560-6fa08500f857', NULL, '2025-02-19 04:27:18.879727', NULL);
INSERT INTO public.users VALUES ('0e21ea31-f70f-41ff-b8d7-37a759753ee8', 'x', 'x', 'x', 'x', '1988-04-28', 'x', 'xx', 'x', 'N_DMV9-bB84', '8070e1a5-1a73-412a-9560-6fa08500f857', NULL, '2025-02-19 04:27:18.879727', NULL);
INSERT INTO public.users VALUES ('df043034-4604-48b0-ba80-f055f04f9fe3', '', '', NULL, '', '', '', '', '', 'j6JIgXL4OBI', NULL, NULL, '2025-02-27 23:33:07.851477', NULL);
INSERT INTO public.users VALUES ('28f65606-645c-4f3e-bbf4-f0eea632ec14', '', '', NULL, '', '', '', '', '', 'xBsmrtiPwDc', NULL, NULL, '2025-02-27 23:34:06.192737', NULL);
INSERT INTO public.users VALUES ('8070e1a5-1a73-412a-9560-6fa08500f857', 'Stanislav', 'Israel', 'CTO', 'Viete', '1988-04-28', 'Traction', 'Master degree in Computer Science', NULL, 'mx6KtWgEvJ0', NULL, '/avatars/8070e1a5-1a73-412a-9560-6fa08500f857.jpg', '2025-02-19 04:27:18.879727', NULL);


--
-- TOC entry 5030 (class 0 OID 50448)
-- Dependencies: 235
-- Data for Name: waiting_list; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5039 (class 0 OID 0)
-- Dependencies: 229
-- Name: admin_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admin_settings_id_seq', 1, true);


--
-- TOC entry 5040 (class 0 OID 0)
-- Dependencies: 226
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 1, true);


--
-- TOC entry 4823 (class 2606 OID 49735)
-- Name: admin_settings admin_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_settings
    ADD CONSTRAINT admin_settings_pkey PRIMARY KEY (id);


--
-- TOC entry 4784 (class 2606 OID 49355)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4791 (class 2606 OID 49379)
-- Name: auth_users auth_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_users
    ADD CONSTRAINT auth_users_pkey PRIMARY KEY (id);


--
-- TOC entry 4843 (class 2606 OID 50036)
-- Name: credits credits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_pkey PRIMARY KEY (id);


--
-- TOC entry 4804 (class 2606 OID 49464)
-- Name: email_users email_users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_users
    ADD CONSTRAINT email_users_email_key UNIQUE (email);


--
-- TOC entry 4806 (class 2606 OID 49462)
-- Name: email_users email_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_users
    ADD CONSTRAINT email_users_pkey PRIMARY KEY (auth_id);


--
-- TOC entry 4827 (class 2606 OID 49959)
-- Name: fillout_data fillout_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fillout_data
    ADD CONSTRAINT fillout_data_pkey PRIMARY KEY (id);


--
-- TOC entry 4813 (class 2606 OID 49572)
-- Name: fillout_submissions fillout_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fillout_submissions
    ADD CONSTRAINT fillout_submissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4798 (class 2606 OID 49447)
-- Name: google_users google_users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.google_users
    ADD CONSTRAINT google_users_email_key UNIQUE (email);


--
-- TOC entry 4800 (class 2606 OID 49445)
-- Name: google_users google_users_google_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.google_users
    ADD CONSTRAINT google_users_google_id_key UNIQUE (google_id);


--
-- TOC entry 4802 (class 2606 OID 49443)
-- Name: google_users google_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.google_users
    ADD CONSTRAINT google_users_pkey PRIMARY KEY (auth_id);


--
-- TOC entry 4796 (class 2606 OID 49431)
-- Name: invitations invitations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invitations
    ADD CONSTRAINT invitations_pkey PRIMARY KEY (id);


--
-- TOC entry 4821 (class 2606 OID 49718)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 4839 (class 2606 OID 49992)
-- Name: project_members project_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_members
    ADD CONSTRAINT project_members_pkey PRIMARY KEY (id);


--
-- TOC entry 4835 (class 2606 OID 49978)
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- TOC entry 4811 (class 2606 OID 49552)
-- Name: role_nodes role_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_nodes
    ADD CONSTRAINT role_nodes_pkey PRIMARY KEY (id);


--
-- TOC entry 4794 (class 2606 OID 49389)
-- Name: telegram_users telegram_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_pkey PRIMARY KEY (auth_id);


--
-- TOC entry 4832 (class 2606 OID 49961)
-- Name: fillout_data uq_fillout_data_user_form; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fillout_data
    ADD CONSTRAINT uq_fillout_data_user_form UNIQUE (user_id, form_id);


--
-- TOC entry 4841 (class 2606 OID 49994)
-- Name: project_members uq_project_members_project_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_members
    ADD CONSTRAINT uq_project_members_project_user UNIQUE (project_id, user_id);


--
-- TOC entry 4816 (class 2606 OID 49591)
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- TOC entry 4787 (class 2606 OID 49370)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (uuid);


--
-- TOC entry 4789 (class 2606 OID 49417)
-- Name: users users_referral_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_referral_code_key UNIQUE (referral_code);


--
-- TOC entry 4848 (class 2606 OID 50457)
-- Name: waiting_list waiting_list_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waiting_list
    ADD CONSTRAINT waiting_list_pkey PRIMARY KEY (id);


--
-- TOC entry 4807 (class 1259 OID 50470)
-- Name: idx_role_nodes_previous_sibling_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_role_nodes_previous_sibling_id ON public.role_nodes USING btree (previous_sibling_id);


--
-- TOC entry 4845 (class 1259 OID 50464)
-- Name: idx_waiting_list_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_waiting_list_status ON public.waiting_list USING btree (status);


--
-- TOC entry 4846 (class 1259 OID 50463)
-- Name: idx_waiting_list_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_waiting_list_user_id ON public.waiting_list USING btree (user_id);


--
-- TOC entry 4824 (class 1259 OID 49736)
-- Name: ix_admin_settings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_admin_settings_id ON public.admin_settings USING btree (id);


--
-- TOC entry 4825 (class 1259 OID 49737)
-- Name: ix_admin_settings_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_admin_settings_key ON public.admin_settings USING btree (key);


--
-- TOC entry 4844 (class 1259 OID 50042)
-- Name: ix_credits_user_uuid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_credits_user_uuid ON public.credits USING btree (user_uuid);


--
-- TOC entry 4828 (class 1259 OID 49968)
-- Name: ix_fillout_data_form_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fillout_data_form_id ON public.fillout_data USING btree (form_id);


--
-- TOC entry 4829 (class 1259 OID 50012)
-- Name: ix_fillout_data_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fillout_data_project_id ON public.fillout_data USING btree (project_id);


--
-- TOC entry 4830 (class 1259 OID 49967)
-- Name: ix_fillout_data_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fillout_data_user_id ON public.fillout_data USING btree (user_id);


--
-- TOC entry 4814 (class 1259 OID 49578)
-- Name: ix_fillout_submissions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fillout_submissions_user_id ON public.fillout_submissions USING btree (user_id);


--
-- TOC entry 4818 (class 1259 OID 49724)
-- Name: ix_payments_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_email ON public.payments USING btree (email);


--
-- TOC entry 4819 (class 1259 OID 49725)
-- Name: ix_payments_payment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_payments_payment_id ON public.payments USING btree (payment_id);


--
-- TOC entry 4836 (class 1259 OID 50005)
-- Name: ix_project_members_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_members_project_id ON public.project_members USING btree (project_id);


--
-- TOC entry 4837 (class 1259 OID 50006)
-- Name: ix_project_members_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_members_user_id ON public.project_members USING btree (user_id);


--
-- TOC entry 4833 (class 1259 OID 49984)
-- Name: ix_projects_owner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_owner_id ON public.projects USING btree (owner_id);


--
-- TOC entry 4808 (class 1259 OID 49558)
-- Name: ix_role_nodes_parent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_role_nodes_parent_id ON public.role_nodes USING btree (parent_id);


--
-- TOC entry 4809 (class 1259 OID 50018)
-- Name: ix_role_nodes_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_role_nodes_project_id ON public.role_nodes USING btree (project_id);


--
-- TOC entry 4792 (class 1259 OID 49395)
-- Name: ix_telegram_users_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_telegram_users_telegram_id ON public.telegram_users USING btree (telegram_id);


--
-- TOC entry 4785 (class 1259 OID 49371)
-- Name: ix_users_uuid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_uuid ON public.users USING btree (uuid);


--
-- TOC entry 4817 (class 1259 OID 49597)
-- Name: user_roles_user_id_role_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX user_roles_user_id_role_idx ON public.user_roles USING btree (user_id, role);


--
-- TOC entry 4850 (class 2606 OID 49380)
-- Name: auth_users auth_users_user_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_users
    ADD CONSTRAINT auth_users_user_uuid_fkey FOREIGN KEY (user_uuid) REFERENCES public.users(uuid) ON DELETE CASCADE;


--
-- TOC entry 4854 (class 2606 OID 49465)
-- Name: email_users email_users_auth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_users
    ADD CONSTRAINT email_users_auth_id_fkey FOREIGN KEY (auth_id) REFERENCES public.auth_users(id) ON DELETE CASCADE;


--
-- TOC entry 4862 (class 2606 OID 49962)
-- Name: fillout_data fillout_data_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fillout_data
    ADD CONSTRAINT fillout_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(uuid);


--
-- TOC entry 4858 (class 2606 OID 49573)
-- Name: fillout_submissions fillout_submissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fillout_submissions
    ADD CONSTRAINT fillout_submissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(uuid);


--
-- TOC entry 4867 (class 2606 OID 50037)
-- Name: credits fk_credits_user_uuid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT fk_credits_user_uuid FOREIGN KEY (user_uuid) REFERENCES public.users(uuid) ON DELETE CASCADE;


--
-- TOC entry 4863 (class 2606 OID 50007)
-- Name: fillout_data fk_fillout_data_project_id_projects; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fillout_data
    ADD CONSTRAINT fk_fillout_data_project_id_projects FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 4859 (class 2606 OID 50019)
-- Name: fillout_submissions fk_fillout_submissions_project_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fillout_submissions
    ADD CONSTRAINT fk_fillout_submissions_project_id FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 4865 (class 2606 OID 49995)
-- Name: project_members fk_project_members_project_id_projects; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_members
    ADD CONSTRAINT fk_project_members_project_id_projects FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 4866 (class 2606 OID 50000)
-- Name: project_members fk_project_members_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_members
    ADD CONSTRAINT fk_project_members_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(uuid) ON DELETE CASCADE;


--
-- TOC entry 4864 (class 2606 OID 49979)
-- Name: projects fk_projects_owner_id_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT fk_projects_owner_id_users FOREIGN KEY (owner_id) REFERENCES public.users(uuid);


--
-- TOC entry 4855 (class 2606 OID 50465)
-- Name: role_nodes fk_role_nodes_previous_sibling; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_nodes
    ADD CONSTRAINT fk_role_nodes_previous_sibling FOREIGN KEY (previous_sibling_id) REFERENCES public.role_nodes(id) ON DELETE SET NULL;


--
-- TOC entry 4856 (class 2606 OID 50013)
-- Name: role_nodes fk_role_nodes_project_id_projects; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_nodes
    ADD CONSTRAINT fk_role_nodes_project_id_projects FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 4849 (class 2606 OID 49418)
-- Name: users fk_users_referral; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_referral FOREIGN KEY (referral_id) REFERENCES public.users(uuid) ON DELETE SET NULL;


--
-- TOC entry 4853 (class 2606 OID 49448)
-- Name: google_users google_users_auth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.google_users
    ADD CONSTRAINT google_users_auth_id_fkey FOREIGN KEY (auth_id) REFERENCES public.auth_users(id) ON DELETE CASCADE;


--
-- TOC entry 4852 (class 2606 OID 49432)
-- Name: invitations invitations_referral_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invitations
    ADD CONSTRAINT invitations_referral_fkey FOREIGN KEY (referral) REFERENCES public.users(uuid);


--
-- TOC entry 4861 (class 2606 OID 49719)
-- Name: payments payments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(uuid) ON DELETE SET NULL;


--
-- TOC entry 4857 (class 2606 OID 49553)
-- Name: role_nodes role_nodes_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_nodes
    ADD CONSTRAINT role_nodes_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.role_nodes(id) ON DELETE CASCADE;


--
-- TOC entry 4851 (class 2606 OID 49390)
-- Name: telegram_users telegram_users_auth_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_auth_id_fkey FOREIGN KEY (auth_id) REFERENCES public.auth_users(id) ON DELETE CASCADE;


--
-- TOC entry 4860 (class 2606 OID 49592)
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(uuid);


--
-- TOC entry 4868 (class 2606 OID 50458)
-- Name: waiting_list waiting_list_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waiting_list
    ADD CONSTRAINT waiting_list_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(uuid) ON DELETE CASCADE;


-- Completed on 2025-03-24 20:18:57

--
-- PostgreSQL database dump complete
--

