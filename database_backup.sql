--
-- PostgreSQL database dump
--

\restrict UNedNNbMeDneEmL2lqXZqToHl8PO7FcaXXH5NTTtjfZPeOFNTvCISQbQZ6eh2cv

-- Dumped from database version 15.17
-- Dumped by pg_dump version 15.17

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
-- Name: assessment_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.assessment_type AS ENUM (
    'homework',
    'quiz',
    'midterm',
    'final',
    'project',
    'lab',
    'presentation',
    'other'
);


--
-- Name: enrollmentstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.enrollmentstatus AS ENUM (
    'PASSED',
    'IN_PROGRESS',
    'WITHDRAWN',
    'FAILED',
    'AUDIT',
    'INCOMPLETE'
);


--
-- Name: materialcurationstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.materialcurationstatus AS ENUM (
    'PENDING',
    'PUBLISHED',
    'REJECTED',
    'NOT_REQUESTED'
);


--
-- Name: materialuploadstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.materialuploadstatus AS ENUM (
    'QUEUED',
    'UPLOADING',
    'COMPLETED',
    'FAILED'
);


--
-- Name: recurrence_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.recurrence_type AS ENUM (
    'none',
    'daily',
    'weekly',
    'biweekly',
    'monthly'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: assessments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.assessments (
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    assessment_type public.assessment_type NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    deadline timestamp with time zone NOT NULL,
    weight double precision,
    score double precision,
    max_score double precision,
    is_completed boolean NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.assessments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.assessments_id_seq OWNED BY public.assessments.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    color character varying(7) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: course_gpa_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_gpa_stats (
    course_id integer NOT NULL,
    term character varying(16) NOT NULL,
    year integer NOT NULL,
    section character varying(16),
    avg_gpa double precision,
    total_enrolled integer,
    grade_distribution json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: course_gpa_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_gpa_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_gpa_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_gpa_stats_id_seq OWNED BY public.course_gpa_stats.id;


--
-- Name: course_offerings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_offerings (
    course_id integer NOT NULL,
    term character varying(16) NOT NULL,
    year integer NOT NULL,
    section character varying(16),
    start_date date,
    end_date date,
    days character varying(64),
    meeting_time character varying(64),
    enrolled integer,
    capacity integer,
    faculty text,
    room character varying(128),
    id integer NOT NULL
);


--
-- Name: course_offerings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_offerings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_offerings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_offerings_id_seq OWNED BY public.course_offerings.id;


--
-- Name: course_reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.course_reviews (
    course_id integer NOT NULL,
    user_id integer NOT NULL,
    comment text,
    overall_rating integer NOT NULL,
    difficulty integer,
    informativeness integer,
    gpa_boost integer,
    workload integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_review_difficulty CHECK (((difficulty IS NULL) OR ((difficulty >= 1) AND (difficulty <= 5)))),
    CONSTRAINT ck_review_gpa_boost CHECK (((gpa_boost IS NULL) OR ((gpa_boost >= 1) AND (gpa_boost <= 5)))),
    CONSTRAINT ck_review_informativeness CHECK (((informativeness IS NULL) OR ((informativeness >= 1) AND (informativeness <= 5)))),
    CONSTRAINT ck_review_overall_rating CHECK (((overall_rating >= 1) AND (overall_rating <= 5))),
    CONSTRAINT ck_review_workload CHECK (((workload IS NULL) OR ((workload >= 1) AND (workload <= 5))))
);


--
-- Name: course_reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.course_reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: course_reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.course_reviews_id_seq OWNED BY public.course_reviews.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.courses (
    code character varying(16) NOT NULL,
    level character varying(16) NOT NULL,
    title character varying(256) NOT NULL,
    department character varying(64),
    ects integer NOT NULL,
    description text,
    pass_grade character varying,
    school character varying(32),
    academic_level character varying(16),
    credits_us double precision,
    prerequisites text,
    corequisites text,
    antirequisites text,
    priority_1 text,
    priority_2 text,
    priority_3 text,
    priority_4 text,
    requirements_term character varying(16),
    requirements_year integer,
    id integer NOT NULL
);


--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: enrollments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enrollments (
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    term character varying(16) NOT NULL,
    year integer NOT NULL,
    grade character varying(4),
    grade_points double precision,
    status public.enrollmentstatus NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.events (
    user_id integer NOT NULL,
    category_id integer,
    title character varying(255) NOT NULL,
    description text,
    start_at timestamp with time zone NOT NULL,
    end_at timestamp with time zone,
    is_all_day boolean NOT NULL,
    location character varying(255),
    recurrence public.recurrence_type NOT NULL,
    recurrence_end_at timestamp with time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- Name: study_material_library_entries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.study_material_library_entries (
    upload_id integer NOT NULL,
    course_id integer NOT NULL,
    curated_title character varying(255) NOT NULL,
    curated_week integer NOT NULL,
    curated_by_admin_id integer NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: study_material_library_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.study_material_library_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: study_material_library_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.study_material_library_entries_id_seq OWNED BY public.study_material_library_entries.id;


--
-- Name: study_material_uploads; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.study_material_uploads (
    course_id integer NOT NULL,
    uploader_id integer NOT NULL,
    user_week integer NOT NULL,
    original_filename character varying(255) NOT NULL,
    staged_path character varying(512),
    storage_key character varying(512) NOT NULL,
    content_type character varying(128) NOT NULL,
    file_size_bytes integer NOT NULL,
    upload_status public.materialuploadstatus NOT NULL,
    curation_status public.materialcurationstatus NOT NULL,
    error_message text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: study_material_uploads_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.study_material_uploads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: study_material_uploads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.study_material_uploads_id_seq OWNED BY public.study_material_uploads.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    email character varying(255) NOT NULL,
    google_id character varying(255) NOT NULL,
    first_name character varying(64) NOT NULL,
    last_name character varying(64) NOT NULL,
    major character varying(64),
    study_year integer,
    cgpa double precision,
    total_credits_earned integer,
    total_credits_enrolled integer,
    avatar_url character varying,
    is_onboarded boolean NOT NULL,
    is_admin boolean NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: assessments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessments ALTER COLUMN id SET DEFAULT nextval('public.assessments_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: course_gpa_stats id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_gpa_stats ALTER COLUMN id SET DEFAULT nextval('public.course_gpa_stats_id_seq'::regclass);


--
-- Name: course_offerings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_offerings ALTER COLUMN id SET DEFAULT nextval('public.course_offerings_id_seq'::regclass);


--
-- Name: course_reviews id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_reviews ALTER COLUMN id SET DEFAULT nextval('public.course_reviews_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- Name: study_material_library_entries id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_library_entries ALTER COLUMN id SET DEFAULT nextval('public.study_material_library_entries_id_seq'::regclass);


--
-- Name: study_material_uploads id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_uploads ALTER COLUMN id SET DEFAULT nextval('public.study_material_uploads_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
20260414_0003
\.


--
-- Data for Name: assessments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.assessments (user_id, course_id, assessment_type, title, description, deadline, weight, score, max_score, is_completed, id, created_at, updated_at) FROM stdin;
1	265	midterm	midterm 1	\N	2026-04-19 08:50:00+00	30	\N	100	f	4	2026-04-18 13:33:54.92183+00	2026-04-18 13:55:46.441418+00
1	265	lab	lab 1	\N	2026-04-18 09:00:00+00	5	0	\N	t	5	2026-04-18 13:50:46.246753+00	2026-04-18 14:16:56.960305+00
1	924	midterm	Midterm 1	\N	2026-04-18 04:00:00+00	30	65	70	t	6	2026-04-18 13:56:21.281866+00	2026-04-18 14:21:26.40392+00
1	924	homework	HW 1	\N	2026-04-20 17:59:00+00	10	\N	\N	f	7	2026-04-18 14:21:49.050127+00	2026-04-18 14:25:52.900236+00
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categories (user_id, name, color, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: course_gpa_stats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_gpa_stats (course_id, term, year, section, avg_gpa, total_enrolled, grade_distribution, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: course_offerings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_offerings (course_id, term, year, section, start_date, end_date, days, meeting_time, enrolled, capacity, faculty, room, id) FROM stdin;
1	Fall	2022	\N	\N	\N	\N	\N	\N	\N	\N	\N	1
2	Fall	2022	\N	\N	\N	\N	\N	\N	\N	\N	\N	2
3	Fall	2022	\N	\N	\N	\N	\N	\N	\N	\N	\N	3
4	Fall	2022	\N	\N	\N	\N	\N	\N	\N	\N	\N	4
5	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	5
6	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	6
7	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	7
8	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	8
9	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	9
10	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	10
11	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	11
12	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	12
13	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	13
14	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	14
15	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	15
16	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	16
17	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	17
18	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	18
19	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	19
20	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	20
21	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	21
22	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	22
23	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	23
24	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	24
25	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	25
26	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	26
27	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	27
28	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	28
29	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	29
30	Summer	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	30
31	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	31
32	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	32
33	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	33
34	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	34
35	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	35
36	Spring	2026	1L	2026-01-12	2026-04-24	T	02:00 PM-05:00 PM	50	50	Mirat Akshalov,\nChristian\nSofilkanitsch	(C3) 1009 -\ncap:70	36
36	Spring	2026	2L	2026-01-12	2026-04-24	R	02:00 PM-05:00 PM	30	23	Mirat Akshalov,\nChristian\nSofilkanitsch	(C3) 3017 -\ncap:38	37
37	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	107	75	Russell Zanca	Green Hall -\ncap:231	38
38	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	142	150	Alima Bissenova	Green Hall -\ncap:231	39
39	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	87	100	Abay Namen	5.103 -\ncap:160	40
40	Spring	2026	1S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	27	27	Karina\nMatkarimova	8.310 -\ncap:27	41
40	Spring	2026	2S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	27	27	Philipp\nSchroeder	8.154 -\ncap:56	42
41	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	25	25	Russell Zanca	8.310 -\ncap:27	43
42	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	25	25	Katherine\nErdman	8.422A -\ncap:32	44
43	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	25	25	Paula Dupuy	8.321 -\ncap:32	45
44	Spring	2026	1L	2026-01-12	2026-04-24	F	09:00 AM-11:50 AM	24	25	Ulan Bigozhin	8.154 -\ncap:56	46
45	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	18	25	Paula Dupuy	8.321 -\ncap:32	47
46	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	24	25	Snezhana\nAtanova	8.154 -\ncap:56	48
47	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-03:50 PM	19	25	Snezhana\nAtanova	8.422A -\ncap:32	49
48	Spring	2026	1L	2026-01-12	2026-04-24	W	01:00 PM-03:50 PM	12	16	Reed Coil	8.147 -\ncap:15	50
49	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	20	25	Matvey\nLomonosov	8.310 -\ncap:27	51
50	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Paula Dupuy	\N	52
50	Spring	2026	3Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Abay Namen	\N	53
50	Spring	2026	4Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Philipp\nSchroeder	\N	54
51	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Paula Dupuy	\N	55
52	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	26	26	Philipp\nSchroeder	8.154 -\ncap:56	56
52	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	26	26	Philipp\nSchroeder	8.154 -\ncap:56	57
53	Spring	2026	1S	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	2	25	Dana\nBurkhanova	8.154 -\ncap:56	58
54	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:30 AM-10:20 AM	1	1	Mirat Akshalov	(C3) 3038 -\ncap:39	59
55	Spring	2026	1L	2026-01-12	2026-04-24	M	02:00 PM-05:00 PM	7	7	Mirat Akshalov,\nDavid Reinhard	(C3) 1009 -\ncap:70	60
56	Spring	2026	1L	2026-01-12	2026-04-24	W	02:00 PM-05:00 PM	9	7	Mirat Akshalov,\nRoza\nNurgozhayeva	(C3) 1009 -\ncap:70	61
57	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	1	1	Mirat Akshalov	(C3) 3038 -\ncap:39	62
58	Spring	2026	1L	2026-01-12	2026-04-24	F	02:00 PM-05:00 PM	7	7	Mirat Akshalov,\nNarendra Singh	(C3) 1009 -\ncap:70	63
23	Spring	2026	3L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	78	90	Nurtilek Galimov	Blue Hall -\ncap:239	64
23	Spring	2026	4L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	86	90	Aigerim\nSoltabayeva	Blue Hall -\ncap:239	65
23	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	81	90	yingqiu Xie	Green Hall -\ncap:231	66
23	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	67	90	Zarina\nSautbayeva	7E.329 -\ncap:95	67
59	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	13	60	Alexandr Pak	7E.529 -\ncap:95	68
59	Spring	2026	2L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	69	70	Olena\nFilchakova	7E.529 -\ncap:95	69
60	Spring	2026	4Lb	2026-01-12	2026-04-24	T	12:00 PM-02:50 PM	15	16	Nurtilek Galimov	9.228 -\ncap:40	70
60	Spring	2026	5Lb	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	16	16	Zarina\nSautbayeva	9.228 -\ncap:40	71
60	Spring	2026	6Lb	2026-01-12	2026-04-24	R	12:00 PM-02:50 PM	17	16	Zarina\nSautbayeva	9.228 -\ncap:40	72
60	Spring	2026	2Lb	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	16	16	Burkitkan Akbay	7.407 -\ncap:20	73
60	Spring	2026	3Lb	2026-01-12	2026-04-24	M	12:00 PM-02:50 PM	17	16	Burkitkan Akbay	7.407 -\ncap:20	74
61	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	17	30	Alexandr Pak	7.105 -\ncap:75	75
62	Spring	2026	1R	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	10	24	Sergey Yegorov	7E.217 -\ncap:24	76
62	Spring	2026	3R	2026-01-12	2026-04-24	M	06:00 PM-06:50 PM	8	24	Sergey Yegorov	7E.217 -\ncap:24	77
62	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	18	72	Sergey Yegorov	8.522 -\ncap:72	78
63	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	50	60	Ivan Vorobyev	7.105 -\ncap:75	79
64	Spring	2026	1Lb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	6	16	Radmir\nSarsenov	7.410 -\ncap:15	80
65	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	26	60	Damira\nKanayeva	7E.529 -\ncap:95	81
66	Spring	2026	2Lb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	16	16	Nurtilek Galimov	7.407 -\ncap:20	82
67	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	48	60	Timo Burster	7.105 -\ncap:75	83
68	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	23	60	Otilia Nuta	7.105 -\ncap:75	84
69	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	21	24	Tursonjan Tokay	8.105 -\ncap:56	85
70	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	32	36	Natalie\nBarteneva	7.105 -\ncap:75	86
71	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	70	70	Timo Burster	7E.529 -\ncap:95	87
72	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	21	24	Otilia Nuta	7.105 -\ncap:75	88
72	Spring	2026	2L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	14	14	yingqiu Xie	7.105 -\ncap:75	89
73	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	23	70	Zhanat\nMuminova	7E.529 -\ncap:95	90
74	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	18	30	Dos Sarbassov	7E.529 -\ncap:95	91
75	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	53	75	Olena\nFilchakova	7E.529 -\ncap:95	92
76	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	33	60	Zhanat\nMuminova	7E.529 -\ncap:95	93
77	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	13	36	Damira\nKanayeva	7E.529 -\ncap:95	94
78	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	5	18	Ivan Vorobyev	7.517 -\ncap:25	95
79	Spring	2026	1Lb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	4	12	Radmir\nSarsenov	9.502 -\ncap:8	96
80	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	6	24	Sergey Yegorov	7.517 -\ncap:25	97
81	Spring	2026	1Wsh	2026-01-12	2026-04-24	\N	Online/Distant	8	18	Olena\nFilchakova	\N	98
82	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	27	27	Dos Sarbassov	\N	99
82	Spring	2026	2P	2026-01-12	2026-04-24	\N	Online/Distant	25	27	Tri Pham	\N	100
83	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	17	25	Tri Pham	7E.529 -\ncap:95	101
84	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	15	16	Ulykbek Kairov	7E.545/1 -\ncap:25	102
85	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	16	16	Ferdinand\nMolnar	\N	103
86	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	14	16	Natalie\nBarteneva	7.517 -\ncap:25	104
87	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	16	20	yingqiu Xie	\N	105
88	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	12	16	Tursonjan Tokay	7E.545/1 -\ncap:25	106
89	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	10	16	Ivan Vorobyev	7.517 -\ncap:25	107
90	Spring	2026	1Lb	2026-01-12	2026-04-24	F	03:00 PM-05:50 PM	7	6	Radmir\nSarsenov	9.502 -\ncap:8	108
91	Spring	2026	1ThDef	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	12	20	Tursonjan Tokay	online -\ncap:0	109
92	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	10	10	Natalie\nBarteneva	\N	110
92	Spring	2026	2R	2026-01-12	2026-04-24	\N	Online/Distant	2	10	Natalie\nBarteneva	\N	111
92	Spring	2026	3R	2026-01-12	2026-04-24	\N	Online/Distant	8	10	Timo Burster	\N	112
92	Spring	2026	4R	2026-01-12	2026-04-24	\N	Online/Distant	8	10	Timo Burster	\N	113
93	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	9	10	Tri Pham	7E.529 -\ncap:95	114
94	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	8	10	Tursonjan Tokay	7E.545/1 -\ncap:25	115
95	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	1	10	Ivan Vorobyev	7.517 -\ncap:25	116
95	Spring	2026	1Lb	2026-01-12	2026-04-24	F	03:00 PM-05:50 PM	1	8	Radmir\nSarsenov	9.502 -\ncap:8	117
96	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	9	10	Ulykbek Kairov	7E.545/1 -\ncap:25	118
96	Spring	2026	1Lb	2026-01-12	2026-04-24	W	06:00 PM-06:50 PM	9	10	Ulykbek Kairov	7E.545/1 -\ncap:25	119
97	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	10	10	Natalie\nBarteneva	7.517 -\ncap:25	120
20	Spring	2026	3R	2026-01-12	2026-04-24	T	11:00 AM-11:50 AM	47	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 2003 -\ncap:67	121
20	Spring	2026	10R	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	47	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 2003 -\ncap:67	122
20	Spring	2026	1R	2026-01-12	2026-04-24	T	09:00 AM-09:50 AM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	124
20	Spring	2026	2R	2026-01-12	2026-04-24	T	10:00 AM-10:50 AM	45	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	125
20	Spring	2026	4R	2026-01-12	2026-04-24	T	11:00 AM-11:50 AM	48	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	126
20	Spring	2026	5R	2026-01-12	2026-04-24	T	12:00 PM-12:50 PM	47	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	127
20	Spring	2026	6R	2026-01-12	2026-04-24	T	01:00 PM-01:50 PM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	128
20	Spring	2026	7R	2026-01-12	2026-04-24	W	09:00 AM-09:50 AM	46	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	129
20	Spring	2026	8R	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	48	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	130
20	Spring	2026	9R	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	131
20	Spring	2026	11R	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	48	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	132
20	Spring	2026	12R	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	133
99	Spring	2026	1T	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	65	70	Mert Guney	3E.223 -\ncap:63	135
99	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	65	70	Mert Guney	3E.224 -\ncap:90	136
99	Spring	2026	1Lb	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	30	35	Mert Guney	3E.120 -\ncap:20	137
99	Spring	2026	2Lb	2026-01-12	2026-04-24	R	12:00 PM-01:15 PM	35	35	Mert Guney	3E.120 -\ncap:20	138
20	Spring	2026	1L	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	572	588	Mirat Akshalov,\nSaniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	Blue Hall -\ncap:239	123
100	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	66	70	Elnara\nKussinova	3E.220 -\ncap:90	139
100	Spring	2026	1T	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	66	70	Elnara\nKussinova	3E.223 -\ncap:63	140
101	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	64	65	Dichuan Zhang	3E.220 -\ncap:90	141
101	Spring	2026	1T	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	64	65	Dichuan Zhang	3E.220 -\ncap:90	142
102	Spring	2026	1Lb	2026-01-12	2026-04-24	W	04:00 PM-05:45 PM	29	27	Sung Moon	3.323 -\ncap:64	143
102	Spring	2026	2Lb	2026-01-12	2026-04-24	M	04:00 PM-05:45 PM	26	28	Sung Moon	3.323 -\ncap:64	144
102	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	55	55	Sung Moon	3E.220 -\ncap:90	145
103	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	52	55	Ferhat Karaca	3E.220 -\ncap:90	146
103	Spring	2026	1T	2026-01-12	2026-04-24	M	03:00 PM-03:50 PM	52	55	Ferhat Karaca	3E.220 -\ncap:90	147
104	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	11	30	Woojin Lee	3.316 -\ncap:41	148
104	Spring	2026	1T	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	11	30	Woojin Lee	3.316 -\ncap:41	149
105	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	54	70	Chang Shon	3E.220 -\ncap:90	150
105	Spring	2026	1P	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	54	70	Chang Shon	3E.220 -\ncap:90	151
106	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	45	40	Alfrendo\nSatyanaga	7E.220 -\ncap:56	152
107	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	42	40	Ferhat Karaca	3.309 -\ncap:40	153
107	Spring	2026	1T	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	42	40	Ferhat Karaca	3.309 -\ncap:40	154
108	Spring	2026	1Lb	2026-01-12	2026-04-24	F	04:00 PM-05:45 PM	43	30	Alfrendo\nSatyanaga	3.323 -\ncap:64	155
108	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	43	30	Alfrendo\nSatyanaga	7E.220 -\ncap:56	156
109	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	15	20	Jong Kim,\nBakhyt\nAubakirova	3.309 -\ncap:40	157
110	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	13	40	Shazim Memon	3.302 -\ncap:76	158
110	Spring	2026	1Lb	2026-01-12	2026-04-24	T	04:30 PM-05:45 PM	13	40	Shazim Memon	3E.136 -\ncap:22	159
111	Spring	2026	1Lb	2026-01-12	2026-04-24	F	04:00 PM-05:45 PM	22	40	Elnara\nKussinova	3.302 -\ncap:76	160
111	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	22	40	Elnara\nKussinova	3.303 -\ncap:32	161
32	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	69	70	Zhannat\nAshikbayeva	5.103 -\ncap:160	163
113	Spring	2026	2L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	47	40	Akmaral\nSuleimenova	7.105 -\ncap:75	164
113	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	38	40	Khalil Amro	7E.222 -\ncap:95	165
113	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	8	40	Akmaral\nSuleimenova	7E.222 -\ncap:95	166
114	Spring	2026	1ChLb	2026-01-12	2026-04-24	M	12:00 PM-02:50 PM	24	24	Aisulu\nZhanbossinova	9.210 -\ncap:40	167
114	Spring	2026	2ChLb	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	12	24	Roza Oztopcu	9.210 -\ncap:40	168
114	Spring	2026	4ChLb	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	19	24	Roza Oztopcu	9.210 -\ncap:40	169
114	Spring	2026	6ChLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	20	24	Aliya Toleuova	9.210 -\ncap:40	170
114	Spring	2026	7ChLb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	20	24	Saule Issayeva	9.210 -\ncap:40	171
114	Spring	2026	9ChLb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	6	24	Akmaral\nSuleimenova	9.210 -\ncap:40	172
114	Spring	2026	10ChLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	7	15	Aisulu\nZhanbossinova	7.307 -\ncap:15	173
115	Spring	2026	7L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	29	32	Ellina Mun	7.246 -\ncap:48	174
115	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	19	32	Aigerim\nGalyamova	7E.221 -\ncap:56	175
115	Spring	2026	3L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	40	32	Aisulu\nZhanbossinova	7E.221 -\ncap:56	176
115	Spring	2026	4L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	19	32	Sandugash\nKalybekkyzy	7E.221 -\ncap:56	177
115	Spring	2026	5L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	33	32	Aliya Toleuova	7E.221 -\ncap:56	178
115	Spring	2026	6L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	31	32	Aliya Toleuova	7E.529 -\ncap:95	179
115	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	27	32	Roza Oztopcu	7E.125/2 -\ncap:56	180
116	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	68	70	Zhannat\nAshikbayeva	5.103 -\ncap:160	181
116	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	70	70	Zhannat\nAshikbayeva	5.103 -\ncap:160	182
116	Spring	2026	3L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	41	40	Saule Issayeva	5.103 -\ncap:160	183
117	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	1	1	Irshad\nKammakakam	\N	184
118	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	5	32	Salimgerey\nAdilov, Ahmed\nElkamhawy	7E.221 -\ncap:56	185
118	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	18	32	Salimgerey\nAdilov, Ahmed\nElkamhawy	7E.221 -\ncap:56	186
119	Spring	2026	1Lb	2026-01-12	2026-04-24	F	09:00 AM-11:50 AM	5	24	Ozgur Oztopcu	7.307 -\ncap:15	187
119	Spring	2026	2Lb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	5	24	Rauan Smail	7.307 -\ncap:15	188
120	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	22	24	Irshad\nKammakakam	7E.221 -\ncap:56	189
120	Spring	2026	2L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	8	32	Davit\nHayrapetyan	7E.221 -\ncap:56	190
120	Spring	2026	3L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	23	24	Irshad\nKammakakam	7E.221 -\ncap:56	191
121	Spring	2026	1ChLb	2026-01-12	2026-04-24	F	03:00 PM-05:50 PM	21	24	Ozgur Oztopcu	7.307 -\ncap:15	192
121	Spring	2026	2ChLb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	13	24	Ozgur Oztopcu	7.307 -\ncap:15	193
121	Spring	2026	4ChLb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	6	24	Rauan Smail	7.307 -\ncap:15	194
122	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	37	40	Timur Atabaev	7.105 -\ncap:75	195
123	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	27	28	Rostislav\nBukasov	7.105 -\ncap:75	196
124	Spring	2026	1ChLb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	24	24	Rostislav\nBukasov	7.310 -\ncap:15	197
125	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	23	24	Haiyan Fan	7E.221 -\ncap:56	198
126	Spring	2026	1ChLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	18	20	Haiyan Fan	7.310 -\ncap:15	199
127	Spring	2026	1ChLb	2026-01-12	2026-04-24	F	03:00 PM-05:50 PM	18	24	Akmaral\nSuleimenova	7.310 -\ncap:15	200
127	Spring	2026	2ChLb	2026-01-12	2026-04-24	M	11:00 AM-01:50 PM	10	24	Akmaral\nSuleimenova	7.310 -\ncap:15	201
128	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	20	24	Andrey\nKhalimon	7E.221 -\ncap:56	202
128	Spring	2026	2L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	9	24	Andrey\nKhalimon	7E.221 -\ncap:56	203
129	Spring	2026	1S	2026-01-12	2026-04-24	\N	Online/Distant	13	24	Salimgerey\nAdilov	\N	204
130	Spring	2026	1L	2026-01-12	2026-04-24	W	06:00 PM-08:50 PM	20	24	Davit\nHayrapetyan	7E.221 -\ncap:56	205
131	Spring	2026	1L	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	4	12	Mannix Balanay	7E.546/1 -\ncap:25	206
132	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	20	30	Vesselin Paunov	7.507 -\ncap:48	207
133	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	21	30	Ellina Mun,\nAhmed\nElkamhawy	7E.125/2 -\ncap:56	208
134	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	16	24	Salimgerey\nAdilov	\N	209
135	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	7	24	Timur Atabaev	9.105 -\ncap:68	210
136	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	8	12	Vesselin Paunov	7.507 -\ncap:48	211
137	Spring	2026	1L	2026-01-12	2026-04-24	W	06:00 PM-08:50 PM	9	12	Davit\nHayrapetyan	7E.221 -\ncap:56	212
138	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	6	12	Ellina Mun,\nAhmed\nElkamhawy	7E.125/2 -\ncap:56	213
139	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	9	12	Ahmed\nElkamhawy	\N	214
140	Spring	2026	1Lb	2026-01-12	2026-04-24	\N	Online/Distant	9	12	Timur Atabaev	\N	215
141	Spring	2026	1S	2026-01-12	2026-04-24	F	06:00 PM-08:50 PM	9	12	Vesselin Paunov	7E.221 -\ncap:56	216
142	Spring	2026	1ThDef	2026-01-12	2026-04-24	\N	Online/Distant	8	12	Ellina Mun	\N	217
143	Spring	2026	1L	2026-01-12	2026-04-24	W	06:00 PM-08:50 PM	5	12	Davit\nHayrapetyan	7E.221 -\ncap:56	218
144	Spring	2026	1L	2026-01-12	2026-04-24	F	03:00 PM-05:50 PM	11	12	Sandugash\nKalybekkyzy,\nIrshad\nKammakakam	7E.221 -\ncap:56	219
145	Spring	2026	1L	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	3	6	Mannix Balanay	7E.546/1 -\ncap:25	220
146	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	9	12	Vesselin Paunov	7.507 -\ncap:48	221
147	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	9	12	Timur Atabaev	9.105 -\ncap:68	222
148	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	10	12	Andrey\nKhalimon	7E.221 -\ncap:56	223
149	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	22	30	Mannix Balanay	\N	224
150	Spring	2026	1Lb	2026-01-12	2026-04-24	W	02:00 PM-03:50 PM	29	35	Yanwei Wang	3.323 -\ncap:64	225
150	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	29	35	Yanwei Wang	3.309 -\ncap:40	226
151	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	31	35	Azhar\nMukasheva	3.316 -\ncap:41	227
151	Spring	2026	1Lb	2026-01-12	2026-04-24	T	12:00 PM-01:45 PM	17	17	Azhar\nMukasheva	3E.418 -\ncap:20	228
151	Spring	2026	2Lb	2026-01-12	2026-04-24	T	02:00 PM-03:25 PM	14	17	Azhar\nMukasheva	3E.418 -\ncap:20	229
152	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:30 PM-04:45 PM	27	30	Stavros\nPoulopoulos,\nSabina\nKhamzina	3E.223 -\ncap:63	230
153	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	26	30	Stavros\nPoulopoulos	3.322 -\ncap:41	231
153	Spring	2026	1CLb	2026-01-12	2026-04-24	R	05:00 PM-06:15 PM	26	30	Stavros\nPoulopoulos,\nSabina\nKhamzina	7E.125/3 -\ncap:54	232
154	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-03:50 PM	8	8	Azhar\nMukasheva	3E.424 -\ncap:15	233
154	Spring	2026	2Lb	2026-01-12	2026-04-24	W	02:00 PM-03:50 PM	8	8	Azhar\nMukasheva	3E.424 -\ncap:15	234
154	Spring	2026	3Lb	2026-01-12	2026-04-24	F	02:00 PM-03:50 PM	8	8	Azhar\nMukasheva	3E.424 -\ncap:15	235
154	Spring	2026	4Lb	2026-01-12	2026-04-24	M	04:00 PM-05:50 PM	0	8	Azhar\nMukasheva	3E.424 -\ncap:15	236
155	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	26	30	Lyazzat\nMukhangaliyeva	\N	237
156	Spring	2026	1L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	47	50	Aishuak Konarov	3E.220 -\ncap:90	238
156	Spring	2026	1Lb	2026-01-12	2026-04-24	W	01:00 PM-02:50 PM	47	50	Aishuak Konarov	3E.422 -\ncap:20	239
157	Spring	2026	1Lb	2026-01-12	2026-04-24	T	10:30 AM-11:45 AM	48	50	Dhawal Shah	3.323 -\ncap:64	240
157	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	48	50	Dhawal Shah	3E.220 -\ncap:90	241
158	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	29	30	Cevat Erisken	3.316 -\ncap:41	242
159	Spring	2026	1Lb	2026-01-12	2026-04-24	M	12:00 PM-01:50 PM	14	45	Sergey Spotar	3.323 -\ncap:64	243
159	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	14	45	Sergey Spotar	3.316 -\ncap:41	244
160	Spring	2026	1L	2026-01-12	2026-04-24	T R	02:30 PM-03:45 PM	22	30	Boris Golman	3.322 -\ncap:41	245
160	Spring	2026	1Lb	2026-01-12	2026-04-24	F	02:00 PM-03:50 PM	22	30	Boris Golman	3E.427 -\ncap:20	246
161	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	01:00 PM-01:50 PM	23	24	Lili Zhang	8.305 -\ncap:30	247
161	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	12:00 PM-12:50 PM	25	24	Lili Zhang	8.305 -\ncap:30	248
162	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	02:00 PM-02:50 PM	12	24	Lili Zhang	8.305 -\ncap:30	249
163	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	32	45	Iliyas Tursynbek	7.522 -\ncap:30	250
163	Spring	2026	2L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	41	45	Talgat\nManglayev	7.522 -\ncap:30	251
163	Spring	2026	3L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	39	40	Irina Dolzhikova	7.522 -\ncap:30	252
164	Spring	2026	1Lb	2026-01-12	2026-04-24	F	01:00 PM-01:50 PM	75	85	Irina Dolzhikova	7E.125/3 -\ncap:54	257
164	Spring	2026	2Lb	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	36	85	Marat Isteleyev	7E.125/3 -\ncap:54	258
164	Spring	2026	3Lb	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	32	85	Adai Shomanov	7E.125/3 -\ncap:54	259
164	Spring	2026	4Lb	2026-01-12	2026-04-24	F	04:00 PM-04:50 PM	21	85	Adai Shomanov	7E.125/3 -\ncap:54	260
3	Spring	2026	1CLb	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	36	56	Asset Berdibek	7.522 -\ncap:30	261
3	Spring	2026	2CLb	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	35	56	Adai Shomanov	7.522 -\ncap:30	262
182	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	34	35	Tansel\nDokeroglu	online -\ncap:0	312
164	Spring	2026	1L	2026-01-12	2026-04-24	T	01:30 PM-02:45 PM	74	85	Minho Lee	7E.429 -\ncap:90	253
3	Spring	2026	3CLb	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	12	56	Asset Berdibek,\nAdai Shomanov	7.522 -\ncap:30	263
7	Spring	2026	1Lb	2026-01-12	2026-04-24	M	09:00 AM-09:50 AM	31	75	Asset Berdibek	7E.125/3 -\ncap:54	269
7	Spring	2026	2Lb	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	73	75	Asset Berdibek	7E.125/3 -\ncap:54	270
7	Spring	2026	3Lb	2026-01-12	2026-04-24	M	11:00 AM-11:50 AM	74	75	Iliyas Tursynbek	7E.125/3 -\ncap:54	271
7	Spring	2026	4Lb	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	71	75	Iliyas Tursynbek	7E.125/3 -\ncap:54	272
165	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	133	120	Askar\nBoranbayev	Green Hall -\ncap:231	273
166	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	132	120	Askar\nBoranbayev	7E.220 -\ncap:56	274
167	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	5	40	Antonio Cerone	7.422 -\ncap:30	281
31	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	37	70	Ben Tyler	\N	282
29	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	84	80	Dimitrios\nZormpas	7E.429 -\ncap:90	285
29	Spring	2026	2L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	132	130	Jurn Gyu Park	7E.429 -\ncap:90	286
29	Spring	2026	3L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	84	80	Latif Zohaib	7E.429 -\ncap:90	287
27	Spring	2026	1L	2026-01-12	2026-04-24	M W	09:00 AM-09:50 AM	77	80	Sain Saginbekov	7E.429 -\ncap:90	288
27	Spring	2026	2L	2026-01-12	2026-04-24	M W	10:00 AM-10:50 AM	129	130	Latif Zohaib	7E.429 -\ncap:90	289
27	Spring	2026	3L	2026-01-12	2026-04-24	M W	09:00 AM-09:50 AM	66	80	Shinnazar\nSeytnazarov	7E.429 -\ncap:90	290
27	Spring	2026	1Lb	2026-01-12	2026-04-24	F	09:00 AM-09:50 AM	57	73	Syed\nMuhammad\nUmair Arif	7E.125/3 -\ncap:54	291
27	Spring	2026	2Lb	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	70	73	Syed\nMuhammad\nUmair Arif	7E.125/3 -\ncap:54	292
27	Spring	2026	3Lb	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	72	73	Marat Isteleyev	7E.125/3 -\ncap:54	293
27	Spring	2026	4Lb	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	73	73	Marat Isteleyev	7E.125/3 -\ncap:54	294
169	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	27	35	Tansel\nDokeroglu	online -\ncap:0	295
30	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	31	70	Ben Tyler	\N	296
170	Spring	2026	1L	2026-01-12	2026-04-24	F	05:00 PM-05:50 PM	234	245	Anh Tu Nguyen,\nEnver Ever	online -\ncap:0	297
171	Spring	2026	1L	2026-01-12	2026-04-24	M W	03:00 PM-03:50 PM	15	32	Talgar Bayan	7.246 -\ncap:48	298
171	Spring	2026	1Lb	2026-01-12	2026-04-24	F	03:00 PM-05:00 PM	11	16	Talgar Bayan	7.522 -\ncap:30	299
171	Spring	2026	2Lb	2026-01-12	2026-04-24	F	01:00 PM-02:50 PM	4	16	Talgar Bayan	7.522 -\ncap:30	300
172	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	12	32	Syed\nMuhammad\nUmair Arif	7.422 -\ncap:30	301
173	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	9	35	Dimitrios\nZormpas	3.407 -\ncap:40	302
174	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	65	50	Siamac Fazli	7E.220 -\ncap:56	303
175	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	2	40	Antonio Cerone	7.422 -\ncap:30	304
176	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	21	40	Siamac Fazli	3E.221 -\ncap:50	305
177	Spring	2026	1Lb	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	32	40	Minho Lee	3.323 -\ncap:64	306
177	Spring	2026	1L	2026-01-12	2026-04-24	M W	11:00 AM-11:50 AM	32	40	Minho Lee	7E.220 -\ncap:56	307
180	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	28	35	Talgat\nManglayev	7.522 -\ncap:30	310
181	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	55	65	Yesdaulet\nIzenov, Jose\nBerengueres	3E.223 -\ncap:63	311
3	Spring	2026	1L	2026-01-12	2026-04-24	T	10:30 AM-11:45 AM	39	84	Hashim Ali	7E.429 -\ncap:90	264
3	Spring	2026	2L	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	44	84	Shinnazar\nSeytnazarov	7E.429 -\ncap:90	265
7	Spring	2026	1L	2026-01-12	2026-04-24	R	10:30 AM-11:45 AM	76	80	Jean Marie\nGuillaume\nGerard de\nNivelle	7E.429 -\ncap:90	266
7	Spring	2026	2L	2026-01-12	2026-04-24	R	12:00 PM-01:15 PM	121	140	Ben Tyler	7E.429 -\ncap:90	267
7	Spring	2026	3L	2026-01-12	2026-04-24	R	10:30 AM-11:45 AM	52	80	Yesdaulet Izenov	7E.429 -\ncap:90	268
14	Spring	2026	1L	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	74	75	Meiram\nMurzabulatov	3E.224 -\ncap:90	275
14	Spring	2026	2L	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	84	110	Adnan Yazici	3E.224 -\ncap:90	276
183	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	1	1	Ben Tyler	\N	313
184	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	37	35	Lisa Chalaguine	7.246 -\ncap:48	314
185	Spring	2026	1Lb	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	21	35	Anh Tu Nguyen	3.323 -\ncap:64	315
185	Spring	2026	1L	2026-01-12	2026-04-24	M W	12:00 PM-12:50 PM	21	35	Anh Tu Nguyen	7E.220 -\ncap:56	316
186	Spring	2026	1L	2026-01-12	2026-04-24	M W	10:30 AM-11:45 AM	36	35	Hari Mohan Rai	7.422 -\ncap:30	317
187	Spring	2026	1L	2026-01-12	2026-04-24	S	02:00 PM-04:45 PM	35	50	Latif Zohaib	7E.429 -\ncap:90	318
189	Spring	2026	1L	2026-01-12	2026-04-24	M W	01:30 PM-02:45 PM	13	12	Almas\nShintemirov	7.322 -\ncap:24	320
190	Spring	2026	1R	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	10	20	Hashim Ali, Hari\nMohan Rai	Orange Hall\n- cap:450	321
191	Spring	2026	1Lb	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	12	6	Anh Tu Nguyen	3.323 -\ncap:64	322
191	Spring	2026	1L	2026-01-12	2026-04-24	M W	12:00 PM-12:50 PM	12	6	Anh Tu Nguyen	7E.220 -\ncap:56	323
192	Spring	2026	1ThDef	2026-01-12	2026-04-24	\N	Online/Distant	0	28	Jong Kim,\nBakhyt\nAubakirova	\N	324
192	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	29	28	Jong Kim,\nBakhyt\nAubakirova	\N	325
193	Spring	2026	1CLb	2026-01-12	2026-04-24	\N	Online/Distant	6	5	Jong Kim,\nBakhyt\nAubakirova	\N	326
194	Spring	2026	1L	2026-01-12	2026-04-24	M W	02:00 PM-03:15 PM	4	5	Dichuan Zhang	3.303 -\ncap:32	327
195	Spring	2026	1L	2026-01-12	2026-04-24	M W	11:00 AM-12:15 PM	4	5	Sung Moon	3.309 -\ncap:40	328
196	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	2	5	Woojin Lee	3.316 -\ncap:41	329
197	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	13	5	Abid Nadeem	3.303 -\ncap:32	330
198	Spring	2026	1Th	2026-01-12	2026-04-24	\N	Online/Distant	0	30	Nurxat Nuraje,\nChang-Keun Lim	\N	331
198	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	24	30	Nurxat Nuraje	\N	332
199	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	10	12	Zhumabay\nBakenov	\N	333
200	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	6	12	Yanwei Wang	3.415 -\ncap:42	334
201	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	10	12	Nurxat Nuraje	3E.221 -\ncap:50	335
202	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	10	12	Sergey Spotar	3.316 -\ncap:41	336
202	Spring	2026	1Lb	2026-01-12	2026-04-24	W	12:00 PM-01:50 PM	10	12	Sergey Spotar	3E.227 -\ncap:28	337
203	Spring	2026	1Th	2026-01-12	2026-04-24	\N	Online/Distant	0	5	Mehdi Bagheri	\N	338
203	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	22	30	Mehdi Bagheri	\N	339
204	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	7	20	Daniele Tosi	3.317 -\ncap:40	340
205	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	7	15	Mehdi Shafiee,\nAzamat\nMukhamediya	3.309 -\ncap:40	341
206	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	0	15	Muhammad\nAkhtar	3.416 -\ncap:46	342
207	Spring	2026	1L	2026-01-12	2026-04-24	M W	01:30 PM-02:45 PM	6	15	Mohammad\nHashmi	3.322 -\ncap:41	343
208	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	6	15	Annie Ng	3.317 -\ncap:40	344
209	Spring	2026	1Th	2026-01-12	2026-04-24	F	09:00 AM-10:15 AM	0	10	Konstantinos\nKostas	3.302 -\ncap:76	345
209	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	6	6	Konstantinos\nKostas	\N	346
210	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	5	10	Konstantinos\nKostas	\N	347
211	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	0	1	Konstantinos\nKostas	\N	348
212	Spring	2026	1Th	2026-01-12	2026-04-24	\N	Online/Distant	0	30	Gulnur\nKalimuldina	\N	349
212	Spring	2026	1L	2026-01-12	2026-04-24	M	02:30 PM-03:45 PM	21	30	Yerbol\nSarbassov	3.316 -\ncap:41	350
213	Spring	2026	1L	2026-01-12	2026-04-24	F	03:00 PM-04:15 PM	6	7	Yerbol\nSarbassov	3.303 -\ncap:32	351
214	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	6	7	Dmitriy Sizov	3.303 -\ncap:32	352
214	Spring	2026	1Lb	2026-01-12	2026-04-24	F	10:00 AM-12:45 PM	6	7	Dmitriy Sizov	3E.217 -\ncap:28	353
215	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	12	7	Yerkin Abdildin	3.303 -\ncap:32	354
216	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	4	7	Amgad Salama	3.317 -\ncap:40	355
216	Spring	2026	1Lb	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	4	7	Amgad Salama	3E.217 -\ncap:28	356
217	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	1	7	Dmitriy Sizov	3.316 -\ncap:41	357
217	Spring	2026	1Lb	2026-01-12	2026-04-24	M	04:00 PM-04:45 PM	1	7	Dmitriy Sizov	3E.217 -\ncap:28	358
218	Spring	2026	1R	2026-01-12	2026-05-08	\N	Online/Distant	47	50	Aziz Burkhanov	\N	359
219	Spring	2026	1L	2026-01-12	2026-05-08	R	09:00 AM-12:00 PM	17	20	Simeon\nNanovsky	(C3) 2008 -\ncap:37	360
220	Spring	2026	1L	2026-01-12	2026-05-08	M	09:00 AM-12:00 PM	22	20	Dina Sharipova	(C3) 2005 -\ncap:38	361
221	Spring	2026	1L	2026-01-12	2026-05-08	T	02:00 PM-05:00 PM	18	20	Dayashankar\nMaurya	(C3) 2003 -\ncap:67	362
222	Spring	2026	1L	2026-01-12	2026-05-08	W	09:00 AM-12:00 PM	18	20	Aziz Burkhanov	(C3) 2005 -\ncap:38	363
223	Spring	2026	1L	2026-01-12	2026-05-08	\N	Online/Distant	19	20	Peter Howie	\N	364
224	Spring	2026	1R	2026-01-12	2026-05-08	\N	Online/Distant	16	18	Aziz Burkhanov	\N	365
225	Spring	2026	1L	2026-01-12	2026-05-08	T R	09:00 AM-12:00 PM	15	16	Riccardo Pelizzo	(C3) 2005 -\ncap:38	366
226	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	46	50	Jurn Gyu Park	7E.220 -\ncap:56	367
227	Spring	2026	1L	2026-01-12	2026-04-24	M W	01:30 PM-02:45 PM	21	30	Jose\nBerengueres	3.416 -\ncap:46	368
228	Spring	2026	1IS	2026-01-12	2026-04-24	S	02:00 PM-04:45 PM	44	50	Michael Lewis	7E.429 -\ncap:90	369
229	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	9	6	Jurn Gyu Park	7E.220 -\ncap:56	370
230	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	11:00 AM-11:50 AM	21	24	Bastiaan\nLohmann	7.317 -\ncap:24	371
230	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	12:00 PM-12:50 PM	22	24	Bastiaan\nLohmann	7.317 -\ncap:24	372
231	Spring	2026	1L	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	17	24	Daniel\nScarborough	8.154 -\ncap:56	373
232	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	24	25	Daniel\nScarborough	\N	374
233	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	3	10	Daniel\nScarborough	\N	375
234	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Curtis Murphy	\N	376
234	Spring	2026	2IS	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Daniel\nScarborough	\N	377
234	Spring	2026	3IS	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Halit Akarca	\N	378
235	Spring	2026	2L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	2	5	Clinton Parker	8.322A -\ncap:32	379
235	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	1	5	Russell Zanca	8.310 -\ncap:27	380
235	Spring	2026	4L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	1	5	Gavin Slade	8.310 -\ncap:27	381
235	Spring	2026	1L	2026-01-12	2026-04-24	W	10:00 AM-03:50 PM	1	2	Reed Coil	8.147 -\ncap:15	382
236	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	2	5	Mikhail Akulov	6.105 -\ncap:64	383
236	Spring	2026	2L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	1	5	Philipp\nSchroeder	8.154 -\ncap:56	384
236	Spring	2026	3L	2026-01-12	2026-04-24	W	05:00 PM-07:50 PM	2	5	Gavin Slade	8.154 -\ncap:56	385
236	Spring	2026	4L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	1	5	Yuliya\nKozitskaya	8.422A -\ncap:32	386
237	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	3	5	Paula Dupuy	8.321 -\ncap:32	387
237	Spring	2026	3L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	1	5	Mikhail Sokolov	8.154 -\ncap:56	388
238	Spring	2026	2L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	1	3	Clinton Parker	8.322A -\ncap:32	389
238	Spring	2026	3L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	1	5	Maria Rybakova	8.422A -\ncap:32	390
238	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	1	3	Daniel Beben	9.204 -\ncap:38	391
239	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	1	3	Katherine\nErdman	8.105 -\ncap:56	392
240	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	1	3	Clinton Parker	8.322A -\ncap:32	393
241	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	1	3	Saltanat\nAkhmetova	8.310 -\ncap:27	394
242	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Mikhail Akulov	\N	395
242	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Benjamin Brosig	\N	396
242	Spring	2026	3L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Matvey\nLomonosov	\N	397
242	Spring	2026	4L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Uli Schamiloglu	\N	398
242	Spring	2026	5L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Brian Smith	\N	399
242	Spring	2026	6L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Nikolay\nTsyrempilov	\N	400
243	Spring	2026	1S	2026-01-12	2026-04-24	\N	Online/Distant	9	15	Uli Schamiloglu	\N	401
244	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	9	15	Uli Schamiloglu	\N	402
245	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	31	35	Uli Schamiloglu	\N	403
246	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	160	170	Alejandro Melo\nPonce	Blue Hall -\ncap:239	404
246	Spring	2026	1T	2026-01-12	2026-04-24	M	06:00 PM-06:50 PM	63	65	Alejandro Melo\nPonce	8.522 -\ncap:72	405
246	Spring	2026	2T	2026-01-12	2026-04-24	M	07:00 PM-07:50 PM	46	65	Alejandro Melo\nPonce	8.522 -\ncap:72	406
246	Spring	2026	3T	2026-01-12	2026-04-24	T	06:00 PM-06:50 PM	51	65	Alejandro Melo\nPonce	8.522 -\ncap:72	407
247	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	158	170	Galiya\nSagyndykova	Blue Hall -\ncap:239	408
247	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	170	170	Mehmet Demir	Blue Hall -\ncap:239	409
247	Spring	2026	1T	2026-01-12	2026-04-24	T	07:00 PM-07:50 PM	42	65	Galiya\nSagyndykova	8.522 -\ncap:72	410
247	Spring	2026	2T	2026-01-12	2026-04-24	W	06:00 PM-06:50 PM	64	65	Galiya\nSagyndykova	8.522 -\ncap:72	411
247	Spring	2026	3T	2026-01-12	2026-04-24	W	07:00 PM-07:50 PM	59	65	Galiya\nSagyndykova	8.522 -\ncap:72	412
247	Spring	2026	4T	2026-01-12	2026-04-24	R	06:00 PM-06:50 PM	65	65	Mehmet Demir	8.522 -\ncap:72	413
247	Spring	2026	5T	2026-01-12	2026-04-24	R	07:00 PM-07:50 PM	37	65	Mehmet Demir	8.522 -\ncap:72	414
247	Spring	2026	6T	2026-01-12	2026-04-24	F	06:00 PM-06:50 PM	61	65	Mehmet Demir	8.522 -\ncap:72	415
248	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	169	200	Aigerim\nSarsenbayeva	Blue Hall -\ncap:239	416
249	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	44	40	Oleg Rubanov	8.307 -\ncap:55	417
250	Spring	2026	1T	2026-01-12	2026-04-24	M	06:00 PM-06:50 PM	64	65	Zhanna\nKapsalyamova	8.307 -\ncap:55	418
250	Spring	2026	2T	2026-01-12	2026-04-24	M	07:00 PM-07:50 PM	60	65	Zhanna\nKapsalyamova	8.307 -\ncap:55	419
250	Spring	2026	3T	2026-01-12	2026-04-24	T	06:00 PM-06:50 PM	43	60	Zhanna\nKapsalyamova	8.307 -\ncap:55	420
250	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	167	170	Zhanna\nKapsalyamova	Blue Hall -\ncap:239	421
251	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	52	50	Vladyslav Nora	8.327 -\ncap:58	422
252	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Rajarshi Bhowal	\N	423
252	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Aigerim\nSarsenbayeva	\N	424
252	Spring	2026	3Int	2026-01-12	2026-04-24	\N	Online/Distant	4	5	Mehmet Demir	\N	425
252	Spring	2026	6Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Andrey\nTkachenko	\N	426
253	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	41	40	Nino Buliskeria	8.327 -\ncap:58	427
254	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	33	35	Ahmet Altinok	8.307 -\ncap:55	428
254	Spring	2026	2L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	36	35	Ahmet Altinok	8.307 -\ncap:55	429
255	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	36	35	Levent Kockesen	8.307 -\ncap:55	430
255	Spring	2026	2L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	39	35	Levent Kockesen	8.307 -\ncap:55	431
256	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:15 PM	33	35	Rajarshi Bhowal	8.327 -\ncap:58	432
256	Spring	2026	2L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	31	33	Rajarshi Bhowal	8.327 -\ncap:58	433
257	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	37	35	Aigerim\nSarsenbayeva	8.307 -\ncap:55	434
257	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	44	35	Aigerim\nSarsenbayeva	8.307 -\ncap:55	435
258	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	14	35	Zhanna\nKapsalyamova	8.307 -\ncap:55	436
258	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	17	31	Zhanna\nKapsalyamova	8.307 -\ncap:55	437
259	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Rajarshi Bhowal	\N	438
259	Spring	2026	6IS	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Nino Buliskeria	\N	439
259	Spring	2026	7IS	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Alejandro Melo\nPonce	\N	440
260	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	24	22	Josef Ruzicka	8.327 -\ncap:58	441
260	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	41	35	Josef Ruzicka	8.327 -\ncap:58	442
261	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	32	35	Andrey\nTkachenko	8.307 -\ncap:55	443
261	Spring	2026	2L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	32	35	Andrey\nTkachenko	8.307 -\ncap:55	444
262	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	31	34	Rajarshi Bhowal	8.307 -\ncap:55	445
263	Spring	2026	1L	2026-01-12	2026-04-24	T R	07:30 PM-08:45 PM	18	20	Alejandro Melo\nPonce	7E.329 -\ncap:95	446
264	Spring	2026	1L	2026-01-12	2026-04-24	M	02:00 PM-04:50 PM	12	20	Vladyslav Nora	8.319 -\ncap:30	447
265	Spring	2026	1L	2026-01-12	2026-04-24	W	02:00 PM-04:50 PM	12	20	Ali Elminejad	8.319 -\ncap:30	448
266	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	12	20	Josef Ruzicka	8.319 -\ncap:30	449
267	Spring	2026	2L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	17	12	Josef Ruzicka	8.327 -\ncap:58	450
267	Spring	2026	3L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	1	1	Josef Ruzicka	8.327 -\ncap:58	451
268	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	1	10	Rajarshi Bhowal	8.307 -\ncap:55	452
269	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	0	10	Rajarshi Bhowal	8.327 -\ncap:58	453
270	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	3	10	Zhanna\nKapsalyamova	8.307 -\ncap:55	454
271	Spring	2026	1CP	2026-01-12	2026-04-24	\N	Online/Distant	9	15	Zhanna\nKapsalyamova	\N	455
272	Spring	2026	1L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	7	10	Ahmet Aypay	(C3) 2001 -\ncap:68	456
272	Spring	2026	4L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	4	8	Gulzhanat Gafu	(C3) 5029 -\ncap:9	457
272	Spring	2026	2L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	7	8	Alper Calikoglu	(C3) 5033 -\ncap:9	458
272	Spring	2026	3L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	6	8	Zumrad Kataeva	(C3) 2033 -\ncap:10	459
273	Spring	2026	3L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	6	10	Zumrad Kataeva	TBA - cap:0	460
273	Spring	2026	1L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	7	10	Ahmet Aypay	(C3) 2001 -\ncap:68	461
273	Spring	2026	4L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	4	10	Gulzhanat Gafu	(C3) 5029 -\ncap:9	462
273	Spring	2026	2L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	7	10	Alper Calikoglu	(C3) 5033 -\ncap:9	463
274	Spring	2026	1L	2026-04-08	2026-04-17	M T W R F	09:00 AM-06:00 PM	18	20	Gulzhanat Gafu	(C3) 1010 -\ncap:70	464
275	Spring	2026	1L	2026-03-30	2026-04-07	M T W R F	09:00 AM-06:00 PM	10	8	Zumrad Kataeva	(C3) 2004 -\ncap:67	465
276	Spring	2026	1L	2026-03-30	2026-04-07	M T W R F	09:00 AM-06:00 PM	8	8	Gulzhanat Gafu	(C3) 1011 -\ncap:28	466
277	Spring	2026	3L	2026-01-12	2026-01-16	\N	Online/Distant	1	1	Duishonkul\nShamatov	\N	467
277	Spring	2026	2L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	7	10	Sourav\nMukhopadhyay	(C3) 5030 -\ncap:9	468
277	Spring	2026	1L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	5	10	Janet Helmer	(C3) 1010 -\ncap:70	469
278	Spring	2026	3L	2026-04-20	2026-04-24	\N	Online/Distant	1	1	Duishonkul\nShamatov	\N	470
278	Spring	2026	2L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	7	10	Sourav\nMukhopadhyay	(C3) 5030 -\ncap:9	471
278	Spring	2026	1L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	5	10	Janet Helmer	(C3) 1010 -\ncap:70	472
279	Spring	2026	1L	2026-04-08	2026-04-17	M T W R F	09:00 AM-06:00 PM	15	20	Oliver Mutanga	(C3) 2004 -\ncap:67	473
280	Spring	2026	1L	2026-03-30	2026-04-07	M T W R F	09:00 AM-06:00 PM	15	22	Sourav\nMukhopadhyay	(C3) 2001 -\ncap:68	474
281	Spring	2026	1L	2026-01-12	2026-04-24	T	02:00 PM-05:00 PM	22	25	Abdelaal Amr	(C3) 2024 -\ncap:24	475
282	Spring	2026	1L	2026-01-12	2026-04-24	M	10:00 AM-01:00 PM	21	21	Philip\nMontgomery	(C3) 2016 -\ncap:24	476
283	Spring	2026	1L	2026-01-12	2026-04-24	M	10:00 AM-01:00 PM	22	25	Abdelaal Amr	(C3) 2024 -\ncap:24	477
284	Spring	2026	1L	2026-01-12	2026-04-24	T	10:00 AM-01:00 PM	7	10	Anas Hajar	(C3) 2016 -\ncap:24	478
284	Spring	2026	2L	2026-01-12	2026-04-24	T	02:00 PM-05:00 PM	7	10	Syed Manan	(C3) 2016 -\ncap:24	479
284	Spring	2026	3L	2026-01-12	2026-04-24	W	10:00 AM-01:00 PM	4	10	Sulushash\nKerimkulova	(C3) 2016 -\ncap:24	480
284	Spring	2026	4L	2026-01-12	2026-04-24	W	02:00 PM-05:00 PM	3	10	Philip\nMontgomery	(C3) 2016 -\ncap:24	481
285	Spring	2026	3L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	6	10	Gulmira Qanay	TBA - cap:0	482
285	Spring	2026	2L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	7	10	Daniel Torrano	(C3) 2004 -\ncap:67	483
285	Spring	2026	1L	2026-01-12	2026-01-16	M T W R F	09:00 AM-05:00 PM	7	10	Kairat\nKurakbayev	(C3) 1011 -\ncap:28	484
286	Spring	2026	3L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	6	10	Gulmira Qanay	TBA - cap:0	485
286	Spring	2026	2L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	7	10	Daniel Torrano	(C3) 2004 -\ncap:67	486
286	Spring	2026	1L	2026-04-20	2026-04-24	M T W R F	09:00 AM-05:00 PM	7	10	Kairat\nKurakbayev	(C3) 1011 -\ncap:28	487
287	Spring	2026	1L	2026-04-08	2026-04-17	M T W R F	09:00 AM-05:00 PM	21	20	Naureen Durrani	(C3) 2001 -\ncap:68	488
288	Spring	2026	1L	2026-03-30	2026-04-07	M T W R F	09:00 AM-06:05 PM	21	22	Duishonkul\nShamatov	(C3) 1010 -\ncap:70	489
289	Spring	2026	1T	2026-01-12	2026-04-24	M	02:00 PM-05:00 PM	21	21	Anita\nJayachandran	(C3) 2016 -\ncap:24	490
290	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	24	25	Jeremy Richard\nSpring	\N	491
290	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	18	25	Andrew\nDrybrough	\N	492
290	Spring	2026	3L	2026-01-12	2026-04-24	\N	Online/Distant	12	25	Jeremy Richard\nSpring	\N	493
291	Spring	2026	1L	2026-01-12	2026-04-24	W	02:00 PM-05:00 PM	14	30	Nazira\nAmirzhanova	(C3) 3034 -\ncap:26	494
292	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	26	30	Nazira\nAmirzhanova	\N	495
293	Spring	2026	1L	2026-01-12	2026-04-24	R	09:00 AM-01:00 PM	3	30	Dilrabo\nJonbekova	(C3) 3034 -\ncap:26	496
294	Spring	2026	1L	2026-01-12	2026-04-24	R	10:00 AM-01:00 PM	8	10	Andrew\nDrybrough	(C3) 2002 -\ncap:66	497
295	Spring	2026	1L	2026-01-12	2026-04-24	T	10:00 AM-01:00 PM	5	25	Anita\nJayachandran	(C3) 2008 -\ncap:37	498
296	Spring	2026	2L	2026-01-28	2026-02-06	M T W R F	09:00 AM-05:00 PM	17	20	Sourav\nMukhopadhyay	(C3) 2001 -\ncap:68	499
296	Spring	2026	3L	2026-01-28	2026-02-06	M T W R F	09:00 AM-06:00 PM	18	20	Daniel Torrano	(C3) 2004 -\ncap:67	500
296	Spring	2026	4L	2026-01-12	2026-04-24	T	10:00 AM-01:00 PM	22	25	Ahmet Aypay	(C3) 2024 -\ncap:24	501
296	Spring	2026	1L	2026-01-28	2026-02-06	M T W R F	09:00 AM-06:00 PM	19	20	Dilrabo\nJonbekova	(C3) 1010 -\ncap:70	502
297	Spring	2026	2L	2026-01-19	2026-01-27	M T W R F	09:00 AM-06:00 PM	21	20	Assel Sharimova	(C3) 2001 -\ncap:68	503
297	Spring	2026	3L	2026-01-19	2026-01-27	M T W R F	09:00 AM-06:00 PM	15	20	Sourav\nMukhopadhyay	(C3) 2004 -\ncap:67	504
297	Spring	2026	1L	2026-01-19	2026-01-27	M T W R F	09:00 AM-06:00 PM	18	20	Alper Calikoglu	(C3) 1010 -\ncap:70	505
298	Spring	2026	1L	2026-01-12	2026-04-24	W	10:00 AM-01:00 PM	12	12	Ahmet Aypay	(C3) 3034 -\ncap:26	506
299	Spring	2026	1L	2026-01-12	2026-04-24	M	10:00 AM-01:00 PM	12	12	Duishonkul\nShamatov	(C3) 3034 -\ncap:26	507
300	Spring	2026	1L	2026-01-12	2026-04-24	T	02:00 PM-05:00 PM	12	12	Munyaradzi\nHwami	(C3) 3034 -\ncap:26	508
301	Spring	2026	1L	2026-01-12	2026-04-24	R	02:00 PM-05:00 PM	12	12	Jason Sparks	(C3) 3034 -\ncap:26	509
302	Spring	2026	1IS	2026-01-12	2026-04-24	T	10:00 AM-01:00 PM	12	12	Dilrabo\nJonbekova	(C3) 3034 -\ncap:26	510
303	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Sourav\nMukhopadhyay	\N	511
303	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	3	3	Daniel Torrano	\N	512
303	Spring	2026	3L	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Afzal Mir	\N	513
303	Spring	2026	4L	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Kairat\nKurakbayev	\N	514
303	Spring	2026	5L	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Sulushash\nKerimkulova	\N	515
303	Spring	2026	6L	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Syed Manan	\N	516
304	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	1	2	Anas Hajar	\N	517
304	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	1	2	Sourav\nMukhopadhyay	\N	518
304	Spring	2026	3L	2026-01-12	2026-04-24	\N	Online/Distant	1	1	Ahmet Aypay	\N	519
305	Spring	2026	1S	2026-01-12	2026-04-24	M	10:00 AM-01:00 PM	8	8	Zumrad Kataeva	(C3) 2003 -\ncap:67	520
306	Spring	2026	1S	2026-01-12	2026-04-24	F	02:00 PM-05:00 PM	10	10	Jason Sparks	(C3) 3034 -\ncap:26	521
307	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	3	5	Ahmet Aypay	\N	522
307	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Anas Hajar	\N	523
307	Spring	2026	3L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Duishonkul\nShamatov	\N	524
307	Spring	2026	4L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Jason Sparks	\N	525
307	Spring	2026	5L	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Afzal Mir	\N	526
307	Spring	2026	6L	2026-01-12	2026-04-24	\N	Online/Distant	3	5	Sourav\nMukhopadhyay	\N	527
307	Spring	2026	7L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Munyaradzi\nHwami	\N	528
307	Spring	2026	8L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Daniel Torrano	\N	529
307	Spring	2026	9L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Daniel Torrano	\N	530
307	Spring	2026	10L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Syed Manan	\N	531
307	Spring	2026	11L	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Bridget\nGoodman	\N	532
307	Spring	2026	12L	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Naureen Durrani	\N	533
307	Spring	2026	13L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Dilrabo\nJonbekova	\N	534
308	Spring	2026	1L	2026-01-12	2026-04-24	M	02:00 PM-05:00 PM	6	25	Philip\nMontgomery	(C3) 2005 -\ncap:38	535
309	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	72	80	Galymzhan\nNauryzbayev	3E.220 -\ncap:90	536
310	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-03:45 PM	20	20	Shyngys\nSalakchinov	3E.321 -\ncap:22	537
310	Spring	2026	2Lb	2026-01-12	2026-04-24	T	02:00 PM-03:45 PM	10	20	Shyngys\nSalakchinov	3E.321 -\ncap:22	538
310	Spring	2026	3Lb	2026-01-12	2026-04-24	W	02:00 PM-03:45 PM	20	20	Gulsim\nKulsharova	3E.321 -\ncap:22	539
310	Spring	2026	4Lb	2026-01-12	2026-04-24	R	02:00 PM-03:45 PM	20	20	Gulsim\nKulsharova	3E.321 -\ncap:22	540
311	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	74	80	Sultangali\nArzykulov	3E.220 -\ncap:90	541
312	Spring	2026	1Lb	2026-01-12	2026-04-24	M	12:00 PM-01:45 PM	25	26	Aliya\nNurmukhanbeto\nva	3E.322 -\ncap:25	542
312	Spring	2026	2Lb	2026-01-12	2026-04-24	T	12:00 PM-01:45 PM	22	27	Aliya\nNurmukhanbeto\nva	3E.322 -\ncap:25	543
312	Spring	2026	3Lb	2026-01-12	2026-04-24	W	12:00 PM-01:45 PM	27	27	Aliya\nNurmukhanbeto\nva	3E.322 -\ncap:25	544
313	Spring	2026	1L	2026-01-12	2026-04-24	M W	09:00 AM-10:15 AM	45	60	Mohammad\nHashmi	3E.221 -\ncap:50	545
314	Spring	2026	1Lb	2026-01-12	2026-04-24	W	02:00 PM-03:45 PM	29	30	Shyngys\nSalakchinov	3E.322 -\ncap:25	546
314	Spring	2026	2Lb	2026-01-12	2026-04-24	R	02:00 PM-03:45 PM	14	30	Shyngys\nSalakchinov	3E.322 -\ncap:25	547
315	Spring	2026	1L	2026-01-12	2026-04-24	M W	10:30 AM-11:45 AM	17	20	Prashant Jamwal	(C3) 3037 -\ncap:39	548
316	Spring	2026	1Lb	2026-01-12	2026-04-24	T	02:30 PM-04:15 PM	16	15	Aliya\nNurmukhanbeto\nva	TBA - cap:0	549
317	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	23	40	Mehdi Bagheri	3E.224 -\ncap:90	550
318	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	19	50	Ainur\nRakhymbay,\nAresh Dadlani	3E.221 -\ncap:50	551
319	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	26	40	Sultangali\nArzykulov	3.322 -\ncap:41	552
320	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	4	4	Aliya\nNurmukhanbeto\nva	\N	553
321	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	31	40	Carlo Molardi	3.415 -\ncap:42	555
322	Spring	2026	1Lb	2026-01-12	2026-04-24	F	01:00 PM-04:00 PM	14	25	Ainur\nRakhymbay	3E.318 -\ncap:40	556
323	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	3	40	Muhammad\nAkhtar	3.416 -\ncap:46	557
324	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	9	25	Ainur\nRakhymbay,\nAresh Dadlani	3.309 -\ncap:40	558
326	Spring	2026	1Lb	2026-01-12	2026-04-24	W	02:30 PM-04:00 PM	10	20	Ainur\nRakhymbay,\nMehdi Shafiee	3E.333 -\ncap:40	560
329	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	2	20	Carlo Molardi	3.309 -\ncap:40	563
330	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	35	30	Daniele Tosi	3.303 -\ncap:32	564
331	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	0	0	Maria\nTsakalerou,\nSaltanat\nAkhmadi	3.317 -\ncap:40	565
332	Spring	2026	1P	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	19	19	Maria\nTsakalerou	3.317 -\ncap:40	566
333	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	93	95	Arailym\nSerikbay	3E.224 -\ncap:90	567
334	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	71	75	Chang Shon	3E.224 -\ncap:90	568
334	Spring	2026	2L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	91	92	Asma Perveen	3E.224 -\ncap:90	569
320	Spring	2026	1L	2026-01-12	2026-04-24	W	05:00 PM-06:15 PM	44	54	Aliya\nNurmukhanbeto\nva	7E.220 -\ncap:56	554
325	Spring	2026	1L	2026-01-12	2026-04-24	R	01:30 PM-03:00 PM	17	40	Ainur\nRakhymbay,\nMehdi Shafiee	3.407 -\ncap:40	559
334	Spring	2026	1Lb	2026-01-12	2026-04-24	T	04:00 PM-05:45 PM	34	38	Chang Shon	3E.331 -\ncap:24	570
334	Spring	2026	2Lb	2026-01-12	2026-04-24	R	04:00 PM-05:45 PM	34	37	Chang Shon	3E.331 -\ncap:24	571
334	Spring	2026	3Lb	2026-01-12	2026-04-24	W	01:00 PM-02:45 PM	48	48	Asma Perveen	3E.331 -\ncap:24	572
334	Spring	2026	4Lb	2026-01-12	2026-04-24	F	04:00 PM-05:45 PM	46	48	Asma Perveen	3E.331 -\ncap:24	573
335	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	85	85	Annie Ng,\nNurxat Nuraje	5.103 -\ncap:160	574
335	Spring	2026	2L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	54	60	Annie Ng,\nNurxat Nuraje	3E.220 -\ncap:90	575
336	Spring	2026	2L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	27	35	Aishuak Konarov	3.317 -\ncap:40	577
336	Spring	2026	4L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	36	40	Behrouz Maham	3.416 -\ncap:46	578
336	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	58	64	Elnara\nKussinova	3E.220 -\ncap:90	579
336	Spring	2026	3L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	74	75	Yerkin Abdildin	3E.223 -\ncap:63	580
337	Spring	2026	4Lb	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Md. Hazrat Ali	\N	581
337	Spring	2026	3Lb	2026-01-12	2026-04-24	R	09:00 AM-10:15 AM	29	35	Boris Golman	3.323 -\ncap:64	582
337	Spring	2026	1Lb	2026-01-12	2026-04-24	W	04:00 PM-05:15 PM	66	70	Saltanat\nAkhmadi	3E.223 -\ncap:63	583
337	Spring	2026	2L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	73	75	Md. Hazrat Ali	3E.223 -\ncap:63	584
337	Spring	2026	2Lb	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	71	75	Md. Hazrat Ali	3E.223 -\ncap:63	585
337	Spring	2026	3L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	30	35	Boris Golman	3.415 -\ncap:42	586
337	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	64	70	Saltanat\nAkhmadi	7E.429 -\ncap:90	587
338	Spring	2026	5L	2026-01-12	2026-04-24	\N	Online/Distant	2	3	Yerkin Abdildin,\nEssam Shehab	\N	588
338	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	46	50	Dhawal Shah,\nSabina\nKhamzina	3.323 -\ncap:64	589
338	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	68	70	Mert Guney	5.103 -\ncap:160	590
338	Spring	2026	4L	2026-01-12	2026-04-24	F	03:00 PM-04:45 PM	45	51	Yerkin Abdildin,\nEssam Shehab	3E.223 -\ncap:63	591
338	Spring	2026	1L	2026-01-12	2026-04-24	W	05:00 PM-06:15 PM	43	50	Galymzhan\nNauryzbayev	3E.224 -\ncap:90	592
339	Spring	2026	39S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay, Zhanel\nZakirova	2.142 -\ncap:28	593
339	Spring	2026	40S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay, Zhanel\nZakirova	2.142 -\ncap:28	594
339	Spring	2026	9S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nAlina Maksut,\nMichael\nJohnson, Susan\nFinlay	2.317 -\ncap:20	595
339	Spring	2026	10S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nAlina Maksut,\nMichael\nJohnson, Susan\nFinlay	2.317 -\ncap:20	596
339	Spring	2026	23S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nBenjamin\nThomas, Michael\nJohnson, Susan\nFinlay	2.417 -\ncap:21	597
339	Spring	2026	24S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nBenjamin\nThomas, Michael\nJohnson, Susan\nFinlay	2.417 -\ncap:21	598
339	Spring	2026	1S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nAlisa Neufeldt,\nMichael\nJohnson, Susan\nFinlay	2.228 -\ncap:17	599
339	Spring	2026	2S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	13	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nAlisa Neufeldt,\nMichael\nJohnson, Susan\nFinlay	2.228 -\ncap:17	600
339	Spring	2026	17S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.408 -\ncap:18	601
339	Spring	2026	18S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	13	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.408 -\ncap:18	602
339	Spring	2026	15S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson,\nKatherine\nAndersen, Susan\nFinlay	2.402 -\ncap:28	603
339	Spring	2026	16S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson,\nKatherine\nAndersen, Susan\nFinlay	2.402 -\ncap:28	604
339	Spring	2026	45S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.247 -\ncap:22	605
339	Spring	2026	46S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.247 -\ncap:22	606
339	Spring	2026	43S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.246 -\ncap:23	607
339	Spring	2026	44S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.246 -\ncap:23	608
339	Spring	2026	11S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nGeorge\nKovacevic,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.319 -\ncap:25	609
339	Spring	2026	12S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	13	15	Deanne Cobb-\nZygadlo, Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.319 -\ncap:25	610
339	Spring	2026	21S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay,\nClaudette Clerc	2.410 -\ncap:21	611
339	Spring	2026	22S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay,\nClaudette Clerc	2.410 -\ncap:21	612
339	Spring	2026	25S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Phillip Bell,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.419 -\ncap:21	613
339	Spring	2026	26S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	Phillip Bell,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.419 -\ncap:21	614
339	Spring	2026	7S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Anel\nNurmukhametov\na, Susan Finlay	2.312 -\ncap:22	615
341	Spring	2026	14S	2026-01-12	2026-04-17	T R	10:00 AM-10:50 AM	20	22	Elmira\nTursunkhanova,\nGyuzel\nZhumabayeva	2.105 -\ncap:64	660
339	Spring	2026	8S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Anel\nNurmukhametov\na, Susan Finlay	2.312 -\ncap:22	616
339	Spring	2026	5S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	13	15	Lala Movsesian,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.310 -\ncap:24	617
339	Spring	2026	6S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Lala Movsesian,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.310 -\ncap:24	618
339	Spring	2026	13S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay, Anna Sin	2.321 -\ncap:31	619
339	Spring	2026	14S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay, Anna Sin	2.321 -\ncap:31	620
339	Spring	2026	29S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nNatasha\nSinclair, Michael\nJohnson, Susan\nFinlay	2.427 -\ncap:20	621
339	Spring	2026	30S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson,\nSaltanat\nDochshanova,\nSusan Finlay	2.427 -\ncap:20	622
339	Spring	2026	31S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay, Joyce\nChoueri	2.502 -\ncap:25	623
339	Spring	2026	32S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay, Joyce\nChoueri	2.502 -\ncap:25	624
339	Spring	2026	33S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	13	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Mark\nHoughtaling,\nSusan Finlay	2.508 -\ncap:24	625
339	Spring	2026	34S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	James Arthurs,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.508 -\ncap:24	626
339	Spring	2026	35S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nAnne Stander,\nMichael\nJohnson, Susan\nFinlay	2.509 -\ncap:16	627
339	Spring	2026	36S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nAnne Stander,\nMichael\nJohnson, Susan\nFinlay	2.509 -\ncap:16	628
339	Spring	2026	37S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.510 -\ncap:23	629
339	Spring	2026	38S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.510 -\ncap:23	630
339	Spring	2026	41S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Sabine\nSundell, Susan\nFinlay	2.518 -\ncap:16	631
339	Spring	2026	42S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Sabine\nSundell, Susan\nFinlay	2.518 -\ncap:16	632
339	Spring	2026	19S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Sabina\nBairamova,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.522b -\ncap:24	633
339	Spring	2026	20S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	15	15	Sabina\nBairamova,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.522b -\ncap:24	634
339	Spring	2026	3S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay, Eduard\nSurdeanu	2.308 -\ncap:22	635
339	Spring	2026	4S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	13	15	Nabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay, Eduard\nSurdeanu	2.308 -\ncap:22	636
339	Spring	2026	27S	2026-01-12	2026-04-17	T W R F	09:00 AM-10:50 AM	15	15	Gerald Selous,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.422B -\ncap:20	637
339	Spring	2026	28S	2026-01-12	2026-04-17	T W R F	11:00 AM-12:50 PM	14	15	Gerald Selous,\nNabila\nNejmaoui,\nAlejandro Acuyo-\nCespedes,\nRaquel Reinagel,\nMichael\nJohnson, Susan\nFinlay	2.422B -\ncap:20	638
340	Spring	2026	2L	2026-01-12	2026-04-24	R	02:00 PM-05:00 PM	47	50	Mirat Akshalov,\nTom Vinaimont	(C3) 1009 -\ncap:70	639
340	Spring	2026	1L	2026-01-12	2026-04-24	T	02:00 PM-05:00 PM	30	23	Mirat Akshalov,\nTom Vinaimont	(C3) 3017 -\ncap:38	640
341	Spring	2026	2S	2026-01-12	2026-04-17	T R	09:00 AM-09:50 AM	18	22	Elmira\nTursunkhanova,\nAssel\nNurdauletova	2.302 -\ncap:78	641
341	Spring	2026	4S	2026-01-12	2026-04-17	T R	10:00 AM-10:50 AM	18	22	Elmira\nTursunkhanova,\nAssel\nNurdauletova	2.302 -\ncap:78	642
341	Spring	2026	3L	2026-01-12	2026-04-17	M	12:00 PM-01:20 PM	38	48	Elmira\nTursunkhanova,\nAssel\nNurdauletova	2.307 -\ncap:75	643
341	Spring	2026	4L	2026-01-12	2026-04-17	M	01:30 PM-02:50 PM	39	48	Elmira\nTursunkhanova,\nAssel\nNurdauletova	2.307 -\ncap:75	644
341	Spring	2026	11L	2026-01-12	2026-04-17	M	09:00 AM-10:20 AM	61	66	Elmira\nTursunkhanova,\nAruzhan\nKamalova	2.307 -\ncap:75	645
341	Spring	2026	12L	2026-01-12	2026-04-17	M	10:30 AM-11:50 AM	43	48	Elmira\nTursunkhanova,\nAruzhan\nKamalova	2.307 -\ncap:75	646
341	Spring	2026	22S	2026-01-12	2026-04-17	T R	09:00 AM-09:50 AM	19	22	Elmira\nTursunkhanova,\nAruzhan\nKamalova	2.507 -\ncap:73	647
341	Spring	2026	24S	2026-01-12	2026-04-17	T R	10:00 AM-10:50 AM	21	22	Elmira\nTursunkhanova,\nAruzhan\nKamalova	2.507 -\ncap:73	648
341	Spring	2026	26S	2026-01-12	2026-04-17	T R	01:00 PM-01:50 PM	21	22	Elmira\nTursunkhanova,\nAruzhan\nKamalova	2.507 -\ncap:73	649
341	Spring	2026	18S	2026-01-12	2026-04-17	W F	09:00 AM-09:50 AM	21	22	Elmira\nTursunkhanova,\nGyuzel\nZhumabayeva	2.141 -\ncap:28	650
341	Spring	2026	20S	2026-01-12	2026-04-17	W F	10:00 AM-10:50 AM	21	22	Elmira\nTursunkhanova,\nGyuzel\nZhumabayeva	2.141 -\ncap:28	651
341	Spring	2026	6S	2026-01-12	2026-04-17	T R	02:00 PM-02:50 PM	20	22	Terence\nGreatrex, Elmira\nTursunkhanova	2.105 -\ncap:64	652
341	Spring	2026	7L	2026-01-12	2026-04-17	M	09:00 AM-10:20 AM	41	48	Elmira\nTursunkhanova,\nGyuzel\nZhumabayeva	2.105 -\ncap:64	653
341	Spring	2026	8L	2026-01-12	2026-04-17	M	10:30 AM-11:50 AM	42	48	Elmira\nTursunkhanova,\nGyuzel\nZhumabayeva	2.105 -\ncap:64	654
341	Spring	2026	8S	2026-01-12	2026-04-17	W F	09:00 AM-09:50 AM	21	22	Elmira\nTursunkhanova,\nAssel\nNurdauletova	2.105 -\ncap:64	655
341	Spring	2026	9L	2026-01-12	2026-04-17	M	12:00 PM-01:20 PM	61	66	Elmira\nTursunkhanova,\nAssel Sadykova	2.105 -\ncap:64	656
341	Spring	2026	10L	2026-01-12	2026-04-17	M	01:30 PM-02:50 PM	42	48	Elmira\nTursunkhanova,\nAssel Sadykova	2.105 -\ncap:64	657
341	Spring	2026	10S	2026-01-12	2026-04-17	W F	10:00 AM-10:50 AM	20	22	Elmira\nTursunkhanova,\nAssel\nNurdauletova	2.105 -\ncap:64	658
341	Spring	2026	12S	2026-01-12	2026-04-17	T R	09:00 AM-09:50 AM	21	22	Elmira\nTursunkhanova,\nGyuzel\nZhumabayeva	2.105 -\ncap:64	659
341	Spring	2026	16S	2026-01-12	2026-04-17	T R	01:00 PM-01:50 PM	21	22	Terence\nGreatrex, Elmira\nTursunkhanova	2.105 -\ncap:64	661
341	Spring	2026	27S	2026-01-12	2026-04-17	W F	11:00 AM-11:50 AM	21	22	Elmira\nTursunkhanova,\nAssel Sadykova	2.105 -\ncap:64	662
341	Spring	2026	29S	2026-01-12	2026-04-17	W F	12:00 PM-12:50 PM	21	22	Elmira\nTursunkhanova,\nAssel Sadykova	2.105 -\ncap:64	663
341	Spring	2026	31S	2026-01-12	2026-04-17	T R	12:00 PM-12:50 PM	21	22	Terence\nGreatrex, Elmira\nTursunkhanova	2.105 -\ncap:64	664
341	Spring	2026	21S	2026-01-12	2026-04-17	T R	11:00 AM-11:50 AM	20	22	Elmira\nTursunkhanova,\nAssel Sadykova	2.327 -\ncap:88	665
341	Spring	2026	23S	2026-01-12	2026-04-17	T R	12:00 PM-12:50 PM	20	22	Elmira\nTursunkhanova,\nAssel Sadykova	2.327 -\ncap:88	666
341	Spring	2026	25S	2026-01-12	2026-04-17	T R	01:00 PM-01:50 PM	21	22	Elmira\nTursunkhanova,\nAssel Sadykova	2.327 -\ncap:88	667
341	Spring	2026	1L	2026-01-12	2026-04-17	M	09:00 AM-10:20 AM	59	66	Elmira\nTursunkhanova,\nJonathan\nLemelman	2.407 -\ncap:85	668
341	Spring	2026	2L	2026-01-12	2026-04-17	M	10:30 AM-11:50 AM	42	48	Elmira\nTursunkhanova,\nJonathan\nLemelman	2.407 -\ncap:85	669
341	Spring	2026	5L	2026-01-12	2026-04-17	M	12:00 PM-01:30 PM	63	66	Elmira\nTursunkhanova,\nShannon Smith	2.407 -\ncap:85	670
341	Spring	2026	6L	2026-01-12	2026-04-17	M	01:30 PM-02:50 PM	42	48	Elmira\nTursunkhanova,\nShannon Smith	2.407 -\ncap:85	671
341	Spring	2026	1S	2026-01-12	2026-04-17	W F	11:00 AM-11:50 AM	20	22	Elmira\nTursunkhanova,\nJonathan\nLemelman	2.517 -\ncap:23	672
341	Spring	2026	3S	2026-01-12	2026-04-17	T R	12:00 PM-12:50 PM	20	22	Elmira\nTursunkhanova,\nJonathan\nLemelman	2.517 -\ncap:23	673
341	Spring	2026	5S	2026-01-12	2026-04-17	T R	11:00 AM-11:50 AM	19	22	Elmira\nTursunkhanova,\nJonathan\nLemelman	2.517 -\ncap:23	674
341	Spring	2026	7S	2026-01-12	2026-04-17	W F	12:00 PM-12:50 PM	21	22	Elmira\nTursunkhanova,\nJonathan\nLemelman	2.517 -\ncap:23	675
341	Spring	2026	9S	2026-01-12	2026-04-17	T R	01:00 PM-01:50 PM	21	22	Elmira\nTursunkhanova,\nJonathan\nLemelman	2.517 -\ncap:23	676
341	Spring	2026	28S	2026-01-12	2026-04-17	W F	09:00 AM-09:50 AM	21	22	Elmira\nTursunkhanova,\nAruzhan\nKamalova	2.517 -\ncap:23	677
341	Spring	2026	30S	2026-01-12	2026-04-17	W F	10:00 AM-10:50 AM	22	22	Elmira\nTursunkhanova,\nAruzhan\nKamalova	2.517 -\ncap:23	678
341	Spring	2026	11S	2026-01-12	2026-04-17	T R	11:00 AM-11:50 AM	21	22	Elmira\nTursunkhanova,\nShannon Smith	2.322 -\ncap:45	679
341	Spring	2026	13L	2026-01-12	2026-04-17	M	09:00 AM-10:20 AM	41	48	Terence\nGreatrex, Elmira\nTursunkhanova	2.322 -\ncap:45	680
341	Spring	2026	13S	2026-01-12	2026-04-17	T R	12:00 PM-12:50 PM	21	22	Elmira\nTursunkhanova,\nShannon Smith	2.322 -\ncap:45	681
341	Spring	2026	14L	2026-01-12	2026-04-17	M	10:30 AM-11:50 AM	43	48	Terence\nGreatrex, Elmira\nTursunkhanova	2.322 -\ncap:45	682
341	Spring	2026	15S	2026-01-12	2026-04-17	T R	01:00 PM-01:50 PM	21	22	Elmira\nTursunkhanova,\nShannon Smith	2.322 -\ncap:45	683
341	Spring	2026	17S	2026-01-12	2026-04-17	W F	11:00 AM-11:50 AM	21	22	Elmira\nTursunkhanova,\nShannon Smith	2.322 -\ncap:45	684
341	Spring	2026	19S	2026-01-12	2026-04-17	W F	12:00 PM-12:50 PM	21	22	Elmira\nTursunkhanova,\nShannon Smith	2.322 -\ncap:45	685
341	Spring	2026	32S	2026-01-12	2026-04-17	W F	10:00 AM-10:50 AM	22	22	Terence\nGreatrex, Elmira\nTursunkhanova	2.322 -\ncap:45	686
342	Spring	2026	3L	2026-01-12	2026-04-17	W	11:00 AM-11:50 AM	40	44	Joohee Hong,\nDariga\nAkhmetova	2.302 -\ncap:78	687
342	Spring	2026	4L	2026-01-12	2026-04-17	W	09:00 AM-09:50 AM	40	44	Joohee Hong,\nDariga\nAkhmetova	2.302 -\ncap:78	688
342	Spring	2026	11L	2026-01-12	2026-04-17	M	02:00 PM-02:50 PM	42	44	Joohee Hong,\nMaksim Kozlov	2.507 -\ncap:73	708
342	Spring	2026	14L	2026-01-12	2026-04-17	M	03:00 PM-03:50 PM	40	44	Joohee Hong,\nMaksim Kozlov	2.507 -\ncap:73	709
342	Spring	2026	16L	2026-01-12	2026-04-17	M	10:00 AM-10:50 AM	42	44	Joohee Hong	2.302 -\ncap:78	696
342	Spring	2026	5S	2026-01-12	2026-04-17	T	12:00 PM-12:50 PM	19	22	Joohee Hong,\nDariga\nAkhmetova	2.519 -\ncap:24	711
342	Spring	2026	6S	2026-01-12	2026-04-17	T	09:00 AM-09:50 AM	20	22	Joohee Hong,\nDariga\nAkhmetova	2.519 -\ncap:24	690
342	Spring	2026	10S	2026-01-12	2026-04-17	T	10:00 AM-10:50 AM	20	22	Joohee Hong,\nDariga\nAkhmetova	2.519 -\ncap:24	694
342	Spring	2026	31S	2026-01-12	2026-04-17	T	11:00 AM-11:50 AM	21	22	Joohee Hong,\nDariga\nAkhmetova	2.519 -\ncap:24	715
342	Spring	2026	2S	2026-01-12	2026-04-17	T	10:00 AM-10:50 AM	18	22	Joohee Hong,\nRustem Iskakov	2.522a -\ncap:23	730
342	Spring	2026	4S	2026-01-12	2026-04-17	T	09:00 AM-09:50 AM	18	22	Joohee Hong,\nRustem Iskakov	2.522a -\ncap:23	731
342	Spring	2026	7S	2026-01-12	2026-04-17	R	11:00 AM-11:50 AM	21	22	Azamat\nOrazbayev,\nJoohee Hong	2.522a -\ncap:23	691
342	Spring	2026	9S	2026-01-12	2026-04-17	R	12:00 PM-12:50 PM	21	22	Azamat\nOrazbayev,\nJoohee Hong	2.522a -\ncap:23	693
342	Spring	2026	15S	2026-01-12	2026-04-17	T	12:00 PM-12:50 PM	21	22	Joohee Hong,\nRustem Iskakov	2.522a -\ncap:23	695
342	Spring	2026	17S	2026-01-12	2026-04-17	T	11:00 AM-11:50 AM	21	22	Joohee Hong,\nRustem Iskakov	2.522a -\ncap:23	697
342	Spring	2026	8L	2026-01-12	2026-04-17	W	10:00 AM-10:50 AM	41	44	Galymzhan\nKoishiyev,\nJoohee Hong	2.507 -\ncap:73	712
342	Spring	2026	12L	2026-01-12	2026-04-17	M	10:00 AM-10:50 AM	42	44	Galymzhan\nKoishiyev,\nJoohee Hong	2.507 -\ncap:73	713
342	Spring	2026	5L	2026-01-12	2026-04-17	M	02:00 PM-02:50 PM	42	44	Azamat\nOrazbayev,\nJoohee Hong	2.322 -\ncap:45	707
342	Spring	2026	20S	2026-01-12	2026-04-17	T	09:00 AM-09:50 AM	21	22	Azamat\nOrazbayev,\nJoohee Hong	2.322 -\ncap:45	732
342	Spring	2026	2L	2026-01-12	2026-04-17	M W	10:00 AM-10:50 AM	36	44	Joohee Hong,\nRustem Iskakov	2.327 -\ncap:88	722
342	Spring	2026	7L	2026-01-12	2026-04-17	W	11:00 AM-11:50 AM	42	44	Kairat Ismailov,\nJoohee Hong	2.327 -\ncap:88	723
342	Spring	2026	9L	2026-01-12	2026-04-17	M	11:00 AM-11:50 AM	42	44	Joohee Hong,\nRustem Iskakov	2.327 -\ncap:88	724
342	Spring	2026	10L	2026-01-12	2026-04-17	W	09:00 AM-09:50 AM	43	44	Kairat Ismailov,\nJoohee Hong	2.327 -\ncap:88	725
342	Spring	2026	22S	2026-01-12	2026-04-17	T R	10:00 AM-10:50 AM	19	22	Joohee Hong,\nJonathan\nDallmann	2.527 -\ncap:24	700
342	Spring	2026	24S	2026-01-12	2026-04-17	T R	09:00 AM-09:50 AM	21	22	Joohee Hong,\nJonathan\nDallmann	2.527 -\ncap:24	702
342	Spring	2026	8S	2026-01-12	2026-04-17	T R	02:00 PM-02:50 PM	21	22	Joohee Hong,\nMarc\nFormichella	2.141 -\ncap:28	692
342	Spring	2026	13L	2026-01-12	2026-04-17	W	09:00 AM-09:50 AM	43	44	Azamat\nOrazbayev,\nJoohee Hong	2.322 -\ncap:45	734
343	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	80	90	George Mathews	Red Hall\n1022 (C3) -\ncap:265	735
344	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	137	200	George Mathews	Red Hall\n1022 (C3) -\ncap:265	736
345	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	11	15	Milovan Fustic	6.327 -\ncap:10	737
346	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	12	15	Davit Vasilyan	6.327 -\ncap:10	738
347	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	10	25	Kamal Regmi	6.327 -\ncap:10	739
348	Spring	2026	1L	2026-01-12	2026-04-24	M W	02:00 PM-03:15 PM	13	20	Mahmoud Leila	6.527 -\ncap:4	740
349	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	11	20	Sebastianus\nWillem Josef Den\nBrok	6.427 -\ncap:24	741
350	Spring	2026	1L	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	21	20	Emil Bayramov	6.302 -\ncap:44	742
352	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-03:50 PM	22	20	Emil Bayramov	6.302 -\ncap:44	744
353	Spring	2026	1IS	2026-01-12	2026-04-24	M W F	06:00 PM-06:50 PM	12	15	Sebastianus\nWillem Josef Den\nBrok	6.105 -\ncap:64	745
354	Spring	2026	1L	2026-01-12	2026-04-24	F	12:00 PM-02:30 PM	4	15	Marzhan\nBaigaliyeva	6.422 -\ncap:28	746
355	Spring	2026	1L	2026-01-12	2026-04-24	R	05:00 PM-06:50 PM	9	15	Sebastianus\nWillem Josef Den\nBrok	TBA - cap:0	747
356	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	9	15	Kamal Regmi	6.327 -\ncap:10	748
357	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	9	15	Medet Junussov	6.419 -\ncap:24	749
358	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	9	15	Jovid Aminov	6.327 -\ncap:10	750
359	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	6	15	Sebastianus\nWillem Josef Den\nBrok	\N	751
360	Spring	2026	1RT	2026-01-12	2026-04-24	T R	06:00 PM-07:30 PM	6	10	Sebastianus\nWillem Josef Den\nBrok	6.105 -\ncap:64	752
361	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	11:00 AM-11:50 AM	28	30	Florian Kuechler	8.305 -\ncap:30	753
362	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	01:00 PM-01:50 PM	11	24	Florian Kuechler	8.508 -\ncap:24	754
363	Spring	2026	1L	2026-03-10	2026-05-08	M T W R F	09:30 AM-12:30 PM	20	26	Mirat Akshalov,\nJaehyeon Kim	(C3) 3038 -\ncap:39	755
364	Spring	2026	1L	2026-01-12	2026-03-06	M T W R F	09:30 AM-12:30 PM	20	26	Mirat Akshalov,\nBektemir\nYsmailov	(C3) 3016 -\ncap:62	756
365	Spring	2026	1L	2026-01-12	2026-03-02	M T W R F	01:30 PM-04:30 PM	20	26	Mirat Akshalov,\nFrancesco\nRocciolo	(C3) 3016 -\ncap:62	757
366	Spring	2026	1S	2026-01-12	2026-04-24	T	01:00 PM-04:00 PM	3	4	Mirat Akshalov,\nJaehyeon Kim	(C3) 3037 -\ncap:39	758
367	Spring	2026	1S	2026-01-12	2026-04-24	F	01:00 PM-04:00 PM	3	4	Mirat Akshalov,\nMustafa Karatas	(C3) 3037 -\ncap:39	759
368	Spring	2026	1L	2026-01-12	2026-04-24	F	01:00 PM-04:00 PM	4	4	Mirat Akshalov,\nJaehyeon Kim	(C3) 3037 -\ncap:39	760
369	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	2	4	Mirat Akshalov,\nDoron Israeli	\N	761
6	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	600	732	Rozaliya\nGaripova	\N	762
6	Spring	2026	4S	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	14	20	Diana\nKopbayeva	9.105 -\ncap:68	763
6	Spring	2026	5S	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	17	20	Diana\nKopbayeva	9.105 -\ncap:68	764
6	Spring	2026	7S	2026-01-12	2026-04-24	M	03:00 PM-03:50 PM	23	24	Nikolay\nTsyrempilov	9.105 -\ncap:68	765
6	Spring	2026	8S	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	24	24	Nikolay\nTsyrempilov	9.105 -\ncap:68	766
6	Spring	2026	9S	2026-01-12	2026-04-24	M	05:00 PM-05:50 PM	24	24	Nikolay\nTsyrempilov	9.105 -\ncap:68	767
6	Spring	2026	10S	2026-01-12	2026-04-24	W	09:00 AM-09:50 AM	24	24	Mikhail Akulov	9.105 -\ncap:68	768
6	Spring	2026	11S	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	24	24	Mikhail Akulov	9.105 -\ncap:68	769
6	Spring	2026	12S	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	24	24	Mikhail Akulov	9.105 -\ncap:68	770
6	Spring	2026	13S	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	16	20	Diana\nKopbayeva	9.105 -\ncap:68	771
6	Spring	2026	14S	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	10	20	Diana\nKopbayeva	9.105 -\ncap:68	772
6	Spring	2026	16S	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	24	24	Mollie Arbuthnot	9.105 -\ncap:68	773
6	Spring	2026	17S	2026-01-12	2026-04-24	W	04:00 PM-04:50 PM	24	24	Mollie Arbuthnot	9.105 -\ncap:68	774
6	Spring	2026	19S	2026-01-12	2026-04-24	W	05:00 PM-05:50 PM	23	24	Mollie Arbuthnot	9.105 -\ncap:68	775
6	Spring	2026	21S	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	21	24	Diana\nKopbayeva	9.105 -\ncap:68	776
6	Spring	2026	22S	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	22	24	Diana\nKopbayeva	9.105 -\ncap:68	777
6	Spring	2026	24S	2026-01-12	2026-04-24	F	01:00 PM-01:50 PM	16	20	Diana\nKopbayeva	9.105 -\ncap:68	778
6	Spring	2026	25S	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	13	20	Diana\nKopbayeva	9.105 -\ncap:68	779
6	Spring	2026	1S	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	24	24	Mikhail Akulov	8.154 -\ncap:56	780
6	Spring	2026	2S	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	22	24	Mikhail Akulov	8.154 -\ncap:56	781
6	Spring	2026	3S	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	24	24	Mikhail Akulov	8.154 -\ncap:56	782
6	Spring	2026	26S	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	21	24	Meiramgul\nKussainova	8.422A -\ncap:32	783
6	Spring	2026	27S	2026-01-12	2026-04-24	F	01:00 PM-01:50 PM	23	24	Meiramgul\nKussainova	8.422A -\ncap:32	784
6	Spring	2026	28S	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	24	24	Meiramgul\nKussainova	8.422A -\ncap:32	785
6	Spring	2026	29S	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	20	20	Aybike Tezel	9.204 -\ncap:38	786
6	Spring	2026	30S	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	20	20	Aybike Tezel	9.204 -\ncap:38	787
6	Spring	2026	31S	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	19	20	Aybike Tezel	9.204 -\ncap:38	788
6	Spring	2026	32S	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	20	20	Aybike Tezel	9.204 -\ncap:38	789
6	Spring	2026	33S	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	20	20	Aybike Tezel	9.204 -\ncap:38	790
6	Spring	2026	34S	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	20	20	Aybike Tezel	9.204 -\ncap:38	791
370	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	53	40	Di Lu	5.103 -\ncap:160	792
371	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	53	40	Di Lu	7E.529 -\ncap:95	793
372	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	30	30	Curtis Murphy	9.204 -\ncap:38	794
373	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	25	28	Aybike Tezel	9.204 -\ncap:38	795
374	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	34	28	Mollie Arbuthnot	7.210 -\ncap:54	796
375	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	28	28	Curtis Murphy	9.204 -\ncap:38	797
376	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	41	40	Halit Akarca	8.105 -\ncap:56	798
377	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	27	28	Daniel Beben	9.204 -\ncap:38	799
378	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	35	28	Jenni Lehtinen	8.322A -\ncap:32	800
379	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	13	24	Chandler Hatch	9.204 -\ncap:38	801
380	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	27	25	Mikhail Akulov	6.105 -\ncap:64	802
381	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Di Lu	\N	803
382	Spring	2026	1S	2026-01-12	2026-04-24	M W F	06:00 PM-06:50 PM	18	16	Nikolay\nTsyrempilov	9.204 -\ncap:38	804
383	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	20	20	Amanda Murphy	8.322A -\ncap:32	805
384	Spring	2026	1S	2026-01-12	2026-04-24	F	02:00 PM-04:50 PM	9	16	Rozaliya\nGaripova	8.319 -\ncap:30	806
385	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	9	10	Curtis Murphy	\N	807
386	Spring	2026	1S	2026-01-12	2026-04-24	M W F	06:00 PM-06:50 PM	7	8	Nikolay\nTsyrempilov	9.204 -\ncap:38	808
387	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	5	4	Amanda Murphy	8.322A -\ncap:32	809
388	Spring	2026	1S	2026-01-12	2026-04-24	F	02:00 PM-04:50 PM	1	6	Rozaliya\nGaripova	8.319 -\ncap:30	810
389	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	6	2	Amanda Murphy	8.322A -\ncap:32	811
390	Spring	2026	3L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	12	16	Gulzhamilya\nShalabayeva	8.319 -\ncap:30	812
390	Spring	2026	7L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	16	16	Aidar Balabekov	8.308 -\ncap:24	813
390	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	17	16	Aidar Balabekov	8.141 -\ncap:24	814
390	Spring	2026	2L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	17	16	Aidar Balabekov	8.141 -\ncap:24	815
390	Spring	2026	4L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	15	16	Kulyan Kopesh	8.141 -\ncap:24	816
390	Spring	2026	5L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	16	16	Kulyan Kopesh	8.141 -\ncap:24	817
390	Spring	2026	6L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	13	16	Raushan\nMyrzabekova	8.141 -\ncap:24	818
391	Spring	2026	6L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	16	16	Gulzhamilya\nShalabayeva	8.319 -\ncap:30	819
391	Spring	2026	8L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	15	16	Gulzhamilya\nShalabayeva	8.319 -\ncap:30	820
391	Spring	2026	7L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	16	16	Gulzhamilya\nShalabayeva	8.302 -\ncap:57	821
391	Spring	2026	10L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	15	16	Bakyt\nAkbuzauova	8.317 -\ncap:28	822
391	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	10	16	Raushan\nMyrzabekova	8.141 -\ncap:24	823
391	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	14	16	Raushan\nMyrzabekova	8.141 -\ncap:24	824
391	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	14	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	825
391	Spring	2026	4L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	13	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	826
391	Spring	2026	5L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	16	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	827
392	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	161	150	Meiramgul\nKussainova, Uli\nSchamiloglu,\nMoldiyar\nYergebekov	\N	828
392	Spring	2026	1S	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	28	25	Meiramgul\nKussainova, Uli\nSchamiloglu	7E.125/1 -\ncap:36	829
392	Spring	2026	2S	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	24	25	Uli Schamiloglu,\nMoldiyar\nYergebekov	7E.125/1 -\ncap:36	830
392	Spring	2026	3S	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	25	25	Meiramgul\nKussainova, Uli\nSchamiloglu	7E.125/1 -\ncap:36	831
392	Spring	2026	4S	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	26	25	Meiramgul\nKussainova, Uli\nSchamiloglu	7E.125/1 -\ncap:36	832
392	Spring	2026	5S	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	29	25	Uli Schamiloglu,\nMoldiyar\nYergebekov	7E.125/1 -\ncap:36	833
392	Spring	2026	6S	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	29	25	Uli Schamiloglu,\nMoldiyar\nYergebekov	7E.125/1 -\ncap:36	834
393	Spring	2026	1S	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	29	30	Meruyert\nIbrayeva	8.105 -\ncap:56	835
394	Spring	2026	4S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	29	30	Zeinep\nZhumatayeva	2.407 -\ncap:85	836
394	Spring	2026	5S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	28	30	Zeinep\nZhumatayeva	2.407 -\ncap:85	837
394	Spring	2026	2S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	35	30	Zeinekhan\nKuzekova	8.302 -\ncap:57	838
394	Spring	2026	1S	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	29	30	Samal\nAbzhanova	7E.125/1 -\ncap:36	839
394	Spring	2026	3S	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	30	30	Samal\nAbzhanova	7E.125/1 -\ncap:36	840
395	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	29	30	Zhanar\nBaiteliyeva	8.105 -\ncap:56	841
396	Spring	2026	1S	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	28	30	Mustafa Shokay	8.302 -\ncap:57	842
396	Spring	2026	2S	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	28	30	Mustafa Shokay	8.302 -\ncap:57	843
396	Spring	2026	3S	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	30	30	Mustafa Shokay	8.302 -\ncap:57	844
396	Spring	2026	4S	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	29	30	Mustafa Shokay	8.302 -\ncap:57	845
397	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	28	30	Zhanar\nAbdigapparova	8.302 -\ncap:57	846
398	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	35	30	Meiramgul\nKussainova	8.105 -\ncap:56	847
399	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	28	30	Zhanar\nAbdigapparova	8.302 -\ncap:57	848
400	Spring	2026	2L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	29	30	Kulyan Kopesh	8.327 -\ncap:58	849
400	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	30	30	Kulyan Kopesh	8.105 -\ncap:56	850
401	Spring	2026	1S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	30	30	Zhazira\nAgabekova	7E.125/1 -\ncap:36	851
402	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	29	30	Zhazira\nAgabekova	7E.125/1 -\ncap:36	852
403	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	27	30	Yermek Adayeva	9.204 -\ncap:38	853
403	Spring	2026	2L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	28	30	Yermek Adayeva	9.204 -\ncap:38	854
403	Spring	2026	3L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	29	30	Yermek Adayeva	9.204 -\ncap:38	855
403	Spring	2026	4L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	28	30	Yermek Adayeva	9.204 -\ncap:38	856
404	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	29	30	Zhanar\nBaiteliyeva	8.105 -\ncap:56	857
405	Spring	2026	1S	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	30	30	Sarkyt Aliszhan	7E.125/1 -\ncap:36	858
34	Spring	2026	1S	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	33	30	Zeinekhan\nKuzekova	8.302 -\ncap:57	859
406	Spring	2026	1S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	30	30	Sarkyt Aliszhan	7E.125/1 -\ncap:36	860
407	Spring	2026	1S	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	29	30	Zeinep\nZhumatayeva	2.407 -\ncap:85	861
408	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	29	30	Samal\nAbzhanova	6.507 -\ncap:72	862
408	Spring	2026	2L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	31	30	Samal\nAbzhanova	6.507 -\ncap:72	863
409	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	41	40	Moldiyar\nYergebekov	8.105 -\ncap:56	864
410	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	12	20	Aigul Ismakova	8.140 -\ncap:24	865
411	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	8	20	Aigul Ismakova	8.140 -\ncap:24	866
412	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	7	16	Raushan\nMyrzabekova	8.141 -\ncap:24	867
413	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	09:00 AM-09:50 AM	16	24	Joomi Kong	8.317 -\ncap:28	868
413	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	10:00 AM-10:50 AM	23	24	Joomi Kong	8.317 -\ncap:28	869
414	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	11:00 AM-11:50 AM	23	24	Joomi Kong	8.317 -\ncap:28	870
415	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	98	100	Olga Potanina	5.103 -\ncap:160	871
416	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	29	28	Olga Potanina	8.322A -\ncap:32	872
417	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	27	28	Emad Mohamed	8.322A -\ncap:32	873
418	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	12	28	Andrey\nFilchenko	8.322A -\ncap:32	874
419	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	31	28	Clinton Parker	8.327 -\ncap:58	875
420	Spring	2026	1Wsh	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Andrey\nFilchenko	\N	876
420	Spring	2026	2Wsh	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Florian Kuechler	\N	877
421	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	10	20	Benjamin Brosig	8.319 -\ncap:30	878
422	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	21	26	Clinton Parker	8.307 -\ncap:55	879
423	Spring	2026	1S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	9	26	Benjamin Brosig	8.422A -\ncap:32	880
424	Spring	2026	1S	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	13	20	Gabriel\nMcGuire,\nNikolay\nMikhailov	8.322A -\ncap:32	881
425	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	9	20	Emad Mohamed	8.322A -\ncap:32	882
426	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	23	24	Eva-Marie\nDubuisson	8.322A -\ncap:32	883
427	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	4	5	Benjamin Brosig	\N	884
428	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	1	4	Benjamin Brosig	8.319 -\ncap:30	885
429	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	1	2	Emad Mohamed	8.322A -\ncap:32	886
430	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	2	2	Eva-Marie\nDubuisson	8.322A -\ncap:32	887
431	Spring	2026	1Lb	2026-01-12	2026-04-24	M	11:00 AM-12:45 PM	40	40	Didier Talamona	TBA - cap:0	888
431	Spring	2026	2Lb	2026-01-12	2026-04-24	F	03:00 PM-04:45 PM	33	40	Didier Talamona	TBA - cap:0	889
431	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	73	80	Didier Talamona	3E.220 -\ncap:90	890
432	Spring	2026	1T	2026-01-12	2026-04-24	M	02:00 PM-02:45 PM	36	40	Md. Hazrat Ali	3.302 -\ncap:76	891
432	Spring	2026	2T	2026-01-12	2026-04-24	W	02:00 PM-02:45 PM	40	40	Md. Hazrat Ali	3.302 -\ncap:76	892
432	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	76	80	Md. Hazrat Ali	3E.220 -\ncap:90	893
433	Spring	2026	1Lb	2026-01-12	2026-04-24	W	11:00 AM-01:45 PM	59	70	Sherif Gouda,\nDmitriy Sizov	3.323 -\ncap:64	894
433	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	59	70	Sherif Gouda	3E.224 -\ncap:90	895
433	Spring	2026	1T	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	59	70	Sherif Gouda	3E.224 -\ncap:90	896
434	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	23	35	Sergey Spotar	3.415 -\ncap:42	897
434	Spring	2026	1T	2026-01-12	2026-04-24	F	04:00 PM-04:50 PM	23	35	Sergey Spotar	3.415 -\ncap:42	898
434	Spring	2026	1Lb	2026-01-12	2026-04-24	W	03:00 PM-05:45 PM	23	35	Sergey Spotar	3E.324 -\ncap:25	899
435	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	58	70	Konstantinos\nKostas	3E.224 -\ncap:90	900
435	Spring	2026	1Lb	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	58	70	Konstantinos\nKostas	3E.224 -\ncap:90	901
436	Spring	2026	2T	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Didier Talamona	\N	902
436	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	25	35	Didier Talamona	3.316 -\ncap:41	903
436	Spring	2026	1Lb	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	25	35	Didier Talamona	3.407 -\ncap:40	904
436	Spring	2026	1T	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	24	35	Didier Talamona	3.407 -\ncap:40	905
437	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	40	35	Altay\nZhakatayev	3.309 -\ncap:40	906
437	Spring	2026	1T	2026-01-12	2026-04-24	M	03:00 PM-03:50 PM	40	35	Altay\nZhakatayev	3.407 -\ncap:40	907
437	Spring	2026	1Lb	2026-01-12	2026-04-24	M	11:00 AM-12:45 PM	40	35	Altay\nZhakatayev	3E.327 -\ncap:25	908
438	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	37	35	Amgad Salama	3.407 -\ncap:40	909
438	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	37	35	Amgad Salama	3.415 -\ncap:42	910
439	Spring	2026	1T	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	41	44	Yerbol\nSarbassov	3.316 -\ncap:41	911
439	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	41	44	Yerbol\nSarbassov	3E.221 -\ncap:50	912
440	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	33	44	Gulnur\nKalimuldina	3E.221 -\ncap:50	913
440	Spring	2026	1T	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	33	44	Gulnur\nKalimuldina	3E.221 -\ncap:50	914
441	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-03:45 PM	29	44	Gulnur\nKalimuldina	TBA - cap:0	915
441	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	29	44	Gulnur\nKalimuldina	3E.221 -\ncap:50	916
442	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	42	44	Altay\nZhakatayev	3.302 -\ncap:76	917
442	Spring	2026	1P	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	42	44	Altay\nZhakatayev	3E.221 -\ncap:50	918
443	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	16	20	Dmitriy Sizov	3.316 -\ncap:41	919
443	Spring	2026	1Lb	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	16	20	Dmitriy Sizov	3E.217 -\ncap:28	920
444	Spring	2026	2L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	40	60	Catalina Troshev	7E.222 -\ncap:95	921
444	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	57	60	Catalina Troshev	7E.329 -\ncap:95	922
1	Spring	2026	1R	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	58	57	Bibinur\nShupeyeva	7.210 -\ncap:54	923
1	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	230	228	Amin Esfahani	Orange Hall\n- cap:450	924
1	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	257	228	Andrey Melnikov	Orange Hall\n- cap:450	925
1	Spring	2026	2R	2026-01-12	2026-04-24	M	11:00 AM-11:50 AM	58	57	Catalina Troshev	8.522 -\ncap:72	926
1	Spring	2026	3R	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	64	57	Catalina Troshev	8.522 -\ncap:72	927
1	Spring	2026	4R	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	66	57	Catalina Troshev	8.522 -\ncap:72	928
1	Spring	2026	5R	2026-01-12	2026-04-24	T	01:30 PM-02:45 PM	57	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	929
1	Spring	2026	6R	2026-01-12	2026-04-24	R	01:30 PM-02:45 PM	59	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	930
1	Spring	2026	7R	2026-01-12	2026-04-24	M	03:00 PM-03:50 PM	64	57	Samat Kassabek	8.522 -\ncap:72	931
1	Spring	2026	8R	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	61	57	Samat Kassabek	8.522 -\ncap:72	932
5	Spring	2026	1R	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	54	57	Bibinur\nShupeyeva	7.210 -\ncap:54	933
5	Spring	2026	2R	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	46	57	Bibinur\nShupeyeva	7.210 -\ncap:54	934
5	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	153	200	Manat Mustafa	Orange Hall\n- cap:450	935
5	Spring	2026	2L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	202	210	Samat Kassabek	Orange Hall\n- cap:450	936
5	Spring	2026	3L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	202	210	Yerlan Amanbek	Orange Hall\n- cap:450	937
5	Spring	2026	4L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	208	210	Samat Kassabek	Orange Hall\n- cap:450	938
5	Spring	2026	3R	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	57	57	Viktor Ten	8.522 -\ncap:72	939
5	Spring	2026	4R	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	52	57	Catalina Troshev	8.522 -\ncap:72	940
5	Spring	2026	5R	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	54	57	Catalina Troshev	8.522 -\ncap:72	941
5	Spring	2026	6R	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	57	57	Samat Kassabek	8.522 -\ncap:72	942
5	Spring	2026	7R	2026-01-12	2026-04-24	T	10:30 AM-11:45 AM	55	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	943
5	Spring	2026	8R	2026-01-12	2026-04-24	W	04:00 PM-04:50 PM	55	57	Viktor Ten	8.522 -\ncap:72	944
5	Spring	2026	9R	2026-01-12	2026-04-24	R	10:30 AM-11:45 AM	54	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	945
5	Spring	2026	10R	2026-01-12	2026-04-24	F	04:00 PM-04:50 PM	52	57	Viktor Ten	8.522 -\ncap:72	946
5	Spring	2026	11R	2026-01-12	2026-04-24	T	09:00 AM-10:15 AM	37	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	947
5	Spring	2026	12R	2026-01-12	2026-04-24	R	09:00 AM-10:15 AM	39	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	948
5	Spring	2026	13R	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	42	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	949
5	Spring	2026	14R	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	56	57	Samat Kassabek	8.522 -\ncap:72	950
5	Spring	2026	15R	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	55	57	Samat Kassabek	8.522 -\ncap:72	951
10	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	67	90	Aigerim\nMadiyeva	7E.222 -\ncap:95	952
10	Spring	2026	2L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	72	90	Aigerim\nMadiyeva	7E.222 -\ncap:95	953
26	Spring	2026	1R	2026-01-12	2026-04-24	T	06:00 PM-06:50 PM	61	60	Bibinur\nShupeyeva	7E.222 -\ncap:95	954
26	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	61	60	Bibinur\nShupeyeva	7E.329 -\ncap:95	955
11	Spring	2026	1R	2026-01-12	2026-04-24	T	06:00 PM-06:50 PM	94	90	Viktor Ten	7E.329 -\ncap:95	956
11	Spring	2026	2L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	97	90	Viktor Ten	7E.329 -\ncap:95	957
11	Spring	2026	2R	2026-01-12	2026-04-24	R	06:00 PM-06:50 PM	92	90	Viktor Ten	7E.329 -\ncap:95	958
11	Spring	2026	3L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	89	90	Viktor Ten	7E.329 -\ncap:95	959
445	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	69	60	Achenef\nTesfahun	7E.222 -\ncap:95	960
445	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	60	60	Dongming Wei	7E.222 -\ncap:95	961
446	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	45	60	Manat Mustafa	7E.222 -\ncap:95	962
447	Spring	2026	1L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	70	70	Eunghyun Lee	7E.329 -\ncap:95	963
448	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	57	60	Bibinur\nShupeyeva	7E.222 -\ncap:95	964
18	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	54	54	Zhansaya\nTleuliyeva	7.210 -\ncap:54	965
18	Spring	2026	2L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	89	96	Zhansaya\nTleuliyeva	7E.222 -\ncap:95	966
18	Spring	2026	3L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	79	90	Zhansaya\nTleuliyeva	7E.222 -\ncap:95	967
18	Spring	2026	4L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	45	60	Aigerim\nMadiyeva	7E.329 -\ncap:95	968
28	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	55	60	Kerem Ugurlu	7E.222 -\ncap:95	969
449	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	76	75	Durvudkhan\nSuragan	7E.222 -\ncap:95	970
449	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	71	75	Durvudkhan\nSuragan	7E.329 -\ncap:95	971
450	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	21	54	Alejandro Javier\nCastro Castilla	7.210 -\ncap:54	972
450	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	57	60	Yerlan Amanbek	7E.329 -\ncap:95	973
451	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	72	60	Adilbek Kairzhan	7E.222 -\ncap:95	974
451	Spring	2026	2L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	68	60	Adilbek Kairzhan	7E.329 -\ncap:95	975
452	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	55	55	Adilet Otemissov	5E.438 -\ncap:82	976
453	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	56	55	Adilet Otemissov	7.210 -\ncap:54	977
454	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	64	70	Rustem\nTakhanov	7E.329 -\ncap:95	978
455	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	68	60	Dongming Wei	7E.329 -\ncap:95	979
456	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	72	55	Piotr Sebastian\nSkrzypacz	7E.329 -\ncap:95	980
457	Spring	2026	1L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	54	55	Kerem Ugurlu	7.210 -\ncap:54	981
458	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	10	55	Zhibek\nKadyrsizova	7.210 -\ncap:54	982
459	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	29	55	Eunghyun Lee	7.210 -\ncap:54	983
25	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	43	70	Zhibek\nKadyrsizova	7E.329 -\ncap:95	984
460	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	18	60	Amin Esfahani	7E.329 -\ncap:95	985
461	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	46	60	Andrey Melnikov	8.522 -\ncap:72	986
462	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	46	55	Achenef\nTesfahun	7.210 -\ncap:54	987
463	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	3	10	Alejandro Javier\nCastro Castilla	7E.220 -\ncap:56	988
464	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	5	5	Alejandro Javier\nCastro Castilla	7E.220 -\ncap:56	989
465	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	2	5	Alejandro Javier\nCastro Castilla	7E.220 -\ncap:56	990
466	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Eunghyun Lee	\N	991
467	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	2	1	Piotr Sebastian\nSkrzypacz	\N	992
468	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	35	30	Manat Mustafa	\N	993
469	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	18	30	Rustem\nTakhanov	7.210 -\ncap:54	994
470	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	13	20	Piotr Sebastian\nSkrzypacz	7.210 -\ncap:54	995
471	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	9	20	Alejandro Javier\nCastro Castilla	7E.220 -\ncap:56	996
472	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	15	20	Manat Mustafa	\N	997
473	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	12	20	Manat Mustafa	\N	998
474	Spring	2026	1L	2026-01-12	2026-04-24	M	02:00 PM-03:00 PM	18	25	Alejandro Javier\nCastro Castilla	7.507 -\ncap:48	999
475	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	4	10	Alejandro Javier\nCastro Castilla	7E.220 -\ncap:56	1000
476	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	3	10	Piotr Sebastian\nSkrzypacz	7.210 -\ncap:54	1001
477	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	7	10	Tolga Etgu	7E.220 -\ncap:56	1002
478	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	5	10	Alejandro Javier\nCastro Castilla	\N	1003
480	Spring	2026	1L	2026-01-12	2026-02-12	M W F	01:30 PM-04:30 PM	33	40	Zhanar\nSmailova,\nFrancesco\nRocciolo	(C3) 2002 -\ncap:66	1005
480	Spring	2026	2L	2026-01-10	2026-02-15	S S	09:00 AM-05:30 PM	20	22	Gerrit Post,\nMirat Akshalov,\nZhanerke\nKozybayeva	(C3) 3016 -\ncap:62	1006
481	Spring	2026	1L	2026-02-16	2026-03-26	M W F	09:30 AM-12:30 PM	34	40	Mirat Akshalov,\nDavid Reinhard	(C3) 2004 -\ncap:67	1007
482	Spring	2026	1L	2026-02-16	2026-03-27	M W F	01:30 PM-04:30 PM	33	40	Shumaila\nYousafzai,\nZhanar Smailova	(C3) 2004 -\ncap:67	1008
482	Spring	2026	2L	2026-03-07	2026-04-19	S S	08:30 AM-05:30 PM	21	22	Mirat Akshalov,\nMustafa Karatas,\nDiyas Takenov	(C3) 3016 -\ncap:62	1009
483	Spring	2026	1L	2026-03-30	2026-04-27	M W F	09:30 AM-12:30 PM	33	40	Jiyang Dong,\nZhanar Smailova	(C3) 3015 -\ncap:60	1010
483	Spring	2026	2L	2026-03-07	2026-04-19	S S	08:30 AM-05:30 PM	21	22	Mirat Akshalov,\nJiyang Dong	(C3) 3038 -\ncap:39	1011
484	Spring	2026	1L	2026-03-30	2026-04-29	M W F	01:30 PM-04:30 PM	33	40	Venkat\nSubramanian,\nZhasmin\nYersaiyn	(C3) 2002 -\ncap:66	1012
484	Spring	2026	2L	2026-01-12	2026-05-11	S	08:30 AM-05:00 PM	21	20	Zhanerke\nKozybayeva,\nAnjan Ghosh	(C3)\n3030/3031 -\ncap:46	1013
485	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	16	20	Chang-Keun Lim	\N	1014
486	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	13	20	Cevat Erisken	\N	1015
487	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	17	30	Cevat Erisken	3.407 -\ncap:40	1016
488	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	16	30	Lyazzat\nMukhangaliyeva	3.407 -\ncap:40	1017
489	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	19	20	Chang-Keun Lim	3.407 -\ncap:40	1018
490	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	13	18	Jong Kim,\nBakhyt\nAubakirova	3.303 -\ncap:32	1019
491	Spring	2026	1P	2026-01-12	2026-04-24	F	01:30 PM-02:45 PM	17	18	Jong Kim,\nBakhyt\nAubakirova	3.303 -\ncap:32	1020
492	Spring	2026	1L	2026-01-12	2026-04-24	M W	02:00 PM-03:15 PM	6	10	Dichuan Zhang	3.303 -\ncap:32	1021
493	Spring	2026	1L	2026-01-12	2026-04-24	M W	11:00 AM-12:15 PM	14	10	Sung Moon	3.309 -\ncap:40	1022
494	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	8	10	Woojin Lee	3.316 -\ncap:41	1023
495	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	15	18	Abid Nadeem	3.303 -\ncap:32	1024
496	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	17	20	Chang-Keun Lim	\N	1025
497	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	14	20	Nurxat Nuraje,\nChang-Keun Lim	\N	1026
498	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	18	20	Sergey Spotar	3.316 -\ncap:41	1027
498	Spring	2026	1CLb	2026-01-12	2026-04-24	W	12:00 PM-01:50 PM	18	20	Sergey Spotar	3E.227 -\ncap:28	1028
499	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	16	20	Nurxat Nuraje	3E.221 -\ncap:50	1029
500	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	18	20	Yanwei Wang	3.415 -\ncap:42	1030
501	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	21	30	Daniele Tosi	3E.221 -\ncap:50	1031
502	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	28	30	Mehdi Bagheri	\N	1032
503	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	16	30	Mehdi Bagheri	3E.224 -\ncap:90	1033
504	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	2	30	Muhammad\nAkhtar	3.416 -\ncap:46	1034
505	Spring	2026	1L	2026-01-12	2026-04-24	M W	01:30 PM-02:45 PM	16	30	Mohammad\nHashmi	3.322 -\ncap:41	1035
506	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	0	30	Muhammad\nAkhtar	3.416 -\ncap:46	1036
507	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	12	15	Mehdi Shafiee,\nAzamat\nMukhamediya	3.309 -\ncap:40	1037
508	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	1	15	Ainur\nRakhymbay,\nAresh Dadlani	3.309 -\ncap:40	1038
342	Spring	2026	30S	2026-01-12	2026-04-17	T	10:00 AM-10:50 AM	22	22	Azamat\nOrazbayev,\nJoohee Hong	2.322 -\ncap:45	733
510	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	14	30	Carlo Molardi	3.309 -\ncap:40	1040
511	Spring	2026	1L	2026-01-12	2026-04-24	W	12:00 PM-02:45 PM	15	20	Ata Akcil	6.302 -\ncap:44	1041
511	Spring	2026	1Lb	2026-01-12	2026-04-24	R	12:00 PM-01:15 PM	15	20	Ata Akcil	6.302 -\ncap:44	1042
512	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	9	12	Amoussou Coffi\nAdoko	6.419 -\ncap:24	1043
513	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	17	20	Nasser\nMadaniesfahani	6.527 -\ncap:4	1044
514	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	9	12	Saffet Yagiz	6.427 -\ncap:24	1045
515	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	9	12	Fidelis Suorineni	6.519 -\ncap:26	1046
516	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	9	12	Ali Mortazavi	6.427 -\ncap:24	1047
517	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	6	15	Sergei Sabanov	6.522 -\ncap:35	1048
518	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	11	15	Sergei Sabanov	6.522 -\ncap:35	1049
519	Spring	2026	1P	2026-01-12	2026-04-24	F	03:00 PM-04:50 PM	9	15	Amoussou Coffi\nAdoko	6.522 -\ncap:35	1050
520	Spring	2026	1L	2026-01-12	2026-04-24	W	10:00 AM-12:15 PM	8	20	Sergei Sabanov	6.522 -\ncap:35	1051
521	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	8	12	Saffet Yagiz	6.527 -\ncap:4	1052
522	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	8	12	Amoussou Coffi\nAdoko	6.519 -\ncap:26	1053
523	Spring	2026	1L	2026-01-12	2026-04-24	M W	01:00 PM-02:15 PM	8	12	Ali Mortazavi	6.427 -\ncap:24	1054
524	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	8	15	Fidelis Suorineni	6.527 -\ncap:4	1055
525	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	8	15	Zauresh\nAtakhanova	6.105 -\ncap:64	1056
526	Spring	2026	1RP	2026-01-12	2026-04-24	\N	Online/Distant	8	15	Fidelis Suorineni	\N	1057
527	Spring	2026	1IS	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	3	30	Mahmoud Leila	6.419 -\ncap:24	1058
528	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	3	10	Fidelis Suorineni	6.518 -\ncap:15	1059
529	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:00 PM-05:15 PM	3	10	Nasser\nMadaniesfahani	6.302 -\ncap:44	1060
531	Spring	2026	1P	2026-01-12	2026-04-24	W	03:00 PM-04:15 PM	15	20	Yerbol\nSarbassov	3.407 -\ncap:40	1062
532	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	17	22	Amgad Salama	3.317 -\ncap:40	1063
532	Spring	2026	1Lb	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	17	22	Amgad Salama	3E.217 -\ncap:28	1064
533	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	15	22	Sherif Gouda	3.309 -\ncap:40	1065
534	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	18	12	Yerkin Abdildin	3.303 -\ncap:32	1066
535	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	16	22	Dmitriy Sizov	3.303 -\ncap:32	1067
535	Spring	2026	1Lb	2026-01-12	2026-04-24	F	10:00 AM-12:45 PM	16	22	Dmitriy Sizov	3E.217 -\ncap:28	1068
536	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	3	12	Dmitriy Sizov	3.316 -\ncap:41	1069
536	Spring	2026	1Lb	2026-01-12	2026-04-24	M	04:00 PM-04:45 PM	3	12	Dmitriy Sizov	3E.217 -\ncap:28	1070
537	Spring	2026	1P	2026-01-13	2026-04-25	M T W R F	09:00 AM-05:00 PM	19	20	Nikolai Barlev	NUSOM\nBuilding -\ncap:0	1071
538	Spring	2026	1L	2026-01-12	2026-05-09	S	09:00 AM-12:00 PM	24	24	Peter Howie	(C3) 1010 -\ncap:70	1072
539	Spring	2026	1Wsh	2026-01-18	2026-01-18	S S	09:00 AM-05:00 PM	44	45	Lisa Lim, Aipara\nBerekeyeva	(C3) 1010 -\ncap:70	1073
540	Spring	2026	1S	2026-01-12	2026-05-09	S	05:30 PM-07:00 PM	23	23	Lisa Lim, Aipara\nBerekeyeva	(C3) 2003 -\ncap:67	1074
541	Spring	2026	1L	2026-01-12	2026-05-08	T	02:00 PM-05:00 PM	11	10	Peter Howie	(C3) 2002 -\ncap:66	1075
542	Spring	2026	1L	2026-01-12	2026-05-08	F	07:00 PM-10:00 PM	11	10	Dayashankar\nMaurya	(C3) 2005 -\ncap:38	1076
543	Spring	2026	1L	2026-01-12	2026-05-08	M	02:00 PM-05:00 PM	8	10	Asad Bokhari	(C3) 2003 -\ncap:67	1077
544	Spring	2026	1L	2026-01-12	2026-05-08	W	07:00 PM-10:00 PM	11	10	Vladimir Kozlov	(C3) 2003 -\ncap:67	1078
545	Spring	2026	1L	2026-01-12	2026-05-08	T	07:00 PM-10:00 PM	13	10	Zhanibek Arynov	(C3) 2005 -\ncap:38	1079
546	Spring	2026	1L	2026-01-12	2026-05-08	W	02:00 PM-05:00 PM	8	10	Scott Valentine	(C3) 2003 -\ncap:67	1080
547	Spring	2026	1L	2026-01-12	2026-05-08	M	07:00 PM-10:00 PM	10	10	Scott Valentine	(C3) 2005 -\ncap:38	1081
548	Spring	2026	1L	2026-01-12	2026-05-08	T	02:00 PM-05:00 PM	9	12	Zhanibek Arynov	(C3) 2008 -\ncap:37	1082
549	Spring	2026	1L	2026-01-12	2026-05-09	S	02:00 PM-05:00 PM	13	10	Simeon\nNanovsky	(C3) 2002 -\ncap:66	1083
550	Spring	2026	1L	2026-01-12	2026-05-08	M	07:00 PM-10:00 PM	7	10	Hyesong Ha	(C3) 2002 -\ncap:66	1084
551	Spring	2026	1L	2026-01-12	2026-05-08	W	02:00 PM-05:00 PM	7	10	Aliya\nAssubayeva	(C3) 2008 -\ncap:37	1085
552	Spring	2026	1L	2026-01-12	2026-05-08	M	02:00 PM-05:00 PM	11	10	Omer Baris	(C3) 2008 -\ncap:37	1086
553	Spring	2026	1L	2026-01-12	2026-05-08	R	02:00 PM-05:00 PM	7	10	Artan Karini	(C3) 2002 -\ncap:66	1087
554	Spring	2026	1L	2026-01-12	2026-05-08	T	07:00 PM-10:00 PM	19	10	Serik\nOrazgaliyev	(C3) 2008 -\ncap:37	1088
555	Spring	2026	1L	2026-01-12	2026-05-09	S	02:00 PM-05:00 PM	14	10	Aliya\nAssubayeva	(C3) 2005 -\ncap:38	1089
556	Spring	2026	1L	2026-01-12	2026-05-08	R	07:00 PM-10:00 PM	9	10	Asad Bokhari	(C3) 2008 -\ncap:37	1090
557	Spring	2026	1L	2026-01-12	2026-05-08	W	09:00 AM-12:00 PM	25	25	Omer Baris	(C3) 2008 -\ncap:37	1091
558	Spring	2026	1L	2026-01-12	2026-05-08	M	09:00 AM-12:00 PM	25	25	Vladimir Kozlov	(C3) 2002 -\ncap:66	1092
559	Spring	2026	1L	2026-01-12	2026-05-08	T	09:00 AM-12:00 PM	26	25	Artan Karini	(C3) 2002 -\ncap:66	1093
560	Spring	2026	1L	2026-01-12	2026-05-08	R	09:00 AM-10:30 AM	47	47	Lisa Lim, Aipara\nBerekeyeva	(C3) 2003 -\ncap:67	1094
561	Spring	2026	1L	2026-01-12	2026-05-08	R	10:30 AM-12:00 PM	25	25	Lisa Lim, Aipara\nBerekeyeva	(C3) 2003 -\ncap:67	1095
562	Spring	2026	1IS	2026-01-12	2026-04-24	M T W R F	09:00 AM-12:00 PM	19	19	Mohamad\nAljofan	NUSOM\nBuilding -\ncap:0	1096
563	Spring	2026	1L	2026-01-12	2026-04-24	W	09:00 AM-12:00 PM	28	30	Agata Natasza\nBurska	NUSOM\nBuilding -\ncap:0	1097
564	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-05:00 PM	27	30	Denis Bulanin,\nMarina\nKriajevskaia,\nKamilya Kokabi,\nLarisa Lezina	NUSOM\nBuilding -\ncap:0	1098
565	Spring	2026	1L	2026-01-12	2026-04-24	W	02:00 PM-05:00 PM	3	30	Srinivasa Bolla,\nYeltay\nRakhmanov	NUSOM\nBuilding -\ncap:0	1099
566	Spring	2026	1L	2026-01-12	2026-04-24	F	02:00 PM-05:00 PM	3	30	Yeltay\nRakhmanov	NUSOM\nBuilding -\ncap:0	1100
567	Spring	2026	1L	2026-01-12	2026-04-24	M	09:00 AM-12:00 PM	5	30	Mohamad\nAljofan, Vladimir\nSurov	NUSOM\nBuilding -\ncap:0	1101
351	Spring	2026	1L	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	12	20	Marzhan\nBaigaliyeva	6.519 -\ncap:26	743
568	Spring	2026	1L	2026-01-12	2026-04-24	F	09:00 AM-12:00 PM	5	30	Mohamad\nAljofan, Assem\nZhakupova	NUSOM\nBuilding -\ncap:0	1102
569	Spring	2026	1L	2026-01-12	2026-04-24	M	09:00 AM-12:00 PM	19	30	Syed Hani\nHassan Abidi	NUSOM\nBuilding -\ncap:0	1103
570	Spring	2026	1L	2026-01-12	2026-04-24	W	01:00 PM-04:00 PM	21	30	Dieter\nRiethmacher,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	1104
571	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-04:00 PM	24	30	Nikolai Barlev	NUSOM\nBuilding -\ncap:0	1105
572	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-04:00 PM	3	30	Syed Ali, Yeltay\nRakhmanov	NUSOM\nBuilding -\ncap:0	1106
573	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	21	30	Azamat\nMukhamediya	3.302 -\ncap:76	1107
573	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	23	41	Saltanat\nAkhmadi	3.309 -\ncap:40	1108
573	Spring	2026	2L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	56	66	Jorge Ona\nRuales	online -\ncap:0	1109
574	Spring	2026	5L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	12	24	Olga Campbell-\nThomson	3.316 -\ncap:41	1110
574	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	12	24	Bakhtiar\nNaghdipour	7.246 -\ncap:48	1111
574	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	19	24	Bakhtiar\nNaghdipour	3.407 -\ncap:40	1112
574	Spring	2026	4L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	20	24	Yamen Rahvan	3.407 -\ncap:40	1113
575	Spring	2026	1L	2026-01-12	2026-03-04	M T W R F	09:30 AM-12:30 PM	20	26	Mirat Akshalov,\nTom Vinaimont	(C3) 3038 -\ncap:39	1114
576	Spring	2026	1L	2026-03-10	2026-05-04	M T W R F	09:30 AM-12:30 PM	20	26	Mirat Akshalov,\nTom Vinaimont	(C3) 3016 -\ncap:62	1115
577	Spring	2026	1L	2026-03-10	2026-05-06	M T W R F	01:30 PM-04:30 PM	20	26	Mirat Akshalov,\nBektemir\nYsmailov	(C3) 3016 -\ncap:62	1116
578	Spring	2026	1Wsh	2026-01-12	2026-05-08	M T W R F	01:30 PM-04:30 PM	20	22	Tom Vinaimont,\nZhanar Smailova	(C3) 3015 -\ncap:60	1117
579	Spring	2026	1L	2026-01-12	2026-04-23	M	02:00 PM-05:00 PM	10	10	Syed Ali, Yeltay\nRakhmanov	NUSOM\nBuilding -\ncap:0	1118
580	Spring	2026	1RT	2026-01-12	2026-04-24	T	02:00 PM-05:00 PM	10	10	Syed Ali, Yeltay\nRakhmanov,\nSyed Hani\nHassan Abidi	NUSOM\nBuilding -\ncap:0	1119
581	Spring	2026	1P	2026-01-12	2026-05-08	S	01:00 PM-02:15 PM	20	50	Jonas Cruz	NUSOM\nBuilding -\ncap:0	1120
582	Spring	2026	1P	2026-01-12	2026-05-08	S	09:00 AM-10:15 AM	20	50	Joseph Almazan	NUSOM\nBuilding -\ncap:0	1121
583	Spring	2026	1P	2026-01-12	2026-05-08	S	10:30 AM-11:45 AM	20	50	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	1122
584	Spring	2026	1P	2026-01-12	2026-05-08	S	02:30 PM-03:45 PM	20	50	Paolo Colet	NUSOM\nBuilding -\ncap:0	1123
585	Spring	2026	1P	2026-01-12	2026-05-08	F S	04:00 PM-05:15 PM	20	50	Paolo Colet,\nAnargul\nKuntuganova,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	1124
586	Spring	2026	1L	2026-01-12	2026-04-24	M T	12:45 PM-02:00 PM	5	5	Nancy Stitt,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	1125
587	Spring	2026	1L	2026-01-12	2026-04-24	M	10:00 AM-12:10 PM	42	42	Nancy Stitt,\nAssem\nZhakupova	NUSOM\nBuilding -\ncap:0	1126
588	Spring	2026	1L	2026-01-12	2026-04-24	T	09:30 AM-12:30 PM	42	42	Nancy Stitt,\nYesbolat Sakko	NUSOM\nBuilding -\ncap:0	1127
589	Spring	2026	1L	2026-01-12	2026-04-24	W	09:30 AM-12:30 PM	42	42	Joseph Almazan	NUSOM\nBuilding -\ncap:0	1128
590	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:30 PM-02:40 PM	42	42	Paolo Colet	NUSOM\nBuilding -\ncap:0	1129
591	Spring	2026	1ClinPract	2026-01-12	2026-04-24	W R	08:00 AM-03:50 PM	5	5	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	1130
591	Spring	2026	1L	2026-01-12	2026-04-24	M T	09:00 AM-12:00 PM	5	5	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	1131
592	Spring	2026	1ClinPract	2026-01-12	2026-04-24	F	08:00 AM-03:50 PM	5	5	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	1132
592	Spring	2026	1L	2026-01-12	2026-04-24	M T	02:15 PM-03:45 PM	5	5	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	1133
593	Spring	2026	1L	2026-01-12	2026-04-24	M W	05:00 PM-05:50 PM	5	5	Nancy Stitt	NUSOM\nBuilding -\ncap:0	1134
594	Spring	2026	1L	2026-01-12	2026-04-24	W	10:00 AM-12:10 PM	35	35	Nancy Stitt,\nAnargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	1135
595	Spring	2026	1L	2026-01-12	2026-04-24	M	10:00 AM-12:10 PM	35	35	Nancy Stitt,\nAnargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	1136
596	Spring	2026	1L	2026-01-12	2026-04-24	R	09:30 AM-12:30 PM	35	35	Nancy Stitt	NUSOM\nBuilding -\ncap:0	1137
597	Spring	2026	1L	2026-01-12	2026-04-24	T	10:00 AM-12:10 PM	35	35	Paolo Colet	NUSOM\nBuilding -\ncap:0	1138
598	Spring	2026	1ClinPract	2026-01-12	2026-04-24	T R F	08:00 AM-01:00 PM	3	3	Paolo Colet,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	1139
598	Spring	2026	1L	2026-01-12	2026-04-24	W	10:00 AM-12:00 PM	3	3	Paolo Colet,\nAnargul\nKuntuganova,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	1140
599	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-03:50 PM	3	3	Jonas Cruz	NUSOM\nBuilding -\ncap:0	1141
600	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:00 PM-02:15 PM	141	150	Jeanette Kunz\nHalder	NUSOM\nBuilding -\ncap:0	1142
600	Spring	2026	1Lb	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	22	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	1143
600	Spring	2026	2Lb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	40	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	1144
600	Spring	2026	3Lb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	40	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	1145
600	Spring	2026	4Lb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	39	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	1146
601	Spring	2026	1P	2026-01-12	2026-04-24	M W	09:00 AM-01:50 PM	50	50	Larisa Lezina	NUSOM\nBuilding -\ncap:0	1147
602	Spring	2026	1L	2026-01-05	2026-02-06	M T W R F	09:00 AM-12:00 PM	30	31	Matthew\nNaanlep Tanko	NUSOM\nBuilding -\ncap:0	1148
603	Spring	2026	1L	2026-02-09	2026-03-11	M T W R F	09:00 AM-12:00 PM	30	31	Denis Bulanin,\nNikolai Barlev	NUSOM\nBuilding -\ncap:0	1149
604	Spring	2026	1L	2026-03-12	2026-04-25	M T W R F	09:00 AM-12:00 PM	31	32	Sanja Terzic,\nSyed Hani\nHassan Abidi	NUSOM\nBuilding -\ncap:0	1150
605	Spring	2026	1L	2025-10-14	2026-03-17	T	01:00 PM-05:00 PM	28	31	Vitaliy Sazonov	NUSOM\nBuilding -\ncap:0	1151
606	Spring	2026	1L	2026-01-05	2026-05-04	M	01:00 PM-04:00 PM	28	31	Alessandra\nClementi,\nLyazzat\nToleubekova	NUSOM\nBuilding -\ncap:0	1152
607	Spring	2026	1L	2026-01-07	2026-05-06	W	01:00 PM-04:00 PM	28	31	Yesbolat Sakko	NUSOM\nBuilding -\ncap:0	1153
608	Spring	2026	1L	2026-03-31	2026-04-28	T	01:00 PM-04:30 PM	28	31	Vitaliy Sazonov	NUSOM\nBuilding -\ncap:0	1154
609	Spring	2026	1L	2026-01-12	2026-04-24	F	09:30 AM-12:30 PM	44	50	Mirat Akshalov,\nNarendra Singh	(C3) 1009 -\ncap:70	1155
610	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	02:00 PM-02:50 PM	25	24	Marzieh Sadat\nRazavi	8.508 -\ncap:24	1156
610	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	12:00 PM-12:50 PM	24	24	Marzieh Sadat\nRazavi	8.508 -\ncap:24	1157
611	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	03:00 PM-03:50 PM	5	24	Marzieh Sadat\nRazavi	8.508 -\ncap:24	1158
612	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	18	30	Peyman\nPourafshary	6.507 -\ncap:72	1159
613	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	21	30	Irawan Sonny	6.105 -\ncap:64	1160
613	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-04:50 PM	21	30	Irawan Sonny	6.141 -\ncap:15	1161
614	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	25	30	Ali Shafiei	6.105 -\ncap:64	1162
614	Spring	2026	1Lb	2026-01-12	2026-04-24	W	01:00 PM-03:50 PM	25	30	Ali Shafiei	6.105 -\ncap:64	1163
615	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	26	30	Masoud Riazi	6.105 -\ncap:64	1164
616	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	26	30	Randy Hazlett	6.105 -\ncap:64	1165
617	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	29	30	Shams Kalam	6.507 -\ncap:72	1166
618	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	24	30	Mian Umer\nShafiq	6.422 -\ncap:28	1167
619	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	16	30	Ali Shafiei	6.302 -\ncap:44	1168
620	Spring	2026	1IS	2026-01-12	2026-04-24	W	11:00 AM-01:50 PM	18	30	Mian Umer\nShafiq	6.527 -\ncap:4	1169
621	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	17	30	Masoud Riazi	6.302 -\ncap:44	1170
622	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	16	30	Mian Umer\nShafiq	6.507 -\ncap:72	1171
623	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	16	30	Shams Kalam	6.427 -\ncap:24	1172
624	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	16	30	Peyman\nPourafshary	6.427 -\ncap:24	1173
625	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	14	30	Irawan Sonny	6.507 -\ncap:72	1174
626	Spring	2026	1S	2026-01-12	2026-04-24	F	04:00 PM-06:50 PM	16	30	Peyman\nPourafshary	6.507 -\ncap:72	1175
627	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	6	30	Shams Kalam	6.427 -\ncap:24	1176
628	Spring	2026	1IS	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	7	30	Mahmoud Leila	6.419 -\ncap:24	1177
629	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	7	30	Mian Umer\nShafiq	6.507 -\ncap:72	1178
630	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	4	20	Masoud Riazi	6.302 -\ncap:44	1179
631	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	0	30	Peyman\nPourafshary	6.427 -\ncap:24	1180
634	Spring	2026	1S	2026-01-12	2026-04-24	F	01:00 PM-03:00 PM	11	12	Agata Natasza\nBurska	NUSOM\nBuilding -\ncap:0	1183
635	Spring	2026	1S	2026-01-12	2026-04-24	F	09:00 AM-10:00 AM	11	12	Eva\nRiethmacher	NUSOM\nBuilding -\ncap:0	1184
637	Spring	2026	1S	2026-01-12	2026-04-24	F	09:00 AM-10:00 AM	6	7	Eva\nRiethmacher	NUSOM\nBuilding -\ncap:0	1186
638	Spring	2026	1S	2026-01-12	2026-04-24	F	01:00 PM-03:00 PM	6	7	Eva\nRiethmacher	NUSOM\nBuilding -\ncap:0	1187
639	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-04:00 PM	2	2	Nikolai Barlev	NUSOM\nBuilding -\ncap:0	1188
642	Spring	2026	1L	2026-01-12	2026-04-23	F	09:00 AM-12:00 PM	14	16	Raushan\nAlibekova	NUSOM\nBuilding -\ncap:0	1191
643	Spring	2026	1L	2026-01-12	2026-04-23	T	09:00 AM-12:00 PM	14	16	Yuliya Semenova	NUSOM\nBuilding -\ncap:0	1192
644	Spring	2026	1L	2026-01-12	2026-04-23	W	09:00 AM-12:00 PM	14	16	Paolo Colet	NUSOM\nBuilding -\ncap:0	1193
645	Spring	2026	1L	2026-01-12	2026-04-23	R	09:00 AM-12:00 PM	8	10	Joseph Almazan	NUSOM\nBuilding -\ncap:0	1194
646	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	27	28	Bakinaz Abdalla	8.422A -\ncap:32	1195
22	Spring	2026	7S	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	49	50	Matthew Heeney	2.307 -\ncap:75	1196
22	Spring	2026	9S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	38	50	Mihnea Capraru	2.307 -\ncap:75	1197
22	Spring	2026	10S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	27	50	Mihnea Capraru	2.307 -\ncap:75	1198
22	Spring	2026	12S	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	46	50	Matthew Heeney	2.307 -\ncap:75	1199
22	Spring	2026	6S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	35	50	Chandler Hatch	2.407 -\ncap:85	1200
22	Spring	2026	1S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	50	50	Siegfried Van\nDuffel	9.105 -\ncap:68	1201
22	Spring	2026	15S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	31	50	Mihnea Capraru	9.105 -\ncap:68	1202
22	Spring	2026	3S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	38	40	Donovan Cox	5E.438 -\ncap:82	1203
22	Spring	2026	4S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	40	40	Donovan Cox	5E.438 -\ncap:82	1204
22	Spring	2026	8S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	38	40	Donovan Cox	5E.438 -\ncap:82	1205
22	Spring	2026	14S	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	37	50	Ted Parent	5E.438 -\ncap:82	1206
22	Spring	2026	16S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	41	50	James\nHutchinson	5E.438 -\ncap:82	1207
22	Spring	2026	17S	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	48	50	Donovan Cox	5E.438 -\ncap:82	1208
647	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	25	28	Mihnea Capraru	8.154 -\ncap:56	1209
648	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	25	24	James\nHutchinson	8.305 -\ncap:30	1210
649	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	22	24	Ted Parent	7E.125/1 -\ncap:36	1211
650	Spring	2026	1L	2026-01-12	2026-04-24	T R	07:30 PM-08:45 PM	4	6	Matthew Heeney	6.302 -\ncap:44	1212
2	Spring	2026	2PLb	2026-01-12	2026-04-24	M	12:00 PM-02:50 PM	31	33	Mereke\nTontayeva	7.302 -\ncap:30	1213
2	Spring	2026	3PLb	2026-01-12	2026-04-24	T	09:00 AM-11:50 AM	15	33	Mereke\nTontayeva	7.302 -\ncap:30	1214
2	Spring	2026	4PLb	2026-01-12	2026-04-24	T	12:00 PM-02:50 PM	24	33	Mereke\nTontayeva	7.302 -\ncap:30	1215
2	Spring	2026	5PLb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	20	33	Mereke\nTontayeva	7.302 -\ncap:30	1216
2	Spring	2026	6PLb	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	21	33	Mereke\nTontayeva	7.302 -\ncap:30	1217
479	Spring	2026	1L	2026-01-12	2026-02-10	M	09:30 AM-12:30 PM	33	40	Zhanar\nSmailova,\nChristian\nSofilkanitsch	(C3) 1009 -\ncap:70	1004
509	Spring	2026	1L	2026-01-12	2026-04-24	F	04:00 PM-05:15 PM	7	20	Gulsim\nKulsharova	3E.224 -\ncap:90	1039
2	Spring	2026	7PLb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	22	33	Mereke\nTontayeva	7.302 -\ncap:30	1218
2	Spring	2026	8PLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	21	33	Mereke\nTontayeva	7.302 -\ncap:30	1219
2	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	154	240	Ernazar\nAbdikamalov	Orange Hall\n- cap:450	1220
2	Spring	2026	2R	2026-01-12	2026-04-24	M	11:00 AM-11:50 AM	16	60	Omid Farzadian	7E.125/2 -\ncap:56	1221
2	Spring	2026	3R	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	45	60	Omid Farzadian	7E.125/2 -\ncap:56	1222
2	Spring	2026	4R	2026-01-12	2026-04-24	F	01:00 PM-01:50 PM	49	60	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	1223
2	Spring	2026	5R	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	44	60	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	1224
8	Spring	2026	1PLb	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	1225
8	Spring	2026	2PLb	2026-01-12	2026-04-24	M	12:00 PM-02:50 PM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	1226
8	Spring	2026	3PLb	2026-01-12	2026-04-24	T	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	1227
8	Spring	2026	4PLb	2026-01-12	2026-04-24	T	12:00 PM-02:50 PM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	1228
8	Spring	2026	5PLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	33	36	Mereke\nTontayeva	9.202 -\ncap:40	1229
8	Spring	2026	6PLb	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	33	36	Mereke\nTontayeva	9.202 -\ncap:40	1230
8	Spring	2026	7PLb	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	1231
8	Spring	2026	8PLb	2026-01-12	2026-04-24	R	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	1232
8	Spring	2026	9PLb	2026-01-12	2026-04-24	R	12:00 PM-02:50 PM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	1233
8	Spring	2026	10PLb	2026-01-12	2026-04-24	F	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	1234
8	Spring	2026	12PLb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	1235
8	Spring	2026	16PLb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	34	36	Mereke\nTontayeva	9.202 -\ncap:40	1236
8	Spring	2026	17PLb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	1237
8	Spring	2026	19PLb	2026-01-12	2026-04-24	F	12:00 PM-02:50 PM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	1238
8	Spring	2026	11PLb	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	30	36	Mereke\nTontayeva	9.222 -\ncap:40	1239
8	Spring	2026	13PLb	2026-01-12	2026-04-24	T	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.222 -\ncap:40	1240
8	Spring	2026	14PLb	2026-01-12	2026-04-24	R	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.222 -\ncap:40	1241
8	Spring	2026	15PLb	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.222 -\ncap:40	1242
8	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	218	230	Askhat\nJumabekov	Orange Hall\n- cap:450	1243
8	Spring	2026	2L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	185	230	Kyunghwan Oh	Orange Hall\n- cap:450	1244
8	Spring	2026	3L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	226	230	Marat Kaikanov	Orange Hall\n- cap:450	1245
8	Spring	2026	1R	2026-01-12	2026-04-24	M	09:00 AM-09:50 AM	51	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	1246
8	Spring	2026	2R	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	62	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	1247
8	Spring	2026	3R	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	66	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	1248
8	Spring	2026	5R	2026-01-12	2026-04-24	W	09:00 AM-09:50 AM	61	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	1249
8	Spring	2026	6R	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	64	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	1250
8	Spring	2026	7R	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	65	66	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	1251
8	Spring	2026	8R	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	62	66	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	1252
8	Spring	2026	9R	2026-01-12	2026-04-24	F	09:00 AM-09:50 AM	66	66	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	1253
8	Spring	2026	10R	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	66	66	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	1254
8	Spring	2026	11R	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	66	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	1255
651	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	42	55	Dana Alina	7E.125/2 -\ncap:56	1256
652	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	14	24	Rayner\nRodriguez\nGuzman	7.507 -\ncap:48	1257
652	Spring	2026	1R	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	14	15	Rayner\nRodriguez\nGuzman	7.507 -\ncap:48	1258
653	Spring	2026	1CLb	2026-01-12	2026-04-24	T	06:00 PM-07:15 PM	25	24	Ernazar\nAbdikamalov,\nDana Alina	7.507 -\ncap:48	1259
653	Spring	2026	1L	2026-01-12	2026-04-24	T	04:30 PM-05:45 PM	25	24	Ernazar\nAbdikamalov,\nDana Alina	7.507 -\ncap:48	1260
654	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	20	24	Zhandos\nUtegulov	7.507 -\ncap:48	1261
654	Spring	2026	1R	2026-01-12	2026-04-24	R	03:00 PM-04:15 PM	20	24	Zhandos\nUtegulov	7.507 -\ncap:48	1262
655	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	6	24	Bakhtiyar\nOrazbayev	7.507 -\ncap:48	1263
655	Spring	2026	1R	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	6	24	Bakhtiyar\nOrazbayev	7.507 -\ncap:48	1264
656	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	9	24	Alexander\nTikhonov	7.507 -\ncap:48	1265
656	Spring	2026	1Lb	2026-01-12	2026-04-24	R	04:30 PM-07:15 PM	9	24	Alexander\nTikhonov,\nBekdaulet\nShukirgaliyev	7.502 -\ncap:24	1266
657	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	6	24	Sergiy Bubin	7.507 -\ncap:48	1267
657	Spring	2026	1R	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	6	20	Sergiy Bubin	7.507 -\ncap:48	1268
658	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	4	24	Daniele\nMalafarina	7.507 -\ncap:48	1269
659	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	8	24	Anton\nDesyatnikov	\N	1270
660	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	8	24	Daniele\nMalafarina	\N	1271
661	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	11	12	Sergiy Bubin	7.507 -\ncap:48	1272
661	Spring	2026	1R	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	11	12	Sergiy Bubin	7.507 -\ncap:48	1273
662	Spring	2026	1L	2026-01-12	2026-04-24	T	04:30 PM-05:45 PM	11	12	Ernazar\nAbdikamalov,\nDana Alina	7.507 -\ncap:48	1274
662	Spring	2026	1Lb	2026-01-12	2026-04-24	T	06:00 PM-07:15 PM	11	12	Ernazar\nAbdikamalov,\nDana Alina	7.507 -\ncap:48	1275
663	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	12	12	Michael Good	7.507 -\ncap:48	1276
663	Spring	2026	1R	2026-01-12	2026-04-24	T	03:00 PM-04:15 PM	12	12	Michael Good	7.507 -\ncap:48	1277
664	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	2	12	Daniele\nMalafarina	7.507 -\ncap:48	1278
665	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	6	24	Anton\nDesyatnikov	\N	1279
666	Spring	2026	1ThDef	2026-01-12	2026-04-24	\N	Online/Distant	6	20	Rayner\nRodriguez\nGuzman	\N	1280
667	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	15	20	Ernazar\nAbdikamalov	\N	1281
668	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	3	12	Alexander\nTikhonov	\N	1282
669	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	3	6	Sergiy Bubin	7.507 -\ncap:48	1283
669	Spring	2026	1R	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	3	6	Sergiy Bubin	7.507 -\ncap:48	1284
670	Spring	2026	1L	2026-01-12	2026-04-24	T	04:30 PM-05:45 PM	7	6	Ernazar\nAbdikamalov,\nDana Alina	7.507 -\ncap:48	1285
670	Spring	2026	1Lb	2026-01-12	2026-04-24	T	06:00 PM-07:15 PM	7	6	Ernazar\nAbdikamalov,\nDana Alina	7.507 -\ncap:48	1286
671	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	1	6	Michael Good	7.507 -\ncap:48	1287
671	Spring	2026	1R	2026-01-12	2026-04-24	T	03:00 PM-04:15 PM	1	6	Michael Good	7.507 -\ncap:48	1288
672	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	4	24	Anton\nDesyatnikov	\N	1289
673	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	86	80	Neil Collins	Green Hall -\ncap:231	1290
16	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	82	120	Caress Schenk	Green Hall -\ncap:231	1291
674	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	86	120	Bimal Adhikari	Green Hall -\ncap:231	1292
675	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	24	29	Dinara Pisareva,\nAndrey Semenov	8.321 -\ncap:32	1293
675	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	26	29	Dinara Pisareva,\nAndrey Semenov	8.321 -\ncap:32	1294
676	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	17	24	Ho Koh	8.321 -\ncap:32	1295
676	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	28	24	Jessica Neafie	6.522 -\ncap:35	1296
677	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	15	18	Chunho Park	8.308 -\ncap:24	1297
678	Spring	2026	1L	2026-01-12	2026-04-24	F	01:00 PM-03:50 PM	11	10	Brian Smith	8.317 -\ncap:28	1298
679	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	22	18	Dinara Pisareva,\nAndrey Semenov	8.321 -\ncap:32	1299
680	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	19	18	Maja Savevska	8.308 -\ncap:24	1300
681	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	20	18	Maja Savevska	8.308 -\ncap:24	1301
682	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	17	18	Berikbol\nDukeyev	8.321 -\ncap:32	1302
683	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	18	18	Sabina\nInsebayeva	8.321 -\ncap:32	1303
684	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	11	18	Alexei Trochev	8.308 -\ncap:24	1304
685	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	24	18	Neil Collins	8.308 -\ncap:24	1305
686	Spring	2026	1L	2026-01-12	2026-04-24	T	10:30 AM-01:15 PM	15	18	Chun Young\nPark	7.210 -\ncap:54	1306
687	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Bimal Adhikari	\N	1307
687	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Helene Thibault	\N	1308
687	Spring	2026	3L	2026-01-12	2026-04-24	\N	Online/Distant	3	5	Neil Collins	\N	1309
688	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	10	14	Chunho Park	8.308 -\ncap:24	1310
689	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	12	14	Elmira\nJoldybayeva	8.308 -\ncap:24	1311
690	Spring	2026	1S	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	6	6	Helene Thibault	8.302 -\ncap:57	1312
691	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	15	14	Ho Koh	8.308 -\ncap:24	1313
692	Spring	2026	1S	2026-01-12	2026-04-24	R	10:30 AM-01:15 PM	14	14	Chun Young\nPark	7.210 -\ncap:54	1314
693	Spring	2026	1L	2026-01-12	2026-04-24	M	11:00 AM-01:50 PM	13	14	Sabina\nInsebayeva	5E.438 -\ncap:82	1315
694	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Bimal Adhikari	\N	1316
694	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	4	5	Jessica Neafie	\N	1317
694	Spring	2026	3Int	2026-01-12	2026-04-24	\N	Online/Distant	3	6	Alexei Trochev	\N	1318
694	Spring	2026	4Int	2026-01-12	2026-04-24	\N	Online/Distant	4	5	Maja Savevska	\N	1319
695	Spring	2026	1L	2026-01-12	2026-04-24	W	11:00 AM-01:50 PM	15	15	Dinara Pisareva,\nAndrey Semenov	8.321 -\ncap:32	1320
696	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	1	6	Chunho Park	8.308 -\ncap:24	1321
697	Spring	2026	1L	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	15	15	Helene Thibault	8.317 -\ncap:28	1322
698	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	6	6	Elmira\nJoldybayeva	8.308 -\ncap:24	1323
699	Spring	2026	1L	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	4	6	Helene Thibault	8.302 -\ncap:57	1324
700	Spring	2026	1L	2026-01-12	2026-04-24	R	10:30 AM-01:15 PM	6	6	Chun Young\nPark	7.210 -\ncap:54	1325
701	Spring	2026	1L	2026-01-12	2026-04-24	M	11:00 AM-01:50 PM	6	6	Sabina\nInsebayeva	5E.438 -\ncap:82	1326
702	Spring	2026	1S	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Ho Koh	\N	1327
702	Spring	2026	2S	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Alexei Trochev	\N	1328
703	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	15	15	Brian Smith	\N	1329
704	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	8	15	Brian Smith	\N	1330
705	Spring	2026	1S	2026-01-12	2026-04-24	R	10:30 AM-01:15 PM	2	2	Chun Young\nPark	7.210 -\ncap:54	1331
706	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	09:00 AM-09:50 AM	16	24	Katarzyna Galaj	8.508 -\ncap:24	1332
706	Spring	2026	3L	2026-01-12	2026-04-24	M T W R	10:00 AM-10:50 AM	12	24	Katarzyna Galaj	8.508 -\ncap:24	1333
707	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	11:00 AM-11:50 AM	13	24	Katarzyna Galaj	8.508 -\ncap:24	1334
708	Spring	2026	1L	2026-01-12	2026-04-22	T	10:00 AM-12:00 PM	24	70	Byron Crape	NUSOM\nBuilding -\ncap:0	1335
709	Spring	2026	1L	2026-01-15	2026-04-23	R	09:00 AM-12:00 PM	24	70	Yesbolat Sakko	NUSOM\nBuilding -\ncap:0	1336
710	Spring	2026	1L	2026-01-16	2026-04-24	F	01:00 PM-03:00 PM	24	70	Anargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	1337
711	Spring	2026	1L	2026-01-14	2026-04-22	W	09:00 AM-12:00 PM	24	70	Raushan\nAlibekova	NUSOM\nBuilding -\ncap:0	1338
712	Spring	2026	1L	2026-01-12	2026-04-20	M	01:00 PM-03:00 PM	24	70	Byron Crape	NUSOM\nBuilding -\ncap:0	1339
713	Spring	2026	1L	2026-01-12	2026-04-20	M	01:00 PM-04:00 PM	27	70	Anargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	1340
714	Spring	2026	1P	2026-01-13	2026-04-21	T	01:00 PM-04:00 PM	34	70	Mei Yen Chan	NUSOM\nBuilding -\ncap:0	1341
715	Spring	2026	1L	2026-01-12	2026-04-20	M	01:00 PM-04:00 PM	8	70	Kuanysh\nYergaliyev	NUSOM\nBuilding -\ncap:0	1342
716	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	14	22	Katherine\nErdman	8.105 -\ncap:56	1343
717	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	1	5	Katherine\nErdman	8.105 -\ncap:56	1344
718	Spring	2026	1L	2026-01-12	2026-04-24	M W	03:30 PM-05:00 PM	2	5	Elvira\nYavorskaya	8.322B -\ncap:24	1345
719	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	4	10	Aleksandr\nGrishin	8.322B -\ncap:24	1346
720	Spring	2026	1L	2026-01-12	2026-04-24	T R	11:00 AM-12:15 PM	5	10	Yuliya\nKozitskaya	8.322B -\ncap:24	1347
721	Spring	2026	1S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	2	10	Meiramgul\nKussainova	8.322B -\ncap:24	1348
722	Spring	2026	1L	2026-01-12	2026-04-24	M W	02:00 PM-03:15 PM	3	10	Sabina\nInsebayeva	8.322B -\ncap:24	1349
723	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	37	36	Matteo\nRubagotti	7.246 -\ncap:48	1350
724	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	33	36	Ton Duc Do	7.246 -\ncap:48	1351
724	Spring	2026	1Lb	2026-01-12	2026-04-24	T	12:00 PM-02:45 PM	15	20	Ahmad Alhassan	7.327 -\ncap:48	1352
724	Spring	2026	2Lb	2026-01-12	2026-04-24	T	03:00 PM-05:45 PM	18	20	Ahmad Alhassan	7.327 -\ncap:48	1353
17	Spring	2026	3Lb	2026-01-12	2026-04-24	M	04:00 PM-06:00 PM	38	36	Togzhan\nSyrymova	7.327 -\ncap:48	1354
17	Spring	2026	4Lb	2026-01-12	2026-04-24	T	10:00 AM-12:00 PM	31	32	Anara\nSandygulova	7.327 -\ncap:48	1355
17	Spring	2026	5Lb	2026-01-12	2026-04-24	W	10:00 AM-12:00 PM	32	32	Zhanat\nKappassov	7.327 -\ncap:48	1356
17	Spring	2026	6Lb	2026-01-12	2026-04-24	W	12:00 PM-02:00 PM	37	36	Zhanat\nKappassov	7.327 -\ncap:48	1357
17	Spring	2026	7Lb	2026-01-12	2026-04-24	R	09:00 AM-11:00 AM	23	32	Anara\nSandygulova	7.327 -\ncap:48	1358
17	Spring	2026	10Lb	2026-01-12	2026-04-24	F	04:00 PM-06:00 PM	36	36	Togzhan\nSyrymova	7.327 -\ncap:48	1359
17	Spring	2026	11Lb	2026-01-12	2026-04-24	R	11:00 AM-01:00 PM	37	36	Anara\nSandygulova	7.327 -\ncap:48	1360
17	Spring	2026	12Lb	2026-01-12	2026-04-24	F	09:00 AM-11:00 AM	32	32	Anara\nSandygulova	7.327 -\ncap:48	1361
17	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	80	90	Togzhan\nSyrymova	online -\ncap:0	1362
17	Spring	2026	2L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	54	90	Togzhan\nSyrymova	online -\ncap:0	1363
17	Spring	2026	4L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	132	130	Azamat\nYeshmukhameto\nv	online -\ncap:0	1364
725	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	27	36	Aibek\nNiyetkaliyev	7.246 -\ncap:48	1365
725	Spring	2026	1Lb	2026-01-12	2026-04-24	R	03:00 PM-05:45 PM	18	18	Aibek\nNiyetkaliyev	7.327 -\ncap:48	1366
725	Spring	2026	2Lb	2026-01-12	2026-04-24	W	03:00 PM-05:45 PM	9	18	Aibek\nNiyetkaliyev	7.327 -\ncap:48	1367
726	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	17	18	Tohid Alizadeh	7E.230 -\ncap:24	1368
727	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	27	32	Michele\nFolgheraiter	7.246 -\ncap:48	1369
728	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	25	32	Anara\nSandygulova	7.246 -\ncap:48	1370
729	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	16	32	Almas\nShintemirov	7.322 -\ncap:24	1371
730	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	16	32	Togzhan\nSyrymova	\N	1372
730	Spring	2026	2P	2026-01-12	2026-04-24	\N	Online/Distant	1	2	Togzhan\nSyrymova	\N	1373
731	Spring	2026	1L	2026-01-12	2026-04-24	M W	04:30 PM-05:45 PM	20	26	Huseyin Atakan\nVarol	7.246 -\ncap:48	1374
732	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	21	22	Tohid Alizadeh	\N	1375
733	Spring	2026	1Th	2026-01-12	2026-04-24	\N	Online/Distant	0	26	Ton Duc Do	\N	1376
733	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	23	26	Ton Duc Do	\N	1377
734	Spring	2026	1L	2026-01-12	2026-04-24	M W	04:30 PM-05:45 PM	13	12	Zhanat\nKappassov	7.322 -\ncap:24	1378
735	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	11	12	Ton Duc Do	\N	1379
736	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	2	2	Michael Lewis	\N	1380
736	Spring	2026	1L	2026-01-12	2026-04-24	M W	03:00 PM-04:15 PM	96	80	Michael Lewis	3E.224 -\ncap:90	1381
737	Spring	2026	1CL	2026-01-12	2026-04-24	\N	Online/Distant	9	10	Jong Kim,\nBakhyt\nAubakirova	\N	1382
738	Spring	2026	1CL	2026-01-12	2026-04-24	\N	Online/Distant	7	15	Stavros\nPoulopoulos,\nLyazzat\nMukhangaliyeva	\N	1383
738	Spring	2026	2CL	2026-01-12	2026-04-24	\N	Online/Distant	5	19	Sherif Gouda	\N	1384
738	Spring	2026	3CL	2026-01-12	2026-04-24	\N	Online/Distant	5	10	Mehdi Bagheri	\N	1385
739	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	2	2	Hashim Ali, Hari\nMohan Rai	\N	1386
739	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	104	130	Hashim Ali, Hari\nMohan Rai	Orange Hall\n- cap:450	1387
740	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	20	20	Zauresh\nAtakhanova	6.105 -\ncap:64	1388
741	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	103	100	Karina\nMatkarimova	\N	1389
741	Spring	2026	1S	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	26	25	Ana Cristina\nHenriques\nMarques	8.310 -\ncap:27	1390
741	Spring	2026	2S	2026-01-12	2026-04-24	M	11:00 AM-11:50 AM	26	25	Ana Cristina\nHenriques\nMarques	8.310 -\ncap:27	1391
741	Spring	2026	3S	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	27	25	Karina\nMatkarimova	8.310 -\ncap:27	1392
741	Spring	2026	4S	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	24	25	Karina\nMatkarimova	8.310 -\ncap:27	1393
742	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	28	27	Dana\nBurkhanova	8.310 -\ncap:27	1394
742	Spring	2026	3L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	30	27	Matvey\nLomonosov	8.307 -\ncap:55	1395
743	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	25	25	Darkhan\nMedeuov	6.522 -\ncap:35	1396
744	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	26	26	Ana Cristina\nHenriques\nMarques	8.422A -\ncap:32	1397
745	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	27	27	Saltanat\nAkhmetova	8.310 -\ncap:27	1398
746	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	27	25	Darkhan\nMedeuov	8.310 -\ncap:27	1399
746	Spring	2026	2L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	25	25	Darkhan\nMedeuov	8.310 -\ncap:27	1400
747	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	28	27	Dana\nBurkhanova	8.154 -\ncap:56	1401
747	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	25	27	Mikhail Sokolov	8.154 -\ncap:56	1402
748	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	24	22	Ana Cristina\nHenriques\nMarques	8.154 -\ncap:56	1403
749	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	27	27	Karina\nMatkarimova	8.310 -\ncap:27	1404
750	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	25	26	Gavin Slade	8.310 -\ncap:27	1405
751	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Dana\nBurkhanova	\N	1406
751	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Matvey\nLomonosov	\N	1407
752	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	3	5	Matvey\nLomonosov	\N	1408
753	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Matvey\nLomonosov	\N	1409
754	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	26	26	Saltanat\nAkhmetova	8.310 -\ncap:27	1410
755	Spring	2026	1L	2026-01-12	2026-04-24	W	05:00 PM-07:50 PM	26	26	Gavin Slade	8.154 -\ncap:56	1411
756	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	20	26	Mikhail Sokolov	8.154 -\ncap:56	1412
757	Spring	2026	1S	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	18	25	Dana\nBurkhanova	8.154 -\ncap:56	1413
758	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	4	5	Ana Cristina\nHenriques\nMarques	8.154 -\ncap:56	1414
759	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	5	5	Ana Cristina\nHenriques\nMarques	8.154 -\ncap:56	1415
760	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	12:00 PM-12:50 PM	24	24	Arturo Bellido	8.317 -\ncap:28	1416
760	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	09:00 AM-09:50 AM	18	24	Edyta Denst-\nGarcia	8.305 -\ncap:30	1417
760	Spring	2026	3L	2026-01-12	2026-04-24	M T W R	10:00 AM-10:50 AM	11	24	Edyta Denst-\nGarcia	8.305 -\ncap:30	1418
761	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	01:00 PM-01:50 PM	14	24	Arturo Bellido	8.317 -\ncap:28	1419
761	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	02:00 PM-02:50 PM	19	24	Arturo Bellido	8.317 -\ncap:28	1420
762	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	29	24	Edyta Denst-\nGarcia	8.322A -\ncap:32	1421
763	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	47	50	Daniel Beben	\N	1422
764	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	41	50	Daniel Beben	\N	1423
765	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	50	100	Moldir\nAkhmetova	\N	1424
766	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	43	40	Halit Akarca	8.105 -\ncap:56	1425
767	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	28	30	Wulidanayi\nJumabay	2.407 -\ncap:85	1426
768	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	37	35	Funda Guven	8.302 -\ncap:57	1427
769	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	31	35	Funda Guven	8.302 -\ncap:57	1428
770	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	34	35	Wulidanayi\nJumabay	2.407 -\ncap:85	1429
771	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	10	24	Uli Schamiloglu	8.105 -\ncap:56	1430
772	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	1	5	Uli Schamiloglu	8.105 -\ncap:56	1431
773	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	75	75	Brandon Brock,\nBellido\nLanguasco	7E.429 -\ncap:90	1432
4	Spring	2026	5L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	18	20	Jane Hoelker	6.419 -\ncap:24	1433
4	Spring	2026	15L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	21	20	Olga Campbell-\nThomson	6.410 -\ncap:24	1434
4	Spring	2026	16L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	19	20	Olga Campbell-\nThomson	6.410 -\ncap:24	1435
4	Spring	2026	30L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	20	20	Marina Zaffari	6.410 -\ncap:24	1436
4	Spring	2026	31L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	19	20	Marina Zaffari	6.410 -\ncap:24	1437
4	Spring	2026	32L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	19	20	Marina Zaffari	6.410 -\ncap:24	1438
4	Spring	2026	9L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	7	20	Nicholas\nWalmsley	6.402 -\ncap:24	1439
4	Spring	2026	10L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	14	20	Nicholas\nWalmsley	6.402 -\ncap:24	1440
4	Spring	2026	11L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	20	20	J.C. Ross	6.402 -\ncap:24	1441
4	Spring	2026	12L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	20	20	J.C. Ross	6.402 -\ncap:24	1442
4	Spring	2026	13L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	20	20	J.C. Ross	6.402 -\ncap:24	1443
4	Spring	2026	14L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	20	20	Jeremy Richard\nSpring	6.402 -\ncap:24	1444
4	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	17	20	Bellido\nLanguasco	7.427 -\ncap:23	1445
4	Spring	2026	2L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	8	20	Bellido\nLanguasco	7.427 -\ncap:23	1446
4	Spring	2026	3L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	17	20	Elizabeth Abele	7.427 -\ncap:23	1447
4	Spring	2026	4L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	19	20	Elizabeth Abele	7.427 -\ncap:23	1448
4	Spring	2026	17L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	16	20	Michael Jones	7.427 -\ncap:23	1449
4	Spring	2026	36L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	20	20	Ian Albert\nPeterkin Jr	7.427 -\ncap:23	1450
4	Spring	2026	37L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	20	20	Ian Albert\nPeterkin Jr	7.427 -\ncap:23	1451
4	Spring	2026	34L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	20	20	Shahreen Binti\nMat Nayan	7.517 -\ncap:25	1452
4	Spring	2026	35L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	20	20	Shahreen Binti\nMat Nayan	7.517 -\ncap:25	1453
4	Spring	2026	18L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	20	20	Fariza Tolesh	7.527 -\ncap:24	1454
4	Spring	2026	19L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	20	20	Fariza Tolesh	7.527 -\ncap:24	1455
4	Spring	2026	20L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	19	20	Fariza Tolesh	7.527 -\ncap:24	1456
4	Spring	2026	27L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	19	20	Gulden Issina	7.527 -\ncap:24	1457
4	Spring	2026	28L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	19	20	Gulden Issina	7.527 -\ncap:24	1458
4	Spring	2026	29L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	20	20	Gulden Issina	7.527 -\ncap:24	1459
4	Spring	2026	38L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	20	20	Adam Hefty	7.527 -\ncap:24	1460
4	Spring	2026	33L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	20	20	Andrew\nDrybrough	8.141 -\ncap:24	1461
4	Spring	2026	21L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	20	20	Benjamin\nGibbon	8.140 -\ncap:24	1462
4	Spring	2026	22L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	20	20	Benjamin\nGibbon	8.140 -\ncap:24	1463
4	Spring	2026	23L	2026-01-12	2026-04-24	M W F	06:00 PM-06:50 PM	20	20	Benjamin\nGibbon	8.140 -\ncap:24	1464
4	Spring	2026	24L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	20	20	Nurly Marshal	8.140 -\ncap:24	1465
4	Spring	2026	25L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	20	20	Nurly Marshal	8.140 -\ncap:24	1466
4	Spring	2026	26L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	20	20	Nurly Marshal	8.140 -\ncap:24	1467
4	Spring	2026	39L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	20	20	James Nielsen	8.140 -\ncap:24	1468
774	Spring	2026	10L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	24	24	Yamen Rahvan	6.402 -\ncap:24	1469
774	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	24	24	Tiffany Moore	7.427 -\ncap:23	1470
774	Spring	2026	4L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	23	24	Tiffany Moore	7.427 -\ncap:23	1471
774	Spring	2026	5L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	24	24	Samira Esat	7.427 -\ncap:23	1472
774	Spring	2026	6L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	24	24	Samira Esat	7.427 -\ncap:23	1473
774	Spring	2026	9L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	24	24	Samira Esat	7.427 -\ncap:23	1474
774	Spring	2026	7L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	24	24	Thomas Carl\nHughes	7.527 -\ncap:24	1475
774	Spring	2026	8L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	23	24	Thomas Carl\nHughes	7.527 -\ncap:24	1476
775	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	19	30	Elizabeth Abele	8.327 -\ncap:58	1477
776	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	31	30	Marilyn Plumlee	2.105 -\ncap:64	1478
13	Spring	2026	3L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	24	24	James Nielsen	6.410 -\ncap:24	1479
13	Spring	2026	4L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	24	24	James Nielsen	6.410 -\ncap:24	1480
13	Spring	2026	9L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	24	24	Carlos Abaunza	6.402 -\ncap:24	1481
13	Spring	2026	10L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	25	24	Carlos Abaunza	6.402 -\ncap:24	1482
13	Spring	2026	11L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	23	24	Bakhtiar\nNaghdipour	7.246 -\ncap:48	1483
13	Spring	2026	6L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	24	24	Gamze Oncul	2.322 -\ncap:45	1484
13	Spring	2026	7L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	22	24	Gamze Oncul	2.322 -\ncap:45	1485
13	Spring	2026	8L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	23	24	Gamze Oncul	2.322 -\ncap:45	1486
777	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	22	24	Adam Hefty	7.527 -\ncap:24	1487
777	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	23	24	Adam Hefty	7.527 -\ncap:24	1488
778	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	25	24	Marilyn Plumlee	7.246 -\ncap:48	1489
778	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	21	24	Zhanar\nKabylbekova	7.527 -\ncap:24	1490
778	Spring	2026	3L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	23	24	Zhanar\nKabylbekova	7.527 -\ncap:24	1491
779	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	20	24	Brandon Brock	7E.217 -\ncap:24	1492
779	Spring	2026	3L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	22	24	Michael Jones	7E.217 -\ncap:24	1493
779	Spring	2026	4L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	24	24	James Swider	7E.217 -\ncap:24	1494
779	Spring	2026	5L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	23	24	James Swider	7E.217 -\ncap:24	1495
779	Spring	2026	6L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	21	24	Shahreen Binti\nMat Nayan	7E.217 -\ncap:24	1496
780	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	18	20	Arlyce Menzies	\N	1497
780	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	20	20	Arlyce Menzies	\N	1498
780	Spring	2026	3L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	11	20	Nicholas\nWalmsley	6.402 -\ncap:24	1499
781	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	35	36	Thomas Duke	8.327 -\ncap:58	1500
781	Spring	2026	3L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	36	36	Thomas Carl\nHughes	8.327 -\ncap:58	1501
781	Spring	2026	2L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	36	36	Yamen Rahvan	9.105 -\ncap:68	1502
781	Spring	2026	4L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	36	36	Tiffany Moore	7.105 -\ncap:75	1503
782	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Thomas Duke	\N	1504
783	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	6	5	Thomas Duke	\N	1505
784	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Brandon Brock	\N	1506
785	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	3	5	Brandon Brock	\N	1507
786	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	17	16	Marilyn Plumlee	2.105 -\ncap:64	1508
787	Spring	2026	1Int	2026-01-12	2026-04-24	S	09:00 AM-10:15 AM	9	5	James Swider	online -\ncap:0	1509
788	Spring	2026	1Int	2026-01-12	2026-04-24	S	09:00 AM-10:15 AM	5	5	James Swider	online -\ncap:0	1510
789	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	16	24	Carlos Abaunza	online -\ncap:0	1511
790	Spring	2026	1S	2026-01-12	2026-04-24	\N	Online/Distant	1	1	Adam Hefty	\N	1512
791	Spring	2026	1S	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	25	25	Ivan Delazari	8.305 -\ncap:30	1513
791	Spring	2026	2S	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	26	25	Ivan Delazari	8.305 -\ncap:30	1514
791	Spring	2026	3S	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	27	25	Ivan Delazari	8.305 -\ncap:30	1515
791	Spring	2026	4S	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	25	25	Ivan Delazari	8.305 -\ncap:30	1516
791	Spring	2026	1L	2026-01-12	2026-04-24	M W	02:00 PM-02:50 PM	103	100	Ivan Delazari	Blue Hall -\ncap:239	1517
792	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	30	28	Maria Rybakova	8.422A -\ncap:32	1518
793	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	18	20	Jonathan Dupuy	6.410 -\ncap:24	1519
793	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	18	20	Jonathan Dupuy	6.410 -\ncap:24	1520
793	Spring	2026	4L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	20	20	Ian Albert\nPeterkin Jr	7.246 -\ncap:48	1521
794	Spring	2026	1S	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	28	28	Gabriel McGuire	8.322A -\ncap:32	1522
795	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	25	28	Yuliya\nKozitskaya	8.422A -\ncap:32	1523
796	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	26	25	Maria Rybakova	8.422A -\ncap:32	1524
797	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	23	26	Yuliya\nKozitskaya	8.422A -\ncap:32	1525
798	Spring	2026	1L	2026-01-12	2026-04-24	T R	07:30 PM-08:45 PM	20	21	Matthew Heeney	6.302 -\ncap:44	1526
799	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	13	15	Florian Kuechler	\N	1527
799	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Marzieh Sadat\nRazavi	\N	1528
800	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	8	10	Yuliya\nKozitskaya	\N	1529
800	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Andrey\nFilchenko	\N	1530
801	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	31	26	Jenni Lehtinen	8.302 -\ncap:57	1531
802	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	15	12	Jonathan Dupuy	6.410 -\ncap:24	1532
803	Spring	2026	1CP	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	20	20	Amanda Murphy	8.322A -\ncap:32	1533
804	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	7	6	Jenni Lehtinen	8.302 -\ncap:57	1534
805	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	1	0	Jonathan Dupuy	6.410 -\ncap:24	1535
806	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	4	4	Jenni Lehtinen	8.302 -\ncap:57	1536
98	Spring	2026	1L	2026-01-12	2026-04-24	R	10:30 AM-11:45 AM	50	50	Mirat Akshalov,\nRoza\nNurgozhayeva	(C3) 1009 -\ncap:70	134
112	Spring	2026	1L	2026-01-12	2026-04-24	M W	11:00 AM-11:50 AM	54	40	Abid Nadeem	3E.224 -\ncap:90	162
164	Spring	2026	2L	2026-01-12	2026-04-24	T	03:00 PM-04:15 PM	32	85	Lisa Chalaguine	7E.429 -\ncap:90	254
164	Spring	2026	3L	2026-01-12	2026-04-24	T	04:30 PM-05:45 PM	34	85	Anwar Ghani	7E.429 -\ncap:90	255
164	Spring	2026	4L	2026-01-12	2026-04-24	T	06:00 PM-07:15 PM	24	85	Sain Saginbekov	7E.429 -\ncap:90	256
14	Spring	2026	3L	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	76	75	Muhammed\nDemirci	3E.224 -\ncap:90	277
15	Spring	2026	1L	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	75	75	Ben Tyler	7E.429 -\ncap:90	278
15	Spring	2026	2L	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	92	110	Jean Marie\nGuillaume\nGerard de\nNivelle	7E.429 -\ncap:90	279
15	Spring	2026	3L	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	72	75	Meiram\nMurzabulatov	7E.429 -\ncap:90	280
168	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	143	145	Michael Lewis	Orange Hall\n- cap:450	283
168	Spring	2026	2L	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	138	145	Saida\nMussakhojayeva	Orange Hall\n- cap:450	284
178	Spring	2026	1L	2026-01-12	2026-04-24	M W	01:30 PM-02:45 PM	33	34	Almas\nShintemirov	3E.224 -\ncap:90	308
179	Spring	2026	1L	2026-01-12	2026-04-24	M	10:30 AM-11:45 AM	19	35	Anwar Ghani	3E.223 -\ncap:63	309
188	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	28	32	Siamac Fazli	\N	319
327	Spring	2026	1L	2026-01-12	2026-04-24	M	03:00 PM-04:15 PM	14	20	Prashant Jamwal	3E.223 -\ncap:63	561
328	Spring	2026	1L	2026-01-12	2026-04-24	F	04:00 PM-05:15 PM	4	40	Gulsim\nKulsharova	3E.224 -\ncap:90	562
336	Spring	2026	5L	2026-01-12	2026-04-24	F	10:30 AM-11:30 AM	40	40	Behrouz Maham	3.309 -\ncap:40	576
342	Spring	2026	26S	2026-01-12	2026-04-17	T R	03:00 PM-03:50 PM	21	22	Joohee Hong,\nMarc\nFormichella	2.141 -\ncap:28	704
342	Spring	2026	25S	2026-01-12	2026-04-17	T R	02:00 PM-02:50 PM	21	22	Joohee Hong	2.321 -\ncap:31	703
342	Spring	2026	27S	2026-01-12	2026-04-17	T R	01:00 PM-01:50 PM	21	22	Joohee Hong	2.321 -\ncap:31	705
342	Spring	2026	6L	2026-01-12	2026-04-17	M	12:00 PM-12:50 PM	42	44	Joohee Hong,\nMarc\nFormichella	2.327 -\ncap:88	689
342	Spring	2026	1L	2026-01-12	2026-04-17	W	12:00 PM-12:50 PM	40	44	Joohee Hong,\nJonathan\nDallmann	2.407 -\ncap:85	710
342	Spring	2026	1S	2026-01-12	2026-04-17	F	12:00 PM-12:50 PM	20	22	Joohee Hong,\nJonathan\nDallmann	2.407 -\ncap:85	716
342	Spring	2026	3S	2026-01-12	2026-04-17	F	12:00 PM-12:50 PM	20	22	Joohee Hong,\nJonathan\nDallmann	2.407 -\ncap:85	717
342	Spring	2026	11S	2026-01-12	2026-04-17	F	11:00 AM-11:50 AM	21	22	Kairat Ismailov,\nJoohee Hong	2.407 -\ncap:85	720
342	Spring	2026	12S	2026-01-12	2026-04-17	F	09:00 AM-09:50 AM	21	22	Galymzhan\nKoishiyev,\nJoohee Hong	2.407 -\ncap:85	726
342	Spring	2026	13S	2026-01-12	2026-04-17	F	11:00 AM-11:50 AM	21	22	Kairat Ismailov,\nJoohee Hong	2.407 -\ncap:85	721
342	Spring	2026	14S	2026-01-12	2026-04-17	F	09:00 AM-09:50 AM	20	22	Galymzhan\nKoishiyev,\nJoohee Hong	2.407 -\ncap:85	727
342	Spring	2026	15L	2026-01-12	2026-04-17	W	10:00 AM-10:50 AM	40	44	Joohee Hong,\nJonathan\nDallmann	2.407 -\ncap:85	714
342	Spring	2026	16S	2026-01-12	2026-04-17	F	10:00 AM-10:50 AM	21	22	Kairat Ismailov,\nJoohee Hong	2.407 -\ncap:85	728
342	Spring	2026	19S	2026-01-12	2026-04-17	F	11:00 AM-11:50 AM	21	22	Galymzhan\nKoishiyev,\nJoohee Hong	2.407 -\ncap:85	718
342	Spring	2026	29S	2026-01-12	2026-04-17	F	11:00 AM-11:50 AM	21	22	Galymzhan\nKoishiyev,\nJoohee Hong	2.407 -\ncap:85	719
342	Spring	2026	32S	2026-01-12	2026-04-17	F	10:00 AM-10:50 AM	22	22	Kairat Ismailov,\nJoohee Hong	2.407 -\ncap:85	729
342	Spring	2026	18S	2026-01-12	2026-04-17	T	02:00 PM-02:50 PM	21	22	Joohee Hong,\nMaksim Kozlov	2.502 -\ncap:25	698
342	Spring	2026	21S	2026-01-12	2026-04-17	R	01:00 PM-01:50 PM	20	22	Joohee Hong,\nMaksim Kozlov	2.502 -\ncap:25	699
342	Spring	2026	23S	2026-01-12	2026-04-17	R	02:00 PM-02:50 PM	20	22	Joohee Hong,\nMaksim Kozlov	2.502 -\ncap:25	701
342	Spring	2026	28S	2026-01-12	2026-04-17	T	03:00 PM-03:50 PM	21	22	Joohee Hong,\nMaksim Kozlov	2.502 -\ncap:25	706
530	Spring	2026	1S	2026-01-12	2026-04-24	\N	Online/Distant	9	35	Fidelis Suorineni	\N	1061
632	Spring	2026	1S	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	19	40	Peyman\nPourafshary	6.105 -\ncap:64	1181
633	Spring	2026	1Lb	2026-01-12	2026-04-24	M T W R F	06:00 PM-07:00 PM	23	26	Eva\nRiethmacher	NUSOM\nBuilding -\ncap:0	1182
636	Spring	2026	1S	2026-01-12	2026-04-24	F	04:00 PM-06:00 PM	20	30	Eugene\nTulchinsky	NUSOM\nBuilding -\ncap:0	1185
640	Spring	2026	1P	2026-01-12	2026-04-23	M	05:00 PM-06:00 PM	36	36	Antonio Sarria-\nSantamera	NUSOM\nBuilding -\ncap:0	1189
641	Spring	2026	1S	2026-01-12	2026-04-23	F	01:00 PM-04:00 PM	29	36	Mei Yen Chan	NUSOM\nBuilding -\ncap:0	1190
37	Fall	2025	1L	2025-08-18	2025-11-28	R	09:00 AM-10:15 AM	149	150	Russell Zanca	Main Hall -\ncap:1319	1537
807	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	93	100	Reed Coil	Senate Hall\n- cap:144	1538
40	Fall	2025	1S	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	26	25	Karina\nMatkarimova	8.154 -\ncap:56	1539
40	Fall	2025	2S	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	24	25	Karina\nMatkarimova	8.154 -\ncap:56	1540
808	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	14	15	Abay Namen	8.147 -\ncap:15	1541
809	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	26	25	Katherine\nErdman	8.154 -\ncap:56	1542
810	Fall	2025	2L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	16	25	Reed Coil	8.105 -\ncap:70	1543
811	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	1	5	Reed Coil	\N	1544
812	Fall	2025	1S	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	12	25	Philipp\nSchroeder	8.321 -\ncap:32	1545
813	Fall	2025	1S	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	20	25	Philipp\nSchroeder	8.321 -\ncap:32	1546
813	Fall	2025	2S	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	20	25	Philipp\nSchroeder	8.321 -\ncap:32	1547
814	Fall	2025	1R	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	2	10	Dana\nBurkhanova	8.154 -\ncap:56	1548
815	Fall	2025	1L	2025-08-18	2025-11-28	R	02:00 PM-05:00 PM	7	12	Assem\nSeidalina, Mirat\nAkshalov,\nJaehyeon Kim	(C3) 1009 -\ncap:70	1549
816	Fall	2025	1L	2025-08-18	2025-11-28	F	02:00 PM-05:00 PM	7	12	Mirat Akshalov,\nMustafa Karatas	(C3) 1009 -\ncap:70	1550
817	Fall	2025	1L	2025-08-18	2025-11-28	M	02:00 PM-05:00 PM	7	12	Mirat Akshalov,\nJiyang Dong	(C3) 1009 -\ncap:70	1551
818	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	1	2	Mirat Akshalov,\nJiyang Dong	\N	1552
23	Fall	2025	5L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	83	90	Radmir\nSarsenov	5.103 -\ncap:160	1553
23	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	88	90	Sergey Yegorov	7E.529 -\ncap:95	1554
23	Fall	2025	2L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	85	90	Burkitkan Akbay	7E.529 -\ncap:95	1555
23	Fall	2025	3L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	85	90	Zarina\nSautbayeva	7E.529 -\ncap:95	1556
23	Fall	2025	4L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	88	90	Nurtilek\nGalimov	7E.529 -\ncap:95	1557
819	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	90	90	Radmir\nSarsenov	7E.529 -\ncap:95	1558
59	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	13	40	Olena\nFilchakova	7E.529 -\ncap:95	1559
61	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	65	75	Alexandr Pak	7E.529 -\ncap:95	1560
820	Fall	2025	2Lb	2025-08-18	2025-11-28	T	03:00 PM-05:50 PM	16	16	Nurtilek\nGalimov	7.407 -\ncap:20	1561
820	Fall	2025	1Lb	2025-08-18	2025-11-28	W	12:00 PM-02:50 PM	17	16	Zarina\nSautbayeva	7.410 -\ncap:15	1562
820	Fall	2025	3Lb	2025-08-18	2025-11-28	W	03:00 PM-05:50 PM	17	16	Zarina\nSautbayeva	7.410 -\ncap:15	1563
820	Fall	2025	4Lb	2025-08-18	2025-11-28	T	03:00 PM-05:50 PM	7	16	Radmir\nSarsenov	7.410 -\ncap:15	1564
62	Fall	2025	1R	2025-08-18	2025-11-28	M	04:00 PM-04:50 PM	18	20	Sergey Yegorov	7E.217 -\ncap:24	1565
62	Fall	2025	2R	2025-08-18	2025-11-28	M	05:00 PM-05:50 PM	18	20	Sergey Yegorov	7E.217 -\ncap:24	1566
62	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	36	40	Tursonjan Tokay	7E.529 -\ncap:95	1567
63	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	38	40	Ivan Vorobyev	7.105 -\ncap:75	1568
65	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	46	45	Damira\nKanayeva	7.105 -\ncap:75	1569
66	Fall	2025	1Lb	2025-08-18	2025-11-28	W	10:00 AM-12:50 PM	19	20	Burkitkan Akbay	7.407 -\ncap:20	1570
66	Fall	2025	2Lb	2025-08-18	2025-11-28	R	12:00 PM-02:50 PM	18	20	Nurtilek\nGalimov	7.407 -\ncap:20	1571
66	Fall	2025	3Lb	2025-08-18	2025-11-28	W	03:00 PM-05:50 PM	14	20	Burkitkan Akbay	7.407 -\ncap:20	1572
67	Fall	2025	1L	2025-08-18	2025-11-28	T	12:00 PM-02:50 PM	7	24	Timo Burster	7.517 -\ncap:25	1573
821	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	7	24	Zhanat\nMuminova	7.105 -\ncap:75	1574
68	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	15	40	Otilia Nuta	7.105 -\ncap:75	1575
822	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	15	24	Ulykbek Kairov	7E.217 -\ncap:24	1576
71	Fall	2025	1L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	43	48	Timo Burster	7.105 -\ncap:75	1577
72	Fall	2025	4L	2025-08-18	2025-11-28	T	10:00 AM-11:15 AM	50	55	Jeanette Kunz\nHalder, Kamilya\nKokabi	NUSOM\nBuilding -\ncap:0	1578
72	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	13	24	yingqiu Xie	7E.546/1 -\ncap:25	1579
72	Fall	2025	3L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	16	24	yingqiu Xie	7E.546/1 -\ncap:25	1580
823	Fall	2025	1L	2025-08-18	2025-11-28	F	12:00 PM-02:50 PM	24	24	Ferdinand\nMolnar	7E.545/1 -\ncap:25	1581
823	Fall	2025	1Lb	2025-08-18	2025-11-28	M	12:00 PM-02:50 PM	24	24	Ferdinand\nMolnar	7E.545/1 -\ncap:25	1582
73	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	38	40	Zhanat\nMuminova	7E.529 -\ncap:95	1583
824	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	32	36	Tursonjan Tokay	7.105 -\ncap:75	1584
825	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	31	40	Alexandr Pak	7E.125/2 -\ncap:56	1585
826	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	43	50	Eugene\nPonomarev	7.105 -\ncap:75	1586
827	Fall	2025	2S	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	20	24	Tri Pham	7.105 -\ncap:75	1587
827	Fall	2025	4S	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	32	24	Eugene\nPonomarev	7.105 -\ncap:75	1588
828	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	23	24	Zhanat\nMuminova	7.105 -\ncap:75	1589
829	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	2	24	Ivan Vorobyev	7.105 -\ncap:75	1590
830	Fall	2025	1R	2025-08-18	2025-11-28	\N	Online/Distant	8	24	Olena\nFilchakova	\N	1591
81	Fall	2025	1Wsh	2025-08-18	2025-11-28	\N	Online/Distant	1	1	Dos Sarbassov	\N	1592
20	Fall	2025	10R	2025-08-18	2025-11-28	W	11:00 AM-11:50 AM	46	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 2002 -\ncap:66	1593
20	Fall	2025	1L	2025-08-18	2025-11-28	F	12:00 PM-12:50 PM	539	561	Mirat Akshalov,\nSaniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	Orange Hall\n- cap:450	1594
20	Fall	2025	1R	2025-08-18	2025-11-28	T	09:00 AM-09:50 AM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1595
20	Fall	2025	2R	2025-08-18	2025-11-28	T	10:00 AM-10:50 AM	47	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1596
20	Fall	2025	4R	2025-08-18	2025-11-28	T	11:00 AM-11:50 AM	46	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1597
20	Fall	2025	5R	2025-08-18	2025-11-28	T	12:00 PM-12:50 PM	47	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1598
20	Fall	2025	6R	2025-08-18	2025-11-28	T	01:00 PM-01:50 PM	42	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1599
20	Fall	2025	7R	2025-08-18	2025-11-28	W	09:00 AM-09:50 AM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1600
20	Fall	2025	8R	2025-08-18	2025-11-28	W	10:00 AM-10:50 AM	46	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1601
20	Fall	2025	9R	2025-08-18	2025-11-28	W	11:00 AM-11:50 AM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1602
20	Fall	2025	11R	2025-08-18	2025-11-28	W	12:00 PM-12:50 PM	48	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1603
20	Fall	2025	12R	2025-08-18	2025-11-28	W	01:00 PM-01:50 PM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	1604
20	Fall	2025	3R	2025-08-18	2025-11-28	T	11:00 AM-11:50 AM	21	22	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 3017 -\ncap:38	1605
831	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	64	70	Elnara\nKussinova	3.302 -\ncap:70	1606
831	Fall	2025	1T	2025-08-18	2025-11-28	F	09:00 AM-09:50 AM	63	70	Elnara\nKussinova	3.302 -\ncap:70	1607
831	Fall	2025	2L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	75	82	Asma Perveen	3E.224 -\ncap:85	1608
831	Fall	2025	2T	2025-08-18	2025-11-28	M	02:00 PM-02:50 PM	76	82	Asma Perveen	3E.224 -\ncap:85	1609
831	Fall	2025	1Lb	2025-08-18	2025-11-28	W	04:30 PM-05:45 PM	33	35	Elnara\nKussinova	3E.328 -\ncap:20	1610
831	Fall	2025	2Lb	2025-08-18	2025-11-28	R	03:00 PM-04:15 PM	31	35	Elnara\nKussinova	3E.328 -\ncap:20	1611
831	Fall	2025	3Lb	2025-08-18	2025-11-28	M	03:00 PM-04:45 PM	35	41	Asma Perveen	3E.328 -\ncap:20	1612
831	Fall	2025	4Lb	2025-08-18	2025-11-28	W	01:30 PM-02:45 PM	40	41	Asma Perveen	3E.328 -\ncap:20	1613
832	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	66	65	Mert Guney	3E.220 -\ncap:85	1614
832	Fall	2025	1T	2025-08-18	2025-11-28	W	09:00 AM-09:50 AM	66	65	Mert Guney	3E.220 -\ncap:85	1615
832	Fall	2025	1Lb	2025-08-18	2025-11-28	F	03:00 PM-05:45 PM	33	32	Mert Guney	3E.120 -\ncap:20	1616
832	Fall	2025	2Lb	2025-08-18	2025-11-28	M	03:00 PM-05:45 PM	33	33	Mert Guney	3E.120 -\ncap:20	1617
833	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	66	65	Bakhyt\nAubakirova	2.302 -\ncap:78	1618
833	Fall	2025	1CLb	2025-10-14	2025-10-14	T T T T T T\nT	03:00 PM-04:15 PM	20	20	Bakhyt\nAubakirova	3E.217 -\ncap:28	1619
833	Fall	2025	2CLb	2025-10-15	2025-10-15	W W W W\nW W W	03:00 PM-04:15 PM	23	22	Bakhyt\nAubakirova	3E.217 -\ncap:28	1620
833	Fall	2025	3CLb	2025-10-16	2025-10-16	R R R R R\nR R	04:30 PM-05:45 PM	23	23	Bakhyt\nAubakirova	3E.217 -\ncap:28	1621
833	Fall	2025	1Lb	2025-08-19	2025-08-19	T T T T T T\nT	03:00 PM-04:15 PM	21	20	Bakhyt\nAubakirova	3E.143 -\ncap:14	1622
833	Fall	2025	2Lb	2025-08-20	2025-08-20	W W W W\nW W W	03:00 PM-04:15 PM	23	22	Bakhyt\nAubakirova	3E.143 -\ncap:14	1623
833	Fall	2025	3Lb	2025-08-21	2025-08-21	R R R R R\nR R	04:30 PM-05:45 PM	22	23	Bakhyt\nAubakirova	3E.143 -\ncap:14	1624
834	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	59	60	Shazim Memon	3E.223 -\ncap:63	1625
834	Fall	2025	1T	2025-08-18	2025-11-28	F	04:30 PM-05:20 PM	59	60	Shazim Memon	3E.223 -\ncap:63	1626
835	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	55	60	Sung Moon	3E.220 -\ncap:85	1627
835	Fall	2025	1Lb	2025-08-18	2025-11-28	M	03:00 PM-04:15 PM	27	30	Sung Moon	3E.129 -\ncap:25	1628
835	Fall	2025	2Lb	2025-08-18	2025-11-28	F	03:00 PM-04:15 PM	28	30	Sung Moon	3E.129 -\ncap:25	1629
836	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	53	60	Ferhat Karaca	3E.223 -\ncap:63	1630
836	Fall	2025	1T	2025-08-18	2025-11-28	W	12:00 PM-12:50 PM	53	60	Ferhat Karaca	3E.223 -\ncap:63	1631
837	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	53	60	Chang Shon	3E.220 -\ncap:85	1632
837	Fall	2025	1Lb	2025-08-18	2025-11-28	M	04:30 PM-06:15 PM	15	20	Chang Shon	3E.136 -\ncap:22	1633
837	Fall	2025	2Lb	2025-08-18	2025-11-28	T	04:30 PM-06:15 PM	18	20	Chang Shon	3E.136 -\ncap:22	1634
837	Fall	2025	3Lb	2025-08-18	2025-11-28	W	04:30 PM-06:15 PM	20	20	Chang Shon	3E.136 -\ncap:22	1635
838	Fall	2025	1T	2025-08-18	2025-11-28	W	04:30 PM-05:15 PM	66	70	Abid Nadeem	3E.220 -\ncap:85	1636
838	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	66	70	Abid Nadeem	3E.224 -\ncap:85	1637
839	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	19	35	Dichuan Zhang	3.303 -\ncap:32	1638
839	Fall	2025	1P	2025-08-18	2025-11-28	F	01:00 PM-01:50 PM	19	35	Dichuan Zhang	3.303 -\ncap:32	1639
840	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	46	35	Ferhat Karaca	3.309 -\ncap:40	1640
840	Fall	2025	1T	2025-08-18	2025-11-28	W	03:00 PM-03:50 PM	46	35	Ferhat Karaca	3.309 -\ncap:40	1641
841	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	27	35	Chang Shon	3.407 -\ncap:40	1642
841	Fall	2025	1P	2025-08-18	2025-11-28	F	03:00 PM-03:50 PM	27	35	Chang Shon	3.407 -\ncap:40	1643
109	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	15	20	Jong Kim,\nBakhyt\nAubakirova	3.303 -\ncap:32	1644
842	Fall	2025	1Lb	2025-08-18	2025-11-28	M	04:30 PM-05:45 PM	42	35	Alfrendo\nSatyanaga	3.323 -\ncap:64	1645
842	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-09:50 AM	42	35	Alfrendo\nSatyanaga	3.407 -\ncap:40	1646
32	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	68	70	Zhannat\nAshikbayeva	7.105 -\ncap:75	1647
32	Fall	2025	2L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	50	50	Zhannat\nAshikbayeva	7E.429 -\ncap:90	1648
113	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	28	65	Khalil Amro	9.105 -\ncap:75	1649
113	Fall	2025	2L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	65	65	Aisulu\nZhanbossinova	9.105 -\ncap:75	1650
113	Fall	2025	5L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	62	65	Roza Oztopcu	9.105 -\ncap:75	1651
113	Fall	2025	4L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	64	65	Akmaral\nSuleimenova	5.103 -\ncap:160	1652
113	Fall	2025	6L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	62	65	Rauan Smail	5.103 -\ncap:160	1653
113	Fall	2025	3L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	52	65	Aigerim\nGalyamova	8.522 -\ncap:72	1654
114	Fall	2025	1ChLb	2025-08-18	2025-11-28	W	09:00 AM-11:50 AM	21	24	Roza Oztopcu	9.210 -\ncap:40	1655
114	Fall	2025	2ChLb	2025-08-18	2025-11-28	W	12:00 PM-02:50 PM	4	24	Aliya Toleuova	9.210 -\ncap:40	1656
114	Fall	2025	3ChLb	2025-08-18	2025-11-28	M	09:00 AM-11:50 AM	16	24	Roza Oztopcu	9.210 -\ncap:40	1657
114	Fall	2025	4ChLb	2025-08-18	2025-11-28	W	03:00 PM-05:50 PM	21	24	Aisulu\nZhanbossinova	9.210 -\ncap:40	1658
114	Fall	2025	5ChLb	2025-08-18	2025-11-28	M	12:00 PM-02:50 PM	10	24	Sandugash\nKalybekkyzy	9.210 -\ncap:40	1659
114	Fall	2025	6ChLb	2025-08-18	2025-11-28	M	03:00 PM-05:50 PM	11	24	Rauan Smail	9.210 -\ncap:40	1660
114	Fall	2025	7ChLb	2025-08-18	2025-11-28	F	09:00 AM-11:50 AM	22	24	Roza Oztopcu	9.210 -\ncap:40	1661
114	Fall	2025	8ChLb	2025-08-18	2025-11-28	F	12:00 PM-02:50 PM	10	24	Aliya Toleuova	9.210 -\ncap:40	1662
114	Fall	2025	9ChLb	2025-08-18	2025-11-28	F	03:00 PM-05:50 PM	11	24	Akmaral\nSuleimenova	9.210 -\ncap:40	1663
114	Fall	2025	10ChLb	2025-08-18	2025-11-28	T	09:00 AM-11:50 AM	20	24	Akmaral\nSuleimenova	9.210 -\ncap:40	1664
114	Fall	2025	11ChLb	2025-08-18	2025-11-28	T	12:00 PM-02:50 PM	17	24	Zhannat\nAshikbayeva	9.210 -\ncap:40	1665
114	Fall	2025	12ChLb	2025-08-18	2025-11-28	T	03:00 PM-05:50 PM	13	24	Rauan Smail	9.210 -\ncap:40	1666
114	Fall	2025	13ChLb	2025-08-18	2025-11-28	R	09:00 AM-11:50 AM	14	24	Rauan Smail	9.210 -\ncap:40	1667
115	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	8	20	Aliya Toleuova	7E.220 -\ncap:56	1668
843	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	58	60	Timur Atabaev	9.105 -\ncap:75	1669
118	Fall	2025	3L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	34	40	Irshad\nKammakakam	7E.221 -\ncap:56	1670
118	Fall	2025	4L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	11	40	Salimgerey\nAdilov	8.522 -\ncap:72	1671
118	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	19	40	Ahmed\nElkamhawy	7E.125/2 -\ncap:56	1672
118	Fall	2025	2L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	39	40	Irshad\nKammakakam	7E.125/2 -\ncap:56	1673
119	Fall	2025	2Lb	2025-08-18	2025-11-28	M	02:00 PM-04:50 PM	22	24	Ozgur Oztopcu	7.307 -\ncap:15	1674
119	Fall	2025	3Lb	2025-08-18	2025-11-28	W	02:00 PM-04:50 PM	21	24	Ozgur Oztopcu	7.307 -\ncap:15	1675
119	Fall	2025	4Lb	2025-08-18	2025-11-28	T	02:00 PM-04:50 PM	6	24	Ellina Mun	7.307 -\ncap:15	1676
119	Fall	2025	5Lb	2025-08-18	2025-11-28	R	09:00 AM-11:50 AM	8	24	Ozgur Oztopcu	7.307 -\ncap:15	1677
120	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	14	34	Davit\nHayrapetyan	7E.221 -\ncap:56	1678
121	Fall	2025	1ChLb	2025-08-18	2025-11-28	T	09:00 AM-11:50 AM	12	24	Davit\nHayrapetyan	7.307 -\ncap:15	1679
844	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	32	24	Rostislav\nBukasov	7E.221 -\ncap:56	1680
845	Fall	2025	1ChLb	2025-08-18	2025-11-28	R	03:00 PM-05:50 PM	24	24	Aliya Toleuova	9.210 -\ncap:40	1681
846	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	26	30	Haiyan Fan	7E.221 -\ncap:56	1682
847	Fall	2025	1ChLb	2025-08-18	2025-11-28	R	03:00 PM-05:50 PM	22	24	Haiyan Fan	7.310 -\ncap:15	1683
848	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	32	24	Ahmed\nElkamhawy	7E.221 -\ncap:56	1684
849	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	26	24	Andrey\nKhalimon	7E.221 -\ncap:56	1685
850	Fall	2025	1Lb	2025-08-18	2025-11-28	F	03:00 PM-05:50 PM	24	24	Aisulu\nZhanbossinova	7.310 -\ncap:15	1686
851	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	11	30	Salimgerey\nAdilov	8.522 -\ncap:72	1687
852	Fall	2025	1L	2025-08-18	2025-11-28	M	03:00 PM-05:50 PM	5	30	Mannix Balanay	7E.221 -\ncap:56	1688
853	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	27	30	Ellina Mun,\nAhmed\nElkamhawy	7E.221 -\ncap:56	1689
854	Fall	2025	1L	2025-08-18	2025-11-28	W	03:00 PM-05:50 PM	27	30	Mannix Balanay	7E.221 -\ncap:56	1690
855	Fall	2025	1Lb	2025-08-18	2025-11-28	\N	Online/Distant	16	24	Timur Atabaev	\N	1691
856	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	30	30	Cevat Erisken	3.317 -\ncap:40	1692
856	Fall	2025	1R	2025-08-18	2025-11-28	M	01:00 PM-01:50 PM	30	30	Cevat Erisken	3.317 -\ncap:40	1693
857	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	30	30	Nurxat Nuraje	3.316 -\ncap:40	1694
857	Fall	2025	1R	2025-08-18	2025-11-28	W	01:00 PM-01:50 PM	30	30	Nurxat Nuraje	3.317 -\ncap:40	1695
858	Fall	2025	1Lb	2025-08-18	2025-11-28	T	02:00 PM-03:45 PM	16	15	Almagul\nMentbayeva,\nLyazzat\nMukhangaliyeva	3.143 -\ncap:20	1696
858	Fall	2025	2Lb	2025-08-18	2025-11-28	R	02:00 PM-03:45 PM	15	15	Almagul\nMentbayeva,\nLyazzat\nMukhangaliyeva	3.143 -\ncap:20	1697
858	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	31	30	Almagul\nMentbayeva,\nLyazzat\nMukhangaliyeva	3.407 -\ncap:40	1698
859	Fall	2025	1T	2025-08-18	2025-11-28	M	02:00 PM-03:00 PM	23	30	Sergey Spotar	3.302 -\ncap:70	1699
859	Fall	2025	1L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	23	30	Sergey Spotar	3.309 -\ncap:40	1700
860	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	29	30	Boris Golman,\nSabina\nKhamzina	3.316 -\ncap:40	1701
860	Fall	2025	1Lb	2025-08-18	2025-11-28	R	05:00 PM-05:50 PM	29	30	Boris Golman,\nSabina\nKhamzina	7E.125/3 -\ncap:98	1702
861	Fall	2025	1Lb	2025-08-18	2025-11-28	W	02:00 PM-03:45 PM	22	30	Chang-Keun Lim	3.143 -\ncap:20	1703
861	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	22	30	Chang-Keun Lim	3.316 -\ncap:40	1704
862	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	18	15	Stavros\nPoulopoulos	3E.221 -\ncap:50	1705
863	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	20	20	Azhar\nMukasheva	3.322 -\ncap:40	1706
863	Fall	2025	1Lb	2025-08-18	2025-11-28	M	03:00 PM-04:45 PM	20	20	Azhar\nMukasheva	3E.422 -\ncap:20	1707
864	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	32	25	Aishuak\nKonarov	3.322 -\ncap:40	1708
864	Fall	2025	1Lb	2025-08-18	2025-11-28	R	02:00 PM-03:45 PM	32	25	Aishuak\nKonarov	3E.422 -\ncap:20	1709
865	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	48	50	Dhawal Shah	3.323 -\ncap:64	1710
865	Fall	2025	1Lb	2025-08-18	2025-11-28	W	03:00 PM-04:45 PM	33	50	Dhawal Shah	online -\ncap:0	1711
865	Fall	2025	2Lb	2025-08-18	2025-11-28	F	03:00 PM-04:45 PM	15	50	Dhawal Shah	online -\ncap:0	1712
866	Fall	2025	1Lb	2025-08-18	2025-11-28	M	09:00 AM-10:45 AM	14	12	Azhar\nMukasheva	3E.429 -\ncap:15	1713
866	Fall	2025	2Lb	2025-08-18	2025-11-28	W	09:00 AM-10:45 AM	13	12	Azhar\nMukasheva	3E.429 -\ncap:15	1714
866	Fall	2025	3Lb	2025-08-18	2025-11-28	F	09:00 AM-10:45 AM	14	12	Azhar\nMukasheva	3E.429 -\ncap:15	1715
866	Fall	2025	4Lb	2025-08-18	2025-11-28	R	11:00 AM-12:45 PM	7	12	Azhar\nMukasheva	3E.429 -\ncap:15	1716
867	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	32	25	Sergey Spotar	3.416 -\ncap:46	1717
867	Fall	2025	1Lb	2025-08-18	2025-11-28	T	04:15 PM-06:00 PM	32	25	Sergey Spotar	3E.217 -\ncap:28	1718
868	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	12:00 PM-12:50 PM	26	24	Lili Zhang	8.508 -\ncap:27	1719
868	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	01:00 PM-01:50 PM	23	24	Lili Zhang	8.508 -\ncap:27	1720
869	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	02:00 PM-02:50 PM	15	24	Lili Zhang	8.508 -\ncap:27	1721
163	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	29	30	Irina Dolzhikova	7.422 -\ncap:30	1722
163	Fall	2025	2L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	26	30	Talgat\nManglayev	7.422 -\ncap:30	1723
163	Fall	2025	3L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	26	30	Syed\nMuhammad\nUmair Arif	7.422 -\ncap:30	1724
164	Fall	2025	1L	2025-08-18	2025-11-28	W	02:00 PM-02:50 PM	96	100	Minho Lee	7E.429 -\ncap:90	1725
164	Fall	2025	2L	2025-08-18	2025-11-28	W	03:00 PM-03:50 PM	100	100	Sain Saginbekov	7E.429 -\ncap:90	1726
164	Fall	2025	3L	2025-08-18	2025-11-28	W	04:00 PM-04:50 PM	94	100	Saida\nMussakhojayeva	7E.429 -\ncap:90	1727
164	Fall	2025	4L	2025-08-18	2025-11-28	W	05:00 PM-05:50 PM	97	100	Anwar Ghani	7E.429 -\ncap:90	1728
164	Fall	2025	1Lb	2025-08-18	2025-11-28	M	02:00 PM-02:50 PM	79	80	Marat Isteleyev	7E.125/3 -\ncap:98	1729
164	Fall	2025	2Lb	2025-08-18	2025-11-28	M	03:00 PM-03:50 PM	77	80	Marat Isteleyev	7E.125/3 -\ncap:98	1730
164	Fall	2025	3Lb	2025-08-18	2025-11-28	M	04:00 PM-04:50 PM	78	80	Marat Isteleyev,\nAdai Shomanov	7E.125/3 -\ncap:98	1731
164	Fall	2025	4Lb	2025-08-18	2025-11-28	M	05:00 PM-05:50 PM	75	80	Adai Shomanov	7E.125/3 -\ncap:98	1732
164	Fall	2025	5Lb	2025-08-18	2025-11-28	M	06:00 PM-06:50 PM	78	80	Adai Shomanov	7E.125/3 -\ncap:98	1733
3	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	98	96	Antonio Cerone	7E.429 -\ncap:90	1734
3	Fall	2025	2L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	131	120	Shinnazar\nSeytnazarov	7E.429 -\ncap:90	1735
3	Fall	2025	3L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	97	96	Muhammed\nDemirci	7E.429 -\ncap:90	1736
3	Fall	2025	1CLb	2025-08-18	2025-11-28	M	09:00 AM-09:50 AM	77	82	Adai Shomanov	7E.125/3 -\ncap:98	1737
3	Fall	2025	2CLb	2025-08-18	2025-11-28	M	10:00 AM-10:50 AM	79	82	Adai Shomanov	7E.125/3 -\ncap:98	1738
3	Fall	2025	3CLb	2025-08-18	2025-11-28	M	11:00 AM-11:50 AM	83	82	Irina Dolzhikova	7E.125/3 -\ncap:98	1739
3	Fall	2025	4CLb	2025-08-18	2025-11-28	M	12:00 PM-12:50 PM	87	82	Irina Dolzhikova	7E.125/3 -\ncap:98	1740
9	Fall	2025	1L	2025-08-18	2025-11-28	M	11:00 AM-11:50 AM	89	100	Shinnazar\nSeytnazarov	7E.429 -\ncap:90	1741
9	Fall	2025	2L	2025-08-18	2025-11-28	M	12:00 PM-12:50 PM	83	100	Hashim Ali	7E.429 -\ncap:90	1742
9	Fall	2025	3L	2025-08-18	2025-11-28	M	11:00 AM-11:50 AM	46	100	Hari Mohan Rai	7E.429 -\ncap:90	1743
9	Fall	2025	1Lb	2025-08-18	2025-11-28	F	09:00 AM-09:50 AM	29	75	Asset Berdibek	7E.125/3 -\ncap:98	1744
9	Fall	2025	2Lb	2025-08-18	2025-11-28	F	10:00 AM-10:50 AM	62	75	Asset Berdibek	7E.125/3 -\ncap:98	1745
9	Fall	2025	3Lb	2025-08-18	2025-11-28	F	11:00 AM-11:50 AM	68	75	Iliyas Tursynbek	7E.125/3 -\ncap:98	1746
9	Fall	2025	4Lb	2025-08-18	2025-11-28	F	12:00 PM-12:50 PM	59	75	Iliyas Tursynbek	7E.125/3 -\ncap:98	1747
12	Fall	2025	1L	2025-08-18	2025-11-28	R	12:00 PM-01:15 PM	146	150	Ben Tyler	7E.429 -\ncap:90	1748
12	Fall	2025	2L	2025-08-18	2025-11-28	R	01:30 PM-02:45 PM	88	150	Jean Marie\nGuillaume\nGerard de\nNivelle	7E.429 -\ncap:90	1749
12	Fall	2025	1Lb	2025-08-18	2025-11-28	F	01:00 PM-01:50 PM	66	75	Aigerim\nYessenbayeva	7E.125/3 -\ncap:98	1750
12	Fall	2025	2Lb	2025-08-18	2025-11-28	F	02:00 PM-02:50 PM	74	75	Aigerim\nYessenbayeva	7E.125/3 -\ncap:98	1751
12	Fall	2025	3Lb	2025-08-18	2025-11-28	F	03:00 PM-03:50 PM	52	75	Iliyas Tursynbek	7E.125/3 -\ncap:98	1752
12	Fall	2025	4Lb	2025-08-18	2025-11-28	F	04:00 PM-04:50 PM	42	75	Iliyas Tursynbek	7E.125/3 -\ncap:98	1753
167	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	12	32	Antonio Cerone	7.422 -\ncap:30	1754
31	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	17	50	Ben Tyler	\N	1755
21	Fall	2025	1L	2025-08-18	2025-11-28	F	01:00 PM-01:50 PM	91	94	Meiram\nMurzabulatov	7E.429 -\ncap:90	1756
21	Fall	2025	2L	2025-08-18	2025-11-28	F	02:00 PM-02:50 PM	93	94	Adnan Yazici	7E.429 -\ncap:90	1757
21	Fall	2025	3L	2025-08-18	2025-11-28	F	01:00 PM-01:50 PM	72	94	Yesdaulet\nIzenov	7E.429 -\ncap:90	1758
870	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	27	32	Park, Jurn Gyu	7.522 -\ncap:30	1759
871	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	20	32	de Nivelle, Jean\nMarie\nGuillaume\nGerard	7.522 -\ncap:30	1760
24	Fall	2025	1L	2025-08-18	2025-11-28	M	03:00 PM-03:45 PM	132	140	Askar\nBoranbayev	7E.429 -\ncap:90	1761
24	Fall	2025	2L	2025-08-18	2025-11-28	M	04:00 PM-04:50 PM	127	140	Askar\nBoranbayev	7E.429 -\ncap:90	1762
24	Fall	2025	1Lb	2025-08-18	2025-11-28	R	09:00 AM-09:50 AM	64	75	Marat Isteleyev	7E.125/3 -\ncap:98	1763
24	Fall	2025	2Lb	2025-08-18	2025-11-28	R	10:00 AM-10:50 AM	50	75	Marat Isteleyev	7E.125/3 -\ncap:98	1764
24	Fall	2025	3Lb	2025-08-18	2025-11-28	R	11:00 AM-11:50 AM	73	75	Syed\nMuhammad\nUmair Arif	7E.125/3 -\ncap:98	1765
24	Fall	2025	4Lb	2025-08-18	2025-11-28	R	12:00 PM-12:50 PM	72	75	Syed\nMuhammad\nUmair Arif	7E.125/3 -\ncap:98	1766
872	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	43	40	Marko Ristin	3.416 -\ncap:46	1767
19	Fall	2025	3L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	79	94	Khalil Khan	2.302 -\ncap:78	1768
19	Fall	2025	1L	2025-08-18	2025-11-28	T	01:30 PM-02:45 PM	92	94	Anh Tu Nguyen	7E.429 -\ncap:90	1769
19	Fall	2025	2L	2025-08-18	2025-11-28	T	03:00 PM-04:15 PM	93	94	Minho Lee	7E.429 -\ncap:90	1770
33	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	47	32	Lisa Chalaguine	7.422 -\ncap:30	1771
30	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	27	50	Ben Tyler	\N	1772
35	Fall	2025	1L	2025-08-18	2025-11-28	F	06:00 PM-06:50 PM	235	260	Askar\nBoranbayev,\nEnver Ever	online -\ncap:0	1773
873	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	19	24	Talgat\nManglayev	7E.125/3 -\ncap:98	1774
874	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	41	40	Anwar Ghani	7E.220 -\ncap:56	1775
173	Fall	2025	1L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	38	40	Dimitrios\nZormpas	7E.220 -\ncap:56	1776
174	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	37	32	Hari Mohan Rai	3.317 -\ncap:40	1777
875	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	19	40	Murzabulatov,\nMeiram	7E.220 -\ncap:56	1778
876	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	75	32	Siamac Fazli	3E.220 -\ncap:85	1779
230	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	11:00 AM-11:50 AM	22	24	Bastiaan\nLohmann	8.305 -\ncap:30	1780
230	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	12:00 PM-12:50 PM	23	24	Bastiaan\nLohmann	8.305 -\ncap:30	1781
230	Fall	2025	3L	2025-08-18	2025-11-28	M T W R	01:00 PM-01:50 PM	17	24	Bastiaan\nLohmann	8.305 -\ncap:30	1782
246	Fall	2025	1T	2025-08-18	2025-11-28	M	06:00 PM-06:50 PM	61	65	Aigerim\nSarsenbayeva	8.327 -\ncap:55	1783
246	Fall	2025	2T	2025-08-18	2025-11-28	M	07:00 PM-07:50 PM	42	65	Aigerim\nSarsenbayeva	8.327 -\ncap:55	1784
246	Fall	2025	3T	2025-08-18	2025-11-28	W	06:00 PM-06:50 PM	62	65	Aigerim\nSarsenbayeva	8.327 -\ncap:55	1785
246	Fall	2025	4T	2025-08-18	2025-11-28	W	07:00 PM-07:50 PM	63	65	Levent\nKockesen	8.327 -\ncap:55	1786
246	Fall	2025	5T	2025-08-18	2025-11-28	F	06:00 PM-06:50 PM	58	65	Levent\nKockesen	8.327 -\ncap:55	1787
246	Fall	2025	6T	2025-08-18	2025-11-28	F	07:00 PM-07:50 PM	46	65	Levent\nKockesen	8.327 -\ncap:55	1788
246	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	168	170	Aigerim\nSarsenbayeva	Blue Hall -\ncap:239	1789
246	Fall	2025	2L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	164	170	Levent\nKockesen	Blue Hall -\ncap:239	1790
247	Fall	2025	1T	2025-08-18	2025-11-28	T	06:00 PM-06:50 PM	57	65	Dana\nBazarkulova	8.327 -\ncap:55	1791
247	Fall	2025	2T	2025-08-18	2025-11-28	T	07:00 PM-07:50 PM	52	65	Dana\nBazarkulova	8.327 -\ncap:55	1792
247	Fall	2025	3T	2025-08-18	2025-11-28	R	06:00 PM-06:50 PM	52	65	Dana\nBazarkulova	8.327 -\ncap:55	1793
247	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	161	170	Dana\nBazarkulova	Blue Hall -\ncap:239	1794
248	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	184	200	Aigerim\nSarsenbayeva	Blue Hall -\ncap:239	1795
249	Fall	2025	1T	2025-08-18	2025-11-28	M	06:00 PM-06:50 PM	50	50	Oleg Rubanov	8.307 -\ncap:70	1796
249	Fall	2025	2T	2025-08-18	2025-11-28	M	07:00 PM-07:50 PM	34	50	Oleg Rubanov	8.307 -\ncap:70	1797
249	Fall	2025	3T	2025-08-18	2025-11-28	T	06:00 PM-06:50 PM	46	50	Oleg Rubanov	8.105 -\ncap:70	1798
249	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	130	130	Oleg Rubanov	Blue Hall -\ncap:239	1799
251	Fall	2025	2T	2025-08-18	2025-11-28	W	06:00 PM-06:50 PM	49	50	Vladyslav Nora	8.307 -\ncap:70	1800
251	Fall	2025	3T	2025-08-18	2025-11-28	W	07:00 PM-07:50 PM	32	50	Vladyslav Nora	8.307 -\ncap:70	1801
251	Fall	2025	1T	2025-08-18	2025-11-28	T	07:00 PM-07:50 PM	48	50	Vladyslav Nora	8.105 -\ncap:70	1802
251	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	129	130	Vladyslav Nora	Senate Hall\n- cap:144	1803
252	Fall	2025	2Int	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Aigerim\nSarsenbayeva	\N	1804
252	Fall	2025	4Int	2025-08-18	2025-11-28	\N	Online/Distant	1	5	Alejandro Melo\nPonce	\N	1805
252	Fall	2025	5Int	2025-08-18	2025-11-28	\N	Online/Distant	3	5	Nino Buliskeria	\N	1806
252	Fall	2025	6Int	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Rajarshi Bhowal	\N	1807
252	Fall	2025	9Int	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Vladyslav Nora	\N	1808
252	Fall	2025	10Int	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Dana\nBazarkulova	\N	1809
253	Fall	2025	3T	2025-08-18	2025-11-28	F	06:00 PM-06:50 PM	40	50	Nino Buliskeria	8.307 -\ncap:70	1810
253	Fall	2025	1T	2025-08-18	2025-11-28	R	06:00 PM-06:50 PM	47	50	Nino Buliskeria	8.105 -\ncap:70	1811
253	Fall	2025	2T	2025-08-18	2025-11-28	R	07:00 PM-07:50 PM	41	50	Nino Buliskeria	8.105 -\ncap:70	1812
253	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	128	130	Nino Buliskeria	Blue Hall -\ncap:239	1813
877	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	26	35	Okan Yilankaya	8.327 -\ncap:55	1814
877	Fall	2025	2L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	23	35	Okan Yilankaya	8.327 -\ncap:55	1815
878	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	32	35	Oleg Rubanov	8.307 -\ncap:70	1816
879	Fall	2025	2L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	36	30	Andrey\nTkachenko	8.307 -\ncap:70	1817
879	Fall	2025	3L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	35	34	Andrey\nTkachenko	8.307 -\ncap:70	1818
880	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	38	40	Giulio Seccia	8.307 -\ncap:70	1819
881	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	28	35	Ahmet Altinok	8.327 -\ncap:55	1820
881	Fall	2025	2L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	31	35	Ahmet Altinok	8.327 -\ncap:55	1821
882	Fall	2025	1S	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	1	5	Nino Buliskeria	8.327 -\ncap:55	1822
259	Fall	2025	1IS	2025-08-18	2025-11-28	\N	Online/Distant	3	5	Andrey\nTkachenko	\N	1823
259	Fall	2025	4IS	2025-08-18	2025-11-28	\N	Online/Distant	3	5	Nino Buliskeria	\N	1824
259	Fall	2025	6IS	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Rajarshi Bhowal	\N	1825
259	Fall	2025	7IS	2025-08-18	2025-11-28	\N	Online/Distant	1	5	Vladyslav Nora	\N	1826
883	Fall	2025	2L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	11	26	Alejandro Melo\nPonce	7E.220 -\ncap:56	1827
883	Fall	2025	1L	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	16	30	Alejandro Melo\nPonce	7E.329 -\ncap:95	1828
884	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	29	30	Ali Elminejad	8.327 -\ncap:55	1829
884	Fall	2025	2L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	21	22	Ali Elminejad	8.327 -\ncap:55	1830
885	Fall	2025	1L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	36	35	Mehmet Demir	8.522 -\ncap:72	1831
885	Fall	2025	2L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	30	27	Mehmet Demir	8.522 -\ncap:72	1832
886	Fall	2025	2L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	35	35	Rajarshi Bhowal	8.307 -\ncap:70	1833
886	Fall	2025	3L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	27	27	Rajarshi Bhowal	8.307 -\ncap:70	1834
887	Fall	2025	1L	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	18	30	Ali Elminejad	8.307 -\ncap:70	1835
888	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	81	80	Galymzhan\nNauryzbayev	3E.220 -\ncap:85	1836
889	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	70	85	Muhammad\nAkhtar	3E.220 -\ncap:85	1837
889	Fall	2025	1T	2025-08-18	2025-11-28	W	03:00 PM-04:15 PM	70	85	Muhammad\nAkhtar	3E.223 -\ncap:63	1838
890	Fall	2025	2Lb	2025-08-18	2025-11-28	F	04:00 PM-05:45 PM	33	40	Shyngys\nSalakchinov	3E.217 -\ncap:28	1839
890	Fall	2025	1Lb	2025-08-18	2025-11-28	M	04:00 PM-05:45 PM	37	40	Shyngys\nSalakchinov	3E.318 -\ncap:40	1840
891	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	18	75	Annie Ng	3E.224 -\ncap:85	1841
892	Fall	2025	1Lb	2025-08-18	2025-11-28	F	09:00 AM-09:50 AM	15	15	Annie Ng	TBA - cap:0	1842
892	Fall	2025	2Lb	2025-08-18	2025-11-28	F	03:00 PM-03:50 PM	1	15	Annie Ng	TBA - cap:0	1843
893	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	74	80	Carlo Molardi	3E.224 -\ncap:85	1844
894	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	43	75	Mohammad\nHashmi	3E.224 -\ncap:85	1845
894	Fall	2025	1T	2025-08-18	2025-11-28	M	01:00 PM-01:50 PM	43	75	Mohammad\nHashmi	3E.224 -\ncap:85	1846
895	Fall	2025	1Lb	2025-08-18	2025-11-28	M	09:00 AM-10:45 AM	15	30	Gulsim\nKulsharova	3E.321 -\ncap:22	1847
895	Fall	2025	2Lb	2025-08-18	2025-11-28	M	03:00 PM-04:45 PM	29	30	Gulsim\nKulsharova	3E.321 -\ncap:22	1848
896	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	43	60	Refik Kizilirmak	3E.223 -\ncap:63	1849
897	Fall	2025	1Lb	2025-08-18	2025-11-28	M	02:00 PM-02:50 PM	28	30	Refik Kizilirmak	3E.318 -\ncap:40	1850
897	Fall	2025	2Lb	2025-08-18	2025-11-28	F	02:00 PM-02:50 PM	17	30	Refik Kizilirmak	3E.318 -\ncap:40	1851
898	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	43	70	Refik Kizilirmak	3E.220 -\ncap:85	1852
899	Fall	2025	1T	2025-08-18	2025-11-28	W	04:30 PM-05:45 PM	14	40	Muhammad\nAkhtar	3E.223 -\ncap:63	1853
899	Fall	2025	1L	2025-08-18	2025-11-28	T R	05:00 PM-06:15 PM	14	40	Muhammad\nAkhtar	3E.224 -\ncap:85	1854
900	Fall	2025	1Lb	2025-08-18	2025-11-28	M	05:00 PM-06:15 PM	14	25	Muhammad\nAkhtar	3E.227 -\ncap:28	1855
322	Fall	2025	1Lb	2025-08-18	2025-11-28	F	03:00 PM-06:00 PM	25	25	Ainur\nRakhymbay	3E.318 -\ncap:40	1856
322	Fall	2025	2Lb	2025-08-18	2025-11-28	F	09:00 AM-12:00 PM	11	25	Ainur\nRakhymbay	3E.318 -\ncap:40	1857
901	Fall	2025	1L	2025-08-18	2025-11-28	M W	03:00 PM-04:15 PM	24	40	Ainur\nRakhymbay	3E.224 -\ncap:85	1858
902	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	5	40	Ainur\nRakhymbay	3E.217 -\ncap:28	1859
903	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	35	60	Mehdi Shafiee	online -\ncap:0	1860
904	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	7	40	Behrouz Maham	3.309 -\ncap:40	1861
905	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	14	40	Ainur\nRakhymbay,\nAresh Dadlani	online -\ncap:0	1862
906	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	19	40	Mohammad\nHashmi	3E.224 -\ncap:85	1863
907	Fall	2025	1Lb	2025-08-18	2025-11-28	T	12:00 PM-02:45 PM	77	78	Gulnur\nKalimuldina,\nAssiya\nYermukhambeto\nva, Gulsim\nKulsharova,\nWoojin Lee	3.323 -\ncap:64	1864
907	Fall	2025	2Lb	2025-08-18	2025-11-28	R	12:00 PM-02:45 PM	76	78	Gulnur\nKalimuldina,\nAssiya\nYermukhambeto\nva, Gulsim\nKulsharova,\nWoojin Lee	3.323 -\ncap:64	1865
907	Fall	2025	3Lb	2025-08-18	2025-11-28	T	03:00 PM-05:45 PM	74	78	Gulnur\nKalimuldina,\nAssiya\nYermukhambeto\nva, Gulsim\nKulsharova,\nWoojin Lee	3.323 -\ncap:64	1866
907	Fall	2025	4Lb	2025-08-18	2025-11-28	R	03:00 PM-05:45 PM	74	78	Gulnur\nKalimuldina,\nAssiya\nYermukhambeto\nva, Gulsim\nKulsharova,\nWoojin Lee	3.323 -\ncap:64	1867
907	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	301	312	Gulnur\nKalimuldina,\nAssiya\nYermukhambeto\nva, Gulsim\nKulsharova,\nWoojin Lee	online -\ncap:0	1868
333	Fall	2025	1Lb	2025-08-18	2025-11-28	T	12:00 PM-02:45 PM	73	75	Shyngys\nSalakchinov	3.302 -\ncap:70	1869
333	Fall	2025	2Lb	2025-08-18	2025-11-28	R	12:00 PM-02:45 PM	75	75	Shyngys\nSalakchinov	3.302 -\ncap:70	1870
333	Fall	2025	3Lb	2025-08-18	2025-11-28	T	03:00 PM-05:45 PM	65	75	Shyngys\nSalakchinov	3.302 -\ncap:70	1871
333	Fall	2025	4Lb	2025-08-18	2025-11-28	R	03:00 PM-05:45 PM	66	75	Shyngys\nSalakchinov	3.302 -\ncap:70	1872
333	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	279	300	Sultangali\nArzykulov	online -\ncap:0	1873
908	Fall	2025	2Lb	2025-08-18	2025-11-28	F	03:00 PM-04:45 PM	51	50	Yanwei Wang	3.323 -\ncap:64	1874
908	Fall	2025	3Lb	2025-08-18	2025-11-28	M	12:00 PM-01:45 PM	70	80	Dmitriy Sizov	3.323 -\ncap:64	1875
908	Fall	2025	4L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	60	60	Daniele Tosi	3.302 -\ncap:70	1876
908	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	73	70	Elnara\nKussinova	5.103 -\ncap:160	1877
908	Fall	2025	4Lb	2025-08-18	2025-11-28	M	01:00 PM-02:45 PM	45	55	Ainur\nRakhymbay	3E.217 -\ncap:28	1878
908	Fall	2025	5Lb	2025-08-18	2025-11-28	W	01:00 PM-02:45 PM	44	55	Ainur\nRakhymbay	3E.217 -\ncap:28	1879
908	Fall	2025	2L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	32	50	Yanwei Wang	3E.221 -\ncap:50	1880
908	Fall	2025	3L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	70	80	Dmitriy Sizov	3E.223 -\ncap:63	1881
908	Fall	2025	5L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	48	50	Prashant\nJamwal	3E.224 -\ncap:85	1882
908	Fall	2025	1Lb	2025-08-18	2025-11-28	T	04:30 PM-06:15 PM	73	70	Elnara\nKussinova	3E.227 -\ncap:28	1883
338	Fall	2025	2L	2025-08-18	2025-11-28	F	11:00 AM-11:50 AM	46	50	Dhawal Shah,\nSabina\nKhamzina	online -\ncap:0	1884
338	Fall	2025	4L	2025-08-18	2025-11-28	W	04:30 PM-05:45 PM	43	70	Galymzhan\nNauryzbayev	online -\ncap:0	1885
338	Fall	2025	1L	2025-08-18	2025-11-28	F	11:00 AM-11:50 AM	68	70	Mert Guney	3E.223 -\ncap:63	1886
338	Fall	2025	3L	2025-08-18	2025-11-28	F	03:00 PM-04:45 PM	47	60	Yerkin Abdildin,\nEssam Shehab	3E.224 -\ncap:85	1887
909	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	18	35	Kamal Regmi	6.402 -\ncap:24	1888
910	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	10	25	Jovid Aminov	6.327 -\ncap:10	1889
911	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	12	25	Jovid Aminov	6.327 -\ncap:10	1890
912	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	10	25	Medet Junussov	6.419 -\ncap:21	1891
913	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	11	25	Kamal Regmi	6.427 -\ncap:24	1892
914	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	13	25	Sebastianus\nWillem Josef\nDen Brok	6.427 -\ncap:24	1893
915	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	23	25	George\nMathews	6.507 -\ncap:72	1894
916	Fall	2025	1OCA	2025-08-18	2025-11-28	\N	Online/Distant	13	20	Sebastianus\nWillem Josef\nDen Brok	\N	1895
917	Fall	2025	1L	2025-08-18	2025-11-28	M	01:00 PM-01:50 PM	27	40	Milovan Fustic	6.105 -\ncap:64	1896
918	Fall	2025	1L	2025-08-18	2025-11-28	T	02:30 PM-03:45 PM	16	17	Marzhan\nBaigaliyeva	6.419 -\ncap:21	1897
919	Fall	2025	1P	2025-08-18	2025-11-28	F	04:00 PM-05:15 PM	12	20	Sebastianus\nWillem Josef\nDen Brok	6.105 -\ncap:64	1898
920	Fall	2025	1L	2025-08-18	2025-11-28	T	12:00 PM-01:15 PM	4	5	Marzhan\nBaigaliyeva	6.418 -\ncap:12	1899
921	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	09:00 AM-09:50 AM	24	24	Florian\nKuechler	8.317 -\ncap:28	1900
921	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	10:00 AM-10:50 AM	24	24	Florian\nKuechler	8.317 -\ncap:28	1901
922	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	11:00 AM-11:50 AM	18	24	Florian\nKuechler	8.317 -\ncap:28	1902
6	Fall	2025	1L	2025-08-18	2025-11-28	\N	Online/Distant	674	704	Rozaliya\nGaripova	\N	1903
6	Fall	2025	1S	2025-08-18	2025-11-28	M	09:00 AM-09:50 AM	20	20	Diana\nKopbayeva	9.105 -\ncap:75	1904
6	Fall	2025	2S	2025-08-18	2025-11-28	M	10:00 AM-10:50 AM	20	20	Diana\nKopbayeva	9.105 -\ncap:75	1905
6	Fall	2025	3S	2025-08-18	2025-11-28	M	11:00 AM-11:50 AM	19	20	Aybike Tezel	9.105 -\ncap:75	1906
6	Fall	2025	4S	2025-08-18	2025-11-28	M	01:00 PM-01:50 PM	19	20	Diana\nKopbayeva	9.105 -\ncap:75	1907
6	Fall	2025	5S	2025-08-18	2025-11-28	M	02:00 PM-02:50 PM	19	20	Diana\nKopbayeva	9.105 -\ncap:75	1908
6	Fall	2025	6S	2025-08-18	2025-11-28	M	04:00 PM-04:50 PM	24	24	Halit Akarca	9.105 -\ncap:75	1909
6	Fall	2025	7S	2025-08-18	2025-11-28	F	01:00 PM-01:50 PM	23	24	Mollie\nArbuthnot	9.105 -\ncap:75	1910
6	Fall	2025	8S	2025-08-18	2025-11-28	F	02:00 PM-02:50 PM	24	24	Mollie\nArbuthnot	9.105 -\ncap:75	1911
6	Fall	2025	9S	2025-08-18	2025-11-28	F	04:00 PM-04:50 PM	18	20	Aybike Tezel	9.105 -\ncap:75	1912
6	Fall	2025	10S	2025-08-18	2025-11-28	W	01:00 PM-01:50 PM	22	24	Meiramgul\nKussainova	9.105 -\ncap:75	1913
6	Fall	2025	11S	2025-08-18	2025-11-28	W	02:00 PM-02:50 PM	23	24	Meiramgul\nKussainova	9.105 -\ncap:75	1914
6	Fall	2025	12S	2025-08-18	2025-11-28	F	03:00 PM-03:50 PM	25	24	Halit Akarca	9.105 -\ncap:75	1915
6	Fall	2025	13S	2025-08-18	2025-11-28	F	05:00 PM-05:50 PM	19	20	Aybike Tezel	9.105 -\ncap:75	1916
6	Fall	2025	14S	2025-08-18	2025-11-28	F	06:00 PM-06:50 PM	19	20	Diana\nKopbayeva	9.105 -\ncap:75	1917
6	Fall	2025	15S	2025-08-18	2025-11-28	F	09:00 AM-09:50 AM	23	24	Rozaliya\nGaripova	9.105 -\ncap:75	1918
6	Fall	2025	16S	2025-08-18	2025-11-28	F	10:00 AM-10:50 AM	24	24	Rozaliya\nGaripova	9.105 -\ncap:75	1919
6	Fall	2025	17S	2025-08-18	2025-11-28	F	11:00 AM-11:50 AM	23	24	Rozaliya\nGaripova	9.105 -\ncap:75	1920
6	Fall	2025	19S	2025-08-18	2025-11-28	F	12:00 PM-12:50 PM	22	24	Mollie\nArbuthnot	9.105 -\ncap:75	1921
6	Fall	2025	20S	2025-08-18	2025-11-28	M	06:00 PM-06:50 PM	20	20	Aybike Tezel	9.105 -\ncap:75	1922
6	Fall	2025	21S	2025-08-18	2025-11-28	M	03:00 PM-03:50 PM	21	24	Halit Akarca	9.105 -\ncap:75	1923
6	Fall	2025	22S	2025-08-18	2025-11-28	M	05:00 PM-05:50 PM	18	20	Aybike Tezel	9.105 -\ncap:75	1924
6	Fall	2025	23S	2025-08-18	2025-11-28	M	12:00 PM-12:50 PM	20	20	Aybike Tezel	9.105 -\ncap:75	1925
6	Fall	2025	24S	2025-08-18	2025-11-28	W	03:00 PM-03:50 PM	23	24	Diana\nKopbayeva	9.105 -\ncap:75	1926
6	Fall	2025	25S	2025-08-18	2025-11-28	W	04:00 PM-04:50 PM	19	20	Aybike Tezel	9.105 -\ncap:75	1927
6	Fall	2025	26S	2025-08-18	2025-11-28	W	05:00 PM-05:50 PM	19	20	Aybike Tezel	9.105 -\ncap:75	1928
6	Fall	2025	27S	2025-08-18	2025-11-28	W	06:00 PM-06:50 PM	19	20	Aybike Tezel	9.105 -\ncap:75	1929
6	Fall	2025	28S	2025-08-18	2025-11-28	W	09:00 AM-09:50 AM	23	24	Rozaliya\nGaripova	9.105 -\ncap:75	1930
6	Fall	2025	29S	2025-08-18	2025-11-28	W	10:00 AM-10:50 AM	24	24	Rozaliya\nGaripova	9.105 -\ncap:75	1931
6	Fall	2025	30S	2025-08-18	2025-11-28	W	11:00 AM-11:50 AM	23	24	Rozaliya\nGaripova	9.105 -\ncap:75	1932
6	Fall	2025	31S	2025-08-18	2025-11-28	W	12:00 PM-12:50 PM	24	24	Meiramgul\nKussainova	9.105 -\ncap:75	1933
6	Fall	2025	32S	2025-08-18	2025-11-28	W	04:00 PM-04:50 PM	18	20	Diana\nKopbayeva	9.204 -\ncap:34	1934
6	Fall	2025	33S	2025-08-18	2025-11-28	W	11:00 AM-11:50 AM	17	20	Diana\nKopbayeva	9.204 -\ncap:34	1935
923	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	26	30	Diana\nKopbayeva	9.204 -\ncap:34	1936
924	Fall	2025	1L	2025-08-18	2025-11-28	\N	Online/Distant	89	100	Nikolay\nTsyrempilov	\N	1937
924	Fall	2025	1S	2025-08-18	2025-11-28	W	09:00 AM-09:50 AM	22	25	Nikolay\nTsyrempilov	9.204 -\ncap:34	1938
924	Fall	2025	2S	2025-08-18	2025-11-28	F	09:00 AM-09:50 AM	20	25	Nikolay\nTsyrempilov	9.204 -\ncap:34	1939
924	Fall	2025	3S	2025-08-18	2025-11-28	M	09:00 AM-09:50 AM	24	25	Nikolay\nTsyrempilov	9.204 -\ncap:34	1940
924	Fall	2025	4S	2025-08-18	2025-11-28	M	10:00 AM-10:50 AM	23	25	Nikolay\nTsyrempilov	9.204 -\ncap:34	1941
925	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	31	30	Di Lu	9.204 -\ncap:34	1942
371	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	29	30	Di Lu	9.204 -\ncap:34	1943
926	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	50	40	Halit Akarca	7E.529 -\ncap:95	1944
378	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	27	28	Curtis Murphy	9.204 -\ncap:34	1945
927	Fall	2025	1L	2025-08-18	2025-11-28	M	02:00 PM-04:50 PM	24	25	U Kim	8.322A -\ncap:32	1946
928	Fall	2025	1L	2025-08-18	2025-11-28	\N	Online/Distant	0	5	Rozaliya\nGaripova	\N	1947
929	Fall	2025	1S	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	15	16	Mollie\nArbuthnot	9.204 -\ncap:34	1948
930	Fall	2025	1IS	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	21	20	Curtis Murphy	9.204 -\ncap:34	1949
390	Fall	2025	3L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	14	16	Kulyan Kopesh	8.105 -\ncap:70	1950
390	Fall	2025	5L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	14	16	Kulyan Kopesh	8.105 -\ncap:70	1951
390	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	16	16	Aidar Balabekov	8.141 -\ncap:24	1952
390	Fall	2025	2L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	16	16	Aidar Balabekov	8.141 -\ncap:24	1953
390	Fall	2025	4L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	14	16	Aidar Balabekov	8.141 -\ncap:24	1954
390	Fall	2025	6L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	14	16	Gulzhamilya\nShalabayeva	8.141 -\ncap:24	1955
391	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	14	16	Raushan\nMyrzabekova	8.141 -\ncap:24	1956
391	Fall	2025	2L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	12	16	Raushan\nMyrzabekova	8.141 -\ncap:24	1957
391	Fall	2025	3L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	13	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	1958
391	Fall	2025	4L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	14	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	1959
391	Fall	2025	5L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	15	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	1960
391	Fall	2025	6L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	4	16	Gulzhamilya\nShalabayeva	8.141 -\ncap:24	1961
391	Fall	2025	7L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	15	16	Gulzhamilya\nShalabayeva	8.141 -\ncap:24	1962
391	Fall	2025	8L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	15	16	Gulzhamilya\nShalabayeva	8.141 -\ncap:24	1963
391	Fall	2025	10L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	12	16	Raushan\nMyrzabekova	8.141 -\ncap:24	1964
392	Fall	2025	1L	2025-08-18	2025-11-28	\N	Online/Distant	145	150	Uli Schamiloglu,\nMoldiyar\nYergebekov	\N	1965
392	Fall	2025	1S	2025-08-18	2025-11-28	M	02:00 PM-02:50 PM	25	25	Moldiyar\nYergebekov	7E.125/1 -\ncap:36	1966
392	Fall	2025	2S	2025-08-18	2025-11-28	W	02:00 PM-02:50 PM	24	25	Moldiyar\nYergebekov	7E.125/1 -\ncap:36	1967
392	Fall	2025	3S	2025-08-18	2025-11-28	M	10:00 AM-10:50 AM	23	25	Moldiyar\nYergebekov	7E.125/1 -\ncap:36	1968
392	Fall	2025	4S	2025-08-18	2025-11-28	M	11:00 AM-11:50 AM	25	25	Moldiyar\nYergebekov	7E.125/1 -\ncap:36	1969
392	Fall	2025	5S	2025-08-18	2025-11-28	W	11:00 AM-11:50 AM	23	25	Moldiyar\nYergebekov	7E.125/1 -\ncap:36	1970
392	Fall	2025	6S	2025-08-18	2025-11-28	W	10:00 AM-10:50 AM	25	25	Moldiyar\nYergebekov	7E.125/1 -\ncap:36	1971
394	Fall	2025	4S	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	32	30	Zeinep\nZhumatayeva	2.407 -\ncap:85	1972
394	Fall	2025	2S	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	35	30	Zeinekhan\nKuzekova	8.302 -\ncap:54	1973
394	Fall	2025	5S	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	32	30	Gulnara\nOmarbekova	8.302 -\ncap:54	1974
394	Fall	2025	1S	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	28	30	Samal\nAbzhanova	8.307 -\ncap:70	1975
394	Fall	2025	3S	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	30	30	Samal\nAbzhanova	8.307 -\ncap:70	1976
394	Fall	2025	6S	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	30	32	Zeinep\nZhumatayeva	2.322 -\ncap:45	1977
395	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	33	35	Zhanar\nBaiteliyeva	7E.125/1 -\ncap:36	1978
396	Fall	2025	2S	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	30	32	Mustafa Shokay	8.327 -\ncap:55	1979
396	Fall	2025	1S	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	31	32	Mustafa Shokay	8.302 -\ncap:54	1980
396	Fall	2025	3S	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	30	32	Mustafa Shokay	8.302 -\ncap:54	1981
396	Fall	2025	4S	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	32	32	Mustafa Shokay	8.302 -\ncap:54	1982
397	Fall	2025	1S	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	30	30	Zhanar\nAbdigapparova	2.407 -\ncap:85	1983
398	Fall	2025	1S	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	39	30	Meiramgul\nKussainova	7.105 -\ncap:75	1984
399	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	33	30	Zhanar\nAbdigapparova	2.407 -\ncap:85	1985
399	Fall	2025	2L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	24	30	Aigul Ismakova	8.105 -\ncap:70	1986
400	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	30	30	Kulyan Kopesh	8.302 -\ncap:54	1987
400	Fall	2025	2L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	30	30	Kulyan Kopesh	8.302 -\ncap:54	1988
931	Fall	2025	1S	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	31	30	Gulnara\nOmarbekova	8.302 -\ncap:54	1989
931	Fall	2025	2S	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	30	30	Gulnara\nOmarbekova	8.302 -\ncap:54	1990
401	Fall	2025	1S	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	35	35	Zhazira\nAgabekova	8.302 -\ncap:54	1991
402	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	33	35	Zhazira\nAgabekova	8.302 -\ncap:54	1992
403	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	30	30	Yermek Adayeva	7E.125/1 -\ncap:36	1993
403	Fall	2025	2L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	29	30	Yermek Adayeva	7E.125/1 -\ncap:36	1994
403	Fall	2025	3L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	30	30	Yermek Adayeva	7E.125/1 -\ncap:36	1995
403	Fall	2025	4L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	25	30	Yermek Adayeva	7E.125/1 -\ncap:36	1996
404	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	29	30	Zhanar\nBaiteliyeva	7E.125/1 -\ncap:36	1997
405	Fall	2025	1S	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	35	35	Sarkyt Aliszhan	7E.125/1 -\ncap:36	1998
34	Fall	2025	1S	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	32	30	Zeinekhan\nKuzekova	8.302 -\ncap:54	1999
406	Fall	2025	1S	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	33	34	Sarkyt Aliszhan	7E.125/1 -\ncap:36	2000
407	Fall	2025	1S	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	32	35	Zeinep\nZhumatayeva	2.407 -\ncap:85	2001
408	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	26	30	Samal\nAbzhanova	8.327 -\ncap:55	2002
408	Fall	2025	2L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	27	30	Samal\nAbzhanova	8.327 -\ncap:55	2003
932	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	12	16	Aigul Ismakova	8.105 -\ncap:70	2004
933	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	16	24	Raushan\nMyrzabekova	8.310 -\ncap:30	2005
934	Fall	2025	1L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	4	16	Aidar Balabekov	8.105 -\ncap:70	2006
935	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	03:00 PM-03:50 PM	23	24	Joomi Kong	8.317 -\ncap:28	2007
935	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	04:00 PM-04:50 PM	24	24	Joomi Kong	8.317 -\ncap:28	2008
935	Fall	2025	3L	2025-08-18	2025-11-28	M T W R	06:00 PM-06:50 PM	24	24	Joomi Kong	8.317 -\ncap:28	2009
936	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	05:00 PM-05:50 PM	24	24	Joomi Kong	8.317 -\ncap:28	2010
937	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	72	100	Olga Potanina	5.103 -\ncap:160	2011
938	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	15	28	Benjamin Brosig	8.319 -\ncap:30	2012
418	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	25	26	Andrey\nFilchenko,\nNikolay\nMikhailov	8.322A -\ncap:32	2013
939	Fall	2025	2L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	24	28	Olga Potanina	8.319 -\ncap:30	2014
419	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	36	35	Clinton Parker	6.507 -\ncap:72	2015
940	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	37	35	Clinton Parker	6.507 -\ncap:72	2016
420	Fall	2025	2Wsh	2025-08-18	2025-11-28	\N	Online/Distant	1	1	Florian\nKuechler	\N	2017
941	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	20	20	Nikolay\nMikhailov	8.319 -\ncap:30	2018
942	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	4	24	Benjamin Brosig	8.319 -\ncap:30	2019
943	Fall	2025	1Lb	2025-08-18	2025-11-28	W	03:00 PM-04:15 PM	75	82	Konstantinos\nKostas	3.323 -\ncap:64	2020
943	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	75	82	Konstantinos\nKostas	3E.220 -\ncap:85	2021
944	Fall	2025	1T	2025-08-18	2025-11-28	F	11:00 AM-11:50 AM	74	83	Gulnur\nKalimuldina	3E.220 -\ncap:85	2022
944	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	74	83	Gulnur\nKalimuldina	3E.224 -\ncap:85	2023
944	Fall	2025	1Lb	2025-08-18	2025-11-28	R	03:00 PM-05:45 PM	31	41	Gulnur\nKalimuldina	3E.431 -\ncap:15	2024
944	Fall	2025	2Lb	2025-08-18	2025-11-28	F	03:00 PM-05:45 PM	43	42	Gulnur\nKalimuldina	3E.431 -\ncap:15	2025
945	Fall	2025	2Lb	2025-08-18	2025-11-28	\N	Online/Distant	4	3	Sergey Spotar	\N	2026
945	Fall	2025	1T	2025-08-18	2025-11-28	M	09:00 AM-09:50 AM	64	70	Sergey Spotar	3E.220 -\ncap:85	2027
945	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	64	70	Sergey Spotar	3E.223 -\ncap:63	2028
945	Fall	2025	1Lb	2025-08-18	2025-11-28	F	03:00 PM-04:45 PM	60	70	Sergey Spotar	3E.324 -\ncap:25	2029
946	Fall	2025	2Lb	2025-08-18	2025-11-28	\N	Online/Distant	1	3	Amgad Salama	\N	2030
946	Fall	2025	1T	2025-08-18	2025-11-28	M	01:00 PM-01:50 PM	64	70	Amgad Salama	3E.223 -\ncap:63	2031
946	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	64	70	Amgad Salama	3E.224 -\ncap:85	2032
946	Fall	2025	1Lb	2025-08-18	2025-11-28	F	01:00 PM-02:45 PM	63	70	Amgad Salama	3E.327 -\ncap:25	2033
947	Fall	2025	2Lb	2025-08-18	2025-11-28	\N	Online/Distant	1	1	Md. Hazrat Ali	\N	2034
947	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	61	70	Md. Hazrat Ali	3E.223 -\ncap:63	2035
947	Fall	2025	1Lb	2025-08-18	2025-11-28	W	01:30 PM-03:15 PM	60	70	Md. Hazrat Ali	3E.326 -\ncap:30	2036
948	Fall	2025	2L	2025-08-18	2025-11-28	\N	Online/Distant	3	4	Sherif Gouda	\N	2037
948	Fall	2025	2Lb	2025-08-18	2025-11-28	\N	Online/Distant	1	4	Sherif Gouda	\N	2038
948	Fall	2025	2T	2025-08-18	2025-11-28	\N	Online/Distant	1	4	Sherif Gouda	\N	2039
948	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	59	70	Sherif Gouda	3E.221 -\ncap:50	2040
948	Fall	2025	1T	2025-08-18	2025-11-28	M	02:00 PM-02:50 PM	61	70	Sherif Gouda	3E.223 -\ncap:63	2041
948	Fall	2025	1Lb	2025-08-18	2025-11-28	F	09:00 AM-10:45 AM	61	70	Sherif Gouda	3E.328 -\ncap:20	2042
949	Fall	2025	1T	2025-08-18	2025-11-28	W	10:00 AM-10:50 AM	46	55	Yerbol\nSarbassov	3.323 -\ncap:64	2043
949	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	46	55	Yerbol\nSarbassov	3.416 -\ncap:46	2044
949	Fall	2025	1Lb	2025-08-18	2025-11-28	W	03:00 PM-05:45 PM	46	55	Yerbol\nSarbassov	3E.327 -\ncap:25	2045
950	Fall	2025	1T	2025-08-18	2025-11-28	M	10:00 AM-10:50 AM	45	55	Didier Talamona	3.323 -\ncap:64	2046
950	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	45	55	Didier Talamona	3E.221 -\ncap:50	2047
950	Fall	2025	1P	2025-08-18	2025-11-28	M	03:00 PM-04:15 PM	45	55	Didier Talamona	3E.330 -\ncap:15	2048
951	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	14	12	Didier Talamona	3.316 -\ncap:40	2049
951	Fall	2025	1Lb	2025-08-18	2025-11-28	M	11:00 AM-11:50 AM	14	12	Didier Talamona	3E.334 -\ncap:20	2050
952	Fall	2025	1T	2025-08-18	2025-11-28	M	09:00 AM-09:50 AM	8	27	Altay\nZhakatayev,\nDmitriy Sizov	3.322 -\ncap:40	2051
952	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	8	27	Altay\nZhakatayev,\nDmitriy Sizov	3.303 -\ncap:32	2052
953	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	27	27	Yerbol\nSarbassov	3.322 -\ncap:40	2053
953	Fall	2025	1T	2025-08-18	2025-11-28	W	01:00 PM-01:50 PM	27	27	Yerbol\nSarbassov	3.322 -\ncap:40	2054
954	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	16	27	Altay\nZhakatayev	3.303 -\ncap:32	2055
954	Fall	2025	1T	2025-08-18	2025-11-28	W	11:00 AM-11:50 AM	16	27	Altay\nZhakatayev	3.309 -\ncap:40	2056
1	Fall	2025	1L	2025-08-18	2025-11-28	M F	01:00 PM-01:50 PM	269	270	Achenef\nTesfahun	BallRoom\nLeft(BL) -\ncap:200	2057
1	Fall	2025	2L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	271	270	Achenef\nTesfahun	BallRoom\nLeft(BL) -\ncap:200	2058
1	Fall	2025	4L	2025-08-18	2025-11-28	R	01:30 PM-02:45 PM	262	270	Yerlan Amanbek	Main Hall -\ncap:1319	2059
1	Fall	2025	1R	2025-08-18	2025-11-28	M	12:00 PM-12:50 PM	60	60	Samat Kassabek	7E.529 -\ncap:95	2060
1	Fall	2025	2R	2025-08-18	2025-11-28	M	03:00 PM-03:50 PM	60	60	Samat Kassabek	7E.529 -\ncap:95	2061
1	Fall	2025	3R	2025-08-18	2025-11-28	M	04:00 PM-04:50 PM	60	60	Catalina\nTroshev	7E.529 -\ncap:95	2062
1	Fall	2025	4R	2025-08-18	2025-11-28	W	12:00 PM-12:50 PM	60	60	Samat Kassabek	7E.529 -\ncap:95	2063
1	Fall	2025	5R	2025-08-18	2025-11-28	W	03:00 PM-03:50 PM	60	60	Samat Kassabek	7E.529 -\ncap:95	2064
1	Fall	2025	6R	2025-08-18	2025-11-28	W	04:00 PM-04:50 PM	62	60	Catalina\nTroshev	7E.529 -\ncap:95	2065
1	Fall	2025	7R	2025-08-18	2025-11-28	F	03:00 PM-03:50 PM	61	60	Samat Kassabek	7E.529 -\ncap:95	2066
1	Fall	2025	8R	2025-08-18	2025-11-28	F	12:00 PM-12:50 PM	60	60	Samat Kassabek	7E.529 -\ncap:95	2067
1	Fall	2025	3L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	261	270	Ardak\nKashkynbayev	Red Hall\n1022 (C3) -\ncap:265	2068
1	Fall	2025	9R	2025-08-18	2025-11-28	T	09:00 AM-10:15 AM	57	60	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	2069
1	Fall	2025	10R	2025-08-18	2025-11-28	T	10:30 AM-11:45 AM	58	60	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	2070
1	Fall	2025	11R	2025-08-18	2025-11-28	T	01:30 PM-02:45 PM	59	60	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	2071
1	Fall	2025	12R	2025-08-18	2025-11-28	T	03:00 PM-04:15 PM	58	60	Bibinur\nShupeyeva	8.522 -\ncap:72	2072
1	Fall	2025	13R	2025-08-18	2025-11-28	T	04:30 PM-05:45 PM	57	60	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	2073
1	Fall	2025	14R	2025-08-18	2025-11-28	R	09:00 AM-10:15 AM	57	60	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	2074
1	Fall	2025	15R	2025-08-18	2025-11-28	R	10:30 AM-11:45 AM	58	60	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	2075
1	Fall	2025	16R	2025-08-18	2025-11-28	R	01:30 PM-02:45 PM	60	60	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	2076
1	Fall	2025	17R	2025-08-18	2025-11-28	R	03:00 PM-04:15 PM	58	60	Bibinur\nShupeyeva	8.522 -\ncap:72	2077
1	Fall	2025	18R	2025-08-18	2025-11-28	R	04:30 PM-05:45 PM	58	60	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	2078
5	Fall	2025	2R	2025-08-18	2025-11-28	W	06:00 PM-06:50 PM	84	90	Bibinur\nShupeyeva	7E.222 -\ncap:95	2079
5	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	84	90	Bibinur\nShupeyeva	7E.529 -\ncap:95	2080
10	Fall	2025	3L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	56	54	Catalina\nTroshev	7.210 -\ncap:54	2081
10	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	60	90	Zhanbota\nMyrzakul	7E.329 -\ncap:95	2082
10	Fall	2025	2L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	97	96	Catalina\nTroshev	7E.329 -\ncap:95	2083
10	Fall	2025	4L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	58	90	Zhanbota\nMyrzakul	7E.329 -\ncap:95	2084
26	Fall	2025	1R	2025-08-18	2025-11-28	\N	Online/Distant	191	194	Eunghyun Lee	\N	2085
26	Fall	2025	2L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	61	60	Andrey\nMelnikov	7E.222 -\ncap:95	2086
26	Fall	2025	1L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	67	60	Andrey\nMelnikov	7E.329 -\ncap:95	2087
26	Fall	2025	3L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	63	60	Amin Esfahani	7E.329 -\ncap:95	2088
11	Fall	2025	5L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	48	50	Zhansaya\nTleuliyeva	7.210 -\ncap:54	2089
11	Fall	2025	6L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	49	50	Zhansaya\nTleuliyeva	7.210 -\ncap:54	2090
11	Fall	2025	1R	2025-08-18	2025-11-28	M	06:00 PM-06:50 PM	82	82	Viktor Ten	7E.222 -\ncap:95	2091
11	Fall	2025	2L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	91	90	Viktor Ten	7E.222 -\ncap:95	2092
11	Fall	2025	2R	2025-08-18	2025-11-28	F	06:00 PM-06:50 PM	77	82	Zhansaya\nTleuliyeva	7E.222 -\ncap:95	2093
11	Fall	2025	7L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	59	80	Zhansaya\nTleuliyeva	7E.222 -\ncap:95	2094
11	Fall	2025	3R	2025-08-18	2025-11-28	M	06:00 PM-06:50 PM	80	83	Zhansaya\nTleuliyeva	7E.329 -\ncap:95	2095
11	Fall	2025	4L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	58	60	Zhanbota\nMyrzakul	7E.329 -\ncap:95	2096
11	Fall	2025	4R	2025-08-18	2025-11-28	W	06:00 PM-06:50 PM	66	83	Zhanbota\nMyrzakul	7E.329 -\ncap:95	2097
445	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	53	60	Adilet\nOtemissov	7E.222 -\ncap:95	2098
445	Fall	2025	3L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	69	70	Aigerim\nMadiyeva	7E.222 -\ncap:95	2099
445	Fall	2025	2L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	42	50	Aigerim\nMadiyeva	8.522 -\ncap:72	2100
955	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	37	54	Durvudkhan\nSuragan	7.210 -\ncap:54	2101
447	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	29	60	Manat Mustafa	7E.329 -\ncap:95	2102
447	Fall	2025	2L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	58	60	Zhibek\nKadyrsizova	7E.329 -\ncap:95	2103
448	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	69	90	Bibinur\nShupeyeva	7E.222 -\ncap:95	2104
18	Fall	2025	3L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	55	50	Viktor Ten	7.210 -\ncap:54	2105
18	Fall	2025	2L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	84	70	Viktor Ten	7E.222 -\ncap:95	2106
18	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	58	60	Erum Rehman	7E.329 -\ncap:95	2107
28	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	57	60	Erum Rehman	7E.222 -\ncap:95	2108
28	Fall	2025	2L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	54	60	Kerem Ugurlu	7E.222 -\ncap:95	2109
956	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	65	60	Dongming Wei	7E.329 -\ncap:95	2110
450	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	58	60	Piotr Sebastian\nSkrzypacz	7E.329 -\ncap:95	2111
451	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	49	60	Alejandro Javier\nCastro Castilla	7E.329 -\ncap:95	2112
957	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	51	60	Ardak\nKashkynbayev	7E.222 -\ncap:95	2113
958	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	13	60	Manat Mustafa	7E.222 -\ncap:95	2114
959	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	64	60	Tolga Etgu	7E.329 -\ncap:95	2115
960	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	56	60	Kerem Ugurlu	7E.329 -\ncap:95	2116
961	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	70	60	Piotr Sebastian\nSkrzypacz	7E.222 -\ncap:95	2117
962	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	60	60	Rustem\nTakhanov	7E.222 -\ncap:95	2118
963	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	48	60	Adilbek\nKairzhan	7E.329 -\ncap:95	2119
964	Fall	2025	1L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	61	60	Dongming Wei	7E.222 -\ncap:95	2120
965	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	49	60	Amin Esfahani	7E.222 -\ncap:95	2121
966	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	17	54	Adilbek\nKairzhan	7.210 -\ncap:54	2122
463	Fall	2025	2L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	5	15	Eunghyun Lee	7.210 -\ncap:54	2123
463	Fall	2025	3L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	1	15	Durvudkhan\nSuragan	7.210 -\ncap:54	2124
463	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	8	15	Zhibek\nKadyrsizova	7E.221 -\ncap:56	2125
464	Fall	2025	2L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	2	10	Eunghyun Lee	7.210 -\ncap:54	2126
464	Fall	2025	3L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	2	10	Durvudkhan\nSuragan	7.210 -\ncap:54	2127
465	Fall	2025	3L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	3	5	Durvudkhan\nSuragan	7.210 -\ncap:54	2128
465	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	1	5	Zhibek\nKadyrsizova	7E.221 -\ncap:56	2129
466	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	4	5	Zhibek\nKadyrsizova	7E.221 -\ncap:56	2130
967	Fall	2025	1L	2025-08-18	2025-11-28	M	09:00 AM-11:50 AM	19	20	Emil Bayramov	6.422 -\ncap:28	2131
968	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	12	20	Fidelis\nSuorineni	6.302 -\ncap:44	2132
969	Fall	2025	1L	2025-08-18	2025-11-28	M W	11:00 AM-12:15 PM	10	20	Ali Mortazavi	6.427 -\ncap:24	2133
970	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	9	20	Nasser\nMadaniesfahani	6.508 -\ncap:20	2134
517	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	9	15	Fidelis\nSuorineni	6.518 -\ncap:14	2135
971	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	10	20	Sergei Sabanov	6.522 -\ncap:36	2136
972	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	3	20	Ata Akcil	6.302 -\ncap:44	2137
973	Fall	2025	1S	2025-08-18	2025-11-28	W	04:00 PM-06:30 PM	9	15	Sergei Sabanov	6.522 -\ncap:36	2138
974	Fall	2025	1L	2025-08-18	2025-11-28	R	09:00 AM-12:00 PM	5	6	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	2139
975	Fall	2025	1L	2025-08-18	2025-11-28	M	01:00 PM-03:30 PM	5	6	Jonas Cruz	NUSOM\nBuilding -\ncap:0	2140
976	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:00 PM-04:00 PM	42	45	Ainetta\nNurmagambeto\nva, Joseph\nAlmazan,\nJamilya\nSaparbay	NUSOM\nBuilding -\ncap:0	2141
977	Fall	2025	1L	2025-08-18	2025-11-28	M W	01:00 PM-03:10 PM	42	45	Joseph Almazan	NUSOM\nBuilding -\ncap:0	2142
978	Fall	2025	1L	2025-08-18	2025-11-28	T W	10:30 AM-12:10 PM	42	45	Nancy Stitt,\nAizada Badiyeva	NUSOM\nBuilding -\ncap:0	2143
979	Fall	2025	1L	2025-08-18	2025-11-28	R	10:00 AM-12:10 PM	42	45	Anargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	2144
980	Fall	2025	1ClinPract	2025-08-18	2025-11-28	T W	08:00 AM-04:00 PM	5	6	Paolo Colet	NUSOM\nBuilding -\ncap:0	2145
980	Fall	2025	1L	2025-08-18	2025-11-28	M	10:00 AM-12:00 PM	5	6	Paolo Colet	NUSOM\nBuilding -\ncap:0	2146
981	Fall	2025	1ClinPract	2025-08-18	2025-11-28	F	08:00 AM-04:00 PM	5	6	Ruslan Bilal,\nJoseph Almazan	NUSOM\nBuilding -\ncap:0	2147
981	Fall	2025	1L	2025-08-18	2025-11-28	R	01:00 PM-04:00 PM	5	6	Ruslan Bilal,\nJoseph Almazan	NUSOM\nBuilding -\ncap:0	2148
982	Fall	2025	1L	2025-08-18	2025-11-28	T	12:30 PM-02:40 PM	35	35	Nancy Stitt,\nAnargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	2149
983	Fall	2025	1L	2025-08-18	2025-11-28	T	10:00 AM-12:10 PM	35	35	Paolo Colet	NUSOM\nBuilding -\ncap:0	2150
984	Fall	2025	1L	2025-08-18	2025-11-28	R	10:00 AM-12:10 PM	35	35	Anargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	2151
596	Fall	2025	1L	2025-08-18	2025-11-28	M W	10:00 AM-12:00 PM	35	35	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	2152
985	Fall	2025	1ClinPract	2025-08-18	2025-11-28	F	09:00 AM-04:00 PM	3	3	Anargul\nKuntuganova,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	2153
985	Fall	2025	1L	2025-08-18	2025-11-28	R	10:00 AM-12:10 PM	3	3	Anargul\nKuntuganova,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	2154
986	Fall	2025	1L	2025-08-18	2025-11-28	M W	01:00 PM-03:10 PM	3	3	Joseph Almazan	NUSOM\nBuilding -\ncap:0	2155
987	Fall	2025	1ClinPract	2025-08-18	2025-11-28	T	08:00 AM-04:00 PM	3	3	Nancy Stitt	NUSOM\nBuilding -\ncap:0	2156
987	Fall	2025	1L	2025-08-18	2025-11-28	M	09:00 AM-12:00 PM	3	3	Nancy Stitt	NUSOM\nBuilding -\ncap:0	2157
988	Fall	2025	1L	2025-08-18	2025-11-28	R	01:00 PM-04:00 PM	3	3	Jonas Cruz	NUSOM\nBuilding -\ncap:0	2158
989	Fall	2025	1L	2025-08-18	2025-11-28	W	01:00 PM-02:50 PM	150	150	Arman Saparov,\nMatthew\nNaanlep Tanko	Blue Hall -\ncap:239	2159
990	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:00 PM-02:15 PM	145	150	Larisa Lezina	NUSOM\nBuilding -\ncap:0	2160
990	Fall	2025	1Lb	2025-08-18	2025-11-28	T	09:00 AM-11:50 AM	40	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	2161
990	Fall	2025	2Lb	2025-08-18	2025-11-28	T	03:00 PM-05:50 PM	37	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	2162
990	Fall	2025	3Lb	2025-08-18	2025-11-28	R	09:00 AM-11:50 AM	38	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	2163
990	Fall	2025	4Lb	2025-08-18	2025-11-28	R	03:00 PM-05:50 PM	30	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	2164
991	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	50	55	Arman Saparov,\nJeanette Kunz\nHalder, Denis\nBulanin, Prim\nSingh, Sanja\nTerzic, Syed\nHani Hassan\nAbidi, Larisa\nLezina	NUSOM\nBuilding -\ncap:0	2165
992	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	50	55	Yuliya\nSemenova	NUSOM\nBuilding -\ncap:0	2166
993	Fall	2025	1L	2025-08-18	2025-11-28	T	09:00 AM-09:50 AM	50	55	Matthew\nNaanlep Tanko,\nSrinivasa Bolla	NUSOM\nBuilding -\ncap:0	2167
994	Fall	2025	1L	2025-08-04	2025-08-08	M T W R F	10:00 AM-06:00 PM	30	30	Arman Saparov,\nVitaliy Sazonov,\nDenis Bulanin,\nMatthew\nNaanlep Tanko	NUSOM\nBuilding -\ncap:0	2168
995	Fall	2025	1L	2025-08-11	2025-10-10	M T W R	09:00 AM-12:00 PM	30	30	Lyazzat\nToleubekova,\nSrinivasa Bolla	NUSOM\nBuilding -\ncap:0	2169
996	Fall	2025	1L	2025-10-13	2025-10-31	M T W R	09:00 AM-12:00 PM	30	30	Denis Bulanin,\nPrim Singh	NUSOM\nBuilding -\ncap:0	2170
997	Fall	2025	1L	2025-11-03	2025-11-21	M T W R	09:00 AM-12:00 PM	30	30	Denis Bulanin,\nAgata Natasza\nBurska	NUSOM\nBuilding -\ncap:0	2171
998	Fall	2025	1L	2025-11-24	2025-12-05	M T W R	09:00 AM-12:00 PM	30	30	Mohamad\nAljofan,\nVladimir Surov	NUSOM\nBuilding -\ncap:0	2172
999	Fall	2025	1L	2025-08-12	2025-10-07	T	01:00 PM-05:00 PM	28	30	Vitaliy Sazonov	NUSOM\nBuilding -\ncap:0	2173
1000	Fall	2025	1L	2025-10-14	2025-11-28	T	01:00 PM-05:00 PM	28	30	Vitaliy Sazonov	NUSOM\nBuilding -\ncap:0	2174
1001	Fall	2025	1L	2025-08-13	2025-11-26	W	01:00 PM-04:00 PM	28	30	Yesbolat Sakko	NUSOM\nBuilding -\ncap:0	2175
1002	Fall	2025	1L	2025-09-04	2025-11-13	R	01:00 PM-04:00 PM	28	30	Ruslan Bilal	NUSOM\nBuilding -\ncap:0	2176
1003	Fall	2025	1L	2025-08-11	2025-11-24	M	01:00 PM-04:00 PM	28	30	Alessandra\nClementi,\nLyazzat\nToleubekova	NUSOM\nBuilding -\ncap:0	2177
610	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	02:00 PM-02:50 PM	24	24	Marzieh Sadat\nRazavi	8.305 -\ncap:30	2178
610	Fall	2025	3L	2025-08-18	2025-11-28	M T W R	03:00 PM-03:50 PM	21	24	Marzieh Sadat\nRazavi	8.305 -\ncap:30	2179
1004	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	33	65	Shams Kalam	6.105 -\ncap:64	2180
1005	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	28	35	Sagyn\nOmirbekov	6.422 -\ncap:28	2181
1006	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	27	30	Masoud Riazi	6.522 -\ncap:36	2182
1007	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	29	35	Ali Shafiei	6.302 -\ncap:44	2183
1008	Fall	2025	1L	2025-08-18	2025-11-28	M	03:00 PM-04:50 PM	31	35	Irawan Sonny	6.105 -\ncap:64	2184
1009	Fall	2025	1P	2025-08-18	2025-11-28	W	10:00 AM-11:50 AM	18	25	Mian Umer\nShafiq	6.302 -\ncap:44	2185
1010	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	14	35	Peyman\nPourafshary	6.419 -\ncap:21	2186
1011	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	13	35	Mian Umer\nShafiq	6.302 -\ncap:44	2187
1012	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	27	30	Siegfried Van\nDuffel	9.204 -\ncap:34	2188
1013	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	40	40	Ted Parent	6.507 -\ncap:72	2189
22	Fall	2025	3L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	49	50	Bakinaz Abdalla	2.307 -\ncap:75	2190
22	Fall	2025	4L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	36	50	Bakinaz Abdalla	2.307 -\ncap:75	2191
22	Fall	2025	5L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	37	40	Donovan Cox	2.307 -\ncap:75	2192
22	Fall	2025	8L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	35	50	Chandler Hatch	2.307 -\ncap:75	2193
22	Fall	2025	11L	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	45	50	James\nHutchinson	2.307 -\ncap:75	2194
22	Fall	2025	12L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	48	50	Bakinaz Abdalla	2.307 -\ncap:75	2195
22	Fall	2025	9L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	50	50	Matthew\nHeeney	2.407 -\ncap:85	2196
22	Fall	2025	13L	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	40	50	Mihnea Capraru	9.105 -\ncap:75	2197
22	Fall	2025	16L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	45	50	Matthew\nHeeney	7E.220 -\ncap:56	2198
22	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	49	50	Ted Parent	5E.438 -\ncap:82	2199
22	Fall	2025	7L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	39	40	Donovan Cox	5E.438 -\ncap:82	2200
22	Fall	2025	10L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	37	40	Donovan Cox	5E.438 -\ncap:82	2201
22	Fall	2025	14L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	38	40	Donovan Cox	5E.438 -\ncap:82	2202
1014	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	19	24	Siegfried Van\nDuffel	5E.438 -\ncap:82	2203
1015	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	24	24	Mihnea Capraru	9.204 -\ncap:34	2204
1016	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	19	24	Chandler Hatch	8.305 -\ncap:30	2205
649	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	20	24	James\nHutchinson	2.407 -\ncap:85	2206
2	Fall	2025	2PLb	2025-08-18	2025-11-28	M	12:00 PM-02:50 PM	36	36	Diana Seitova	9.202 -\ncap:40	2207
2	Fall	2025	4PLb	2025-08-18	2025-11-28	M	09:00 AM-11:50 AM	34	36	Diana Seitova	9.202 -\ncap:40	2208
2	Fall	2025	5PLb	2025-08-18	2025-11-28	T	09:00 AM-11:50 AM	33	36	Diana Seitova	9.202 -\ncap:40	2209
2	Fall	2025	8PLb	2025-08-18	2025-11-28	T	12:00 PM-02:50 PM	37	36	Diana Seitova	9.202 -\ncap:40	2210
2	Fall	2025	10PLb	2025-08-18	2025-11-28	W	09:00 AM-11:50 AM	36	36	Diana Seitova	9.202 -\ncap:40	2211
2	Fall	2025	12PLb	2025-08-18	2025-11-28	W	12:00 PM-02:50 PM	36	36	Diana Seitova	9.202 -\ncap:40	2212
2	Fall	2025	15PLb	2025-08-18	2025-11-28	W	03:00 PM-05:50 PM	36	36	Diana Seitova	9.202 -\ncap:40	2213
2	Fall	2025	16PLb	2025-08-18	2025-11-28	R	09:00 AM-11:50 AM	33	36	Diana Seitova	9.202 -\ncap:40	2214
2	Fall	2025	18PLb	2025-08-18	2025-11-28	R	12:00 PM-02:50 PM	36	36	Diana Seitova	9.202 -\ncap:40	2215
2	Fall	2025	20PLb	2025-08-18	2025-11-28	F	09:00 AM-11:50 AM	36	36	Diana Seitova	9.202 -\ncap:40	2216
2	Fall	2025	23PLb	2025-08-18	2025-11-28	T	03:00 PM-05:50 PM	36	36	Diana Seitova	9.202 -\ncap:40	2217
2	Fall	2025	24PLb	2025-08-18	2025-11-28	R	03:00 PM-05:50 PM	35	36	Diana Seitova	9.202 -\ncap:40	2218
2	Fall	2025	27PLb	2025-08-18	2025-11-28	F	12:00 PM-02:50 PM	33	33	Diana Seitova	9.202 -\ncap:40	2219
2	Fall	2025	1PLb	2025-08-18	2025-11-28	M	09:00 AM-11:50 AM	36	36	Diana Seitova	9.222 -\ncap:40	2220
2	Fall	2025	3PLb	2025-08-18	2025-11-28	M	12:00 PM-02:50 PM	33	36	Diana Seitova	9.222 -\ncap:40	2221
2	Fall	2025	7PLb	2025-08-18	2025-11-28	T	12:00 PM-02:50 PM	36	36	Diana Seitova	9.222 -\ncap:40	2222
2	Fall	2025	9PLb	2025-08-18	2025-11-28	T	03:00 PM-05:50 PM	36	36	Diana Seitova	9.222 -\ncap:40	2223
2	Fall	2025	11PLb	2025-08-18	2025-11-28	W	09:00 AM-11:50 AM	34	36	Diana Seitova	9.222 -\ncap:40	2224
2	Fall	2025	13PLb	2025-08-18	2025-11-28	W	12:00 PM-02:50 PM	35	36	Diana Seitova	9.222 -\ncap:40	2225
2	Fall	2025	14PLb	2025-08-18	2025-11-28	W	03:00 PM-05:50 PM	36	36	Diana Seitova	9.222 -\ncap:40	2226
2	Fall	2025	19PLb	2025-08-18	2025-11-28	R	12:00 PM-02:50 PM	36	36	Diana Seitova	9.222 -\ncap:40	2227
2	Fall	2025	21PLb	2025-08-18	2025-11-28	F	09:00 AM-11:50 AM	35	36	Diana Seitova	9.222 -\ncap:40	2228
2	Fall	2025	22PLb	2025-08-18	2025-11-28	F	12:00 PM-02:50 PM	35	36	Diana Seitova	9.222 -\ncap:40	2229
2	Fall	2025	25PLb	2025-08-18	2025-11-28	R	03:00 PM-05:50 PM	35	36	Diana Seitova	9.222 -\ncap:40	2230
2	Fall	2025	26PLb	2025-08-18	2025-11-28	R	09:00 AM-11:50 AM	17	33	Diana Seitova	9.222 -\ncap:40	2231
2	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	170	180	Kyunghwan Oh	Red Hall\n1022 (C3) -\ncap:265	2232
2	Fall	2025	2L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	172	180	Ernazar\nAbdikamalov	Red Hall\n1022 (C3) -\ncap:265	2233
2	Fall	2025	3L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	173	200	Alexander\nTikhonov	Red Hall\n1022 (C3) -\ncap:265	2234
2	Fall	2025	4L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	177	180	Zhandos\nUtegulov	Red Hall\n1022 (C3) -\ncap:265	2235
2	Fall	2025	5L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	169	180	Marat Kaikanov	Red Hall\n1022 (C3) -\ncap:265	2236
2	Fall	2025	1R	2025-08-18	2025-11-28	M	12:00 PM-12:50 PM	60	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2237
2	Fall	2025	2R	2025-08-18	2025-11-28	M	01:00 PM-01:50 PM	62	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2238
2	Fall	2025	3R	2025-08-18	2025-11-28	M	02:00 PM-02:50 PM	63	64	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	2239
2	Fall	2025	5R	2025-08-18	2025-11-28	M	03:00 PM-03:50 PM	62	64	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	2240
2	Fall	2025	7R	2025-08-18	2025-11-28	W	12:00 PM-12:50 PM	63	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2241
2	Fall	2025	8R	2025-08-18	2025-11-28	W	01:00 PM-01:50 PM	62	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2242
2	Fall	2025	9R	2025-08-18	2025-11-28	W	02:00 PM-02:50 PM	63	64	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	2243
2	Fall	2025	11R	2025-08-18	2025-11-28	W	04:00 PM-04:50 PM	62	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2244
2	Fall	2025	12R	2025-08-18	2025-11-28	F	12:00 PM-12:50 PM	65	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2245
2	Fall	2025	13R	2025-08-18	2025-11-28	F	01:00 PM-01:50 PM	64	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2246
2	Fall	2025	14R	2025-08-18	2025-11-28	F	03:00 PM-03:50 PM	63	64	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	2247
2	Fall	2025	16R	2025-08-18	2025-11-28	F	04:00 PM-04:50 PM	62	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2248
2	Fall	2025	17R	2025-08-18	2025-11-28	W	03:00 PM-03:50 PM	64	64	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	2249
2	Fall	2025	18R	2025-08-18	2025-11-28	M	04:00 PM-04:50 PM	46	62	Omid Farzadian	7E.125/2 -\ncap:56	2250
1017	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	33	55	Dana Alina	7E.125/2 -\ncap:56	2251
1018	Fall	2025	1R	2025-08-18	2025-11-28	M	01:00 PM-01:50 PM	17	20	Daniele\nMalafarina,\nRayner\nRodriguez\nGuzman	7.507 -\ncap:48	2252
1018	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	17	20	Daniele\nMalafarina,\nRayner\nRodriguez\nGuzman	7E.125/2 -\ncap:56	2253
1019	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	37	55	Rayner\nRodriguez\nGuzman	7E.125/2 -\ncap:56	2254
1020	Fall	2025	1Lb	2025-08-18	2025-11-28	M	04:00 PM-06:50 PM	21	24	Ainur\nKoshkinbayeva,\nBekdaulet\nShukirgaliyev	7.302 -\ncap:30	2255
1020	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	21	24	Askhat\nJumabekov	7E.125/2 -\ncap:56	2256
1021	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	19	20	Michael Good	7.507 -\ncap:48	2257
1021	Fall	2025	1R	2025-08-18	2025-11-28	F	01:00 PM-01:50 PM	19	20	Michael Good	7.507 -\ncap:48	2258
1022	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	6	20	Bakhtiyar\nOrazbayev	7.507 -\ncap:48	2259
1022	Fall	2025	1R	2025-08-18	2025-11-28	W	01:00 PM-01:50 PM	6	20	Bakhtiyar\nOrazbayev	7.507 -\ncap:48	2260
1023	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	6	20	Anton\nDesyatnikov	7.507 -\ncap:48	2261
1024	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	14	20	Sergiy Bubin,\nBekdaulet\nShukirgaliyev	7.507 -\ncap:48	2262
1025	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	11	20	Sergiy Bubin	7.507 -\ncap:48	2263
1025	Fall	2025	1R	2025-08-18	2025-11-28	T	12:00 PM-01:15 PM	11	20	Sergiy Bubin	7.507 -\ncap:48	2264
1026	Fall	2025	1L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	5	20	Daniele\nMalafarina	7.507 -\ncap:48	2265
1027	Fall	2025	1P	2025-08-18	2025-11-28	\N	Online/Distant	8	20	Anton\nDesyatnikov	\N	2266
1028	Fall	2025	1L	2025-08-18	2025-11-28	R	10:30 AM-11:45 AM	116	120	Sabina\nInsebayeva	Red Hall\n1022 (C3) -\ncap:265	2267
673	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	103	100	Neil Collins	Senate Hall\n- cap:144	2268
1029	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	77	80	Brian Smith	Blue Hall -\ncap:239	2269
16	Fall	2025	1L	2025-08-18	2025-11-28	R	03:00 PM-04:15 PM	112	120	Caress Schenk	Red Hall\n1022 (C3) -\ncap:265	2270
674	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	110	120	Maja Savevska	Senate Hall\n- cap:144	2271
675	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	27	29	Alexei Trochev	8.422A -\ncap:32	2272
675	Fall	2025	2L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	32	29	Dinara Pisareva	8.422A -\ncap:32	2273
676	Fall	2025	2L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	26	29	Ho Koh	8.105 -\ncap:70	2274
676	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	27	29	Chunho Park	8.154 -\ncap:56	2275
1030	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	22	18	Andrey\nSemenov	8.308 -\ncap:28	2276
1031	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	20	18	Neil Collins	8.308 -\ncap:28	2277
1032	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	9	18	Bimal Adhikari	8.308 -\ncap:28	2278
1033	Fall	2025	1L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	19	18	Dinara Pisareva	7E.125/1 -\ncap:36	2279
1034	Fall	2025	1L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	20	18	Alexei Trochev	8.308 -\ncap:28	2280
1035	Fall	2025	1L	2025-08-18	2025-11-28	F	10:00 AM-12:50 PM	18	20	Chun Young\nPark	7.507 -\ncap:48	2281
1036	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	14	18	Bimal Adhikari	8.308 -\ncap:28	2282
1037	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	18	18	Alexei Trochev	8.308 -\ncap:28	2283
687	Fall	2025	1L	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Jessica Neafie	\N	2284
687	Fall	2025	2L	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Andrey\nSemenov	\N	2285
687	Fall	2025	3L	2025-08-18	2025-11-28	\N	Online/Distant	3	5	Dinara Pisareva	\N	2286
687	Fall	2025	4L	2025-08-18	2025-11-28	\N	Online/Distant	1	5	Helene Thibault	\N	2287
1038	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	11	12	Ho Koh	8.308 -\ncap:28	2288
1039	Fall	2025	1S	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	14	12	Dinara Pisareva	7E.125/1 -\ncap:36	2289
1040	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	9	12	Brian Smith	8.308 -\ncap:28	2290
1041	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	15	12	Andrey\nSemenov	8.308 -\ncap:28	2291
1042	Fall	2025	1S	2025-08-18	2025-11-28	F	01:00 PM-03:50 PM	12	12	Chunho Park	8.321 -\ncap:32	2292
689	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	8	12	Berikbol\nDukeyev	8.308 -\ncap:28	2293
1043	Fall	2025	1L	2025-08-18	2025-11-28	W	01:00 PM-03:50 PM	9	12	Jessica Neafie	8.321 -\ncap:32	2294
1044	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	12	12	Chun Young\nPark	8.308 -\ncap:28	2295
694	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	5	5	Jessica Neafie	\N	2296
694	Fall	2025	4Int	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Bimal Adhikari	\N	2297
1045	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	09:00 AM-09:50 AM	22	24	Katarzyna Galaj	8.508 -\ncap:27	2298
1045	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	10:00 AM-10:50 AM	23	24	Katarzyna Galaj	8.508 -\ncap:27	2299
706	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	11:00 AM-11:50 AM	16	24	Katarzyna Galaj	8.508 -\ncap:27	2300
1046	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	29	28	Nikolay\nTsyrempilov	9.204 -\ncap:34	2301
1047	Fall	2025	1L	2025-08-18	2025-11-28	M W	10:00 AM-11:15 AM	5	10	Yuliya\nKozitskaya	8.322B -\ncap:28	2302
1048	Fall	2025	1L	2025-08-18	2025-11-28	M W	11:30 AM-12:45 PM	4	10	Aleksandr\nGrishin	8.322B -\ncap:28	2303
718	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	5	10	Andrey\nFilchenko	8.322B -\ncap:28	2304
721	Fall	2025	1S	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	3	10	Meiramgul\nKussainova	8.322B -\ncap:28	2305
722	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	3	10	Sabina\nInsebayeva	8.322B -\ncap:28	2306
1049	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	63	80	Aibek\nNiyetkaliyev	7E.429 -\ncap:90	2307
1050	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	34	40	Ton Duc Do	7.246 -\ncap:48	2308
1050	Fall	2025	1Lb	2025-08-18	2025-11-28	M	12:00 PM-02:45 PM	21	22	Ahmad Alhassan	7.327 -\ncap:48	2309
1050	Fall	2025	2Lb	2025-08-18	2025-11-28	M	03:00 PM-05:45 PM	13	22	Ahmad Alhassan	7.327 -\ncap:48	2310
1051	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	39	40	Matteo\nRubagotti	7.246 -\ncap:48	2311
1051	Fall	2025	1Lb	2025-08-18	2025-11-28	W	12:00 PM-02:45 PM	22	22	Togzhan\nSyrymova	7.327 -\ncap:48	2312
1051	Fall	2025	2Lb	2025-08-18	2025-11-28	W	03:00 PM-05:45 PM	17	22	Togzhan\nSyrymova	7.327 -\ncap:48	2313
1052	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	26	32	Aibek\nNiyetkaliyev	7.246 -\ncap:48	2314
1052	Fall	2025	1Lb	2025-08-18	2025-11-28	R	01:00 PM-02:45 PM	16	16	Azamat\nYeshmukhameto\nv	7.327 -\ncap:48	2315
1052	Fall	2025	2Lb	2025-08-18	2025-11-28	R	03:00 PM-04:45 PM	10	16	Azamat\nYeshmukhameto\nv	7.327 -\ncap:48	2316
1053	Fall	2025	1L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	24	32	Tohid Alizadeh	7.246 -\ncap:48	2317
1053	Fall	2025	1Lb	2025-08-18	2025-11-28	F	12:00 PM-02:45 PM	11	16	Togzhan\nSyrymova	7.327 -\ncap:48	2318
1053	Fall	2025	2Lb	2025-08-18	2025-11-28	F	03:00 PM-05:45 PM	13	16	Togzhan\nSyrymova	7.327 -\ncap:48	2319
1054	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	32	32	Zhanat\nKappassov	7.322 -\ncap:24	2320
1055	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	16	24	Tohid Alizadeh	7.246 -\ncap:48	2321
1055	Fall	2025	2Lb	2025-08-18	2025-11-28	T	12:00 PM-02:45 PM	4	12	Zhanat\nKappassov	7.327 -\ncap:48	2322
1055	Fall	2025	1Lb	2025-08-18	2025-11-28	T	12:00 PM-02:45 PM	12	12	Zhanat\nKappassov	7.322 -\ncap:24	2323
1056	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	34	32	Berdakh\nAbibullaev	3E.227 -\ncap:28	2324
1057	Fall	2025	1L	2025-08-18	2025-11-28	\N	Online/Distant	16	32	Togzhan\nSyrymova	\N	2325
1057	Fall	2025	2L	2025-08-18	2025-11-28	\N	Online/Distant	0	2	Togzhan\nSyrymova	\N	2326
1058	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	97	100	Randy Hazlett	Red Hall\n1022 (C3) -\ncap:265	2327
1059	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	25	30	Zauresh\nAtakhanova	6.105 -\ncap:64	2328
1059	Fall	2025	2L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	27	30	Zauresh\nAtakhanova	6.105 -\ncap:64	2329
1060	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	36	60	Amoussou Coffi\nAdoko	6.507 -\ncap:72	2330
741	Fall	2025	1L	2025-08-18	2025-11-28	\N	Online/Distant	95	100	Dana\nBurkhanova,\nAna Cristina\nHenriques\nMarques	\N	2331
741	Fall	2025	1S	2025-08-18	2025-11-28	M	10:00 AM-10:50 AM	23	25	Dana\nBurkhanova	8.310 -\ncap:30	2332
741	Fall	2025	2S	2025-08-18	2025-11-28	M	09:00 AM-09:50 AM	22	25	Dana\nBurkhanova	8.310 -\ncap:30	2333
741	Fall	2025	3S	2025-08-18	2025-11-28	M	11:00 AM-11:50 AM	25	25	Ana Cristina\nHenriques\nMarques	8.310 -\ncap:30	2334
741	Fall	2025	4S	2025-08-18	2025-11-28	W	11:00 AM-11:50 AM	25	25	Ana Cristina\nHenriques\nMarques	8.310 -\ncap:30	2335
742	Fall	2025	2L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	23	25	Katherine\nErdman	8.154 -\ncap:56	2336
742	Fall	2025	3L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	24	25	Katherine\nErdman	8.154 -\ncap:56	2337
743	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	25	25	Darkhan\nMedeuov	6.522 -\ncap:36	2338
743	Fall	2025	2L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	22	25	Darkhan\nMedeuov	6.522 -\ncap:36	2339
743	Fall	2025	3L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	23	25	Mariya\nSafonova	6.522 -\ncap:36	2340
743	Fall	2025	4L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	22	25	Mariya\nSafonova	6.522 -\ncap:36	2341
744	Fall	2025	1L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	26	25	Ana Cristina\nHenriques\nMarques	8.154 -\ncap:56	2342
746	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	25	25	Darkhan\nMedeuov	8.154 -\ncap:56	2343
1061	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	25	25	Saltanat\nAkhmetova	8.310 -\ncap:30	2344
1062	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	28	25	Matvey\nLomonosov	8.310 -\ncap:30	2345
747	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	25	25	Dana\nBurkhanova	8.310 -\ncap:30	2346
747	Fall	2025	2L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	26	25	Mikhail Sokolov	8.154 -\ncap:56	2347
748	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	25	25	Ana Cristina\nHenriques\nMarques	8.154 -\ncap:56	2348
749	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	27	25	Karina\nMatkarimova	8.310 -\ncap:30	2349
1063	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	25	25	Saltanat\nAkhmetova	8.310 -\ncap:30	2350
1064	Fall	2025	1L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	21	25	Mariya\nSafonova	8.321 -\ncap:32	2351
1064	Fall	2025	2L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	22	25	Mariya\nSafonova	8.321 -\ncap:32	2352
751	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	3	5	Matvey\nLomonosov	\N	2353
752	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Matvey\nLomonosov	\N	2354
753	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	1	5	Matvey\nLomonosov	\N	2355
1065	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	23	25	Mikhail Sokolov	8.154 -\ncap:56	2356
1066	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	13	25	Matvey\nLomonosov	6.522 -\ncap:36	2357
1067	Fall	2025	1CP	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	21	30	Dana\nBurkhanova	8.154 -\ncap:56	2358
1068	Fall	2025	3L	2025-08-18	2025-11-28	M T W R	12:00 PM-12:50 PM	24	24	Arturo Bellido	8.317 -\ncap:28	2359
1068	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	09:00 AM-09:50 AM	25	24	Edyta Denst-\nGarcia	8.305 -\ncap:30	2360
1068	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	10:00 AM-10:50 AM	20	24	Edyta Denst-\nGarcia	8.305 -\ncap:30	2361
1069	Fall	2025	1L	2025-08-18	2025-11-28	M T W R	01:00 PM-01:50 PM	13	24	Arturo Bellido	8.317 -\ncap:28	2362
1069	Fall	2025	2L	2025-08-18	2025-11-28	M T W R	02:00 PM-02:50 PM	25	24	Arturo Bellido	8.317 -\ncap:28	2363
1070	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	31	24	Edyta Denst-\nGarcia	8.321 -\ncap:32	2364
763	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	29	50	Daniel Beben	\N	2365
763	Fall	2025	2Int	2025-08-18	2025-11-28	\N	Online/Distant	3	2	Brandon Brock	\N	2366
764	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	28	50	Daniel Beben	\N	2367
1071	Fall	2025	2L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	40	40	Uli Schamiloglu	8.105 -\ncap:70	2368
768	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	39	40	Funda Guven	8.105 -\ncap:70	2369
770	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	32	30	Wulidanayi\nJumabay	8.105 -\ncap:70	2370
1072	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	15	16	Funda Guven	8.105 -\ncap:70	2371
1073	Fall	2025	1L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	26	24	Wulidanayi\nJumabay	8.105 -\ncap:70	2372
1074	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	63	85	Thomas Duke	5.103 -\ncap:160	2373
4	Fall	2025	38L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	20	20	Nurly Marshal	8.321 -\ncap:32	2374
4	Fall	2025	41L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	18	20	Gulden Issina	8.321 -\ncap:32	2375
4	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	20	20	J.C. Ross	8.307 -\ncap:70	2376
4	Fall	2025	40L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	20	20	J.C. Ross	8.307 -\ncap:70	2377
4	Fall	2025	42L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	19	20	Gulden Issina	8.307 -\ncap:70	2378
4	Fall	2025	43L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	19	20	J.C. Ross	8.307 -\ncap:70	2379
4	Fall	2025	8L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	20	20	Andrew\nDrybrough	6.410 -\ncap:24	2380
4	Fall	2025	16L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	18	20	Ian Albert\nPeterkin Jr	6.410 -\ncap:24	2381
4	Fall	2025	17L	2025-08-18	2025-11-28	M W F	06:00 PM-06:50 PM	18	20	Ian Albert\nPeterkin Jr	6.410 -\ncap:24	2382
4	Fall	2025	21L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	20	20	Jane Hoelker	6.410 -\ncap:24	2383
4	Fall	2025	22L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	17	20	Jane Hoelker	6.410 -\ncap:24	2384
4	Fall	2025	23L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	14	20	Jane Hoelker	6.410 -\ncap:24	2385
4	Fall	2025	28L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	19	20	Michael Jones	6.410 -\ncap:24	2386
4	Fall	2025	29L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	20	20	Michael Jones	6.410 -\ncap:24	2387
4	Fall	2025	35L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	20	20	James Swider	6.410 -\ncap:24	2388
4	Fall	2025	39L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	19	20	Nurly Marshal	6.410 -\ncap:24	2389
4	Fall	2025	2L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	20	20	Gulden Issina	6.402 -\ncap:24	2390
4	Fall	2025	6L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	20	20	Adam Hefty	6.402 -\ncap:24	2391
4	Fall	2025	7L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	18	20	Adam Hefty	6.402 -\ncap:24	2392
4	Fall	2025	9L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	19	20	Fariza Tolesh	6.402 -\ncap:24	2393
4	Fall	2025	24L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	20	20	Jeremy Richard\nSpring	6.402 -\ncap:24	2394
4	Fall	2025	25L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	20	20	Marina Zaffari	6.402 -\ncap:24	2395
4	Fall	2025	26L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	20	20	Marina Zaffari	6.402 -\ncap:24	2396
4	Fall	2025	27L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	19	20	Marina Zaffari	6.402 -\ncap:24	2397
4	Fall	2025	30L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	21	20	Olga Campbell-\nThomson	6.402 -\ncap:24	2398
4	Fall	2025	31L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	20	20	Olga Campbell-\nThomson	6.402 -\ncap:24	2399
4	Fall	2025	3L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	19	20	Nicholas\nWalmsley	7.427 -\ncap:23	2400
4	Fall	2025	4L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	19	20	Nicholas\nWalmsley	7.427 -\ncap:23	2401
4	Fall	2025	5L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	17	20	Nicholas\nWalmsley	7.427 -\ncap:23	2402
4	Fall	2025	13L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	17	20	Bellido\nLanguasco	7.427 -\ncap:23	2403
4	Fall	2025	14L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	15	20	Bellido\nLanguasco	7.427 -\ncap:23	2404
4	Fall	2025	15L	2025-08-18	2025-11-28	M W F	06:00 PM-06:50 PM	20	20	Bellido\nLanguasco	7.427 -\ncap:23	2405
4	Fall	2025	32L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	20	20	Shahreen Binti\nMat Nayan	7.427 -\ncap:23	2406
4	Fall	2025	33L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	20	20	Shahreen Binti\nMat Nayan	7.427 -\ncap:23	2407
4	Fall	2025	34L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	19	20	Benjamin\nGibbon	8.422A -\ncap:32	2408
4	Fall	2025	36L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	20	20	Benjamin\nGibbon	8.422A -\ncap:32	2409
4	Fall	2025	37L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	20	20	Fariza Tolesh	8.422A -\ncap:32	2410
4	Fall	2025	10L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	20	20	Elizabeth Abele	8.140 -\ncap:24	2411
4	Fall	2025	11L	2025-08-18	2025-11-28	M W F	10:00 AM-10:50 AM	19	20	Elizabeth Abele	8.140 -\ncap:24	2412
4	Fall	2025	12L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	20	20	Elizabeth Abele	8.140 -\ncap:24	2413
4	Fall	2025	18L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	19	20	Fariza Tolesh	8.140 -\ncap:24	2414
4	Fall	2025	19L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	20	20	Benjamin\nGibbon	8.140 -\ncap:24	2415
4	Fall	2025	20L	2025-08-18	2025-11-28	M W F	05:00 PM-05:50 PM	20	20	Nurly Marshal	8.140 -\ncap:24	2416
774	Fall	2025	6L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	24	24	Thomas Carl\nHughes	6.402 -\ncap:24	2417
774	Fall	2025	7L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	24	24	Thomas Carl\nHughes	6.402 -\ncap:24	2418
774	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	23	24	Samira Esat	7.527 -\ncap:24	2419
774	Fall	2025	2L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	22	24	Samira Esat	7.527 -\ncap:24	2420
774	Fall	2025	3L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	23	24	Samira Esat	7.527 -\ncap:24	2421
774	Fall	2025	4L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	23	24	Tiffany Moore	8.422A -\ncap:32	2422
774	Fall	2025	5L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	23	24	Tiffany Moore	8.422A -\ncap:32	2423
1075	Fall	2025	1L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	29	30	Thomas Carl\nHughes	8.327 -\ncap:55	2424
1076	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	29	30	Tiffany Moore	7.507 -\ncap:48	2425
13	Fall	2025	4L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	22	24	Gamze Oncul	7.427 -\ncap:23	2426
13	Fall	2025	5L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	24	24	James Nielsen	7.427 -\ncap:23	2427
13	Fall	2025	6L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	20	24	James Nielsen	7.427 -\ncap:23	2428
13	Fall	2025	10L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	22	24	James Nielsen	7.427 -\ncap:23	2429
13	Fall	2025	2L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	23	24	Gamze Oncul	7.527 -\ncap:24	2430
13	Fall	2025	3L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	23	24	Gamze Oncul	7.527 -\ncap:24	2431
13	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	24	24	Bakhtiar\nNaghdipour	8.422A -\ncap:32	2432
13	Fall	2025	7L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	24	24	Shane Coates	8.140 -\ncap:24	2433
13	Fall	2025	8L	2025-08-18	2025-11-28	M W F	01:00 PM-01:50 PM	22	24	Shane Coates	8.140 -\ncap:24	2434
13	Fall	2025	9L	2025-08-18	2025-11-28	M W F	02:00 PM-02:50 PM	24	24	Shane Coates	8.140 -\ncap:24	2435
778	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	22	24	Zhanar\nKabylbekova	8.422A -\ncap:32	2436
778	Fall	2025	2L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	24	24	Zhanar\nKabylbekova	8.422A -\ncap:32	2437
778	Fall	2025	5L	2025-08-18	2025-11-28	M W F	09:00 AM-09:50 AM	24	24	Zhanar\nKabylbekova	8.422A -\ncap:32	2438
778	Fall	2025	3L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	23	24	Marilyn Plumlee	8.140 -\ncap:24	2439
778	Fall	2025	4L	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	22	24	Marilyn Plumlee	8.140 -\ncap:24	2440
779	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	23	24	Brandon Brock	7E.217 -\ncap:24	2441
779	Fall	2025	2L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	20	24	Brandon Brock	7E.217 -\ncap:24	2442
779	Fall	2025	3L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	23	24	James Swider	7E.217 -\ncap:24	2443
779	Fall	2025	4L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	24	24	Michael Jones	7E.217 -\ncap:24	2444
780	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	24	24	Arlyce Menzies	8.140 -\ncap:24	2445
780	Fall	2025	2L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	23	24	Arlyce Menzies	8.140 -\ncap:24	2446
781	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	35	36	Yamen Rahvan	9.105 -\ncap:75	2447
781	Fall	2025	2L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	36	36	Thomas Duke	9.105 -\ncap:75	2448
782	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	8	5	Thomas Duke	\N	2449
783	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Thomas Duke	\N	2450
786	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	14	18	Marilyn Plumlee	8.140 -\ncap:24	2451
787	Fall	2025	1Int	2025-08-18	2025-11-28	S	09:00 AM-10:15 AM	5	6	Adina-Camelia\nArvatu, James\nSwider	online -\ncap:0	2452
791	Fall	2025	1L	2025-08-18	2025-11-28	T R	01:30 PM-02:45 PM	117	120	Jenni Lehtinen	5.103 -\ncap:160	2453
791	Fall	2025	1S	2025-08-18	2025-11-28	F	01:00 PM-01:50 PM	30	30	Jenni Lehtinen	8.305 -\ncap:30	2454
791	Fall	2025	2S	2025-08-18	2025-11-28	F	02:00 PM-02:50 PM	29	30	Jenni Lehtinen	8.305 -\ncap:30	2455
791	Fall	2025	3S	2025-08-18	2025-11-28	F	03:00 PM-03:50 PM	28	30	Jenni Lehtinen	8.305 -\ncap:30	2456
791	Fall	2025	4S	2025-08-18	2025-11-28	F	04:00 PM-04:50 PM	30	30	Jenni Lehtinen	8.305 -\ncap:30	2457
1077	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	79	75	U Kim	5.103 -\ncap:160	2458
1078	Fall	2025	1L	2025-08-18	2025-11-28	M W F	11:00 AM-11:50 AM	30	28	Gabriel McGuire	8.322A -\ncap:32	2459
1079	Fall	2025	1L	2025-08-18	2025-11-28	M W F	12:00 PM-12:50 PM	25	24	Amanda Murphy	8.322A -\ncap:32	2460
1080	Fall	2025	1L	2025-08-18	2025-11-28	T R	04:30 PM-05:45 PM	28	28	Maria Rybakova	8.322A -\ncap:32	2461
793	Fall	2025	1L	2025-08-18	2025-11-28	T R	09:00 AM-10:15 AM	17	20	Jonathan Dupuy	6.410 -\ncap:24	2462
793	Fall	2025	2L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	18	20	Jonathan Dupuy	6.410 -\ncap:24	2463
793	Fall	2025	3L	2025-08-18	2025-11-28	M W F	03:00 PM-03:50 PM	20	20	Ian Albert\nPeterkin Jr	6.410 -\ncap:24	2464
1081	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	25	26	Yuliya\nKozitskaya	3E.221 -\ncap:50	2465
1082	Fall	2025	1L	2025-08-18	2025-11-28	T R	10:30 AM-11:45 AM	25	26	Ivan Delazari	8.322A -\ncap:32	2466
1083	Fall	2025	1L	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	28	26	Yuliya\nKozitskaya	3E.221 -\ncap:50	2467
1084	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	16	16	Arlyce Menzies	6.410 -\ncap:24	2468
1085	Fall	2025	1L	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	15	16	Matthew\nHeeney	9.204 -\ncap:34	2469
1086	Fall	2025	1L	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	20	20	Alima Bissenova	8.310 -\ncap:30	2470
799	Fall	2025	1L	2025-08-18	2025-11-28	\N	Online/Distant	4	5	Amanda Murphy	\N	2471
799	Fall	2025	2L	2025-08-18	2025-11-28	\N	Online/Distant	2	5	Marzieh Sadat\nRazavi	\N	2472
799	Fall	2025	3L	2025-08-18	2025-11-28	\N	Online/Distant	5	10	Florian\nKuechler	\N	2473
800	Fall	2025	1Int	2025-08-18	2025-11-28	\N	Online/Distant	10	10	Yuliya\nKozitskaya	\N	2474
800	Fall	2025	2Int	2025-08-18	2025-11-28	\N	Online/Distant	4	5	Andrey\nFilchenko	\N	2475
800	Fall	2025	3Int	2025-08-18	2025-11-28	\N	Online/Distant	5	5	Wulidanayi\nJumabay	\N	2476
1087	Fall	2025	1L	2025-08-18	2025-11-28	T R	03:00 PM-04:15 PM	24	22	Ivan Delazari	8.322A -\ncap:32	2477
802	Fall	2025	1S	2025-08-18	2025-11-28	T R	06:00 PM-07:15 PM	25	24	Maria Rybakova	8.322A -\ncap:32	2478
1088	Fall	2025	1S	2025-08-18	2025-11-28	T R	12:00 PM-01:15 PM	15	12	Jonathan Dupuy	6.410 -\ncap:24	2479
1089	Fall	2025	1R	2025-08-18	2025-11-28	M W F	04:00 PM-04:50 PM	20	20	Amanda Murphy	8.327 -\ncap:55	2480
38	Summer	2026	1L	2026-06-01	2026-07-22	M W F	09:00 AM-10:30 AM	0	50	Ulan Bigozhin	8.154 -\ncap:56	2481
1090	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	25	Ulan Bigozhin	8.154 -\ncap:56	2482
50	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Snezhana\nAtanova	\N	2483
811	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Snezhana\nAtanova	\N	2484
51	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Snezhana\nAtanova	\N	2485
1091	Summer	2026	1R	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Katherine\nErdman	\N	2486
60	Summer	2026	1Lb	2026-06-01	2026-07-22	M W	12:00 PM-02:50 PM	0	20	Burkitkan\nAkbay	7.407 -\ncap:20	2487
820	Summer	2026	1Lb	2026-06-01	2026-07-22	T R	12:00 PM-02:50 PM	0	16	Burkitkan\nAkbay	7.407 -\ncap:20	2488
1092	Summer	2026	1Wsh	2026-06-01	2026-07-22	\N	Online/Distant	0	10	Zhanat\nMuminova	\N	2489
1093	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	10	Zhanat\nMuminova	\N	2490
20	Summer	2026	1L	2026-06-01	2026-07-22	F	12:00 PM-12:50 PM	0	196	Mirat\nAkshalov,\nSaniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	Orange\nHall -\ncap:450	2491
20	Summer	2026	1R	2026-06-01	2026-07-22	W	10:00 AM-10:50 AM	0	49	Moldir\nKaiynbayeva	(C3) 1009\n- cap:70	2492
20	Summer	2026	2R	2026-06-01	2026-07-22	W	11:00 AM-11:50 AM	0	49	Moldir\nKaiynbayeva	(C3) 1009\n- cap:70	2493
20	Summer	2026	3R	2026-06-01	2026-07-22	W	12:00 PM-12:50 PM	0	49	\N	(C3) 1009\n- cap:70	2494
20	Summer	2026	4R	2026-06-01	2026-07-22	W	01:00 PM-01:50 PM	0	49	Zharaskhan\nTemirkhanov	(C3) 1009\n- cap:70	2495
32	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	40	Saule Issayeva,\nZhannat\nAshikbayeva	7.105 -\ncap:75	2496
32	Summer	2026	2L	2026-06-01	2026-07-22	M W F	01:00 PM-02:30 PM	0	40	Zhannat\nAshikbayeva	7.105 -\ncap:75	2497
113	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	30	Rauan Smail	7E.221 -\ncap:56	2498
113	Summer	2026	2L	2026-06-01	2026-07-22	M W F	01:00 PM-02:30 PM	0	30	Rauan Smail	7E.221 -\ncap:56	2499
114	Summer	2026	1ChLb	2026-06-01	2026-07-22	M W	12:00 PM-02:50 PM	0	24	Roza Oztopcu	9.210 -\ncap:40	2500
114	Summer	2026	2ChLb	2026-06-01	2026-07-22	M W	03:00 PM-05:50 PM	0	24	Aisulu\nZhanbossinova	9.210 -\ncap:40	2501
115	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	30	Aisulu\nZhanbossinova,\nAliya Toleuova	7.210 -\ncap:54	2502
115	Summer	2026	2L	2026-06-01	2026-07-22	M W F	01:00 PM-02:30 PM	0	30	Aisulu\nZhanbossinova,\nAliya Toleuova	7.210 -\ncap:54	2503
116	Summer	2026	1L	2026-06-01	2026-07-22	M W F	01:00 PM-02:30 PM	0	40	Saule Issayeva	7.507 -\ncap:48	2504
116	Summer	2026	2L	2026-06-01	2026-07-22	M W F	03:00 PM-04:30 PM	0	40	Saule Issayeva	7.507 -\ncap:48	2505
1094	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	15	Ozgur Oztopcu	\N	2506
118	Summer	2026	1L	2026-06-01	2026-07-22	T R	12:00 PM-02:30 PM	0	20	Ozgur Oztopcu	7.210 -\ncap:54	2507
119	Summer	2026	1Lb	2026-06-01	2026-07-22	T R	03:00 PM-05:50 PM	0	24	Ozgur Oztopcu	7.307 -\ncap:15	2508
7	Summer	2026	2Lb	2026-06-01	2026-07-22	\N	Online/Distant	0	45	TBA TBA	\N	2509
7	Summer	2026	1L	2026-06-01	2026-07-22	F	03:00 PM-03:50 PM	0	90	TBA TBA	7E.429 -\ncap:90	2510
7	Summer	2026	1Lb	2026-06-01	2026-07-22	M W	03:00 PM-04:15 PM	0	45	TBA TBA	7E.125/3 -\ncap:98	2511
31	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	160	Askar\nBoranbayev	\N	2512
30	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	50	Askar\nBoranbayev	\N	2513
246	Summer	2026	1L	2026-06-01	2026-07-22	T R	05:00 PM-07:30 PM	0	40	Julio Davila\nMuro	8.522 -\ncap:72	2514
249	Summer	2026	1L	2026-06-01	2026-07-22	T R	02:00 PM-04:30 PM	0	40	Julio Davila\nMuro	8.522 -\ncap:72	2515
252	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	20	Aigerim\nSarsenbayeva	\N	2516
309	Summer	2026	1L	2026-06-01	2026-07-22	T R	03:00 PM-04:15 PM	0	20	Ainur\nRakhymbay	online -\ncap:0	2517
889	Summer	2026	1L	2026-06-01	2026-07-22	T	10:30 AM-11:45 AM	0	20	Azamat\nMukhamediya	online -\ncap:0	2518
894	Summer	2026	1L	2026-06-01	2026-07-22	T R	01:30 PM-02:45 PM	0	20	Azamat\nMukhamediya	online -\ncap:0	2519
320	Summer	2026	1L	2026-06-01	2026-07-22	T R	03:00 PM-04:15 PM	0	5	Azamat\nMukhamediya	online -\ncap:0	2520
1095	Summer	2026	1OCA	2026-06-01	2026-07-22	M W F	10:00 AM-05:50 PM	0	12	Jovid Aminov	6.105 -\ncap:64	2521
6	Summer	2026	1L	2026-06-01	2026-07-22	\N	Online/Distant	0	72	Rozaliya\nGaripova	\N	2522
6	Summer	2026	1S	2026-06-01	2026-07-22	M R	02:00 PM-02:50 PM	0	24	Rozaliya\nGaripova	8.105 -\ncap:70	2523
6	Summer	2026	2S	2026-06-01	2026-07-22	M R	03:00 PM-03:50 PM	0	24	Rozaliya\nGaripova	8.105 -\ncap:70	2524
6	Summer	2026	3S	2026-06-01	2026-07-22	M R	04:00 PM-04:50 PM	0	24	Rozaliya\nGaripova	8.105 -\ncap:70	2525
928	Summer	2026	1L	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Mikhail Akulov	\N	2526
928	Summer	2026	2L	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Di Lu	\N	2527
1096	Summer	2026	1S	2026-06-01	2026-07-22	\N	Online/Distant	0	90	Zhanar\nBaiteliyeva	\N	2528
390	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	16	Samal\nAbzhanova	8.302 -\ncap:54	2529
391	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	16	Meruyert\nIbrayeva	8.307 -\ncap:70	2530
393	Summer	2026	1S	2026-06-01	2026-07-22	M W F	01:00 PM-02:30 PM	0	30	Meruyert\nIbrayeva	8.307 -\ncap:70	2531
403	Summer	2026	1L	2026-06-01	2026-07-22	M W F	09:00 AM-10:30 AM	0	30	Yermek\nAdayeva	8.105 -\ncap:70	2532
403	Summer	2026	2L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	30	Yermek\nAdayeva	8.105 -\ncap:70	2533
408	Summer	2026	1L	2026-06-01	2026-07-22	M W F	01:00 PM-02:30 PM	0	30	Samal\nAbzhanova	8.302 -\ncap:54	2534
934	Summer	2026	1L	2026-06-01	2026-07-22	M T W R F	09:00 AM-12:30 PM	0	16	Aidar\nBalabekov	8.327 -\ncap:55	2535
1097	Summer	2026	1L	2026-06-01	2026-07-22	M T W R F	09:00 AM-12:30 PM	0	16	Aidar\nBalabekov	8.327 -\ncap:55	2536
935	Summer	2026	1L	2026-06-01	2026-07-22	M T W R	09:00 AM-10:30 AM	0	24	Joomi Kong	8.305 -\ncap:30	2537
1098	Summer	2026	1L	2026-06-01	2026-07-22	M T W R	01:00 PM-02:00 PM	0	28	Eva-Marie\nDubuisson	8.154 -\ncap:56	2538
419	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	28	Benjamin\nBrosig	9.105 -\ncap:75	2539
420	Summer	2026	1Wsh	2026-06-01	2026-07-22	\N	Online/Distant	0	1	Florian\nKuechler	\N	2540
1099	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	20	Yerkin\nAbdildin, Altay\nZhakatayev	\N	2541
1	Summer	2026	1L	2026-06-01	2026-07-22	M T W R	10:30 AM-11:45 AM	0	90	Samat\nKassabek	7E.222 -\ncap:95	2542
1	Summer	2026	1R	2026-06-01	2026-07-22	F	10:30 AM-11:45 AM	0	90	Samat\nKassabek	7E.222 -\ncap:95	2543
5	Summer	2026	1L	2026-06-01	2026-07-22	T W R	01:30 PM-02:45 PM	0	210	Aigerim\nMadiyeva	Blue Hall -\ncap:239	2544
5	Summer	2026	1R	2026-06-01	2026-07-22	F	01:30 PM-02:45 PM	0	105	Viktor Ten,\nAigerim\nMadiyeva	7E.222 -\ncap:95	2545
5	Summer	2026	2R	2026-06-01	2026-07-22	F	12:00 PM-01:15 PM	0	105	Viktor Ten,\nAigerim\nMadiyeva	7E.222 -\ncap:95	2546
2	Summer	2026	1PLb	2026-06-01	2026-07-22	M W	12:00 PM-02:50 PM	0	36	TBA1 TBA1	9.202 -\ncap:40	2547
2	Summer	2026	2PLb	2026-06-01	2026-07-22	T R	12:00 PM-02:50 PM	0	36	TBA1 TBA1	9.202 -\ncap:40	2548
2	Summer	2026	3PLb	2026-06-01	2026-07-22	M W	03:00 PM-05:50 PM	0	36	TBA1 TBA1	9.202 -\ncap:40	2549
2	Summer	2026	1L	2026-06-01	2026-07-22	M T W F	10:30 AM-11:45 AM	0	108	Zhandos\nUtegulov,\nKyunghwan Oh	7E.329 -\ncap:95	2550
2	Summer	2026	1R	2026-06-01	2026-07-22	R	10:30 AM-11:45 AM	0	108	Ainur\nKoshkinbayeva,\nBekdaulet\nShukirgaliyev	7E.329 -\ncap:95	2551
8	Summer	2026	1PLb	2026-06-01	2026-07-22	M W	03:00 PM-05:50 PM	0	36	TBA1 TBA1	9.222 -\ncap:40	2552
8	Summer	2026	2PLb	2026-06-01	2026-07-22	M W	09:00 AM-11:50 AM	0	36	TBA1 TBA1	9.222 -\ncap:40	2553
8	Summer	2026	3PLb	2026-06-01	2026-07-22	T R	09:00 AM-11:50 AM	0	36	TBA1 TBA1	9.222 -\ncap:40	2554
8	Summer	2026	1L	2026-06-01	2026-07-22	M T W F	12:00 PM-01:15 PM	0	108	Alexander\nTikhonov,\nMarat\nKaikanov	7E.329 -\ncap:95	2555
8	Summer	2026	1R	2026-06-01	2026-07-22	R	12:00 PM-01:15 PM	0	108	Ainur\nKoshkinbayeva,\nBekdaulet\nShukirgaliyev	7E.329 -\ncap:95	2556
1100	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	36	Askhat\nJumabekov	\N	2557
1101	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	36	Zhandos\nUtegulov	\N	2558
1029	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	40	Jean-Francois\nCaron	8.522 -\ncap:72	2559
676	Summer	2026	1L	2026-06-01	2026-07-22	T R	12:00 PM-02:30 PM	0	24	Ho Koh	8.422A -\ncap:32	2560
687	Summer	2026	1L	2026-06-01	2026-07-22	\N	Online/Distant	0	3	Andrey\nSemenov	\N	2561
687	Summer	2026	2L	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Bimal Adhikari	\N	2562
687	Summer	2026	3L	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Helene\nThibault	\N	2563
687	Summer	2026	4L	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Neil Collins	\N	2564
691	Summer	2026	1L	2026-06-01	2026-07-22	T R	09:30 AM-12:00 PM	0	24	Chun Young\nPark	8.422A -\ncap:32	2565
694	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Bimal Adhikari	\N	2566
694	Summer	2026	2Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Helene\nThibault	\N	2567
694	Summer	2026	3Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Alexei Trochev	\N	2568
694	Summer	2026	4Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Maja Savevska	\N	2569
1102	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	32	Togzhan\nSyrymova	\N	2570
751	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Matvey\nLomonosov	\N	2571
752	Summer	2026	2Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Matvey\nLomonosov	\N	2572
753	Summer	2026	2Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Matvey\nLomonosov	\N	2573
763	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	150	Daniel Beben	\N	2574
764	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	100	Daniel Beben	\N	2575
4	Summer	2026	1L	2026-06-01	2026-07-22	M W F	11:00 AM-12:30 PM	0	20	Fariza Tolesh,\nJane Hoelker	8.310 -\ncap:30	2576
783	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	2	Thomas Duke	\N	2577
785	Summer	2026	1L	2026-06-01	2026-07-22	\N	Online/Distant	0	2	Brandon Brock	\N	2578
799	Summer	2026	1L	2026-06-01	2026-07-22	\N	Online/Distant	0	24	Florian\nKuechler	\N	2579
800	Summer	2026	1Int	2026-06-01	2026-07-22	\N	Online/Distant	0	7	Gabriel\nMcGuire	\N	2580
800	Summer	2026	2Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Andrey\nFilchenko	\N	2581
800	Summer	2026	3Int	2026-06-01	2026-07-22	\N	Online/Distant	0	5	Wulidanayi\nJumabay	\N	2582
\.


--
-- Data for Name: course_reviews; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.course_reviews (course_id, user_id, comment, overall_rating, difficulty, informativeness, gpa_boost, workload, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.courses (code, level, title, department, ects, description, pass_grade, school, academic_level, credits_us, prerequisites, corequisites, antirequisites, priority_1, priority_2, priority_3, priority_4, requirements_term, requirements_year, id) FROM stdin;
ACCT	201	Introduction to Accounting	ACCT	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	36
ANT	101	Being Human: An\nIntroduction to Four Field\nAnthropology	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	37
ANT	140	World Prehistory	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	39
ANT	214	Qualitative Methods	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	40
ANT	215	What is Islam?\nAnthropological\nPerspectives	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	41
ANT	231	Frauds and Fallacies in\nArchaeology	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	42
ANT	232	Life, Death and Economy:\nArchaeology of Central Asia	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	43
ANT	270	Anthropology of Warfare	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	44
ANT	286	Nomads: Around the world\nand through time	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	45
ANT	306	Anthropology of\nPerformance	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	46
ANT	317	Museum space: collections,\ncollectors and society	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	47
ANT	361	Human Evolution: Bones,\nStones and Genomes	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	48
ANT	386	Social Challenges of\nClimate Change	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	49
ANT	412	Approaches to Global\nDevelopment	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	52
ANT	499	Capstone Seminar II	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	53
BBA	201	Management and\nOrganizations	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	54
BBA	203	Responsible Leadership\n(Ethics)	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	55
BBA	209	Environmental, Social and\nGovernance Factors (ESG)\nfor Business	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	56
BBA	240	Strategy	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	57
BBA	260	Operations Management	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	58
BIOL	101	Introductory Biology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	23
BIOL	110	Modern Biology I	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	59
BIOL	110L	Modern Biology I\nLaboratory	BIOL	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	60
BIOL	120	Modern Biology II	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	61
BIOL	230	Human Anatomy and\nPhysiology I	BIOL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	62
BIOL	301	Molecular Cell Biology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	63
BIOL	301L	Molecular Cell Biology\nLaboratory	BIOL	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	64
BIOL	305	Introduction to\nMicrobiology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	65
BIOL	305L	Introduction to\nMicrobiology Laboratory	BIOL	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	66
BIOL	310	Immunology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	67
BIOL	321	Bioethics	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	68
BIOL	331	Human Anatomy and\nPhysiology II	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	69
BIOL	333	Environmental Biology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	70
BIOL	341	Biochemistry I	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	71
BIOL	355	Critical Research\nReasoning	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	72
BIOL	370	Genetics	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	73
BIOL	425	Biomedical Research\nMethods	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	74
BIOL	440	Neuroscience	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	75
BIOL	445	Medical Microbiology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	76
BIOL	450	Food Microbiology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	77
BIOL	471	Light and Electron\nmicroscopy concepts and\ntechniques	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	78
BIOL	471L	Light and Electron\nMicroscopy Concepts and\nTechniques-Lab	BIOL	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	79
BIOL	481	Neuroimmunology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	80
BIOL	491	Honors Thesis	BIOL	18	\N	\N	SSH	UG	9	\N	\N	\N	\N	\N	\N	\N	\N	\N	81
CSCI	231	Computer Systems and\nOrganization	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	9
CSCI	235	Programming Languages	CSCI	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	12
CSCI	341	Database Systems	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	21
CSCI	361	Software Engineering	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	24
CSCI	390	Artificial Intelligence	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	19
CSCI	393	Introduction to Natural\nLanguage Processing	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	33
CSCI	408	Senior Project I	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	35
ANT	110	Introduction to\nSociocultural\nAnthropology	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	38
ANT	400	Research\nAssistance in\nAnthropology	ANT	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	50
ANT	402	Research\nAssistance in\nAnthropology	ANT	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	51
BIOL	492	Research Experience in\nBiology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	82
BIOL	502	Research Methods and\nBioethics	BIOL	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	83
BIOL	580	Applied Bioinformatics	BIOL	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	84
BIOL	590	Research Design and\nProject Planning	BIOL	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	85
BIOL	591	Cellular Biophysics	BIOL	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	86
BIOL	599	Master’s Thesis Research	BIOL	0	\N	\N	SSH	GrM	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	87
BIOL	630	Advanced Neuroscience	BIOL	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	88
BIOL	637	Fundamentals of Advanced\nMicroscopy	BIOL	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	89
BIOL	637L	Fundamentals of advanced\nmicroscopy	BIOL	2	\N	\N	SSH	GrM	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	90
BIOL	692	Master’s Thesis	BIOL	30	\N	\N	SSH	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	91
BIOL	800	Thesis Research	BIOL	0	\N	\N	SSH	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	92
BIOL	802	Research Methods and\nBioethics	BIOL	6	\N	\N	SSH	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	93
BIOL	830	Advanced Neuroscience	BIOL	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	94
BIOL	837	Advanced Optical and\nElectron Microscopy	BIOL	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	95
BIOL	880	Applied Bioinformatics	BIOL	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	96
BIOL	891	Cellular Biophysics	BIOL	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	97
BUS	420	Business Law	BUS	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	98
CEE	202	Environmental Engineering	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	99
CEE	203	Structural Analysis	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	100
CEE	301	Structural Design – Steel	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	101
CEE	303	Geotechnical Design	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	102
CEE	305	Hydraulics and Hydrology	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	103
CEE	350	Water and Wastewater\nTreatment Processes	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	104
CEE	400	Transportation Engineering	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	105
CEE	454	Foundation Engineering	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	106
CEE	457	Air Quality Management	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	107
CEE	458	Modern Information\nTechnology in Construction	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	108
CEE	465	Structure and Properties of\nConcrete Materials	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	110
CEE	466	Introduction to Finite\nElement Methods	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	111
CEE	470	Construction Engineering\nEconomics	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	112
CHEM	189A	Independent Study	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	117
CHEM	212	Organic Chemistry II	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	120
CHEM	212L	Organic Chemistry II Lab	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	121
CHEM	250	Descriptive Inorganic\nChemistry	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	122
CHEM	320	Instrumental Analysis	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	123
CHEM	320L	Instrumental Analysis Lab	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	124
CHEM	332	Physical Chemistry II	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	125
CHEM	332L	Physical Chemistry II Lab	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	126
CHEM	341L	Biochemistry I Lab	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	127
CHEM	380	Research Methods	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	128
CHEM	400	Chemistry Seminar	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	129
CHEM	411	Advanced Organic\nChemistry I	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	130
CHEM	431	Computational Chemistry	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	131
CHEM	433	Surfactants and Colloids	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	132
CHEM	445	Drug Discovery and\nDevelopment	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	133
CHEM	489	Directed Research II	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	134
CHEM	490	Nanochemistry	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	135
CHEM	515	Applied Colloid and\nSurfactant Science	CHEM	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	136
CHEM	540	Organic Reactions and\nMechanisms	CHEM	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	137
CHEM	542	Advanced Topics in Drug\nDesign	CHEM	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	138
CHEM	550	Selected Topics in\nChemistry	CHEM	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	139
CHEM	560	Directed research in\nchemistry	CHEM	0	\N	\N	SSH	GrM	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	140
CHEM	592	Chemistry Seminar	CHEM	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	141
CHEM	692	MSc Thesis in Chemistry	CHEM	36	\N	\N	SSH	GrM	18	\N	\N	\N	\N	\N	\N	\N	\N	\N	142
CHEM	710	Mechanistic Principles of\nOrganic Reactions	CHEM	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	143
CHEM	723	Membrane Science and\nTechnology	CHEM	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	144
CHEM	731	Design of Functional\nMaterials	CHEM	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	145
CHEM	733	Colloid and Surfactant\nScience	CHEM	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	146
CHEM	752	Materials Chemistry	CHEM	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	147
CHEM	780	Research Methods and\nEthics	CHEM	6	\N	\N	SSH	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	148
CHEM	798	Thesis Research	CHEM	0	\N	\N	SSH	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	149
CHME	202	Fluid Mechanics	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	150
CHME	203	Organic and Polymer\nChemistry	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	151
CHME	303	Separation Processes	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	152
CHME	304	Chemical Reaction\nEngineering	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	153
CHME	305L	Chemical Engineering\nLaboratory I	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	154
BUS	101	Core Course in\nBusiness	BUS	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	20
CHME	352	Research Practice	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	155
CHME	402	Materials Chemistry	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	156
CHME	403	Chemical Process Control\nand Safety	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	157
CHME	421	Tissue Engineering	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	158
CHME	454	Transport Phenomena and\nOperations	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	159
CHME	461	Powder technology	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	160
CHN	102	Beginning Mandarin II	CHN	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	161
CHN	301	Upper Intermediate\nChinese I	CHN	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	162
CSCI	111	Web Programming and\nProblem Solving	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	163
CSCI	115	Programming\nFundamentals	CSCI	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	164
CSCI	245	System Analysis and Design	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	165
CSCI	262	Software Project\nManagement	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	166
CSCI	270	Algorithms	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	14
CSCI	272	Formal Languages	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	15
CSCI	281	Human-Computer\nInteraction	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	167
CSCI	299	Internship I	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	31
CSCI	307	Research Methods	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	168
CSCI	332	Operating Systems	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	29
CSCI	333	Computer Networks	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	27
CSCI	363	Software Testing and\nQuality Assurance	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	169
CSCI	399	Internship II	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	30
CSCI	409	Senior Project II	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	170
CSCI	435	Blockchain and\nCryptocurrencies	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	171
CSCI	436	Introduction to Cloud\nComputing	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	172
CSCI	437	Internet of Things:\nTechnologies and\nApplications	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	173
CSCI	462	Open Source Software	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	175
CSCI	490	Brain Computer Interface	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	176
CSCI	496	Generative Artificial\nIntelligence	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	177
CSCI	502	Hardware Software Co-\nDesign	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	178
CSCI	512	Information Theory	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	179
CSCI	531	Distributed Systems	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	180
CSCI	545	Big Data Analytics	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	181
CSCI	563	Software Testing and\nQuality Assurance	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	182
CSCI	575	Formal Methods and\nApplications	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	183
CSCI	593	Natural Language\nProcessing	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	184
CSCI	595	Generative Artificial\nIntelligence	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	185
CSCI	597	Machine Learning: Theory\nand Practice	CSCI	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	186
CSCI	694	Thesis	CSCI	30	\N	\N	SEDS	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	187
CSCI	151	Programming for\nScientists and Engineers	CSCI	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	3
CSCI	702	Advanced\nHardware/Software Co-\nDesign	CSCI	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	189
CSCI	722	Current Research\nLiterature	CSCI	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	190
CSCI	795	Advanced Generative\nArtificial Intelligence	CSCI	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	191
CSCI	447	Machine Learning:\nTheory and Practice	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	174
DCEE	701	Current Research\nLiterature	DCEE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	193
DCEE	751	Structural Dynamics and\nEarthquake Engineering	DCEE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	194
DCEE	759	Geotechnical Earthquake\nEngineering	DCEE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	195
DCEE	768	Advanced Wastewater\nTreatment	DCEE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	196
DCEE	769	Sustainable Construction\nand Development	DCEE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	197
CSCI	152	Performance and\nData Structures	CSCI	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	7
DCHME	701	Current Research\nLiterature	DCHME	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	199
DCHME	752	Polymer Melt Fluid\nMechanics and Processing	DCHME	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	200
DCHME	757	Advanced Chemical\nEngineering\nThermodynamics	DCHME	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	201
DCHME	763	Advanced Heat and Mass\nTransfer	DCHME	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	202
DELCE	701	Current Research\nLiterature	DELCE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	204
DELCE	759	Advanced Pattern\nRecognition and Machine\nLearning	DELCE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	205
DELCE	762	Fundamentals of Signal\nProcessing	DELCE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	206
DELCE	763	Advanced Electronic\nCircuits	DELCE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	207
DELCE	764	Advanced Semiconductor\nProcess Engineering for\nVLSI	DELCE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	208
DENG	701	Thesis Literature Research	DENG	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	210
DENG	795	Research at Host\nUniversity	DENG	12	\N	\N	SEDS	PhD	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	211
DMAE	702	Current Research\nLiterature	DMAE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	213
CSCI	700	Thesis Research	CSCI	0	\N	\N	SEDS	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	188
DCEE	700	Thesis Research	DCEE	0	\N	\N	SEDS	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	192
DCHME	700	Thesis Research	DCHME	0	\N	\N	SEDS	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	198
DMAE	703	Numerical Techniques for\nEngineers	DMAE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	214
DMAE	750	Advanced Statistics and\nProbability	DMAE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	215
DMAE	769	Advanced Computational\nFluid Dynamics and Heat\nTransfer in Mechanical\nEngineering	DMAE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	216
DMAE	771	Space Flight Dynamics	DMAE	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	217
DPP	600	Developing Dissertation\nResearch	DPP	0	\N	\N	GSPP	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	218
DPP	602	Macroeconomics in Public\nSector	DPP	8	\N	\N	GSPP	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	219
DPP	613	Research Design\n(qualitative and\nquantitative)	DPP	8	\N	\N	GSPP	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	220
DPP	621	Public Policy and Analysis	DPP	8	\N	\N	GSPP	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	221
DPP	631	Politics of Public Policy	DPP	8	\N	\N	GSPP	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	222
DPP	689	PhD Qualifying\nExaminations	DPP	0	\N	\N	GSPP	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	223
DPP	690	Thesis Preparation and\nWriting	DPP	0	\N	\N	GSPP	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	224
DPP	699	Thesis Design and Written\nProposal	DPP	12	\N	\N	GSPP	PhD	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	225
DS	504	Data Mining and Decision\nSupport	DS	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	226
DS	551	Process and Project\nManagement	DS	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	227
DS	694	Thesis	DS	30	\N	\N	SEDS	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	228
DS	704	Advanced Data Mining and\nDecision Support	DS	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	229
DUT	101	Beginning Dutch I	DUT	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	230
EAS	502	Disciplinary Methodology	EAS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	231
EAS	504	Thesis II	EAS	25	\N	\N	SSH	GrM	12.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	232
EAS	505	Research and Fieldwork\nPracticum	EAS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	233
EAS	511	Independent Study in\nEurasian Studies	EAS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	234
EAS	512	Topics in Eurasian Studies	EAS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	235
EAS	513	Critical Issues in Eurasian\nStudies	EAS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	236
EAS	514	Topics in Eurasian Social\nSciences	EAS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	237
EAS	702	Elective in Eurasian\nHumanities	EAS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	238
EAS	703	Elective in Eurasian Social\nSciences	EAS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	239
EAS	704	Elective 2 in Eurasian\nHumanities	EAS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	240
EAS	705	Elective 2 in Social\nSciences	EAS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	241
EAS	710	Independent Study in\nEurasian Studies	EAS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	242
EAS	712	Doctoral Seminar in\nEurasian Studies II	EAS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	243
EAS	713	Qualifying Examination	EAS	0	\N	\N	SSH	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	244
EAS	800	Dissertation Research in\nEurasian Studies	EAS	0	\N	\N	SSH	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	245
ECON	101	Introduction to\nMicroeconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	246
ECON	102	Introduction to\nMacroeconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	247
ECON	120	Managerial Economics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	248
ECON	201	Intermediate\nMicroeconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	249
ECON	202	Intermediate\nMacroeconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	250
ECON	211	Economic Statistics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	251
ECON	301	Econometrics I	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	253
ECON	319	Matching Theory and\nApplications	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	254
ECON	335	Economics of Information	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	255
ECON	336	Programming for\nEconomists	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	256
ECON	337	Empirical Finance	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	257
ECON	341	Economic Simulation\nModeling	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	258
ECON	400	Research Assistance in\nEconomics 2	ECON	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	259
ECON	413	Econometrics II Time\nSeries	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	260
ECON	415	Industrial Organization	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	261
ECON	434	Introduction to Big Data\nAnalytics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	262
ECON	498	Advanced Special Topics in\nEconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	263
ECON	521	Microeconomic Theory II	ECON	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	264
ECON	522	Macroeconomics II	ECON	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	265
ECON	531	Econometrics	ECON	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	266
ECON	532	Applied Econometrics	ECON	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	267
ECON	534	Introduction to Big Data\nAnalytics	ECON	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	268
ECON	536	Programming for\nEconomists	ECON	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	269
ECON	541	Economic Simulation\nModeling	ECON	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	270
ECON	590	Thesis II	ECON	16	\N	\N	SSH	GrM	8	\N	\N	\N	\N	\N	\N	\N	\N	\N	271
EDHE	604	Thesis Seminar 4	EDHE	0	\N	\N	GSE	GrM	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	272
EDHE	605	Thesis Submission and\nDefense	EDHE	21	\N	\N	GSE	GrM	10.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	273
EDHE	626	Organization and\nGovernance in Higher\nEducation	EDHE	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	274
EDHE	628	Higher Education Policy\nAnalysis and Development	EDHE	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	275
EDHE	629	Globalization and\nInternational Higher\nEducation	EDHE	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	276
EDIE	604	Thesis Seminar 4	EDIE	0	\N	\N	GSE	GrM	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	277
EDIE	605	Thesis Submission and\nDefense	EDIE	21	\N	\N	GSE	GrM	10.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	278
EDIE	626	Global Perspectives on\nInclusive Education	EDIE	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	279
EDIE	628	Inclusive Curriculum and\nAssessment	EDIE	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	280
EDML	612	Multilingual Society	EDML	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	281
EDML	620	Language and Literacy\nDevelopment	EDML	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	282
EDML	622	First and Second Language\nAcquisition	EDML	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	283
EDML	695	Thesis Research 3	EDML	24	\N	\N	GSE	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	284
EDSE	604	Thesis Seminar 4	EDSE	0	\N	\N	GSE	GrM	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	285
EDSE	605	Thesis Submission and\nDefense	EDSE	21	\N	\N	GSE	GrM	10.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	286
EDSE	626	Curriculum Development\nand Implementation	EDSE	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	287
EDSE	629	Teacher Development and\nIdentity	EDSE	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	288
EDUC	513	English for Thesis Writing\nII	EDUC	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	289
EDUC	531	Academic English 2	EDUC	4	\N	\N	GSE	GrM	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	290
EDUC	573	Academic Writing in\nKazakh	EDUC	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	291
EDUC	583	Academic Writing in\nKazakh (MSc)	EDUC	4	\N	\N	GSE	GrM	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	292
EDUC	585	Education in Kazakhstan\nfor International Students	EDUC	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	293
EDUC	591	Academic English Writing\nfor Doctoral Students II	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	294
EDUC	592	Academic English Writing\nfor Doctoral Students III	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	295
EDUC	608	Research Methods 2	EDUC	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	296
EDUC	618	Educational Leadership	EDUC	6	\N	\N	GSE	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	297
EDUC	704	Advanced Methods of\nEducation Research	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	298
EDUC	705	Advanced Methods of\nEducation Research:\nQualitative Methods	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	299
EDUC	711	Globalisation and\nEducation	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	300
EDUC	720	Philosophy of Education	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	301
EDUC	728	Exploring the Research\nTopic 2	EDUC	0	\N	\N	GSE	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	302
EDUC	730	Preparation for Proposal\nDefence	EDUC	0	\N	\N	GSE	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	303
EDUC	733	Thesis Proposal Defense	EDUC	25	\N	\N	GSE	PhD	12.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	304
EDUC	740	Doctoral seminar 1	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	305
EDUC	741	Doctoral seminar 2	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	306
EDUC	751	Dissertation Research	EDUC	0	\N	\N	GSE	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	307
EDUC	760	Teaching and Learning in\nthe University Context:\nCurriculum, Pedagogy and\nAssessment	EDUC	6	\N	\N	GSE	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	308
ELCE	201	Circuits Theory II	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	309
ELCE	201L	Circuit Theory Laboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	310
ELCE	202	Digital Logic Design	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	311
ELCE	202L	Digital Logic Design\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	312
ELCE	300	Microprocessor Systems	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	313
ELCE	300L	Microprocessor Systems\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	314
ELCE	302	Electric Machines	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	315
ELCE	302L	Electrical Machines\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	316
ELCE	303	Power System Analysis	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	317
ELCE	305	Data Structures and\nAlgorithms	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	318
ELCE	308	Communication Systems	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	319
ELCE	350	Electromagnetics I	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	321
ELCE	352	Applied Simulation\nLaboratory	ELCE	4	\N	\N	SEDS	UG	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	322
ELCE	403	Introduction to Adaptive\nSignal Processing	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	323
ELCE	458	Numerical Optimization\nTechniques and Computer\nApplications	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	324
ELCE	461	Industrial Automation	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	325
ELCE	461L	Industrial Automation\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	326
ELCE	468	Robots For Rehabilitation	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	327
ELCE	469	Microfluidics Fundamentals\nand Applications	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	328
ELCE	470	Optical Communications	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	329
ELCE	486	Photonics for Engineering	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	330
EMEM	551	Digital Transformation and\nDisruption	EMEM	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	331
EMEM	553	Capstone Project\nDevelopment	EMEM	24	\N	\N	SEDS	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	332
ENG	102	Engineering Materials I	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	334
ENG	103	Engineering Materials II	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	335
ENG	201	Applied Probability and\nStatistics	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	336
ENG	202	Numerical Methods in\nEngineering	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	337
ENG	400	Capstone Project	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	338
FEAP	020	Foundation English for\nAcademic Purposes 2	FEAP	0	\N	\N	CPS	CPS NUFYP	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	339
FIN	201	Principles of Finance	FIN	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	340
FLDP	095	Leadership 2	FLDP	0	\N	\N	CPS	CPS NUFYP	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	341
FMAT	041	Foundation Mathematics 2	FMAT	0	\N	\N	CPS	CPS NUFYP	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	342
GEOL	101	Fundamentals of Geology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	343
GEOL	103	Introduction to Geology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	344
GEOL	204	Sedimentology and\nstrartigraphy	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	345
GEOL	205	Paleontology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	346
GEOL	301	Igneous and metamorphic\npetrology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	347
GEOL	304	Geophysics	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	348
GEOL	306	Geodynamics	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	349
GEOL	307	Geographic Information\nSystems	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	350
GEOL	309	Hydrogeology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	351
GEOL	403	Geostatistics	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	352
GEOL	405	Research Project II	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	353
GEOL	408	Remote Sensing of the\nEarth	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	354
GEOL	411	Photography for\nGeosciences	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	355
GEOL	506	Advanced Petrology	GEOL	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	356
GEOL	507	Exploration Geoscience	GEOL	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	357
GEOL	508	Advanced Structural\nGeology and Microtectonics	GEOL	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	358
GEOL	509	Advanced Field Geology	GEOL	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	359
ELCE	311	Interdisciplinary\nDesign Project	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	320
GEOL	690	Thesis II	GEOL	30	\N	\N	SMG	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	360
GER	102	Beginning German II	GER	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	361
GER	202	Intermediate German II	GER	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	362
GSBF	513	Financial Data Analytics II	GSBF	5	\N	\N	GSB	GrM	2.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	363
GSBF	514	Corporate Finance	GSBF	5	\N	\N	GSB	GrM	2.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	364
GSBF	520	Empirical Asset Pricing	GSBF	5	\N	\N	GSB	GrM	2.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	365
GSBPHD	03	Quantitative Research\nMethods	GSBPHD	8	\N	\N	GSB	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	366
GSBPHD	04	Core Research Skills I	GSBPHD	8	\N	\N	GSB	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	367
GSBPHD	08	Core Research Skills II	GSBPHD	8	\N	\N	GSB	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	368
GSBPHD	14	Thesis Research Progress	GSBPHD	0	\N	\N	GSB	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	369
HST	123	Introduction to the History\nof Science and Technology	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	370
HST	132	European History II (from\n1700)	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	372
HST	205	The Mongol Empire	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	373
HST	243	Soviet History Through\nFilm	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	374
HST	245	Global History of Travel\nand Travel Literature	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	375
HST	272	Modern Turkey: from the\nOttoman Empire to the\nTurkish Republic	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	376
HST	273	History of Sufism in the\nMiddle East and Central\nAsia	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	377
HST	274	Texts and Contexts	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	378
HST	319	Philosophy of History	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	379
HST	336	The Totalitarian\nPhenomenon	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	380
HST	400	Research Assistance	HST	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	381
HST	440	Religions in the Soviet and\nPost-Soviet Eras	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	382
HST	447	Media and Memory Politics\nin the Post-Soviet Space	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	383
HST	462	History of Islam Under\nRussian Rule	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	384
HST	499	History Capstone:\nUndergraduate\nDissertation	HST	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	385
HST	540	Religions in the Soviet and\nPost-Soviet Eras	HST	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	386
HST	547	Media and Memory Politics\nin the Post-Soviet Space	HST	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	387
HST	562	History of Islam under\nRussian Rule	HST	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	388
HST	747	Media and Memory Politics\nin the Post-Soviet Space	HST	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	389
KAZ	312	Kazakh discourse	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	393
KAZ	313	Kazakh for Business	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	394
KAZ	349	Kazakh Mythology	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	395
KAZ	350	Kazakh Literature	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	396
KAZ	351	Kazakh Short Stories	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	397
KAZ	356	Kazakh Music History	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	398
KAZ	357	Literature of Alash	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	399
KAZ	359	Professional Kazakh for\nMedicine	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	400
KAZ	366	Kazakh Language for\nEngineers	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	401
KAZ	368	Onomastics: History and\nFunction of Names	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	402
KAZ	372	Language and ethnicity	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	404
KAZ	373	Kazakh Terminology	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	405
KAZ	374	Kazakh Diplomacy	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	34
KAZ	376	Language and Culture	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	406
KAZ	377	Intercultural\nCommunication through\nFilm	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	407
KAZ	379	Kazakh Cinema	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	409
KAZ	411	Shoqan Studies: A\nDecolonialist Discourse	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	410
KAZ	412	Scientific Discourse of\nAlash	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	411
KFL	102	Elementary Kazakh as a\nForeign Language II	KFL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	412
KOR	102	Beginning Korean II	KOR	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	413
KOR	202	Intermediate Korean II	KOR	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	414
LING	111	Linguistics for non-majors	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	415
LING	140	Language Variation and\nChange: the Story of\nEnglish	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	416
LING	271	Introduction to Cognitive\nLinguistics	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	417
LING	273	Survey of Research\nMethods in Linguistics	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	418
LING	374	Language Contact in\nCentral Asia	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	421
LING	375	The Art and Science of\nAnalyzing Languages:\nMorphosyntax of the\nWorld's Languages	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	422
LING	377	Historical Linguistics	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	423
LING	461	Experimental semantics	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	424
LING	473	Advanced Empirical\nMethods in Linguistics	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	425
LING	482	Language and Worldview	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	426
LING	491	Advanced Independent\nStudy	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	427
LING	574	Language Contact in\nCentral Asia	LING	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	428
LING	773	Advanced Empirical\nMethods in Linguistics	LING	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	429
HST	100	History of\nKazakhstan	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	6
KAZ	201	Academic Kazakh\nI	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	390
KAZ	202	Academic Kazakh\nII	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	391
LING	782	Language and Worldview	LING	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	430
MAE	205	Material and\nManufacturing I	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	431
MAE	206	Engineering Dynamics I	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	432
MAE	302	Machine Elements Design	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	433
MAE	305	Fluid Mechanics II	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	434
MAE	306	Computer Aided\nEngineering	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	435
MAE	350	Structural Mechanics II	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	436
MAE	351	Vehicle Propulsion Systems	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	437
MAE	454	Aerodynamics	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	438
MAE	457	Feasibility Analysis of\nClean Energy Technologies	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	439
MAE	463	Micro-Electro-Mechanical\nSystems and Microsystems\ntechnology	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	440
MAE	464	Mechanics of Soft\nMaterials	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	441
MAE	465	Introduction to\nMaintenance Engineering	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	442
MAE	469	Fundamentals of Space\nFlight Dynamics	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	443
MATH	109	Mathematical Discovery	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	444
MATH	161	Calculus I	MATH	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1
MATH	162	Calculus II	MATH	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	5
MATH	251	Discrete Mathematics	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	10
MATH	263	Calculus III	MATH	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	26
MATH	273	Linear Algebra with\nApplications	MATH	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	11
MATH	275	Mathematics for Artificial\nIntelligence	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	446
MATH	302	Abstract Algebra I	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	447
MATH	321	Probability	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	18
MATH	322	Mathematical Statistics	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	28
MATH	350	Research Methods	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	449
MATH	351	Numerical Methods with\nApplications	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	450
MATH	361	Real Analysis I	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	451
MATH	407	Graph Theory	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	452
MATH	411	Linear Programming	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	453
MATH	412	Nonlinear Optimization	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	454
MATH	423	Actuarial Mathematics II	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	455
MATH	440	Regression Analysis	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	456
MATH	455	Stochastic Calculus	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	457
MATH	456	Introduction to Lie Groups\nand Representations	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	458
MATH	461	Real Analysis II	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	459
MATH	462	Advanced Linear Algebra	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	25
MATH	465	Introduction to Differential\nGeometry	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	460
MATH	466	Nonlinear Continuum\nMechanics	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	461
MATH	482	Fourier Analysis	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	462
MATH	490	Special Topics in\nMathematics I	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	463
MATH	491	Special Topics in\nMathematics II	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	464
MATH	492	Special Topics in\nMathematics III	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	465
MATH	497	Directed Study in\nMathematics I	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	466
MATH	498	Directed Study in\nMathematics II	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	467
MATH	499	Capstone Project	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	468
MATH	541	Data Analysis and\nStatistical Learning	MATH	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	469
MATH	676	Advanced Partial\nDifferential Equations with\nApplications	MATH	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	470
MATH	682	Applied Functional Analysis	MATH	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	471
MATH	691	Thesis Proposal	MATH	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	472
MATH	692	Thesis	MATH	30	\N	\N	SSH	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	473
MATH	700	Thesis Research	MATH	0	\N	\N	SSH	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	474
MATH	702	Functional Analysis with\nApplications	MATH	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	475
MATH	722	Advanced Partial\nDifferential Equations	MATH	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	476
MATH	761	Mathematical Finance	MATH	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	477
MATH	791	Topics in Mathematics	MATH	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	478
MBA	03	Financial Accounting	MBA	4	\N	\N	GSB	GrM	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	479
MBA	05	Principles of Finance	MBA	6	\N	\N	GSB	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	480
MBA	07	Management and\nOrganizations	MBA	6	\N	\N	GSB	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	481
MBA	08	Marketing	MBA	6	\N	\N	GSB	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	482
MBA	09	Entrepreneurship	MBA	6	\N	\N	GSB	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	483
MBA	10	Foundations of Strategy	MBA	6	\N	\N	GSB	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	484
MBME	600	Research Seminar	MBME	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	485
MBME	602	Master Thesis II	MBME	24	\N	\N	SEDS	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	486
MBME	607	Advanced Tissue\nEngineering	MBME	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	487
MBME	700	Strategies for Controlled\nTopical Delivery of Drugs	MBME	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	488
MBME	708	Biomedical Imaging	MBME	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	489
MCEE	600	Research Seminar	MCEE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	490
MCEE	602	MSc Thesis II	MCEE	24	\N	\N	SEDS	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	491
MCEE	700	Structural Dynamics and\nEarthquake Engineering	MCEE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	492
MCEE	707	Geotechnical Earthquake\nEngineering	MCEE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	493
MCEE	714	Advanced Wastewater\nTreatment	MCEE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	494
MCEE	715	Sustainable Construction\nand Development	MCEE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	495
MCHME	600	Research Seminar	MCHME	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	496
MCHME	602	MSc Thesis II	MCHME	24	\N	\N	SEDS	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	497
MCHME	606	Advanced Heat and Mass\nTransfer	MCHME	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	498
MCHME	701	Advanced Chemical\nThermodynamics	MCHME	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	499
MCHME	707	Polymer Melt Fluid\nMechanics and Processing	MCHME	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	500
MECE	600	Research Seminar	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	501
MECE	602	Master Thesis II	MECE	24	\N	\N	SEDS	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	502
MECE	608	Energy Systems Operations\nand Planning	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	503
MECE	704	Fundamentals of Signal\nProcessing	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	504
MECE	707	Advanced Electronic\nCircuits	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	505
MECE	716	Adaptive Signal Processing	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	506
MECE	717	Pattern Recognition and\nMachine Learning	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	507
MECE	729	Convex Optimization	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	508
MECE	730	Microfluidic Devices	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	509
MECE	732	Optical Communications	MECE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	510
MINE	201	Mineral Processing	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	511
MINE	303	Mine Services and\nMaterials Handling	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	512
MINE	304	Resource Estimation	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	513
MINE	305	Rock Breakage	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	514
MINE	306	Underground Mining\nSystems and Design	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	515
MINE	307	Surface Mining System and\nDesign	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	516
MINE	404	Health, Safety and\nSustainability in Mining	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	518
MINE	490	Mine Design Project II	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	519
MINE	505	Advanced Mine Ventilation	MINE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	520
MINE	507	Rock Excavation Methods	MINE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	521
MINE	508	Advanced Rock Mechanics	MINE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	522
MINE	509	Advanced Surface Mine\nDesign	MINE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	523
MINE	510	Advanced Underground\nMine Design	MINE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	524
MINE	601	Mine Management and\nSustainability	MINE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	525
MINE	691	Thesis II	MINE	30	\N	\N	SMG	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	526
MINE	702	Current Research\nLiterature	MINE	8	\N	\N	SMG	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	527
MINE	703	Advanced Mining Systems	MINE	8	\N	\N	SMG	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	528
MINE	803	Advanced Geometallurgy	MINE	8	\N	\N	SMG	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	529
MINE	403	Coal Mining	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	517
MMAE	602	Master Thesis II	MMAE	24	\N	\N	SEDS	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	531
MMAE	604	Advanced Computational\nFluid Dynamics and Heat\nTransfer in Mechanical\nEngineering	MMAE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	532
MMAE	606	Research Methods	MMAE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	533
MMAE	700	Advanced Statistics and\nProbability	MMAE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	534
MMAE	701	Numerical Techniques for\nEngineers	MMAE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	535
MMAE	714	Space Flight Dynamics	MMAE	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	536
MMMM	690	Master Research Project	MMMM	30	\N	\N	SoM	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	537
MPA	610	Program Evaluation	MPA	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	538
MPA	699	Master’s Project with\nOverseas Component	MPA	12	\N	\N	GSPP	GrM	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	539
MPA	699A	Master’s Project with\nOverseas Component	MPA	0	\N	\N	GSPP	GrM	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	540
MPE	611	Benefit Cost Analysis	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	541
MPE	616	Designing and Managing\nPublic Private\nCollaboration	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	542
MPE	632	Artificial Intelligence and\nGovernance	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	543
MPE	633	Big Data Applications in\nPublic Policy	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	544
MPE	634	Foreign Policy Analysis	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	545
MPE	635	Innovation Management	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	546
MPE	636	Social Entrepreneurship	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	547
MPE	637	Policy Lab	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	548
MPE	639	International Financial\nPolicy	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	549
MPE	649	Public Sector Innovation	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	550
MPE	651	Agricultural Policy Analysis	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	551
MPE	670	Behavioural Insights and\nPublic Policy	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	552
MPE	673	Development Assistance\nand Governance	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	553
MPE	682	Sustainable Development\nand Environmental\nGovernance	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	554
MPE	685	Water Resources Policy and\nManagement	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	555
MPE	688	New Technologies and\nPublic Policy	MPE	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	556
MPP	602	Macroeconomics and\nPublic Policy	MPP	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	557
MPP	603	Data Analytics in Public\nPolicy	MPP	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	558
MPP	641	Public Management and\nLeadership	MPP	8	\N	\N	GSPP	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	559
MPP	699	Policy Analysis Exercise\nwith Overseas Component	MPP	16	\N	\N	GSPP	GrM	8	\N	\N	\N	\N	\N	\N	\N	\N	\N	560
MPP	699A	Policy Analysis Exercise\nwith Overseas Component	MPP	0	\N	\N	GSPP	GrM	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	561
MPTX	701	Research Project and\nThesis	MPTX	30	\N	\N	SoM	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	562
MSBM	506	Metabolism in Health and\nDisease	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	563
MSBM	507	Research Methods in\nMolecular Biomedicine	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	564
MSBM	509	Musculoskeletal System	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	565
MSBM	510	Exercise and Biomechanics	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	566
POL	101	Beginning Polish	POL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1045
MSBM	512	Principles of Pharmacology\nand Toxicology	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	567
MSBM	513	Drug Discovery	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	568
MSBM	514	Molecular Basis of\nInfection	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	569
MSBM	515	Molecular Basis of\nNeurological Disorders	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	570
MSBM	516	Molecular Immunology	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	571
MSBM	603	Advances in Sports\nMedicine and\nRehabilitation	MSBM	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	572
MSC	600	Research Methods and\nEthics	MSC	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	573
MSC	601	Technical Communication	MSC	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	574
MSF	01	Financial Modeling	MSF	5	\N	\N	GSB	GrM	2.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	575
MSF	06	Banking and Credit	MSF	5	\N	\N	GSB	GrM	2.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	576
MSF	11	FinTech	MSF	5	\N	\N	GSB	GrM	2.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	577
MSF	513A	Industry Insights Initiative	MSF	0	\N	\N	GSB	GrM	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	578
MSMR	602	Advances in Sports and\nRehabilitation	MSMR	8	\N	\N	SoM	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	579
MSMR	702	Master Research Project\nThesis	MSMR	29	\N	\N	SoM	GrM	14.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	580
MSN	506	Nursing Research,\nEvidence-Based Practice,\nand Quality Improvement	MSN	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	581
MSN	507	Advanced Pathophysiology	MSN	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	582
MSN	508	Advanced Pharmacology	MSN	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	583
MSN	509	Learning and Teaching\nStrategies and Innovation\nin Nursing	MSN	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	584
MSN	510	Population-Based Health\nPromotion and Clinical\nPrevention	MSN	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	585
NUR	121	Introduction to Basic\nStatistics for Evidence-\nBased Practice	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	586
NUR	301	Nutrition for Clinical\nPractice	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	587
NUR	305	Research Methods for\nNursing	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	588
NUR	306	Medical-Surgical Nursing:\nComplex Medical\nManagement for Acute and\nChronic Patient	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	589
NUR	307	Health Promotion and\nDisease Prevention in\nCulturally Diverse\nPopulations	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	590
NUR	313C	Medical-Surgical Nursing\nII: Complex Surgical\nManagement and Clinical	NUR	14	\N	\N	SoM	UG	7	\N	\N	\N	\N	\N	\N	\N	\N	\N	591
NUR	314C	Psychiatric Nursing and\nClinical	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	592
NUR	321	Ethics in Healthcare	NUR	4	\N	\N	SoM	UG	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	593
NUR	402	Principles of Healthcare\nAdministration	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	594
NUR	405	Issues and Trends in\nNursing	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	595
NUR	407	Capstone: Clinical and EBP\nQuality Improvement\nResearch	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	597
NUR	415C	Clinical Transitions	NUR	18	\N	\N	SoM	UG	9	\N	\N	\N	\N	\N	\N	\N	\N	\N	598
NUR	422	Capstone II: Evidence-\nBased Quality\nImprovement/Research\nProject Completion	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	599
NUSM	103	Biology for Medical\nstudents II with Lab	NUSM	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	600
NUSM	310	Capstone Project	NUSM	30	\N	\N	SoM	UG	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	601
NUSM	404	Cellular and Pathological\nBasis of Disease	NUSM	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	602
NUSM	406	Immunology in Health and\nDisease	NUSM	9	\N	\N	SoM	UG	4.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	603
NUSM	407	Medical Microbiology	NUSM	9	\N	\N	SoM	UG	4.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	604
NUSM	411B	Basics of Physical\nExamination	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	605
NUSM	415	Behavioral Medicine	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	606
NUSM	416	Evidence-based Medicine II\nand Biostatistics	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	607
NUSM	417	Clinical Experiences	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	608
OM	201	Operations Management	OM	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	609
PER	101	Beginning Persian I	PER	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	610
PER	102	Beginning Persian II	PER	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	611
PETE	202	Transport Phenomena	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	612
PETE	203	Drilling Engineering with\nLaboratories	PETE	8	\N	\N	SMG	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	613
PETE	204	Reservoir Rock and Fluid\nProperties with Lab	PETE	8	\N	\N	SMG	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	614
PETE	305	Well Test Analysis	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	615
PETE	306	Reservoir Engineering II	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	616
PETE	307	Production Engineering	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	617
PETE	311	Reservoir Simulation	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	618
PETE	404	Petroleum Geomechanics	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	619
PETE	407	Capstone Design Project II	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	620
PETE	506	Advanced Reservoir\nSimulation	PETE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	621
PETE	507	Advanced Reservoir\nEngineering	PETE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	622
PETE	508	Advanced Production\nEngineering	PETE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	623
PETE	606	Advanced Enhanced Oil\nRecovery	PETE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	624
PETE	613	Unconventional resources\ndrilling	PETE	6	\N	\N	SMG	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	625
PETE	620	Thesis II	PETE	24	\N	\N	SMG	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	626
PETE	701	Advanced Well Engineering	PETE	8	\N	\N	SMG	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	627
PETE	702	Current Research\nLiterature	PETE	8	\N	\N	SMG	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	628
PETE	703	Advanced Reservoir\nEngineering	PETE	8	\N	\N	SMG	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	629
PETE	801	Advanced Reservoir\nSimulation	PETE	8	\N	\N	SMG	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	630
PETE	803	Advanced Enhanced Oil\nRecovery	PETE	8	\N	\N	SMG	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	631
NUR	406	Medical-Surgical\nNursing: Complex\nSurgical Management	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	596
PHDBS	702B	Molecular basis of health\nand disease	PHDBS	8	\N	\N	SoM	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	634
PHDBS	703B	Biomedical Research\nAnalysis and Design of\nExperimentation	PHDBS	8	\N	\N	SoM	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	635
PETE	890	Thesis Research	PETE	0	\N	\N	SMG	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	632
PHDBS	706B	Advanced Biomedical\nResearch Analysis and\nDesign of Experimentation	PHDBS	8	\N	\N	SoM	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	637
PHDBS	707B	Publication Analysis	PHDBS	8	\N	\N	SoM	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	638
PHDBS	712	Molecular Immunology	PHDBS	4	\N	\N	SoM	PhD	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	639
PLS	210	Political Science\nResearch Methods	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	675
PHYS	161	Physics I for\nScientists and\nEngineers with\nLaboratory	PHYS	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	2
PHDGH	705	Global Health into Action	PHDGH	6	\N	\N	SoM	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	642
PHDGH	706	Methods in Global Health\nResearch	PHDGH	6	\N	\N	SoM	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	643
PHDGH	707	Implementation Science in\nGlobal Health	PHDGH	6	\N	\N	SoM	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	644
PHDGH	709	Critical Appraisal in Global\nHealth	PHDGH	6	\N	\N	SoM	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	645
PHIL	207	Introduction to Islamic\nPhilosophy and Theology	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	646
PHIL	210	Ethics	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	22
PHIL	240	Formal Logic	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	647
PHIL	350	History of 19th and 20th\nCentury Philosophy	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	648
PHIL	399	Special Topics in\nPhilosophy	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	649
PHIL	575	Philosophy of Art	PHIL	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	650
PHYS	202	Introductory Astrophysics	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	651
PHYS	222	Classical Mechanics II	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	652
PHYS	270	Introduction to Scientific\nComputing and Data\nAnalysis	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	653
PHYS	280	Thermodynamics and\nStatistical Physics	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	654
PHYS	362	Classical Electrodynamics\nII	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	655
PHYS	370	Optics with Laboratory	PHYS	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	656
PHYS	451	Quantum Mechanics I	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	657
PHYS	462	Field Theories in Physics	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	658
PHYS	491	Directed Study of Advanced\nPhysics Topics	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	659
PHYS	499	Honors Thesis	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	660
PHYS	510	Quantum Mechanics	PHYS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	661
PHYS	511	Scientific Computing and\nData Analysis	PHYS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	662
PHYS	520	Statistical Physics	PHYS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	663
PHYS	562	Field Theories	PHYS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	664
PHYS	590	Directed Study of Advanced\nTopics in Modern Physics	PHYS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	665
PHYS	692	Thesis	PHYS	38	\N	\N	SSH	GrM	19	\N	\N	\N	\N	\N	\N	\N	\N	\N	666
PHYS	700	Thesis Research	PHYS	0	\N	\N	SSH	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	667
PHYS	701	Current Research\nLiterature	PHYS	6	\N	\N	SSH	PhD	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	668
PHYS	710	Quantum Mechanics	PHYS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	669
PHYS	711	Scientific Computing and\nData Analysis	PHYS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	670
PHYS	720	Statistical Physics	PHYS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	671
PHYS	790	Directed Study of Advanced\nModern Physics Topics	PHYS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	672
PLS	101	Introduction to Political\nScience	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	673
PLS	140	Introduction to\nComparative Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	16
PLS	150	Introduction to\nInternational Relations	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	674
PLS	315	Political Game Theory	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	677
PLS	327	Contemporary Political\nTheory	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	678
PLS	345	Revolutions, Social\nMovements, and\nContentious Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	679
PLS	351	International Political\nEconomy	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	680
PLS	355	European Union:\nInstitutions and Policies	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	681
PLS	361	Memory Politics in East\nAsia	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	682
PLS	363	Visual Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	683
PLS	391	Intermediate Special Topics\nin Comparative Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	684
PLS	392	Politics of China	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	685
PLS	393	Modern Korean Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	686
PLS	435	Political Polarization in\nDemocracies	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	688
PLS	441	Advanced Topics in\nComparative Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	689
PLS	445	Political Violence	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	690
PLS	457	International Security and\nConflict	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	692
PLS	469	International Relations of\nEurasia	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	693
PLS	511	Advanced Research I	PLS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	695
PLS	535	Political Polarization in\nDemocracies	PLS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	696
PLS	540	Core Seminar in\nComparative Politics	PLS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	697
PLS	541	Advanced Topics in\nComparative Politics	PLS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	698
PLS	545	Political Violence	PLS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	699
PLS	557	International Security and\nConflict	PLS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	700
PHYS	162	Physics II for\nScientists and\nEngineers with\nLaboratory	PHYS	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	8
PHDBS	704	NUSOM seminar	PHDBS	0	\N	\N	SoM	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	636
PLS	211	Quantitative\nMethods	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	676
PHDGH	701	Thesis Research	PHDGH	0	\N	\N	SoM	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	640
PLS	395	Independent\nStudy	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	687
PLS	569	International Relations of\nEurasia	PLS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	701
PLS	581	Independent Study in\nPolitical Science	PLS	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	702
PLS	596	Thesis Preparation	PLS	4	\N	\N	SSH	GrM	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	703
PLS	599	MA Thesis II	PLS	20	\N	\N	SSH	GrM	10	\N	\N	\N	\N	\N	\N	\N	\N	\N	704
PLS	757	International Security and\nConflict	PLS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	705
POL	102	Beginning Polish II	POL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	706
POL	201	Intermediate Polish I	POL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	707
PUBH	512	Biostatistical Modeling and\nSampling	PUBH	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	708
PUBH	522	Advanced Analytical\nEpidemiology	PUBH	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	709
PUBH	551	Health Services\nManagement, Health\nEconomic and Health\nPolicy	PUBH	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	710
PUBH	631	Social and Behavioral\nSciences in Public Health	PUBH	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	711
PUBH	641	Problem Investigations in\nEnvironmental Health	PUBH	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	712
PUBH	651	Risk Management in Health\nCare	PUBH	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	713
PUBH	682	Master’s Project\nImplementation	PUBH	24	\N	\N	SoM	GrM	12	\N	\N	\N	\N	\N	\N	\N	\N	\N	714
PUBH	698	Public Health Management	PUBH	6	\N	\N	SoM	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	715
REL	435	The Archaeology of Ritual	REL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	716
REL	535	The Archaeology of Ritual	REL	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	717
RFL	305	Academic Writing in\nRussian	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	719
RFL	312	Soviet Female Writers and\nPoets	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	720
RFL	356	Kazakh Music History	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	721
RFL	469	International relations of\nEurasia	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	722
ROBT	202	System Dynamics and\nModeling	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	723
ROBT	204	Electrical and Electronic\nCircuits II with Lab	ROBT	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	724
ROBT	206	Microcontrollers with Lab	ROBT	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	17
ROBT	304	Electromechanical Systems\nwith lab	ROBT	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	725
ROBT	308	Industrial Automation	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	726
ROBT	312	Robotics I: Kinematics and\nDynamics	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	727
ROBT	391	Research methods	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	728
ROBT	402	Robotic/Mechatronic\nSystem Design	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	729
ROBT	492	Capstone Project II	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	730
ROBT	502	Robot Perception & Vision	ROBT	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	731
ROBT	692	Thesis	ROBT	30	\N	\N	SEDS	GrM	15	\N	\N	\N	\N	\N	\N	\N	\N	\N	732
RFL	303	Intensive Advanced\nRussian	RFL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	718
ROBT	702	Advanced Robot Perception\nand Vision	ROBT	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	734
ROBT	722	Current Research\nLiterature	ROBT	8	\N	\N	SEDS	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	735
SEDS	502	Teaching Practicum	SEDS	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	736
SEDS	505	Teaching and Laboratory\nPracticum I	SEDS	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	737
SEDS	506	Teaching and Laboratory\nPracticum II	SEDS	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	738
SEDS	592	Research Seminar	SEDS	6	\N	\N	SEDS	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	739
SMG	400	Engineering Economics	SMG	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	740
SOC	101	Introduction to Sociology	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	741
SOC	201	Social Science Research\nMethods	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	742
SOC	203	Quantitative Methods in\nSociology	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	743
SOC	210	Gender and Society	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	744
SOC	215	Sociology of Race and\nEthnicity	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	745
SOC	220	Science, Technology, and\nSociety	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	746
SOC	301	Classical Sociological\nTheory	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	747
SOC	310	Social Inequality	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	748
SOC	313	Social Foundations of\nEducation	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	749
SOC	320	Organized Crime and\nCorruption	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	750
SOC	410	Violence Against Women:\nAn Intersectional Approach	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	754
SOC	416	Sociology of Punishment	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	755
SOC	425	Modern Sociological\nTheory	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	756
SOC	499	Capstone Seminar II	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	757
SOC	510	Social Inequality	SOC	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	758
SOC	710	Social Inequality	SOC	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	759
SPA	102	Beginning Spanish II	SPA	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	760
SPA	202	Intermediate Spanish II	SPA	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	761
SPA	311	Colloquial Spanish	SPA	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	762
STUMOB	001	Student Mobility Course	STUMOB	0	\N	\N	Other	ND	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	765
TUR	100	Languages, Cultures, and\nCommunities of the Turkic\nWorld	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	766
TUR	180	Introduction to Turkic\nlanguages	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	767
TUR	231	Istanbul in Literature and\nCulture	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	768
TUR	235	Turkish Poetry in\nTranslation	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	769
TUR	305	Introduction to Chagatay\nand Ottoman Turkish	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	771
SOC	400	Research\nAssistance in\nSociology	SOC	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	751
SOC	401	Research\nAssistance in\nSociology	SOC	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	752
TUR	575	Advanced Topics in Turkic\nStudies	TUR	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	772
WCS	135	Introduction to Visual\nCommunication	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	773
WCS	200	Introduction to Public\nSpeaking	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	774
WCS	204	Gender and\nCommunication	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	775
WCS	205	Intercultural\nCommunication	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	776
WCS	220	Science Writing	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	777
WCS	240	Writing for Digital Media	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	779
WCS	250	Advanced Rhetoric and\nComposition	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	780
WCS	304	Multimodal Communication\nInternship I	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	784
WCS	394	Internship: Undergraduate\nWriting Tutor II	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	788
WCS	501	Science Communication	WCS	6	\N	\N	SSH	GrM	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	789
WCS	730	From Genre to Style and\nBack: Writing for PhD\nStudents	WCS	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	790
WLL	110	Introduction to Literary\nStudies	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	791
WLL	211	World Literature II: from\nthe 18th to the 20th\ncentury	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	792
WLL	235	Creative Writing:\nIntroduction to Fiction\nWriting I	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	793
WLL	241	Survey of Folk Tales	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	794
WLL	248	Survey of Soviet Literature\nand Culture	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	795
WLL	313	Dante's Inferno	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	796
WLL	341	Soviet Literature as\nMultinational Literature	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	797
WLL	375	Philosophy of Art	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	798
WLL	451	The Call of the Evil:\nUnmasking the\nVillain(ness) in Popular\nCulture and Literature	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	801
WLL	462	Creative Nonfiction	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	802
WLL	499	Languages, Linguistics, and\nLiteratures Capstone II	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	803
WLL	551	The Call of the Evil:\nUnmasking the\nVillain(ness) in Popular\nCulture and Literature	WLL	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	804
WLL	562	Creative Nonfiction	WLL	8	\N	\N	SSH	GrM	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	805
WLL	751	The Call of the Evil:\nUnmasking the\nVillain(ness) in Popular\nCulture and Literature	WLL	8	\N	\N	SSH	PhD	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	806
DELCE	700	Thesis Research	DELCE	0	\N	\N	SEDS	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	203
DENG	700	Thesis Research	DENG	0	\N	\N	SEDS	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	209
DMAE	700	Thesis Research	DMAE	0	\N	\N	SEDS	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	212
MINE	890	Thesis Research	MINE	0	\N	\N	SMG	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	530
PHDBS	701	Thesis Research	PHDBS	0	\N	\N	SoM	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	633
PHDGH	704	NUSOM Seminar in Global\nHealth	PHDGH	0	\N	\N	SoM	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	641
ROBT	700	Thesis Research	ROBT	0	\N	\N	SEDS	PhD	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	733
ANT	160	Introduction to Biological\nAnthropology	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	807
ANT	240	Laboratory Methods in\nArchaeology	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	808
ANT	285	Food and Society	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	809
ANT	333	Anthropology of Space	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	810
ANT	475	Digital Ethnographies	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	812
ANT	482	Climate Change, Future\nEnergy and Sustainability	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	813
ANT	498	Capstone Seminar I	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	814
BBA	208	Data Analytics for\nBusiness	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	815
BBA	210	Fundamentals of\nMarketing	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	816
BBA	230	Entrepreneurship	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	817
BBA	399	Internship	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	818
BIOL	105	General Biology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	819
BIOL	120L	Modern Biology II\nLaboratory	BIOL	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	820
BIOL	320	Developmental Biology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	821
BIOL	340	Introduction to\nBioinformatics with Lab	BIOL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	822
BIOL	363	Structural Bioinformatics	BIOL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	823
BIOL	380	Biology of Behavior	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	824
BIOL	385	Cell signaling: principles\nand mechanisms	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	825
BIOL	452	Biology of Cancer	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	826
BIOL	456	Biology Research Design	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	827
BIOL	460	Human Parasitology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	828
BIOL	470	Advanced Cell Biology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	829
BIOL	490	Honors Thesis Research	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	830
CEE	200	Structural Mechanics I	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	831
CEE	201	Environmental Chemistry	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	832
CEE	204	Civil Engineering CAD\nand Surveying	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	833
ANT	401	Research\nAssistance in\nAnthropology	ANT	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	811
WCS	150	Rhetoric and\nComposition	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	4
WCS	305	Multimodal\nCommunication\nInternship II	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	785
WLL	399	Independent\nStudy	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	799
WLL	400	Research\nAssistance in\nLinguistics and\nLiterature	WLL	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	800
CEE	300	Structural Design –\nConcrete	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	834
CEE	302	Geotechnical Engineering	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	835
CEE	304	Fluid Mechanics	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	836
CEE	306	Civil Engineering\nMaterials	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	837
CEE	401	Construction Technology\nand Management	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	838
CEE	450	Behavior and Design of\nStructural System	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	839
CEE	460	Water Supply and\nDistribution Management	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	840
CEE	462	Pavement Design and\nPerformance	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	841
CEE	463	Individual Research\nProject in Civil &\nEnvironmental\nEngineering 1	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	109
CEE	467	Building Information\nModelling for\nGeotechnical Engineering	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	842
CHEM	104	Introduction to Physical\nand Chemical Sciences	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	843
CHEM	220	Quantitative Chemical\nAnalysis	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	844
CHEM	220L	Quantitative Chemical\nAnalysis Lab	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	845
CHEM	331	Physical Chemistry I	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	846
CHEM	331L	Physical Chemistry Lab	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	847
CHEM	341	Biochemistry I	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	848
CHEM	350	Advanced Inorganic\nChemistry	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	849
CHEM	350L	Advanced Inorganic\nChemistry Laboratory	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	850
CHEM	410	Structural Spectroscopy	CHEM	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	851
CHEM	432	Introduction to\nCheminformatics and\nComputer aided drug\ndesign	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	852
CHEM	440	Pharmaceutical and\nMedicinal Chemistry	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	853
CHEM	471	Environmental Chemistry	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	854
CHEM	488	Directed Research I	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	855
CHME	200	Basic Principles and\nCalculations in Chemical\nEngineering	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	856
CHME	201	Chemical Engineering\nThermodynamics	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	857
CHME	222	Inorganic and Analytical\nChemistry	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	858
CHME	300	Heat and Mass Transfer	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	859
CHME	301	Applied Mathematics for\nProcess Design	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	860
CHME	302	Instrumental Methods of\nAnalysis for Engineers	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	861
CHME	351	Environment and\nDevelopment	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	862
CHME	353	Electrochemical\nEngineering	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	863
CHME	354	Introduction to\nMetallurgy	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	864
CHME	400	Process Design and\nSimulation	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	865
CHME	401	Chemical Engineering\nLab II	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	866
CHME	453	Multiphase Systems	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	867
CHN	101	Beginning Mandarin I	CHN	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	868
CHN	202	Intermediate Mandarin II	CHN	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	869
CSCI	344	Data Mining and Decision\nSupport	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	870
CSCI	355	Compiler Construction	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	871
CSCI	364	Software Architecture\nand Design	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	872
CSCI	423	Introduction to Parallel\nSystems and GPU\nProgramming	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	873
CSCI	434	Information Security	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	874
CSCI	471	Complexity and\nComputability	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	875
CSCI	494	Deep Learning	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	876
ECON	302	Game Theory and\nEconomic Analysis	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	877
ECON	305	Advanced\nMicroeconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	878
ECON	325	International Trade	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	879
ECON	326	The Economics of\nFinancial Markets	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	880
ECON	333	Political Economy	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	881
ECON	399	Independent Study in\nEconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	882
ECON	403	Introduction to Contract\nTheory and Auctions	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	883
ECON	414	Advanced Monetary\nPolicy	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	884
ECON	418	Corporate Finance and\nGovernance	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	885
ECON	433	Econometrics II Panel\nData	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	886
ECON	449	Quantitative\nMacroeconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	887
ELCE	200	Circuits Theory I	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	888
ELCE	203L	Signals and Systems\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	890
ELCE	204	Solid State Devices	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	891
ELCE	204L	Solid State Devices\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	892
ELCE	205	Discrete Mathematics	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	893
ELCE	301L	Electronic Circuits\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	895
ELCE	304	Computer Networks	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	896
ELCE	304L	Computer Networks\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	897
ELCE	306	Linear Control Theory	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	898
ELCE	307	Digital Signal Processing	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	899
ELCE	307L	Digital Signal Processing\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	900
ELCE	354	Power Electronics	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	901
ELCE	355	Power Systems\nProtection	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	902
ELCE	455	Machine Learning with\nPython	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	903
ELCE	462	Wireless Networks	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	904
ELCE	463	Network Science:\nMethods and Applications	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	905
ELCE	466	RF and Microwave\nCircuits	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	906
ENG	100	Introduction to\nEngineering	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	907
ENG	101	Programming for\nEngineers	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	333
ENG	200	Engineering Mathematics\nIII (Differential Equations\nand Linear Algebra)	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	908
GEOL	201	Mineralogy	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	909
GEOL	202	Geologic Maps and Cross-\nSections	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	910
GEOL	203	Sedimentary petrology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	911
GEOL	207	Geomorphology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	912
GEOL	302	Thermodynamics and\nGeochemistry	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	913
GEOL	303	Structural Geology and\nTectonics	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	914
GEOL	305	Geology of ore deposits	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	915
GEOL	310	Field Geology 2	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	916
GEOL	401	Petroleum Geology and\nGeochemistry	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	917
GEOL	402	Water Resource\nManagement	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	918
GEOL	404	Research Project I	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	919
GEOL	412	Advanced Hydrogeology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	920
GER	101	Beginning German	GER	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	921
GER	201	Intermediate German I	GER	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	922
HST	104	Central Asian History II\n(1700 - 1991)	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	923
HST	110	Introduction to World\nReligions	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	924
HST	121	World History I (to 1500)	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	925
HST	124	Introduction to the\nHistory of Medicine	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	371
HST	271	History of the Ottoman\nEmpire	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	926
HST	375	Inner Asian Frontiers of\nChina: A Cultural\nPerspective	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	927
HST	435	Stalinist Central Asia	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	929
HST	498	Directed Reading	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	930
KAZ	300	Kazakh Studies in the\nPost-Colonial Era	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	392
KAZ	363	Language and\nGlobalization	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	931
KAZ	410	Kazakh literature of the\nXV-XIX centuries	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	932
KFL	101	Elementary Kazakh as a\nForeign Language I	KFL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	933
KOR	201	Intermediate Korean I	KOR	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	936
LING	131	Introduction to\nLinguistics	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	937
LING	270	Languages of Eurasia	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	938
LING	277	Language Diversity and\nLanguage Universals	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	939
LING	350	Introduction to\nGenerative Syntax	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	940
LING	431	Statistics and\ncomputational methods in\nLinguistics	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	941
LING	479	Tense, Aspect, Modality\nand Evidentiality	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	942
MAE	201	Computer Aided Design	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	943
MAE	202	Environmental Science	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	944
MAE	300	Fluid Mechanics I	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	945
MAE	301	Engineering\nThermodynamics	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	946
MAE	303	Control Systems	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	947
MAE	307	Engineering Dynamics II	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	948
MAE	400	Heat Transfer	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	949
MAE	401	Mechanical Systems\nDesign	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	950
MAE	450	Additive Manufacturing	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	951
MAE	455	Flight Performance and\nMechanics	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	952
MAE	467	Heating, Ventilating and\nAir Conditioning	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	953
MAE	468	Introduction to Aerospace\nPropulsion.	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	954
MATH	274	Introduction to\nDifferential Equations	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	445
MATH	301	Introduction to Number\nTheory	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	955
MATH	310	Applied Statistical\nMethods	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	448
MATH	323	Actuarial Mathematics I	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	956
MATH	371	Introduction to\nMathematical Biology	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	957
MATH	417	Cryptography	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	958
MATH	424	Mathematical Finance	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	959
MATH	425	Stochastic Processes	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	960
MATH	446	Time Series Analysis	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	961
MATH	449	Statistical Programming	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	962
MATH	471	Nonlinear Differential\nEquations	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	963
MATH	477	Applied Finite Element\nMethods	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	964
MATH	480	Complex Analysis	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	965
MATH	481	Partial Differential\nEquations	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	966
MINE	301	Mine Surveying and\nGeographic Information\nSystems	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	967
MINE	302	Geomechanics	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	968
MINE	401	Mining Geotechnical\nEngineering	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	969
MINE	402	Mine Planning	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	970
MINE	405	Mine Ventilation	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	971
MINE	407	Mining and Environment	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	972
MINE	489	Mine Design Project I	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	973
NUR	205	Psychology for the Health\nPractitioner	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	974
HST	399	Independent\nStudy	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	928
NUR	221	Nursing Research:\nIntroduction to Critical\nAppraisal and Evidence-\nBased Practice	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	975
NUR	302	Physical Assessment\nAcross the Lifespan	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	976
NUR	303	Nursing Care of Older\nAdults	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	977
NUR	304	Introduction to Basic\nStatistics for Evidence\nBased Practice	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	978
NUR	308	Enhanced\nCommunication in\nProfessional Nursing	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	979
NUR	311C	Obstetric Nursing +\nClinical	NUR	10	\N	\N	SoM	UG	5	\N	\N	\N	\N	\N	\N	\N	\N	\N	980
NUR	312C	Pediatric Nursing +\nClinical: Care of Children\nand Families	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	981
NUR	401	Education: Principles and\nPractice for Teaching in\nNursing	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	982
NUR	403	Data Analytics for Quality\nImprovement in\nHealthcare	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	983
NUR	404	Community and Home\nHealth Nursing	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	984
NUR	411C	Community and Home\nHealth Nursing and\nClinical	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	985
NUR	412	Geriatric Nursing:\nNursing Care of the Older\nAdult	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	986
NUR	413C	Medical Surgical Nursing\n3 - Management of the\nComplex and Critically Ill\nPatient and Clinical	NUR	14	\N	\N	SoM	UG	7	\N	\N	\N	\N	\N	\N	\N	\N	\N	987
NUR	421	Capstone I: Developing a\nProject Proposal in\nNursing	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	988
NUSM	101	Introduction to Medicine	NUSM	4	\N	\N	SoM	UG	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	989
NUSM	102	Biology for Medical\nstudents I with Lab	NUSM	8	\N	\N	SoM	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	990
NUSM	301	Introduction to\nImmunology,\nMicrobiology and\nGenetics	NUSM	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	991
NUSM	302	Introduction to Statistics\nfor Evidence-Based\nPractice	NUSM	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	992
NUSM	303	Introduction to Anatomy\nand Histology	NUSM	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	993
NUSM	401	Introduction to Being a\nPhysician	NUSM	4	\N	\N	SoM	UG	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	994
NUSM	402	Medical Anatomy	NUSM	16	\N	\N	SoM	UG	8	\N	\N	\N	\N	\N	\N	\N	\N	\N	995
NUSM	403	Human Genetics	NUSM	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	996
NUSM	405	Fuel Metabolism	NUSM	6	\N	\N	SoM	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	997
NUSM	408	Pharmacology	NUSM	4	\N	\N	SoM	UG	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	998
NUSM	410	Basics of Medical\nInterviewing	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	999
NUSM	411A	Basics of Physical\nExamination	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	1000
NUSM	412	Evidence-based Medicine\nI and Biostatistics	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	1001
NUSM	413	English-Russian-Kazakh\nMedical Terminology	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	1002
NUSM	414	Medical Ethics and\nProfessionalism	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	1003
PETE	201	Fluid Mechanics and\nThermodynamics	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1004
PETE	301	Numerical Methods for\nPetroleum Engineers	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1005
PETE	302	Reservoir Engineering I\nwith Laboratory works	PETE	8	\N	\N	SMG	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1006
PETE	303	Well Logging and\nFormation Evaluation	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1007
PETE	304	Well Completion and\nStimulation	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1008
PETE	400	Capstone Design Project I	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1009
PETE	405	Enhanced Oil Recovery	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1010
PETE	409	Surface Facilities	PETE	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1011
PHIL	131	Introduction to\nContemporary Political\nPhilosophy	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1012
PHIL	160	Philosophy of Religion	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1013
PHIL	232	Philosophy of Law	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1014
PHIL	362	Philosophy of Mind	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1015
PHIL	383	Kant’s Critique of Pure\nReason	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1016
PHYS	201	Introductory Astronomy I	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1017
PHYS	221	Classical Mechanics I	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1018
PHYS	250	Introduction to Nuclear\nScience and Technology	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1019
PHYS	261	Modern Physics with\nlaboratory	PHYS	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1020
PHYS	315	Applied Mathematical\nMethods	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1021
PHYS	361	Classical Electrodynamics\nI	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1022
PHYS	395	Research Methods	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1023
PHYS	421	Parallel Computing	PHYS	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1024
PHYS	452	Quantum Mechanics II	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1025
PHYS	463	Astrophysics and General\nRelativity	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1026
PHYS	498	Honors Thesis Research	PHYS	0	\N	\N	SSH	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	1027
PLS	100	Introduction to the\nPolitics of Central Asia	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1028
PLS	330	Politics and Governance\nof Eurasia	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1030
PLS	338	U.S. Government and\nPolitics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1031
PLS	341	Politics of Development	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1032
PLS	352	International Relations\nTheory	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1033
PLS	354	Introduction to\nInternational Law	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1034
PLS	356	International Politics of\nthe Korean Peninsula	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1035
PLS	360	Foreign Policy Analysis	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1036
PLS	370	Law, Politics and Society	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1037
PLS	416	Experimental Political\nScience	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1038
PLS	424	Issues in the Philosophy\nof Social Science	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1039
PLS	426	Hannah Arendt on Power,\nViolence, and Revolution	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1040
PLS	431	Politics and Governance\nof the Russian Federation	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1041
PLS	432	Comparative\nDemocratization	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1042
PLS	460	Environmental Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1043
PLS	463	NGO Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1044
REL	212	Buddhist Religious\nTraditions	REL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1046
RFL	211	East in Soviet Russian-\nlanguage culture: origin\nand fate	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1047
RFL	213	Soviet Everyday Life\nthrough Cinema	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1048
ROBT	201	Mechanics: Statics and\nDynamics	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1049
ROBT	203	Electrical and Electronic\nCircuits I with Lab	ROBT	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1050
ROBT	205	Signals and Sensing with\nLab	ROBT	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1051
ROBT	301	Mechanical Design with\nCAD and Machining\nLaboratory	ROBT	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1052
ROBT	303	Linear Control Theory\nwith Lab	ROBT	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1053
ROBT	310	Image Processing	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1054
ROBT	403	Robotics II: Control,\nModeling and Learning\nwith Laboratory	ROBT	8	\N	\N	SEDS	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1055
ROBT	407	Machine Learning with\nApplications	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1056
ROBT	491	Capstone Project I	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1057
SMG	100	Introduction to Natural\nResources Extraction	SMG	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1058
SMG	200	Resource Economics	SMG	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1059
SMG	210	Strength of Materials	SMG	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1060
SOC	221	International Migration	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1061
SOC	223	Social Movements: How\nPeople Make Change	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1062
SOC	350	Digital Deviance	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1063
SOC	399	Special Topics in\nSociology	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1064
SOC	475	Sociology of Consumption	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1065
SOC	485	Statistics and Machine\nLearning for Social\nReform	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1066
SOC	498	Capstone Seminar Part I	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1067
SPA	101	Beginning Spanish I	SPA	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1068
SPA	201	Intermediate Spanish I	SPA	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1069
SPA	314	Advanced Spanish\nGrammar and\nComposition	SPA	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1070
TUR	230	Literatures of Central\nAsia	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1071
TUR	280	Introduction to Turkic\nHistorical and\nComparative Linguistics	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	770
TUR	451	The Turkish Novel	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1072
TUR	480	Selective reading of\nhistorical Turkic\nliterature	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1073
WCS	101	Communication and\nSociety	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1074
WCS	201	Introduction to\nJournalism	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1075
WCS	203	Interpersonal\nCommunication	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1076
WCS	210	Technical and\nProfessional Writing	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	13
WCS	230	Say What you Mean:\nClarity, Precision, and\nStyle in Academic Writing	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	778
WCS	270	Academic and\nProfessional\nPresentations	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	781
WCS	300	Internship:\nUndergraduate Speaker\nConsultant I	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	782
WCS	390	Writing Fellows I –\nComposition and\nCollaboration in Theory\nand Practice	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	786
WCS	393	Internship:\nUndergraduate Writing\nTutor I	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	787
WLL	171	Introduction to Linguistic\nAnthropology	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1077
WLL	201	World Literature I	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1078
WLL	209	Introduction to\nTranslation Studies	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1079
WLL	218	Renaissance in Italy and\nBeyond	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1080
WLL	244	Survey of Nineteenth-\nCentury Russian\nLiterature	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1081
WLL	333	Literary Modernism:\nTradition and Innovation	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1082
WLL	340	The image of the East in\nRussophone literature\nand culture: genesis and\nmeaning	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1083
WLL	360	Poetry Writing Seminar	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1084
WLL	377	Philosophy and Tragedy	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1085
WLL	385	Postcolonial Theory and\nits Applications in Eurasia	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1086
WLL	410	Literary Theory	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1087
WLL	465	Creative Writing:\nAutofiction	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1088
WLL	498	Languages, Linguistics,\nand Literatures Capstone\nI	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1089
ANT	314	Politics of Identity\nin Eurasia	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1090
ANT	403	Research\nAssistance in\nAnthropology	ANT	4	\N	\N	SSH	UG	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	1091
BIOL	392	Directed Study in\nBiology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1092
BIOL	399	Biology Internship\n- 2B	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1093
CHEM	100	Introduction to\nChemistry	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	32
CHEM	101	General\nChemistry I	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	113
CHEM	101L	General\nChemistry I lab	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	114
CHEM	102	General\nChemistry II	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	115
CHEM	105	Introduction to\nEnvironmental\nScience	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	116
CHEM	189C	Independent\nStudy	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1094
CHEM	211	Organic\nChemistry I	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	118
CHEM	211L	Organic\nChemistry I Lab	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	119
ECON	300	Research\nAssistance in\nEconomics	ECON	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	252
ELCE	203	Signals and\nSystems	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	889
ELCE	301	Electronic\nCircuits	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	894
GEOL	206	Field Geology 1	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1095
KAZ	150	Basic Kazakh	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1096
KAZ	371	Contemporary\nKazakh Literature	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	403
KAZ	378	Kazakh for Social\nScience	KAZ	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	408
KFL	201	Intermediate\nKazakh as a\nForeign Language\nI	KFL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	934
KFL	202	Intermediate\nKazakh as a\nForeign Language\nII	KFL	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	1097
KOR	101	Beginning Korean\nI	KOR	8	\N	\N	SSH	UG	4	\N	\N	\N	\N	\N	\N	\N	\N	\N	935
LING	240	Introduction to\nSociolinguistics	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1098
LING	278	Sounds of the\nWorld’s\nLanguages	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	419
LING	371	Practicum in\nTeaching Foreign\nLanguages	LING	4	\N	\N	SSH	UG	2	\N	\N	\N	\N	\N	\N	\N	\N	\N	420
MAE	353	Summer\nInternship	MAE	3	\N	\N	SEDS	UG	1.5	\N	\N	\N	\N	\N	\N	\N	\N	\N	1099
PHYS	299	Research project\nand internship	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1100
PHYS	399	Physics Research\nProject	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1101
PLS	120	Introduction to\nPolitical Theory	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1029
PLS	451	Advanced Topics\nin International\nRelations	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	691
PLS	495	Research\nPracticum in PSIR	PLS	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	694
ROBT	399	Internship	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	1102
SOC	402	Research\nAssistance in\nSociology	SOC	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	753
SSH	300	School of\nSciences and\nHumanities\nInternship	SSH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	763
SSH	301	School of\nSciences and\nHumanities\nInternship:\nSecond\nExperience	SSH	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	764
WCS	301	Internship:\nUndergraduate\nSpeaker\nConsultant II	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	\N	\N	\N	\N	\N	\N	783
\.


--
-- Data for Name: enrollments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.enrollments (user_id, course_id, term, year, grade, grade_points, status, created_at, updated_at) FROM stdin;
1	1	Fall	2022	B+	3.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	2	Fall	2022	B	3	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	3	Fall	2022	B+	3.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	4	Fall	2022	B-	2.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	5	Spring	2023	B+	3.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	6	Spring	2023	C+	2.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	7	Spring	2023	C+	2.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	8	Spring	2023	C+	2.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	9	Fall	2023	B-	2.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	10	Fall	2023	B+	3.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	11	Fall	2023	A	4	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	12	Fall	2023	C+	2.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	13	Fall	2023	B+	3.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	14	Spring	2024	B	3	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	15	Spring	2024	C	2	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	16	Spring	2024	B-	2.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	17	Spring	2024	B	3	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	18	Spring	2024	A-	3.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	19	Fall	2024	B-	2.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	20	Fall	2024	A-	3.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	21	Fall	2024	B-	2.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	22	Fall	2024	A-	3.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	23	Fall	2024	B-	2.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	24	Fall	2024	B+	3.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	25	Spring	2025	B+	3.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	26	Spring	2025	A-	3.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	27	Spring	2025	D+	1.33	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	28	Spring	2025	A	4	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	29	Spring	2025	C-	1.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	30	Summer	2025	P	0	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	31	Fall	2025	P	0	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	32	Fall	2025	B	3	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	33	Fall	2025	B-	2.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	34	Fall	2025	B-	2.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	35	Fall	2025	A-	3.67	PASSED	2026-04-17 11:27:15.112456+00	2026-04-17 11:27:15.112456+00
1	265	Spring	2026	\N	\N	IN_PROGRESS	2026-04-18 13:17:30.817686+00	2026-04-18 13:17:30.817686+00
1	924	Spring	2026	\N	\N	IN_PROGRESS	2026-04-18 13:18:40.6646+00	2026-04-18 13:18:40.6646+00
\.


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.events (user_id, category_id, title, description, start_at, end_at, is_all_day, location, recurrence, recurrence_end_at, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: study_material_library_entries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.study_material_library_entries (upload_id, course_id, curated_title, curated_week, curated_by_admin_id, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: study_material_uploads; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.study_material_uploads (course_id, uploader_id, user_week, original_filename, staged_path, storage_key, content_type, file_size_bytes, upload_status, curation_status, error_message, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (email, google_id, first_name, last_name, major, study_year, cgpa, total_credits_earned, total_credits_enrolled, avatar_url, is_onboarded, is_admin, id, created_at, updated_at) FROM stdin;
anuar.nyssanbayev@nu.edu.kz	111485480978212812125	Anuar	Nyssanbayev	Computer Science	4	2.96	230	230	https://lh3.googleusercontent.com/a/ACg8ocJWb5VThDLF_sWFAaA0dxsyx5_SKVK_h3ZbULr1I8UFaKRvsg=s96-c	t	t	1	2026-04-17 11:25:47.756906+00	2026-04-17 11:27:15.112456+00
\.


--
-- Name: assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.assessments_id_seq', 7, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_id_seq', 1, false);


--
-- Name: course_gpa_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_gpa_stats_id_seq', 1, false);


--
-- Name: course_offerings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_offerings_id_seq', 2582, true);


--
-- Name: course_reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.course_reviews_id_seq', 1, false);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.courses_id_seq', 1102, true);


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.events_id_seq', 1, false);


--
-- Name: study_material_library_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.study_material_library_entries_id_seq', 1, false);


--
-- Name: study_material_uploads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.study_material_uploads_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: assessments assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: course_gpa_stats course_gpa_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_gpa_stats
    ADD CONSTRAINT course_gpa_stats_pkey PRIMARY KEY (id);


--
-- Name: course_offerings course_offerings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_offerings
    ADD CONSTRAINT course_offerings_pkey PRIMARY KEY (id);


--
-- Name: course_reviews course_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: enrollments enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_pkey PRIMARY KEY (user_id, course_id, term, year);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: study_material_library_entries study_material_library_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT study_material_library_entries_pkey PRIMARY KEY (id);


--
-- Name: study_material_uploads study_material_uploads_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_uploads
    ADD CONSTRAINT study_material_uploads_pkey PRIMARY KEY (id);


--
-- Name: categories uq_categories_user_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT uq_categories_user_name UNIQUE (user_id, name);


--
-- Name: course_gpa_stats uq_course_gpa_stats_course_term_year_section; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_gpa_stats
    ADD CONSTRAINT uq_course_gpa_stats_course_term_year_section UNIQUE (course_id, term, year, section);


--
-- Name: course_offerings uq_course_offerings_course_term_year_section; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_offerings
    ADD CONSTRAINT uq_course_offerings_course_term_year_section UNIQUE (course_id, term, year, section);


--
-- Name: course_reviews uq_course_reviews_course_user; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT uq_course_reviews_course_user UNIQUE (course_id, user_id);


--
-- Name: courses uq_courses_code_level; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT uq_courses_code_level UNIQUE (code, level);


--
-- Name: study_material_library_entries uq_study_material_library_upload; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT uq_study_material_library_upload UNIQUE (upload_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_google_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_google_id_key UNIQUE (google_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_assessments_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_assessments_id ON public.assessments USING btree (id);


--
-- Name: ix_assessments_user_course; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_assessments_user_course ON public.assessments USING btree (user_id, course_id);


--
-- Name: ix_assessments_user_deadline; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_assessments_user_deadline ON public.assessments USING btree (user_id, deadline);


--
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_categories_id ON public.categories USING btree (id);


--
-- Name: ix_categories_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_categories_user_id ON public.categories USING btree (user_id);


--
-- Name: ix_course_gpa_stats_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_course_gpa_stats_id ON public.course_gpa_stats USING btree (id);


--
-- Name: ix_course_offerings_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_course_offerings_id ON public.course_offerings USING btree (id);


--
-- Name: ix_course_reviews_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_course_reviews_course_id ON public.course_reviews USING btree (course_id);


--
-- Name: ix_course_reviews_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_course_reviews_id ON public.course_reviews USING btree (id);


--
-- Name: ix_course_reviews_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_course_reviews_user_id ON public.course_reviews USING btree (user_id);


--
-- Name: ix_courses_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_courses_id ON public.courses USING btree (id);


--
-- Name: ix_events_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_events_id ON public.events USING btree (id);


--
-- Name: ix_events_user_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_events_user_category ON public.events USING btree (user_id, category_id);


--
-- Name: ix_events_user_start_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_events_user_start_at ON public.events USING btree (user_id, start_at);


--
-- Name: ix_study_material_library_entries_course_week_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_study_material_library_entries_course_week_created ON public.study_material_library_entries USING btree (course_id, curated_week, created_at);


--
-- Name: ix_study_material_uploads_course_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_study_material_uploads_course_id ON public.study_material_uploads USING btree (course_id);


--
-- Name: ix_study_material_uploads_status_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_study_material_uploads_status_created ON public.study_material_uploads USING btree (upload_status, created_at);


--
-- Name: ix_study_material_uploads_uploader_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_study_material_uploads_uploader_id ON public.study_material_uploads USING btree (uploader_id);


--
-- Name: ix_study_material_uploads_user_course_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_study_material_uploads_user_course_created ON public.study_material_uploads USING btree (uploader_id, course_id, created_at);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: assessments assessments_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: assessments assessments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: categories categories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: course_gpa_stats course_gpa_stats_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_gpa_stats
    ADD CONSTRAINT course_gpa_stats_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: course_offerings course_offerings_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_offerings
    ADD CONSTRAINT course_offerings_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: course_reviews course_reviews_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: course_reviews course_reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: enrollments enrollments_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: enrollments enrollments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: events events_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE SET NULL;


--
-- Name: events events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: study_material_library_entries study_material_library_entries_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT study_material_library_entries_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: study_material_library_entries study_material_library_entries_curated_by_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT study_material_library_entries_curated_by_admin_id_fkey FOREIGN KEY (curated_by_admin_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: study_material_library_entries study_material_library_entries_upload_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT study_material_library_entries_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES public.study_material_uploads(id) ON DELETE CASCADE;


--
-- Name: study_material_uploads study_material_uploads_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_uploads
    ADD CONSTRAINT study_material_uploads_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: study_material_uploads study_material_uploads_uploader_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_material_uploads
    ADD CONSTRAINT study_material_uploads_uploader_id_fkey FOREIGN KEY (uploader_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict UNedNNbMeDneEmL2lqXZqToHl8PO7FcaXXH5NTTtjfZPeOFNTvCISQbQZ6eh2cv

