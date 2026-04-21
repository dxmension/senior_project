--
-- PostgreSQL database dump
--

\restrict MQV5ksn9v7fmQbd13fuyheVlwOTbn2MBfeawhDZYkY8Zrp0gpqo2hPAnC9c1NBN

-- Dumped from database version 15.17
-- Dumped by pg_dump version 18.1 (Postgres.app)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: assessment_type; Type: TYPE; Schema: public; Owner: postgres
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


ALTER TYPE public.assessment_type OWNER TO postgres;

--
-- Name: enrollmentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.enrollmentstatus AS ENUM (
    'PASSED',
    'IN_PROGRESS',
    'WITHDRAWN',
    'FAILED',
    'AUDIT',
    'INCOMPLETE'
);


ALTER TYPE public.enrollmentstatus OWNER TO postgres;

--
-- Name: materialcurationstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.materialcurationstatus AS ENUM (
    'PENDING',
    'PUBLISHED',
    'REJECTED',
    'NOT_REQUESTED'
);


ALTER TYPE public.materialcurationstatus OWNER TO postgres;

--
-- Name: materialuploadstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.materialuploadstatus AS ENUM (
    'QUEUED',
    'UPLOADING',
    'COMPLETED',
    'FAILED'
);


ALTER TYPE public.materialuploadstatus OWNER TO postgres;

--
-- Name: mockexamattemptstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mockexamattemptstatus AS ENUM (
    'IN_PROGRESS',
    'COMPLETED',
    'ABANDONED'
);


ALTER TYPE public.mockexamattemptstatus OWNER TO postgres;

--
-- Name: mockexamgenerationstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mockexamgenerationstatus AS ENUM (
    'queued',
    'running',
    'completed',
    'failed',
    'cancelled',
    'skipped'
);


ALTER TYPE public.mockexamgenerationstatus OWNER TO postgres;

--
-- Name: mockexamgenerationtrigger; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mockexamgenerationtrigger AS ENUM (
    'create',
    'update',
    'deadline_reminder',
    'retry'
);


ALTER TYPE public.mockexamgenerationtrigger OWNER TO postgres;

--
-- Name: mockexamorigin; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mockexamorigin AS ENUM (
    'manual',
    'ai'
);


ALTER TYPE public.mockexamorigin OWNER TO postgres;

--
-- Name: mockexamquestioncurationstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mockexamquestioncurationstatus AS ENUM (
    'pending',
    'approved',
    'rejected'
);


ALTER TYPE public.mockexamquestioncurationstatus OWNER TO postgres;

--
-- Name: mockexamquestionsource; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mockexamquestionsource AS ENUM (
    'ai',
    'historic',
    'rumored',
    'tutor_made'
);


ALTER TYPE public.mockexamquestionsource OWNER TO postgres;

--
-- Name: mockexamvisibilityscope; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.mockexamvisibilityscope AS ENUM (
    'course',
    'personal'
);


ALTER TYPE public.mockexamvisibilityscope OWNER TO postgres;

--
-- Name: recurrence_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.recurrence_type AS ENUM (
    'none',
    'daily',
    'weekly',
    'biweekly',
    'monthly'
);


ALTER TYPE public.recurrence_type OWNER TO postgres;

--
-- Name: studyguidesourcetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.studyguidesourcetype AS ENUM (
    'materials',
    'ai_knowledge',
    'hybrid'
);


ALTER TYPE public.studyguidesourcetype OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: assessments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assessments (
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    assessment_type public.assessment_type NOT NULL,
    description text,
    deadline timestamp with time zone NOT NULL,
    weight double precision,
    score double precision,
    max_score double precision,
    is_completed boolean NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    assessment_number integer NOT NULL
);


ALTER TABLE public.assessments OWNER TO postgres;

--
-- Name: assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.assessments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assessments_id_seq OWNER TO postgres;

--
-- Name: assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.assessments_id_seq OWNED BY public.assessments.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    color character varying(7) NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: course_gpa_stats; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.course_gpa_stats OWNER TO postgres;

--
-- Name: course_gpa_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.course_gpa_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_gpa_stats_id_seq OWNER TO postgres;

--
-- Name: course_gpa_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.course_gpa_stats_id_seq OWNED BY public.course_gpa_stats.id;


--
-- Name: course_offerings; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.course_offerings OWNER TO postgres;

--
-- Name: course_offerings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.course_offerings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_offerings_id_seq OWNER TO postgres;

--
-- Name: course_offerings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.course_offerings_id_seq OWNED BY public.course_offerings.id;


--
-- Name: course_reviews; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.course_reviews OWNER TO postgres;

--
-- Name: course_reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.course_reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_reviews_id_seq OWNER TO postgres;

--
-- Name: course_reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.course_reviews_id_seq OWNED BY public.course_reviews.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.courses OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: enrollments; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.enrollments OWNER TO postgres;

--
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.events OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.events_id_seq OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- Name: flashcard_decks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flashcard_decks (
    id integer NOT NULL,
    course_id integer NOT NULL,
    title character varying(255) NOT NULL,
    card_count integer DEFAULT 0 NOT NULL,
    difficulty character varying(16) NOT NULL,
    owner_user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.flashcard_decks OWNER TO postgres;

--
-- Name: flashcard_decks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.flashcard_decks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.flashcard_decks_id_seq OWNER TO postgres;

--
-- Name: flashcard_decks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.flashcard_decks_id_seq OWNED BY public.flashcard_decks.id;


--
-- Name: flashcard_session_cards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flashcard_session_cards (
    id integer NOT NULL,
    session_id integer NOT NULL,
    flashcard_id integer NOT NULL,
    times_seen integer DEFAULT 0 NOT NULL,
    times_easy integer DEFAULT 0 NOT NULL,
    times_medium integer DEFAULT 0 NOT NULL,
    times_hard integer DEFAULT 0 NOT NULL,
    last_response character varying(16),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.flashcard_session_cards OWNER TO postgres;

--
-- Name: flashcard_session_cards_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.flashcard_session_cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.flashcard_session_cards_id_seq OWNER TO postgres;

--
-- Name: flashcard_session_cards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.flashcard_session_cards_id_seq OWNED BY public.flashcard_session_cards.id;


--
-- Name: flashcard_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flashcard_sessions (
    id integer NOT NULL,
    deck_id integer NOT NULL,
    user_id integer NOT NULL,
    status character varying(16) NOT NULL,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    ai_review text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.flashcard_sessions OWNER TO postgres;

--
-- Name: flashcard_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.flashcard_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.flashcard_sessions_id_seq OWNER TO postgres;

--
-- Name: flashcard_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.flashcard_sessions_id_seq OWNED BY public.flashcard_sessions.id;


--
-- Name: flashcards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flashcards (
    id integer NOT NULL,
    deck_id integer NOT NULL,
    "position" integer NOT NULL,
    question text NOT NULL,
    answer text NOT NULL,
    topic character varying(128),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.flashcards OWNER TO postgres;

--
-- Name: flashcards_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.flashcards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.flashcards_id_seq OWNER TO postgres;

--
-- Name: flashcards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.flashcards_id_seq OWNED BY public.flashcards.id;


--
-- Name: handbook_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.handbook_plans (
    enrollment_year integer NOT NULL,
    filename character varying(256) NOT NULL,
    status character varying(16) NOT NULL,
    plans json,
    error text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.handbook_plans OWNER TO postgres;

--
-- Name: handbook_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.handbook_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.handbook_plans_id_seq OWNER TO postgres;

--
-- Name: handbook_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.handbook_plans_id_seq OWNED BY public.handbook_plans.id;


--
-- Name: mindmaps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mindmaps (
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    week integer NOT NULL,
    topic character varying(500) NOT NULL,
    tree_json json NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mindmaps OWNER TO postgres;

--
-- Name: mindmaps_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mindmaps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mindmaps_id_seq OWNER TO postgres;

--
-- Name: mindmaps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mindmaps_id_seq OWNED BY public.mindmaps.id;


--
-- Name: mock_exam_attempt_answers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mock_exam_attempt_answers (
    attempt_id integer NOT NULL,
    mock_exam_question_link_id integer NOT NULL,
    selected_option_index integer,
    is_correct boolean,
    answered_at timestamp with time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_mock_exam_attempt_answers_selected_option CHECK (((selected_option_index IS NULL) OR ((selected_option_index >= 1) AND (selected_option_index <= 6))))
);


ALTER TABLE public.mock_exam_attempt_answers OWNER TO postgres;

--
-- Name: mock_exam_attempt_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mock_exam_attempt_answers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mock_exam_attempt_answers_id_seq OWNER TO postgres;

--
-- Name: mock_exam_attempt_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mock_exam_attempt_answers_id_seq OWNED BY public.mock_exam_attempt_answers.id;


--
-- Name: mock_exam_attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mock_exam_attempts (
    user_id integer NOT NULL,
    mock_exam_id integer NOT NULL,
    status public.mockexamattemptstatus NOT NULL,
    started_at timestamp with time zone NOT NULL,
    submitted_at timestamp with time zone,
    last_active_at timestamp with time zone NOT NULL,
    current_position integer NOT NULL,
    answered_count integer NOT NULL,
    correct_count integer NOT NULL,
    score_pct double precision,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mock_exam_attempts OWNER TO postgres;

--
-- Name: mock_exam_attempts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mock_exam_attempts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mock_exam_attempts_id_seq OWNER TO postgres;

--
-- Name: mock_exam_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mock_exam_attempts_id_seq OWNED BY public.mock_exam_attempts.id;


--
-- Name: mock_exam_generation_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mock_exam_generation_jobs (
    assessment_id integer NOT NULL,
    user_id integer NOT NULL,
    course_offering_id integer NOT NULL,
    course_id integer NOT NULL,
    assessment_type public.assessment_type NOT NULL,
    assessment_number integer NOT NULL,
    trigger public.mockexamgenerationtrigger NOT NULL,
    status public.mockexamgenerationstatus NOT NULL,
    run_at timestamp with time zone NOT NULL,
    attempts integer NOT NULL,
    celery_task_id character varying(255),
    error_message text,
    generated_mock_exam_id integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    generation_options text,
    notification_sent_at timestamp with time zone
);


ALTER TABLE public.mock_exam_generation_jobs OWNER TO postgres;

--
-- Name: mock_exam_generation_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mock_exam_generation_jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mock_exam_generation_jobs_id_seq OWNER TO postgres;

--
-- Name: mock_exam_generation_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mock_exam_generation_jobs_id_seq OWNED BY public.mock_exam_generation_jobs.id;


--
-- Name: mock_exam_generation_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mock_exam_generation_settings (
    setting_key character varying(32) NOT NULL,
    assessment_type public.assessment_type,
    enabled boolean NOT NULL,
    model character varying(64) NOT NULL,
    temperature double precision NOT NULL,
    question_count integer NOT NULL,
    time_limit_minutes integer,
    max_source_files integer NOT NULL,
    max_source_chars integer NOT NULL,
    regeneration_offset_hours integer NOT NULL,
    new_question_ratio double precision NOT NULL,
    tricky_question_ratio double precision NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mock_exam_generation_settings OWNER TO postgres;

--
-- Name: mock_exam_generation_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mock_exam_generation_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mock_exam_generation_settings_id_seq OWNER TO postgres;

--
-- Name: mock_exam_generation_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mock_exam_generation_settings_id_seq OWNED BY public.mock_exam_generation_settings.id;


--
-- Name: mock_exam_question_links; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mock_exam_question_links (
    mock_exam_id integer NOT NULL,
    question_id integer NOT NULL,
    "position" integer NOT NULL,
    points integer NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mock_exam_question_links OWNER TO postgres;

--
-- Name: mock_exam_question_links_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mock_exam_question_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mock_exam_question_links_id_seq OWNER TO postgres;

--
-- Name: mock_exam_question_links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mock_exam_question_links_id_seq OWNED BY public.mock_exam_question_links.id;


--
-- Name: mock_exam_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mock_exam_questions (
    course_id integer NOT NULL,
    historical_course_offering_id integer,
    question_text text NOT NULL,
    answer_variant_1 text NOT NULL,
    answer_variant_2 text NOT NULL,
    answer_variant_3 text,
    answer_variant_4 text,
    answer_variant_5 text,
    answer_variant_6 text,
    correct_option_index integer NOT NULL,
    explanation text,
    created_by_admin_id integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    source public.mockexamquestionsource NOT NULL,
    visibility_scope public.mockexamvisibilityscope NOT NULL,
    owner_user_id integer,
    historic_section character varying(100),
    historic_year integer,
    curation_status public.mockexamquestioncurationstatus DEFAULT 'approved'::public.mockexamquestioncurationstatus NOT NULL,
    submitted_by_user_id integer,
    rejection_reason text,
    CONSTRAINT ck_mock_exam_questions_correct_option CHECK (((correct_option_index >= 1) AND (correct_option_index <= 6))),
    CONSTRAINT ck_mock_exam_questions_source_offering CHECK ((((source = 'historic'::public.mockexamquestionsource) AND (historical_course_offering_id IS NOT NULL)) OR ((source = ANY (ARRAY['ai'::public.mockexamquestionsource, 'rumored'::public.mockexamquestionsource, 'tutor_made'::public.mockexamquestionsource])) AND (historical_course_offering_id IS NULL))))
);


ALTER TABLE public.mock_exam_questions OWNER TO postgres;

--
-- Name: mock_exam_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mock_exam_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mock_exam_questions_id_seq OWNER TO postgres;

--
-- Name: mock_exam_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mock_exam_questions_id_seq OWNED BY public.mock_exam_questions.id;


--
-- Name: mock_exams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mock_exams (
    course_id integer NOT NULL,
    assessment_type public.assessment_type NOT NULL,
    assessment_title character varying(255) NOT NULL,
    assessment_title_slug character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    version integer NOT NULL,
    question_count integer NOT NULL,
    time_limit_minutes integer,
    instructions text,
    is_active boolean NOT NULL,
    created_by_admin_id integer NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    assessment_number integer NOT NULL,
    origin public.mockexamorigin NOT NULL,
    visibility_scope public.mockexamvisibilityscope NOT NULL,
    owner_user_id integer,
    assessment_id integer
);


ALTER TABLE public.mock_exams OWNER TO postgres;

--
-- Name: mock_exams_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mock_exams_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mock_exams_id_seq OWNER TO postgres;

--
-- Name: mock_exams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mock_exams_id_seq OWNED BY public.mock_exams.id;


--
-- Name: study_guides; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.study_guides (
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    topic character varying(500) NOT NULL,
    overview_json json NOT NULL,
    details_json json DEFAULT '{}'::json NOT NULL,
    source_type public.studyguidesourcetype NOT NULL,
    materials_hash character varying(64),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.study_guides OWNER TO postgres;

--
-- Name: study_guides_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.study_guides_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.study_guides_id_seq OWNER TO postgres;

--
-- Name: study_guides_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.study_guides_id_seq OWNED BY public.study_guides.id;


--
-- Name: study_material_library_entries; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.study_material_library_entries OWNER TO postgres;

--
-- Name: study_material_library_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.study_material_library_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.study_material_library_entries_id_seq OWNER TO postgres;

--
-- Name: study_material_library_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.study_material_library_entries_id_seq OWNED BY public.study_material_library_entries.id;


--
-- Name: study_material_uploads; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.study_material_uploads OWNER TO postgres;

--
-- Name: study_material_uploads_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.study_material_uploads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.study_material_uploads_id_seq OWNER TO postgres;

--
-- Name: study_material_uploads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.study_material_uploads_id_seq OWNED BY public.study_material_uploads.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
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
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    kazakh_level character varying(8),
    enrollment_year integer,
    subscribed_to_notifications boolean DEFAULT true NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: week_overview_cache; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.week_overview_cache (
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    week integer NOT NULL,
    summary character varying(2000) NOT NULL,
    topics_json json NOT NULL,
    materials_hash character varying(64),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.week_overview_cache OWNER TO postgres;

--
-- Name: week_overview_cache_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.week_overview_cache_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.week_overview_cache_id_seq OWNER TO postgres;

--
-- Name: week_overview_cache_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.week_overview_cache_id_seq OWNED BY public.week_overview_cache.id;


--
-- Name: assessments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assessments ALTER COLUMN id SET DEFAULT nextval('public.assessments_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: course_gpa_stats id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_gpa_stats ALTER COLUMN id SET DEFAULT nextval('public.course_gpa_stats_id_seq'::regclass);


--
-- Name: course_offerings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_offerings ALTER COLUMN id SET DEFAULT nextval('public.course_offerings_id_seq'::regclass);


--
-- Name: course_reviews id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_reviews ALTER COLUMN id SET DEFAULT nextval('public.course_reviews_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- Name: flashcard_decks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_decks ALTER COLUMN id SET DEFAULT nextval('public.flashcard_decks_id_seq'::regclass);


--
-- Name: flashcard_session_cards id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_session_cards ALTER COLUMN id SET DEFAULT nextval('public.flashcard_session_cards_id_seq'::regclass);


--
-- Name: flashcard_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_sessions ALTER COLUMN id SET DEFAULT nextval('public.flashcard_sessions_id_seq'::regclass);


--
-- Name: flashcards id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcards ALTER COLUMN id SET DEFAULT nextval('public.flashcards_id_seq'::regclass);


--
-- Name: handbook_plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handbook_plans ALTER COLUMN id SET DEFAULT nextval('public.handbook_plans_id_seq'::regclass);


--
-- Name: mindmaps id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mindmaps ALTER COLUMN id SET DEFAULT nextval('public.mindmaps_id_seq'::regclass);


--
-- Name: mock_exam_attempt_answers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempt_answers ALTER COLUMN id SET DEFAULT nextval('public.mock_exam_attempt_answers_id_seq'::regclass);


--
-- Name: mock_exam_attempts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempts ALTER COLUMN id SET DEFAULT nextval('public.mock_exam_attempts_id_seq'::regclass);


--
-- Name: mock_exam_generation_jobs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_jobs ALTER COLUMN id SET DEFAULT nextval('public.mock_exam_generation_jobs_id_seq'::regclass);


--
-- Name: mock_exam_generation_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_settings ALTER COLUMN id SET DEFAULT nextval('public.mock_exam_generation_settings_id_seq'::regclass);


--
-- Name: mock_exam_question_links id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_question_links ALTER COLUMN id SET DEFAULT nextval('public.mock_exam_question_links_id_seq'::regclass);


--
-- Name: mock_exam_questions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_questions ALTER COLUMN id SET DEFAULT nextval('public.mock_exam_questions_id_seq'::regclass);


--
-- Name: mock_exams id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exams ALTER COLUMN id SET DEFAULT nextval('public.mock_exams_id_seq'::regclass);


--
-- Name: study_guides id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_guides ALTER COLUMN id SET DEFAULT nextval('public.study_guides_id_seq'::regclass);


--
-- Name: study_material_library_entries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_library_entries ALTER COLUMN id SET DEFAULT nextval('public.study_material_library_entries_id_seq'::regclass);


--
-- Name: study_material_uploads id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_uploads ALTER COLUMN id SET DEFAULT nextval('public.study_material_uploads_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: week_overview_cache id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.week_overview_cache ALTER COLUMN id SET DEFAULT nextval('public.week_overview_cache_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
20260420_0017
\.


--
-- Data for Name: assessments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.assessments (user_id, course_id, assessment_type, description, deadline, weight, score, max_score, is_completed, id, created_at, updated_at, assessment_number) FROM stdin;
2	234	midterm	\N	2026-05-12 07:00:00+00	20	\N	1000	f	10	2026-04-20 15:24:00.747892+00	2026-04-20 15:24:00.747892+00	1
2	234	final	\N	2026-04-21 17:31:00+00	20	\N	100	f	12	2026-04-20 17:08:08.770468+00	2026-04-20 17:30:27.069887+00	1
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (user_id, name, color, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: course_gpa_stats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.course_gpa_stats (course_id, term, year, section, avg_gpa, total_enrolled, grade_distribution, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: course_offerings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.course_offerings (course_id, term, year, section, start_date, end_date, days, meeting_time, enrolled, capacity, faculty, room, id) FROM stdin;
1	Spring	2026	1L	2026-01-12	2026-04-24	T	02:00 PM-05:00 PM	50	50	Mirat Akshalov,\nChristian\nSofilkanitsch	(C3) 1009 -\ncap:70	1
1	Spring	2026	2L	2026-01-12	2026-04-24	R	02:00 PM-05:00 PM	30	23	Mirat Akshalov,\nChristian\nSofilkanitsch	(C3) 3017 -\ncap:38	2
2	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	107	75	Russell Zanca	Green Hall -\ncap:231	3
3	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	142	150	Alima Bissenova	Green Hall -\ncap:231	4
4	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	87	100	Abay Namen	5.103 -\ncap:160	5
5	Spring	2026	1S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	27	27	Karina\nMatkarimova	8.310 -\ncap:27	6
5	Spring	2026	2S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	27	27	Philipp\nSchroeder	8.154 -\ncap:56	7
6	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	25	25	Russell Zanca	8.310 -\ncap:27	8
7	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	25	25	Katherine\nErdman	8.422A -\ncap:32	9
8	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	25	25	Paula Dupuy	8.321 -\ncap:32	10
9	Spring	2026	1L	2026-01-12	2026-04-24	F	09:00 AM-11:50 AM	24	25	Ulan Bigozhin	8.154 -\ncap:56	11
10	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	18	25	Paula Dupuy	8.321 -\ncap:32	12
11	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	24	25	Snezhana\nAtanova	8.154 -\ncap:56	13
12	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-03:50 PM	19	25	Snezhana\nAtanova	8.422A -\ncap:32	14
13	Spring	2026	1L	2026-01-12	2026-04-24	W	01:00 PM-03:50 PM	12	16	Reed Coil	8.147 -\ncap:15	15
14	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	20	25	Matvey\nLomonosov	8.310 -\ncap:27	16
15	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Paula Dupuy	\N	17
15	Spring	2026	3Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Abay Namen	\N	18
15	Spring	2026	4Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Philipp\nSchroeder	\N	19
16	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Paula Dupuy	\N	20
17	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	26	26	Philipp\nSchroeder	8.154 -\ncap:56	21
17	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	26	26	Philipp\nSchroeder	8.154 -\ncap:56	22
18	Spring	2026	1S	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	2	25	Dana\nBurkhanova	8.154 -\ncap:56	23
19	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:30 AM-10:20 AM	1	1	Mirat Akshalov	(C3) 3038 -\ncap:39	24
20	Spring	2026	1L	2026-01-12	2026-04-24	M	02:00 PM-05:00 PM	7	7	Mirat Akshalov,\nDavid Reinhard	(C3) 1009 -\ncap:70	25
21	Spring	2026	1L	2026-01-12	2026-04-24	W	02:00 PM-05:00 PM	9	7	Mirat Akshalov,\nRoza\nNurgozhayeva	(C3) 1009 -\ncap:70	26
22	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	1	1	Mirat Akshalov	(C3) 3038 -\ncap:39	27
23	Spring	2026	1L	2026-01-12	2026-04-24	F	02:00 PM-05:00 PM	7	7	Mirat Akshalov,\nNarendra Singh	(C3) 1009 -\ncap:70	28
24	Spring	2026	3L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	78	90	Nurtilek\nGalimov	Blue Hall -\ncap:239	29
24	Spring	2026	4L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	86	90	Aigerim\nSoltabayeva	Blue Hall -\ncap:239	30
24	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	81	90	yingqiu Xie	Green Hall -\ncap:231	31
24	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	67	90	Zarina\nSautbayeva	7E.329 -\ncap:95	32
25	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	13	60	Alexandr Pak	7E.529 -\ncap:95	33
25	Spring	2026	2L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	69	70	Olena\nFilchakova	7E.529 -\ncap:95	34
26	Spring	2026	4Lb	2026-01-12	2026-04-24	T	12:00 PM-02:50 PM	15	16	Nurtilek\nGalimov	9.228 -\ncap:40	35
26	Spring	2026	5Lb	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	16	16	Zarina\nSautbayeva	9.228 -\ncap:40	36
26	Spring	2026	6Lb	2026-01-12	2026-04-24	R	12:00 PM-02:50 PM	17	16	Zarina\nSautbayeva	9.228 -\ncap:40	37
26	Spring	2026	2Lb	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	16	16	Burkitkan\nAkbay	7.407 -\ncap:20	38
26	Spring	2026	3Lb	2026-01-12	2026-04-24	M	12:00 PM-02:50 PM	17	16	Burkitkan\nAkbay	7.407 -\ncap:20	39
27	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	17	30	Alexandr Pak	7.105 -\ncap:75	40
28	Spring	2026	1R	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	10	24	Sergey Yegorov	7E.217 -\ncap:24	41
28	Spring	2026	3R	2026-01-12	2026-04-24	M	06:00 PM-06:50 PM	8	24	Sergey Yegorov	7E.217 -\ncap:24	42
28	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	18	72	Sergey Yegorov	8.522 -\ncap:72	43
29	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	50	60	Ivan Vorobyev	7.105 -\ncap:75	44
30	Spring	2026	1Lb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	6	16	Radmir\nSarsenov	7.410 -\ncap:15	45
31	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	26	60	Damira\nKanayeva	7E.529 -\ncap:95	46
32	Spring	2026	2Lb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	16	16	Nurtilek\nGalimov	7.407 -\ncap:20	47
33	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	48	60	Timo Burster	7.105 -\ncap:75	48
34	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	23	60	Otilia Nuta	7.105 -\ncap:75	49
35	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	21	24	Tursonjan\nTokay	8.105 -\ncap:56	50
36	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	32	36	Natalie\nBarteneva	7.105 -\ncap:75	51
37	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	70	70	Timo Burster	7E.529 -\ncap:95	52
38	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	21	24	Otilia Nuta	7.105 -\ncap:75	53
38	Spring	2026	2L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	14	14	yingqiu Xie	7.105 -\ncap:75	54
39	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	23	70	Zhanat\nMuminova	7E.529 -\ncap:95	55
40	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	18	30	Dos Sarbassov	7E.529 -\ncap:95	56
41	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	53	75	Olena\nFilchakova	7E.529 -\ncap:95	57
42	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	33	60	Zhanat\nMuminova	7E.529 -\ncap:95	58
43	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	13	36	Damira\nKanayeva	7E.529 -\ncap:95	59
44	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	5	18	Ivan Vorobyev	7.517 -\ncap:25	60
45	Spring	2026	1Lb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	4	12	Radmir\nSarsenov	9.502 -\ncap:8	61
46	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	6	24	Sergey Yegorov	7.517 -\ncap:25	62
47	Spring	2026	1Wsh	2026-01-12	2026-04-24	\N	Online/Distant	8	18	Olena\nFilchakova	\N	63
48	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	27	27	Dos Sarbassov	\N	64
114	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	940
48	Spring	2026	2P	2026-01-12	2026-04-24	\N	Online/Distant	25	27	Tri Pham	\N	65
49	Spring	2026	3R	2026-01-12	2026-04-24	T	11:00 AM-11:50 AM	47	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 2003 -\ncap:67	66
49	Spring	2026	10R	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	47	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 2003 -\ncap:67	67
49	Spring	2026	1L	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	572	588	Mirat Akshalov,\nSaniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	Blue Hall -\ncap:239	68
49	Spring	2026	1R	2026-01-12	2026-04-24	T	09:00 AM-09:50 AM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	69
49	Spring	2026	2R	2026-01-12	2026-04-24	T	10:00 AM-10:50 AM	45	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	70
49	Spring	2026	4R	2026-01-12	2026-04-24	T	11:00 AM-11:50 AM	48	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	71
49	Spring	2026	5R	2026-01-12	2026-04-24	T	12:00 PM-12:50 PM	47	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	72
49	Spring	2026	6R	2026-01-12	2026-04-24	T	01:00 PM-01:50 PM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	73
49	Spring	2026	7R	2026-01-12	2026-04-24	W	09:00 AM-09:50 AM	46	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	74
49	Spring	2026	8R	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	48	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	75
49	Spring	2026	9R	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	76
49	Spring	2026	11R	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	48	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	77
49	Spring	2026	12R	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	49	49	Saniya\nBarbolova,\nZharaskhan\nTemirkhanov,\nMoldir\nKaiynbayeva,\nRaola Yerbolat	(C3) 1009 -\ncap:70	78
50	Spring	2026	1L	2026-01-12	2026-04-24	R	10:30 AM-11:45 AM	50	50	Mirat Akshalov,\nRoza\nNurgozhayeva	(C3) 1009 -\ncap:70	79
51	Spring	2026	1T	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	65	70	Mert Guney	3E.223 -\ncap:63	80
51	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	65	70	Mert Guney	3E.224 -\ncap:90	81
51	Spring	2026	1Lb	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	30	35	Mert Guney	3E.120 -\ncap:20	82
51	Spring	2026	2Lb	2026-01-12	2026-04-24	R	12:00 PM-01:15 PM	35	35	Mert Guney	3E.120 -\ncap:20	83
52	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	66	70	Elnara\nKussinova	3E.220 -\ncap:90	84
52	Spring	2026	1T	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	66	70	Elnara\nKussinova	3E.223 -\ncap:63	85
53	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	64	65	Dichuan Zhang	3E.220 -\ncap:90	86
53	Spring	2026	1T	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	64	65	Dichuan Zhang	3E.220 -\ncap:90	87
54	Spring	2026	1Lb	2026-01-12	2026-04-24	W	04:00 PM-05:45 PM	29	27	Sung Moon	3.323 -\ncap:64	88
54	Spring	2026	2Lb	2026-01-12	2026-04-24	M	04:00 PM-05:45 PM	26	28	Sung Moon	3.323 -\ncap:64	89
54	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	55	55	Sung Moon	3E.220 -\ncap:90	90
55	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	52	55	Ferhat Karaca	3E.220 -\ncap:90	91
55	Spring	2026	1T	2026-01-12	2026-04-24	M	03:00 PM-03:50 PM	52	55	Ferhat Karaca	3E.220 -\ncap:90	92
56	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	11	30	Woojin Lee	3.316 -\ncap:41	93
56	Spring	2026	1T	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	11	30	Woojin Lee	3.316 -\ncap:41	94
57	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	54	70	Chang Shon	3E.220 -\ncap:90	95
57	Spring	2026	1P	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	54	70	Chang Shon	3E.220 -\ncap:90	96
58	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	45	40	Alfrendo\nSatyanaga	7E.220 -\ncap:56	97
59	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	42	40	Ferhat Karaca	3.309 -\ncap:40	98
59	Spring	2026	1T	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	42	40	Ferhat Karaca	3.309 -\ncap:40	99
60	Spring	2026	1Lb	2026-01-12	2026-04-24	F	04:00 PM-05:45 PM	43	30	Alfrendo\nSatyanaga	3.323 -\ncap:64	100
60	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	43	30	Alfrendo\nSatyanaga	7E.220 -\ncap:56	101
61	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	15	20	Jong Kim,\nBakhyt\nAubakirova	3.309 -\ncap:40	102
62	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	13	40	Shazim Memon	3.302 -\ncap:76	103
62	Spring	2026	1Lb	2026-01-12	2026-04-24	T	04:30 PM-05:45 PM	13	40	Shazim Memon	3E.136 -\ncap:22	104
63	Spring	2026	1Lb	2026-01-12	2026-04-24	F	04:00 PM-05:45 PM	22	40	Elnara\nKussinova	3.302 -\ncap:76	105
63	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	22	40	Elnara\nKussinova	3.303 -\ncap:32	106
64	Spring	2026	1L	2026-01-12	2026-04-24	M W	11:00 AM-11:50 AM	54	40	Abid Nadeem	3E.224 -\ncap:90	107
65	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	69	70	Zhannat\nAshikbayeva	5.103 -\ncap:160	108
66	Spring	2026	2L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	47	40	Akmaral\nSuleimenova	7.105 -\ncap:75	109
66	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	38	40	Khalil Amro	7E.222 -\ncap:95	110
66	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	8	40	Akmaral\nSuleimenova	7E.222 -\ncap:95	111
67	Spring	2026	1ChLb	2026-01-12	2026-04-24	M	12:00 PM-02:50 PM	24	24	Aisulu\nZhanbossinova	9.210 -\ncap:40	112
67	Spring	2026	2ChLb	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	12	24	Roza Oztopcu	9.210 -\ncap:40	113
67	Spring	2026	4ChLb	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	19	24	Roza Oztopcu	9.210 -\ncap:40	114
67	Spring	2026	6ChLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	20	24	Aliya Toleuova	9.210 -\ncap:40	115
67	Spring	2026	7ChLb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	20	24	Saule Issayeva	9.210 -\ncap:40	116
67	Spring	2026	9ChLb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	6	24	Akmaral\nSuleimenova	9.210 -\ncap:40	117
67	Spring	2026	10ChLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	7	15	Aisulu\nZhanbossinova	7.307 -\ncap:15	118
68	Spring	2026	7L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	29	32	Ellina Mun	7.246 -\ncap:48	119
68	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	19	32	Aigerim\nGalyamova	7E.221 -\ncap:56	120
68	Spring	2026	3L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	40	32	Aisulu\nZhanbossinova	7E.221 -\ncap:56	121
68	Spring	2026	4L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	19	32	Sandugash\nKalybekkyzy	7E.221 -\ncap:56	122
68	Spring	2026	5L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	33	32	Aliya Toleuova	7E.221 -\ncap:56	123
68	Spring	2026	6L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	31	32	Aliya Toleuova	7E.529 -\ncap:95	124
68	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	27	32	Roza Oztopcu	7E.125/2 -\ncap:56	125
69	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	68	70	Zhannat\nAshikbayeva	5.103 -\ncap:160	126
69	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	70	70	Zhannat\nAshikbayeva	5.103 -\ncap:160	127
69	Spring	2026	3L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	41	40	Saule Issayeva	5.103 -\ncap:160	128
70	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	1	1	Irshad\nKammakakam	\N	129
71	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	5	32	Salimgerey\nAdilov, Ahmed\nElkamhawy	7E.221 -\ncap:56	130
71	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	18	32	Salimgerey\nAdilov, Ahmed\nElkamhawy	7E.221 -\ncap:56	131
72	Spring	2026	1Lb	2026-01-12	2026-04-24	F	09:00 AM-11:50 AM	5	24	Ozgur Oztopcu	7.307 -\ncap:15	132
72	Spring	2026	2Lb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	5	24	Rauan Smail	7.307 -\ncap:15	133
73	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	22	24	Irshad\nKammakakam	7E.221 -\ncap:56	134
73	Spring	2026	2L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	8	32	Davit\nHayrapetyan	7E.221 -\ncap:56	135
73	Spring	2026	3L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	23	24	Irshad\nKammakakam	7E.221 -\ncap:56	136
74	Spring	2026	1ChLb	2026-01-12	2026-04-24	F	03:00 PM-05:50 PM	21	24	Ozgur Oztopcu	7.307 -\ncap:15	137
74	Spring	2026	2ChLb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	13	24	Ozgur Oztopcu	7.307 -\ncap:15	138
74	Spring	2026	4ChLb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	6	24	Rauan Smail	7.307 -\ncap:15	139
75	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	37	40	Timur Atabaev	7.105 -\ncap:75	140
76	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	27	28	Rostislav\nBukasov	7.105 -\ncap:75	141
77	Spring	2026	1ChLb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	24	24	Rostislav\nBukasov	7.310 -\ncap:15	142
78	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	23	24	Haiyan Fan	7E.221 -\ncap:56	143
79	Spring	2026	1ChLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	18	20	Haiyan Fan	7.310 -\ncap:15	144
80	Spring	2026	1ChLb	2026-01-12	2026-04-24	F	03:00 PM-05:50 PM	18	24	Akmaral\nSuleimenova	7.310 -\ncap:15	145
80	Spring	2026	2ChLb	2026-01-12	2026-04-24	M	11:00 AM-01:50 PM	10	24	Akmaral\nSuleimenova	7.310 -\ncap:15	146
81	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	20	24	Andrey\nKhalimon	7E.221 -\ncap:56	147
81	Spring	2026	2L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	9	24	Andrey\nKhalimon	7E.221 -\ncap:56	148
82	Spring	2026	1S	2026-01-12	2026-04-24	\N	Online/Distant	13	24	Salimgerey\nAdilov	\N	149
83	Spring	2026	1L	2026-01-12	2026-04-24	W	06:00 PM-08:50 PM	20	24	Davit\nHayrapetyan	7E.221 -\ncap:56	150
84	Spring	2026	1L	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	4	12	Mannix Balanay	7E.546/1 -\ncap:25	151
85	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	20	30	Vesselin Paunov	7.507 -\ncap:48	152
86	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	21	30	Ellina Mun,\nAhmed\nElkamhawy	7E.125/2 -\ncap:56	153
87	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	16	24	Salimgerey\nAdilov	\N	154
88	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	7	24	Timur Atabaev	9.105 -\ncap:68	155
89	Spring	2026	1Lb	2026-01-12	2026-04-24	W	02:00 PM-03:50 PM	29	35	Yanwei Wang	3.323 -\ncap:64	156
89	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	29	35	Yanwei Wang	3.309 -\ncap:40	157
90	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	31	35	Azhar\nMukasheva	3.316 -\ncap:41	158
90	Spring	2026	1Lb	2026-01-12	2026-04-24	T	12:00 PM-01:45 PM	17	17	Azhar\nMukasheva	3E.418 -\ncap:20	159
90	Spring	2026	2Lb	2026-01-12	2026-04-24	T	02:00 PM-03:25 PM	14	17	Azhar\nMukasheva	3E.418 -\ncap:20	160
91	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:30 PM-04:45 PM	27	30	Stavros\nPoulopoulos,\nSabina\nKhamzina	3E.223 -\ncap:63	161
92	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	26	30	Stavros\nPoulopoulos	3.322 -\ncap:41	162
92	Spring	2026	1CLb	2026-01-12	2026-04-24	R	05:00 PM-06:15 PM	26	30	Stavros\nPoulopoulos,\nSabina\nKhamzina	7E.125/3 -\ncap:54	163
93	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-03:50 PM	8	8	Azhar\nMukasheva	3E.424 -\ncap:15	164
93	Spring	2026	2Lb	2026-01-12	2026-04-24	W	02:00 PM-03:50 PM	8	8	Azhar\nMukasheva	3E.424 -\ncap:15	165
93	Spring	2026	3Lb	2026-01-12	2026-04-24	F	02:00 PM-03:50 PM	8	8	Azhar\nMukasheva	3E.424 -\ncap:15	166
93	Spring	2026	4Lb	2026-01-12	2026-04-24	M	04:00 PM-05:50 PM	0	8	Azhar\nMukasheva	3E.424 -\ncap:15	167
94	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	26	30	Lyazzat\nMukhangaliyeva	\N	168
95	Spring	2026	1L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	47	50	Aishuak\nKonarov	3E.220 -\ncap:90	169
95	Spring	2026	1Lb	2026-01-12	2026-04-24	W	01:00 PM-02:50 PM	47	50	Aishuak\nKonarov	3E.422 -\ncap:20	170
96	Spring	2026	1Lb	2026-01-12	2026-04-24	T	10:30 AM-11:45 AM	48	50	Dhawal Shah	3.323 -\ncap:64	171
96	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	48	50	Dhawal Shah	3E.220 -\ncap:90	172
97	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	29	30	Cevat Erisken	3.316 -\ncap:41	173
98	Spring	2026	1Lb	2026-01-12	2026-04-24	M	12:00 PM-01:50 PM	14	45	Sergey Spotar	3.323 -\ncap:64	174
98	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	14	45	Sergey Spotar	3.316 -\ncap:41	175
99	Spring	2026	1L	2026-01-12	2026-04-24	T R	02:30 PM-03:45 PM	22	30	Boris Golman	3.322 -\ncap:41	176
99	Spring	2026	1Lb	2026-01-12	2026-04-24	F	02:00 PM-03:50 PM	22	30	Boris Golman	3E.427 -\ncap:20	177
100	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	01:00 PM-01:50 PM	23	24	Lili Zhang	8.305 -\ncap:30	178
100	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	12:00 PM-12:50 PM	25	24	Lili Zhang	8.305 -\ncap:30	179
101	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	02:00 PM-02:50 PM	12	24	Lili Zhang	8.305 -\ncap:30	180
102	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	32	45	Iliyas Tursynbek	7.522 -\ncap:30	181
102	Spring	2026	2L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	41	45	Talgat\nManglayev	7.522 -\ncap:30	182
102	Spring	2026	3L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	39	40	Irina Dolzhikova	7.522 -\ncap:30	183
335	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	941
103	Spring	2026	1L	2026-01-12	2026-04-24	T	01:30 PM-02:45 PM	74	85	Minho Lee	7E.429 -\ncap:90	184
103	Spring	2026	2L	2026-01-12	2026-04-24	T	03:00 PM-04:15 PM	32	85	Lisa Chalaguine	7E.429 -\ncap:90	185
103	Spring	2026	3L	2026-01-12	2026-04-24	T	04:30 PM-05:45 PM	34	85	Anwar Ghani	7E.429 -\ncap:90	186
103	Spring	2026	4L	2026-01-12	2026-04-24	T	06:00 PM-07:15 PM	24	85	Sain\nSaginbekov	7E.429 -\ncap:90	187
103	Spring	2026	1Lb	2026-01-12	2026-04-24	F	01:00 PM-01:50 PM	75	85	Irina Dolzhikova	7E.125/3 -\ncap:54	188
103	Spring	2026	2Lb	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	36	85	Marat Isteleyev	7E.125/3 -\ncap:54	189
103	Spring	2026	3Lb	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	32	85	Adai Shomanov	7E.125/3 -\ncap:54	190
103	Spring	2026	4Lb	2026-01-12	2026-04-24	F	04:00 PM-04:50 PM	21	85	Adai Shomanov	7E.125/3 -\ncap:54	191
104	Spring	2026	1CLb	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	36	56	Asset Berdibek	7.522 -\ncap:30	192
104	Spring	2026	2CLb	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	35	56	Adai Shomanov	7.522 -\ncap:30	193
104	Spring	2026	3CLb	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	12	56	Asset Berdibek,\nAdai Shomanov	7.522 -\ncap:30	194
104	Spring	2026	1L	2026-01-12	2026-04-24	T	10:30 AM-11:45 AM	39	84	Hashim Ali	7E.429 -\ncap:90	195
104	Spring	2026	2L	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	44	84	Shinnazar\nSeytnazarov	7E.429 -\ncap:90	196
105	Spring	2026	1L	2026-01-12	2026-04-24	R	10:30 AM-11:45 AM	76	80	Jean Marie\nGuillaume\nGerard de\nNivelle	7E.429 -\ncap:90	197
105	Spring	2026	2L	2026-01-12	2026-04-24	R	12:00 PM-01:15 PM	121	140	Ben Tyler	7E.429 -\ncap:90	198
105	Spring	2026	3L	2026-01-12	2026-04-24	R	10:30 AM-11:45 AM	52	80	Yesdaulet\nIzenov	7E.429 -\ncap:90	199
105	Spring	2026	1Lb	2026-01-12	2026-04-24	M	09:00 AM-09:50 AM	31	75	Asset Berdibek	7E.125/3 -\ncap:54	200
105	Spring	2026	2Lb	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	73	75	Asset Berdibek	7E.125/3 -\ncap:54	201
105	Spring	2026	3Lb	2026-01-12	2026-04-24	M	11:00 AM-11:50 AM	74	75	Iliyas Tursynbek	7E.125/3 -\ncap:54	202
105	Spring	2026	4Lb	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	71	75	Iliyas Tursynbek	7E.125/3 -\ncap:54	203
106	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	133	120	Askar\nBoranbayev	Green Hall -\ncap:231	204
107	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	132	120	Askar\nBoranbayev	7E.220 -\ncap:56	205
108	Spring	2026	1L	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	74	75	Meiram\nMurzabulatov	3E.224 -\ncap:90	206
108	Spring	2026	2L	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	84	110	Adnan Yazici	3E.224 -\ncap:90	207
108	Spring	2026	3L	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	76	75	Muhammed\nDemirci	3E.224 -\ncap:90	208
109	Spring	2026	1L	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	75	75	Ben Tyler	7E.429 -\ncap:90	209
109	Spring	2026	2L	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	92	110	Jean Marie\nGuillaume\nGerard de\nNivelle	7E.429 -\ncap:90	210
109	Spring	2026	3L	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	72	75	Meiram\nMurzabulatov	7E.429 -\ncap:90	211
110	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	5	40	Antonio Cerone	7.422 -\ncap:30	212
111	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	37	70	Ben Tyler	\N	213
112	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	143	145	Michael Lewis	Orange\nHall -\ncap:450	214
112	Spring	2026	2L	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	138	145	Saida\nMussakhojayeva	Orange\nHall -\ncap:450	215
113	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	84	80	Dimitrios\nZormpas	7E.429 -\ncap:90	216
113	Spring	2026	2L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	132	130	Jurn Gyu Park	7E.429 -\ncap:90	217
113	Spring	2026	3L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	84	80	Latif Zohaib	7E.429 -\ncap:90	218
114	Spring	2026	1L	2026-01-12	2026-04-24	M W	09:00 AM-09:50 AM	77	80	Sain\nSaginbekov	7E.429 -\ncap:90	219
114	Spring	2026	2L	2026-01-12	2026-04-24	M W	10:00 AM-10:50 AM	129	130	Latif Zohaib	7E.429 -\ncap:90	220
114	Spring	2026	3L	2026-01-12	2026-04-24	M W	09:00 AM-09:50 AM	66	80	Shinnazar\nSeytnazarov	7E.429 -\ncap:90	221
114	Spring	2026	1Lb	2026-01-12	2026-04-24	F	09:00 AM-09:50 AM	57	73	Syed\nMuhammad\nUmair Arif	7E.125/3 -\ncap:54	222
114	Spring	2026	2Lb	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	70	73	Syed\nMuhammad\nUmair Arif	7E.125/3 -\ncap:54	223
114	Spring	2026	3Lb	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	72	73	Marat Isteleyev	7E.125/3 -\ncap:54	224
114	Spring	2026	4Lb	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	73	73	Marat Isteleyev	7E.125/3 -\ncap:54	225
115	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	27	35	Tansel\nDokeroglu	online -\ncap:0	226
116	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	31	70	Ben Tyler	\N	227
117	Spring	2026	1L	2026-01-12	2026-04-24	F	05:00 PM-05:50 PM	234	245	Anh Tu Nguyen,\nEnver Ever	online -\ncap:0	228
118	Spring	2026	1L	2026-01-12	2026-04-24	M W	03:00 PM-03:50 PM	15	32	Talgar Bayan	7.246 -\ncap:48	229
118	Spring	2026	1Lb	2026-01-12	2026-04-24	F	03:00 PM-05:00 PM	11	16	Talgar Bayan	7.522 -\ncap:30	230
118	Spring	2026	2Lb	2026-01-12	2026-04-24	F	01:00 PM-02:50 PM	4	16	Talgar Bayan	7.522 -\ncap:30	231
119	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	12	32	Syed\nMuhammad\nUmair Arif	7.422 -\ncap:30	232
120	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	9	35	Dimitrios\nZormpas	3.407 -\ncap:40	233
121	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	65	50	Siamac Fazli	7E.220 -\ncap:56	234
122	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	2	40	Antonio Cerone	7.422 -\ncap:30	235
123	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	21	40	Siamac Fazli	3E.221 -\ncap:50	236
124	Spring	2026	1Lb	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	32	40	Minho Lee	3.323 -\ncap:64	237
124	Spring	2026	1L	2026-01-12	2026-04-24	M W	11:00 AM-11:50 AM	32	40	Minho Lee	7E.220 -\ncap:56	238
125	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	11:00 AM-11:50 AM	21	24	Bastiaan\nLohmann	7.317 -\ncap:24	239
125	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	12:00 PM-12:50 PM	22	24	Bastiaan\nLohmann	7.317 -\ncap:24	240
126	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	160	170	Alejandro Melo\nPonce	Blue Hall -\ncap:239	241
126	Spring	2026	1T	2026-01-12	2026-04-24	M	06:00 PM-06:50 PM	63	65	Alejandro Melo\nPonce	8.522 -\ncap:72	242
126	Spring	2026	2T	2026-01-12	2026-04-24	M	07:00 PM-07:50 PM	46	65	Alejandro Melo\nPonce	8.522 -\ncap:72	243
126	Spring	2026	3T	2026-01-12	2026-04-24	T	06:00 PM-06:50 PM	51	65	Alejandro Melo\nPonce	8.522 -\ncap:72	244
127	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	158	170	Galiya\nSagyndykova	Blue Hall -\ncap:239	245
127	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	170	170	Mehmet Demir	Blue Hall -\ncap:239	246
127	Spring	2026	1T	2026-01-12	2026-04-24	T	07:00 PM-07:50 PM	42	65	Galiya\nSagyndykova	8.522 -\ncap:72	247
127	Spring	2026	2T	2026-01-12	2026-04-24	W	06:00 PM-06:50 PM	64	65	Galiya\nSagyndykova	8.522 -\ncap:72	248
127	Spring	2026	3T	2026-01-12	2026-04-24	W	07:00 PM-07:50 PM	59	65	Galiya\nSagyndykova	8.522 -\ncap:72	249
127	Spring	2026	4T	2026-01-12	2026-04-24	R	06:00 PM-06:50 PM	65	65	Mehmet Demir	8.522 -\ncap:72	250
127	Spring	2026	5T	2026-01-12	2026-04-24	R	07:00 PM-07:50 PM	37	65	Mehmet Demir	8.522 -\ncap:72	251
127	Spring	2026	6T	2026-01-12	2026-04-24	F	06:00 PM-06:50 PM	61	65	Mehmet Demir	8.522 -\ncap:72	252
128	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	169	200	Aigerim\nSarsenbayeva	Blue Hall -\ncap:239	253
129	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	44	40	Oleg Rubanov	8.307 -\ncap:55	254
130	Spring	2026	1T	2026-01-12	2026-04-24	M	06:00 PM-06:50 PM	64	65	Zhanna\nKapsalyamova	8.307 -\ncap:55	255
130	Spring	2026	2T	2026-01-12	2026-04-24	M	07:00 PM-07:50 PM	60	65	Zhanna\nKapsalyamova	8.307 -\ncap:55	256
130	Spring	2026	3T	2026-01-12	2026-04-24	T	06:00 PM-06:50 PM	43	60	Zhanna\nKapsalyamova	8.307 -\ncap:55	257
130	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	167	170	Zhanna\nKapsalyamova	Blue Hall -\ncap:239	258
131	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	52	50	Vladyslav Nora	8.327 -\ncap:58	259
132	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Rajarshi Bhowal	\N	260
132	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Aigerim\nSarsenbayeva	\N	261
132	Spring	2026	3Int	2026-01-12	2026-04-24	\N	Online/Distant	4	5	Mehmet Demir	\N	262
132	Spring	2026	6Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Andrey\nTkachenko	\N	263
133	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	41	40	Nino Buliskeria	8.327 -\ncap:58	264
134	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	33	35	Ahmet Altinok	8.307 -\ncap:55	265
134	Spring	2026	2L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	36	35	Ahmet Altinok	8.307 -\ncap:55	266
135	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	36	35	Levent\nKockesen	8.307 -\ncap:55	267
135	Spring	2026	2L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	39	35	Levent\nKockesen	8.307 -\ncap:55	268
136	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:15 PM	33	35	Rajarshi Bhowal	8.327 -\ncap:58	269
136	Spring	2026	2L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	31	33	Rajarshi Bhowal	8.327 -\ncap:58	270
137	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	37	35	Aigerim\nSarsenbayeva	8.307 -\ncap:55	271
137	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	44	35	Aigerim\nSarsenbayeva	8.307 -\ncap:55	272
138	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	14	35	Zhanna\nKapsalyamova	8.307 -\ncap:55	273
138	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	17	31	Zhanna\nKapsalyamova	8.307 -\ncap:55	274
139	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Rajarshi Bhowal	\N	275
139	Spring	2026	6IS	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Nino Buliskeria	\N	276
139	Spring	2026	7IS	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Alejandro Melo\nPonce	\N	277
140	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	24	22	Josef Ruzicka	8.327 -\ncap:58	278
140	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	41	35	Josef Ruzicka	8.327 -\ncap:58	279
141	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	32	35	Andrey\nTkachenko	8.307 -\ncap:55	280
141	Spring	2026	2L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	32	35	Andrey\nTkachenko	8.307 -\ncap:55	281
142	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	31	34	Rajarshi Bhowal	8.307 -\ncap:55	282
143	Spring	2026	1L	2026-01-12	2026-04-24	T R	07:30 PM-08:45 PM	18	20	Alejandro Melo\nPonce	7E.329 -\ncap:95	283
144	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	72	80	Galymzhan\nNauryzbayev	3E.220 -\ncap:90	284
145	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-03:45 PM	20	20	Shyngys\nSalakchinov	3E.321 -\ncap:22	285
145	Spring	2026	2Lb	2026-01-12	2026-04-24	T	02:00 PM-03:45 PM	10	20	Shyngys\nSalakchinov	3E.321 -\ncap:22	286
145	Spring	2026	3Lb	2026-01-12	2026-04-24	W	02:00 PM-03:45 PM	20	20	Gulsim\nKulsharova	3E.321 -\ncap:22	287
145	Spring	2026	4Lb	2026-01-12	2026-04-24	R	02:00 PM-03:45 PM	20	20	Gulsim\nKulsharova	3E.321 -\ncap:22	288
146	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	74	80	Sultangali\nArzykulov	3E.220 -\ncap:90	289
147	Spring	2026	1Lb	2026-01-12	2026-04-24	M	12:00 PM-01:45 PM	25	26	Aliya\nNurmukhanbeto\nva	3E.322 -\ncap:25	290
147	Spring	2026	2Lb	2026-01-12	2026-04-24	T	12:00 PM-01:45 PM	22	27	Aliya\nNurmukhanbeto\nva	3E.322 -\ncap:25	291
147	Spring	2026	3Lb	2026-01-12	2026-04-24	W	12:00 PM-01:45 PM	27	27	Aliya\nNurmukhanbeto\nva	3E.322 -\ncap:25	292
148	Spring	2026	1L	2026-01-12	2026-04-24	M W	09:00 AM-10:15 AM	45	60	Mohammad\nHashmi	3E.221 -\ncap:50	293
149	Spring	2026	1Lb	2026-01-12	2026-04-24	W	02:00 PM-03:45 PM	29	30	Shyngys\nSalakchinov	3E.322 -\ncap:25	294
149	Spring	2026	2Lb	2026-01-12	2026-04-24	R	02:00 PM-03:45 PM	14	30	Shyngys\nSalakchinov	3E.322 -\ncap:25	295
150	Spring	2026	1L	2026-01-12	2026-04-24	M W	10:30 AM-11:45 AM	17	20	Prashant\nJamwal	(C3) 3037 -\ncap:39	296
151	Spring	2026	1Lb	2026-01-12	2026-04-24	T	02:30 PM-04:15 PM	16	15	Aliya\nNurmukhanbeto\nva	TBA - cap:0	297
152	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	23	40	Mehdi Bagheri	3E.224 -\ncap:90	298
153	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	19	50	Ainur\nRakhymbay,\nAresh Dadlani	3E.221 -\ncap:50	299
154	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	26	40	Sultangali\nArzykulov	3.322 -\ncap:41	300
155	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	4	4	Aliya\nNurmukhanbeto\nva	\N	301
155	Spring	2026	1L	2026-01-12	2026-04-24	W	05:00 PM-06:15 PM	44	54	Aliya\nNurmukhanbeto\nva	7E.220 -\ncap:56	302
156	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	31	40	Carlo Molardi	3.415 -\ncap:42	303
157	Spring	2026	1Lb	2026-01-12	2026-04-24	F	01:00 PM-04:00 PM	14	25	Ainur\nRakhymbay	3E.318 -\ncap:40	304
158	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	3	40	Muhammad\nAkhtar	3.416 -\ncap:46	305
159	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	9	25	Ainur\nRakhymbay,\nAresh Dadlani	3.309 -\ncap:40	306
160	Spring	2026	1L	2026-01-12	2026-04-24	R	01:30 PM-03:00 PM	17	40	Ainur\nRakhymbay,\nMehdi Shafiee	3.407 -\ncap:40	307
161	Spring	2026	1Lb	2026-01-12	2026-04-24	W	02:30 PM-04:00 PM	10	20	Ainur\nRakhymbay,\nMehdi Shafiee	3E.333 -\ncap:40	308
162	Spring	2026	1L	2026-01-12	2026-04-24	M	03:00 PM-04:15 PM	14	20	Prashant\nJamwal	3E.223 -\ncap:63	309
163	Spring	2026	1L	2026-01-12	2026-04-24	F	04:00 PM-05:15 PM	4	40	Gulsim\nKulsharova	3E.224 -\ncap:90	310
164	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	2	20	Carlo Molardi	3.309 -\ncap:40	311
165	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	35	30	Daniele Tosi	3.303 -\ncap:32	312
166	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	93	95	Arailym\nSerikbay	3E.224 -\ncap:90	313
167	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	71	75	Chang Shon	3E.224 -\ncap:90	314
167	Spring	2026	2L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	91	92	Asma Perveen	3E.224 -\ncap:90	315
167	Spring	2026	1Lb	2026-01-12	2026-04-24	T	04:00 PM-05:45 PM	34	38	Chang Shon	3E.331 -\ncap:24	316
167	Spring	2026	2Lb	2026-01-12	2026-04-24	R	04:00 PM-05:45 PM	34	37	Chang Shon	3E.331 -\ncap:24	317
167	Spring	2026	3Lb	2026-01-12	2026-04-24	W	01:00 PM-02:45 PM	48	48	Asma Perveen	3E.331 -\ncap:24	318
167	Spring	2026	4Lb	2026-01-12	2026-04-24	F	04:00 PM-05:45 PM	46	48	Asma Perveen	3E.331 -\ncap:24	319
168	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	85	85	Annie Ng,\nNurxat Nuraje	5.103 -\ncap:160	320
168	Spring	2026	2L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	54	60	Annie Ng,\nNurxat Nuraje	3E.220 -\ncap:90	321
169	Spring	2026	5L	2026-01-12	2026-04-24	F	10:30 AM-11:30 AM	40	40	Behrouz Maham	3.309 -\ncap:40	322
169	Spring	2026	2L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	27	35	Aishuak\nKonarov	3.317 -\ncap:40	323
169	Spring	2026	4L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	36	40	Behrouz Maham	3.416 -\ncap:46	324
169	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	58	64	Elnara\nKussinova	3E.220 -\ncap:90	325
169	Spring	2026	3L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	74	75	Yerkin Abdildin	3E.223 -\ncap:63	326
170	Spring	2026	4Lb	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Md. Hazrat Ali	\N	327
170	Spring	2026	3Lb	2026-01-12	2026-04-24	R	09:00 AM-10:15 AM	29	35	Boris Golman	3.323 -\ncap:64	328
170	Spring	2026	1Lb	2026-01-12	2026-04-24	W	04:00 PM-05:15 PM	66	70	Saltanat\nAkhmadi	3E.223 -\ncap:63	329
170	Spring	2026	2L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	73	75	Md. Hazrat Ali	3E.223 -\ncap:63	330
170	Spring	2026	2Lb	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	71	75	Md. Hazrat Ali	3E.223 -\ncap:63	331
170	Spring	2026	3L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	30	35	Boris Golman	3.415 -\ncap:42	332
170	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	64	70	Saltanat\nAkhmadi	7E.429 -\ncap:90	333
171	Spring	2026	5L	2026-01-12	2026-04-24	\N	Online/Distant	2	3	Yerkin Abdildin,\nEssam Shehab	\N	334
171	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	46	50	Dhawal Shah,\nSabina\nKhamzina	3.323 -\ncap:64	335
171	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	68	70	Mert Guney	5.103 -\ncap:160	336
171	Spring	2026	4L	2026-01-12	2026-04-24	F	03:00 PM-04:45 PM	45	51	Yerkin Abdildin,\nEssam Shehab	3E.223 -\ncap:63	337
171	Spring	2026	1L	2026-01-12	2026-04-24	W	05:00 PM-06:15 PM	43	50	Galymzhan\nNauryzbayev	3E.224 -\ncap:90	338
172	Spring	2026	2L	2026-01-12	2026-04-24	R	02:00 PM-05:00 PM	47	50	Mirat Akshalov,\nTom Vinaimont	(C3) 1009 -\ncap:70	339
172	Spring	2026	1L	2026-01-12	2026-04-24	T	02:00 PM-05:00 PM	30	23	Mirat Akshalov,\nTom Vinaimont	(C3) 3017 -\ncap:38	340
173	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	80	90	George\nMathews	Red Hall\n1022 (C3) -\ncap:265	341
174	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	137	200	George\nMathews	Red Hall\n1022 (C3) -\ncap:265	342
175	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	11	15	Milovan Fustic	6.327 -\ncap:10	343
176	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	12	15	Davit Vasilyan	6.327 -\ncap:10	344
177	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	10	25	Kamal Regmi	6.327 -\ncap:10	345
178	Spring	2026	1L	2026-01-12	2026-04-24	M W	02:00 PM-03:15 PM	13	20	Mahmoud Leila	6.527 -\ncap:4	346
179	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	11	20	Sebastianus\nWillem Josef\nDen Brok	6.427 -\ncap:24	347
180	Spring	2026	1L	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	21	20	Emil Bayramov	6.302 -\ncap:44	348
181	Spring	2026	1L	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	12	20	Marzhan\nBaigaliyeva	6.519 -\ncap:26	349
182	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-03:50 PM	22	20	Emil Bayramov	6.302 -\ncap:44	350
183	Spring	2026	1IS	2026-01-12	2026-04-24	M W F	06:00 PM-06:50 PM	12	15	Sebastianus\nWillem Josef\nDen Brok	6.105 -\ncap:64	351
184	Spring	2026	1L	2026-01-12	2026-04-24	F	12:00 PM-02:30 PM	4	15	Marzhan\nBaigaliyeva	6.422 -\ncap:28	352
185	Spring	2026	1L	2026-01-12	2026-04-24	R	05:00 PM-06:50 PM	9	15	Sebastianus\nWillem Josef\nDen Brok	TBA - cap:0	353
456	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	942
113	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	943
112	Spring	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	944
186	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	11:00 AM-11:50 AM	28	30	Florian\nKuechler	8.305 -\ncap:30	354
187	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	01:00 PM-01:50 PM	11	24	Florian\nKuechler	8.508 -\ncap:24	355
188	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	600	732	Rozaliya\nGaripova	\N	356
188	Spring	2026	4S	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	14	20	Diana\nKopbayeva	9.105 -\ncap:68	357
188	Spring	2026	5S	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	17	20	Diana\nKopbayeva	9.105 -\ncap:68	358
188	Spring	2026	7S	2026-01-12	2026-04-24	M	03:00 PM-03:50 PM	23	24	Nikolay\nTsyrempilov	9.105 -\ncap:68	359
188	Spring	2026	8S	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	24	24	Nikolay\nTsyrempilov	9.105 -\ncap:68	360
188	Spring	2026	9S	2026-01-12	2026-04-24	M	05:00 PM-05:50 PM	24	24	Nikolay\nTsyrempilov	9.105 -\ncap:68	361
188	Spring	2026	10S	2026-01-12	2026-04-24	W	09:00 AM-09:50 AM	24	24	Mikhail Akulov	9.105 -\ncap:68	362
188	Spring	2026	11S	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	24	24	Mikhail Akulov	9.105 -\ncap:68	363
188	Spring	2026	12S	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	24	24	Mikhail Akulov	9.105 -\ncap:68	364
188	Spring	2026	13S	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	16	20	Diana\nKopbayeva	9.105 -\ncap:68	365
188	Spring	2026	14S	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	10	20	Diana\nKopbayeva	9.105 -\ncap:68	366
188	Spring	2026	16S	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	24	24	Mollie\nArbuthnot	9.105 -\ncap:68	367
188	Spring	2026	17S	2026-01-12	2026-04-24	W	04:00 PM-04:50 PM	24	24	Mollie\nArbuthnot	9.105 -\ncap:68	368
188	Spring	2026	19S	2026-01-12	2026-04-24	W	05:00 PM-05:50 PM	23	24	Mollie\nArbuthnot	9.105 -\ncap:68	369
188	Spring	2026	21S	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	21	24	Diana\nKopbayeva	9.105 -\ncap:68	370
188	Spring	2026	22S	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	22	24	Diana\nKopbayeva	9.105 -\ncap:68	371
188	Spring	2026	24S	2026-01-12	2026-04-24	F	01:00 PM-01:50 PM	16	20	Diana\nKopbayeva	9.105 -\ncap:68	372
188	Spring	2026	25S	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	13	20	Diana\nKopbayeva	9.105 -\ncap:68	373
188	Spring	2026	1S	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	24	24	Mikhail Akulov	8.154 -\ncap:56	374
188	Spring	2026	2S	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	22	24	Mikhail Akulov	8.154 -\ncap:56	375
188	Spring	2026	3S	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	24	24	Mikhail Akulov	8.154 -\ncap:56	376
188	Spring	2026	26S	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	21	24	Meiramgul\nKussainova	8.422A -\ncap:32	377
188	Spring	2026	27S	2026-01-12	2026-04-24	F	01:00 PM-01:50 PM	23	24	Meiramgul\nKussainova	8.422A -\ncap:32	378
188	Spring	2026	28S	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	24	24	Meiramgul\nKussainova	8.422A -\ncap:32	379
188	Spring	2026	29S	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	20	20	Aybike Tezel	9.204 -\ncap:38	380
188	Spring	2026	30S	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	20	20	Aybike Tezel	9.204 -\ncap:38	381
188	Spring	2026	31S	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	19	20	Aybike Tezel	9.204 -\ncap:38	382
188	Spring	2026	32S	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	20	20	Aybike Tezel	9.204 -\ncap:38	383
188	Spring	2026	33S	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	20	20	Aybike Tezel	9.204 -\ncap:38	384
188	Spring	2026	34S	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	20	20	Aybike Tezel	9.204 -\ncap:38	385
189	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	53	40	Di Lu	5.103 -\ncap:160	386
190	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	53	40	Di Lu	7E.529 -\ncap:95	387
191	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	30	30	Curtis Murphy	9.204 -\ncap:38	388
192	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	25	28	Aybike Tezel	9.204 -\ncap:38	389
193	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	34	28	Mollie\nArbuthnot	7.210 -\ncap:54	390
194	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	28	28	Curtis Murphy	9.204 -\ncap:38	391
195	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	41	40	Halit Akarca	8.105 -\ncap:56	392
196	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	27	28	Daniel Beben	9.204 -\ncap:38	393
197	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	35	28	Jenni Lehtinen	8.322A -\ncap:32	394
198	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	13	24	Chandler Hatch	9.204 -\ncap:38	395
199	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	27	25	Mikhail Akulov	6.105 -\ncap:64	396
200	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Di Lu	\N	397
201	Spring	2026	1S	2026-01-12	2026-04-24	M W F	06:00 PM-06:50 PM	18	16	Nikolay\nTsyrempilov	9.204 -\ncap:38	398
202	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	20	20	Amanda\nMurphy	8.322A -\ncap:32	399
203	Spring	2026	1S	2026-01-12	2026-04-24	F	02:00 PM-04:50 PM	9	16	Rozaliya\nGaripova	8.319 -\ncap:30	400
204	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	9	10	Curtis Murphy	\N	401
205	Spring	2026	3L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	12	16	Gulzhamilya\nShalabayeva	8.319 -\ncap:30	402
205	Spring	2026	7L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	16	16	Aidar Balabekov	8.308 -\ncap:24	403
205	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	17	16	Aidar Balabekov	8.141 -\ncap:24	404
205	Spring	2026	2L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	17	16	Aidar Balabekov	8.141 -\ncap:24	405
205	Spring	2026	4L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	15	16	Kulyan Kopesh	8.141 -\ncap:24	406
205	Spring	2026	5L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	16	16	Kulyan Kopesh	8.141 -\ncap:24	407
205	Spring	2026	6L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	13	16	Raushan\nMyrzabekova	8.141 -\ncap:24	408
206	Spring	2026	6L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	16	16	Gulzhamilya\nShalabayeva	8.319 -\ncap:30	409
206	Spring	2026	8L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	15	16	Gulzhamilya\nShalabayeva	8.319 -\ncap:30	410
206	Spring	2026	7L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	16	16	Gulzhamilya\nShalabayeva	8.302 -\ncap:57	411
206	Spring	2026	10L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	15	16	Bakyt\nAkbuzauova	8.317 -\ncap:28	412
206	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	10	16	Raushan\nMyrzabekova	8.141 -\ncap:24	413
206	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	14	16	Raushan\nMyrzabekova	8.141 -\ncap:24	414
206	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	14	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	415
206	Spring	2026	4L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	13	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	416
206	Spring	2026	5L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	16	16	Bakyt\nAkbuzauova	8.141 -\ncap:24	417
207	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	161	150	Meiramgul\nKussainova, Uli\nSchamiloglu,\nMoldiyar\nYergebekov	\N	418
457	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	945
207	Spring	2026	1S	2026-01-12	2026-04-24	M	01:00 PM-01:50 PM	28	25	Meiramgul\nKussainova, Uli\nSchamiloglu	7E.125/1 -\ncap:36	419
207	Spring	2026	2S	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	24	25	Uli\nSchamiloglu,\nMoldiyar\nYergebekov	7E.125/1 -\ncap:36	420
207	Spring	2026	3S	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	25	25	Meiramgul\nKussainova, Uli\nSchamiloglu	7E.125/1 -\ncap:36	421
207	Spring	2026	4S	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	26	25	Meiramgul\nKussainova, Uli\nSchamiloglu	7E.125/1 -\ncap:36	422
207	Spring	2026	5S	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	29	25	Uli\nSchamiloglu,\nMoldiyar\nYergebekov	7E.125/1 -\ncap:36	423
207	Spring	2026	6S	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	29	25	Uli\nSchamiloglu,\nMoldiyar\nYergebekov	7E.125/1 -\ncap:36	424
208	Spring	2026	1S	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	29	30	Meruyert\nIbrayeva	8.105 -\ncap:56	425
209	Spring	2026	4S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	29	30	Zeinep\nZhumatayeva	2.407 -\ncap:85	426
209	Spring	2026	5S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	28	30	Zeinep\nZhumatayeva	2.407 -\ncap:85	427
209	Spring	2026	2S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	35	30	Zeinekhan\nKuzekova	8.302 -\ncap:57	428
209	Spring	2026	1S	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	29	30	Samal\nAbzhanova	7E.125/1 -\ncap:36	429
209	Spring	2026	3S	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	30	30	Samal\nAbzhanova	7E.125/1 -\ncap:36	430
210	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	29	30	Zhanar\nBaiteliyeva	8.105 -\ncap:56	431
211	Spring	2026	1S	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	28	30	Mustafa Shokay	8.302 -\ncap:57	432
211	Spring	2026	2S	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	28	30	Mustafa Shokay	8.302 -\ncap:57	433
211	Spring	2026	3S	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	30	30	Mustafa Shokay	8.302 -\ncap:57	434
211	Spring	2026	4S	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	29	30	Mustafa Shokay	8.302 -\ncap:57	435
212	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	28	30	Zhanar\nAbdigapparova	8.302 -\ncap:57	436
213	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	35	30	Meiramgul\nKussainova	8.105 -\ncap:56	437
214	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	28	30	Zhanar\nAbdigapparova	8.302 -\ncap:57	438
215	Spring	2026	2L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	29	30	Kulyan Kopesh	8.327 -\ncap:58	439
215	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	30	30	Kulyan Kopesh	8.105 -\ncap:56	440
216	Spring	2026	1S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	30	30	Zhazira\nAgabekova	7E.125/1 -\ncap:36	441
217	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	29	30	Zhazira\nAgabekova	7E.125/1 -\ncap:36	442
218	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	27	30	Yermek\nAdayeva	9.204 -\ncap:38	443
218	Spring	2026	2L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	28	30	Yermek\nAdayeva	9.204 -\ncap:38	444
218	Spring	2026	3L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	29	30	Yermek\nAdayeva	9.204 -\ncap:38	445
218	Spring	2026	4L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	28	30	Yermek\nAdayeva	9.204 -\ncap:38	446
219	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	29	30	Zhanar\nBaiteliyeva	8.105 -\ncap:56	447
220	Spring	2026	1S	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	30	30	Sarkyt Aliszhan	7E.125/1 -\ncap:36	448
221	Spring	2026	1S	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	33	30	Zeinekhan\nKuzekova	8.302 -\ncap:57	449
222	Spring	2026	1S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	30	30	Sarkyt Aliszhan	7E.125/1 -\ncap:36	450
223	Spring	2026	1S	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	29	30	Zeinep\nZhumatayeva	2.407 -\ncap:85	451
224	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	29	30	Samal\nAbzhanova	6.507 -\ncap:72	452
224	Spring	2026	2L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	31	30	Samal\nAbzhanova	6.507 -\ncap:72	453
225	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	41	40	Moldiyar\nYergebekov	8.105 -\ncap:56	454
226	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	12	20	Aigul Ismakova	8.140 -\ncap:24	455
227	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	8	20	Aigul Ismakova	8.140 -\ncap:24	456
228	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	7	16	Raushan\nMyrzabekova	8.141 -\ncap:24	457
229	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	09:00 AM-09:50 AM	16	24	Joomi Kong	8.317 -\ncap:28	458
229	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	10:00 AM-10:50 AM	23	24	Joomi Kong	8.317 -\ncap:28	459
230	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	11:00 AM-11:50 AM	23	24	Joomi Kong	8.317 -\ncap:28	460
231	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	98	100	Olga Potanina	5.103 -\ncap:160	461
232	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	29	28	Olga Potanina	8.322A -\ncap:32	462
233	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	27	28	Emad Mohamed	8.322A -\ncap:32	463
234	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	12	28	Andrey\nFilchenko	8.322A -\ncap:32	464
235	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	31	28	Clinton Parker	8.327 -\ncap:58	465
236	Spring	2026	1Wsh	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Andrey\nFilchenko	\N	466
236	Spring	2026	2Wsh	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Florian\nKuechler	\N	467
237	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	10	20	Benjamin\nBrosig	8.319 -\ncap:30	468
238	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	21	26	Clinton Parker	8.307 -\ncap:55	469
239	Spring	2026	1S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	9	26	Benjamin\nBrosig	8.422A -\ncap:32	470
240	Spring	2026	1S	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	13	20	Gabriel\nMcGuire,\nNikolay\nMikhailov	8.322A -\ncap:32	471
241	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	9	20	Emad Mohamed	8.322A -\ncap:32	472
242	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	23	24	Eva-Marie\nDubuisson	8.322A -\ncap:32	473
243	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	4	5	Benjamin\nBrosig	\N	474
244	Spring	2026	1Lb	2026-01-12	2026-04-24	M	11:00 AM-12:45 PM	40	40	Didier\nTalamona	TBA - cap:0	475
244	Spring	2026	2Lb	2026-01-12	2026-04-24	F	03:00 PM-04:45 PM	33	40	Didier\nTalamona	TBA - cap:0	476
244	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	73	80	Didier\nTalamona	3E.220 -\ncap:90	477
245	Spring	2026	1T	2026-01-12	2026-04-24	M	02:00 PM-02:45 PM	36	40	Md. Hazrat Ali	3.302 -\ncap:76	478
245	Spring	2026	2T	2026-01-12	2026-04-24	W	02:00 PM-02:45 PM	40	40	Md. Hazrat Ali	3.302 -\ncap:76	479
245	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	76	80	Md. Hazrat Ali	3E.220 -\ncap:90	480
246	Spring	2026	1Lb	2026-01-12	2026-04-24	W	11:00 AM-01:45 PM	59	70	Sherif Gouda,\nDmitriy Sizov	3.323 -\ncap:64	481
246	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	59	70	Sherif Gouda	3E.224 -\ncap:90	482
246	Spring	2026	1T	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	59	70	Sherif Gouda	3E.224 -\ncap:90	483
247	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	23	35	Sergey Spotar	3.415 -\ncap:42	484
247	Spring	2026	1T	2026-01-12	2026-04-24	F	04:00 PM-04:50 PM	23	35	Sergey Spotar	3.415 -\ncap:42	485
247	Spring	2026	1Lb	2026-01-12	2026-04-24	W	03:00 PM-05:45 PM	23	35	Sergey Spotar	3E.324 -\ncap:25	486
248	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	58	70	Konstantinos\nKostas	3E.224 -\ncap:90	487
248	Spring	2026	1Lb	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	58	70	Konstantinos\nKostas	3E.224 -\ncap:90	488
249	Spring	2026	2T	2026-01-12	2026-04-24	\N	Online/Distant	1	3	Didier\nTalamona	\N	489
249	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	25	35	Didier\nTalamona	3.316 -\ncap:41	490
249	Spring	2026	1Lb	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	25	35	Didier\nTalamona	3.407 -\ncap:40	491
249	Spring	2026	1T	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	24	35	Didier\nTalamona	3.407 -\ncap:40	492
250	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	40	35	Altay\nZhakatayev	3.309 -\ncap:40	493
250	Spring	2026	1T	2026-01-12	2026-04-24	M	03:00 PM-03:50 PM	40	35	Altay\nZhakatayev	3.407 -\ncap:40	494
250	Spring	2026	1Lb	2026-01-12	2026-04-24	M	11:00 AM-12:45 PM	40	35	Altay\nZhakatayev	3E.327 -\ncap:25	495
251	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	37	35	Amgad Salama	3.407 -\ncap:40	496
251	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	37	35	Amgad Salama	3.415 -\ncap:42	497
252	Spring	2026	1T	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	41	44	Yerbol\nSarbassov	3.316 -\ncap:41	498
252	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	41	44	Yerbol\nSarbassov	3E.221 -\ncap:50	499
253	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	33	44	Gulnur\nKalimuldina	3E.221 -\ncap:50	500
253	Spring	2026	1T	2026-01-12	2026-04-24	F	12:00 PM-12:50 PM	33	44	Gulnur\nKalimuldina	3E.221 -\ncap:50	501
254	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-03:45 PM	29	44	Gulnur\nKalimuldina	TBA - cap:0	502
254	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	29	44	Gulnur\nKalimuldina	3E.221 -\ncap:50	503
255	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	42	44	Altay\nZhakatayev	3.302 -\ncap:76	504
255	Spring	2026	1P	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	42	44	Altay\nZhakatayev	3E.221 -\ncap:50	505
256	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	16	20	Dmitriy Sizov	3.316 -\ncap:41	506
256	Spring	2026	1Lb	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	16	20	Dmitriy Sizov	3E.217 -\ncap:28	507
257	Spring	2026	2L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	40	60	Catalina\nTroshev	7E.222 -\ncap:95	508
257	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	57	60	Catalina\nTroshev	7E.329 -\ncap:95	509
258	Spring	2026	1R	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	58	57	Bibinur\nShupeyeva	7.210 -\ncap:54	510
258	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	230	228	Amin Esfahani	Orange\nHall -\ncap:450	511
258	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	257	228	Andrey\nMelnikov	Orange\nHall -\ncap:450	512
258	Spring	2026	2R	2026-01-12	2026-04-24	M	11:00 AM-11:50 AM	58	57	Catalina\nTroshev	8.522 -\ncap:72	513
258	Spring	2026	3R	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	64	57	Catalina\nTroshev	8.522 -\ncap:72	514
258	Spring	2026	4R	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	66	57	Catalina\nTroshev	8.522 -\ncap:72	515
258	Spring	2026	5R	2026-01-12	2026-04-24	T	01:30 PM-02:45 PM	57	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	516
258	Spring	2026	6R	2026-01-12	2026-04-24	R	01:30 PM-02:45 PM	59	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	517
258	Spring	2026	7R	2026-01-12	2026-04-24	M	03:00 PM-03:50 PM	64	57	Samat Kassabek	8.522 -\ncap:72	518
258	Spring	2026	8R	2026-01-12	2026-04-24	W	03:00 PM-03:50 PM	61	57	Samat Kassabek	8.522 -\ncap:72	519
259	Spring	2026	1R	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	54	57	Bibinur\nShupeyeva	7.210 -\ncap:54	520
259	Spring	2026	2R	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	46	57	Bibinur\nShupeyeva	7.210 -\ncap:54	521
259	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	153	200	Manat Mustafa	Orange\nHall -\ncap:450	522
259	Spring	2026	2L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	202	210	Samat Kassabek	Orange\nHall -\ncap:450	523
259	Spring	2026	3L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	202	210	Yerlan Amanbek	Orange\nHall -\ncap:450	524
259	Spring	2026	4L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	208	210	Samat Kassabek	Orange\nHall -\ncap:450	525
259	Spring	2026	3R	2026-01-12	2026-04-24	M	04:00 PM-04:50 PM	57	57	Viktor Ten	8.522 -\ncap:72	526
259	Spring	2026	4R	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	52	57	Catalina\nTroshev	8.522 -\ncap:72	527
259	Spring	2026	5R	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	54	57	Catalina\nTroshev	8.522 -\ncap:72	528
259	Spring	2026	6R	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	57	57	Samat Kassabek	8.522 -\ncap:72	529
259	Spring	2026	7R	2026-01-12	2026-04-24	T	10:30 AM-11:45 AM	55	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	530
259	Spring	2026	8R	2026-01-12	2026-04-24	W	04:00 PM-04:50 PM	55	57	Viktor Ten	8.522 -\ncap:72	531
259	Spring	2026	9R	2026-01-12	2026-04-24	R	10:30 AM-11:45 AM	54	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	532
259	Spring	2026	10R	2026-01-12	2026-04-24	F	04:00 PM-04:50 PM	52	57	Viktor Ten	8.522 -\ncap:72	533
259	Spring	2026	11R	2026-01-12	2026-04-24	T	09:00 AM-10:15 AM	37	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	534
259	Spring	2026	12R	2026-01-12	2026-04-24	R	09:00 AM-10:15 AM	39	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	535
259	Spring	2026	13R	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	42	57	Khumoyun\nJabbarkhanov	8.522 -\ncap:72	536
259	Spring	2026	14R	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	56	57	Samat Kassabek	8.522 -\ncap:72	537
259	Spring	2026	15R	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	55	57	Samat Kassabek	8.522 -\ncap:72	538
260	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	67	90	Aigerim\nMadiyeva	7E.222 -\ncap:95	539
260	Spring	2026	2L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	72	90	Aigerim\nMadiyeva	7E.222 -\ncap:95	540
261	Spring	2026	1R	2026-01-12	2026-04-24	T	06:00 PM-06:50 PM	61	60	Bibinur\nShupeyeva	7E.222 -\ncap:95	541
261	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	61	60	Bibinur\nShupeyeva	7E.329 -\ncap:95	542
262	Spring	2026	1R	2026-01-12	2026-04-24	T	06:00 PM-06:50 PM	94	90	Viktor Ten	7E.329 -\ncap:95	543
262	Spring	2026	2L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	97	90	Ten, Viktor	7E.329 -\ncap:95	544
262	Spring	2026	2R	2026-01-12	2026-04-24	R	06:00 PM-06:50 PM	92	90	Ten, Viktor	7E.329 -\ncap:95	545
111	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	946
394	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	947
262	Spring	2026	3L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	89	90	Viktor Ten	7E.329 -\ncap:95	546
263	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	69	60	Achenef\nTesfahun	7E.222 -\ncap:95	547
263	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	60	60	Dongming Wei	7E.222 -\ncap:95	548
264	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	45	60	Manat Mustafa	7E.222 -\ncap:95	549
265	Spring	2026	1L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	70	70	Eunghyun Lee	7E.329 -\ncap:95	550
266	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	57	60	Bibinur\nShupeyeva	7E.222 -\ncap:95	551
267	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	54	54	Zhansaya\nTleuliyeva	7.210 -\ncap:54	552
267	Spring	2026	2L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	89	96	Zhansaya\nTleuliyeva	7E.222 -\ncap:95	553
267	Spring	2026	3L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	79	90	Zhansaya\nTleuliyeva	7E.222 -\ncap:95	554
267	Spring	2026	4L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	45	60	Aigerim\nMadiyeva	7E.329 -\ncap:95	555
268	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	55	60	Kerem Ugurlu	7E.222 -\ncap:95	556
269	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	76	75	Durvudkhan\nSuragan	7E.222 -\ncap:95	557
269	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	71	75	Durvudkhan\nSuragan	7E.329 -\ncap:95	558
270	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	21	54	Alejandro Javier\nCastro Castilla	7.210 -\ncap:54	559
270	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	57	60	Yerlan Amanbek	7E.329 -\ncap:95	560
271	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	72	60	Adilbek\nKairzhan	7E.222 -\ncap:95	561
271	Spring	2026	2L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	68	60	Adilbek\nKairzhan	7E.329 -\ncap:95	562
272	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	55	55	Adilet\nOtemissov	5E.438 -\ncap:82	563
273	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	56	55	Adilet\nOtemissov	7.210 -\ncap:54	564
274	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	64	70	Rustem\nTakhanov	7E.329 -\ncap:95	565
275	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	68	60	Dongming Wei	7E.329 -\ncap:95	566
276	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	72	55	Piotr Sebastian\nSkrzypacz	7E.329 -\ncap:95	567
277	Spring	2026	1L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	54	55	Kerem Ugurlu	7.210 -\ncap:54	568
278	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	10	55	Zhibek\nKadyrsizova	7.210 -\ncap:54	569
279	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	29	55	Eunghyun Lee	7.210 -\ncap:54	570
280	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	43	70	Zhibek\nKadyrsizova	7E.329 -\ncap:95	571
281	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	18	60	Amin Esfahani	7E.329 -\ncap:95	572
282	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	46	60	Andrey\nMelnikov	8.522 -\ncap:72	573
283	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	46	55	Achenef\nTesfahun	7.210 -\ncap:54	574
284	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	3	10	Alejandro Javier\nCastro Castilla	7E.220 -\ncap:56	575
285	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	5	5	Alejandro Javier\nCastro Castilla	7E.220 -\ncap:56	576
286	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	2	5	Alejandro Javier\nCastro Castilla	7E.220 -\ncap:56	577
287	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Eunghyun Lee	\N	578
288	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	2	1	Piotr Sebastian\nSkrzypacz	\N	579
289	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	35	30	Manat Mustafa	\N	580
290	Spring	2026	1L	2026-01-12	2026-04-24	W	12:00 PM-02:45 PM	15	20	Ata Akcil	6.302 -\ncap:44	581
290	Spring	2026	1Lb	2026-01-12	2026-04-24	R	12:00 PM-01:15 PM	15	20	Ata Akcil	6.302 -\ncap:44	582
291	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	9	12	Amoussou Coffi\nAdoko	6.419 -\ncap:24	583
292	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	17	20	Nasser\nMadaniesfahani	6.527 -\ncap:4	584
293	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	9	12	Saffet Yagiz	6.427 -\ncap:24	585
294	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	9	12	Fidelis\nSuorineni	6.519 -\ncap:26	586
295	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	9	12	Ali Mortazavi	6.427 -\ncap:24	587
296	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	6	15	Sergei Sabanov	6.522 -\ncap:35	588
297	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	11	15	Sergei Sabanov	6.522 -\ncap:35	589
298	Spring	2026	1P	2026-01-12	2026-04-24	F	03:00 PM-04:50 PM	9	15	Amoussou Coffi\nAdoko	6.522 -\ncap:35	590
299	Spring	2026	1L	2026-01-12	2026-04-24	M T	12:45 PM-02:00 PM	5	5	Nancy Stitt,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	591
300	Spring	2026	1L	2026-01-12	2026-04-24	M	10:00 AM-12:10 PM	42	42	Nancy Stitt,\nAssem\nZhakupova	NUSOM\nBuilding -\ncap:0	592
301	Spring	2026	1L	2026-01-12	2026-04-24	T	09:30 AM-12:30 PM	42	42	Nancy Stitt,\nYesbolat Sakko	NUSOM\nBuilding -\ncap:0	593
302	Spring	2026	1L	2026-01-12	2026-04-24	W	09:30 AM-12:30 PM	42	42	Joseph Almazan	NUSOM\nBuilding -\ncap:0	594
303	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:30 PM-02:40 PM	42	42	Paolo Colet	NUSOM\nBuilding -\ncap:0	595
304	Spring	2026	1ClinPract	2026-01-12	2026-04-24	W R	08:00 AM-03:50 PM	5	5	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	596
304	Spring	2026	1L	2026-01-12	2026-04-24	M T	09:00 AM-12:00 PM	5	5	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	597
305	Spring	2026	1ClinPract	2026-01-12	2026-04-24	F	08:00 AM-03:50 PM	5	5	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	598
305	Spring	2026	1L	2026-01-12	2026-04-24	M T	02:15 PM-03:45 PM	5	5	Ejercito Balay-\nOdao	NUSOM\nBuilding -\ncap:0	599
306	Spring	2026	1L	2026-01-12	2026-04-24	M W	05:00 PM-05:50 PM	5	5	Nancy Stitt	NUSOM\nBuilding -\ncap:0	600
307	Spring	2026	1L	2026-01-12	2026-04-24	W	10:00 AM-12:10 PM	35	35	Nancy Stitt,\nAnargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	601
308	Spring	2026	1L	2026-01-12	2026-04-24	M	10:00 AM-12:10 PM	35	35	Nancy Stitt,\nAnargul\nKuntuganova	NUSOM\nBuilding -\ncap:0	602
309	Spring	2026	1L	2026-01-12	2026-04-24	R	09:30 AM-12:30 PM	35	35	Nancy Stitt	NUSOM\nBuilding -\ncap:0	603
310	Spring	2026	1L	2026-01-12	2026-04-24	T	10:00 AM-12:10 PM	35	35	Paolo Colet	NUSOM\nBuilding -\ncap:0	604
311	Spring	2026	1ClinPract	2026-01-12	2026-04-24	T R F	08:00 AM-01:00 PM	3	3	Paolo Colet,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	605
311	Spring	2026	1L	2026-01-12	2026-04-24	W	10:00 AM-12:00 PM	3	3	Paolo Colet,\nAnargul\nKuntuganova,\nJonas Cruz	NUSOM\nBuilding -\ncap:0	606
312	Spring	2026	1L	2026-01-12	2026-04-24	M	01:00 PM-03:50 PM	3	3	Jonas Cruz	NUSOM\nBuilding -\ncap:0	607
313	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:00 PM-02:15 PM	141	150	Jeanette Kunz\nHalder	NUSOM\nBuilding -\ncap:0	608
313	Spring	2026	1Lb	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	22	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	609
313	Spring	2026	2Lb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	40	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	610
313	Spring	2026	3Lb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	40	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	611
313	Spring	2026	4Lb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	39	40	Kamilya Kokabi,\nAgata Natasza\nBurska, Assem\nZhakupova,\nKamila Raziyeva	NUSOM\nBuilding -\ncap:0	612
314	Spring	2026	1P	2026-01-12	2026-04-24	M W	09:00 AM-01:50 PM	50	50	Larisa Lezina	NUSOM\nBuilding -\ncap:0	613
315	Spring	2026	1L	2026-01-05	2026-02-06	M T W R F	09:00 AM-12:00 PM	30	31	Matthew\nNaanlep Tanko	NUSOM\nBuilding -\ncap:0	614
316	Spring	2026	1L	2026-02-09	2026-03-11	M T W R F	09:00 AM-12:00 PM	30	31	Denis Bulanin,\nNikolai Barlev	NUSOM\nBuilding -\ncap:0	615
317	Spring	2026	1L	2026-03-12	2026-04-25	M T W R F	09:00 AM-12:00 PM	31	32	Sanja Terzic,\nSyed Hani\nHassan Abidi	NUSOM\nBuilding -\ncap:0	616
318	Spring	2026	1L	2025-10-14	2026-03-17	T	01:00 PM-05:00 PM	28	31	Vitaliy Sazonov	NUSOM\nBuilding -\ncap:0	617
319	Spring	2026	1L	2026-01-05	2026-05-04	M	01:00 PM-04:00 PM	28	31	Alessandra\nClementi,\nLyazzat\nToleubekova	NUSOM\nBuilding -\ncap:0	618
320	Spring	2026	1L	2026-01-07	2026-05-06	W	01:00 PM-04:00 PM	28	31	Yesbolat Sakko	NUSOM\nBuilding -\ncap:0	619
321	Spring	2026	1L	2026-03-31	2026-04-28	T	01:00 PM-04:30 PM	28	31	Vitaliy Sazonov	NUSOM\nBuilding -\ncap:0	620
322	Spring	2026	1L	2026-01-12	2026-04-24	F	09:30 AM-12:30 PM	44	50	Mirat Akshalov,\nNarendra Singh	(C3) 1009 -\ncap:70	621
323	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	02:00 PM-02:50 PM	25	24	Marzieh Sadat\nRazavi	8.508 -\ncap:24	622
323	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	12:00 PM-12:50 PM	24	24	Marzieh Sadat\nRazavi	8.508 -\ncap:24	623
324	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	03:00 PM-03:50 PM	5	24	Marzieh Sadat\nRazavi	8.508 -\ncap:24	624
325	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	18	30	Peyman\nPourafshary	6.507 -\ncap:72	625
326	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	21	30	Irawan Sonny	6.105 -\ncap:64	626
326	Spring	2026	1Lb	2026-01-12	2026-04-24	M	02:00 PM-04:50 PM	21	30	Irawan Sonny	6.141 -\ncap:15	627
327	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	25	30	Ali Shafiei	6.105 -\ncap:64	628
327	Spring	2026	1Lb	2026-01-12	2026-04-24	W	01:00 PM-03:50 PM	25	30	Ali Shafiei	6.105 -\ncap:64	629
328	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	26	30	Masoud Riazi	6.105 -\ncap:64	630
329	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	26	30	Randy Hazlett	6.105 -\ncap:64	631
330	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	29	30	Shams Kalam	6.507 -\ncap:72	632
331	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	24	30	Mian Umer\nShafiq	6.422 -\ncap:28	633
332	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	16	30	Ali Shafiei	6.302 -\ncap:44	634
333	Spring	2026	1IS	2026-01-12	2026-04-24	W	11:00 AM-01:50 PM	18	30	Mian Umer\nShafiq	6.527 -\ncap:4	635
334	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	27	28	Bakinaz Abdalla	8.422A -\ncap:32	636
335	Spring	2026	7S	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	49	50	Matthew\nHeeney	2.307 -\ncap:75	637
335	Spring	2026	9S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	38	50	Mihnea Capraru	2.307 -\ncap:75	638
335	Spring	2026	10S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	27	50	Mihnea Capraru	2.307 -\ncap:75	639
335	Spring	2026	12S	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	46	50	Matthew\nHeeney	2.307 -\ncap:75	640
335	Spring	2026	6S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	35	50	Chandler Hatch	2.407 -\ncap:85	641
335	Spring	2026	1S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	50	50	Siegfried Van\nDuffel	9.105 -\ncap:68	642
335	Spring	2026	15S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	31	50	Mihnea Capraru	9.105 -\ncap:68	643
335	Spring	2026	3S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	38	40	Donovan Cox	5E.438 -\ncap:82	644
335	Spring	2026	4S	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	40	40	Donovan Cox	5E.438 -\ncap:82	645
335	Spring	2026	8S	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	38	40	Donovan Cox	5E.438 -\ncap:82	646
335	Spring	2026	14S	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	37	50	Ted Parent	5E.438 -\ncap:82	647
335	Spring	2026	16S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	41	50	James\nHutchinson	5E.438 -\ncap:82	648
335	Spring	2026	17S	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	48	50	Donovan Cox	5E.438 -\ncap:82	649
336	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	25	28	Mihnea Capraru	8.154 -\ncap:56	650
337	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	25	24	James\nHutchinson	8.305 -\ncap:30	651
338	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	22	24	Ted Parent	7E.125/1 -\ncap:36	652
339	Spring	2026	2PLb	2026-01-12	2026-04-24	M	12:00 PM-02:50 PM	31	33	Mereke\nTontayeva	7.302 -\ncap:30	653
339	Spring	2026	3PLb	2026-01-12	2026-04-24	T	09:00 AM-11:50 AM	15	33	Mereke\nTontayeva	7.302 -\ncap:30	654
339	Spring	2026	4PLb	2026-01-12	2026-04-24	T	12:00 PM-02:50 PM	24	33	Mereke\nTontayeva	7.302 -\ncap:30	655
339	Spring	2026	5PLb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	20	33	Mereke\nTontayeva	7.302 -\ncap:30	656
339	Spring	2026	6PLb	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	21	33	Mereke\nTontayeva	7.302 -\ncap:30	657
339	Spring	2026	7PLb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	22	33	Mereke\nTontayeva	7.302 -\ncap:30	658
339	Spring	2026	8PLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	21	33	Mereke\nTontayeva	7.302 -\ncap:30	659
339	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	154	240	Ernazar\nAbdikamalov	Orange\nHall -\ncap:450	660
339	Spring	2026	2R	2026-01-12	2026-04-24	M	11:00 AM-11:50 AM	16	60	Omid Farzadian	7E.125/2 -\ncap:56	661
339	Spring	2026	3R	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	45	60	Omid Farzadian	7E.125/2 -\ncap:56	662
339	Spring	2026	4R	2026-01-12	2026-04-24	F	01:00 PM-01:50 PM	49	60	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	663
339	Spring	2026	5R	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	44	60	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	664
340	Spring	2026	1PLb	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	665
340	Spring	2026	2PLb	2026-01-12	2026-04-24	M	12:00 PM-02:50 PM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	666
340	Spring	2026	3PLb	2026-01-12	2026-04-24	T	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	667
340	Spring	2026	4PLb	2026-01-12	2026-04-24	T	12:00 PM-02:50 PM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	668
458	Fall	2025	\N	\N	\N	\N	\N	\N	\N	\N	\N	948
340	Spring	2026	5PLb	2026-01-12	2026-04-24	T	03:00 PM-05:50 PM	33	36	Mereke\nTontayeva	9.202 -\ncap:40	669
340	Spring	2026	6PLb	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	33	36	Mereke\nTontayeva	9.202 -\ncap:40	670
340	Spring	2026	7PLb	2026-01-12	2026-04-24	W	12:00 PM-02:50 PM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	671
340	Spring	2026	8PLb	2026-01-12	2026-04-24	R	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	672
340	Spring	2026	9PLb	2026-01-12	2026-04-24	R	12:00 PM-02:50 PM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	673
340	Spring	2026	10PLb	2026-01-12	2026-04-24	F	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	674
340	Spring	2026	12PLb	2026-01-12	2026-04-24	M	03:00 PM-05:50 PM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	675
340	Spring	2026	16PLb	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	34	36	Mereke\nTontayeva	9.202 -\ncap:40	676
340	Spring	2026	17PLb	2026-01-12	2026-04-24	R	03:00 PM-05:50 PM	36	36	Mereke\nTontayeva	9.202 -\ncap:40	677
340	Spring	2026	19PLb	2026-01-12	2026-04-24	F	12:00 PM-02:50 PM	35	36	Mereke\nTontayeva	9.202 -\ncap:40	678
340	Spring	2026	11PLb	2026-01-12	2026-04-24	M	09:00 AM-11:50 AM	30	36	Mereke\nTontayeva	9.222 -\ncap:40	679
340	Spring	2026	13PLb	2026-01-12	2026-04-24	T	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.222 -\ncap:40	680
340	Spring	2026	14PLb	2026-01-12	2026-04-24	R	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.222 -\ncap:40	681
340	Spring	2026	15PLb	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	36	36	Mereke\nTontayeva	9.222 -\ncap:40	682
340	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	218	230	Askhat\nJumabekov	Orange\nHall -\ncap:450	683
340	Spring	2026	2L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	185	230	Kyunghwan Oh	Orange\nHall -\ncap:450	684
340	Spring	2026	3L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	226	230	Marat Kaikanov	Orange\nHall -\ncap:450	685
340	Spring	2026	1R	2026-01-12	2026-04-24	M	09:00 AM-09:50 AM	51	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	686
340	Spring	2026	2R	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	62	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	687
340	Spring	2026	3R	2026-01-12	2026-04-24	M	12:00 PM-12:50 PM	66	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	688
340	Spring	2026	5R	2026-01-12	2026-04-24	W	09:00 AM-09:50 AM	61	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	689
340	Spring	2026	6R	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	64	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	690
340	Spring	2026	7R	2026-01-12	2026-04-24	W	12:00 PM-12:50 PM	65	66	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	691
340	Spring	2026	8R	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	62	66	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	692
340	Spring	2026	9R	2026-01-12	2026-04-24	F	09:00 AM-09:50 AM	66	66	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	693
340	Spring	2026	10R	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	66	66	Bekdaulet\nShukirgaliyev	7E.125/2 -\ncap:56	694
340	Spring	2026	11R	2026-01-12	2026-04-24	M	02:00 PM-02:50 PM	66	66	Ainur\nKoshkinbayeva	7E.125/2 -\ncap:56	695
341	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	42	55	Dana Alina	7E.125/2 -\ncap:56	696
342	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	14	24	Rayner\nRodriguez\nGuzman	7.507 -\ncap:48	697
342	Spring	2026	1R	2026-01-12	2026-04-24	W	02:00 PM-02:50 PM	14	15	Rayner\nRodriguez\nGuzman	7.507 -\ncap:48	698
343	Spring	2026	1CLb	2026-01-12	2026-04-24	T	06:00 PM-07:15 PM	25	24	Ernazar\nAbdikamalov,\nDana Alina	7.507 -\ncap:48	699
343	Spring	2026	1L	2026-01-12	2026-04-24	T	04:30 PM-05:45 PM	25	24	Ernazar\nAbdikamalov,\nDana Alina	7.507 -\ncap:48	700
344	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	20	24	Zhandos\nUtegulov	7.507 -\ncap:48	701
344	Spring	2026	1R	2026-01-12	2026-04-24	R	03:00 PM-04:15 PM	20	24	Zhandos\nUtegulov	7.507 -\ncap:48	702
345	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	6	24	Bakhtiyar\nOrazbayev	7.507 -\ncap:48	703
345	Spring	2026	1R	2026-01-12	2026-04-24	W	01:00 PM-01:50 PM	6	24	Bakhtiyar\nOrazbayev	7.507 -\ncap:48	704
346	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	9	24	Alexander\nTikhonov	7.507 -\ncap:48	705
346	Spring	2026	1Lb	2026-01-12	2026-04-24	R	04:30 PM-07:15 PM	9	24	Alexander\nTikhonov,\nBekdaulet\nShukirgaliyev	7.502 -\ncap:24	706
347	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	6	24	Sergiy Bubin	7.507 -\ncap:48	707
347	Spring	2026	1R	2026-01-12	2026-04-24	T	12:00 PM-01:15 PM	6	20	Sergiy Bubin	7.507 -\ncap:48	708
348	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	4	24	Daniele\nMalafarina	7.507 -\ncap:48	709
349	Spring	2026	1IS	2026-01-12	2026-04-24	\N	Online/Distant	8	24	Anton\nDesyatnikov	\N	710
350	Spring	2026	1R	2026-01-12	2026-04-24	\N	Online/Distant	8	24	Daniele\nMalafarina	\N	711
351	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	86	80	Neil Collins	Green Hall -\ncap:231	712
352	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	82	120	Caress Schenk	Green Hall -\ncap:231	713
353	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	86	120	Bimal Adhikari	Green Hall -\ncap:231	714
354	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	24	29	Dinara\nPisareva,\nAndrey\nSemenov	8.321 -\ncap:32	715
354	Spring	2026	2L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	26	29	Dinara\nPisareva,\nAndrey\nSemenov	8.321 -\ncap:32	716
355	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	17	24	Ho Koh	8.321 -\ncap:32	717
355	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	28	24	Jessica Neafie	6.522 -\ncap:35	718
356	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	15	18	Chunho Park	8.308 -\ncap:24	719
357	Spring	2026	1L	2026-01-12	2026-04-24	F	01:00 PM-03:50 PM	11	10	Brian Smith	8.317 -\ncap:28	720
358	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	22	18	Dinara\nPisareva,\nAndrey\nSemenov	8.321 -\ncap:32	721
359	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	19	18	Maja Savevska	8.308 -\ncap:24	722
360	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	20	18	Maja Savevska	8.308 -\ncap:24	723
361	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	17	18	Berikbol\nDukeyev	8.321 -\ncap:32	724
362	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	18	18	Sabina\nInsebayeva	8.321 -\ncap:32	725
363	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	11	18	Alexei Trochev	8.308 -\ncap:24	726
364	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	24	18	Neil Collins	8.308 -\ncap:24	727
365	Spring	2026	1L	2026-01-12	2026-04-24	T	10:30 AM-01:15 PM	15	18	Chun Young\nPark	7.210 -\ncap:54	728
366	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Bimal Adhikari	\N	729
366	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Helene Thibault	\N	730
366	Spring	2026	3L	2026-01-12	2026-04-24	\N	Online/Distant	3	5	Neil Collins	\N	731
367	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	10	14	Chunho Park	8.308 -\ncap:24	732
368	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	12	14	Elmira\nJoldybayeva	8.308 -\ncap:24	733
369	Spring	2026	1S	2026-01-12	2026-04-24	W	03:00 PM-05:50 PM	6	6	Helene Thibault	8.302 -\ncap:57	734
370	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	15	14	Ho Koh	8.308 -\ncap:24	735
371	Spring	2026	1S	2026-01-12	2026-04-24	R	10:30 AM-01:15 PM	14	14	Chun Young\nPark	7.210 -\ncap:54	736
372	Spring	2026	1L	2026-01-12	2026-04-24	M	11:00 AM-01:50 PM	13	14	Sabina\nInsebayeva	5E.438 -\ncap:82	737
373	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Bimal Adhikari	\N	738
373	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	4	5	Jessica Neafie	\N	739
373	Spring	2026	3Int	2026-01-12	2026-04-24	\N	Online/Distant	3	6	Alexei Trochev	\N	740
373	Spring	2026	4Int	2026-01-12	2026-04-24	\N	Online/Distant	4	5	Maja Savevska	\N	741
374	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	09:00 AM-09:50 AM	16	24	Katarzyna Galaj	8.508 -\ncap:24	742
374	Spring	2026	3L	2026-01-12	2026-04-24	M T W R	10:00 AM-10:50 AM	12	24	Katarzyna Galaj	8.508 -\ncap:24	743
375	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	11:00 AM-11:50 AM	13	24	Katarzyna Galaj	8.508 -\ncap:24	744
376	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	14	22	Katherine\nErdman	8.105 -\ncap:56	745
377	Spring	2026	1L	2026-01-12	2026-04-24	M W	03:30 PM-05:00 PM	2	5	Elvira\nYavorskaya	8.322B -\ncap:24	746
378	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	4	10	Aleksandr\nGrishin	8.322B -\ncap:24	747
379	Spring	2026	1L	2026-01-12	2026-04-24	T R	11:00 AM-12:15 PM	5	10	Yuliya\nKozitskaya	8.322B -\ncap:24	748
380	Spring	2026	1S	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	2	10	Meiramgul\nKussainova	8.322B -\ncap:24	749
381	Spring	2026	1L	2026-01-12	2026-04-24	M W	02:00 PM-03:15 PM	3	10	Sabina\nInsebayeva	8.322B -\ncap:24	750
382	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	37	36	Matteo\nRubagotti	7.246 -\ncap:48	751
383	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	33	36	Ton Duc Do	7.246 -\ncap:48	752
383	Spring	2026	1Lb	2026-01-12	2026-04-24	T	12:00 PM-02:45 PM	15	20	Ahmad\nAlhassan	7.327 -\ncap:48	753
383	Spring	2026	2Lb	2026-01-12	2026-04-24	T	03:00 PM-05:45 PM	18	20	Ahmad\nAlhassan	7.327 -\ncap:48	754
384	Spring	2026	3Lb	2026-01-12	2026-04-24	M	04:00 PM-06:00 PM	38	36	Togzhan\nSyrymova	7.327 -\ncap:48	755
384	Spring	2026	4Lb	2026-01-12	2026-04-24	T	10:00 AM-12:00 PM	31	32	Anara\nSandygulova	7.327 -\ncap:48	756
384	Spring	2026	5Lb	2026-01-12	2026-04-24	W	10:00 AM-12:00 PM	32	32	Zhanat\nKappassov	7.327 -\ncap:48	757
384	Spring	2026	6Lb	2026-01-12	2026-04-24	W	12:00 PM-02:00 PM	37	36	Zhanat\nKappassov	7.327 -\ncap:48	758
384	Spring	2026	7Lb	2026-01-12	2026-04-24	R	09:00 AM-11:00 AM	23	32	Anara\nSandygulova	7.327 -\ncap:48	759
384	Spring	2026	10Lb	2026-01-12	2026-04-24	F	04:00 PM-06:00 PM	36	36	Togzhan\nSyrymova	7.327 -\ncap:48	760
384	Spring	2026	11Lb	2026-01-12	2026-04-24	R	11:00 AM-01:00 PM	37	36	Anara\nSandygulova	7.327 -\ncap:48	761
384	Spring	2026	12Lb	2026-01-12	2026-04-24	F	09:00 AM-11:00 AM	32	32	Anara\nSandygulova	7.327 -\ncap:48	762
384	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	80	90	Togzhan\nSyrymova	online -\ncap:0	763
384	Spring	2026	2L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	54	90	Togzhan\nSyrymova	online -\ncap:0	764
384	Spring	2026	4L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	132	130	Azamat\nYeshmukhamet\nov	online -\ncap:0	765
385	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	27	36	Aibek\nNiyetkaliyev	7.246 -\ncap:48	766
385	Spring	2026	1Lb	2026-01-12	2026-04-24	R	03:00 PM-05:45 PM	18	18	Aibek\nNiyetkaliyev	7.327 -\ncap:48	767
385	Spring	2026	2Lb	2026-01-12	2026-04-24	W	03:00 PM-05:45 PM	9	18	Aibek\nNiyetkaliyev	7.327 -\ncap:48	768
386	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	17	18	Tohid Alizadeh	7E.230 -\ncap:24	769
387	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	27	32	Michele\nFolgheraiter	7.246 -\ncap:48	770
388	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	25	32	Anara\nSandygulova	7.246 -\ncap:48	771
389	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	16	32	Almas\nShintemirov	7.322 -\ncap:24	772
390	Spring	2026	1P	2026-01-12	2026-04-24	\N	Online/Distant	16	32	Togzhan\nSyrymova	\N	773
390	Spring	2026	2P	2026-01-12	2026-04-24	\N	Online/Distant	1	2	Togzhan\nSyrymova	\N	774
391	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	20	20	Zauresh\nAtakhanova	6.105 -\ncap:64	775
392	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	103	100	Karina\nMatkarimova	\N	776
392	Spring	2026	1S	2026-01-12	2026-04-24	M	10:00 AM-10:50 AM	26	25	Ana Cristina\nHenriques\nMarques	8.310 -\ncap:27	777
392	Spring	2026	2S	2026-01-12	2026-04-24	M	11:00 AM-11:50 AM	26	25	Ana Cristina\nHenriques\nMarques	8.310 -\ncap:27	778
392	Spring	2026	3S	2026-01-12	2026-04-24	W	10:00 AM-10:50 AM	27	25	Karina\nMatkarimova	8.310 -\ncap:27	779
392	Spring	2026	4S	2026-01-12	2026-04-24	W	11:00 AM-11:50 AM	24	25	Karina\nMatkarimova	8.310 -\ncap:27	780
393	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	28	27	Dana\nBurkhanova	8.310 -\ncap:27	781
393	Spring	2026	3L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	30	27	Matvey\nLomonosov	8.307 -\ncap:55	782
394	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	25	25	Darkhan\nMedeuov	6.522 -\ncap:35	783
395	Spring	2026	1L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	26	26	Ana Cristina\nHenriques\nMarques	8.422A -\ncap:32	784
396	Spring	2026	1L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	27	27	Saltanat\nAkhmetova	8.310 -\ncap:27	785
397	Spring	2026	1L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	27	25	Darkhan\nMedeuov	8.310 -\ncap:27	786
397	Spring	2026	2L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	25	25	Darkhan\nMedeuov	8.310 -\ncap:27	787
398	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	28	27	Dana\nBurkhanova	8.154 -\ncap:56	788
398	Spring	2026	2L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	25	27	Mikhail Sokolov	8.154 -\ncap:56	789
399	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	24	22	Ana Cristina\nHenriques\nMarques	8.154 -\ncap:56	790
400	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	27	27	Karina\nMatkarimova	8.310 -\ncap:27	791
401	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	25	26	Gavin Slade	8.310 -\ncap:27	792
402	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Dana\nBurkhanova	\N	793
402	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Matvey\nLomonosov	\N	794
403	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	3	5	Matvey\nLomonosov	\N	795
404	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	1	5	Matvey\nLomonosov	\N	796
405	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	26	26	Saltanat\nAkhmetova	8.310 -\ncap:27	797
406	Spring	2026	1L	2026-01-12	2026-04-24	W	05:00 PM-07:50 PM	26	26	Gavin Slade	8.154 -\ncap:56	798
407	Spring	2026	1L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	20	26	Mikhail Sokolov	8.154 -\ncap:56	799
408	Spring	2026	1S	2026-01-12	2026-04-24	W	09:00 AM-11:50 AM	18	25	Dana\nBurkhanova	8.154 -\ncap:56	800
409	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	12:00 PM-12:50 PM	24	24	Arturo Bellido	8.317 -\ncap:28	801
409	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	09:00 AM-09:50 AM	18	24	Edyta Denst-\nGarcia	8.305 -\ncap:30	802
409	Spring	2026	3L	2026-01-12	2026-04-24	M T W R	10:00 AM-10:50 AM	11	24	Edyta Denst-\nGarcia	8.305 -\ncap:30	803
410	Spring	2026	1L	2026-01-12	2026-04-24	M T W R	01:00 PM-01:50 PM	14	24	Arturo Bellido	8.317 -\ncap:28	804
410	Spring	2026	2L	2026-01-12	2026-04-24	M T W R	02:00 PM-02:50 PM	19	24	Arturo Bellido	8.317 -\ncap:28	805
411	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	29	24	Edyta Denst-\nGarcia	8.322A -\ncap:32	806
412	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	47	50	Daniel Beben	\N	807
413	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	41	50	Daniel Beben	\N	808
414	Spring	2026	1L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	43	40	Halit Akarca	8.105 -\ncap:56	809
415	Spring	2026	1L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	28	30	Wulidanayi\nJumabay	2.407 -\ncap:85	810
416	Spring	2026	1L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	37	35	Funda Guven	8.302 -\ncap:57	811
417	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	31	35	Funda Guven	8.302 -\ncap:57	812
418	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	34	35	Wulidanayi\nJumabay	2.407 -\ncap:85	813
419	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	10	24	Uli Schamiloglu	8.105 -\ncap:56	814
420	Spring	2026	1L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	75	75	Brandon Brock,\nBellido\nLanguasco	7E.429 -\ncap:90	815
421	Spring	2026	5L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	18	20	Jane Hoelker	6.419 -\ncap:24	816
421	Spring	2026	15L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	21	20	Olga Campbell-\nThomson	6.410 -\ncap:24	817
421	Spring	2026	16L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	19	20	Olga Campbell-\nThomson	6.410 -\ncap:24	818
421	Spring	2026	30L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	20	20	Marina Zaffari	6.410 -\ncap:24	819
421	Spring	2026	31L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	19	20	Marina Zaffari	6.410 -\ncap:24	820
421	Spring	2026	32L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	19	20	Marina Zaffari	6.410 -\ncap:24	821
421	Spring	2026	9L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	7	20	Nicholas\nWalmsley	6.402 -\ncap:24	822
421	Spring	2026	10L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	14	20	Nicholas\nWalmsley	6.402 -\ncap:24	823
421	Spring	2026	11L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	20	20	J.C. Ross	6.402 -\ncap:24	824
421	Spring	2026	12L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	20	20	J.C. Ross	6.402 -\ncap:24	825
421	Spring	2026	13L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	20	20	J.C. Ross	6.402 -\ncap:24	826
421	Spring	2026	14L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	20	20	Jeremy Richard\nSpring	6.402 -\ncap:24	827
421	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	17	20	Bellido\nLanguasco	7.427 -\ncap:23	828
421	Spring	2026	2L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	8	20	Bellido\nLanguasco	7.427 -\ncap:23	829
421	Spring	2026	3L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	17	20	Elizabeth Abele	7.427 -\ncap:23	830
421	Spring	2026	4L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	19	20	Elizabeth Abele	7.427 -\ncap:23	831
421	Spring	2026	17L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	16	20	Michael Jones	7.427 -\ncap:23	832
421	Spring	2026	36L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	20	20	Ian Albert\nPeterkin Jr	7.427 -\ncap:23	833
421	Spring	2026	37L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	20	20	Ian Albert\nPeterkin Jr	7.427 -\ncap:23	834
421	Spring	2026	34L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	20	20	Shahreen Binti\nMat Nayan	7.517 -\ncap:25	835
421	Spring	2026	35L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	20	20	Shahreen Binti\nMat Nayan	7.517 -\ncap:25	836
421	Spring	2026	18L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	20	20	Fariza Tolesh	7.527 -\ncap:24	837
421	Spring	2026	19L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	20	20	Fariza Tolesh	7.527 -\ncap:24	838
421	Spring	2026	20L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	19	20	Fariza Tolesh	7.527 -\ncap:24	839
421	Spring	2026	27L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	19	20	Gulden Issina	7.527 -\ncap:24	840
421	Spring	2026	28L	2026-01-12	2026-04-24	M W F	10:00 AM-10:50 AM	19	20	Gulden Issina	7.527 -\ncap:24	841
421	Spring	2026	29L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	20	20	Gulden Issina	7.527 -\ncap:24	842
421	Spring	2026	38L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	20	20	Adam Hefty	7.527 -\ncap:24	843
421	Spring	2026	33L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	20	20	Andrew\nDrybrough	8.141 -\ncap:24	844
421	Spring	2026	21L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	20	20	Benjamin\nGibbon	8.140 -\ncap:24	845
421	Spring	2026	22L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	20	20	Benjamin\nGibbon	8.140 -\ncap:24	846
421	Spring	2026	23L	2026-01-12	2026-04-24	M W F	06:00 PM-06:50 PM	20	20	Benjamin\nGibbon	8.140 -\ncap:24	847
421	Spring	2026	24L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	20	20	Nurly Marshal	8.140 -\ncap:24	848
421	Spring	2026	25L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	20	20	Nurly Marshal	8.140 -\ncap:24	849
421	Spring	2026	26L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	20	20	Nurly Marshal	8.140 -\ncap:24	850
421	Spring	2026	39L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	20	20	James Nielsen	8.140 -\ncap:24	851
422	Spring	2026	10L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	24	24	Yamen Rahvan	6.402 -\ncap:24	852
422	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	24	24	Tiffany Moore	7.427 -\ncap:23	853
422	Spring	2026	4L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	23	24	Tiffany Moore	7.427 -\ncap:23	854
422	Spring	2026	5L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	24	24	Samira Esat	7.427 -\ncap:23	855
422	Spring	2026	6L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	24	24	Samira Esat	7.427 -\ncap:23	856
422	Spring	2026	9L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	24	24	Samira Esat	7.427 -\ncap:23	857
422	Spring	2026	7L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	24	24	Thomas Carl\nHughes	7.527 -\ncap:24	858
422	Spring	2026	8L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	23	24	Thomas Carl\nHughes	7.527 -\ncap:24	859
423	Spring	2026	1L	2026-01-12	2026-04-24	M W F	01:00 PM-01:50 PM	19	30	Elizabeth Abele	8.327 -\ncap:58	860
424	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	31	30	Marilyn Plumlee	2.105 -\ncap:64	861
425	Spring	2026	3L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	24	24	James Nielsen	6.410 -\ncap:24	862
425	Spring	2026	4L	2026-01-12	2026-04-24	M W F	05:00 PM-05:50 PM	24	24	James Nielsen	6.410 -\ncap:24	863
425	Spring	2026	9L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	24	24	Carlos Abaunza	6.402 -\ncap:24	864
425	Spring	2026	10L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	25	24	Carlos Abaunza	6.402 -\ncap:24	865
425	Spring	2026	11L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	23	24	Bakhtiar\nNaghdipour	7.246 -\ncap:48	866
425	Spring	2026	6L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	24	24	Gamze Oncul	2.322 -\ncap:45	867
425	Spring	2026	7L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	22	24	Gamze Oncul	2.322 -\ncap:45	868
425	Spring	2026	8L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	23	24	Gamze Oncul	2.322 -\ncap:45	869
426	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	22	24	Adam Hefty	7.527 -\ncap:24	870
426	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	23	24	Adam Hefty	7.527 -\ncap:24	871
427	Spring	2026	2L	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	25	24	Marilyn Plumlee	7.246 -\ncap:48	872
427	Spring	2026	1L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	21	24	Zhanar\nKabylbekova	7.527 -\ncap:24	873
427	Spring	2026	3L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	23	24	Zhanar\nKabylbekova	7.527 -\ncap:24	874
428	Spring	2026	2L	2026-01-12	2026-04-24	T R	03:00 PM-04:15 PM	20	24	Brandon Brock	7E.217 -\ncap:24	875
428	Spring	2026	3L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	22	24	Michael Jones	7E.217 -\ncap:24	876
428	Spring	2026	4L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	24	24	James Swider	7E.217 -\ncap:24	877
428	Spring	2026	5L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	23	24	James Swider	7E.217 -\ncap:24	878
428	Spring	2026	6L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	21	24	Shahreen Binti\nMat Nayan	7E.217 -\ncap:24	879
429	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	18	20	Arlyce Menzies	\N	880
429	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	20	20	Arlyce Menzies	\N	881
429	Spring	2026	3L	2026-01-12	2026-04-24	M W F	09:00 AM-09:50 AM	11	20	Nicholas\nWalmsley	6.402 -\ncap:24	882
430	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	35	36	Thomas Duke	8.327 -\ncap:58	883
430	Spring	2026	3L	2026-01-12	2026-04-24	M W F	03:00 PM-03:50 PM	36	36	Thomas Carl\nHughes	8.327 -\ncap:58	884
430	Spring	2026	2L	2026-01-12	2026-04-24	T R	01:30 PM-02:45 PM	36	36	Yamen Rahvan	9.105 -\ncap:68	885
430	Spring	2026	4L	2026-01-12	2026-04-24	M W F	04:00 PM-04:50 PM	36	36	Tiffany Moore	7.105 -\ncap:75	886
431	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Thomas Duke	\N	887
432	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	6	5	Thomas Duke	\N	888
433	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Brandon Brock	\N	889
434	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	3	5	Brandon Brock	\N	890
435	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	17	16	Marilyn Plumlee	2.105 -\ncap:64	891
436	Spring	2026	1Int	2026-01-12	2026-04-24	S	09:00 AM-10:15 AM	9	5	James Swider	online -\ncap:0	892
437	Spring	2026	1Int	2026-01-12	2026-04-24	S	09:00 AM-10:15 AM	5	5	James Swider	online -\ncap:0	893
438	Spring	2026	1S	2026-01-12	2026-04-24	F	10:00 AM-10:50 AM	25	25	Ivan Delazari	8.305 -\ncap:30	894
438	Spring	2026	2S	2026-01-12	2026-04-24	F	11:00 AM-11:50 AM	26	25	Ivan Delazari	8.305 -\ncap:30	895
438	Spring	2026	3S	2026-01-12	2026-04-24	F	02:00 PM-02:50 PM	27	25	Ivan Delazari	8.305 -\ncap:30	896
438	Spring	2026	4S	2026-01-12	2026-04-24	F	03:00 PM-03:50 PM	25	25	Ivan Delazari	8.305 -\ncap:30	897
438	Spring	2026	1L	2026-01-12	2026-04-24	M W	02:00 PM-02:50 PM	103	100	Ivan Delazari	Blue Hall -\ncap:239	898
439	Spring	2026	1L	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	30	28	Maria Rybakova	8.422A -\ncap:32	899
440	Spring	2026	1L	2026-01-12	2026-04-24	T R	10:30 AM-11:45 AM	18	20	Jonathan Dupuy	6.410 -\ncap:24	900
440	Spring	2026	3L	2026-01-12	2026-04-24	T R	09:00 AM-10:15 AM	18	20	Jonathan Dupuy	6.410 -\ncap:24	901
440	Spring	2026	4L	2026-01-12	2026-04-24	M W F	02:00 PM-02:50 PM	20	20	Ian Albert\nPeterkin Jr	7.246 -\ncap:48	902
441	Spring	2026	1S	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	28	28	Gabriel\nMcGuire	8.322A -\ncap:32	903
442	Spring	2026	1L	2026-01-12	2026-04-24	M W F	11:00 AM-11:50 AM	25	28	Yuliya\nKozitskaya	8.422A -\ncap:32	904
443	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	26	25	Maria Rybakova	8.422A -\ncap:32	905
444	Spring	2026	1L	2026-01-12	2026-04-24	M W F	12:00 PM-12:50 PM	23	26	Yuliya\nKozitskaya	8.422A -\ncap:32	906
445	Spring	2026	1L	2026-01-12	2026-04-24	T R	07:30 PM-08:45 PM	20	21	Matthew\nHeeney	6.302 -\ncap:44	907
446	Spring	2026	1L	2026-01-12	2026-04-24	\N	Online/Distant	13	15	Florian\nKuechler	\N	908
446	Spring	2026	2L	2026-01-12	2026-04-24	\N	Online/Distant	5	5	Marzieh Sadat\nRazavi	\N	909
447	Spring	2026	1Int	2026-01-12	2026-04-24	\N	Online/Distant	8	10	Yuliya\nKozitskaya	\N	910
447	Spring	2026	2Int	2026-01-12	2026-04-24	\N	Online/Distant	2	5	Andrey\nFilchenko	\N	911
448	Spring	2026	1L	2026-01-12	2026-04-24	T R	06:00 PM-07:15 PM	31	26	Jenni Lehtinen	8.302 -\ncap:57	912
449	Spring	2026	1S	2026-01-12	2026-04-24	T R	12:00 PM-01:15 PM	15	12	Jonathan Dupuy	6.410 -\ncap:24	913
450	Spring	2026	1CP	2026-01-12	2026-04-24	T R	04:30 PM-05:45 PM	20	20	Amanda\nMurphy	8.322A -\ncap:32	914
258	Fall	2022	\N	\N	\N	\N	\N	\N	\N	\N	\N	915
339	Fall	2022	\N	\N	\N	\N	\N	\N	\N	\N	\N	916
104	Fall	2022	\N	\N	\N	\N	\N	\N	\N	\N	\N	917
421	Fall	2022	\N	\N	\N	\N	\N	\N	\N	\N	\N	918
259	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	919
188	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	920
209	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	921
105	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	922
340	Spring	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	923
451	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	924
260	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	925
262	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	926
452	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	927
427	Fall	2023	\N	\N	\N	\N	\N	\N	\N	\N	\N	928
108	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	929
109	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	930
384	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	931
267	Spring	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	932
116	Summer	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	933
453	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	934
218	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	935
49	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	936
454	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	937
24	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	938
455	Fall	2024	\N	\N	\N	\N	\N	\N	\N	\N	\N	939
\.


--
-- Data for Name: course_reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.course_reviews (course_id, user_id, comment, overall_rating, difficulty, informativeness, gpa_boost, workload, id, created_at, updated_at) FROM stdin;
1	2	The best course i have ever take	5	3	5	2	2	1	2026-04-20 17:43:30.782435+00	2026-04-20 17:43:30.782435+00
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.courses (code, level, title, department, ects, description, pass_grade, school, academic_level, credits_us, prerequisites, corequisites, antirequisites, priority_1, priority_2, priority_3, priority_4, requirements_term, requirements_year, id) FROM stdin;
CSCI	231	Computer Systems and Organization	CSCI	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	451
CSCI	235	Programming Languages	CSCI	8	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	452
CSCI	390	Artificial Intelligence	CSCI	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	453
CSCI	341	Database Systems	CSCI	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	454
CSCI	361	Software Engineering	CSCI	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	455
ELCE	455	Machine Learning with Python	ELCE	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	456
CSCI	494	Deep Learning	CSCI	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	457
CSCI	408	Senior Project I	CSCI	6	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	458
CHEM	189A	Independent Study	CHEM	2	\N	\N	SSH	UG	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	70
NUSM	411B	Basics of Physical\nExamination	NUSM	0	\N	\N	SoM	UG	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	318
BBA	201	Management and\nOrganizations	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	3 year UG GSB Business Administration (UG), 4 year UG GSB Business Administration (UG)	\N	\N	\N	Spring	2026	19
BBA	203	Responsible Leadership\n(Ethics)	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	2 year UG GSB Business Administration (UG), 3 year UG GSB Business Administration (UG), 4 year UG GSB Business Administration (UG)	\N	\N	\N	Spring	2026	20
BBA	209	Environmental, Social and\nGovernance Factors (ESG)\nfor Business	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	2 year UG GSB Business Administration (UG), 3 year UG GSB Business Administration (UG), 4 year UG GSB Business Administration (UG)	\N	\N	\N	Spring	2026	21
BBA	240	Strategy	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	3 year UG GSB Business Administration (UG), 4 year UG GSB Business Administration (UG)	\N	\N	\N	Spring	2026	22
BBA	260	Operations Management	BBA	6	\N	\N	GSB	UG	3	\N	\N	\N	2 year UG GSB Business Administration (UG), 3 year UG GSB Business Administration (UG), 4 year UG GSB Business Administration (UG)	\N	\N	\N	Spring	2026	23
ACCT	201	Introduction to Accounting	ACCT	6	\N	\N	GSB	UG	3	\N	\N	\N	Business Administration (UG)	SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	1
BUS	101	Core Course in Business	BUS	6	\N	\N	GSB	UG	3	\N	\N	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	49
BUS	420	Business Law	BUS	6	\N	\N	GSB	UG	3	BUS 101 Core Course in Business (5889) (C- and above)	\N	\N	Business Administration (UG)	SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	50
FIN	201	Principles of Finance	FIN	6	\N	\N	GSB	UG	3	BUS 101 Core Course in Business (5889) (B- and above)	\N	\N	Business Administration (UG)	SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	172
OM	201	Operations Management	OM	6	\N	\N	GSB	UG	3	BUS 101 Core Course in Business (5889) (C- and above)	\N	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	322
NUSM	103	Biology for Medical\nstudents II with Lab	NUSM	8	\N	\N	SoM	UG	4	NUSM 102 Biology for Medical students I with Lab (8491) (D and above)	\N	\N	1 year UG SOM A Six-Year Medical Program	\N	\N	\N	Spring	2026	313
NUSM	310	Capstone Project	NUSM	30	\N	\N	SoM	UG	15	NUSM 301 Introduction to Immunology, Microbiology and Genetics (6958) (C- and above) OR NUSM 302 Introduction to Statistics for Evidence-Based Practice (6959) (C- and above) OR NUSM 303 Introduction to Anatomy and Histology (6957) (C- and above)	\N	\N	3 year UG SOM Medical Sciences	\N	\N	\N	Spring	2026	314
NUSM	404	Cellular and Pathological\nBasis of Disease	NUSM	8	\N	\N	SoM	UG	4	NUSM 310 Capstone Project (7138) (C- and above)	\N	\N	4 year UG SOM Medical Sciences	\N	\N	\N	Spring	2026	315
NUSM	406	Immunology in Health and\nDisease	NUSM	9	\N	\N	SoM	UG	4.5	NUSM 310 Capstone Project (7138) (C- and above)	\N	\N	4 year UG SOM Medical Sciences	\N	\N	\N	Spring	2026	316
NUSM	407	Medical Microbiology	NUSM	9	\N	\N	SoM	UG	4.5	NUSM 310 Capstone Project (7138) (C- and above)	\N	\N	4 year UG SOM Medical Sciences	\N	\N	\N	Spring	2026	317
NUSM	415	Behavioral Medicine	NUSM	0	\N	\N	SoM	UG	0	NUSM 310 Capstone Project (7138) (C and above)	\N	\N	4 year UG SOM Medical Sciences	\N	\N	\N	Spring	2026	319
NUSM	416	Evidence-based Medicine\nII and Biostatistics	NUSM	0	\N	\N	SoM	UG	0	NUSM 310 Capstone Project (7138) (C and above)	\N	\N	4 year UG SOM Medical Sciences	\N	\N	\N	Spring	2026	320
NUSM	417	Clinical Experiences	NUSM	0	\N	\N	SoM	UG	0	NUSM 310 Capstone Project (7138) (C and above)	\N	\N	4 year UG SOM Medical Sciences	\N	\N	\N	Spring	2026	321
NUR	121	Introduction to Basic\nStatistics for Evidence-\nBased Practice	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	3 year UG SOM Nursing	\N	\N	\N	Spring	2026	299
NUR	301	Nutrition for Clinical\nPractice	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	1 year UG SOM Nursing	\N	\N	\N	Spring	2026	300
NUR	305	Research Methods for\nNursing	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	1 year UG SOM Nursing	\N	\N	\N	Spring	2026	301
NUR	306	Medical-Surgical Nursing:\nComplex Medical\nManagement for Acute and\nChronic Patient	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	1 year UG SOM Nursing	\N	\N	\N	Spring	2026	302
NUR	307	Health Promotion and\nDisease Prevention in\nCulturally Diverse\nPopulations	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	1 year UG SOM Nursing	\N	\N	\N	Spring	2026	303
NUR	313C	Medical-Surgical Nursing\nII: Complex Surgical\nManagement and Clinical	NUR	14	\N	\N	SoM	UG	7	\N	\N	\N	3 year UG SOM Nursing	\N	\N	\N	Spring	2026	304
NUR	314C	Psychiatric Nursing and\nClinical	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	3 year UG SOM Nursing	\N	\N	\N	Spring	2026	305
NUR	321	Ethics in Healthcare	NUR	4	\N	\N	SoM	UG	2	\N	\N	\N	3 year UG SOM Nursing	\N	\N	\N	Spring	2026	306
NUR	402	Principles of Healthcare\nAdministration	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	2 year UG SOM Nursing	\N	\N	\N	Spring	2026	307
NUR	405	Issues and Trends in\nNursing	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	2 year UG SOM Nursing	\N	\N	\N	Spring	2026	308
NUR	406	Medical-Surgical Nursing:\nComplex Management	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	2 year UG SOM Nursing	\N	\N	\N	Spring	2026	309
NUR	407	Capstone: Clinical and EBP\nQuality Improvement\nResearch	NUR	8	\N	\N	SoM	UG	4	\N	\N	\N	2 year UG SOM Nursing	\N	\N	\N	Spring	2026	310
NUR	415C	Clinical Transitions	NUR	18	\N	\N	SoM	UG	9	\N	\N	\N	4 year UG SOM Nursing	\N	\N	\N	Spring	2026	311
NUR	422	Capstone II: Evidence-\nBased Quality\nImprovement/Research\nProject Completion	NUR	6	\N	\N	SoM	UG	3	\N	\N	\N	4 year UG SOM Nursing	\N	\N	\N	Spring	2026	312
GEOL	101	Fundamentals of Geology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	1 year UG SMG, 2 year UG SMG	\N	\N	\N	Spring	2026	173
GEOL	103	Introduction to Geology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	3 year UG SEDS, 3 year UG SSH, 4 year UG SEDS, 4 year UG SSH	\N	\N	\N	Spring	2026	174
GEOL	204	Sedimentology and\nstrartigraphy	GEOL	6	\N	\N	SMG	UG	3	GEOL 101 Fundamentals of Geology (4774) (D and above) OR GEOL 102 Fundamentals of Geology (4772) (D and above) AND GEOL 202 Geologic Maps and Cross-Sections (5123) (D and above)	\N	\N	2 year UG SMG Geology	2 year UG SMG Mining Engineering	\N	\N	Spring	2026	175
BIOL	110	Modern Biology I	BIOL	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH Biological Sciences, 2 year UG SSH Biological Sciences, Undeclared SSH	\N	\N	\N	Spring	2026	25
GEOL	205	Paleontology	GEOL	6	\N	\N	SMG	UG	3	GEOL 101 Fundamentals of Geology (4774) (D and above) OR GEOL 102 Fundamentals of Geology (4772) (D and above)	\N	\N	2 year UG SMG Geology, 3 year UG SMG Geology	\N	\N	\N	Spring	2026	176
GEOL	301	Igneous and metamorphic\npetrology	GEOL	6	\N	\N	SMG	UG	3	GEOL 101 Fundamentals of Geology (4774) (D and above) OR GEOL 102 Fundamentals of Geology (4772) (D and above)	\N	\N	2 year UG SMG Geology	2 year UG SMG Mining Engineering, 3 year UG SMG Mining Engineering, 4 year UG SMG Mining Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	177
GEOL	304	Geophysics	GEOL	6	\N	\N	SMG	UG	3	GEOL 204 Sedimentology and strartigraphy (5475) (D and above)	\N	\N	3 year UG SMG Geology	3 year UG SMG Mining Engineering	\N	\N	Spring	2026	178
GEOL	306	Geodynamics	GEOL	6	\N	\N	SMG	UG	3	GEOL 101 Fundamentals of Geology (4774) (D and above) OR GEOL 102 Fundamentals of Geology (4772) (D and above)	\N	\N	3 year UG SMG Geology	4 year UG SMG Mining Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	179
GEOL	307	Geographic Information\nSystems	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	3 year UG SMG Geology	4 year UG SMG Mining Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	180
GEOL	309	Hydrogeology	GEOL	6	\N	\N	SMG	UG	3	\N	\N	\N	3 year UG SMG Geology	4 year UG SMG Mining Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	181
GEOL	403	Geostatistics	GEOL	6	\N	\N	SMG	UG	3	MATH 161 Calculus I (118) (C- and above)	\N	\N	4 year UG SMG Geology	4 year UG SMG Mining Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	182
GEOL	405	Research Project II	GEOL	6	\N	\N	SMG	UG	3	GEOL 404 Research Project I (6423) (C- and above)	\N	\N	4 year UG SMG Geology	\N	\N	\N	Spring	2026	183
GEOL	408	Remote Sensing of the\nEarth	GEOL	6	\N	\N	SMG	UG	3	GEOL 402 Water Resource Management (6422) (C- and above)	\N	\N	4 year UG SMG Geology	3 year UG SMG Petroleum Engineering, 4 year UG SMG Mining Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	184
GEOL	411	Photography for\nGeosciences	GEOL	6	\N	\N	SMG	UG	3	GEOL 101 Fundamentals of Geology (4774) (D and above)	\N	\N	4 year UG SMG Geology	4 year UG SMG Mining Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	185
MINE	201	Mineral Processing	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	2 year UG SMG Mining Engineering, 3 year UG SMG Mining Engineering	4 year UG SMG Geology, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	290
MINE	303	Mine Services and\nMaterials Handling	MINE	6	\N	\N	SMG	UG	3	SMG 100 Introduction to Natural Resources Extraction (4773) (C- and above) AND PHYS 162 Physics II for Scientists and Engineers with Laboratory (173) (C- and above) AND ROBT 201 Mechanics: Statics and Dynamics (475) (C- and above)	\N	\N	3 year UG SMG Mining Engineering	\N	\N	\N	Spring	2026	291
MINE	304	Resource Estimation	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	3 year UG SMG Mining Engineering	4 year UG SMG Geology	\N	\N	Spring	2026	292
MINE	305	Rock Breakage	MINE	6	\N	\N	SMG	UG	3	MINE 302 Geomechanics (5878) (D and above)	\N	\N	3 year UG SMG Mining Engineering	\N	\N	\N	Spring	2026	293
MINE	306	Underground Mining\nSystems and Design	MINE	6	\N	\N	SMG	UG	3	MINE 302 Geomechanics (5878) (D and above)	\N	\N	3 year UG SMG Mining Engineering	\N	\N	\N	Spring	2026	294
MINE	307	Surface Mining System\nand Design	MINE	6	\N	\N	SMG	UG	3	MINE 302 Geomechanics (5878) (D and above)	\N	\N	3 year UG SMG Mining Engineering	\N	\N	\N	Spring	2026	295
MINE	403	Mine Risk Management	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	4 year UG SMG Mining Engineering	4 year UG SMG Geology, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	296
MINE	404	Health, Safety and\nSustainability in Mining	MINE	6	\N	\N	SMG	UG	3	\N	\N	\N	4 year UG SMG Mining Engineering	4 year UG SMG Geology, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	297
MINE	490	Mine Design Project II	MINE	6	\N	\N	SMG	UG	3	MINE 489 Mine Design Project I (6419) (P)	\N	\N	4 year UG SMG Mining Engineering	\N	\N	\N	Spring	2026	298
PETE	202	Transport Phenomena	PETE	6	\N	\N	SMG	UG	3	ENG 200 Engineering Mathematics III (Differential Equations and Linear Algebra) (5009) (C- and above)	\N	\N	2 year UG SMG Petroleum Engineering	\N	\N	\N	Spring	2026	325
PETE	203	Drilling Engineering with\nLaboratories	PETE	8	\N	\N	SMG	UG	4	PETE 201 Fluid Mechanics and Thermodynamics (5120) (C- and above)	\N	\N	2 year UG SMG Petroleum Engineering	3 year UG SMG Petroleum Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	Spring	2026	326
PETE	204	Reservoir Rock and Fluid\nProperties with Lab	PETE	8	\N	\N	SMG	UG	4	\N	\N	\N	2 year UG SMG Petroleum Engineering	\N	\N	\N	Spring	2026	327
PETE	305	Well Test Analysis	PETE	6	\N	\N	SMG	UG	3	PETE 302 Reservoir Engineering I with Laboratory works (5955) (C- and above)	\N	\N	3 year UG SMG Petroleum Engineering, 4 year UG SMG Petroleum Engineering, 5 year UG SMG Petroleum Engineering (pending graduation)	\N	\N	\N	Spring	2026	328
PETE	306	Reservoir Engineering II	PETE	6	\N	\N	SMG	UG	3	PETE 302 Reservoir Engineering I with Laboratory works (5955) (C- and above)	\N	\N	3 year UG SMG Petroleum Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	\N	Spring	2026	329
PETE	307	Production Engineering	PETE	6	\N	\N	SMG	UG	3	PETE 201 Fluid Mechanics and Thermodynamics (5120) (C- and above) OR PETE 302 Reservoir Engineering I with Laboratory works (5955) (C- and above)	\N	\N	3 year UG SMG Petroleum Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	\N	Spring	2026	330
PETE	311	Reservoir Simulation	PETE	6	\N	\N	SMG	UG	3	PETE 301 Numerical Methods for Petroleum Engineers (5881) (C- and above) AND PETE 302 Reservoir Engineering I with Laboratory works (5955) (C- and above)	\N	\N	3 year UG SMG Petroleum Engineering, 4 year UG SMG Petroleum Engineering	\N	\N	\N	Spring	2026	331
PETE	404	Petroleum Geomechanics	PETE	6	\N	\N	SMG	UG	3	GEOL 101 Fundamentals of Geology (4774) (C- and above) OR GEOL 102 Fundamentals of Geology (4772) (C- and above)	\N	\N	4 year UG SMG Petroleum Engineering	\N	\N	\N	Spring	2026	332
PETE	407	Capstone Design Project II	PETE	6	\N	\N	SMG	UG	3	PETE 400 Capstone Design Project I (6424) (P)	\N	\N	4 year UG SMG Petroleum Engineering, 5 year UG SMG Petroleum Engineering (pending graduation)	\N	\N	\N	Spring	2026	333
SMG	400	Engineering Economics	SMG	6	\N	\N	SMG	UG	3	SMG 200/ECON 220 Resource Economics (6197) (C- and above) OR ECON 120 Managerial Economics (1852) (C- and above) OR MATH 161 Calculus I (118) (C- and above) OR MATH 162 Calculus II (170) (C- and above)	\N	\N	4 year UG SMG Geology, 4 year UG SMG Mining Engineering, 4 year UG SMG Petroleum Engineering	3 year UG SMG Petroleum Engineering	SEDS, SSH	\N	Spring	2026	391
BIOL	101	Introductory Biology	BIOL	6	\N	\N	SSH	UG	3	\N	\N	BIOL 110 Modern Biology I (1070) (C- and above)	5 year UG SSH (pending graduation), Anthropology, Chemistry, Economics, History, Nursing, Political Science and International Relations, Sociology, Undeclared SSH, World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	24
BIOL	110L	Modern Biology I\nLaboratory	BIOL	2	\N	\N	SSH	UG	1	\N	BIOL 110 Modern Biology I (1070) (C and above)	\N	1 year UG SSH Biological Sciences, 2 year UG SSH Biological Sciences	Undeclared SSH	\N	\N	Spring	2026	26
BIOL	120	Modern Biology II	BIOL	6	\N	\N	SSH	UG	3	BIOL 110 Modern Biology I (1070) (C and above)	\N	\N	1 year UG SSH Biological Sciences, 2 year UG SSH Biological Sciences, Undeclared SSH	\N	\N	\N	Spring	2026	27
BIOL	230	Human Anatomy and\nPhysiology I	BIOL	8	\N	\N	SSH	UG	4	BIOL 110 Modern Biology I (107) (C and above) OR BIOL 110 Modern Biology I (1070) (C and above)	\N	\N	2 year UG SSH Biological Sciences	3 year UG SSH Biological Sciences	Biological Sciences, SoM	\N	Spring	2026	28
BIOL	301	Molecular Cell Biology	BIOL	6	\N	\N	SSH	UG	3	BIOL 120 Modern Biology II (1195) (C and above)	\N	\N	2 year UG SSH Biological Sciences, 3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	2 year UG SOM Medical Sciences, 4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	29
BIOL	301L	Molecular Cell Biology\nLaboratory	BIOL	2	\N	\N	SSH	UG	1	BIOL 120 Modern Biology II (1195) (C and above) OR BIOL 120L Modern Biology II Laboratory (5443) (C and above)	BIOL 301 Molecular Cell Biology (5809) (C and above)	\N	2 year UG SSH Biological Sciences, 3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	30
BIOL	305	Introduction to\nMicrobiology	BIOL	6	\N	\N	SSH	UG	3	(BIOL 120 Modern Biology II (1195) (C and above) AND BIOL 120L Modern Biology II Laboratory (5443) (C and above)) OR BIOL 120 Modern Biology II (1195) (C and above)	\N	\N	2 year UG SSH Biological Sciences, 3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	31
BIOL	305L	Introduction to\nMicrobiology Laboratory	BIOL	2	\N	\N	SSH	UG	1	BIOL 120 Modern Biology II (1195) (C and above) OR BIOL 120L Modern Biology II Laboratory (5443) (C and above)	BIOL 305 Introduction to Microbiology (5789) (C and above)	\N	2 year UG SSH Biological Sciences, 3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	32
BIOL	310	Immunology	BIOL	6	\N	\N	SSH	UG	3	BIOL 301 Molecular Biology of Cell with Lab (1197) (C and above) OR BIOL 305 Introduction to Microbiology with Lab (1642) (C and above) OR BIOL 301 Molecular Cell Biology (5809) (C and above) OR BIOL 305 Introduction to Microbiology (5789) (C and above)	\N	\N	2 year UG SSH Biological Sciences, 3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	33
BIOL	321	Bioethics	BIOL	6	\N	\N	SSH	UG	3	BIOL 120 Modern Biology II (1195) (C and above)	\N	\N	3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	34
BIOL	331	Human Anatomy and\nPhysiology II	BIOL	6	\N	\N	SSH	UG	3	BIOL 230 Human Anatomy and Physiology I (72) (C and above) OR BIOL 230 Human Anatomy and Physiology I (6217) (C and above)	\N	\N	3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	35
BIOL	333	Environmental Biology	BIOL	6	\N	\N	SSH	UG	3	BIOL 120 Modern Biology II (1195) (C and above)	\N	\N	3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	36
BIOL	341	Biochemistry I	BIOL	6	\N	\N	SSH	UG	3	CHEM 211 Organic Chemistry I (154) (C and above)	\N	\N	2 year UG SSH Biological Sciences, 3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	2 year UG SOM Medical Sciences, 4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	37
BIOL	355	Critical Research\nReasoning	BIOL	6	\N	\N	SSH	UG	3	BIOL 120 Modern Biology II (1195) (C and above)	\N	\N	3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	38
BIOL	370	Genetics	BIOL	6	\N	\N	SSH	UG	3	BIOL 120 Modern Biology II (1195) (C and above)	\N	\N	3 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	4 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	39
BIOL	425	Biomedical Research\nMethods	BIOL	6	\N	\N	SSH	UG	3	BIOL 110 Modern Biology I Lab (1444) (C and above) OR BIOL 110 Modern Biology I (1070) (C and above) AND BIOL 341 Biochemistry I (2002) (C and above) OR CHEM 341 Biochemistry I (1058) (C and above)	\N	\N	4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	3 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	40
BIOL	440	Neuroscience	BIOL	6	\N	\N	SSH	UG	3	BIOL 230 Human Anatomy and Physiology I (72) (C and above) OR BIOL 230 Human Anatomy and Physiology I (6217) (C and above)	\N	\N	4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	3 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	41
BIOL	445	Medical Microbiology	BIOL	6	\N	\N	SSH	UG	3	BIOL 305 Introduction to Microbiology (5789) (C and above) OR BIOL 305 Introduction to Microbiology with Lab (1642) (C and above)	\N	\N	4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	3 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	42
BIOL	450	Food Microbiology	BIOL	6	\N	\N	SSH	UG	3	BIOL 305 Introduction to Microbiology with Lab (1642) (C and above) OR BIOL 305 Introduction to Microbiology (5789) (C and above)	\N	\N	4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	3 year UG SSH Biological Sciences	3 year UG SOM Medical Sciences, Biological Sciences	\N	Spring	2026	43
BIOL	471	Light and Electron\nmicroscopy concepts and\ntechniques	BIOL	6	\N	\N	SSH	UG	3	BIOL 110 Modern Biology I (1070) (C and above) AND BIOL 120 Modern Biology II (1195) (C and above) AND CHEM 101 General Chemistry I (113) (C and above) AND PHYS 161 Physics I for Scientists and Engineers with Laboratory (116) (C and above)	\N	\N	3 year UG SSH Biological Sciences, 4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	\N	\N	\N	Spring	2026	44
BIOL	471L	Light and Electron\nMicroscopy Concepts and\nTechniques-Lab	BIOL	2	\N	\N	SSH	UG	1	\N	BIOL 471 Light and Electron microscopy concepts and techniques (4686) (C and above)	\N	3 year UG SSH Biological Sciences, 4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	\N	\N	\N	Spring	2026	45
BIOL	481	Neuroimmunology	BIOL	6	\N	\N	SSH	UG	3	BIOL 310 Immunology (628) (C and above)	\N	\N	3 year UG SSH Biological Sciences, 4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	\N	\N	\N	Spring	2026	46
BIOL	491	Honors Thesis	BIOL	6	\N	\N	SSH	UG	3	BIOL 490 Honors Thesis Research (1581) (C and above)	\N	\N	4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	\N	\N	\N	Spring	2026	47
BIOL	492	Research Experience in\nBiology	BIOL	6	\N	\N	SSH	UG	3	BIOL 456 Biology Research Design (1217) (C- and above)	\N	\N	4 year UG SSH Biological Sciences, 5 year UG SSH Biological Sciences (pending graduation)	\N	\N	\N	Spring	2026	48
CHEM	100	Introduction to Chemistry	CHEM	6	\N	\N	SSH	UG	3	\N	\N	CHEM 090 Chemistry for Non-Science majors (152) (D+ and above)	5 year UG SEDS (pending graduation), 5 year UG SSH (pending graduation), Anthropology, Economics, History, Nursing, Political Science and International Relations, Sociology, Undeclared SSH, World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	65
CHEM	101	General Chemistry I	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	Chemistry, Undeclared SSH	Biological Sciences, SMG, SoM	Business Administration (UG), SEDS, SSH	\N	Spring	2026	66
CHEM	101L	General Chemistry I lab	CHEM	2	\N	\N	SSH	UG	1	\N	CHEM 101 General Chemistry I (113) (C and above)	\N	Chemistry	Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	67
CHEM	102	General Chemistry II	CHEM	6	\N	\N	SSH	UG	3	CHEM 101 General Chemistry I (113) (C and above)	\N	\N	Chemistry	Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	68
CHEM	105	Introduction to\nEnvironmental Science	CHEM	6	\N	\N	SSH	UG	3	\N	\N	CHEM 092 Survey of Environmental Sciences for Non-Science Majors (1149) (D+ and above)	Anthropology, Economics, History, Nursing, Political Science and International Relations, Sociology, Undeclared SSH, World Languages, Literature and Culture	Mathematics, Physics	Business Administration (UG), SEDS, SMG	\N	Spring	2026	69
CHEM	211	Organic Chemistry I	CHEM	6	\N	\N	SSH	UG	3	CHEM 102 General Chemistry II (232) (C and above)	\N	\N	Chemistry	Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	71
CHEM	211L	Organic Chemistry I Lab	CHEM	2	\N	\N	SSH	UG	1	CHEM 101L General Chemistry I lab (179) (C and above)	CHEM 211 Organic Chemistry I (154) (C and above)	\N	Chemistry	Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	72
CHEM	212	Organic Chemistry II	CHEM	6	\N	\N	SSH	UG	3	CHEM 211 Organic Chemistry I (154) (C and above) OR CHEM 191 Chemistry I for Engineers (1908) (C and above)	\N	\N	Chemistry	Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	73
CHEM	212L	Organic Chemistry II Lab	CHEM	2	\N	\N	SSH	UG	1	CHEM 211L Organic Chemistry I Lab (156) (C and above)	CHEM 212 Organic Chemistry II (443) (C and above) OR CHEM 292 Organic Chemistry for Biologists II (1901) (C and above)	\N	Chemistry	Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	74
CHEM	250	Descriptive Inorganic\nChemistry	CHEM	6	\N	\N	SSH	UG	3	CHEM 101 General Chemistry I (113) (C and above)	\N	\N	Chemistry	Biological Sciences	\N	\N	Spring	2026	75
CHEM	320	Instrumental Analysis	CHEM	6	\N	\N	SSH	UG	3	CHEM 220 Quantitative Chemical Analysis (555) (C and above)	\N	\N	Chemistry	Biological Sciences	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	76
CHEM	320L	Instrumental Analysis Lab	CHEM	2	\N	\N	SSH	UG	1	(CHEM 220 Quantitative Chemical Analysis (555) (C and above) AND CHEM 220L Quantitative Chemical Analysis Lab (5271) (C and above)) OR CHEM 220 Quantitative Chemical Analysis (555) (C and above)	CHEM 320 Instrumental Analysis (1055) (C and above)	\N	Chemistry	Biological Sciences	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	77
CHEM	332	Physical Chemistry II	CHEM	6	\N	\N	SSH	UG	3	CHEM 331 Physical Chemistry I (634) (C and above)	MATH 274 Introduction to Differential Equations (484) (C and above)	\N	Chemistry	Biological Sciences	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	78
CHEM	332L	Physical Chemistry II Lab	CHEM	2	\N	\N	SSH	UG	1	\N	CHEM 332 Physical Chemistry II (1056) (C and above) AND CHEM 331L Physical Chemistry Lab (1060) (C and above)	\N	Chemistry	Biological Sciences	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	79
CHEM	341L	Biochemistry I Lab	CHEM	2	\N	\N	SSH	UG	1	CHEM 212L Organic Chemistry II Lab (444) (C and above)	CHEM 341 Biochemistry I (1058) (C and above)	\N	Chemistry	Biological Sciences	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	80
CHEM	380	Research Methods	CHEM	6	\N	\N	SSH	UG	3	\N	\N	\N	Chemistry	\N	\N	\N	Spring	2026	81
CHEM	400	Chemistry Seminar	CHEM	6	\N	\N	SSH	UG	3	CHEM 380 Research Methods (636) (C and above)	\N	\N	Chemistry	\N	\N	\N	Spring	2026	82
CHEM	411	Advanced Organic\nChemistry I	CHEM	6	\N	\N	SSH	UG	3	CHEM 212 Organic Chemistry II (443) (C and above) AND MATH 161 Calculus I (118) (C and above)	\N	\N	Chemistry	Biological Sciences	SEDS, SMG, SSH	\N	Spring	2026	83
CHEM	431	Computational Chemistry	CHEM	6	\N	\N	SSH	UG	3	CHEM 332 Physical Chemistry II (1056) (C and above) AND (CSCI 111 Web Programming and Problem Solving (110) (C- and above) OR CSCI 150 Fundamentals of Programming (1501) (C- and above) OR CSCI 151 Programming for Scientists and Engineers (192) (C- and above))	\N	\N	Chemistry	SEDS, SMG, SSH	\N	\N	Spring	2026	84
CHEM	433	Surfactants and Colloids	CHEM	6	\N	\N	SSH	UG	3	CHEM 102 General Chemistry II (232) (C and above)	\N	\N	Chemistry	SEDS, SMG, SSH	\N	\N	Spring	2026	85
CHEM	445	Drug Discovery and\nDevelopment	CHEM	6	\N	\N	SSH	UG	3	CHEM 211 Organic Chemistry I (154) (C and above)	\N	\N	Chemistry	Biological Sciences	SEDS, SMG, SSH, SoM	\N	Spring	2026	86
CHEM	489	Directed Research II	CHEM	6	\N	\N	SSH	UG	3	CHEM 488 Directed Research I (7174) (C and above)	\N	\N	Chemistry	\N	\N	\N	Spring	2026	87
CHEM	490	Nanochemistry	CHEM	6	\N	\N	SSH	UG	3	CHEM 331 Physical Chemistry I (634) (C and above) AND CHEM 250 Descriptive Inorganic Chemistry (445) (C and above)	\N	\N	Chemistry	SSH	SEDS, SMG	\N	Spring	2026	88
WCS	135	Introduction to Visual\nCommunication	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH	2 year UG SSH, 3 year UG SSH	1 year UG SEDS, 1 year UG SMG, Business Administration (UG), SoM	\N	Spring	2026	420
WCS	150	Rhetoric and Composition	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	421
WCS	200	Introduction to Public\nSpeaking	WCS	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (C- and above)	\N	\N	2 year UG SEDS, 2 year UG SMG, 2 year UG SSH, SoM	3 year UG SEDS, 3 year UG SMG, 3 year UG SSH	\N	\N	Spring	2026	422
WCS	204	Gender and\nCommunication	WCS	6	\N	\N	SSH	UG	3	WCS 101 Communication and Society (199) (C- and above) OR WCS 150 Rhetoric and Composition (2183) (B- and above)	\N	\N	2 year UG SSH	1 year UG SSH, 3 year UG SSH	2 year UG SEDS, 2 year UG SMG, SoM	\N	Spring	2026	423
WCS	205	Intercultural\nCommunication	WCS	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH	1 year UG SSH, 3 year UG SSH	2 year UG SEDS, 2 year UG SMG, SoM	\N	Spring	2026	424
WCS	210	Technical and Professional\nWriting	WCS	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (C- and above)	\N	WCS 220 Science Writing (5686) (C- and above)	Chemical and Materials Engineering, Chemistry, Civil and Environmental Engineering, Electrical and Computer Engineering, Geology, Mechanical and Aerospace Engineering, Mining Engineering, Petroleum Engineering, Robotics Engineering	SEDS	Business Administration (UG), SSH, SoM	\N	Spring	2026	425
WCS	220	Science Writing	WCS	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (C- and above)	\N	WCS 210 Technical and Professional Writing (4881) (C- and above)	Business Administration (UG), SEDS, SSH, SoM	\N	\N	\N	Spring	2026	426
WCS	230	Say What you Mean:\nClarity, Precision, and\nStyle in Academic Writing	WCS	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (C- and above)	\N	\N	2 year UG SEDS, 2 year UG SMG, 2 year UG SSH, SoM	3 year UG SEDS, 3 year UG SMG, 3 year UG SSH	\N	\N	Spring	2026	427
WCS	240	Writing for Digital Media	WCS	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (C- and above)	\N	\N	2 year UG SEDS, 2 year UG SMG, 2 year UG SSH, SoM	3 year UG SEDS, 3 year UG SMG, 3 year UG SSH	\N	\N	Spring	2026	428
WCS	250	Advanced Rhetoric and\nComposition	WCS	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (C- and above)	\N	\N	2 year UG SEDS, 2 year UG SMG, 2 year UG SSH, SoM	3 year UG SEDS, 3 year UG SMG, 3 year UG SSH	\N	\N	Spring	2026	429
WCS	270	Academic and Professional\nPresentations	WCS	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (C- and above)	\N	WCS 210 Technical and Professional Writing (4881) (C- and above)	2 year UG SEDS, 2 year UG SMG, 2 year UG SSH, SoM	3 year UG SEDS, 3 year UG SMG, 3 year UG SSH	\N	\N	Spring	2026	430
WCS	300	Internship: Undergraduate\nSpeaker Consultant I	WCS	6	\N	\N	SSH	UG	3	WCS 200 Introduction to Public Speaking (175) (A- and above) OR WCS 270 Academic and Professional Presentations (8409) (A- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	431
WCS	301	Internship: Undergraduate\nSpeaker Consultant II	WCS	6	\N	\N	SSH	UG	3	WCS 300 Internship: Undergraduate Speaker Consultant I (8538) (P)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	432
WCS	304	Multimodal\nCommunication Internship\nI	WCS	6	\N	\N	SSH	UG	3	WCS 240 Writing for Digital Media (4421) (A- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	433
WCS	305	Multimodal\nCommunication Internship\nII	WCS	6	\N	\N	SSH	UG	3	WCS 304 Multimodal Communication Internship I (8702) (P) OR SSH 300 School of Sciences and Humanities Internship (712) (P)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	434
WCS	390	Writing Fellows I –\nComposition and\nCollaboration in Theory\nand Practice	WCS	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (B and above) AND (WCS 220 Science Writing (5686) (B+ and above) OR WCS 230 Say What you Mean: Clarity, Precision, and Style in Academic Writing (3026) (B+ and above) OR WCS 250 Advanced Rhetoric and Composition (3027) (B+ and above))	\N	\N	2 year UG SSH	3 year UG SSH	2 year UG SEDS, 2 year UG SMG	\N	Spring	2026	435
WCS	393	Internship: Undergraduate\nWriting Tutor I	WCS	6	\N	\N	SSH	UG	3	WCS 392 Writing Fellows III - Research & Practice in Writing & Peer Mentorship (4472) (B and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	436
WCS	394	Internship: Undergraduate\nWriting Tutor II	WCS	6	\N	\N	SSH	UG	3	WCS 393 Internship: Undergraduate Writing Tutor I (7346) (P)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	437
WLL	235	Creative Writing:\nIntroduction to Fiction\nWriting I	WLL	6	\N	\N	SSH	UG	3	WCS 150 Rhetoric and Composition (2183) (C- and above)	\N	\N	2 year UG SEDS, 2 year UG SMG, 2 year UG SSH, SoM	3 year UG SEDS, 3 year UG SMG, 3 year UG SSH	\N	\N	Spring	2026	440
WLL	462	Creative Nonfiction	WLL	6	\N	\N	SSH	UG	3	WCS 260/WLL 235 Creative Writing: Introduction to Fiction Writing I (4000) (C and above)	\N	\N	World Languages, Literature and Culture	SSH	\N	\N	Spring	2026	449
ECON	101	Introduction to\nMicroeconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SSH (pending graduation), Undeclared SSH	Business Administration (UG), SSH	SEDS, SMG, SoM	\N	Spring	2026	126
ECON	102	Introduction to\nMacroeconomics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SSH (pending graduation), Undeclared SSH	Business Administration (UG), SSH	SEDS, SMG, SoM	\N	Spring	2026	127
ECON	120	Managerial Economics	ECON	6	\N	\N	SSH	UG	3	\N	\N	\N	SEDS	SMG, SSH, SoM	\N	\N	Spring	2026	128
ECON	201	Intermediate\nMicroeconomics	ECON	6	\N	\N	SSH	UG	3	ECON 101 Introduction to Microeconomics (379) (B- and above) AND (MATH 161 Calculus I (118) (B- and above) OR MATH 162 Calculus II (170) (B- and above))	\N	\N	Economics	2 year UG SSH Undeclared	SSH	\N	Spring	2026	129
ECON	202	Intermediate\nMacroeconomics	ECON	6	\N	\N	SSH	UG	3	ECON 102 Introduction to Macroeconomics (503) (B- and above) AND (MATH 161 Calculus I (118) (B- and above) OR MATH 162 Calculus II (170) (B- and above))	\N	\N	Economics	2 year UG SSH Undeclared	SSH	\N	Spring	2026	130
ECON	211	Economic Statistics	ECON	6	\N	\N	SSH	UG	3	ECON 101 Introduction to Microeconomics (379) (C and above) OR ECON 102 Introduction to Macroeconomics (503) (C and above)	\N	\N	Economics	2 year UG SSH Undeclared	SSH	\N	Spring	2026	131
ECON	300	Research Assistance in\nEconomics	ECON	2	\N	\N	SSH	UG	1	ECON 101 Introduction to Microeconomics (379) (C- and above) AND ECON 102 Introduction to Macroeconomics (503) (C- and above) OR CSCI 151 Programming for Scientists and Engineers (192) (C- and above) OR CSCI 235 Programming Languages (638) (C- and above) OR CSCI 390 Artificial Intelligence (643) (C- and above) OR MATH 321 Probability (482) (C- and above) OR MATH 322 Mathematical Statistics (1165) (C- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	132
ECON	301	Econometrics I	ECON	6	\N	\N	SSH	UG	3	ECON 211 Economic Statistics (2280) (C- and above) OR (MATH 321 Probability (482) (C- and above) AND (MATH 322 Mathematical Statistics (1165) (C- and above) OR MATH 310 Applied Statistical Methods (82) (C- and above)))	\N	\N	Economics	\N	SSH	\N	Spring	2026	133
ECON	319	Matching Theory and\nApplications	ECON	6	\N	\N	SSH	UG	3	ECON 201 Intermediate Microeconomics (133) (C- and above)	\N	\N	3 year UG SSH Economics, 5 year UG SSH (pending graduation), 6 year UG SSH (pending graduation)	4 year UG SSH Economics	SSH	\N	Spring	2026	134
ECON	335	Economics of Information	ECON	6	\N	\N	SSH	UG	3	ECON 201 Intermediate Microeconomics (133) (C- and above)	\N	\N	3 year UG SSH Economics, 5 year UG SSH (pending graduation), 6 year UG SSH (pending graduation)	4 year UG SSH Economics	SSH	\N	Spring	2026	135
ECON	336	Programming for\nEconomists	ECON	6	\N	\N	SSH	UG	3	ECON 301 Econometrics I (664) (C- and above)	\N	ECON 318 Applied Econometrics (6078) (C- and above)	3 year UG SSH Economics, 5 year UG SSH (pending graduation), 6 year UG SSH (pending graduation)	4 year UG SSH Economics	SSH	\N	Spring	2026	136
ECON	337	Empirical Finance	ECON	6	\N	\N	SSH	UG	3	ECON 211 Economic Statistics (2280) (C- and above) OR MATH 322 Mathematical Statistics (1165) (C- and above)	\N	\N	3 year UG SSH Economics, 5 year UG SSH (pending graduation), 6 year UG SSH (pending graduation)	4 year UG SSH Economics	SSH	\N	Spring	2026	137
ECON	341	Economic Simulation\nModeling	ECON	6	\N	\N	SSH	UG	3	ECON 201 Intermediate Microeconomics (133) (C- and above)	\N	\N	3 year UG SSH Economics, 5 year UG SSH (pending graduation), 6 year UG SSH (pending graduation)	4 year UG SSH Economics	SSH	\N	Spring	2026	138
ECON	400	Research Assistance in\nEconomics 2	ECON	2	\N	\N	SSH	UG	1	ECON 300 Research Assistance in Economics (3080) (P)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	139
ECON	413	Econometrics II Time\nSeries	ECON	6	\N	\N	SSH	UG	3	ECON 301 Econometrics I (664) (C- and above)	\N	\N	Economics	\N	SSH	\N	Spring	2026	140
ECON	415	Industrial Organization	ECON	6	\N	\N	SSH	UG	3	ECON 301 Econometrics I (664) (C- and above)	\N	\N	Economics	\N	SSH	\N	Spring	2026	141
ECON	434	Introduction to Big Data\nAnalytics	ECON	6	\N	\N	SSH	UG	3	ECON 301 Econometrics I (664) (C- and above)	\N	\N	Economics	\N	SSH	\N	Spring	2026	142
ECON	498	Advanced Special Topics in\nEconomics	ECON	6	\N	\N	SSH	UG	3	ECON 201 Intermediate Microeconomics (133) (C- and above) OR ECON 202 Intermediate Macroeconomics (207) (C- and above) OR MATH 322 Mathematical Statistics (1165) (C- and above) OR MATH 321 Probability (482) (C- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	143
HST	100	History of Kazakhstan	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH, 5 year UG SEDS (pending graduation), 5 year UG SMG (pending graduation), 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SSH (pending graduation)	2 year UG SEDS, 2 year UG SMG, 2 year UG SOM, 2 year UG SSH, 3 year UG SEDS, 3 year UG SMG, 3 year UG SOM, 3 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	188
HST	123	Introduction to the History\nof Science and Technology	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH Undeclared, History	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	189
HST	124	Introduction to the History\nof Medicine	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH Undeclared, History	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	190
HST	132	European History II (from\n1700)	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH Undeclared, History	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	191
HST	205	The Mongol Empire	HST	6	\N	\N	SSH	UG	3	Subject "HST" BETWEEN 100 and 199 OR Subject "" BETWEEN 100 and 199 OR Subject "" BETWEEN 100 and 199 OR Subject "" BETWEEN 100 and 199	\N	\N	1 year UG SSH Undeclared, History	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	192
HST	243	Soviet History Through\nFilm	HST	6	\N	\N	SSH	UG	3	HST 100 History of Kazakhstan (172) (C- and above)	\N	\N	1 year UG SSH Undeclared, History	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	193
HST	336	The Totalitarian\nPhenomenon	HST	6	\N	\N	SSH	UG	3	HST 100 History of Kazakhstan (172) (C- and above)	\N	\N	History	4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH, 5 year UG SEDS (pending graduation), 5 year UG SMG (pending graduation), 5 year UG SOM (pending graduation), 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SMG (pending graduation), 6 year UG SOM (pending graduation), 6 year UG SSH (pending graduation)	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	199
HST	400	Research Assistance	HST	2	\N	\N	SSH	UG	1	HST 100 History of Kazakhstan (172) (B and above) AND Subject "HST" BETWEEN 100 and 499	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	200
HST	499	History Capstone:\nUndergraduate\nDissertation	HST	8	\N	\N	SSH	UG	4	HST 498 Directed Reading (1365) (C- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	204
PHIL	207	Introduction to Islamic\nPhilosophy and Theology	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH Undeclared	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	334
PHIL	210	Ethics	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	3 year UG SEDS, 3 year UG SMG, 3 year UG SOM, 3 year UG SSH, 4 year UG SEDS, 4 year UG SMG, 4 year UG SSH, 5 year UG SEDS (pending graduation), 5 year UG SMG (pending graduation), 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SSH (pending graduation)	2 year UG SEDS, 2 year UG SMG, 2 year UG SSH Biological Sciences	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	335
PHIL	240	Formal Logic	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH Undeclared	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	336
PHIL	350	History of 19th and 20th\nCentury Philosophy	PHIL	6	\N	\N	SSH	UG	3	\N	\N	\N	4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH, 5 year UG SEDS (pending graduation), 5 year UG SMG (pending graduation), 5 year UG SOM, 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SMG (pending graduation), 6 year UG SOM (pending graduation), 6 year UG SSH (pending graduation)	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	337
PHIL	399	Special Topics in\nPhilosophy	PHIL	6	\N	\N	SSH	UG	3	PHIL 101 Introduction to Philosophy (242) (C- and above) OR PHIL 210 Ethics (459) (C- and above) OR PHIL 320 Truth, Knowledge and Belief (470) (C- and above) OR PHIL 230/PLS 230 Religion and Democracy (671) (C- and above)	\N	\N	4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH, 5 year UG SEDS (pending graduation), 5 year UG SMG (pending graduation), 5 year UG SOM, 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SMG (pending graduation), 6 year UG SOM (pending graduation), 6 year UG SSH (pending graduation)	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	338
HST	273	History of Sufism in the\nMiddle East and Central\nAsia	HST	6	\N	\N	SSH	UG	3	Subject "HST" BETWEEN 100 and 199	\N	\N	1 year UG SSH Undeclared, History	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	196
HST	319	Philosophy of History	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	World Languages, Literature and Culture	History	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	198
GER	202	Intermediate German II	GER	8	\N	\N	SSH	UG	4	GER 201 Intermediate German I (3722) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	187
HST	440	Religions in the Soviet and\nPost-Soviet Eras	HST	6	\N	\N	SSH	UG	3	Subject "REL" BETWEEN 100 and 200 OR Subject "REL" BETWEEN 100 and 200 OR Subject "HST" BETWEEN 100 and 200	\N	\N	History	4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH, 5 year UG SEDS (pending graduation), 5 year UG SMG (pending graduation), 5 year UG SOM (pending graduation), 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SMG (pending graduation), 6 year UG SOM (pending graduation), 6 year UG SSH (pending graduation)	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	201
HST	462	History of Islam Under\nRussian Rule	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	World Languages, Literature and Culture	History	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	203
HST	272	Modern Turkey: from the\nOttoman Empire to the\nTurkish Republic	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH Undeclared, History	1 year UG SSH, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	195
HST	245	Global History of Travel\nand Travel Literature	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SSH Undeclared, History	1 year UG SSH, 2 year UG SSH, World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	194
HST	274	Texts and Contexts	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	World Languages, Literature and Culture	History	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	197
HST	447	Media and Memory Politics\nin the Post-Soviet Space	HST	6	\N	\N	SSH	UG	3	\N	\N	\N	World Languages, Literature and Culture	History	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	202
WLL	375	Philosophy of Art	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH, 5 year UG SEDS (pending graduation), 5 year UG SMG (pending graduation), 5 year UG SOM, 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SMG (pending graduation), 6 year UG SOM (pending graduation), 6 year UG SSH (pending graduation)	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	445
ANT	215	What is Islam?\nAnthropological\nPerspectives	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	Anthropology, History	Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	6
REL	435	The Archaeology of Ritual	REL	6	\N	\N	SSH	UG	3	ANT 140 World Prehistory (227) (C- and above) OR ANT 231 Frauds and Fallacies in Archaeology (1129) (C- and above) OR ANT 232 Life, Death and Economy: Archaeology of Central Asia (1461) (C- and above) OR ANT 240 Laboratory Methods in Archaeology (5669) (C- and above)	\N	\N	Anthropology, History	Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	376
KAZ	201	Academic Kazakh I	KAZ	6	\N	\N	SSH	UG	3	KAZ 150 Basic Kazakh (1215) (C- and above) OR KLL "[B1.2] Intermediate"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS, 1 year UG SMG, 1 year UG SOM, 1 year UG SSH, 2 year UG GSB Business Administration (UG), 2 year UG SEDS, 2 year UG SMG, 2 year UG SOM, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	205
KAZ	202	Academic Kazakh II	KAZ	6	\N	\N	SSH	UG	3	KAZ 201 Academic Kazakh I (4561) (C- and above) OR KLL "[B2.2] Upper- Interm."	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS, 1 year UG SMG, 1 year UG SOM, 1 year UG SSH, 2 year UG GSB Business Administration (UG), 2 year UG SEDS, 2 year UG SMG, 2 year UG SOM, 2 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	206
KAZ	300	Kazakh Studies in the Post-\nColonial Era	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	207
KAZ	312	Kazakh discourse	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	208
KAZ	313	Kazakh for Business	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 3 year UG SOM A Six-Year Medical Program, 3 year UG SSH Biological Sciences	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	209
KAZ	349	Kazakh Mythology	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 3 year UG SOM A Six-Year Medical Program, 3 year UG SSH Biological Sciences	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	210
KOR	102	Beginning Korean II	KOR	8	\N	\N	SSH	UG	4	KOR 101 Beginning Korean I (4672) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	229
KAZ	350	Kazakh Literature	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	211
KAZ	351	Kazakh Short Stories	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 3 year UG SOM A Six-Year Medical Program, 3 year UG SSH Biological Sciences	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	212
KAZ	356	Kazakh Music History	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	213
KAZ	357	Literature of Alash	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 3 year UG SOM A Six-Year Medical Program, 3 year UG SSH Biological Sciences	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	214
KAZ	359	Professional Kazakh for\nMedicine	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 3 year UG SSH Biological Sciences, 4 year UG SOM	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	215
KAZ	366	Kazakh Language for\nEngineers	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 4 year UG SEDS	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	216
KAZ	368	Onomastics: History and\nFunction of Names	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	217
KAZ	371	Contemporary Kazakh\nLiterature	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	218
KAZ	372	Language and ethnicity	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	219
KAZ	373	Kazakh Terminology	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	220
KAZ	374	Kazakh Diplomacy	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	221
KAZ	376	Language and Culture	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	222
KAZ	377	Intercultural\nCommunication through\nFilm	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	223
KAZ	378	Kazakh for Social Science	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 2 year UG SSH Biological Sciences, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	224
KAZ	379	Kazakh Cinema	KAZ	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	1 year UG GSB Business Administration (UG), 1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 1 year UG SMG Geology, 1 year UG SMG Mining Engineering, 1 year UG SMG Petroleum Engineering, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Biological Sciences, 1 year UG SSH Chemistry, 1 year UG SSH Mathematics, 1 year UG SSH Undeclared, 2 year UG SEDS Computer Science, 3 year UG SEDS Robotics Engineering, 3 year UG SMG Petroleum Engineering, 4 year UG SEDS, 4 year UG SMG, 4 year UG SOM, 4 year UG SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	225
KAZ	411	Shoqan Studies: A\nDecolonialist Discourse	KAZ	6	\N	\N	SSH	UG	3	Subject "KAZ" BETWEEN 300 and 399	\N	\N	4 year UG SEDS, 4 year UG SMG, 4 year UG SOM	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	226
KAZ	412	Scientific Discourse of\nAlash	KAZ	6	\N	\N	SSH	UG	3	Subject "KAZ" BETWEEN 300 and 399	\N	\N	4 year UG SEDS, 4 year UG SMG, 4 year UG SOM	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	227
KFL	102	Elementary Kazakh as a\nForeign Language II	KFL	8	\N	\N	SSH	UG	4	KFL 101 Elementary Kazakh as a Foreign Language I (4889) (C- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	228
TUR	100	Languages, Cultures, and\nCommunities of the Turkic\nWorld	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	414
TUR	231	Istanbul in Literature and\nCulture	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH World Languages, Literatures and Cultures	World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	416
TUR	235	Turkish Poetry in\nTranslation	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	417
TUR	305	Introduction to Chagatay\nand Ottoman Turkish	TUR	6	\N	\N	SSH	UG	3	KAZ 202 Academic Kazakh II (4562) (C- and above) OR KLL "[C1.1] Advanced"	\N	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	419
TUR	180	Introduction to Turkic\nlanguages	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	415
TUR	280	Introduction to Turkic\nHistorical and Comparative\nLinguistics	TUR	6	\N	\N	SSH	UG	3	\N	\N	\N	World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	418
CHN	102	Beginning Mandarin II	CHN	8	\N	\N	SSH	UG	4	CHN 101 Beginning Mandarin I (1384) (C and above)	\N	\N	SSH	SEDS, SMG, SoM	\N	\N	Spring	2026	100
CHN	301	Upper Intermediate\nChinese I	CHN	8	\N	\N	SSH	UG	4	CHN 202 Intermediate Mandarin II (2678) (C and above)	\N	\N	SSH	SEDS, SMG, SoM	\N	\N	Spring	2026	101
DUT	101	Beginning Dutch I	DUT	8	\N	\N	SSH	UG	4	\N	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	125
GER	102	Beginning German II	GER	8	\N	\N	SSH	UG	4	GER 101 Beginning German (3173) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	186
KOR	202	Intermediate Korean II	KOR	8	\N	\N	SSH	UG	4	KOR 201 Intermediate Korean I (5059) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	230
LING	111	Linguistics for non-majors	LING	6	\N	\N	SSH	UG	3	\N	\N	LING 131 Introduction to Linguistics (1394) ( and above)	1 year UG SEDS, 1 year UG SOM, 1 year UG SSH	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	231
LING	140	Language Variation and\nChange: the Story of\nEnglish	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SEDS, 1 year UG SOM, 1 year UG SSH, 2 year UG SSH World Languages, Literatures and Cultures, 3 year UG SSH World Languages, Literatures and Cultures	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	232
LING	271	Introduction to Cognitive\nLinguistics	LING	6	\N	\N	SSH	UG	3	LING 131 Introduction to Linguistics (1394) (C and above)	\N	\N	2 year UG SSH World Languages, Literatures and Cultures	World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	233
LING	273	Survey of Research\nMethods in Linguistics	LING	6	\N	\N	SSH	UG	3	LING 131 Introduction to Linguistics (1394) (C- and above)	\N	\N	2 year UG SSH World Languages, Literatures and Cultures	World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	234
LING	278	Sounds of the World’s\nLanguages	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH World Languages, Literatures and Cultures	World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	235
LING	371	Practicum in Teaching\nForeign Languages	LING	4	\N	\N	SSH	UG	2	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	236
LING	374	Language Contact in\nCentral Asia	LING	6	\N	\N	SSH	UG	3	LING 131 Introduction to Linguistics (1394) (C- and above)	\N	\N	SSH	SEDS, SMG, SoM	\N	\N	Spring	2026	237
LING	375	The Art and Science of\nAnalyzing Languages:\nMorphosyntax of the\nWorld's Languages	LING	6	\N	\N	SSH	UG	3	LING 131 Introduction to Linguistics (1394) (C- and above)	\N	\N	World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	238
LING	377	Historical Linguistics	LING	6	\N	\N	SSH	UG	3	LING 131 Introduction to Linguistics (1394) (C- and above) AND (LING 240 Introduction to Sociolinguistics (6838) (C- and above) OR LING 270 Languages of Eurasia (2485) (C- and above) OR LING 273 Survey of Research Methods in Linguistics (2158) (C- and above) OR LING 277 Language Diversity and Language Universals (3834) (C- and above) OR LING 278 Sounds of the World’s Languages (3850) (C- and above) OR LING 280/TUR 280 Introduction to Turkic Historical and Comparative Linguistics (3175) (C- and above) OR LING 375 The Art and Science of Analyzing Languages: Morphosyntax of the World's Languages (6237) (C- and above) OR LING 470 Multilingualism and Language Contact (3339) (C- and above) OR LING 374 Language Contact in Central Asia (3047) (C- and above) OR LING 140 Language Variation and Change: the Story of English (4835) (C- and above))	\N	\N	World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	239
LING	461	Experimental semantics	LING	6	\N	\N	SSH	UG	3	LING 130 Introduction to Language and Communication (4014) (C- and above) OR LING 131 Introduction to Linguistics (1394) (C- and above)	\N	\N	World Languages, Literature and Culture	SSH	SEDS, SMG, SoM	\N	Spring	2026	240
LING	473	Advanced Empirical\nMethods in Linguistics	LING	6	\N	\N	SSH	UG	3	LING 131 Introduction to Linguistics (1394) (C and above)	\N	\N	World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	241
LING	482	Language and Worldview	LING	6	\N	\N	SSH	UG	3	LING 131 Introduction to Linguistics (1394) (C and above) OR LING 272 Language and the Mind (1847) (C and above)	\N	\N	World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	242
LING	491	Advanced Independent\nStudy	LING	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	243
PER	101	Beginning Persian I	PER	8	\N	\N	SSH	UG	4	\N	\N	\N	1 year UG SSH Undeclared, 2 year UG SSH World Languages, Literatures and Cultures	2 year UG SSH Political Sciences and International Relations, 3 year UG SSH World Languages, Literatures and Cultures	2 year UG SSH, 3 year UG SSH	\N	Spring	2026	323
PER	102	Beginning Persian II	PER	8	\N	\N	SSH	UG	4	PER 101 Beginning Persian I (4474) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	324
POL	102	Beginning Polish II	POL	8	\N	\N	SSH	UG	4	POL 101 Beginning Polish (7641) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	374
POL	201	Intermediate Polish I	POL	8	\N	\N	SSH	UG	4	POL 102 Beginning Polish II (8214) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	375
RFL	303	Intensive Advanced\nRussian	RFL	8	\N	\N	SSH	UG	4	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	377
RFL	305	Academic Writing in\nRussian	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	378
RFL	312	Soviet Female Writers and\nPoets	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	379
RFL	356	Kazakh Music History	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	380
RFL	469	International relations of\nEurasia	RFL	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	381
SPA	102	Beginning Spanish II	SPA	8	\N	\N	SSH	UG	4	SPA 101 Beginning Spanish I (685) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	409
SPA	202	Intermediate Spanish II	SPA	8	\N	\N	SSH	UG	4	SPA 201 Intermediate Spanish I (1475) (C- and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	410
SPA	311	Colloquial Spanish	SPA	6	\N	\N	SSH	UG	3	SPA 202 Intermediate Spanish II (1842) (C and above)	\N	\N	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	\N	Spring	2026	411
WLL	110	Introduction to Literary\nStudies	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	1 year UG SEDS, 1 year UG SOM, 1 year UG SSH, World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	438
WLL	211	World Literature II: from\nthe 18th to the 20th\ncentury	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH World Languages, Literatures and Cultures	World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	439
WLL	241	Survey of Folk Tales	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH World Languages, Literatures and Cultures	World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	441
WLL	248	Survey of Soviet Literature\nand Culture	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH World Languages, Literatures and Cultures	World Languages, Literature and Culture	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	442
WLL	313	Dante's Inferno	WLL	6	\N	\N	SSH	UG	3	Subject "WLL" BETWEEN 100 and 499 OR Subject "HST" BETWEEN 100 and 499	\N	\N	World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	443
WLL	341	Soviet Literature as\nMultinational Literature	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	444
WLL	399	Independent Study	WLL	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	446
WLL	400	Research Assistance in\nLinguistics and Literature	WLL	2	\N	\N	SSH	UG	1	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	447
WLL	451	The Call of the Evil:\nUnmasking the\nVillain(ness) in Popular\nCulture and Literature	WLL	6	\N	\N	SSH	UG	3	WLL 201 World Literature I (686) (C+ and above) OR WLL 209 Introduction to Translation Studies (2178) (C+ and above) OR WLL 210 Migrants, Nomads and Exiles (217) (C+ and above) OR WLL 211 World Literature II: from the 18th to the 20th century (492) (C+ and above) OR WLL 212 Introduction to Poetry (2167) (C+ and above) OR WLL 213/SPA 211 Introduction to the Hispanic World (1030) (C+ and above) OR WLL 218 Renaissance in Italy and Beyond (6573) (C+ and above) OR WLL 219 Myth and Adaptation (2489) (C+ and above) OR WLL 220 Ancient World Literature (to 1650) (218) (C+ and above) OR WLL 221 Creative Writing/Theatre (245) (C+ and above) OR WLL 222 Acting: Praxis, Theory and History (3336) (C+ and above) OR WLL 231 Beginning and Intermediate Playwriting (1625) (C+ and above) OR WLL 240 Introduction to the Novel (687) (C+ and above) OR WLL 241 Survey of Folk Tales (466) (C+ and above) OR WLL 243 Western Theatre, Literature and History From Ancient Creece to 1800 (1082) (C+ and above) OR WLL 244 Survey of Nineteenth- Century Russian Literature (1395) (C+ and above) OR WLL 349 Terrible Perfection: Women in 19th-Century Russian Literature (2488) (C+ and above) OR WLL 246 Survey of Contemporary Russian Literature and Culture (3604) (C+ and above) OR WLL 247 Survey of East Asian Literature (1382) (C+ and above) OR WLL 248 Survey of Soviet Literature and Culture (3842) (C+ and above) OR WLL 250 From Page to Screen (472) (C+ and above) OR WLL 251 Hong Kong Cinema (3337) (C+ and above) OR WLL 253 Western Theatre Literature and History: 1800-Present (1396) (C+ and above) OR WLL 254/SPA 254 Superstition, Magical Realism, and Horror in Hispanic Culture (1851) (C+ and above) OR WLL 255 The Comic Book in Japan and America (1849) (C+ and above) OR WLL 257 Fan Culture in the Age of Convergence (2487) (C+ and above) OR WLL 291 Theatre Practicum (2168) (C+ and above)	\N	\N	World Languages, Literature and Culture	SSH	Business Administration (UG), SEDS, SMG, SoM	\N	Spring	2026	448
WLL	499	Languages, Linguistics,\nand Literatures Capstone\nII	WLL	6	\N	\N	SSH	UG	3	WLL 498 Languages, Linguistics, and Literatures Capstone I (3048) (C- and above)	\N	\N	World Languages, Literature and Culture	\N	\N	\N	Spring	2026	450
MATH	109	Mathematical Discovery	MATH	6	\N	\N	SSH	UG	3	\N	\N	MATH 161 Calculus I (118) (C- and above)	5 year UG SSH (pending graduation), 6 year UG SSH (pending graduation), Anthropology, History, Political Science and International Relations, Sociology, Undeclared SSH, World Languages, Literature and Culture	\N	\N	\N	Spring	2026	257
MATH	161	Calculus I	MATH	8	\N	\N	SSH	UG	4	\N	\N	\N	1 year UG SOM A Six-Year Medical Program, 5 year UG SSH (pending graduation), Biological Sciences, Chemistry, Mathematics, Physics, SEDS, SMG	(ND-CC) Undeclared SSH, 1 year UG SSH Undeclared	Business Administration (UG), SSH, SoM	\N	Spring	2026	258
MATH	162	Calculus II	MATH	8	\N	\N	SSH	UG	4	MATH 161 Calculus I (118) (C and above)	\N	\N	5 year UG SSH (pending graduation), Chemistry, Mathematics, Physics, SEDS, SMG	(ND-CC) Undeclared SSH, 1 year UG SSH Undeclared, Biological Sciences	Business Administration (UG), SSH, SoM	\N	Spring	2026	259
MATH	251	Discrete Mathematics	MATH	6	\N	\N	SSH	UG	3	MATH 161 Calculus I (118) (C and above)	\N	\N	2 year UG SEDS Computer Science, Mathematics	Computer Science	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	260
MATH	263	Calculus III	MATH	8	\N	\N	SSH	UG	4	MATH 162 Calculus II (170) (C and above)	\N	\N	Mathematics, Physics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	261
MATH	273	Linear Algebra with\nApplications	MATH	8	\N	\N	SSH	UG	4	MATH 161 Calculus I (118) (C and above)	MATH 162 Calculus II (170) (C and above)	\N	2 year UG SEDS Computer Science, 2 year UG SEDS Robotics Engineering, 2 year UG SEDS Robotics and Mechatronics, Mathematics, Physics	Computer Science, Robotics Engineering, Robotics and Mechatronics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	262
MATH	274	Introduction to Differential\nEquations	MATH	6	\N	\N	SSH	UG	3	MATH 162 Calculus II (170) (C and above)	\N	\N	Chemistry, Mathematics, Physics, Robotics Engineering, Robotics and Mechatronics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	263
MATH	275	Mathematics for Artificial\nIntelligence	MATH	6	\N	\N	SSH	UG	3	MATH 161 Calculus I (118) (C- and above) OR CSCI 151 Programming for Scientists and Engineers (192) (C- and above)	\N	\N	Anthropology, History, Political Science and International Relations, Sociology, World Languages, Literature and Culture	Business Administration (UG), SSH	SEDS, SMG, SoM	\N	Spring	2026	264
MATH	302	Abstract Algebra I	MATH	6	\N	\N	SSH	UG	3	MATH 273 Linear Algebra with Applications (84) (C and above) AND MATH 251 Discrete Mathematics (85) (C and above)	\N	\N	3 year UG SSH Mathematics, 4 year UG SSH Mathematics	2 year UG SSH Mathematics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	265
MATH	310	Applied Statistical Methods	MATH	6	\N	\N	SSH	UG	3	MATH 161 Calculus I (118) (C and above)	\N	MATH 321 Probability (482) (C and above)	2 year UG SMG Mining Engineering, 2 year UG SSH Biological Sciences	Biological Sciences, Mining Engineering, Petroleum Engineering	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	266
MATH	321	Probability	MATH	6	\N	\N	SSH	UG	3	MATH 162 Calculus II (170) (C and above)	\N	ECON 211 Economic Statistics (2280) (C- and above) OR PLS 211 Quantitative Methods (221) (C- and above)	Computer Science, Mathematics, Robotics Engineering, Robotics and Mechatronics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	267
MATH	322	Mathematical Statistics	MATH	6	\N	\N	SSH	UG	3	MATH 321 Probability (482) (C and above) OR ECON 211 Economic Statistics (2280) (C and above)	\N	\N	3 year UG SSH Mathematics, 4 year UG SSH Mathematics	2 year UG SSH Mathematics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	268
MATH	350	Research Methods	MATH	6	\N	\N	SSH	UG	3	MATH 321 Probability (482) (C and above)	\N	\N	Mathematics	\N	\N	\N	Spring	2026	269
MATH	351	Numerical Methods with\nApplications	MATH	6	\N	\N	SSH	UG	3	MATH 274 Introduction to Differential Equations (484) (C and above) AND MATH 263 Calculus III (81) (C and above)	\N	ENG 202 Numerical Methods in Engineering (5506) (C and above)	3 year UG SSH Mathematics, 4 year UG SSH Mathematics	2 year UG SSH Mathematics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	270
MATH	361	Real Analysis I	MATH	6	\N	\N	SSH	UG	3	MATH 263 Calculus III (81) (C and above) AND MATH 251 Discrete Mathematics (85) (C and above)	\N	\N	3 year UG SSH Mathematics, 4 year UG SSH Mathematics	2 year UG SSH Mathematics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	271
MATH	407	Graph Theory	MATH	6	\N	\N	SSH	UG	3	(MATH 301 Introduction to Number Theory (613) (C and above) OR MATH 251 Discrete Mathematics (85) (C and above)) AND MATH 273 Linear Algebra with Applications (84) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	272
MATH	411	Linear Programming	MATH	6	\N	\N	SSH	UG	3	MATH 273 Linear Algebra with Applications (84) (C and above) AND MATH 263 Calculus III (81) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	273
MATH	412	Nonlinear Optimization	MATH	6	\N	\N	SSH	UG	3	MATH 273 Linear Algebra with Applications (84) (C and above) AND MATH 263 Calculus III (81) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	274
MATH	423	Actuarial Mathematics II	MATH	6	\N	\N	SSH	UG	3	MATH 321 Probability (482) (C and above) OR ECON 211 Economic Statistics (2280) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	275
MATH	440	Regression Analysis	MATH	6	\N	\N	SSH	UG	3	MATH 322 Mathematical Statistics (1165) (C and above)	\N	SOC 203 Quantitative Methods in Sociology (1377) (C and above) OR PLS 211 Quantitative Methods (221) (C and above)	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	276
MATH	455	Stochastic Calculus	MATH	6	\N	\N	SSH	UG	3	MATH 321 Probability (482) (C and above) OR ECON 211 Economic Statistics (2280) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	277
MATH	456	Introduction to Lie Groups\nand Representations	MATH	6	\N	\N	SSH	UG	3	MATH 361 Real Analysis I (483) (C and above) AND MATH 273 Linear Algebra with Applications (84) (C and above) AND MATH 274 Introduction to Differential Equations (484) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	278
MATH	461	Real Analysis II	MATH	6	\N	\N	SSH	UG	3	MATH 361 Real Analysis I (483) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	279
MATH	462	Advanced Linear Algebra	MATH	6	\N	\N	SSH	UG	3	MATH 251 Discrete Mathematics (85) (C and above) AND MATH 273 Linear Algebra with Applications (84) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	280
MATH	465	Introduction to Differential\nGeometry	MATH	6	\N	\N	SSH	UG	3	MATH 273 Linear Algebra with Applications (84) (C and above) AND MATH 361 Real Analysis I (483) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	281
MATH	466	Nonlinear Continuum\nMechanics	MATH	6	\N	\N	SSH	UG	3	MATH 273 Linear Algebra with Applications (84) (C and above) AND MATH 263 Calculus III (81) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	282
MATH	482	Fourier Analysis	MATH	6	\N	\N	SSH	UG	3	MATH 263 Calculus III (81) (C and above) AND MATH 274 Introduction to Differential Equations (484) (C and above)	\N	\N	Mathematics	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	283
MATH	490	Special Topics in\nMathematics I	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	284
MATH	491	Special Topics in\nMathematics II	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	285
MATH	492	Special Topics in\nMathematics III	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	286
MATH	497	Directed Study in\nMathematics I	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	287
MATH	498	Directed Study in\nMathematics II	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	288
MATH	499	Capstone Project	MATH	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	289
PHYS	161	Physics I for Scientists and\nEngineers with Laboratory	PHYS	8	\N	\N	SSH	UG	4	\N	MATH 161 Calculus I (118) (C and above)	PHYS 171 Physics I for Physics Majors with Laboratory (1401) (C- and above)	1 year UG SEDS, 1 year UG SMG, 1 year UG SOM A Six-Year Medical Program, 1 year UG SSH Biological Sciences, 1 year UG SSH Physics, 2 year UG SOM Medical Sciences	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	339
PHYS	162	Physics II for Scientists\nand Engineers with\nLaboratory	PHYS	8	\N	\N	SSH	UG	4	PHYS 161 Physics I for Scientists and Engineers with Laboratory (116) (C- and above) OR PHYS 151 Introductory Physics I with Lab (649) (C- and above)	\N	PHYS 172 Physics II for Physics Majors with Laboratory (1402) (C- and above)	1 year UG SEDS, 1 year UG SMG, 1 year UG SSH Physics, 2 year UG SSH Biological Sciences	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	340
PHYS	202	Introductory Astrophysics	PHYS	6	\N	\N	SSH	UG	3	PHYS 162 Physics II for Scientists and Engineers with Laboratory (173) (C- and above)	\N	\N	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	341
PHYS	222	Classical Mechanics II	PHYS	6	\N	\N	SSH	UG	3	PHYS 221 Classical Mechanics I (652) (C- and above)	MATH 274 Introduction to Differential Equations (484) (D and above)	\N	Physics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	342
PHYS	270	Introduction to Scientific\nComputing and Data\nAnalysis	PHYS	6	\N	\N	SSH	UG	3	(CSCI 150 Fundamentals of Programming (1501) (C- and above) OR CSCI 151 Programming for Scientists and Engineers (192) (C- and above) OR CSCI 115 Programming Fundamentals (5257) (C- and above)) AND MATH 162 Calculus II (170) (C- and above)	MATH 273 Linear Algebra with Applications (84) (D and above)	\N	Physics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	343
PHYS	280	Thermodynamics and\nStatistical Physics	PHYS	6	\N	\N	SSH	UG	3	MATH 263 Calculus III (81) (C- and above) AND (PHYS 162 Physics II for Scientists and Engineers with Laboratory (173) (C- and above) OR PHYS 172 Physics II for Physics Majors with Laboratory (1402) (C- and above))	\N	\N	Physics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	344
PHYS	362	Classical Electrodynamics\nII	PHYS	6	\N	\N	SSH	UG	3	PHYS 361 Classical Electrodynamics I (651) (C- and above)	\N	\N	Physics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	345
PHYS	370	Optics with Laboratory	PHYS	8	\N	\N	SSH	UG	4	PHYS 361 Classical Electrodynamics I (651) (C- and above)	\N	\N	Physics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	346
PHYS	451	Quantum Mechanics I	PHYS	6	\N	\N	SSH	UG	3	PHYS 221 Classical Mechanics I (652) (C- and above) AND PHYS 361 Classical Electrodynamics I (651) (C- and above)	\N	\N	Physics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	347
PHYS	462	Field Theories in Physics	PHYS	6	\N	\N	SSH	UG	3	MATH 162 Calculus II (170) (C- and above) AND PHYS 221 Classical Mechanics I (652) (C- and above)	PHYS 451 Quantum Mechanics I (1415) (C- and above)	\N	Physics	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	348
PHYS	491	Directed Study of\nAdvanced Physics Topics	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	349
PHYS	499	Honors Thesis	PHYS	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	350
PLS	101	Introduction to Political\nScience	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SEDS (pending graduation), 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SSH (pending graduation), Undeclared SSH	Anthropology, Biological Sciences, Business Administration (UG), Chemistry, Economics, History, Mathematics, Physics, SEDS, SMG, SoM, Sociology, World Languages, Literature and Culture	\N	\N	Spring	2026	351
PLS	140	Introduction to\nComparative Politics	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SEDS (pending graduation), 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SSH (pending graduation), Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	352
PLS	150	Introduction to\nInternational Relations	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SEDS (pending graduation), 5 year UG SSH (pending graduation), 6 year UG SEDS (pending graduation), 6 year UG SSH (pending graduation), Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	\N	Spring	2026	353
PLS	210	Political Science Research\nMethods	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH Political Sciences and International Relations, 3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	\N	\N	Spring	2026	354
PLS	211	Quantitative Methods	PLS	6	\N	\N	SSH	UG	3	\N	\N	ECON 211 Economic Statistics (2280) (C- and above)	2 year UG SSH Political Sciences and International Relations, 3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	\N	\N	Spring	2026	355
PLS	315	Political Game Theory	PLS	6	\N	\N	SSH	UG	3	PLS 211 Quantitative Methods (221) (C- and above) OR ECON 101 Introduction to Microeconomics (379) (C and above)	\N	\N	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	\N	\N	Spring	2026	356
PLS	327	Contemporary Political\nTheory	PLS	6	\N	\N	SSH	UG	3	PLS 120 Introduction to Political Theory (512) (C- and above)	\N	PHIL 131 Introduction to Contemporary Political Philosophy (4032) (C- and above)	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	\N	\N	Spring	2026	357
PLS	345	Revolutions, Social\nMovements, and\nContentious Politics	PLS	6	\N	\N	SSH	UG	3	PLS 210 Political Science Research Methods (129) (C- and above)	\N	\N	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	SSH	\N	Spring	2026	358
PLS	351	International Political\nEconomy	PLS	6	\N	\N	SSH	UG	3	PLS 150 Introduction to International Relations (511) (C- and above) AND PLS 210 Political Science Research Methods (129) (C- and above) AND PLS 211 Quantitative Methods (221) (C- and above)	\N	\N	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	SSH	\N	Spring	2026	359
PLS	355	European Union:\nInstitutions and Policies	PLS	6	\N	\N	SSH	UG	3	PLS 210 Political Science Research Methods (129) (C- and above)	\N	\N	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	SSH	\N	Spring	2026	360
PLS	361	Memory Politics in East\nAsia	PLS	6	\N	\N	SSH	UG	3	\N	\N	\N	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	\N	\N	Spring	2026	361
PLS	363	Visual Politics	PLS	6	\N	\N	SSH	UG	3	PLS 140 Introduction to Comparative Politics (223) (C- and above) AND PLS 210 Political Science Research Methods (129) (C- and above)	\N	\N	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	SSH	\N	Spring	2026	362
PLS	391	Intermediate Special\nTopics in Comparative\nPolitics	PLS	6	\N	\N	SSH	UG	3	PLS 210 Political Science Research Methods (129) (C- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	363
PLS	392	Politics of China	PLS	6	\N	\N	SSH	UG	3	PLS 210 Political Science Research Methods (129) (C- and above)	\N	\N	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	SSH	\N	Spring	2026	364
PLS	393	Modern Korean Politics	PLS	6	\N	\N	SSH	UG	3	PLS 210 Political Science Research Methods (129) (C and above) AND PLS 211 Quantitative Methods (221) (C and above)	\N	\N	3 year UG SSH Political Sciences and International Relations	Political Science and International Relations	\N	\N	Spring	2026	365
PLS	395	Independent Study	PLS	6	\N	\N	SSH	UG	3	PLS 210 Political Science Research Methods (129) (C- and above) AND PLS 211 Quantitative Methods (221) (C- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	366
PLS	435	Political Polarization in\nDemocracies	PLS	6	\N	\N	SSH	UG	3	PLS 140 Introduction to Comparative Politics (223) (C and above) AND PLS 210 Political Science Research Methods (129) (C and above) AND PLS 211 Quantitative Methods (221) (C and above)	\N	\N	Political Science and International Relations	\N	SSH	\N	Spring	2026	367
PLS	441	Advanced Topics in\nComparative Politics	PLS	6	\N	\N	SSH	UG	3	PLS 140 Introduction to Comparative Politics (223) (C- and above) AND PLS 210 Political Science Research Methods (129) (C- and above)	\N	\N	Political Science and International Relations	\N	SSH	\N	Spring	2026	368
PLS	445	Political Violence	PLS	6	\N	\N	SSH	UG	3	(PLS 140 Introduction to Comparative Politics (223) (C- and above) OR PLS 150 Introduction to International Relations (511) (C- and above)) AND PLS 210 Political Science Research Methods (129) (C- and above)	\N	\N	Political Science and International Relations	\N	SSH	\N	Spring	2026	369
PLS	451	Advanced Topics in\nInternational Relations	PLS	6	\N	\N	SSH	UG	3	PLS 150 Introduction to International Relations (511) (C- and above) AND PLS 210 Political Science Research Methods (129) (C- and above) AND PLS 211 Quantitative Methods (221) (C- and above)	\N	\N	Political Science and International Relations	\N	SSH	\N	Spring	2026	370
PLS	457	International Security and\nConflict	PLS	6	\N	\N	SSH	UG	3	PLS 150 Introduction to International Relations (511) (C- and above) AND PLS 210 Political Science Research Methods (129) (C- and above) AND PLS 211 Quantitative Methods (221) (C- and above)	\N	\N	Political Science and International Relations	\N	SSH	\N	Spring	2026	371
PLS	469	International Relations of\nEurasia	PLS	6	\N	\N	SSH	UG	3	PLS 150 Introduction to International Relations (511) (C- and above) AND PLS 210 Political Science Research Methods (129) (C- and above)	\N	\N	Political Science and International Relations	\N	SSH	\N	Spring	2026	372
PLS	495	Research Practicum in\nPSIR	PLS	2	\N	\N	SSH	UG	1	PLS 210 Political Science Research Methods (129) (C- and above) AND PLS 211 Quantitative Methods (221) (C- and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	373
SSH	300	School of Sciences and\nHumanities Internship	SSH	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	412
SSH	301	School of Sciences and\nHumanities Internship:\nSecond Experience	SSH	6	\N	\N	SSH	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	413
ANT	101	Being Human: An\nIntroduction to Four Field\nAnthropology	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SEDS (pending graduation), 5 year UG SSH (pending graduation), Anthropology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	2 year UG SSH, 3 year UG SSH Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	2
ANT	110	Introduction to\nSociocultural Anthropology	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SEDS (pending graduation), 5 year UG SSH (pending graduation), Anthropology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	2 year UG SSH, 3 year UG SSH Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	3
ANT	140	World Prehistory	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SEDS (pending graduation), 5 year UG SSH (pending graduation), Anthropology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	2 year UG SSH, 3 year UG SSH Biological Sciences, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	4
ANT	231	Frauds and Fallacies in\nArchaeology	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	Anthropology	Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	7
ANT	232	Life, Death and Economy:\nArchaeology of Central\nAsia	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	Anthropology	Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	8
ANT	270	Anthropology of Warfare	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	Anthropology	Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	9
ANT	286	Nomads: Around the world\nand through time	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	SEDS, SMG, SSH, SoM	\N	\N	\N	Spring	2026	10
ANT	306	Anthropology of\nPerformance	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	Anthropology	Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	11
ANT	317	Museum space: collections,\ncollectors and society	ANT	6	\N	\N	SSH	UG	3	ANT 101 Being Human: An Introduction to Four Field Anthropology (2960) (C and above) OR ANT 140 World Prehistory (227) (C and above) OR ANT 110 Introduction to Sociocultural Anthropology (501) (C and above) OR WLL 171/ANT 175 Introduction to Linguistic Anthropology (4417) (C and above)	\N	\N	Anthropology	Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	12
ANT	361	Human Evolution: Bones,\nStones and Genomes	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	Anthropology	Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	13
ANT	400	Research Assistance in\nAnthropology	ANT	2	\N	\N	SSH	UG	1	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	15
ANT	402	Research Assistance in\nAnthropology	ANT	2	\N	\N	SSH	UG	1	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	16
ANT	499	Capstone Seminar II	ANT	6	\N	\N	SSH	UG	3	ANT 498 Capstone Seminar I (2965) (C- and above)	\N	\N	Anthropology, Sociology	\N	\N	\N	Spring	2026	18
SOC	101	Introduction to Sociology	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	5 year UG SEDS (pending graduation), 5 year UG SSH (pending graduation), Sociology, Undeclared SEDS, Undeclared SMG, Undeclared SSH	2 year UG SSH, 3 year UG SSH Biological Sciences, Anthropology, SoM	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	392
SOC	201	Social Science Research\nMethods	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	3 year UG SSH Anthropology, 3 year UG SSH Sociology, 4 year UG SSH Anthropology, 4 year UG SSH Sociology, 5 year UG SSH Anthropology, 5 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	393
SOC	203	Quantitative Methods in\nSociology	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	Anthropology, Sociology	\N	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	394
SOC	210	Gender and Society	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH Sociology, 3 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	395
SOC	215	Sociology of Race and\nEthnicity	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH Sociology, 3 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	396
SOC	220	Science, Technology, and\nSociety	SOC	6	\N	\N	SSH	UG	3	\N	\N	\N	2 year UG SSH Sociology, 3 year UG SSH Sociology	\N	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	397
SOC	301	Classical Sociological\nTheory	SOC	6	\N	\N	SSH	UG	3	SOC 101 Introduction to Sociology (508) (C- and above) OR SOC 115 Global Social Problems (1032) (C- and above) OR ANT 110 Introduction to Sociocultural Anthropology (501) (C- and above)	\N	\N	Anthropology, Sociology	Undeclared SEDS, Undeclared SMG, Undeclared SSH	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	398
SOC	310	Social Inequality	SOC	6	\N	\N	SSH	UG	3	SOC 101 Introduction to Sociology (508) (C- and above) OR SOC 115 Global Social Problems (1032) (C- and above)	\N	\N	3 year UG SSH Sociology, 4 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	399
SOC	313	Social Foundations of\nEducation	SOC	6	\N	\N	SSH	UG	3	SOC 101 Introduction to Sociology (508) (C- and above) OR SOC 115 Global Social Problems (1032) (C- and above)	\N	\N	3 year UG SSH Sociology, 4 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	400
SOC	320	Organized Crime and\nCorruption	SOC	6	\N	\N	SSH	UG	3	SOC 101 Introduction to Sociology (508) (C- and above)	\N	\N	3 year UG SSH Sociology, 4 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	401
SOC	400	Research Assistance in\nSociology	SOC	2	\N	\N	SSH	UG	1	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	402
SOC	401	Research Assistance in\nSociology	SOC	2	\N	\N	SSH	UG	1	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	403
SOC	402	Research Assistance in\nSociology	SOC	2	\N	\N	SSH	UG	1	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	404
SOC	410	Violence Against Women:\nAn Intersectional Approach	SOC	6	\N	\N	SSH	UG	3	Subject "SOC" BETWEEN 200 and 299 OR Subject "SOC" BETWEEN 200 and 299 OR Subject "SOC" BETWEEN 300 and 399 OR Subject "SOC" BETWEEN 300 and 399	\N	\N	3 year UG SSH Sociology, 4 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	405
SOC	416	Sociology of Punishment	SOC	6	\N	\N	SSH	UG	3	SOC 301 Classical Sociological Theory (683) (C- and above)	\N	\N	3 year UG SSH Sociology, 4 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	406
SOC	425	Modern Sociological\nTheory	SOC	6	\N	\N	SSH	UG	3	SOC 301 Classical Sociological Theory (683) (C and above)	\N	\N	3 year UG SSH Sociology, 4 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH	\N	Spring	2026	407
SOC	499	Capstone Seminar II	SOC	6	\N	\N	SSH	UG	3	SOC 498 Capstone Seminar Part I (3043) (C- and above)	\N	\N	Anthropology, Sociology	\N	\N	\N	Spring	2026	408
ANT	214	Qualitative Methods	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	3 year UG SSH Anthropology, 3 year UG SSH Sociology, 4 year UG SSH Anthropology, 4 year UG SSH Sociology, 5 year UG SSH Anthropology, 5 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	5
ANT	386	Social Challenges of\nClimate Change	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	3 year UG SSH Anthropology, 3 year UG SSH Sociology, 4 year UG SSH Anthropology, 4 year UG SSH Sociology, 5 year UG SSH Anthropology, 5 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	14
ANT	412	Approaches to Global\nDevelopment	ANT	6	\N	\N	SSH	UG	3	\N	\N	\N	3 year UG SSH Anthropology, 3 year UG SSH Sociology, 4 year UG SSH Anthropology, 4 year UG SSH Sociology, 5 year UG SSH Anthropology, 5 year UG SSH Sociology	Anthropology, Sociology	Business Administration (UG), SEDS, SMG, SSH, SoM	\N	Spring	2026	17
CHME	202	Fluid Mechanics	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	2 year UG SEDS Chemical and Materials Engineering	3 year UG SEDS Chemical and Materials Engineering, 4 year UG SEDS Chemical and Materials Engineering	\N	\N	Spring	2026	89
CHME	203	Organic and Polymer\nChemistry	CHME	6	\N	\N	SEDS	UG	3	CHME 222 Inorganic and Analytical Chemistry (5039) (D and above)	\N	\N	2 year UG SEDS Chemical and Materials Engineering	3 year UG SEDS Chemical and Materials Engineering, 4 year UG SEDS Chemical and Materials Engineering	\N	\N	Spring	2026	90
CHME	303	Separation Processes	CHME	6	\N	\N	SEDS	UG	3	CHME 200 Basic Principles and Calculations in Chemical Engineering (5038) (D and above) AND CHME 201 Chemical Engineering Thermodynamics (5007) (D and above)	\N	\N	3 year UG SEDS Chemical and Materials Engineering	4 year UG SEDS Chemical and Materials Engineering	\N	\N	Spring	2026	91
CHME	304	Chemical Reaction\nEngineering	CHME	6	\N	\N	SEDS	UG	3	CHME 200 Basic Principles and Calculations in Chemical Engineering (5038) (D and above)	\N	\N	3 year UG SEDS Chemical and Materials Engineering	4 year UG SEDS Chemical and Materials Engineering	\N	\N	Spring	2026	92
CHME	305L	Chemical Engineering\nLaboratory I	CHME	6	\N	\N	SEDS	UG	3	CHME 201 Chemical Engineering Thermodynamics (5007) (D and above) AND CHME 202 Fluid Mechanics (5543) (D and above) AND CHME 300 Heat and Mass Transfer (5952) (D and above)	\N	\N	3 year UG SEDS Chemical and Materials Engineering	4 year UG SEDS Chemical and Materials Engineering	\N	\N	Spring	2026	93
CHME	352	Research Practice	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	3 year UG SEDS Chemical and Materials Engineering	4 year UG SEDS Chemical and Materials Engineering	\N	\N	Spring	2026	94
CHME	402	Materials Chemistry	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Chemical and Materials Engineering	\N	\N	\N	Spring	2026	95
CHME	403	Chemical Process Control\nand Safety	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Chemical and Materials Engineering	\N	\N	\N	Spring	2026	96
CHME	421	Tissue Engineering	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Chemical and Materials Engineering	3 year UG SEDS Chemical and Materials Engineering	\N	\N	Spring	2026	97
CHME	454	Transport Phenomena and\nOperations	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Chemical and Materials Engineering, 4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	\N	Spring	2026	98
CHME	461	Powder technology	CHME	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Chemical and Materials Engineering	3 year UG SEDS Chemical and Materials Engineering	\N	\N	Spring	2026	99
CEE	202	Environmental Engineering	CEE	6	\N	\N	SEDS	UG	3	CEE 201 Environmental Chemistry (4999) (D and above)	\N	\N	2 year UG SEDS Civil and Environmental Engineering	3 year UG SEDS Civil and Environmental Engineering	4 year UG SEDS Civil and Environmental Engineering, 5 year UG SEDS Civil and Environmental Engineering	\N	Spring	2026	51
CEE	203	Structural Analysis	CEE	6	\N	\N	SEDS	UG	3	MAE 200 Structural Mechanics I (5010) (D and above) OR CEE 200 Structural Mechanics I (5005) (D and above)	\N	\N	2 year UG SEDS Civil and Environmental Engineering	3 year UG SEDS Civil and Environmental Engineering	4 year UG SEDS Civil and Environmental Engineering, 5 year UG SEDS Civil and Environmental Engineering	\N	Spring	2026	52
CEE	301	Structural Design – Steel	CEE	6	\N	\N	SEDS	UG	3	CEE 203 Structural Analysis (5500) (D and above)	\N	\N	3 year UG SEDS Civil and Environmental Engineering	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	Spring	2026	53
CEE	303	Geotechnical Design	CEE	6	\N	\N	SEDS	UG	3	CEE 302 Geotechnical Engineering (5896) (D and above)	\N	\N	3 year UG SEDS Civil and Environmental Engineering	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	Spring	2026	54
CEE	305	Hydraulics and Hydrology	CEE	6	\N	\N	SEDS	UG	3	MAE 300 Fluid Mechanics I (5926) (D and above) OR EME 275 Fluid Mechanics I (1988) (D and above) OR CEE 304 Fluid Mechanics (6348) (D and above)	\N	\N	3 year UG SEDS Civil and Environmental Engineering	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	Spring	2026	55
CEE	350	Water and Wastewater\nTreatment Processes	CEE	6	\N	\N	SEDS	UG	3	CEE 201 Environmental Chemistry (4999) (D and above) AND CEE 202 Environmental Engineering (5499) (D and above)	\N	\N	3 year UG SEDS Civil and Environmental Engineering	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	Spring	2026	56
CEE	400	Transportation\nEngineering	CEE	6	\N	\N	SEDS	UG	3	CEE 204 Civil Engineering CAD and Surveying (5002) (D and above)	\N	\N	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	\N	Spring	2026	57
CEE	454	Foundation Engineering	CEE	6	\N	\N	SEDS	UG	3	ECE 306 Geotechnical Design (1043) (D and above) OR CEE 303 Geotechnical Design (6158) (D and above)	\N	\N	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	\N	Spring	2026	58
CEE	457	Air Quality Management	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	\N	Spring	2026	59
ENG	103	Engineering Materials II	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Electrical and Computer Engineering	Chemical and Materials Engineering, Electrical and Computer Engineering	\N	\N	Spring	2026	168
CEE	458	Modern Information\nTechnology in Construction	CEE	6	\N	\N	SEDS	UG	3	CEE 204 Civil Engineering CAD and Surveying (5002) (D and above)	\N	\N	3 year UG SEDS Civil and Environmental Engineering	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	Spring	2026	60
CEE	463	Individual Research\nProject in Civil &\nEnvironmental Engineering\n1	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	\N	Spring	2026	61
CEE	465	Structure and Properties of\nConcrete Materials	CEE	6	\N	\N	SEDS	UG	3	CEE 306 Civil Engineering Materials (5897) (D and above)	\N	\N	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	\N	Spring	2026	62
CEE	466	Introduction to Finite\nElement Methods	CEE	6	\N	\N	SEDS	UG	3	CEE 200 Structural Mechanics I (5005) (D and above)	\N	\N	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering	\N	\N	Spring	2026	63
CEE	470	Construction Engineering\nEconomics	CEE	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Civil and Environmental Engineering	5 year UG SEDS Civil and Environmental Engineering (pending graduation)	\N	\N	Spring	2026	64
CSCI	111	Web Programming and\nProblem Solving	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	CSCI 101 Introduction to Computational Sciences (147) (D and above) OR CSCI 115 Programming Fundamentals (5257) (D and above) OR CSCI 151 Programming for Scientists and Engineers (192) (D and above) OR ENG 101 Programming for Engineers (4517) (D and above)	Business Administration (UG), SSH, SoM	\N	\N	\N	Spring	2026	102
CSCI	115	Programming\nFundamentals	CSCI	8	\N	\N	SEDS	UG	4	\N	\N	CSCI 101 Introduction to Computational Sciences (147) (D and above) OR CSCI 111 Web Programming and Problem Solving (110) (D and above) OR CSCI 151 Programming for Scientists and Engineers (192) (D and above) OR ENG 101 Programming for Engineers (4517) (D and above)	Biological Sciences, Business Administration (UG), Chemistry, Mathematics, SoM	SSH	\N	\N	Spring	2026	103
CSCI	151	Programming for Scientists\nand Engineers	CSCI	8	\N	\N	SEDS	UG	4	\N	\N	CSCI 111 Web Programming and Problem Solving (110) (D and above) OR CSCI 115 Programming Fundamentals (5257) (D and above) OR ENG 101 Programming for Engineers (4517) (B- and above)	Computer Science, Robotics Engineering	Physics, Undeclared SEDS	SEDS, SMG, SSH	\N	Spring	2026	104
CSCI	152	Performance and Data\nStructures	CSCI	8	\N	\N	SEDS	UG	4	CSCI 151 Programming for Scientists and Engineers (192) (C- and above)	\N	\N	Computer Science, Robotics Engineering	Undeclared SEDS	\N	\N	Spring	2026	105
CSCI	245	System Analysis and\nDesign	CSCI	6	\N	\N	SEDS	UG	3	CSCI 152 Performance and Data Structures (489) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	106
CSCI	262	Software Project\nManagement	CSCI	6	\N	\N	SEDS	UG	3	CSCI 152 Performance and Data Structures (489) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	107
CSCI	270	Algorithms	CSCI	6	\N	\N	SEDS	UG	3	CSCI 152 Performance and Data Structures (489) (C- and above)	MATH 251 Discrete Mathematics (85) (D and above)	\N	Computer Science	\N	\N	\N	Spring	2026	108
CSCI	272	Formal Languages	CSCI	6	\N	\N	SEDS	UG	3	CSCI 151 Programming for Scientists and Engineers (192) (C- and above)	MATH 251 Discrete Mathematics (85) (D and above)	\N	Computer Science	\N	\N	\N	Spring	2026	109
CSCI	281	Human-Computer\nInteraction	CSCI	6	\N	\N	SEDS	UG	3	CSCI 152 Performance and Data Structures (489) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	110
CSCI	299	Internship I	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	111
CSCI	307	Research Methods	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	3 year UG SEDS Computer Science, 4 year UG SEDS Computer Science, 5 year UG SEDS Computer Science	\N	\N	\N	Spring	2026	112
CSCI	332	Operating Systems	CSCI	6	\N	\N	SEDS	UG	3	CSCI 231 Computer Systems and Organization (194) (D and above)	\N	\N	3 year UG SEDS Computer Science, 4 year UG SEDS Computer Science, 5 year UG SEDS Computer Science	\N	\N	\N	Spring	2026	113
CSCI	333	Computer Networks	CSCI	6	\N	\N	SEDS	UG	3	CSCI 152 Performance and Data Structures (489) (C- and above)	\N	\N	3 year UG SEDS Computer Science, 4 year UG SEDS Computer Science, 5 year UG SEDS Computer Science	\N	\N	\N	Spring	2026	114
CSCI	363	Software Testing and\nQuality Assurance	CSCI	6	\N	\N	SEDS	UG	3	CSCI 235 Programming Languages (638) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	115
CSCI	399	Internship II	CSCI	6	\N	\N	SEDS	UG	3	\N	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	116
CSCI	409	Senior Project II	CSCI	6	\N	\N	SEDS	UG	3	CSCI 408 Senior Project I (1481) (C- and above)	\N	\N	4 year UG SEDS Computer Science, 5 year UG SEDS Computer Science	\N	\N	\N	Spring	2026	117
CSCI	435	Blockchain and\nCryptocurrencies	CSCI	6	\N	\N	SEDS	UG	3	CSCI 270 Algorithms (648) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	118
CSCI	436	Introduction to Cloud\nComputing	CSCI	6	\N	\N	SEDS	UG	3	CSCI 333 Computer Networks (1145) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	119
CSCI	437	Internet of Things:\nTechnologies and\nApplications	CSCI	6	\N	\N	SEDS	UG	3	CSCI 333 Computer Networks (1145) (C- and above) AND ROBT 206 Microcontrollers with Lab (476) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	120
CSCI	447	Machine Learning: Theory\nand Practice	CSCI	6	\N	\N	SEDS	UG	3	MATH 273 Linear Algebra with Applications (84) (C and above) AND MATH 321 Probability (482) (C and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	121
CSCI	462	Open Source Software	CSCI	6	\N	\N	SEDS	UG	3	CSCI 361 Software Engineering (640) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	122
CSCI	490	Brain Computer Interface	CSCI	6	\N	\N	SEDS	UG	3	MATH 273 Linear Algebra with Applications (84) (C and above) AND MATH 321 Probability (482) (C and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	123
CSCI	496	Generative Artificial\nIntelligence	CSCI	6	\N	\N	SEDS	UG	3	CSCI 390 Artificial Intelligence (643) (C- and above) AND MATH 273 Linear Algebra with Applications (84) (C- and above)	\N	\N	Computer Science	\N	\N	\N	Spring	2026	124
ELCE	201	Circuits Theory II	ELCE	6	\N	\N	SEDS	UG	3	ELCE 200 Introduction to Electrical Circuits (4991) (C- and above)	\N	\N	2 year UG SEDS Electrical and Computer Engineering	3 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	144
ELCE	201L	Circuit Theory Laboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	ELCE 201 Circuit Theory (5507) (D and above)	\N	2 year UG SEDS Electrical and Computer Engineering	3 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	145
ROBT	492	Capstone Project II	ROBT	6	\N	\N	SEDS	UG	3	ROBT 491 Capstone Project I (1896) (D and above)	\N	\N	Robotics Engineering	\N	\N	\N	Spring	2026	390
ELCE	202	Digital Logic Design	ELCE	6	\N	\N	SEDS	UG	3	MATH 162 Calculus II (170) (C- and above) AND PHYS 162 Physics II for Scientists and Engineers with Laboratory (173) (C- and above) AND ENG 101 Programming for Engineers (4517) (C- and above)	\N	\N	2 year UG SEDS Electrical and Computer Engineering	3 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	146
ELCE	202L	Digital Logic Design\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	ELCE 202 Digital Logic Design (4992) (D and above)	\N	2 year UG SEDS Electrical and Computer Engineering	3 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	147
ELCE	300	Microprocessor Systems	ELCE	6	\N	\N	SEDS	UG	3	ELCE 202 Digital Logic Design (4992) (C- and above)	\N	\N	3 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	148
ELCE	300L	Microprocessor Systems\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	ELCE 300 Microprocessor Systems (6183) (C- and above)	\N	3 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	149
ELCE	302	Electric Machines	ELCE	6	\N	\N	SEDS	UG	3	ELCE 201 Circuit Theory (5507) (C- and above)	\N	\N	3 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	150
ELCE	302L	Electrical Machines\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	ELCE 201 Circuit Theory (5507) (C- and above)	ELCE 302 Electric Machines (5919) (C- and above)	\N	3 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	151
ELCE	303	Power System Analysis	ELCE	6	\N	\N	SEDS	UG	3	ELCE 200 Introduction to Electrical Circuits (4991) (C- and above)	\N	\N	3 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	\N	Spring	2026	152
ELCE	305	Data Structures and\nAlgorithms	ELCE	6	\N	\N	SEDS	UG	3	CSCI 151 Programming for Scientists and Engineers (192) (C- and above) OR ENG 101 Programming for Engineers (4517) (C- and above)	\N	\N	3 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	153
ELCE	308	Communication Systems	ELCE	6	\N	\N	SEDS	UG	3	ELCE 203 Signals and Systems (4993) (C- and above)	\N	\N	3 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	154
ELCE	311	Interdisciplinary Design\nProject	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	ENG 400 Capstone Project (6385) (C- and above)	3 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	155
ELCE	350	Electromagnetics I	ELCE	6	\N	\N	SEDS	UG	3	PHYS 162 Physics II for Scientists and Engineers with Laboratory (173) (C- and above) AND ENG 200 Engineering Mathematics III (Differential Equations and Linear Algebra) (5009) (C- and above) AND ELCE 200 Introduction to Electrical Circuits (4991) (C- and above)	\N	\N	3 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	\N	Spring	2026	156
ELCE	352	Applied Simulation\nLaboratory	ELCE	4	\N	\N	SEDS	UG	2	ELCE 200 Introduction to Electrical Circuits (4991) (D+ and above)	\N	\N	3 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	\N	Spring	2026	157
ELCE	403	Introduction to Adaptive\nSignal Processing	ELCE	6	\N	\N	SEDS	UG	3	ELCE 307 Digital Signal Processing (5921) (C- and above)	\N	\N	5 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	158
ELCE	458	Numerical Optimization\nTechniques and Computer\nApplications	ELCE	6	\N	\N	SEDS	UG	3	ENG 200 Engineering Mathematics III (Differential Equations and Linear Algebra) (5009) (C- and above)	\N	\N	5 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	159
ELCE	461	Industrial Automation	ELCE	6	\N	\N	SEDS	UG	3	ELCE 202 Digital Logic Design (4992) (C- and above)	\N	\N	4 year UG SEDS Electrical and Computer Engineering	3 year UG SEDS Electrical and Computer Engineering	\N	\N	Spring	2026	160
ELCE	461L	Industrial Automation\nLaboratory	ELCE	2	\N	\N	SEDS	UG	1	\N	ELCE 461 Industrial Automation (7020) (D and above)	\N	4 year UG SEDS Electrical and Computer Engineering	3 year UG SEDS Electrical and Computer Engineering	\N	\N	Spring	2026	161
ELCE	468	Robots For Rehabilitation	ELCE	6	\N	\N	SEDS	UG	3	\N	\N	\N	5 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	162
ELCE	469	Microfluidics\nFundamentals and\nApplications	ELCE	6	\N	\N	SEDS	UG	3	PHYS 162 Physics II for Scientists and Engineers with Laboratory (173) (C- and above) AND MATH 162 Calculus II (170) (C- and above)	\N	\N	5 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	163
ELCE	470	Optical Communications	ELCE	6	\N	\N	SEDS	UG	3	ELCE 203 Signals and Systems (4993) (C- and above)	\N	\N	5 year UG SEDS Electrical and Computer Engineering	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	Spring	2026	164
ELCE	486	Photonics for Engineering	ELCE	6	\N	\N	SEDS	UG	3	MATH 162 Calculus II (170) (C- and above) AND PHYS 162 Physics II for Scientists and Engineers with Laboratory (173) (C- and above)	\N	\N	4 year UG SEDS Electrical and Computer Engineering	Electrical and Computer Engineering	\N	\N	Spring	2026	165
ENG	101	Programming for\nEngineers	ENG	6	\N	\N	SEDS	UG	3	\N	\N	CSCI 151 Programming for Scientists and Engineers (192) (F) OR CSCI 111 Web Programming and Problem Solving (110) (F) OR CSCI 115 Programming Fundamentals (5257) (F) OR CSCI 152 Performance and Data Structures (489) (F) OR CSCI 408 Senior Project I (1481) (F) OR CSCI 409 Senior Project II (1483) (F)	SMG	1 year UG SEDS Chemical and Materials Engineering, 1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Electrical and Computer Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering, 2 year UG SEDS Chemical and Materials Engineering, 2 year UG SEDS Civil and Environmental Engineering, 2 year UG SEDS Electrical and Computer Engineering, 2 year UG SEDS Mechanical and Aerospace Engineering	SEDS	\N	Spring	2026	166
ENG	102	Engineering Materials I	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	1 year UG SEDS Civil and Environmental Engineering, 1 year UG SEDS Mechanical and Aerospace Engineering	2 year UG SEDS Civil and Environmental Engineering, 2 year UG SEDS Mechanical and Aerospace Engineering, 3 year UG SEDS Civil and Environmental Engineering, 3 year UG SEDS Mechanical and Aerospace Engineering	\N	\N	Spring	2026	167
ENG	201	Applied Probability and\nStatistics	ENG	6	\N	\N	SEDS	UG	3	MATH 162 Calculus II (170) (C- and above)	\N	\N	2 year UG SEDS Chemical and Materials Engineering, 2 year UG SEDS Civil and Environmental Engineering, 2 year UG SEDS Electrical and Computer Engineering, 2 year UG SEDS Mechanical and Aerospace Engineering	3 year UG SEDS Chemical and Materials Engineering, 3 year UG SEDS Civil and Environmental Engineering, 3 year UG SEDS Mechanical and Aerospace Engineering, 4 year UG SEDS Chemical and Materials Engineering, Electrical and Computer Engineering	4 year UG SEDS Civil and Environmental Engineering, 4 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	169
ENG	202	Numerical Methods in\nEngineering	ENG	6	\N	\N	SEDS	UG	3	ENG 200 Engineering Mathematics III (Differential Equations and Linear Algebra) (5009) (D and above)	\N	\N	2 year UG SEDS Chemical and Materials Engineering, 2 year UG SEDS Civil and Environmental Engineering, 2 year UG SEDS Mechanical and Aerospace Engineering	3 year UG SEDS Chemical and Materials Engineering, 3 year UG SEDS Civil and Environmental Engineering, 3 year UG SEDS Mechanical and Aerospace Engineering, 4 year UG SEDS Chemical and Materials Engineering	4 year UG SEDS Civil and Environmental Engineering, 4 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	170
ENG	400	Capstone Project	ENG	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Chemical and Materials Engineering, 4 year UG SEDS Civil and Environmental Engineering, 4 year UG SEDS Electrical and Computer Engineering, 4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Chemical and Materials Engineering (pending graduation), 5 year UG SEDS Mechanical and Aerospace Engineering (pending graduation), Civil and Environmental Engineering, Electrical and Computer Engineering	\N	\N	Spring	2026	171
MAE	205	Material and\nManufacturing I	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	2 year UG SEDS Mechanical and Aerospace Engineering	3 year UG SEDS Mechanical and Aerospace Engineering	4 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	244
MAE	206	Engineering Dynamics I	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	2 year UG SEDS Mechanical and Aerospace Engineering	3 year UG SEDS Mechanical and Aerospace Engineering	4 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	245
MAE	302	Machine Elements Design	MAE	6	\N	\N	SEDS	UG	3	MAE 205 Material and Manufacturing I (5534) (D and above)	\N	\N	3 year UG SEDS Mechanical and Aerospace Engineering	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	246
MAE	305	Fluid Mechanics II	MAE	6	\N	\N	SEDS	UG	3	MAE 300 Fluid Mechanics I (5926) (D and above) OR EME 275 Fluid Mechanics I (1988) (D and above)	\N	\N	3 year UG SEDS Mechanical and Aerospace Engineering	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	247
MAE	306	Computer Aided\nEngineering	MAE	6	\N	\N	SEDS	UG	3	ENG 202 Numerical Methods in Engineering (5506) (D and above) AND MAE 201 Computer Aided Design (5011) (D and above)	\N	\N	3 year UG SEDS Mechanical and Aerospace Engineering	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	248
MAE	350	Structural Mechanics II	MAE	6	\N	\N	SEDS	UG	3	MAE 200 Structural Mechanics I (5010) (D and above) OR CEE 200 Structural Mechanics I (5005) (D and above)	\N	\N	Instructor's Permission Required. Registration through Add Course form only!	\N	\N	\N	Spring	2026	249
MAE	351	Vehicle Propulsion Systems	MAE	6	\N	\N	SEDS	UG	3	MAE 301 Engineering Thermodynamics (5927) (D and above) OR BENG 226 Engineering Thermodynamics (1553) (D and above)	\N	\N	3 year UG SEDS Mechanical and Aerospace Engineering	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	250
MAE	454	Aerodynamics	MAE	6	\N	\N	SEDS	UG	3	MAE 300 Fluid Mechanics I (5926) (D and above)	\N	\N	3 year UG SEDS Mechanical and Aerospace Engineering	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	Spring	2026	251
MAE	457	Feasibility Analysis of\nClean Energy Technologies	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	\N	Spring	2026	252
MAE	463	Micro-Electro-Mechanical\nSystems and Microsystems\ntechnology	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	\N	Spring	2026	253
MAE	464	Mechanics of Soft\nMaterials	MAE	6	\N	\N	SEDS	UG	3	ENG 102 Engineering Materials I (4708) (D and above)	\N	\N	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	\N	Spring	2026	254
MAE	465	Introduction to\nMaintenance Engineering	MAE	6	\N	\N	SEDS	UG	3	ENG 201 Applied Probability and Statistics (5505) (D and above)	\N	\N	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering	\N	\N	Spring	2026	255
MAE	469	Fundamentals of Space\nFlight Dynamics	MAE	6	\N	\N	SEDS	UG	3	\N	\N	\N	4 year UG SEDS Mechanical and Aerospace Engineering	5 year UG SEDS Mechanical and Aerospace Engineering (pending graduation)	\N	\N	Spring	2026	256
ROBT	202	System Dynamics and\nModeling	ROBT	6	\N	\N	SEDS	UG	3	MATH 162 Calculus II (170) (C- and above) AND (PHYS 162 Physics II for Scientists and Engineers with Laboratory (173) (C- and above) OR PHYS 172 Physics II for Physics Majors with Laboratory (1402) (C- and above))	\N	\N	Robotics Engineering	Computer Science	\N	\N	Spring	2026	382
ROBT	204	Electrical and Electronic\nCircuits II with Lab	ROBT	8	\N	\N	SEDS	UG	4	ROBT 203 Electrical and Electronic Circuits I with Lab (62) (C- and above)	\N	\N	Robotics Engineering	\N	\N	\N	Spring	2026	383
ROBT	206	Microcontrollers with Lab	ROBT	8	\N	\N	SEDS	UG	4	CSCI 150 Fundamentals of Programming (1501) (C- and above) OR CSCI 151 Programming for Scientists and Engineers (192) (C- and above) OR ENG 101 Programming for Engineers (4517) (C- and above)	\N	\N	Computer Science, Robotics Engineering	\N	\N	\N	Spring	2026	384
ROBT	304	Electromechanical Systems\nwith lab	ROBT	8	\N	\N	SEDS	UG	4	ROBT 203 Electrical and Electronic Circuits I with Lab (62) (C- and above)	\N	\N	Robotics Engineering	\N	\N	\N	Spring	2026	385
ROBT	308	Industrial Automation	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	Robotics Engineering	Computer Science, Mathematics	\N	\N	Spring	2026	386
ROBT	312	Robotics I: Kinematics and\nDynamics	ROBT	6	\N	\N	SEDS	UG	3	ROBT 201 Mechanics: Statics and Dynamics (475) (C- and above) AND MATH 273 Linear Algebra with Applications (84) (C- and above)	\N	\N	Robotics Engineering	SEDS	\N	\N	Spring	2026	387
ROBT	391	Research methods	ROBT	6	\N	\N	SEDS	UG	3	\N	\N	\N	3 year UG SEDS Robotics Engineering	4 year UG SEDS Robotics Engineering	\N	\N	Spring	2026	388
ROBT	402	Robotic/Mechatronic\nSystem Design	ROBT	6	\N	\N	SEDS	UG	3	ROBT 204 Electrical and Electronic Circuits II with Lab (491) (C- and above) AND ROBT 206 Microcontrollers with Lab (476) (C- and above)	\N	\N	Robotics Engineering	SEDS	\N	\N	Spring	2026	389
\.


--
-- Data for Name: enrollments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.enrollments (user_id, course_id, term, year, grade, grade_points, status, created_at, updated_at) FROM stdin;
2	915	Fall	2022	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	916	Fall	2022	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	917	Fall	2022	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	918	Fall	2022	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	919	Spring	2023	A-	3.67	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	920	Spring	2023	B	3	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	921	Spring	2023	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	922	Spring	2023	B	3	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	923	Spring	2023	B	3	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	924	Fall	2023	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	925	Fall	2023	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	926	Fall	2023	A	4	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	927	Fall	2023	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	928	Fall	2023	A-	3.67	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	929	Spring	2024	A-	3.67	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	930	Spring	2024	B	3	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	931	Spring	2024	A	4	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	932	Spring	2024	A	4	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	933	Summer	2024	W*	0	WITHDRAWN	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	934	Fall	2024	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	935	Fall	2024	B-	2.67	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	936	Fall	2024	A	4	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	937	Fall	2024	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	938	Fall	2024	A-	3.67	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	939	Fall	2024	A	4	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	940	Spring	2025	C+	2.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	941	Spring	2025	A	4	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	942	Spring	2025	B-	2.67	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	943	Spring	2025	B-	2.67	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	944	Spring	2025	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	945	Fall	2025	B+	3.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	946	Fall	2025	P	0	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	947	Fall	2025	C+	2.33	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	948	Fall	2025	A-	3.67	PASSED	2026-04-20 14:27:25.046798+00	2026-04-20 14:27:25.046798+00
2	234	Spring	2026	\N	\N	IN_PROGRESS	2026-04-20 14:29:11.194836+00	2026-04-20 14:29:11.194836+00
2	227	Spring	2026	\N	\N	IN_PROGRESS	2026-04-20 14:29:16.305943+00	2026-04-20 14:29:16.305943+00
2	228	Spring	2026	\N	\N	IN_PROGRESS	2026-04-20 15:59:49.922478+00	2026-04-20 15:59:49.922478+00
2	109	Spring	2026	\N	\N	IN_PROGRESS	2026-04-20 16:00:08.867961+00	2026-04-20 16:00:08.867961+00
\.


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.events (user_id, category_id, title, description, start_at, end_at, is_all_day, location, recurrence, recurrence_end_at, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: flashcard_decks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.flashcard_decks (id, course_id, title, card_count, difficulty, owner_user_id, created_at, updated_at) FROM stdin;
4	234	Nested Cross-Validation and Regularized LDA (CSCI 447)	20	medium	2	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
\.


--
-- Data for Name: flashcard_session_cards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.flashcard_session_cards (id, session_id, flashcard_id, times_seen, times_easy, times_medium, times_hard, last_response, created_at, updated_at) FROM stdin;
44	10	45	1	1	0	0	easy	2026-04-20 15:49:43.071833+00	2026-04-20 15:49:43.071833+00
45	10	46	1	1	0	0	easy	2026-04-20 15:49:44.325199+00	2026-04-20 15:49:44.325199+00
46	10	47	1	1	0	0	easy	2026-04-20 15:49:45.155824+00	2026-04-20 15:49:45.155824+00
47	10	48	1	1	0	0	easy	2026-04-20 15:49:45.930096+00	2026-04-20 15:49:45.930096+00
48	10	49	1	1	0	0	easy	2026-04-20 15:49:46.68926+00	2026-04-20 15:49:46.68926+00
51	10	52	1	1	0	0	easy	2026-04-20 15:49:50.006963+00	2026-04-20 15:49:50.006963+00
52	10	53	1	1	0	0	easy	2026-04-20 15:49:50.725764+00	2026-04-20 15:49:50.725764+00
53	10	54	1	1	0	0	easy	2026-04-20 15:49:51.399461+00	2026-04-20 15:49:51.399461+00
54	10	55	1	1	0	0	easy	2026-04-20 15:49:52.104706+00	2026-04-20 15:49:52.104706+00
55	10	56	1	1	0	0	easy	2026-04-20 15:49:52.747763+00	2026-04-20 15:49:52.747763+00
56	10	57	1	1	0	0	easy	2026-04-20 15:49:53.369418+00	2026-04-20 15:49:53.369418+00
59	10	60	1	1	0	0	easy	2026-04-20 15:49:56.745441+00	2026-04-20 15:49:56.745441+00
60	10	61	1	1	0	0	easy	2026-04-20 15:49:57.533543+00	2026-04-20 15:49:57.533543+00
61	10	62	1	1	0	0	easy	2026-04-20 15:49:58.204872+00	2026-04-20 15:49:58.204872+00
62	10	63	1	1	0	0	easy	2026-04-20 15:49:58.840908+00	2026-04-20 15:49:58.840908+00
63	10	64	1	1	0	0	easy	2026-04-20 15:49:59.507854+00	2026-04-20 15:49:59.507854+00
49	10	50	2	1	1	0	easy	2026-04-20 15:49:47.945395+00	2026-04-20 15:50:00.16591+00
50	10	51	2	1	1	0	easy	2026-04-20 15:49:48.789477+00	2026-04-20 15:50:00.838298+00
57	10	58	2	1	0	1	easy	2026-04-20 15:49:54.61018+00	2026-04-20 15:50:01.77047+00
58	10	59	2	1	0	1	easy	2026-04-20 15:49:55.346105+00	2026-04-20 15:50:03.477774+00
\.


--
-- Data for Name: flashcard_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.flashcard_sessions (id, deck_id, user_id, status, started_at, completed_at, ai_review, created_at, updated_at) FROM stdin;
9	4	2	in_progress	2026-04-20 15:39:48.784939+00	\N	\N	2026-04-20 15:39:48.780515+00	2026-04-20 15:39:48.780515+00
10	4	2	completed	2026-04-20 15:49:39.417108+00	2026-04-20 15:50:22.073525+00	{"summary": "You performed very well on most cards but showed recurring difficulty with nested cross-validation mechanics, implementation steps, computational-cost reductions, and interpreting model-selection plots for \\u03b3. Targeted practice implementing nested CV end-to-end and focused review of cost-saving strategies and plot interpretation will close these gaps quickly.", "weak_topics": ["[Practical Implementation] Nested CV is computationally expensive. Name three ways to reduce its cost without invalidating selection.", "[Model Evaluation] How should you interpret the grand average performance plot across \\u03b3 values and what additional information should you consider before picking \\u03b3?", "[Nested Cross-Validation] Explain the roles of the inner and outer loops in nested CV.", "[Nested Cross-Validation] Give a concise step-by-step implementation plan for F-fold nested cross-validation (Algorithm 1)."], "study_plan": "\\u2022 Re-derive nested CV by hand and label operations: explicitly write the outer vs inner loop responsibilities (outer = honest test, inner = hyperparameter tuning), then walk through a tiny synthetic dataset (e.g., 100 samples) tracking indices to cement the flow.\\n\\u2022 Implement Algorithm 1 in code (or detailed pseudocode) with F outer folds and G inner folds; run it on a small dataset with verbose/logging so you can inspect selected hyperparameters per outer fold and final aggregated metrics.\\n\\u2022 Create a one-page summary of 3\\u20135 valid cost-reduction techniques (e.g., fewer inner folds, randomized/hyperband search, warm starts/early stopping, model reuse, parallelization) and for each note why it does/doesn't bias selection and when to apply it.\\n\\u2022 Improve \\u03b3-selection practice by plotting grand-average performance with error bars (std or SE), inspecting per-fold variability, and applying the 1\\u2011SE or simplest-model rule; make a short checklist (mean, CI/error bars, per-fold spread, model complexity) to consult before choosing \\u03b3."}	2026-04-20 15:49:39.408203+00	2026-04-20 15:50:04.697204+00
\.


--
-- Data for Name: flashcards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.flashcards (id, deck_id, "position", question, answer, topic, created_at, updated_at) FROM stdin;
46	4	2	Write the regularized covariance formula used in RLDA and explain the roles of γ and ν.	S˜ = (1−γ)S + γνI. γ ∈ [0,1] is the shrinkage weight controlling trust in the sample covariance S (γ=0 uses S, γ=1 uses νI). ν is the average eigenvalue of S, chosen so νI has the same trace as S.	Shrinkage & Covariance	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
47	4	3	How does increasing the shrinkage parameter γ affect the eigenvalues of the covariance estimate?	Increasing γ pulls all eigenvalues toward the mean eigenvalue ν: large eigenvalues decrease, small eigenvalues increase. This reduces variance in the eigenvalue spectrum and makes the covariance more isotropic.	Shrinkage & Covariance	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
48	4	4	What are the practical meanings of the two extremes γ=0 and γ=1 in RLDA?	γ=0: no shrinkage, use raw sample covariance S (may be noisy). γ=1: full shrinkage to νI, covariance assumed spherical with variance ν (ignores feature correlations).	Shrinkage & Covariance	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
45	4	1	What specific estimation problem does covariance shrinkage address in small-sample settings?	When sample size is too small to estimate covariance reliably, large eigenvalues are overestimated and small eigenvalues are underestimated. Shrinkage reduces this systematic bias by pulling the sample covariance toward an isotropic matrix, stabilizing eigenvalue estimates.	Shrinkage & Covariance	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
49	4	5	Why is nested cross-validation necessary when tuning hyperparameters like γ?	Nested CV prevents optimistic bias due to tuning on the same data used to evaluate performance. The inner loop selects hyperparameters; the outer loop provides an unbiased estimate of generalization for the chosen hyperparameter.	Nested Cross-Validation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
50	4	6	Explain the roles of the inner and outer loops in nested CV.	Outer loop: splits data to create hold-out test folds for final evaluation. Inner loop: within the outer training set, performs cross-validation to select hyperparameters (model selection).	Nested Cross-Validation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
51	4	7	Give a concise step-by-step implementation plan for F-fold nested cross-validation (Algorithm 1).	1) Split data into F disjoint folds. 2) For each outer fold: hold it out as test. 3) On remaining F−1 folds, run inner CV across candidate hyperparameters: train on F−2 folds, validate on the held inner fold, repeat to get average validation per hyperparameter. 4) Select best hyperparameter (inner average). 5) Retrain on all outer training folds with that hyperparameter and evaluate on the outer test fold. 6) Repeat over outer folds and aggregate results.	Nested Cross-Validation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
52	4	8	How should you choose the best γ after completing inner CV folds for one outer split?	Compute the average validation performance of each γ across the inner folds and pick the γ with the highest average (or lowest loss). If multiple close values, consider choosing the simpler (larger γ towards νI) or use ties-breaking with variance.	Nested Cross-Validation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
53	4	9	Why do you retrain the model on all outer-training data with the selected γ before testing on the outer test fold?	Retraining on the full outer training set uses all available labeled data to get the best parameter estimates for the chosen γ, producing a final model that can be fairly evaluated on the unseen outer test fold.	Nested Cross-Validation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
54	4	10	What should you store during nested CV in order to produce the ‘grand average generalization performance’ plot over γ?	For each inner CV within every outer fold, store the average validation performance for each γ. After completing all outer folds, average these stored inner-average performances across outer folds to obtain the grand average performance per γ and plot it.	Practical Implementation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
55	4	11	Why is stratified folding recommended when performing cross-validation on classification problems?	Stratified folds preserve class proportions in each split, reducing variance and bias in validation estimates, especially important for imbalanced classes to ensure each fold has representative examples.	Practical Implementation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
56	4	12	How does RLDA relate to the LDA assumption of equal class covariances?	LDA assumes all classes share a common covariance matrix. RLDA regularizes the pooled/common covariance estimate (used by LDA), making that shared covariance more stable when sample sizes are small.	LDA & Probabilistic Classification	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
57	4	13	What practical advice would you give when selecting a grid of candidate γ values?	Use a grid that spans extremes (near 0 and 1) and logarithmic spacing (because effects are nonlinear). Include values informed by sample size, add a few intermediate points, and keep grid size manageable to limit compute cost.	Practical Implementation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
58	4	14	Nested CV is computationally expensive. Name three ways to reduce its cost without invalidating selection.	1) Reduce number of outer/inner folds (e.g., 5×5 instead of 10×10). 2) Shrink hyperparameter grid using prior knowledge or coarse-to-fine search. 3) Parallelize inner-loop fits or use more efficient hyperparameter search (random search or Bayesian optimization) while still nesting properly.	Practical Implementation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
59	4	15	How should you interpret the grand average performance plot across γ values and what additional information should you consider before picking γ?	Choose γ with highest grand average performance, but also inspect variability (error bars across outer folds) and robustness: a slightly lower mean with much lower variance may be preferable. Consider complexity trade-offs and domain knowledge.	Model Evaluation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
60	4	16	Explain the conceptual connection between covariance shrinkage (S˜ = (1−γ)S + γνI) and ridge (L2) regularization.	Both add isotropic bias toward simpler solutions. Shrinkage adds νI to the covariance (stabilizing inverse covariance used by LDA); ridge adds λI to the Gram matrix (stabilizing coefficient estimates). Both reduce variance at the cost of bias.	Shrinkage & Covariance	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
61	4	17	Name an automatic alternative to manual shrinkage selection and briefly describe it.	Ledoit–Wolf shrinkage estimator automatically estimates the optimal convex shrinkage weight that minimizes mean-squared error between the true covariance and the shrinkage target, removing the need for manual γ tuning.	Shrinkage & Covariance	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
62	4	18	How do LDA probabilistic outputs provide uncertainty estimates, and how can you assess their calibration?	LDA models class-conditional Gaussians and yields posterior class probabilities via Bayes' rule. Assess calibration with reliability diagrams, Brier score, or calibration metrics (e.g., expected calibration error) to see if predicted probabilities match observed frequencies.	LDA & Probabilistic Classification	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
63	4	19	List common sources of information leakage in nested CV and how to avoid them.	Leakage sources: performing preprocessing (scaling, imputation, feature selection) before splitting, or using test fold labels in feature engineering. Avoid by performing all preprocessing and feature selection inside the inner loop using only training folds, and apply learned transforms to validation/test folds.	Practical Implementation	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
64	4	20	Why is RLDA particularly suitable for EEG data with few samples per class?	EEG features are high-dimensional and samples per class are limited, yielding unstable covariance estimates. RLDA shrinks the covariance toward an isotropic target, reducing variance of estimates and improving classifier stability and generalization.	Application: EEG	2026-04-20 15:38:43.614537+00	2026-04-20 15:38:43.614537+00
\.


--
-- Data for Name: handbook_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.handbook_plans (enrollment_year, filename, status, plans, error, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: mindmaps; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mindmaps (user_id, course_id, week, topic, tree_json, id, created_at, updated_at) FROM stdin;
2	234	1	Nested Cross-Validation	{"id": "3644de7f3188", "label": "Nested Cross-Validation", "description": "Nested cross-validation is a technique used for model selection and evaluation, especially in situations with limited data. It involves splitting the dataset into multiple folds to optimize parameters such as the shrinkage parameter \\u03b3 in regularized linear discriminant analysis (LDA). This process helps in obtaining a more reliable estimate of model performance by minimizing overfitting. The outer loop of cross-validation assesses the model's ability to generalize, while the inner loop focuses on parameter tuning. Using this method can lead to better estimates of covariance matrices and improved classifier performance.", "children": [{"id": "3c790040c50d", "label": "Regularized LDA", "description": "Regularized Linear Discriminant Analysis (LDA) is employed when insufficient data makes it difficult to accurately estimate covariance matrices. The technique adjusts the covariance matrix by shrinking it towards the identity matrix, mitigating biases in eigenvalue estimation. The regularization parameter \\u03b3 governs the extent of this shrinkage, balancing the trust in the original covariance estimate. This method is crucial for improving classification outcomes in high-dimensional spaces where data is scarce. By optimizing \\u03b3 through nested cross-validation, the model's generalization performance can be maximized.", "children": [{"id": "b68615930452", "label": "Shrinkage Parameter \\u03b3", "description": "The shrinkage parameter \\u03b3 is central to the regularization process in LDA. By adjusting \\u03b3, one can control the degree to which the covariance matrix is shrunk towards the identity matrix. A smaller value of \\u03b3 indicates less shrinkage, while larger values increase bias towards the identity matrix. The goal is to find an optimal \\u03b3 that minimizes overfitting while maintaining model accuracy. The effectiveness of different \\u03b3 values is assessed through cross-validation, allowing for a quantitative comparison of model performance under various configurations.", "children": []}, {"id": "588fa8af2b9a", "label": "Covariance Matrix Estimation", "description": "Estimating covariance matrices accurately is challenging in cases with limited data. Errors in estimating large and small eigenvalues can lead to poor model performance. Regularized LDA addresses this by providing a systematic approach to adjust covariance estimates. The proposed formula for the new covariance matrix S\\u02dc combines the original estimate with a scaled identity matrix, utilizing the average eigenvalue for correction. This adjustment is essential for reliable classification in high-dimensional data scenarios where the sample size is small.", "children": []}]}, {"id": "8f7bd38a5eb8", "label": "Model Evaluation Process", "description": "The model evaluation process in nested cross-validation involves two main loops: the outer loop for testing and the inner loop for training. In the outer loop, data is split into folds where one fold is used for testing while the rest are for training. The inner loop iterates through potential values of the shrinkage parameter \\u03b3, training the model on different combinations of the training folds. This dual-loop structure ensures that the selected model and parameters are validated against unseen data, enhancing the robustness of the evaluation process.", "children": [{"id": "8e0b6ec9fae4", "label": "Algorithm for Nested CV", "description": "The algorithm for nested cross-validation outlines the procedural steps for model selection and evaluation. It begins with splitting the data into a specified number of folds. For each outer fold, the algorithm selects the remaining folds for model training and evaluation. Within each outer iteration, the inner loop tests various parameters to find the best-performing \\u03b3. After determining the optimal parameter, the model is retrained on the full outer training data for final evaluation. This structured approach helps ensure thorough testing and parameter optimization.", "children": []}]}]}	3	2026-04-20 15:38:45.460163+00	2026-04-20 15:38:45.460163+00
\.


--
-- Data for Name: mock_exam_attempt_answers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mock_exam_attempt_answers (attempt_id, mock_exam_question_link_id, selected_option_index, is_correct, answered_at, id, created_at, updated_at) FROM stdin;
24	173	1	t	2026-04-20 15:34:55.989219+00	40	2026-04-20 15:34:33.456511+00	2026-04-20 15:34:55.969261+00
24	174	2	t	2026-04-20 15:35:42.145604+00	41	2026-04-20 15:35:42.117002+00	2026-04-20 15:35:42.117002+00
24	175	4	f	2026-04-20 15:36:31.457858+00	42	2026-04-20 15:36:30.27725+00	2026-04-20 15:36:31.431899+00
25	236	1	t	2026-04-20 17:36:55.694153+00	43	2026-04-20 17:36:55.667656+00	2026-04-20 17:36:55.667656+00
25	237	3	f	2026-04-20 17:36:58.29491+00	44	2026-04-20 17:36:58.251857+00	2026-04-20 17:36:58.251857+00
25	238	2	f	2026-04-20 17:37:00.946159+00	45	2026-04-20 17:37:00.9205+00	2026-04-20 17:37:00.9205+00
25	239	4	f	2026-04-20 17:37:02.38444+00	46	2026-04-20 17:37:02.360392+00	2026-04-20 17:37:02.360392+00
25	240	2	f	2026-04-20 17:37:04.860939+00	47	2026-04-20 17:37:04.833666+00	2026-04-20 17:37:04.833666+00
25	241	2	t	2026-04-20 17:37:06.787016+00	48	2026-04-20 17:37:06.764667+00	2026-04-20 17:37:06.764667+00
\.


--
-- Data for Name: mock_exam_attempts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mock_exam_attempts (user_id, mock_exam_id, status, started_at, submitted_at, last_active_at, current_position, answered_count, correct_count, score_pct, id, created_at, updated_at) FROM stdin;
2	27	COMPLETED	2026-04-20 15:34:16.179882+00	2026-04-20 15:36:33.661972+00	2026-04-20 15:36:33.661972+00	3	3	2	66.7	24	2026-04-20 15:34:16.160018+00	2026-04-20 15:36:33.630052+00
2	30	COMPLETED	2026-04-20 17:36:48.633525+00	2026-04-20 17:37:08.87841+00	2026-04-20 17:37:08.87841+00	7	6	2	6.7	25	2026-04-20 17:36:48.610528+00	2026-04-20 17:37:08.846726+00
\.


--
-- Data for Name: mock_exam_generation_jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mock_exam_generation_jobs (assessment_id, user_id, course_offering_id, course_id, assessment_type, assessment_number, trigger, status, run_at, attempts, celery_task_id, error_message, generated_mock_exam_id, id, created_at, updated_at, generation_options, notification_sent_at) FROM stdin;
12	2	234	121	final	1	deadline_reminder	cancelled	2026-04-20 17:11:00+00	0	04d2263c-5bbc-49c4-843a-999c6421d837	Unterminated string starting at: line 1 column 6238 (char 6237)	\N	20	2026-04-20 17:10:27.850916+00	2026-04-20 17:15:50.249526+00	\N	\N
12	2	234	121	final	1	deadline_reminder	completed	2026-04-20 17:16:00+00	1	018a6aa7-b62f-4abd-8571-2a3d52cd6d5f	\N	29	21	2026-04-20 17:15:50.249526+00	2026-04-20 17:21:04.51965+00	\N	\N
12	2	234	121	final	1	deadline_reminder	completed	2026-04-20 17:31:00+00	1	017aa43e-4726-496b-adab-1906a2e19fa1	\N	30	22	2026-04-20 17:30:27.069887+00	2026-04-20 17:33:16.10629+00	\N	2026-04-20 17:33:17.633046+00
10	2	234	121	midterm	1	deadline_reminder	cancelled	2026-05-11 07:00:00+00	0	4601b51f-bda4-4a33-97f8-2f98ee27d6ec	\N	\N	16	2026-04-20 15:24:00.747892+00	2026-04-20 15:24:50.334647+00	\N	\N
10	2	234	121	midterm	1	retry	cancelled	2026-04-20 15:24:50.364566+00	0	0bf4e1ce-0d57-4218-b3e3-a5e7269c81ec	1 validation error for GenerationResult\ncoverage_summary\n  Input should be a valid string [type=string_type, input_value={'topics_covered': ['Regu...stic derivation (107).'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/string_type	\N	17	2026-04-20 15:24:50.334647+00	2026-04-20 15:33:37.705185+00	{"difficulty": "medium", "question_count": 5, "selected_upload_ids": [11], "selected_shared_material_ids": []}	\N
10	2	234	121	midterm	1	retry	completed	2026-04-20 15:33:37.746002+00	1	14fb3551-200e-4b9f-a1fd-7e641e1d03cc	\N	27	18	2026-04-20 15:33:37.705185+00	2026-04-20 15:34:10.118269+00	{"difficulty": "medium", "question_count": 3, "selected_upload_ids": [11], "selected_shared_material_ids": []}	\N
\.


--
-- Data for Name: mock_exam_generation_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mock_exam_generation_settings (setting_key, assessment_type, enabled, model, temperature, question_count, time_limit_minutes, max_source_files, max_source_chars, regeneration_offset_hours, new_question_ratio, tricky_question_ratio, id, created_at, updated_at) FROM stdin;
default	\N	t	gpt-5-mini	0.2	20	40	6	24000	24	0.5	0.3	3	2026-04-19 13:35:51.482572+00	2026-04-19 14:09:45.308462+00
final	final	t	gpt-5-mini	0.2	30	60	6	24000	24	0.5	0.3	6	2026-04-19 13:35:51.482572+00	2026-04-19 14:09:45.308462+00
midterm	midterm	t	gpt-5-mini	0.2	20	40	6	24000	24	0.5	0.3	5	2026-04-19 13:35:51.482572+00	2026-04-19 14:09:45.308462+00
quiz	quiz	t	gpt-5-mini	0.2	12	20	6	24000	24	0.5	0.3	4	2026-04-19 13:35:51.482572+00	2026-04-19 14:09:45.308462+00
\.


--
-- Data for Name: mock_exam_question_links; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mock_exam_question_links (mock_exam_id, question_id, "position", points, id, created_at, updated_at) FROM stdin;
27	113	1	1	173	2026-04-20 15:33:37.900767+00	2026-04-20 15:33:37.900767+00
27	114	2	1	174	2026-04-20 15:33:37.900767+00	2026-04-20 15:33:37.900767+00
27	115	3	1	175	2026-04-20 15:33:37.900767+00	2026-04-20 15:33:37.900767+00
29	115	1	1	206	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	114	2	1	207	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	113	3	1	208	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	143	4	1	209	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	144	5	1	210	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	145	6	1	211	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	146	7	1	212	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	147	8	1	213	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	148	9	1	214	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	149	10	1	215	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	150	11	1	216	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	151	12	1	217	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	152	13	1	218	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	153	14	1	219	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	154	15	1	220	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	155	16	1	221	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	156	17	1	222	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	157	18	1	223	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	158	19	1	224	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	159	20	1	225	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	160	21	1	226	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	161	22	1	227	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	162	23	1	228	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	163	24	1	229	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	164	25	1	230	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	165	26	1	231	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	166	27	1	232	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	167	28	1	233	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	168	29	1	234	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
29	169	30	1	235	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00
30	169	1	1	236	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	166	2	1	237	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	162	3	1	238	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	157	4	1	239	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	156	5	1	240	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	114	6	1	241	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	113	7	1	242	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	115	8	1	243	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	168	9	1	244	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	164	10	1	245	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	160	11	1	246	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	146	12	1	247	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	145	13	1	248	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	152	14	1	249	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	151	15	1	250	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	170	16	1	251	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	171	17	1	252	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	172	18	1	253	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	173	19	1	254	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	174	20	1	255	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	175	21	1	256	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	176	22	1	257	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	177	23	1	258	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	178	24	1	259	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	179	25	1	260	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	180	26	1	261	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	181	27	1	262	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	182	28	1	263	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	183	29	1	264	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
30	184	30	1	265	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00
\.


--
-- Data for Name: mock_exam_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mock_exam_questions (course_id, historical_course_offering_id, question_text, answer_variant_1, answer_variant_2, answer_variant_3, answer_variant_4, answer_variant_5, answer_variant_6, correct_option_index, explanation, created_by_admin_id, id, created_at, updated_at, source, visibility_scope, owner_user_id, historic_section, historic_year, curation_status, submitted_by_user_id, rejection_reason) FROM stdin;
121	\N	Which of the following best explains why sample covariance matrices estimated from small datasets tend to have overestimated large eigenvalues and underestimated small eigenvalues, and how shrinkage towards the identity addresses this problem?	Small sample noise inflates variance along principal directions and shrinks variance along minor directions; shrinkage replaces S with a convex combination with νI which pulls extreme eigenvalues towards the mean eigenvalue, reducing this bias.	Small samples make the covariance matrix singular, therefore its eigenvalues are all zero; shrinkage adds νI to make eigenvalues non-zero.	Small sample estimates invert the true order of eigenvalues; shrinkage permutes eigenvalues to correct ordering.	Small samples produce independent features so covariance estimates are unbiased; shrinkage is only used to simplify computation.	\N	\N	1	With limited data the sample covariance overestimates spread along noisy principal axes and underestimates small axes because sampling variability affects eigenvalue estimates. Shrinking S towards νI (where ν is the average eigenvalue) pulls large eigenvalues down and small ones up toward the global average, counteracting that systematic bias and stabilizing the covariance estimate.	2	113	2026-04-20 15:33:37.900767+00	2026-04-20 15:33:37.900767+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which statement about nested cross-validation for selecting the shrinkage parameter γ in Regularized LDA is correct?	In nested CV you choose γ by evaluating performance on the outer test folds and then reusing the same outer folds for final accuracy reporting.	In nested CV the inner loop is used solely for hyperparameter selection (choosing γ) using only the training portion of each outer fold; the outer test fold is held out until final evaluation.	Nested CV requires that hyperparameter choices from one outer fold be applied unchanged to all other outer folds without re-estimation.	Nested CV trains on the whole dataset for each candidate γ and uses cross-validation only to estimate test error.	\N	\N	2	Nested CV separates model selection (inner loop) from final evaluation (outer loop). For each outer fold, inner CV uses only the outer training data to pick γ; the outer test fold is never used for model selection and is used only once for unbiased performance estimation.	2	114	2026-04-20 15:33:37.900767+00	2026-04-20 15:33:37.900767+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Consider a two-class Regularized LDA classifier that uses S˜=(1−γ)S+γνI for the shared covariance estimate. Assume class priors are equal. Which of the following is true as γ→1 (strong shrinkage)?	S˜ approaches νI, so the LDA decision boundary becomes a linear hyperplane perpendicular to the vector connecting class means; classification reduces to comparing Euclidean distances to the class centroids (i.e. nearest-centroid rule).	S˜ becomes equal to S, so the classifier emphasizes directions of high variance; decision boundary becomes nonlinear.	As γ→1 the covariance estimate becomes singular causing LDA to overfit and produce arbitrary decision boundaries.	S˜ approaches zero matrix so all features are ignored and the classifier always predicts the more frequent class.	\N	\N	1	When γ→1, S˜→νI, a scalar times identity. In that case LDA's quadratic terms cancel and the linear discriminant simplifies to a weight proportional to (μ1−μ2) scaled by 1/ν. With equal priors, the decision boundary is the perpendicular bisector of the two means and classification is equivalent to nearest-centroid (Euclidean) assignment.	2	115	2026-04-20 15:33:37.900767+00	2026-04-20 15:33:37.900767+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	In nested cross-validation with F outer folds and F inner folds (using the remaining F-1 folds for inner CV), how many times is a single data point used for testing across all outer folds?	Exactly once, because each outer fold holds out a disjoint test set covering all points once.	F times, once per outer fold, because every outer fold re-tests all points.	F-1 times, because inner folds also test points during model selection.	It depends on the random seed; could be multiple times due to resampling.	\N	\N	1	Outer folds partition the data into F disjoint test sets; each data point is held out exactly once as outer test. Inner folds test within training data but those are not the outer test; the outer evaluation uses each point once.	2	143	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following describes why using the outer test fold to choose the shrinkage parameter γ would bias the estimated generalization performance?	Because using the outer test fold for selection amounts to training on the test data which inflates estimated performance (optimistic bias).	Because the outer test fold contains different feature distributions that invalidate shrinkage.	Because γ is independent of the data and cannot be influenced by test performance.	Because the outer test fold has fewer examples and increases variance but does not bias performance.	\N	\N	1	Selecting hyperparameters using the outer test data leaks information about the test set into the model selection process, producing an optimistic (biased) estimate of generalization error.	2	144	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	For Regularized LDA with S=(11)S+19I, what is the effect of γ on the Mahalanobis distance used by LDA between two class means?	As γ increases, the Mahalanobis distance approaches a scaled Euclidean distance because S becomes more isotropic.	As γ increases, the Mahalanobis distance increases without bound making classes more separable.	As γ decreases, the Mahalanobis distance ignores all covariance structure and depends only on class priors.	γ does not affect the Mahalanobis distance since it cancels out in the discriminant.	\N	\N	1	Shrinking towards the identity reduces the role of covariance anisotropy; in the limit γ->1 the Mahalanobis metric becomes proportional to Euclidean (identity covariance), so distances depend only on raw coordinate differences.	2	145	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	When computing ν in the shrinkage S=(1)S+νI, ν is defined as the average eigenvalue of S. Which computationally simpler expression equals ν?	ν equals the trace(S) divided by the dimensionality d.	ν equals the determinant of S raised to the 1/d power (geometric mean).	ν equals the largest eigenvalue of S.	ν equals zero if S is singular.	\N	\N	1	The average eigenvalue equals the trace divided by d, since trace equals sum of eigenvalues; this is easier to compute than eigen-decomposition.	2	146	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which scenario makes shrinking S towards νI a poor choice?	When the true covariance is strongly diagonal but with different variances across dimensions and many samples are available.	When sample size is very small and features are approximately isotropic.	When computational resources are limited and eigen-decomposition is expensive.	When using a discriminative classifier like logistic regression that does not use covariance estimates.	\N	\N	1	If the true covariance has important directional variance differences and you have enough samples, shrinking towards the identity (which enforces equal variances) will bias estimates away from the true structure and hurt performance.	2	147	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	In the nested CV experiment described in the material, the inner loop stores average generalization performance for each γ and then the ‘‘grand average’’ across outer loops is plotted. Why is taking the grand average across outer loops useful?	It provides a more stable estimate of how γ performs across different partitions, reducing variance of the selection.	It ensures that the best γ will be the same for all outer folds.	It reduces computation by avoiding retraining on each outer fold.	It increases bias to favor smaller γ values.	\N	\N	1	Averaging inner CV results across outer folds reduces variance and shows overall trends in performance vs γ, helping choose a γ that generalizes well across splits.	2	148	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following best describes a ‘‘tricky’’ pitfall of inner CV when the hyperparameter grid includes extreme values like γ=0 and γ=1?	Extreme γ values can lead to very similar performance across inner folds, making selection unstable due to high variance of estimates.	Including γ=1 always yields the best performance so inner CV is unnecessary.	Extreme γ make the covariance matrix non-invertible which crashes LDA.	Inner CV will always pick γ=0 because it minimizes bias.	\N	\N	1	Extreme parameter choices can result in very similar classifier behavior especially with limited data, so inner CV estimates for those γ may have high variance and selection can fluctuate; careful grid design or smoothing is advisable.	2	149	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Suppose you run 10-fold nested CV to select γ from 6 candidates and report the mean accuracy across outer folds. Which of the following statements about the variance of your reported mean accuracy is true?	The reported mean has lower variance than a single train/test split estimate because it averages over many folds.	The reported mean has the same variance as any single outer fold since only outer folds matter.	Nested CV increases variance compared to non-nested CV because you do model selection many times.	Variance cannot be compared without knowing the classifier used.	\N	\N	1	Averaging test results across multiple outer folds reduces variance compared to a single split. Although nested CV involves repeated model selection, the final reported mean is an average over outer test folds giving a more stable estimate.	2	150	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	How should class imbalance be handled when performing nested cross-validation for LDA shrinkage selection?	Use stratified folds in both inner and outer loops to preserve class proportions and avoid biased estimates.	Only stratify the outer folds; inner folds can be random since they are used for selection.	Resample only in the final training on the outer fold; CV folds do not need adjustment.	Class imbalance is irrelevant for LDA as it assumes equal priors.	\N	\N	1	Stratification in both inner and outer loops helps ensure that class proportions are preserved during selection and evaluation, preventing biased performance estimates especially with small sample sizes.	2	151	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following describes how you would compute the final model after nested CV has been completed to report a single usable classifier?	Train on the entire dataset using the γ that had the best grand-average inner CV performance across outer folds.	Train separately for each outer fold and average the resulting classifiers' predictions by voting.	Use the γ selected in the last outer fold and train on the entire dataset with it.	Never train a final model; nested CV only provides performance estimates.	\N	\N	1	Common practice is to select a hyperparameter using the aggregated inner CV performance across outer folds (grand-average) and then train a final model on all data with that hyperparameter for deployment.	2	152	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	In the context of the tutorial, why is it reasonable to pick the first 500 data points for analysis when data may be more abundant?	Because the study aims to analyze performance in the low-sample regime where covariance estimates are poor and shrinkage matters.	Because the remaining data is corrupted and must be discarded.	Because LDA cannot handle more than 500 samples due to memory constraints.	Because cross-validation requires exactly 500 points to work correctly.	\N	\N	1	The tutorial focuses on small-sample effects on covariance estimation and the benefits of shrinkage; using 500 points simulates this regime even if more data exists.	2	153	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which metric is most appropriate to compare different γ values in inner CV when training probabilistic LDA classifiers?	Average log-likelihood (or cross-entropy) on held-out folds, since probabilistic outputs are available.	Training accuracy on the training folds, because it shows how well the model fits.	P-value of a t-test between class means, because it assesses separability.	The determinant of S, because larger determinants always indicate better models.	\N	\N	1	With probabilistic classifiers, log-likelihood or cross-entropy on held-out data measures quality of predicted probabilities and is more informative than classification accuracy for probabilistic model selection.	2	154	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following best characterizes the difference between shrinkage and dimensionality reduction (e.g., PCA) for stabilizing covariance estimation?	Shrinkage adjusts eigenvalues towards their mean while keeping the original basis; PCA reduces dimension by discarding small-variance directions, changing the basis.	Shrinkage and PCA are equivalent: both produce the same covariance estimate.	PCA always outperforms shrinkage because it reduces noise by removing dimensions.	Shrinkage increases model complexity while PCA decreases it.	\N	\N	1	Shrinkage modifies eigenvalues but retains full dimensionality and original feature basis. PCA projects onto a lower-dimensional subspace, explicitly removing directions assumed to be noise; they are different strategies.	2	155	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: Consider two features that are perfectly correlated in the population but due to sampling noise appear slightly different. How does shrinkage toward νI affect the estimated covariance between them and classification?	Shrinkage reduces the covariance magnitude (towards zero off-diagonals when νI has zeros off-diagonals) and can break the perceived perfect correlation, potentially improving conditioning but losing some discriminative information.	Shrinkage increases the covariance magnitude to enforce perfect correlation.	Shrinkage only affects diagonal entries so covariances remain unchanged.	Shrinkage sets covariance to ν for off-diagonals.	\N	\N	1	νI has zero off-diagonals, so convex combination with S reduces off-diagonal values towards zero; this stabilizes inversion but may remove useful correlation information if truly present.	2	156	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: You observe that the grand-average plot vs γ is flat (no clear optimum). Which of the following is the best interpretation?	The classifier's performance is robust to γ in the tested range; any γ in that range is acceptable, and picking a simple default (e.g., mid-range) is reasonable.	Nested CV failed and results should be discarded.	There is a bug because the performance must vary with γ.	You should pick the γ with the highest variance across folds rather than mean.	\N	\N	1	A flat response means performance isn't sensitive to γ for the dataset and feature set tested; selection can prefer simplicity or a value that regularizes moderately to reduce variance.	2	157	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following practical steps can reduce computation in nested CV without strongly biasing model selection for γ?	Use fewer inner folds (e.g., 5 instead of 9) or use randomized (repeated) CV with fewer repeats to estimate inner performance.	Use the outer test data as part of inner CV to increase sample size.	Evaluate γ on a single validation split instead of inner CV to get an unbiased estimate.	Increase the number of γ candidates to ensure selection stability.	\N	\N	1	Reducing inner folds reduces computation while still providing reasonable estimates. Using outer test data for selection biases results and is not recommended.	2	158	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of these is a correct statement about the relationship between regularization strength γ and bias-variance tradeoff in LDA?	Increasing γ increases bias (moves estimate toward νI) but typically reduces variance of the covariance estimate, possibly improving generalization in small-sample regimes.	Increasing γ reduces bias and increases variance.	γ affects only bias, not variance.	γ only impacts class priors, not bias-variance.	\N	\N	1	Shrinkage toward the identity imposes prior structure increasing bias but stabilizing estimates (lower variance), which can improve generalization when data is scarce.	2	159	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following is a correct consideration when choosing the grid of γ values for nested CV?	Use a logarithmic grid (spanning orders of magnitude) to capture both very small and large regularization effects.	Use equally spaced linear grid between 0 and 1 always.	Include only γ=0 and γ=1 to test extremes; intermediate values are unnecessary.	Grid choice does not matter because nested CV will interpolate missing values.	\N	\N	1	Logarithmic spacing often captures the nonlinear effect of regularization with few points, enabling exploration of orders of magnitude changes.	2	160	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	In Regularized LDA, what happens to the determinant |S| as γ increases towards 1 (assuming S is full-rank)?	The determinant approaches ν^d where d is dimensionality, because S approaches νI.	The determinant goes to zero, making S singular.	The determinant oscillates depending on eigenvectors orientation.	The determinant equals det(S) for all γ because convex combination preserves determinant.	\N	\N	1	As γ->1, S→νI and determinant → ν^d (product of eigenvalues each equal ν).	2	161	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: You perform nested CV and find that the γ chosen by inner CV varies considerably across outer folds. Which strategy is best to pick a final γ for training on the full data?	Use the grand-average performance across outer folds and choose the γ that maximizes this average; if flat, choose a moderate regularization value.	Pick the γ from the first outer fold arbitrarily to avoid overthinking.	Select the γ that appeared most often as the best across outer folds regardless of its mean performance.	Average the γ values numerically and use that average as the final γ.	\N	\N	1	Aggregating inner CV results across outer folds (grand-average) is preferred for stability. Picking arbitrarily or averaging γ numerically may not correspond to any tested candidate; voting alone ignores performance magnitude.	2	162	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following adjustments can improve covariance estimation when features have widely different scales?	Standardize features (zero mean, unit variance) before computing S so that shrinkage towards νI treats dimensions comparably.	Leave features unscaled because S naturally accounts for scale differences.	Scale features by their median absolute deviation but do not center them.	Only remove features with small variance; scaling is unnecessary for LDA.	\N	\N	1	Standardization ensures that identity prior corresponds to meaningful comparable variances across features; otherwise shrinkage may inappropriately bias dimensions.	2	163	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which property of probabilistic classifiers makes log-likelihood a preferable selection metric over accuracy in nested CV when class probabilities are required?	Log-likelihood assesses the quality of predicted probabilities (calibration and confidence) while accuracy ignores confidence and only considers thresholded predictions.	Log-likelihood always gives higher values than accuracy so it is preferred.	Accuracy is non-differentiable and cannot be used in CV.	Probabilistic classifiers do not output hard labels so accuracy cannot be computed.	\N	\N	1	If outputs are used probabilistically, selecting models with better log-likelihood yields better-calibrated probability estimates; accuracy may hide poor calibration.	2	164	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following is true about computational cost of nested CV with F outer and K inner folds and S candidate γ values for a model that trains in time T per fit?	Approximately F*K*S*T fits are required (plus final training), because for each outer fold you run inner CV across K folds for each of S parameters.	Approximately F*S*T fits are required since inner folds are parallelized inherently.	Only S*T fits are necessary because outer folds reuse inner computations.	Cost is independent of S because you can reuse matrix inverses across γ values.	\N	\N	1	Nested CV runs inner CV for each outer fold and each candidate parameter, leading to around F*K*S training runs (commonly K=F-1).	2	165	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: If the sample covariance S is rank-deficient (singular) due to fewer samples than dimensions, which immediate effect does shrinkage with any γ>0 have?	It makes S full-rank (invertible) because adding γνI adds positive values to the diagonal, lifting zero eigenvalues.	It cannot fix singularity; S remains singular.	It removes rows and columns corresponding to redundant features to make it invertible.	It changes the basis so the matrix becomes diagonal.	\N	\N	1	Adding γνI increases all eigenvalues by γν, so any zero eigenvalues become positive for γ>0, making S invertible.	2	166	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which statement correctly contrasts generative LDA and discriminative logistic regression in the small-sample regime?	LDA (generative) can be more sample-efficient if its Gaussian assumptions roughly hold because it models p(x|y), but misspecification can hurt; logistic regression (discriminative) directly models p(y|x) and may be more robust asymptotically.	Logistic regression always outperforms LDA because it has fewer assumptions.	LDA cannot produce probability estimates while logistic regression can.	In small-sample settings discriminative methods are always better because they ignore data distribution.	\N	\N	1	Generative models can outperform discriminative ones with limited data if model assumptions are correct; otherwise discriminative methods may be preferable.	2	167	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which experimental design choice in nested CV can introduce optimistic bias if performed incorrectly before CV (data leakage)?	Performing feature selection (e.g., selecting top features by correlation with labels) on the entire dataset before splitting into folds.	Standardizing features within each training fold and applying same transform to the test fold.	Using stratified folding to preserve class ratios.	Choosing γ values based on domain knowledge before CV.	\N	\N	1	Feature selection using labels on the whole dataset leaks information into CV folds and inflates performance; it must be performed inside the training folds only.	2	168	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: You observe that inner CV suggests γ=0 for most outer folds but outer test performance is worse than for γ>0. Which interpretation is most plausible?	Inner CV overfitted during model selection due to high variance and selected γ=0; outer test reveals that some regularization (γ>0) would have improved generalization.	Outer test is flawed and should be ignored when it disagrees with inner CV.	The data distribution changed between inner and outer folds making γ=0 invalid.	γ=0 is numerically unstable so inner CV cannot pick it correctly.	\N	\N	1	Selection via inner CV can still overfit to the training subsets, especially with many candidates and high variance; outer test gives unbiased estimate revealing that regularization could improve final performance.	2	169	2026-04-20 17:18:37.268714+00	2026-04-20 17:18:37.268714+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	When computing the shrinkage target S˜=(1−γ)S+γνI inside nested CV, how should ν (the average eigenvalue) be computed to avoid data leakage?	Compute ν using only the training data of the current inner fold (i.e., do not use outer test data).	Compute ν using the entire dataset before CV so that it is consistent across folds.	Compute ν using only the outer test fold to ensure unbiased estimation.	Set ν to 1 always; scaling is irrelevant for shrinkage.	\N	\N	1	Any quantity derived from data that depends on labels or features must be computed only on training data inside each fold; using the entire dataset leaks information from test sets. So ν must be computed from the training partition for each fold.	2	170	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: If the true class-conditional covariances differ substantially (i.e., LDA assumptions are violated), what is the most likely effect of using Regularized LDA with a single pooled covariance estimate and cross-validated γ?	The pooled Regularized LDA may still perform reasonably but will be suboptimal compared to a model that models separate covariances (e.g., QDA); cross-validated γ can help but cannot fully correct misspecification.	Regularized LDA will always outperform QDA because shrinkage fixes covariance differences.	Cross-validation will detect model misspecification and always pick γ=0 to avoid bias.	Pooled covariance makes class priors irrelevant and causes random predictions.	\N	\N	1	When class covariances differ, the pooled covariance assumption is violated; shrinkage stabilizes estimation but cannot model differing covariance structure. A more appropriate model (e.g., QDA or discriminative methods) might outperform LDA even with optimized γ.	2	171	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which advantage does Ledoit–Wolf (analytic) shrinkage estimation offer compared to grid-searching γ with nested CV for small to moderate datasets?	Ledoit–Wolf provides a data-driven closed-form estimate of optimal shrinkage that is computationally cheaper than nested CV and often near-optimal in mean-square error.	Ledoit–Wolf always gives the γ that maximizes classification accuracy rather than covariance MSE.	Ledoit–Wolf requires nested CV internally to compute its analytic formula, so it is more expensive.	Ledoit–Wolf does not produce an invertible covariance and therefore is unsuitable for LDA.	\N	\N	1	Ledoit–Wolf minimizes Frobenius- or MSE-based loss to estimate an optimal shrinkage intensity analytically; it avoids the heavy computation of nested CV and often yields good covariance estimates though it optimizes a different criterion than classification accuracy.	2	172	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	When standardizing features inside nested CV to improve covariance estimation, what is the correct procedure to avoid leaking information from test folds?	Fit the standardization parameters (mean and std) on the training data of each inner/outer fold and apply them to the corresponding validation/test fold.	Compute means and standard deviations on the whole dataset once and apply the same transform to all folds to keep consistency.	Standardize only the outer folds and leave inner folds unstandardized since they are used for selection.	Do not standardize features at all because covariance estimation should use raw scales.	\N	\N	1	Preprocessing steps that depend on data statistics must be computed using training data only for each fold. Using global statistics leaks information and biases CV performance estimates.	2	173	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: In the inner CV you observe exact ties in mean log-likelihood between two γ candidates. Which tie-breaking rule is least likely to worsen final outer test performance?	Choose the γ with the larger regularization (higher γ) to prefer simpler/stabler models in small-sample regimes.	Choose the smaller γ to minimize bias because tied mean likelihood implies they are equivalent.	Pick randomly between them because tie means no preference.	Choose the γ that appeared first in the candidate list to be deterministic.	\N	\N	1	When performance is tied, preferring the more regularized (simpler) model often reduces variance and helps generalization, especially in small-sample settings. Random or arbitrary choices can increase instability.	2	174	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	You want to visualize the uncertainty around the grand-average performance vs γ plot. Which of the following is the most appropriate to plot as error bars to reflect variability across outer folds?	Plot mean performance across outer folds with standard error of the mean (SEM) or 95% confidence intervals computed from outer fold means for each γ.	Plot standard deviation of scores within inner folds pooled across all outer folds treated as independent samples.	Plot the maximum and minimum scores observed across inner folds as error bars to show extreme variability.	Do not plot error bars because average performance is sufficient.	\N	\N	1	A common practice is to compute the mean performance across outer folds for each γ and display SEM or confidence intervals based on the distribution of outer fold means. Pooling inner folds violates independence assumptions; extrema are not informative about sampling uncertainty.	2	175	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	How does strong shrinkage (γ close to 1) typically affect the calibration of probability estimates produced by probabilistic LDA?	Strong shrinkage tends to produce more conservative probability estimates (closer to class priors), which may improve calibration when covariance estimates are noisy but can understate confidence when data is plentiful.	Strong shrinkage always makes probabilities overconfident, increasing calibration error.	Shrinkage does not affect probabilities, only classification boundaries.	Strong shrinkage flips class probabilities because it normalizes features incorrectly.	\N	\N	1	By moving covariance towards isotropy, shrinkage reduces extreme Mahalanobis distances and therefore predictions move closer to prior probabilities; this often improves calibration in low-sample, high-variance settings but may make probabilities too conservative if data supports more confident predictions.	2	176	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: If a dataset contains many exact duplicate samples (identical feature vectors repeated), what effect does this have on sample covariance S and on the effectiveness of shrinkage?	Duplicates reduce the effective sample size leading to rank-deficient or low-rank S; shrinkage helps by inflating small eigenvalues, but duplicates can still bias estimates since they do not add new information.	Duplicates increase the rank of S, making shrinkage unnecessary.	Duplicates have no effect because covariance computation treats each sample independently regardless of duplicates.	Duplicates change ν to zero, making shrinkage ineffective.	\N	\N	1	Repeated identical samples reduce the diversity of observations and lower effective degrees of freedom, which can cause singular or poorly conditioned covariance estimates. Shrinkage mitigates conditioning issues but cannot recover information lost due to duplication.	2	177	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which statement correctly describes the effect of computing ν from the full training set vs computing it per inner fold when using nested CV and a grid of γ values?	Computing ν per inner fold (on the inner training sets) avoids leakage and gives valid comparisons between γ candidates within inner CV; computing ν on the full outer training set (but not on outer test) is acceptable for the outer model but not for inner fold comparisons.	Computing ν on the whole dataset before CV yields the most stable ν and is recommended.	ν computed from any dataset partition is identical, so it does not matter where it is computed.	ν should always be set to the largest eigenvalue for numerical stability.	\N	\N	1	Within inner CV, ν must be computed from the inner training splits to avoid leaking validation information. For final training after selecting γ, ν can be computed from the full training data (outer training) but not including outer test.	2	178	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: You use logarithmic spacing for the γ grid [0,0.0005,0.005,0.05,0.5,1] but notice the leftmost interval between 0 and 0.0005 may hide important behavior near zero. What alternative grid strategy can you use to better explore very small γ while keeping the grid size manageable?	Use a mixed grid that includes 0 plus several very small linear spaced values near zero (e.g., 0, 1e-6, 1e-5, 1e-4) and a logarithmic spacing for larger values.	Remove 0 from the grid because it cannot be handled numerically and only use log-spaced positive values.	Use only geometric progression starting at 0.01 and ignore smaller values because they rarely matter.	Use random sampling of γ from a uniform distribution on [0,1] to find small values.	\N	\N	1	A hybrid grid that includes both very small linear steps near zero and log-spaced larger values allows exploration of near-zero behavior without exploding grid size. Zero is important to consider but may need careful numerical handling.	2	179	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which folding strategy should you use for nested CV if your EEG data contains contiguous trials that are temporally correlated?	Use grouped or blocked cross-validation that keeps temporally adjacent trials together in the same fold (e.g., leave-blocks-out) to avoid training on data that is highly correlated with the test fold.	Randomly shuffle trials and use standard k-fold CV because temporal correlation does not affect CV estimates much.	Use leave-one-sample-out CV to maximize training size, which ignores temporal dependence.	Use nested CV with more inner folds to average out temporal correlations.	\N	\N	1	When samples are temporally correlated, standard random folds can leak information between training and test sets. Grouped or blocked CV ensures that correlated samples are contained within folds, giving more realistic generalization estimates.	2	180	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Tricky: Suppose inner CV performance curves for γ are noisy and vary non-monotonically; you still want to pick a robust γ. Which regularized selection rule can help and why?	Select the simplest γ within one standard error of the best (one-standard-error rule), i.e., choose the largest γ whose mean performance is within one SEM of the maximum, favoring stability.	Always choose the γ with the absolute highest mean even if variance is large to maximize expected performance.	Choose the median γ value across folds to avoid extremes without considering performance.	Use the γ that minimizes the determinant of S˜ since smaller determinants imply better conditioning.	\N	\N	1	The one-standard-error rule trades a small loss in mean performance for lower variance by selecting a simpler (more regularized) model whose performance is statistically indistinguishable from the best. This often improves robustness on unseen data.	2	181	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which classifier is most appropriate when class means are nearly identical but covariances differ markedly between classes?	Quadratic Discriminant Analysis (QDA) because it models class-specific covariances allowing different shapes.	Linear Discriminant Analysis (LDA) because pooling covariances improves estimation when means are equal.	Nearest Centroid because it ignores covariance structure and focuses on means.	Logistic regression with L1 penalty because it enforces sparsity in covariances.	\N	\N	1	If covariances differ between classes, QDA models separate covariance matrices and can capture differing class spread, whereas LDA's pooled covariance assumption is inappropriate.	2	182	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	Which of the following is an effective computational shortcut to reduce the runtime of nested CV for selecting γ when the model training scales poorly with dimensionality?	Use fewer inner folds (e.g., 5-fold inner CV) and fewer γ candidates chosen by informed coarse-to-fine search (coarse grid then refine near promising values).	Use the outer test folds as additional inner training folds to increase data for selection.	Compute S once on the whole dataset and reuse it across all folds to avoid recomputation.	Always set γ=0.5 to avoid CV entirely because it is a safe default.	\N	\N	1	Reducing inner folds and doing a coarse-to-fine grid search reduces the number of model fits while focusing effort on promising regions; using test data for selection or reusing whole-dataset estimates causes data leakage and biased selection.	2	183	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
121	\N	When inner CV shows high variance in performance estimates, which of the following actions typically reduces the variance without introducing bias?	Increase the number of repeats (repeated CV) or average results across multiple random fold partitions while keeping folds disjoint from outer test data.	Use the outer test fold to tune hyperparameters to increase sample size for selection.	Decrease regularization to fit inner folds better, which reduces variance of selection.	Remove low-variance features entirely without recomputing within-fold statistics.	\N	\N	1	Repeating CV and averaging across random foldings reduces estimator variance. Using outer test data for tuning introduces bias; arbitrarily changing regularization or removing features without proper within-fold processing can leak information.	2	184	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	ai	personal	2	\N	\N	approved	\N	\N
\.


--
-- Data for Name: mock_exams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mock_exams (course_id, assessment_type, assessment_title, assessment_title_slug, title, version, question_count, time_limit_minutes, instructions, is_active, created_by_admin_id, id, created_at, updated_at, assessment_number, origin, visibility_scope, owner_user_id, assessment_id) FROM stdin;
121	midterm	Midterm 1	midterm-1	Midterm 1 AI Mock 1	1	3	40	Midterm 1 (CSCI 447) — answer all questions. Medium difficulty: mix of conceptual and applied short-answer multiple-choice. No external materials. Show brief justifications if needed.	t	2	27	2026-04-20 15:33:37.900767+00	2026-04-20 15:33:37.900767+00	1	ai	personal	2	10
121	final	Final 1	final-1	Final 1 AI Mock 1	1	30	60	Final exam for CSCI 447 - Machine Learning: Theory and Practice. 30 multiple-choice questions covering nested cross-validation, Regularized LDA, covariance shrinkage, model selection, probabilistic evaluation, and practical pitfalls. Medium difficulty with a subset of tricky questions.	f	2	29	2026-04-20 17:18:37.268714+00	2026-04-20 17:31:00.105501+00	1	ai	personal	2	12
121	final	Final 1	final-1	Final 1 AI Mock 2	2	30	60	Final exam for CSCI 447 - Machine Learning: Theory and Practice. 30 multiple-choice questions covering nested cross-validation, regularized LDA, shrinkage, and probabilistic evaluation. Medium difficulty; includes tricky conceptual items. Answer all questions.	t	2	30	2026-04-20 17:31:00.105501+00	2026-04-20 17:31:00.105501+00	1	ai	personal	2	12
\.


--
-- Data for Name: study_guides; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.study_guides (user_id, course_id, topic, overview_json, details_json, source_type, materials_hash, id, created_at, updated_at) FROM stdin;
2	234	Electroencephalogram (EEG) data	{"summary": "The study focuses on estimating cognitive states from EEG data using Regularized Linear Discriminant Analysis (RLDA) and nested cross-validation techniques. It addresses the challenge of insufficient data for accurately estimating covariance matrices, proposing a method to regularize these estimates through a convex combination of the sample covariance matrix and the identity matrix.", "key_points": [{"id": "1", "label": "EEG Data Analysis", "short_description": "The analysis aims to estimate cognitive states from EEG data, which is critical for understanding brain activity."}, {"id": "2", "label": "Covariance Matrix Estimation", "short_description": "Insufficient data often leads to biased estimates of covariance matrices, affecting the performance of classifiers."}, {"id": "3", "label": "Regularization Technique", "short_description": "The study introduces a method to regularize covariance estimates by combining the sample covariance matrix with the identity matrix."}, {"id": "4", "label": "Nested Cross-Validation", "short_description": "Nested cross-validation is employed to optimize the shrinkage parameter \\u03b3, allowing for better model generalization."}, {"id": "5", "label": "Model Evaluation Process", "short_description": "The process involves splitting data into folds for training and testing, ensuring robust evaluation of the RLDA classifier's performance."}]}	{"1": {"explanation": "EEG data analysis involves the interpretation of electroencephalographic signals to infer cognitive states, which are indicative of various mental processes such as attention, memory, or emotional response. Electroencephalography (EEG) is a non-invasive technique that measures electrical activity in the brain through electrodes placed on the scalp. The resulting data contains rich temporal information about brain activity, making it a valuable resource for cognitive neuroscience research. Analyzing this data allows researchers to identify patterns associated with different cognitive states, thereby enhancing our understanding of brain function and behavior.\\n\\nThe relationship between EEG data and cognitive states is established through the application of statistical and machine learning techniques. In the context of the study, Regularized Linear Discriminant Analysis (RLDA) serves as a primary method for classifying cognitive states based on EEG features. RLDA enhances the estimation process by incorporating regularization techniques that help manage challenges associated with small sample sizes, which can lead to inaccurate covariance matrix estimates. By applying a convex combination of the sample covariance matrix and the identity matrix, the method effectively stabilizes these estimates, allowing for more reliable classification of mental states. This regularization approach is particularly important in EEG studies where data scarcity can affect the performance of traditional discriminant analysis methods.\\n\\nPractically, the implications of EEG data analysis using RLDA and nested cross-validation techniques are significant for both research and clinical applications. For researchers, these methods facilitate the extraction of meaningful patterns from complex EEG datasets, enabling more robust findings in cognitive neuroscience. Clinically, accurate estimation of cognitive states has potential applications in diagnosing and monitoring neurological disorders, tailoring cognitive therapies, and developing brain-computer interfaces. The ability to reliably classify cognitive states from EEG data can lead to advancements in personalized medicine and improved interventions for individuals with cognitive impairments, ultimately contributing to better health outcomes."}}	materials	6c57bedb78ab16d9d1e5d1c96ad6827ce665b0686c3428529d6a1f00afd2b3df	3	2026-04-20 15:39:01.810899+00	2026-04-20 15:39:09.163431+00
\.


--
-- Data for Name: study_material_library_entries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.study_material_library_entries (upload_id, course_id, curated_title, curated_week, curated_by_admin_id, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: study_material_uploads; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.study_material_uploads (course_id, uploader_id, user_week, original_filename, staged_path, storage_key, content_type, file_size_bytes, upload_status, curation_status, error_message, id, created_at, updated_at) FROM stdin;
234	2	1	NestedCV_RLDA.pdf	\N	machine-learning--theory-and-practice/week_1/d28b7038-255b-4678-b872-09101dc0365e__nestedcv_rlda.pdf	application/pdf	149977	COMPLETED	NOT_REQUESTED	\N	11	2026-04-20 15:24:22.469475+00	2026-04-20 15:24:22.848706+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (email, google_id, first_name, last_name, major, study_year, cgpa, total_credits_earned, total_credits_enrolled, avatar_url, is_onboarded, is_admin, id, created_at, updated_at, kazakh_level, enrollment_year, subscribed_to_notifications) FROM stdin;
abdiakhmet.kozhamkulov@nu.edu.kz	116664860737638031794	Abdiakhmet	Kozhamkulov	Computer Science	4	3.35	216	222	https://lh3.googleusercontent.com/a/ACg8ocLWkIxl92QR2S30lvp4sURznZdUlzNgZh7M-CgXzufRZg9SPDU=s96-c	t	t	2	2026-04-20 14:27:10.068703+00	2026-04-20 14:27:31.031244+00	C1	\N	t
\.


--
-- Data for Name: week_overview_cache; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.week_overview_cache (user_id, course_id, week, summary, topics_json, materials_hash, id, created_at, updated_at) FROM stdin;
2	234	2		[]	\N	7	2026-04-20 15:38:48.09146+00	2026-04-20 15:38:48.09146+00
2	234	1	This week focuses on estimating cognitive states from EEG data using Regularized Linear Discriminant Analysis (RLDA) in scenarios with limited data. The tutorial emphasizes the importance of nested cross-validation for optimizing the shrinkage parameter (γ) to improve covariance matrix estimates, thus enhancing model generalization performance.	[{"name": "Estimating cognitive states", "source": "material"}, {"name": "Electroencephalogram (EEG) data", "source": "material"}, {"name": "Regularized Linear Discriminant Analysis", "source": "material"}, {"name": "Covariance matrix estimation", "source": "material"}, {"name": "Nested cross-validation", "source": "material"}, {"name": "Shrinkage parameter optimization", "source": "material"}, {"name": "Model selection", "source": "material"}, {"name": "Generalization performance", "source": "material"}]	6c57bedb78ab16d9d1e5d1c96ad6827ce665b0686c3428529d6a1f00afd2b3df	8	2026-04-20 15:38:46.907048+00	2026-04-20 15:38:46.907048+00
\.


--
-- Name: assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.assessments_id_seq', 12, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 1, false);


--
-- Name: course_gpa_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.course_gpa_stats_id_seq', 1, false);


--
-- Name: course_offerings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.course_offerings_id_seq', 948, true);


--
-- Name: course_reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.course_reviews_id_seq', 1, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.courses_id_seq', 458, true);


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.events_id_seq', 1, false);


--
-- Name: flashcard_decks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.flashcard_decks_id_seq', 4, true);


--
-- Name: flashcard_session_cards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.flashcard_session_cards_id_seq', 63, true);


--
-- Name: flashcard_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.flashcard_sessions_id_seq', 10, true);


--
-- Name: flashcards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.flashcards_id_seq', 64, true);


--
-- Name: handbook_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.handbook_plans_id_seq', 1, false);


--
-- Name: mindmaps_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mindmaps_id_seq', 3, true);


--
-- Name: mock_exam_attempt_answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mock_exam_attempt_answers_id_seq', 48, true);


--
-- Name: mock_exam_attempts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mock_exam_attempts_id_seq', 25, true);


--
-- Name: mock_exam_generation_jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mock_exam_generation_jobs_id_seq', 22, true);


--
-- Name: mock_exam_generation_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mock_exam_generation_settings_id_seq', 6, true);


--
-- Name: mock_exam_question_links_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mock_exam_question_links_id_seq', 265, true);


--
-- Name: mock_exam_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mock_exam_questions_id_seq', 184, true);


--
-- Name: mock_exams_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mock_exams_id_seq', 30, true);


--
-- Name: study_guides_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.study_guides_id_seq', 3, true);


--
-- Name: study_material_library_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.study_material_library_entries_id_seq', 2, true);


--
-- Name: study_material_uploads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.study_material_uploads_id_seq', 11, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: week_overview_cache_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.week_overview_cache_id_seq', 10, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: assessments assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: course_gpa_stats course_gpa_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_gpa_stats
    ADD CONSTRAINT course_gpa_stats_pkey PRIMARY KEY (id);


--
-- Name: course_offerings course_offerings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_offerings
    ADD CONSTRAINT course_offerings_pkey PRIMARY KEY (id);


--
-- Name: course_reviews course_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: enrollments enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_pkey PRIMARY KEY (user_id, course_id, term, year);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: flashcard_decks flashcard_decks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_decks
    ADD CONSTRAINT flashcard_decks_pkey PRIMARY KEY (id);


--
-- Name: flashcard_session_cards flashcard_session_cards_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_session_cards
    ADD CONSTRAINT flashcard_session_cards_pkey PRIMARY KEY (id);


--
-- Name: flashcard_sessions flashcard_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_sessions
    ADD CONSTRAINT flashcard_sessions_pkey PRIMARY KEY (id);


--
-- Name: flashcards flashcards_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcards
    ADD CONSTRAINT flashcards_pkey PRIMARY KEY (id);


--
-- Name: handbook_plans handbook_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handbook_plans
    ADD CONSTRAINT handbook_plans_pkey PRIMARY KEY (id);


--
-- Name: mindmaps mindmaps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mindmaps
    ADD CONSTRAINT mindmaps_pkey PRIMARY KEY (id);


--
-- Name: mock_exam_attempt_answers mock_exam_attempt_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempt_answers
    ADD CONSTRAINT mock_exam_attempt_answers_pkey PRIMARY KEY (id);


--
-- Name: mock_exam_attempts mock_exam_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempts
    ADD CONSTRAINT mock_exam_attempts_pkey PRIMARY KEY (id);


--
-- Name: mock_exam_generation_jobs mock_exam_generation_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_jobs
    ADD CONSTRAINT mock_exam_generation_jobs_pkey PRIMARY KEY (id);


--
-- Name: mock_exam_generation_settings mock_exam_generation_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_settings
    ADD CONSTRAINT mock_exam_generation_settings_pkey PRIMARY KEY (id);


--
-- Name: mock_exam_question_links mock_exam_question_links_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_question_links
    ADD CONSTRAINT mock_exam_question_links_pkey PRIMARY KEY (id);


--
-- Name: mock_exam_questions mock_exam_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_questions
    ADD CONSTRAINT mock_exam_questions_pkey PRIMARY KEY (id);


--
-- Name: mock_exams mock_exams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exams
    ADD CONSTRAINT mock_exams_pkey PRIMARY KEY (id);


--
-- Name: study_guides study_guides_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_guides
    ADD CONSTRAINT study_guides_pkey PRIMARY KEY (id);


--
-- Name: study_material_library_entries study_material_library_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT study_material_library_entries_pkey PRIMARY KEY (id);


--
-- Name: study_material_uploads study_material_uploads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_uploads
    ADD CONSTRAINT study_material_uploads_pkey PRIMARY KEY (id);


--
-- Name: assessments uq_assessments_identity; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT uq_assessments_identity UNIQUE (user_id, course_id, assessment_type, assessment_number);


--
-- Name: categories uq_categories_user_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT uq_categories_user_name UNIQUE (user_id, name);


--
-- Name: course_gpa_stats uq_course_gpa_stats_course_term_year_section; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_gpa_stats
    ADD CONSTRAINT uq_course_gpa_stats_course_term_year_section UNIQUE (course_id, term, year, section);


--
-- Name: course_offerings uq_course_offerings_course_term_year_section; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_offerings
    ADD CONSTRAINT uq_course_offerings_course_term_year_section UNIQUE (course_id, term, year, section);


--
-- Name: course_reviews uq_course_reviews_course_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT uq_course_reviews_course_user UNIQUE (course_id, user_id);


--
-- Name: courses uq_courses_code_level; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT uq_courses_code_level UNIQUE (code, level);


--
-- Name: flashcard_session_cards uq_flashcard_session_cards; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_session_cards
    ADD CONSTRAINT uq_flashcard_session_cards UNIQUE (session_id, flashcard_id);


--
-- Name: flashcards uq_flashcards_deck_position; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcards
    ADD CONSTRAINT uq_flashcards_deck_position UNIQUE (deck_id, "position");


--
-- Name: handbook_plans uq_handbook_plans_year; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handbook_plans
    ADD CONSTRAINT uq_handbook_plans_year UNIQUE (enrollment_year);


--
-- Name: mock_exam_attempt_answers uq_mock_exam_attempt_answers_link; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempt_answers
    ADD CONSTRAINT uq_mock_exam_attempt_answers_link UNIQUE (attempt_id, mock_exam_question_link_id);


--
-- Name: mock_exam_generation_settings uq_mock_exam_generation_settings_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_settings
    ADD CONSTRAINT uq_mock_exam_generation_settings_key UNIQUE (setting_key);


--
-- Name: mock_exam_question_links uq_mock_exam_question_links_position; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_question_links
    ADD CONSTRAINT uq_mock_exam_question_links_position UNIQUE (mock_exam_id, "position");


--
-- Name: mock_exam_question_links uq_mock_exam_question_links_question; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_question_links
    ADD CONSTRAINT uq_mock_exam_question_links_question UNIQUE (mock_exam_id, question_id);


--
-- Name: study_material_library_entries uq_study_material_library_upload; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT uq_study_material_library_upload UNIQUE (upload_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_google_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_google_id_key UNIQUE (google_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: week_overview_cache week_overview_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.week_overview_cache
    ADD CONSTRAINT week_overview_cache_pkey PRIMARY KEY (id);


--
-- Name: ix_assessments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_assessments_id ON public.assessments USING btree (id);


--
-- Name: ix_assessments_user_course; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assessments_user_course ON public.assessments USING btree (user_id, course_id);


--
-- Name: ix_assessments_user_deadline; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assessments_user_deadline ON public.assessments USING btree (user_id, deadline);


--
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_categories_id ON public.categories USING btree (id);


--
-- Name: ix_categories_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_categories_user_id ON public.categories USING btree (user_id);


--
-- Name: ix_course_gpa_stats_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_course_gpa_stats_id ON public.course_gpa_stats USING btree (id);


--
-- Name: ix_course_offerings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_course_offerings_id ON public.course_offerings USING btree (id);


--
-- Name: ix_course_reviews_course_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_course_reviews_course_id ON public.course_reviews USING btree (course_id);


--
-- Name: ix_course_reviews_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_course_reviews_id ON public.course_reviews USING btree (id);


--
-- Name: ix_course_reviews_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_course_reviews_user_id ON public.course_reviews USING btree (user_id);


--
-- Name: ix_courses_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_courses_id ON public.courses USING btree (id);


--
-- Name: ix_events_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_events_id ON public.events USING btree (id);


--
-- Name: ix_events_user_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_user_category ON public.events USING btree (user_id, category_id);


--
-- Name: ix_events_user_start_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_user_start_at ON public.events USING btree (user_id, start_at);


--
-- Name: ix_flashcard_decks_course_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flashcard_decks_course_id ON public.flashcard_decks USING btree (course_id);


--
-- Name: ix_flashcard_decks_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_flashcard_decks_id ON public.flashcard_decks USING btree (id);


--
-- Name: ix_flashcard_decks_owner_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flashcard_decks_owner_user_id ON public.flashcard_decks USING btree (owner_user_id);


--
-- Name: ix_flashcard_session_cards_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_flashcard_session_cards_id ON public.flashcard_session_cards USING btree (id);


--
-- Name: ix_flashcard_session_cards_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flashcard_session_cards_session_id ON public.flashcard_session_cards USING btree (session_id);


--
-- Name: ix_flashcard_sessions_deck_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flashcard_sessions_deck_id ON public.flashcard_sessions USING btree (deck_id);


--
-- Name: ix_flashcard_sessions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_flashcard_sessions_id ON public.flashcard_sessions USING btree (id);


--
-- Name: ix_flashcard_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flashcard_sessions_user_id ON public.flashcard_sessions USING btree (user_id);


--
-- Name: ix_flashcards_deck_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flashcards_deck_id ON public.flashcards USING btree (deck_id);


--
-- Name: ix_flashcards_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_flashcards_id ON public.flashcards USING btree (id);


--
-- Name: ix_handbook_plans_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_handbook_plans_id ON public.handbook_plans USING btree (id);


--
-- Name: ix_mindmaps_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_mindmaps_id ON public.mindmaps USING btree (id);


--
-- Name: ix_mindmaps_user_course; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mindmaps_user_course ON public.mindmaps USING btree (user_id, course_id);


--
-- Name: ix_mock_exam_attempt_answers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_mock_exam_attempt_answers_id ON public.mock_exam_attempt_answers USING btree (id);


--
-- Name: ix_mock_exam_attempts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_mock_exam_attempts_id ON public.mock_exam_attempts USING btree (id);


--
-- Name: ix_mock_exam_attempts_mock_exam_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mock_exam_attempts_mock_exam_id ON public.mock_exam_attempts USING btree (mock_exam_id);


--
-- Name: ix_mock_exam_attempts_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mock_exam_attempts_user_id ON public.mock_exam_attempts USING btree (user_id);


--
-- Name: ix_mock_exam_generation_jobs_assessment; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mock_exam_generation_jobs_assessment ON public.mock_exam_generation_jobs USING btree (assessment_id);


--
-- Name: ix_mock_exam_generation_jobs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_mock_exam_generation_jobs_id ON public.mock_exam_generation_jobs USING btree (id);


--
-- Name: ix_mock_exam_generation_jobs_status_run_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mock_exam_generation_jobs_status_run_at ON public.mock_exam_generation_jobs USING btree (status, run_at);


--
-- Name: ix_mock_exam_generation_settings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_mock_exam_generation_settings_id ON public.mock_exam_generation_settings USING btree (id);


--
-- Name: ix_mock_exam_question_links_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_mock_exam_question_links_id ON public.mock_exam_question_links USING btree (id);


--
-- Name: ix_mock_exam_questions_course_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mock_exam_questions_course_id ON public.mock_exam_questions USING btree (course_id);


--
-- Name: ix_mock_exam_questions_curation_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mock_exam_questions_curation_status ON public.mock_exam_questions USING btree (curation_status);


--
-- Name: ix_mock_exam_questions_historical_offering_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mock_exam_questions_historical_offering_id ON public.mock_exam_questions USING btree (historical_course_offering_id);


--
-- Name: ix_mock_exam_questions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_mock_exam_questions_id ON public.mock_exam_questions USING btree (id);


--
-- Name: ix_mock_exams_course_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mock_exams_course_id ON public.mock_exams USING btree (course_id);


--
-- Name: ix_mock_exams_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_mock_exams_id ON public.mock_exams USING btree (id);


--
-- Name: ix_study_guides_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_study_guides_id ON public.study_guides USING btree (id);


--
-- Name: ix_study_guides_user_course_topic; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_guides_user_course_topic ON public.study_guides USING btree (user_id, course_id, topic);


--
-- Name: ix_study_material_library_entries_course_week_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_material_library_entries_course_week_created ON public.study_material_library_entries USING btree (course_id, curated_week, created_at);


--
-- Name: ix_study_material_uploads_course_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_material_uploads_course_id ON public.study_material_uploads USING btree (course_id);


--
-- Name: ix_study_material_uploads_status_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_material_uploads_status_created ON public.study_material_uploads USING btree (upload_status, created_at);


--
-- Name: ix_study_material_uploads_uploader_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_material_uploads_uploader_id ON public.study_material_uploads USING btree (uploader_id);


--
-- Name: ix_study_material_uploads_user_course_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_material_uploads_user_course_created ON public.study_material_uploads USING btree (uploader_id, course_id, created_at);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_week_overview_cache_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_week_overview_cache_id ON public.week_overview_cache USING btree (id);


--
-- Name: ix_week_overview_cache_user_course_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_week_overview_cache_user_course_week ON public.week_overview_cache USING btree (user_id, course_id, week);


--
-- Name: uq_mock_exam_attempts_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_mock_exam_attempts_active ON public.mock_exam_attempts USING btree (user_id, mock_exam_id) WHERE (status = 'IN_PROGRESS'::public.mockexamattemptstatus);


--
-- Name: uq_mock_exams_active_course; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_mock_exams_active_course ON public.mock_exams USING btree (course_id, assessment_type, assessment_number, origin) WHERE ((is_active = true) AND (visibility_scope = 'course'::public.mockexamvisibilityscope));


--
-- Name: uq_mock_exams_active_personal; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_mock_exams_active_personal ON public.mock_exams USING btree (course_id, assessment_type, assessment_number, origin, owner_user_id) WHERE ((is_active = true) AND (visibility_scope = 'personal'::public.mockexamvisibilityscope));


--
-- Name: uq_mock_exams_version_course; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_mock_exams_version_course ON public.mock_exams USING btree (course_id, assessment_type, assessment_number, origin, version) WHERE (visibility_scope = 'course'::public.mockexamvisibilityscope);


--
-- Name: uq_mock_exams_version_personal; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_mock_exams_version_personal ON public.mock_exams USING btree (course_id, assessment_type, assessment_number, origin, owner_user_id, version) WHERE (visibility_scope = 'personal'::public.mockexamvisibilityscope);


--
-- Name: assessments assessments_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: assessments assessments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: categories categories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: course_gpa_stats course_gpa_stats_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_gpa_stats
    ADD CONSTRAINT course_gpa_stats_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: course_offerings course_offerings_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_offerings
    ADD CONSTRAINT course_offerings_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: course_reviews course_reviews_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: course_reviews course_reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: enrollments enrollments_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: enrollments enrollments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: events events_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE SET NULL;


--
-- Name: events events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: mock_exam_questions fk_mock_exam_questions_submitted_by_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_questions
    ADD CONSTRAINT fk_mock_exam_questions_submitted_by_user FOREIGN KEY (submitted_by_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: flashcard_decks flashcard_decks_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_decks
    ADD CONSTRAINT flashcard_decks_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: flashcard_decks flashcard_decks_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_decks
    ADD CONSTRAINT flashcard_decks_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: flashcard_session_cards flashcard_session_cards_flashcard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_session_cards
    ADD CONSTRAINT flashcard_session_cards_flashcard_id_fkey FOREIGN KEY (flashcard_id) REFERENCES public.flashcards(id) ON DELETE CASCADE;


--
-- Name: flashcard_session_cards flashcard_session_cards_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_session_cards
    ADD CONSTRAINT flashcard_session_cards_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.flashcard_sessions(id) ON DELETE CASCADE;


--
-- Name: flashcard_sessions flashcard_sessions_deck_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_sessions
    ADD CONSTRAINT flashcard_sessions_deck_id_fkey FOREIGN KEY (deck_id) REFERENCES public.flashcard_decks(id) ON DELETE CASCADE;


--
-- Name: flashcard_sessions flashcard_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcard_sessions
    ADD CONSTRAINT flashcard_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: flashcards flashcards_deck_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flashcards
    ADD CONSTRAINT flashcards_deck_id_fkey FOREIGN KEY (deck_id) REFERENCES public.flashcard_decks(id) ON DELETE CASCADE;


--
-- Name: mindmaps mindmaps_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mindmaps
    ADD CONSTRAINT mindmaps_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: mindmaps mindmaps_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mindmaps
    ADD CONSTRAINT mindmaps_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: mock_exam_attempt_answers mock_exam_attempt_answers_attempt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempt_answers
    ADD CONSTRAINT mock_exam_attempt_answers_attempt_id_fkey FOREIGN KEY (attempt_id) REFERENCES public.mock_exam_attempts(id) ON DELETE CASCADE;


--
-- Name: mock_exam_attempt_answers mock_exam_attempt_answers_mock_exam_question_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempt_answers
    ADD CONSTRAINT mock_exam_attempt_answers_mock_exam_question_link_id_fkey FOREIGN KEY (mock_exam_question_link_id) REFERENCES public.mock_exam_question_links(id) ON DELETE CASCADE;


--
-- Name: mock_exam_attempts mock_exam_attempts_mock_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempts
    ADD CONSTRAINT mock_exam_attempts_mock_exam_id_fkey FOREIGN KEY (mock_exam_id) REFERENCES public.mock_exams(id) ON DELETE CASCADE;


--
-- Name: mock_exam_attempts mock_exam_attempts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_attempts
    ADD CONSTRAINT mock_exam_attempts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: mock_exam_generation_jobs mock_exam_generation_jobs_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_jobs
    ADD CONSTRAINT mock_exam_generation_jobs_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.assessments(id) ON DELETE CASCADE;


--
-- Name: mock_exam_generation_jobs mock_exam_generation_jobs_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_jobs
    ADD CONSTRAINT mock_exam_generation_jobs_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: mock_exam_generation_jobs mock_exam_generation_jobs_course_offering_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_jobs
    ADD CONSTRAINT mock_exam_generation_jobs_course_offering_id_fkey FOREIGN KEY (course_offering_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: mock_exam_generation_jobs mock_exam_generation_jobs_generated_mock_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_jobs
    ADD CONSTRAINT mock_exam_generation_jobs_generated_mock_exam_id_fkey FOREIGN KEY (generated_mock_exam_id) REFERENCES public.mock_exams(id) ON DELETE SET NULL;


--
-- Name: mock_exam_generation_jobs mock_exam_generation_jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_generation_jobs
    ADD CONSTRAINT mock_exam_generation_jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: mock_exam_question_links mock_exam_question_links_mock_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_question_links
    ADD CONSTRAINT mock_exam_question_links_mock_exam_id_fkey FOREIGN KEY (mock_exam_id) REFERENCES public.mock_exams(id) ON DELETE CASCADE;


--
-- Name: mock_exam_question_links mock_exam_question_links_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_question_links
    ADD CONSTRAINT mock_exam_question_links_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.mock_exam_questions(id) ON DELETE RESTRICT;


--
-- Name: mock_exam_questions mock_exam_questions_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_questions
    ADD CONSTRAINT mock_exam_questions_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: mock_exam_questions mock_exam_questions_course_offering_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_questions
    ADD CONSTRAINT mock_exam_questions_course_offering_id_fkey FOREIGN KEY (historical_course_offering_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: mock_exam_questions mock_exam_questions_created_by_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_questions
    ADD CONSTRAINT mock_exam_questions_created_by_admin_id_fkey FOREIGN KEY (created_by_admin_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: mock_exam_questions mock_exam_questions_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exam_questions
    ADD CONSTRAINT mock_exam_questions_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: mock_exams mock_exams_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exams
    ADD CONSTRAINT mock_exams_assessment_id_fkey FOREIGN KEY (assessment_id) REFERENCES public.assessments(id) ON DELETE SET NULL;


--
-- Name: mock_exams mock_exams_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exams
    ADD CONSTRAINT mock_exams_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: mock_exams mock_exams_created_by_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exams
    ADD CONSTRAINT mock_exams_created_by_admin_id_fkey FOREIGN KEY (created_by_admin_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: mock_exams mock_exams_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mock_exams
    ADD CONSTRAINT mock_exams_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: study_guides study_guides_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_guides
    ADD CONSTRAINT study_guides_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: study_guides study_guides_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_guides
    ADD CONSTRAINT study_guides_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: study_material_library_entries study_material_library_entries_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT study_material_library_entries_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: study_material_library_entries study_material_library_entries_curated_by_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT study_material_library_entries_curated_by_admin_id_fkey FOREIGN KEY (curated_by_admin_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: study_material_library_entries study_material_library_entries_upload_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_library_entries
    ADD CONSTRAINT study_material_library_entries_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES public.study_material_uploads(id) ON DELETE CASCADE;


--
-- Name: study_material_uploads study_material_uploads_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_uploads
    ADD CONSTRAINT study_material_uploads_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: study_material_uploads study_material_uploads_uploader_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_material_uploads
    ADD CONSTRAINT study_material_uploads_uploader_id_fkey FOREIGN KEY (uploader_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: week_overview_cache week_overview_cache_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.week_overview_cache
    ADD CONSTRAINT week_overview_cache_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course_offerings(id) ON DELETE CASCADE;


--
-- Name: week_overview_cache week_overview_cache_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.week_overview_cache
    ADD CONSTRAINT week_overview_cache_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict MQV5ksn9v7fmQbd13fuyheVlwOTbn2MBfeawhDZYkY8Zrp0gpqo2hPAnC9c1NBN

