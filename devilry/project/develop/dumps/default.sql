--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO dbdev;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO dbdev;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO dbdev;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO dbdev;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO dbdev;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO dbdev;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: core_assignment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_assignment (
    id integer NOT NULL,
    short_name character varying(20) NOT NULL,
    long_name character varying(100) NOT NULL,
    publishing_time timestamp with time zone NOT NULL,
    anonymous boolean NOT NULL,
    students_can_see_points boolean NOT NULL,
    delivery_types integer NOT NULL,
    deadline_handling integer NOT NULL,
    scale_points_percent integer NOT NULL,
    first_deadline timestamp with time zone,
    max_points integer,
    passing_grade_min_points integer,
    points_to_grade_mapper character varying(25),
    grading_system_plugin_id character varying(300),
    students_can_create_groups boolean NOT NULL,
    students_can_not_create_groups_after timestamp with time zone,
    feedback_workflow character varying(50) NOT NULL,
    parentnode_id integer NOT NULL,
    CONSTRAINT core_assignment_deadline_handling_check CHECK ((deadline_handling >= 0)),
    CONSTRAINT core_assignment_delivery_types_check CHECK ((delivery_types >= 0)),
    CONSTRAINT core_assignment_max_points_check CHECK ((max_points >= 0)),
    CONSTRAINT core_assignment_passing_grade_min_points_check CHECK ((passing_grade_min_points >= 0)),
    CONSTRAINT core_assignment_scale_points_percent_check CHECK ((scale_points_percent >= 0))
);


ALTER TABLE public.core_assignment OWNER TO dbdev;

--
-- Name: core_assignment_admins; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_assignment_admins (
    id integer NOT NULL,
    assignment_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_assignment_admins OWNER TO dbdev;

--
-- Name: core_assignment_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignment_admins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_assignment_admins_id_seq OWNER TO dbdev;

--
-- Name: core_assignment_admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_assignment_admins_id_seq OWNED BY core_assignment_admins.id;


--
-- Name: core_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_assignment_id_seq OWNER TO dbdev;

--
-- Name: core_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_assignment_id_seq OWNED BY core_assignment.id;


--
-- Name: core_assignmentgroup; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_assignmentgroup (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    is_open boolean NOT NULL,
    etag timestamp with time zone NOT NULL,
    delivery_status character varying(30),
    created_datetime timestamp with time zone NOT NULL,
    copied_from_id integer,
    feedback_id integer,
    last_deadline_id integer,
    parentnode_id integer NOT NULL
);


ALTER TABLE public.core_assignmentgroup OWNER TO dbdev;

--
-- Name: core_assignmentgroup_examiners; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_assignmentgroup_examiners (
    id integer NOT NULL,
    automatic_anonymous_id character varying(255) NOT NULL,
    assignmentgroup_id integer NOT NULL,
    user_id integer NOT NULL,
    relatedexaminer_id integer
);


ALTER TABLE public.core_assignmentgroup_examiners OWNER TO dbdev;

--
-- Name: core_assignmentgroup_examiners_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignmentgroup_examiners_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_assignmentgroup_examiners_id_seq OWNER TO dbdev;

--
-- Name: core_assignmentgroup_examiners_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_assignmentgroup_examiners_id_seq OWNED BY core_assignmentgroup_examiners.id;


--
-- Name: core_assignmentgroup_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignmentgroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_assignmentgroup_id_seq OWNER TO dbdev;

--
-- Name: core_assignmentgroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_assignmentgroup_id_seq OWNED BY core_assignmentgroup.id;


--
-- Name: core_assignmentgrouptag; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_assignmentgrouptag (
    id integer NOT NULL,
    tag character varying(20) NOT NULL,
    assignment_group_id integer NOT NULL
);


ALTER TABLE public.core_assignmentgrouptag OWNER TO dbdev;

--
-- Name: core_assignmentgrouptag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignmentgrouptag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_assignmentgrouptag_id_seq OWNER TO dbdev;

--
-- Name: core_assignmentgrouptag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_assignmentgrouptag_id_seq OWNED BY core_assignmentgrouptag.id;


--
-- Name: core_candidate; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_candidate (
    id integer NOT NULL,
    candidate_id character varying(30),
    automatic_anonymous_id character varying(255) NOT NULL,
    assignment_group_id integer NOT NULL,
    student_id integer NOT NULL,
    relatedstudent_id integer
);


ALTER TABLE public.core_candidate OWNER TO dbdev;

--
-- Name: core_candidate_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_candidate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_candidate_id_seq OWNER TO dbdev;

--
-- Name: core_candidate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_candidate_id_seq OWNED BY core_candidate.id;


--
-- Name: core_deadline; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_deadline (
    id integer NOT NULL,
    deadline timestamp with time zone NOT NULL,
    text text,
    deliveries_available_before_deadline boolean NOT NULL,
    why_created character varying(50),
    added_by_id integer,
    assignment_group_id integer NOT NULL
);


ALTER TABLE public.core_deadline OWNER TO dbdev;

--
-- Name: core_deadline_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_deadline_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_deadline_id_seq OWNER TO dbdev;

--
-- Name: core_deadline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_deadline_id_seq OWNED BY core_deadline.id;


--
-- Name: core_delivery; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_delivery (
    id integer NOT NULL,
    delivery_type integer NOT NULL,
    time_of_delivery timestamp with time zone NOT NULL,
    number integer NOT NULL,
    successful boolean NOT NULL,
    alias_delivery_id integer,
    copy_of_id integer,
    deadline_id integer NOT NULL,
    delivered_by_id integer,
    last_feedback_id integer,
    CONSTRAINT core_delivery_delivery_type_check CHECK ((delivery_type >= 0)),
    CONSTRAINT core_delivery_number_check CHECK ((number >= 0))
);


ALTER TABLE public.core_delivery OWNER TO dbdev;

--
-- Name: core_delivery_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_delivery_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_delivery_id_seq OWNER TO dbdev;

--
-- Name: core_delivery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_delivery_id_seq OWNED BY core_delivery.id;


--
-- Name: core_devilryuserprofile; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_devilryuserprofile (
    id integer NOT NULL,
    full_name character varying(300),
    languagecode character varying(100),
    user_id integer NOT NULL
);


ALTER TABLE public.core_devilryuserprofile OWNER TO dbdev;

--
-- Name: core_devilryuserprofile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_devilryuserprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_devilryuserprofile_id_seq OWNER TO dbdev;

--
-- Name: core_devilryuserprofile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_devilryuserprofile_id_seq OWNED BY core_devilryuserprofile.id;


--
-- Name: core_filemeta; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_filemeta (
    id integer NOT NULL,
    filename character varying(255) NOT NULL,
    size integer NOT NULL,
    delivery_id integer NOT NULL
);


ALTER TABLE public.core_filemeta OWNER TO dbdev;

--
-- Name: core_filemeta_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_filemeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_filemeta_id_seq OWNER TO dbdev;

--
-- Name: core_filemeta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_filemeta_id_seq OWNED BY core_filemeta.id;


--
-- Name: core_groupinvite; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_groupinvite (
    id integer NOT NULL,
    sent_datetime timestamp with time zone NOT NULL,
    accepted boolean,
    responded_datetime timestamp with time zone,
    group_id integer NOT NULL,
    sent_by_id integer NOT NULL,
    sent_to_id integer NOT NULL
);


ALTER TABLE public.core_groupinvite OWNER TO dbdev;

--
-- Name: core_groupinvite_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_groupinvite_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_groupinvite_id_seq OWNER TO dbdev;

--
-- Name: core_groupinvite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_groupinvite_id_seq OWNED BY core_groupinvite.id;


--
-- Name: core_node; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_node (
    id integer NOT NULL,
    short_name character varying(20) NOT NULL,
    long_name character varying(100) NOT NULL,
    etag timestamp with time zone NOT NULL,
    parentnode_id integer
);


ALTER TABLE public.core_node OWNER TO dbdev;

--
-- Name: core_node_admins; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_node_admins (
    id integer NOT NULL,
    node_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_node_admins OWNER TO dbdev;

--
-- Name: core_node_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_node_admins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_node_admins_id_seq OWNER TO dbdev;

--
-- Name: core_node_admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_node_admins_id_seq OWNED BY core_node_admins.id;


--
-- Name: core_node_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_node_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_node_id_seq OWNER TO dbdev;

--
-- Name: core_node_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_node_id_seq OWNED BY core_node.id;


--
-- Name: core_period; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_period (
    id integer NOT NULL,
    short_name character varying(20) NOT NULL,
    long_name character varying(100) NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    etag timestamp with time zone NOT NULL,
    parentnode_id integer NOT NULL
);


ALTER TABLE public.core_period OWNER TO dbdev;

--
-- Name: core_period_admins; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_period_admins (
    id integer NOT NULL,
    period_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_period_admins OWNER TO dbdev;

--
-- Name: core_period_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_period_admins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_period_admins_id_seq OWNER TO dbdev;

--
-- Name: core_period_admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_period_admins_id_seq OWNED BY core_period_admins.id;


--
-- Name: core_period_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_period_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_period_id_seq OWNER TO dbdev;

--
-- Name: core_period_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_period_id_seq OWNED BY core_period.id;


--
-- Name: core_periodapplicationkeyvalue; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_periodapplicationkeyvalue (
    id integer NOT NULL,
    application character varying(300) NOT NULL,
    key character varying(300) NOT NULL,
    value text,
    period_id integer NOT NULL
);


ALTER TABLE public.core_periodapplicationkeyvalue OWNER TO dbdev;

--
-- Name: core_periodapplicationkeyvalue_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_periodapplicationkeyvalue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_periodapplicationkeyvalue_id_seq OWNER TO dbdev;

--
-- Name: core_periodapplicationkeyvalue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_periodapplicationkeyvalue_id_seq OWNED BY core_periodapplicationkeyvalue.id;


--
-- Name: core_pointrangetograde; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_pointrangetograde (
    id integer NOT NULL,
    minimum_points integer NOT NULL,
    maximum_points integer NOT NULL,
    grade character varying(12) NOT NULL,
    point_to_grade_map_id integer NOT NULL,
    CONSTRAINT core_pointrangetograde_maximum_points_check CHECK ((maximum_points >= 0)),
    CONSTRAINT core_pointrangetograde_minimum_points_check CHECK ((minimum_points >= 0))
);


ALTER TABLE public.core_pointrangetograde OWNER TO dbdev;

--
-- Name: core_pointrangetograde_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_pointrangetograde_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_pointrangetograde_id_seq OWNER TO dbdev;

--
-- Name: core_pointrangetograde_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_pointrangetograde_id_seq OWNED BY core_pointrangetograde.id;


--
-- Name: core_pointtogrademap; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_pointtogrademap (
    id integer NOT NULL,
    invalid boolean NOT NULL,
    assignment_id integer NOT NULL
);


ALTER TABLE public.core_pointtogrademap OWNER TO dbdev;

--
-- Name: core_pointtogrademap_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_pointtogrademap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_pointtogrademap_id_seq OWNER TO dbdev;

--
-- Name: core_pointtogrademap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_pointtogrademap_id_seq OWNED BY core_pointtogrademap.id;


--
-- Name: core_relatedexaminer; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_relatedexaminer (
    id integer NOT NULL,
    tags text,
    period_id integer NOT NULL,
    user_id integer NOT NULL,
    automatic_anonymous_id character varying(255) NOT NULL
);


ALTER TABLE public.core_relatedexaminer OWNER TO dbdev;

--
-- Name: core_relatedexaminer_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedexaminer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_relatedexaminer_id_seq OWNER TO dbdev;

--
-- Name: core_relatedexaminer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_relatedexaminer_id_seq OWNED BY core_relatedexaminer.id;


--
-- Name: core_relatedexaminersyncsystemtag; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_relatedexaminersyncsystemtag (
    id integer NOT NULL,
    tag character varying(15) NOT NULL,
    relatedexaminer_id integer NOT NULL
);


ALTER TABLE public.core_relatedexaminersyncsystemtag OWNER TO dbdev;

--
-- Name: core_relatedexaminersyncsystemtag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedexaminersyncsystemtag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_relatedexaminersyncsystemtag_id_seq OWNER TO dbdev;

--
-- Name: core_relatedexaminersyncsystemtag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_relatedexaminersyncsystemtag_id_seq OWNED BY core_relatedexaminersyncsystemtag.id;


--
-- Name: core_relatedstudent; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_relatedstudent (
    id integer NOT NULL,
    tags text,
    candidate_id character varying(30),
    automatic_anonymous_id character varying(255) NOT NULL,
    period_id integer NOT NULL,
    user_id integer NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public.core_relatedstudent OWNER TO dbdev;

--
-- Name: core_relatedstudent_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedstudent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_relatedstudent_id_seq OWNER TO dbdev;

--
-- Name: core_relatedstudent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_relatedstudent_id_seq OWNED BY core_relatedstudent.id;


--
-- Name: core_relatedstudentkeyvalue; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_relatedstudentkeyvalue (
    id integer NOT NULL,
    application character varying(300) NOT NULL,
    key character varying(300) NOT NULL,
    value text,
    student_can_read boolean NOT NULL,
    relatedstudent_id integer NOT NULL
);


ALTER TABLE public.core_relatedstudentkeyvalue OWNER TO dbdev;

--
-- Name: core_relatedstudentkeyvalue_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedstudentkeyvalue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_relatedstudentkeyvalue_id_seq OWNER TO dbdev;

--
-- Name: core_relatedstudentkeyvalue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_relatedstudentkeyvalue_id_seq OWNED BY core_relatedstudentkeyvalue.id;


--
-- Name: core_relatedstudentsyncsystemtag; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_relatedstudentsyncsystemtag (
    id integer NOT NULL,
    tag character varying(15) NOT NULL,
    relatedstudent_id integer NOT NULL
);


ALTER TABLE public.core_relatedstudentsyncsystemtag OWNER TO dbdev;

--
-- Name: core_relatedstudentsyncsystemtag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedstudentsyncsystemtag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_relatedstudentsyncsystemtag_id_seq OWNER TO dbdev;

--
-- Name: core_relatedstudentsyncsystemtag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_relatedstudentsyncsystemtag_id_seq OWNED BY core_relatedstudentsyncsystemtag.id;


--
-- Name: core_staticfeedback; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_staticfeedback (
    id integer NOT NULL,
    rendered_view text NOT NULL,
    grade character varying(12) NOT NULL,
    points integer NOT NULL,
    is_passing_grade boolean NOT NULL,
    save_timestamp timestamp with time zone,
    delivery_id integer NOT NULL,
    saved_by_id integer NOT NULL,
    CONSTRAINT core_staticfeedback_points_check CHECK ((points >= 0))
);


ALTER TABLE public.core_staticfeedback OWNER TO dbdev;

--
-- Name: core_staticfeedback_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_staticfeedback_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_staticfeedback_id_seq OWNER TO dbdev;

--
-- Name: core_staticfeedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_staticfeedback_id_seq OWNED BY core_staticfeedback.id;


--
-- Name: core_staticfeedbackfileattachment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_staticfeedbackfileattachment (
    id integer NOT NULL,
    filename text NOT NULL,
    file character varying(100) NOT NULL,
    staticfeedback_id integer NOT NULL
);


ALTER TABLE public.core_staticfeedbackfileattachment OWNER TO dbdev;

--
-- Name: core_staticfeedbackfileattachment_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_staticfeedbackfileattachment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_staticfeedbackfileattachment_id_seq OWNER TO dbdev;

--
-- Name: core_staticfeedbackfileattachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_staticfeedbackfileattachment_id_seq OWNED BY core_staticfeedbackfileattachment.id;


--
-- Name: core_subject; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_subject (
    id integer NOT NULL,
    short_name character varying(20) NOT NULL,
    long_name character varying(100) NOT NULL,
    etag timestamp with time zone NOT NULL,
    parentnode_id integer NOT NULL
);


ALTER TABLE public.core_subject OWNER TO dbdev;

--
-- Name: core_subject_admins; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_subject_admins (
    id integer NOT NULL,
    subject_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.core_subject_admins OWNER TO dbdev;

--
-- Name: core_subject_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_subject_admins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_subject_admins_id_seq OWNER TO dbdev;

--
-- Name: core_subject_admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_subject_admins_id_seq OWNED BY core_subject_admins.id;


--
-- Name: core_subject_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_subject_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_subject_id_seq OWNER TO dbdev;

--
-- Name: core_subject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_subject_id_seq OWNED BY core_subject.id;


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadata; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE cradmin_generic_token_with_metadata_generictokenwithmetadata (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    token character varying(100) NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    expiration_datetime timestamp with time zone,
    single_use boolean NOT NULL,
    metadata_json text NOT NULL,
    object_id integer NOT NULL,
    content_type_id integer NOT NULL,
    CONSTRAINT cradmin_generic_token_with_metadata_generictoke_object_id_check CHECK ((object_id >= 0))
);


ALTER TABLE public.cradmin_generic_token_with_metadata_generictokenwithmetadata OWNER TO dbdev;

--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq OWNER TO dbdev;

--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq OWNED BY cradmin_generic_token_with_metadata_generictokenwithmetadata.id;


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE cradmin_temporaryfileuploadstore_temporaryfile (
    id integer NOT NULL,
    filename text NOT NULL,
    file character varying(100) NOT NULL,
    mimetype text NOT NULL,
    collection_id integer NOT NULL
);


ALTER TABLE public.cradmin_temporaryfileuploadstore_temporaryfile OWNER TO dbdev;

--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE cradmin_temporaryfileuploadstore_temporaryfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cradmin_temporaryfileuploadstore_temporaryfile_id_seq OWNER TO dbdev;

--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE cradmin_temporaryfileuploadstore_temporaryfile_id_seq OWNED BY cradmin_temporaryfileuploadstore_temporaryfile.id;


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE cradmin_temporaryfileuploadstore_temporaryfilecollection (
    id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    minutes_to_live integer NOT NULL,
    accept text NOT NULL,
    max_filename_length integer,
    unique_filenames boolean NOT NULL,
    user_id integer NOT NULL,
    singlemode boolean NOT NULL,
    max_filesize_bytes integer,
    CONSTRAINT cradmin_temporaryfileuploadstore_tempo_max_filesize_bytes_check CHECK ((max_filesize_bytes >= 0)),
    CONSTRAINT cradmin_temporaryfileuploadstore_temporar_minutes_to_live_check CHECK ((minutes_to_live >= 0))
);


ALTER TABLE public.cradmin_temporaryfileuploadstore_temporaryfilecollection OWNER TO dbdev;

--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq OWNER TO dbdev;

--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq OWNED BY cradmin_temporaryfileuploadstore_temporaryfilecollection.id;


--
-- Name: devilry_account_periodpermissiongroup; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_account_periodpermissiongroup (
    id integer NOT NULL,
    period_id integer NOT NULL,
    permissiongroup_id integer NOT NULL
);


ALTER TABLE public.devilry_account_periodpermissiongroup OWNER TO dbdev;

--
-- Name: devilry_account_periodpermissiongroup_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_periodpermissiongroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_account_periodpermissiongroup_id_seq OWNER TO dbdev;

--
-- Name: devilry_account_periodpermissiongroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_account_periodpermissiongroup_id_seq OWNED BY devilry_account_periodpermissiongroup.id;


--
-- Name: devilry_account_permissiongroup; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_account_permissiongroup (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    updated_datetime timestamp with time zone NOT NULL,
    syncsystem_update_datetime timestamp with time zone,
    grouptype character varying(30) NOT NULL,
    is_custom_manageable boolean NOT NULL
);


ALTER TABLE public.devilry_account_permissiongroup OWNER TO dbdev;

--
-- Name: devilry_account_permissiongroup_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_permissiongroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_account_permissiongroup_id_seq OWNER TO dbdev;

--
-- Name: devilry_account_permissiongroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_account_permissiongroup_id_seq OWNED BY devilry_account_permissiongroup.id;


--
-- Name: devilry_account_permissiongroupuser; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_account_permissiongroupuser (
    id integer NOT NULL,
    permissiongroup_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.devilry_account_permissiongroupuser OWNER TO dbdev;

--
-- Name: devilry_account_permissiongroupuser_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_permissiongroupuser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_account_permissiongroupuser_id_seq OWNER TO dbdev;

--
-- Name: devilry_account_permissiongroupuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_account_permissiongroupuser_id_seq OWNED BY devilry_account_permissiongroupuser.id;


--
-- Name: devilry_account_subjectpermissiongroup; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_account_subjectpermissiongroup (
    id integer NOT NULL,
    permissiongroup_id integer NOT NULL,
    subject_id integer NOT NULL
);


ALTER TABLE public.devilry_account_subjectpermissiongroup OWNER TO dbdev;

--
-- Name: devilry_account_subjectpermissiongroup_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_subjectpermissiongroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_account_subjectpermissiongroup_id_seq OWNER TO dbdev;

--
-- Name: devilry_account_subjectpermissiongroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_account_subjectpermissiongroup_id_seq OWNED BY devilry_account_subjectpermissiongroup.id;


--
-- Name: devilry_account_user; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_account_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    shortname character varying(255) NOT NULL,
    fullname text NOT NULL,
    lastname text NOT NULL,
    datetime_joined timestamp with time zone NOT NULL,
    suspended_datetime timestamp with time zone,
    suspended_reason text NOT NULL,
    languagecode character varying(10) NOT NULL
);


ALTER TABLE public.devilry_account_user OWNER TO dbdev;

--
-- Name: devilry_account_user_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_account_user_id_seq OWNER TO dbdev;

--
-- Name: devilry_account_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_account_user_id_seq OWNED BY devilry_account_user.id;


--
-- Name: devilry_account_useremail; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_account_useremail (
    id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    last_updated_datetime timestamp with time zone NOT NULL,
    email character varying(255) NOT NULL,
    use_for_notifications boolean NOT NULL,
    is_primary boolean,
    user_id integer NOT NULL
);


ALTER TABLE public.devilry_account_useremail OWNER TO dbdev;

--
-- Name: devilry_account_useremail_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_useremail_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_account_useremail_id_seq OWNER TO dbdev;

--
-- Name: devilry_account_useremail_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_account_useremail_id_seq OWNED BY devilry_account_useremail.id;


--
-- Name: devilry_account_username; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_account_username (
    id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    last_updated_datetime timestamp with time zone NOT NULL,
    username character varying(255) NOT NULL,
    is_primary boolean,
    user_id integer NOT NULL
);


ALTER TABLE public.devilry_account_username OWNER TO dbdev;

--
-- Name: devilry_account_username_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_username_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_account_username_id_seq OWNER TO dbdev;

--
-- Name: devilry_account_username_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_account_username_id_seq OWNED BY devilry_account_username.id;


--
-- Name: devilry_comment_comment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_comment_comment (
    id integer NOT NULL,
    text character varying(4096) NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    published_datetime timestamp with time zone,
    user_role character varying(42) NOT NULL,
    comment_type character varying(42) NOT NULL,
    parent_id integer,
    user_id integer NOT NULL
);


ALTER TABLE public.devilry_comment_comment OWNER TO dbdev;

--
-- Name: devilry_comment_comment_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_comment_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_comment_comment_id_seq OWNER TO dbdev;

--
-- Name: devilry_comment_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_comment_comment_id_seq OWNED BY devilry_comment_comment.id;


--
-- Name: devilry_comment_commentfile; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_comment_commentfile (
    id integer NOT NULL,
    mimetype character varying(42) NOT NULL,
    file character varying(512) NOT NULL,
    filename character varying(255) NOT NULL,
    filesize integer NOT NULL,
    processing_started_datetime timestamp with time zone,
    processing_completed_datetime timestamp with time zone,
    processing_successful boolean NOT NULL,
    comment_id integer NOT NULL,
    CONSTRAINT devilry_comment_commentfile_filesize_check CHECK ((filesize >= 0))
);


ALTER TABLE public.devilry_comment_commentfile OWNER TO dbdev;

--
-- Name: devilry_comment_commentfile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_comment_commentfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_comment_commentfile_id_seq OWNER TO dbdev;

--
-- Name: devilry_comment_commentfile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_comment_commentfile_id_seq OWNED BY devilry_comment_commentfile.id;


--
-- Name: devilry_comment_commentfileimage; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_comment_commentfileimage (
    id integer NOT NULL,
    image character varying(512) NOT NULL,
    image_width integer NOT NULL,
    image_height integer NOT NULL,
    thumbnail character varying(512) NOT NULL,
    thumbnail_width integer NOT NULL,
    thumbnail_height integer NOT NULL,
    comment_file_id integer NOT NULL,
    CONSTRAINT devilry_comment_commentfileimage_image_height_check CHECK ((image_height >= 0)),
    CONSTRAINT devilry_comment_commentfileimage_image_width_check CHECK ((image_width >= 0)),
    CONSTRAINT devilry_comment_commentfileimage_thumbnail_height_check CHECK ((thumbnail_height >= 0)),
    CONSTRAINT devilry_comment_commentfileimage_thumbnail_width_check CHECK ((thumbnail_width >= 0))
);


ALTER TABLE public.devilry_comment_commentfileimage OWNER TO dbdev;

--
-- Name: devilry_comment_commentfileimage_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_comment_commentfileimage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_comment_commentfileimage_id_seq OWNER TO dbdev;

--
-- Name: devilry_comment_commentfileimage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_comment_commentfileimage_id_seq OWNED BY devilry_comment_commentfileimage.id;


--
-- Name: devilry_detektor_comparetwocacheitem; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_detektor_comparetwocacheitem (
    id integer NOT NULL,
    scaled_points integer NOT NULL,
    summary_json text NOT NULL,
    language_id integer NOT NULL,
    parseresult1_id integer NOT NULL,
    parseresult2_id integer NOT NULL
);


ALTER TABLE public.devilry_detektor_comparetwocacheitem OWNER TO dbdev;

--
-- Name: devilry_detektor_comparetwocacheitem_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_detektor_comparetwocacheitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_detektor_comparetwocacheitem_id_seq OWNER TO dbdev;

--
-- Name: devilry_detektor_comparetwocacheitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_detektor_comparetwocacheitem_id_seq OWNED BY devilry_detektor_comparetwocacheitem.id;


--
-- Name: devilry_detektor_detektorassignment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_detektor_detektorassignment (
    id integer NOT NULL,
    status character varying(12) NOT NULL,
    processing_started_datetime timestamp with time zone,
    assignment_id integer NOT NULL,
    processing_started_by_id integer
);


ALTER TABLE public.devilry_detektor_detektorassignment OWNER TO dbdev;

--
-- Name: devilry_detektor_detektorassignment_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_detektor_detektorassignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_detektor_detektorassignment_id_seq OWNER TO dbdev;

--
-- Name: devilry_detektor_detektorassignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_detektor_detektorassignment_id_seq OWNED BY devilry_detektor_detektorassignment.id;


--
-- Name: devilry_detektor_detektorassignmentcachelanguage; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_detektor_detektorassignmentcachelanguage (
    id integer NOT NULL,
    language character varying(255) NOT NULL,
    detektorassignment_id integer NOT NULL
);


ALTER TABLE public.devilry_detektor_detektorassignmentcachelanguage OWNER TO dbdev;

--
-- Name: devilry_detektor_detektorassignmentcachelanguage_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_detektor_detektorassignmentcachelanguage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_detektor_detektorassignmentcachelanguage_id_seq OWNER TO dbdev;

--
-- Name: devilry_detektor_detektorassignmentcachelanguage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_detektor_detektorassignmentcachelanguage_id_seq OWNED BY devilry_detektor_detektorassignmentcachelanguage.id;


--
-- Name: devilry_detektor_detektordeliveryparseresult; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_detektor_detektordeliveryparseresult (
    id integer NOT NULL,
    language character varying(255) NOT NULL,
    operators_string text NOT NULL,
    keywords_string text NOT NULL,
    number_of_operators integer NOT NULL,
    number_of_keywords integer NOT NULL,
    operators_and_keywords_string text NOT NULL,
    normalized_sourcecode text,
    parsed_functions_json text,
    delivery_id integer NOT NULL,
    detektorassignment_id integer NOT NULL
);


ALTER TABLE public.devilry_detektor_detektordeliveryparseresult OWNER TO dbdev;

--
-- Name: devilry_detektor_detektordeliveryparseresult_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_detektor_detektordeliveryparseresult_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_detektor_detektordeliveryparseresult_id_seq OWNER TO dbdev;

--
-- Name: devilry_detektor_detektordeliveryparseresult_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_detektor_detektordeliveryparseresult_id_seq OWNED BY devilry_detektor_detektordeliveryparseresult.id;


--
-- Name: devilry_gradingsystem_feedbackdraft; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_gradingsystem_feedbackdraft (
    id integer NOT NULL,
    feedbacktext_editor character varying(20) NOT NULL,
    feedbacktext_raw text,
    feedbacktext_html text,
    points integer NOT NULL,
    published boolean NOT NULL,
    save_timestamp timestamp with time zone NOT NULL,
    delivery_id integer NOT NULL,
    saved_by_id integer NOT NULL,
    staticfeedback_id integer,
    CONSTRAINT devilry_gradingsystem_feedbackdraft_points_check CHECK ((points >= 0))
);


ALTER TABLE public.devilry_gradingsystem_feedbackdraft OWNER TO dbdev;

--
-- Name: devilry_gradingsystem_feedbackdraft_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_gradingsystem_feedbackdraft_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_gradingsystem_feedbackdraft_id_seq OWNER TO dbdev;

--
-- Name: devilry_gradingsystem_feedbackdraft_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_gradingsystem_feedbackdraft_id_seq OWNED BY devilry_gradingsystem_feedbackdraft.id;


--
-- Name: devilry_gradingsystem_feedbackdraftfile; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_gradingsystem_feedbackdraftfile (
    id integer NOT NULL,
    filename text NOT NULL,
    file character varying(100) NOT NULL,
    delivery_id integer NOT NULL,
    saved_by_id integer NOT NULL
);


ALTER TABLE public.devilry_gradingsystem_feedbackdraftfile OWNER TO dbdev;

--
-- Name: devilry_gradingsystem_feedbackdraftfile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_gradingsystem_feedbackdraftfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_gradingsystem_feedbackdraftfile_id_seq OWNER TO dbdev;

--
-- Name: devilry_gradingsystem_feedbackdraftfile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_gradingsystem_feedbackdraftfile_id_seq OWNED BY devilry_gradingsystem_feedbackdraftfile.id;


--
-- Name: devilry_group_feedbackset; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_group_feedbackset (
    id integer NOT NULL,
    points integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    published_datetime timestamp with time zone,
    deadline_datetime timestamp with time zone,
    created_by_id integer NOT NULL,
    group_id integer NOT NULL,
    published_by_id integer NOT NULL,
    CONSTRAINT devilry_group_feedbackset_points_check CHECK ((points >= 0))
);


ALTER TABLE public.devilry_group_feedbackset OWNER TO dbdev;

--
-- Name: devilry_group_feedbackset_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_group_feedbackset_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_group_feedbackset_id_seq OWNER TO dbdev;

--
-- Name: devilry_group_feedbackset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_group_feedbackset_id_seq OWNED BY devilry_group_feedbackset.id;


--
-- Name: devilry_group_groupcomment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_group_groupcomment (
    comment_ptr_id integer NOT NULL,
    instant_publish boolean NOT NULL,
    visible_for_students boolean NOT NULL,
    feedback_set_id integer NOT NULL
);


ALTER TABLE public.devilry_group_groupcomment OWNER TO dbdev;

--
-- Name: devilry_group_imageannotationcomment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_group_imageannotationcomment (
    comment_ptr_id integer NOT NULL,
    instant_publish boolean NOT NULL,
    visible_for_students boolean NOT NULL,
    x_coordinate integer NOT NULL,
    y_coordinate integer NOT NULL,
    feedback_set_id integer NOT NULL,
    image_id integer NOT NULL,
    CONSTRAINT devilry_group_imageannotationcomment_x_coordinate_check CHECK ((x_coordinate >= 0)),
    CONSTRAINT devilry_group_imageannotationcomment_y_coordinate_check CHECK ((y_coordinate >= 0))
);


ALTER TABLE public.devilry_group_imageannotationcomment OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_deadlinetag; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_qualifiesforexam_deadlinetag (
    id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    tag character varying(30)
);


ALTER TABLE public.devilry_qualifiesforexam_deadlinetag OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_deadlinetag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_qualifiesforexam_deadlinetag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_qualifiesforexam_deadlinetag_id_seq OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_deadlinetag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_qualifiesforexam_deadlinetag_id_seq OWNED BY devilry_qualifiesforexam_deadlinetag.id;


--
-- Name: devilry_qualifiesforexam_periodtag; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_qualifiesforexam_periodtag (
    period_id integer NOT NULL,
    deadlinetag_id integer NOT NULL
);


ALTER TABLE public.devilry_qualifiesforexam_periodtag OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_qualifiesforexam_qualifiesforfinalexam (
    id integer NOT NULL,
    qualifies boolean,
    relatedstudent_id integer NOT NULL,
    status_id integer NOT NULL
);


ALTER TABLE public.devilry_qualifiesforexam_qualifiesforfinalexam OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_qualifiesforexam_qualifiesforfinalexam_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_qualifiesforexam_qualifiesforfinalexam_id_seq OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_qualifiesforexam_qualifiesforfinalexam_id_seq OWNED BY devilry_qualifiesforexam_qualifiesforfinalexam.id;


--
-- Name: devilry_qualifiesforexam_status; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_qualifiesforexam_status (
    id integer NOT NULL,
    status character varying(30) NOT NULL,
    createtime timestamp with time zone NOT NULL,
    message text NOT NULL,
    plugin character varying(500),
    exported_timestamp timestamp with time zone,
    period_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.devilry_qualifiesforexam_status OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_status_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_qualifiesforexam_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_qualifiesforexam_status_id_seq OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_qualifiesforexam_status_id_seq OWNED BY devilry_qualifiesforexam_status.id;


--
-- Name: devilry_student_uploadeddeliveryfile; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_student_uploadeddeliveryfile (
    id integer NOT NULL,
    uploaded_datetime timestamp with time zone NOT NULL,
    uploaded_file character varying(100) NOT NULL,
    filename character varying(255) NOT NULL,
    deadline_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.devilry_student_uploadeddeliveryfile OWNER TO dbdev;

--
-- Name: devilry_student_uploadeddeliveryfile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_student_uploadeddeliveryfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devilry_student_uploadeddeliveryfile_id_seq OWNER TO dbdev;

--
-- Name: devilry_student_uploadeddeliveryfile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_student_uploadeddeliveryfile_id_seq OWNED BY devilry_student_uploadeddeliveryfile.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO dbdev;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO dbdev;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO dbdev;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO dbdev;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO dbdev;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO dbdev;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO dbdev;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment ALTER COLUMN id SET DEFAULT nextval('core_assignment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment_admins ALTER COLUMN id SET DEFAULT nextval('core_assignment_admins_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup ALTER COLUMN id SET DEFAULT nextval('core_assignmentgroup_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners ALTER COLUMN id SET DEFAULT nextval('core_assignmentgroup_examiners_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouptag ALTER COLUMN id SET DEFAULT nextval('core_assignmentgrouptag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate ALTER COLUMN id SET DEFAULT nextval('core_candidate_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_deadline ALTER COLUMN id SET DEFAULT nextval('core_deadline_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery ALTER COLUMN id SET DEFAULT nextval('core_delivery_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_devilryuserprofile ALTER COLUMN id SET DEFAULT nextval('core_devilryuserprofile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_filemeta ALTER COLUMN id SET DEFAULT nextval('core_filemeta_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite ALTER COLUMN id SET DEFAULT nextval('core_groupinvite_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_node ALTER COLUMN id SET DEFAULT nextval('core_node_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_node_admins ALTER COLUMN id SET DEFAULT nextval('core_node_admins_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period ALTER COLUMN id SET DEFAULT nextval('core_period_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period_admins ALTER COLUMN id SET DEFAULT nextval('core_period_admins_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodapplicationkeyvalue ALTER COLUMN id SET DEFAULT nextval('core_periodapplicationkeyvalue_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointrangetograde ALTER COLUMN id SET DEFAULT nextval('core_pointrangetograde_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointtogrademap ALTER COLUMN id SET DEFAULT nextval('core_pointtogrademap_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminer ALTER COLUMN id SET DEFAULT nextval('core_relatedexaminer_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminersyncsystemtag ALTER COLUMN id SET DEFAULT nextval('core_relatedexaminersyncsystemtag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudent ALTER COLUMN id SET DEFAULT nextval('core_relatedstudent_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudentkeyvalue ALTER COLUMN id SET DEFAULT nextval('core_relatedstudentkeyvalue_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudentsyncsystemtag ALTER COLUMN id SET DEFAULT nextval('core_relatedstudentsyncsystemtag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedback ALTER COLUMN id SET DEFAULT nextval('core_staticfeedback_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedbackfileattachment ALTER COLUMN id SET DEFAULT nextval('core_staticfeedbackfileattachment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject ALTER COLUMN id SET DEFAULT nextval('core_subject_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject_admins ALTER COLUMN id SET DEFAULT nextval('core_subject_admins_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_generic_token_with_metadata_generictokenwithmetadata ALTER COLUMN id SET DEFAULT nextval('cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfile ALTER COLUMN id SET DEFAULT nextval('cradmin_temporaryfileuploadstore_temporaryfile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfilecollection ALTER COLUMN id SET DEFAULT nextval('cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup ALTER COLUMN id SET DEFAULT nextval('devilry_account_periodpermissiongroup_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroup ALTER COLUMN id SET DEFAULT nextval('devilry_account_permissiongroup_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroupuser ALTER COLUMN id SET DEFAULT nextval('devilry_account_permissiongroupuser_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup ALTER COLUMN id SET DEFAULT nextval('devilry_account_subjectpermissiongroup_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_user ALTER COLUMN id SET DEFAULT nextval('devilry_account_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_useremail ALTER COLUMN id SET DEFAULT nextval('devilry_account_useremail_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_username ALTER COLUMN id SET DEFAULT nextval('devilry_account_username_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_comment ALTER COLUMN id SET DEFAULT nextval('devilry_comment_comment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfile ALTER COLUMN id SET DEFAULT nextval('devilry_comment_commentfile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfileimage ALTER COLUMN id SET DEFAULT nextval('devilry_comment_commentfileimage_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_comparetwocacheitem ALTER COLUMN id SET DEFAULT nextval('devilry_detektor_comparetwocacheitem_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_detektorassignment ALTER COLUMN id SET DEFAULT nextval('devilry_detektor_detektorassignment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_detektorassignmentcachelanguage ALTER COLUMN id SET DEFAULT nextval('devilry_detektor_detektorassignmentcachelanguage_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_detektordeliveryparseresult ALTER COLUMN id SET DEFAULT nextval('devilry_detektor_detektordeliveryparseresult_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft ALTER COLUMN id SET DEFAULT nextval('devilry_gradingsystem_feedbackdraft_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraftfile ALTER COLUMN id SET DEFAULT nextval('devilry_gradingsystem_feedbackdraftfile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset ALTER COLUMN id SET DEFAULT nextval('devilry_group_feedbackset_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_deadlinetag ALTER COLUMN id SET DEFAULT nextval('devilry_qualifiesforexam_deadlinetag_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam ALTER COLUMN id SET DEFAULT nextval('devilry_qualifiesforexam_qualifiesforfinalexam_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_status ALTER COLUMN id SET DEFAULT nextval('devilry_qualifiesforexam_status_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile ALTER COLUMN id SET DEFAULT nextval('devilry_student_uploadeddeliveryfile_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add session	1	add_session
2	Can change session	1	change_session
3	Can delete session	1	delete_session
4	Can add permission	2	add_permission
5	Can change permission	2	change_permission
6	Can delete permission	2	delete_permission
7	Can add group	3	add_group
8	Can change group	3	change_group
9	Can delete group	3	delete_group
10	Can add content type	4	add_contenttype
11	Can change content type	4	change_contenttype
12	Can delete content type	4	delete_contenttype
13	Can add log entry	5	add_logentry
14	Can change log entry	5	change_logentry
15	Can delete log entry	5	delete_logentry
16	Can add temporary file collection	6	add_temporaryfilecollection
17	Can change temporary file collection	6	change_temporaryfilecollection
18	Can delete temporary file collection	6	delete_temporaryfilecollection
19	Can add temporary file	7	add_temporaryfile
20	Can change temporary file	7	change_temporaryfile
21	Can delete temporary file	7	delete_temporaryfile
22	Can add generic token with metadata	8	add_generictokenwithmetadata
23	Can change generic token with metadata	8	change_generictokenwithmetadata
24	Can delete generic token with metadata	8	delete_generictokenwithmetadata
25	Can add node	9	add_node
26	Can change node	9	change_node
27	Can delete node	9	delete_node
28	Can add course	10	add_subject
29	Can change course	10	change_subject
30	Can delete course	10	delete_subject
31	Can add semester	11	add_period
32	Can change semester	11	change_period
33	Can delete semester	11	delete_period
34	Can add period application key value	12	add_periodapplicationkeyvalue
35	Can change period application key value	12	change_periodapplicationkeyvalue
36	Can delete period application key value	12	delete_periodapplicationkeyvalue
37	Can add related examiner	13	add_relatedexaminer
38	Can change related examiner	13	change_relatedexaminer
39	Can delete related examiner	13	delete_relatedexaminer
40	Can add related student	14	add_relatedstudent
41	Can change related student	14	change_relatedstudent
42	Can delete related student	14	delete_relatedstudent
43	Can add related examiner sync system tag	15	add_relatedexaminersyncsystemtag
44	Can change related examiner sync system tag	15	change_relatedexaminersyncsystemtag
45	Can delete related examiner sync system tag	15	delete_relatedexaminersyncsystemtag
46	Can add related student sync system tag	16	add_relatedstudentsyncsystemtag
47	Can change related student sync system tag	16	change_relatedstudentsyncsystemtag
48	Can delete related student sync system tag	16	delete_relatedstudentsyncsystemtag
49	Can add related student key value	17	add_relatedstudentkeyvalue
50	Can change related student key value	17	change_relatedstudentkeyvalue
51	Can delete related student key value	17	delete_relatedstudentkeyvalue
52	Can add assignment	18	add_assignment
53	Can change assignment	18	change_assignment
54	Can delete assignment	18	delete_assignment
55	Can add point to grade map	19	add_pointtogrademap
56	Can change point to grade map	19	change_pointtogrademap
57	Can delete point to grade map	19	delete_pointtogrademap
58	Can add point range to grade	20	add_pointrangetograde
59	Can change point range to grade	20	change_pointrangetograde
60	Can delete point range to grade	20	delete_pointrangetograde
61	Can add assignment group	21	add_assignmentgroup
62	Can change assignment group	21	change_assignmentgroup
63	Can delete assignment group	21	delete_assignmentgroup
64	Can add assignment group tag	22	add_assignmentgrouptag
65	Can change assignment group tag	22	change_assignmentgrouptag
66	Can delete assignment group tag	22	delete_assignmentgrouptag
67	Can add Deadline	23	add_deadline
68	Can change Deadline	23	change_deadline
69	Can delete Deadline	23	delete_deadline
70	Can add FileMeta	24	add_filemeta
71	Can change FileMeta	24	change_filemeta
72	Can delete FileMeta	24	delete_filemeta
73	Can add Delivery	25	add_delivery
74	Can change Delivery	25	change_delivery
75	Can delete Delivery	25	delete_delivery
76	Can add candidate	26	add_candidate
77	Can change candidate	26	change_candidate
78	Can delete candidate	26	delete_candidate
79	Can add Static feedback	27	add_staticfeedback
80	Can change Static feedback	27	change_staticfeedback
81	Can delete Static feedback	27	delete_staticfeedback
82	Can add Static feedback file attachment	28	add_staticfeedbackfileattachment
83	Can change Static feedback file attachment	28	change_staticfeedbackfileattachment
84	Can delete Static feedback file attachment	28	delete_staticfeedbackfileattachment
85	Can add devilry user profile	29	add_devilryuserprofile
86	Can change devilry user profile	29	change_devilryuserprofile
87	Can delete devilry user profile	29	delete_devilryuserprofile
88	Can add examiner	30	add_examiner
89	Can change examiner	30	change_examiner
90	Can delete examiner	30	delete_examiner
91	Can add group invite	31	add_groupinvite
92	Can change group invite	31	change_groupinvite
93	Can delete group invite	31	delete_groupinvite
94	Can add User	32	add_user
95	Can change User	32	change_user
96	Can delete User	32	delete_user
97	Can add Email address	33	add_useremail
98	Can change Email address	33	change_useremail
99	Can delete Email address	33	delete_useremail
100	Can add Username	34	add_username
101	Can change Username	34	change_username
102	Can delete Username	34	delete_username
103	Can add Permission group user	35	add_permissiongroupuser
104	Can change Permission group user	35	change_permissiongroupuser
105	Can delete Permission group user	35	delete_permissiongroupuser
106	Can add Permission group	36	add_permissiongroup
107	Can change Permission group	36	change_permissiongroup
108	Can delete Permission group	36	delete_permissiongroup
109	Can add Period permission group	37	add_periodpermissiongroup
110	Can change Period permission group	37	change_periodpermissiongroup
111	Can delete Period permission group	37	delete_periodpermissiongroup
112	Can add Subject permission group	38	add_subjectpermissiongroup
113	Can change Subject permission group	38	change_subjectpermissiongroup
114	Can delete Subject permission group	38	delete_subjectpermissiongroup
115	Can add uploaded delivery file	39	add_uploadeddeliveryfile
116	Can change uploaded delivery file	39	change_uploadeddeliveryfile
117	Can delete uploaded delivery file	39	delete_uploadeddeliveryfile
118	Can add feedback set	40	add_feedbackset
119	Can change feedback set	40	change_feedbackset
120	Can delete feedback set	40	delete_feedbackset
121	Can add group comment	41	add_groupcomment
122	Can change group comment	41	change_groupcomment
123	Can delete group comment	41	delete_groupcomment
124	Can add image annotation comment	42	add_imageannotationcomment
125	Can change image annotation comment	42	change_imageannotationcomment
126	Can delete image annotation comment	42	delete_imageannotationcomment
127	Can add comment	43	add_comment
128	Can change comment	43	change_comment
129	Can delete comment	43	delete_comment
130	Can add comment file	44	add_commentfile
131	Can change comment file	44	change_commentfile
132	Can delete comment file	44	delete_commentfile
133	Can add comment file image	45	add_commentfileimage
134	Can change comment file image	45	change_commentfileimage
135	Can delete comment file image	45	delete_commentfileimage
136	Can add deadline tag	46	add_deadlinetag
137	Can change deadline tag	46	change_deadlinetag
138	Can delete deadline tag	46	delete_deadlinetag
139	Can add period tag	47	add_periodtag
140	Can change period tag	47	change_periodtag
141	Can delete period tag	47	delete_periodtag
142	Can add Qualified for final exam status	48	add_status
143	Can change Qualified for final exam status	48	change_status
144	Can delete Qualified for final exam status	48	delete_status
145	Can add qualifies for final exam	49	add_qualifiesforfinalexam
146	Can change qualifies for final exam	49	change_qualifiesforfinalexam
147	Can delete qualifies for final exam	49	delete_qualifiesforfinalexam
148	Can add feedback draft	50	add_feedbackdraft
149	Can change feedback draft	50	change_feedbackdraft
150	Can delete feedback draft	50	delete_feedbackdraft
151	Can add feedback draft file	51	add_feedbackdraftfile
152	Can change feedback draft file	51	change_feedbackdraftfile
153	Can delete feedback draft file	51	delete_feedbackdraftfile
154	Can add detektor assignment	52	add_detektorassignment
155	Can change detektor assignment	52	change_detektorassignment
156	Can delete detektor assignment	52	delete_detektorassignment
157	Can add detektor delivery parse result	53	add_detektordeliveryparseresult
158	Can change detektor delivery parse result	53	change_detektordeliveryparseresult
159	Can delete detektor delivery parse result	53	delete_detektordeliveryparseresult
160	Can add detektor assignment cache language	54	add_detektorassignmentcachelanguage
161	Can change detektor assignment cache language	54	change_detektorassignmentcachelanguage
162	Can delete detektor assignment cache language	54	delete_detektorassignmentcachelanguage
163	Can add compare two cache item	55	add_comparetwocacheitem
164	Can change compare two cache item	55	change_comparetwocacheitem
165	Can delete compare two cache item	55	delete_comparetwocacheitem
\.


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('auth_permission_id_seq', 165, true);


--
-- Data for Name: core_assignment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignment (id, short_name, long_name, publishing_time, anonymous, students_can_see_points, delivery_types, deadline_handling, scale_points_percent, first_deadline, max_points, passing_grade_min_points, points_to_grade_mapper, grading_system_plugin_id, students_can_create_groups, students_can_not_create_groups_after, feedback_workflow, parentnode_id) FROM stdin;
1	week1	Week 1	2014-11-04 14:15:16.095509+01	f	t	0	0	100	2014-11-11 14:15:16.095492+01	4	1	raw-points	devilry_gradingsystemplugin_points	f	\N		2
2	week2	Week 2	2014-11-11 14:15:19.922296+01	f	t	0	0	100	2014-11-18 14:15:19.922277+01	2	1	raw-points	devilry_gradingsystemplugin_points	f	\N		2
3	week3	Week 3	2014-11-18 14:15:23.286803+01	f	t	0	0	100	2014-11-25 14:15:23.286784+01	4	1	raw-points	devilry_gradingsystemplugin_points	f	\N		2
4	week4	Week 4	2014-11-25 14:15:26.678333+01	f	t	0	0	100	2014-12-02 14:15:26.678316+01	8	1	raw-points	devilry_gradingsystemplugin_points	f	\N		2
5	week5	Week 5	2014-12-09 14:15:30.132135+01	f	t	0	0	100	2014-12-16 14:15:30.132099+01	1	1	raw-points	devilry_gradingsystemplugin_points	f	\N		2
6	week6	Week 6	2014-12-16 14:15:33.410759+01	f	t	0	0	100	2014-12-23 14:15:33.410739+01	2	1	raw-points	devilry_gradingsystemplugin_points	f	\N		2
7	week1	Week 1	2015-11-03 14:15:34.693584+01	f	t	0	0	100	2015-11-10 14:15:34.69357+01	4	1	raw-points	devilry_gradingsystemplugin_points	f	\N		1
8	week2	Week 2	2015-11-10 14:15:36.013812+01	f	t	0	0	100	2015-11-17 14:15:36.013798+01	2	1	raw-points	devilry_gradingsystemplugin_points	f	\N		1
9	week3	Week 3	2015-11-17 14:15:37.307293+01	f	t	0	0	100	2015-11-24 14:15:37.307279+01	4	1	raw-points	devilry_gradingsystemplugin_points	f	\N		1
10	week4	Week 4	2015-11-24 14:15:38.795149+01	f	t	0	0	100	2015-12-01 14:15:38.795136+01	8	1	raw-points	devilry_gradingsystemplugin_points	f	\N		1
11	week5	Week 5	2015-12-08 14:15:40.021567+01	f	t	0	0	100	2015-12-15 14:15:40.021552+01	6	1	raw-points	devilry_gradingsystemplugin_points	f	\N		1
12	week6	Week 6	2015-12-15 14:15:41.295269+01	f	t	0	0	100	\N	6	1	raw-points	devilry_gradingsystemplugin_points	f	\N		1
13	Oblig 1 - Domination	Oblig 1 - Domination	2015-12-15 14:15:43.849718+01	f	t	0	0	100	2015-11-30 14:15:43.732615+01	10	3	passed-failed	devilry_gradingsystemplugin_approved	f	\N		3
\.


--
-- Data for Name: core_assignment_admins; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignment_admins (id, assignment_id, user_id) FROM stdin;
\.


--
-- Name: core_assignment_admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignment_admins_id_seq', 1, false);


--
-- Name: core_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignment_id_seq', 13, true);


--
-- Data for Name: core_assignmentgroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgroup (id, name, is_open, etag, delivery_status, created_datetime, copied_from_id, feedback_id, last_deadline_id, parentnode_id) FROM stdin;
1		f	2015-12-15 14:15:16.151727+01	corrected	2015-12-15 14:15:16.150775+01	\N	1	1	1
2		f	2015-12-15 14:15:16.715806+01	corrected	2015-12-15 14:15:16.71496+01	\N	2	2	1
3		f	2015-12-15 14:15:17.021533+01	corrected	2015-12-15 14:15:17.020872+01	\N	3	3	1
4		f	2015-12-15 14:15:17.310056+01	corrected	2015-12-15 14:15:17.309298+01	\N	4	4	1
5		f	2015-12-15 14:15:17.595894+01	corrected	2015-12-15 14:15:17.595114+01	\N	5	5	1
6		f	2015-12-15 14:15:17.856567+01	corrected	2015-12-15 14:15:17.855863+01	\N	6	6	1
7		f	2015-12-15 14:15:18.147867+01	corrected	2015-12-15 14:15:18.1472+01	\N	7	7	1
8		f	2015-12-15 14:15:18.406869+01	corrected	2015-12-15 14:15:18.406191+01	\N	8	8	1
9		f	2015-12-15 14:15:18.667875+01	corrected	2015-12-15 14:15:18.667168+01	\N	9	9	1
10		f	2015-12-15 14:15:18.911849+01	corrected	2015-12-15 14:15:18.91105+01	\N	10	10	1
11		f	2015-12-15 14:15:19.148595+01	corrected	2015-12-15 14:15:19.14789+01	\N	11	11	1
12		f	2015-12-15 14:15:19.424668+01	corrected	2015-12-15 14:15:19.423942+01	\N	12	12	1
13		f	2015-12-15 14:15:19.676541+01	corrected	2015-12-15 14:15:19.675699+01	\N	13	13	1
14		f	2015-12-15 14:15:19.986392+01	corrected	2015-12-15 14:15:19.985674+01	\N	14	14	2
15		f	2015-12-15 14:15:20.279688+01	corrected	2015-12-15 14:15:20.278983+01	\N	15	15	2
16		f	2015-12-15 14:15:20.486111+01	corrected	2015-12-15 14:15:20.48544+01	\N	16	16	2
17		f	2015-12-15 14:15:20.714099+01	corrected	2015-12-15 14:15:20.713442+01	\N	17	17	2
18		f	2015-12-15 14:15:20.949222+01	corrected	2015-12-15 14:15:20.948402+01	\N	18	18	2
19		f	2015-12-15 14:15:21.21147+01	corrected	2015-12-15 14:15:21.2105+01	\N	19	19	2
20		f	2015-12-15 14:15:21.491885+01	corrected	2015-12-15 14:15:21.490927+01	\N	20	20	2
21		f	2015-12-15 14:15:21.745118+01	corrected	2015-12-15 14:15:21.74428+01	\N	21	21	2
22		f	2015-12-15 14:15:22.030167+01	corrected	2015-12-15 14:15:22.029257+01	\N	22	22	2
23		f	2015-12-15 14:15:22.286711+01	corrected	2015-12-15 14:15:22.285841+01	\N	23	23	2
24		f	2015-12-15 14:15:22.508564+01	corrected	2015-12-15 14:15:22.507857+01	\N	24	24	2
25		f	2015-12-15 14:15:22.767001+01	corrected	2015-12-15 14:15:22.766236+01	\N	25	25	2
26		f	2015-12-15 14:15:23.020597+01	corrected	2015-12-15 14:15:23.019943+01	\N	26	26	2
27		f	2015-12-15 14:15:23.339136+01	corrected	2015-12-15 14:15:23.338415+01	\N	27	27	3
28		f	2015-12-15 14:15:23.581278+01	corrected	2015-12-15 14:15:23.580577+01	\N	28	28	3
29		f	2015-12-15 14:15:23.820944+01	corrected	2015-12-15 14:15:23.820234+01	\N	29	29	3
30		f	2015-12-15 14:15:24.114173+01	corrected	2015-12-15 14:15:24.113102+01	\N	30	30	3
31		f	2015-12-15 14:15:24.410338+01	corrected	2015-12-15 14:15:24.409573+01	\N	31	31	3
32		f	2015-12-15 14:15:24.675366+01	corrected	2015-12-15 14:15:24.674711+01	\N	32	32	3
33		f	2015-12-15 14:15:24.997578+01	corrected	2015-12-15 14:15:24.996872+01	\N	33	33	3
34		f	2015-12-15 14:15:25.216326+01	corrected	2015-12-15 14:15:25.21545+01	\N	34	34	3
35		f	2015-12-15 14:15:25.440781+01	corrected	2015-12-15 14:15:25.440089+01	\N	35	35	3
36		f	2015-12-15 14:15:25.677755+01	corrected	2015-12-15 14:15:25.677094+01	\N	36	36	3
37		f	2015-12-15 14:15:25.918284+01	corrected	2015-12-15 14:15:25.917618+01	\N	37	37	3
38		f	2015-12-15 14:15:26.161081+01	corrected	2015-12-15 14:15:26.160295+01	\N	38	38	3
39		f	2015-12-15 14:15:26.416565+01	corrected	2015-12-15 14:15:26.415909+01	\N	39	39	3
40		f	2015-12-15 14:15:26.739406+01	corrected	2015-12-15 14:15:26.738742+01	\N	40	40	4
41		f	2015-12-15 14:15:26.986877+01	corrected	2015-12-15 14:15:26.986201+01	\N	41	41	4
42		f	2015-12-15 14:15:27.263227+01	corrected	2015-12-15 14:15:27.26254+01	\N	42	42	4
43		f	2015-12-15 14:15:27.505694+01	corrected	2015-12-15 14:15:27.504919+01	\N	43	43	4
44		f	2015-12-15 14:15:27.767933+01	corrected	2015-12-15 14:15:27.767236+01	\N	44	44	4
45		f	2015-12-15 14:15:28.007491+01	corrected	2015-12-15 14:15:28.006821+01	\N	45	45	4
46		f	2015-12-15 14:15:28.258329+01	corrected	2015-12-15 14:15:28.25764+01	\N	46	46	4
47		f	2015-12-15 14:15:28.505515+01	corrected	2015-12-15 14:15:28.504847+01	\N	47	47	4
48		f	2015-12-15 14:15:28.762225+01	corrected	2015-12-15 14:15:28.761428+01	\N	48	48	4
49		f	2015-12-15 14:15:29.029271+01	corrected	2015-12-15 14:15:29.028553+01	\N	49	49	4
50		f	2015-12-15 14:15:29.304216+01	corrected	2015-12-15 14:15:29.303566+01	\N	50	50	4
51		f	2015-12-15 14:15:29.588833+01	corrected	2015-12-15 14:15:29.588176+01	\N	51	51	4
52		f	2015-12-15 14:15:29.845196+01	corrected	2015-12-15 14:15:29.844296+01	\N	52	52	4
53		f	2015-12-15 14:15:30.19584+01	corrected	2015-12-15 14:15:30.194183+01	\N	53	53	5
54		f	2015-12-15 14:15:30.443924+01	corrected	2015-12-15 14:15:30.443265+01	\N	54	54	5
55		f	2015-12-15 14:15:30.709574+01	corrected	2015-12-15 14:15:30.708753+01	\N	55	55	5
56		f	2015-12-15 14:15:30.976946+01	corrected	2015-12-15 14:15:30.976296+01	\N	56	56	5
57		f	2015-12-15 14:15:31.245046+01	corrected	2015-12-15 14:15:31.244326+01	\N	57	57	5
58		f	2015-12-15 14:15:31.50293+01	corrected	2015-12-15 14:15:31.502259+01	\N	58	58	5
59		f	2015-12-15 14:15:31.735474+01	corrected	2015-12-15 14:15:31.73477+01	\N	59	59	5
60		f	2015-12-15 14:15:31.997848+01	corrected	2015-12-15 14:15:31.997122+01	\N	60	60	5
61		f	2015-12-15 14:15:32.238466+01	corrected	2015-12-15 14:15:32.23762+01	\N	61	61	5
62		f	2015-12-15 14:15:32.481305+01	corrected	2015-12-15 14:15:32.480652+01	\N	62	62	5
63		f	2015-12-15 14:15:32.707463+01	corrected	2015-12-15 14:15:32.706796+01	\N	63	63	5
64		f	2015-12-15 14:15:32.933867+01	corrected	2015-12-15 14:15:32.932953+01	\N	64	64	5
65		f	2015-12-15 14:15:33.169527+01	corrected	2015-12-15 14:15:33.168632+01	\N	65	65	5
66		t	2015-12-15 14:15:33.470551+01	no-deadlines	2015-12-15 14:15:33.46988+01	\N	\N	\N	6
67		t	2015-12-15 14:15:33.570177+01	no-deadlines	2015-12-15 14:15:33.569548+01	\N	\N	\N	6
68		t	2015-12-15 14:15:33.6743+01	no-deadlines	2015-12-15 14:15:33.673652+01	\N	\N	\N	6
69		t	2015-12-15 14:15:33.736613+01	no-deadlines	2015-12-15 14:15:33.735967+01	\N	\N	\N	6
70		t	2015-12-15 14:15:33.897205+01	no-deadlines	2015-12-15 14:15:33.896585+01	\N	\N	\N	6
71		t	2015-12-15 14:15:33.992235+01	no-deadlines	2015-12-15 14:15:33.991579+01	\N	\N	\N	6
72		t	2015-12-15 14:15:34.089152+01	no-deadlines	2015-12-15 14:15:34.088535+01	\N	\N	\N	6
73		t	2015-12-15 14:15:34.188341+01	no-deadlines	2015-12-15 14:15:34.187712+01	\N	\N	\N	6
74		t	2015-12-15 14:15:34.26241+01	no-deadlines	2015-12-15 14:15:34.261776+01	\N	\N	\N	6
75		t	2015-12-15 14:15:34.345762+01	no-deadlines	2015-12-15 14:15:34.345122+01	\N	\N	\N	6
76		t	2015-12-15 14:15:34.446409+01	no-deadlines	2015-12-15 14:15:34.445773+01	\N	\N	\N	6
77		t	2015-12-15 14:15:34.544472+01	no-deadlines	2015-12-15 14:15:34.543823+01	\N	\N	\N	6
78		t	2015-12-15 14:15:34.625332+01	no-deadlines	2015-12-15 14:15:34.624703+01	\N	\N	\N	6
79		t	2015-12-15 14:15:34.757227+01	no-deadlines	2015-12-15 14:15:34.756558+01	\N	\N	\N	7
80		t	2015-12-15 14:15:34.844586+01	no-deadlines	2015-12-15 14:15:34.843937+01	\N	\N	\N	7
81		t	2015-12-15 14:15:34.954845+01	no-deadlines	2015-12-15 14:15:34.954217+01	\N	\N	\N	7
82		t	2015-12-15 14:15:35.034431+01	no-deadlines	2015-12-15 14:15:35.033822+01	\N	\N	\N	7
83		t	2015-12-15 14:15:35.129281+01	no-deadlines	2015-12-15 14:15:35.128636+01	\N	\N	\N	7
84		t	2015-12-15 14:15:35.212091+01	no-deadlines	2015-12-15 14:15:35.211447+01	\N	\N	\N	7
85		t	2015-12-15 14:15:35.291327+01	no-deadlines	2015-12-15 14:15:35.2907+01	\N	\N	\N	7
86		t	2015-12-15 14:15:35.39333+01	no-deadlines	2015-12-15 14:15:35.392708+01	\N	\N	\N	7
87		t	2015-12-15 14:15:35.490624+01	no-deadlines	2015-12-15 14:15:35.489984+01	\N	\N	\N	7
88		t	2015-12-15 14:15:35.580023+01	no-deadlines	2015-12-15 14:15:35.579403+01	\N	\N	\N	7
89		t	2015-12-15 14:15:35.684712+01	no-deadlines	2015-12-15 14:15:35.684084+01	\N	\N	\N	7
90		t	2015-12-15 14:15:35.807261+01	no-deadlines	2015-12-15 14:15:35.80663+01	\N	\N	\N	7
91		t	2015-12-15 14:15:35.939526+01	no-deadlines	2015-12-15 14:15:35.938899+01	\N	\N	\N	7
92		t	2015-12-15 14:15:36.060709+01	no-deadlines	2015-12-15 14:15:36.06006+01	\N	\N	\N	8
93		t	2015-12-15 14:15:36.149931+01	no-deadlines	2015-12-15 14:15:36.149305+01	\N	\N	\N	8
94		t	2015-12-15 14:15:36.291318+01	no-deadlines	2015-12-15 14:15:36.290662+01	\N	\N	\N	8
95		t	2015-12-15 14:15:36.401473+01	no-deadlines	2015-12-15 14:15:36.400827+01	\N	\N	\N	8
96		t	2015-12-15 14:15:36.485491+01	no-deadlines	2015-12-15 14:15:36.484801+01	\N	\N	\N	8
97		t	2015-12-15 14:15:36.587692+01	no-deadlines	2015-12-15 14:15:36.587047+01	\N	\N	\N	8
98		t	2015-12-15 14:15:36.690644+01	no-deadlines	2015-12-15 14:15:36.689975+01	\N	\N	\N	8
99		t	2015-12-15 14:15:36.773064+01	no-deadlines	2015-12-15 14:15:36.772388+01	\N	\N	\N	8
100		t	2015-12-15 14:15:36.890674+01	no-deadlines	2015-12-15 14:15:36.890026+01	\N	\N	\N	8
101		t	2015-12-15 14:15:36.976213+01	no-deadlines	2015-12-15 14:15:36.975587+01	\N	\N	\N	8
102		t	2015-12-15 14:15:37.080075+01	no-deadlines	2015-12-15 14:15:37.079449+01	\N	\N	\N	8
103		t	2015-12-15 14:15:37.160053+01	no-deadlines	2015-12-15 14:15:37.159408+01	\N	\N	\N	8
104		t	2015-12-15 14:15:37.233513+01	no-deadlines	2015-12-15 14:15:37.232895+01	\N	\N	\N	8
105		t	2015-12-15 14:15:37.365755+01	no-deadlines	2015-12-15 14:15:37.36492+01	\N	\N	\N	9
106		t	2015-12-15 14:15:37.446502+01	no-deadlines	2015-12-15 14:15:37.445861+01	\N	\N	\N	9
107		t	2015-12-15 14:15:37.539741+01	no-deadlines	2015-12-15 14:15:37.5391+01	\N	\N	\N	9
108		t	2015-12-15 14:15:37.628823+01	no-deadlines	2015-12-15 14:15:37.628197+01	\N	\N	\N	9
109		t	2015-12-15 14:15:37.730142+01	no-deadlines	2015-12-15 14:15:37.729509+01	\N	\N	\N	9
110		t	2015-12-15 14:15:37.814753+01	no-deadlines	2015-12-15 14:15:37.814125+01	\N	\N	\N	9
111		t	2015-12-15 14:15:38.185697+01	no-deadlines	2015-12-15 14:15:38.185047+01	\N	\N	\N	9
112		t	2015-12-15 14:15:38.265203+01	no-deadlines	2015-12-15 14:15:38.264575+01	\N	\N	\N	9
113		t	2015-12-15 14:15:38.366872+01	no-deadlines	2015-12-15 14:15:38.366242+01	\N	\N	\N	9
114		t	2015-12-15 14:15:38.439878+01	no-deadlines	2015-12-15 14:15:38.439249+01	\N	\N	\N	9
115		t	2015-12-15 14:15:38.51406+01	no-deadlines	2015-12-15 14:15:38.513435+01	\N	\N	\N	9
116		t	2015-12-15 14:15:38.602691+01	no-deadlines	2015-12-15 14:15:38.602067+01	\N	\N	\N	9
117		t	2015-12-15 14:15:38.703798+01	no-deadlines	2015-12-15 14:15:38.703176+01	\N	\N	\N	9
118		t	2015-12-15 14:15:38.856591+01	no-deadlines	2015-12-15 14:15:38.855917+01	\N	\N	\N	10
119		t	2015-12-15 14:15:38.925877+01	no-deadlines	2015-12-15 14:15:38.925223+01	\N	\N	\N	10
120		t	2015-12-15 14:15:39.034627+01	no-deadlines	2015-12-15 14:15:39.033508+01	\N	\N	\N	10
121		t	2015-12-15 14:15:39.10383+01	no-deadlines	2015-12-15 14:15:39.103215+01	\N	\N	\N	10
122		t	2015-12-15 14:15:39.213001+01	no-deadlines	2015-12-15 14:15:39.212366+01	\N	\N	\N	10
123		t	2015-12-15 14:15:39.292041+01	no-deadlines	2015-12-15 14:15:39.291407+01	\N	\N	\N	10
124		t	2015-12-15 14:15:39.374119+01	no-deadlines	2015-12-15 14:15:39.373378+01	\N	\N	\N	10
125		t	2015-12-15 14:15:39.455267+01	no-deadlines	2015-12-15 14:15:39.454521+01	\N	\N	\N	10
126		t	2015-12-15 14:15:39.541614+01	no-deadlines	2015-12-15 14:15:39.540926+01	\N	\N	\N	10
127		t	2015-12-15 14:15:39.645613+01	no-deadlines	2015-12-15 14:15:39.644987+01	\N	\N	\N	10
128		t	2015-12-15 14:15:39.730183+01	no-deadlines	2015-12-15 14:15:39.72954+01	\N	\N	\N	10
129		t	2015-12-15 14:15:39.838418+01	no-deadlines	2015-12-15 14:15:39.837766+01	\N	\N	\N	10
130		t	2015-12-15 14:15:39.949597+01	no-deadlines	2015-12-15 14:15:39.94898+01	\N	\N	\N	10
131		t	2015-12-15 14:15:40.11748+01	no-deadlines	2015-12-15 14:15:40.116803+01	\N	\N	\N	11
132		t	2015-12-15 14:15:40.194555+01	no-deadlines	2015-12-15 14:15:40.193909+01	\N	\N	\N	11
133		t	2015-12-15 14:15:40.289442+01	no-deadlines	2015-12-15 14:15:40.288826+01	\N	\N	\N	11
134		t	2015-12-15 14:15:40.395696+01	no-deadlines	2015-12-15 14:15:40.395049+01	\N	\N	\N	11
135		t	2015-12-15 14:15:40.486134+01	no-deadlines	2015-12-15 14:15:40.485483+01	\N	\N	\N	11
136		t	2015-12-15 14:15:40.573296+01	no-deadlines	2015-12-15 14:15:40.572651+01	\N	\N	\N	11
137		t	2015-12-15 14:15:40.678014+01	no-deadlines	2015-12-15 14:15:40.677379+01	\N	\N	\N	11
138		t	2015-12-15 14:15:40.769565+01	no-deadlines	2015-12-15 14:15:40.768931+01	\N	\N	\N	11
139		t	2015-12-15 14:15:40.87006+01	no-deadlines	2015-12-15 14:15:40.869422+01	\N	\N	\N	11
140		t	2015-12-15 14:15:40.948201+01	no-deadlines	2015-12-15 14:15:40.947569+01	\N	\N	\N	11
141		t	2015-12-15 14:15:41.051027+01	no-deadlines	2015-12-15 14:15:41.050394+01	\N	\N	\N	11
142		t	2015-12-15 14:15:41.120324+01	no-deadlines	2015-12-15 14:15:41.119665+01	\N	\N	\N	11
143		t	2015-12-15 14:15:41.212702+01	no-deadlines	2015-12-15 14:15:41.212041+01	\N	\N	\N	11
144		t	2015-12-15 14:15:41.343799+01	waiting-for-something	2015-12-15 14:15:41.343048+01	\N	\N	66	12
145		t	2015-12-15 14:15:41.483517+01	waiting-for-something	2015-12-15 14:15:41.482744+01	\N	\N	67	12
146		t	2015-12-15 14:15:41.63552+01	waiting-for-something	2015-12-15 14:15:41.634734+01	\N	\N	68	12
147		t	2015-12-15 14:15:41.797457+01	waiting-for-something	2015-12-15 14:15:41.796696+01	\N	\N	69	12
148		t	2015-12-15 14:15:41.963746+01	waiting-for-something	2015-12-15 14:15:41.962978+01	\N	\N	70	12
149		t	2015-12-15 14:15:42.125723+01	waiting-for-something	2015-12-15 14:15:42.124882+01	\N	\N	71	12
150		t	2015-12-15 14:15:42.287275+01	waiting-for-something	2015-12-15 14:15:42.286415+01	\N	\N	72	12
151		t	2015-12-15 14:15:42.78433+01	waiting-for-something	2015-12-15 14:15:42.783479+01	\N	\N	73	12
152		t	2015-12-15 14:15:42.920914+01	waiting-for-something	2015-12-15 14:15:42.920037+01	\N	\N	74	12
153		t	2015-12-15 14:15:43.063179+01	waiting-for-something	2015-12-15 14:15:43.062437+01	\N	\N	75	12
154		t	2015-12-15 14:15:43.210952+01	waiting-for-something	2015-12-15 14:15:43.21014+01	\N	\N	76	12
155		t	2015-12-15 14:15:43.375113+01	waiting-for-something	2015-12-15 14:15:43.374271+01	\N	\N	77	12
156		t	2015-12-15 14:15:43.540785+01	waiting-for-something	2015-12-15 14:15:43.540083+01	\N	\N	78	12
157		t	2015-12-15 14:15:43.933375+01	no-deadlines	2015-12-15 14:15:43.93257+01	\N	\N	\N	13
\.


--
-- Data for Name: core_assignmentgroup_examiners; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgroup_examiners (id, automatic_anonymous_id, assignmentgroup_id, user_id, relatedexaminer_id) FROM stdin;
1		1	2	\N
2		2	4	\N
3		3	4	\N
4		4	2	\N
5		5	4	\N
6		6	3	\N
7		7	2	\N
8		8	3	\N
9		9	4	\N
10		10	4	\N
11		11	4	\N
12		12	3	\N
13		13	3	\N
14		14	3	\N
15		15	4	\N
16		16	4	\N
17		17	2	\N
18		18	4	\N
19		19	3	\N
20		20	2	\N
21		21	2	\N
22		22	3	\N
23		23	4	\N
24		24	2	\N
25		25	4	\N
26		26	3	\N
27		27	3	\N
28		28	4	\N
29		29	2	\N
30		30	4	\N
31		31	3	\N
32		32	4	\N
33		33	4	\N
34		34	3	\N
35		35	4	\N
36		36	3	\N
37		37	2	\N
38		38	4	\N
39		39	3	\N
40		40	3	\N
41		41	2	\N
42		42	3	\N
43		43	4	\N
44		44	2	\N
45		45	4	\N
46		46	2	\N
47		47	2	\N
48		48	2	\N
49		49	2	\N
50		50	3	\N
51		51	2	\N
52		52	3	\N
53		53	2	\N
54		54	3	\N
55		55	4	\N
56		56	3	\N
57		57	2	\N
58		58	2	\N
59		59	3	\N
60		60	4	\N
61		61	4	\N
62		62	3	\N
63		63	2	\N
64		64	3	\N
65		65	3	\N
66		66	3	\N
67		67	2	\N
68		68	2	\N
69		69	4	\N
70		70	3	\N
71		71	3	\N
72		72	4	\N
73		73	2	\N
74		74	3	\N
75		75	3	\N
76		76	3	\N
77		77	3	\N
78		78	3	\N
79		79	3	\N
80		80	4	\N
81		81	2	\N
82		82	4	\N
83		83	4	\N
84		84	2	\N
85		85	3	\N
86		86	2	\N
87		87	4	\N
88		88	2	\N
89		89	4	\N
90		90	3	\N
91		91	3	\N
92		92	3	\N
93		93	2	\N
94		94	4	\N
95		95	2	\N
96		96	4	\N
97		97	3	\N
98		98	4	\N
99		99	2	\N
100		100	4	\N
101		101	2	\N
102		102	2	\N
103		103	4	\N
104		104	3	\N
105		105	4	\N
106		106	2	\N
107		107	4	\N
108		108	2	\N
109		109	3	\N
110		110	3	\N
111		111	2	\N
112		112	3	\N
113		113	3	\N
114		114	2	\N
115		115	3	\N
116		116	4	\N
117		117	3	\N
118		118	2	\N
119		119	4	\N
120		120	4	\N
121		121	3	\N
122		122	4	\N
123		123	3	\N
124		124	2	\N
125		125	3	\N
126		126	3	\N
127		127	2	\N
128		128	4	\N
129		129	3	\N
130		130	3	\N
131		131	4	\N
132		132	2	\N
133		133	2	\N
134		134	2	\N
135		135	2	\N
136		136	4	\N
137		137	2	\N
138		138	3	\N
139		139	4	\N
140		140	3	\N
141		141	2	\N
142		142	2	\N
143		143	3	\N
144		144	2	\N
145		145	4	\N
146		146	3	\N
147		147	3	\N
148		148	2	\N
149		149	2	\N
150		150	3	\N
151		151	2	\N
152		152	4	\N
153		153	4	\N
154		154	3	\N
155		155	2	\N
156		156	3	\N
157		157	18	\N
158		157	19	\N
\.


--
-- Name: core_assignmentgroup_examiners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgroup_examiners_id_seq', 158, true);


--
-- Name: core_assignmentgroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgroup_id_seq', 157, true);


--
-- Data for Name: core_assignmentgrouptag; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgrouptag (id, tag, assignment_group_id) FROM stdin;
\.


--
-- Name: core_assignmentgrouptag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgrouptag_id_seq', 1, false);


--
-- Data for Name: core_candidate; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_candidate (id, candidate_id, automatic_anonymous_id, assignment_group_id, student_id, relatedstudent_id) FROM stdin;
1	\N		1	5	21
2	\N		2	8	22
3	\N		3	2	23
4	\N		4	9	24
5	\N		5	7	25
6	\N		6	6	26
7	\N		7	13	15
8	\N		8	14	16
9	\N		9	12	17
10	\N		10	10	18
11	\N		11	15	19
12	\N		12	11	20
13	\N		13	16	14
14	\N		14	5	21
15	\N		15	8	22
16	\N		16	2	23
17	\N		17	9	24
18	\N		18	7	25
19	\N		19	6	26
20	\N		20	13	15
21	\N		21	14	16
22	\N		22	12	17
23	\N		23	10	18
24	\N		24	15	19
25	\N		25	11	20
26	\N		26	16	14
27	\N		27	5	21
28	\N		28	8	22
29	\N		29	2	23
30	\N		30	9	24
31	\N		31	7	25
32	\N		32	6	26
33	\N		33	13	15
34	\N		34	14	16
35	\N		35	12	17
36	\N		36	10	18
37	\N		37	15	19
38	\N		38	11	20
39	\N		39	16	14
40	\N		40	5	21
41	\N		41	8	22
42	\N		42	2	23
43	\N		43	9	24
44	\N		44	7	25
45	\N		45	6	26
46	\N		46	13	15
47	\N		47	14	16
48	\N		48	12	17
49	\N		49	10	18
50	\N		50	15	19
51	\N		51	11	20
52	\N		52	16	14
53	\N		53	5	21
54	\N		54	8	22
55	\N		55	2	23
56	\N		56	9	24
57	\N		57	7	25
58	\N		58	6	26
59	\N		59	13	15
60	\N		60	14	16
61	\N		61	12	17
62	\N		62	10	18
63	\N		63	15	19
64	\N		64	11	20
65	\N		65	16	14
66	\N		66	5	21
67	\N		67	8	22
68	\N		68	2	23
69	\N		69	9	24
70	\N		70	7	25
71	\N		71	6	26
72	\N		72	13	15
73	\N		73	14	16
74	\N		74	12	17
75	\N		75	10	18
76	\N		76	15	19
77	\N		77	11	20
78	\N		78	16	14
79	\N		79	5	8
80	\N		80	8	9
81	\N		81	2	10
82	\N		82	9	11
83	\N		83	7	12
84	\N		84	6	13
85	\N		85	13	2
86	\N		86	14	3
87	\N		87	12	4
88	\N		88	10	5
89	\N		89	15	6
90	\N		90	11	7
91	\N		91	16	1
92	\N		92	5	8
93	\N		93	8	9
94	\N		94	2	10
95	\N		95	9	11
96	\N		96	7	12
97	\N		97	6	13
98	\N		98	13	2
99	\N		99	14	3
100	\N		100	12	4
101	\N		101	10	5
102	\N		102	15	6
103	\N		103	11	7
104	\N		104	16	1
105	\N		105	5	8
106	\N		106	8	9
107	\N		107	2	10
108	\N		108	9	11
109	\N		109	7	12
110	\N		110	6	13
111	\N		111	13	2
112	\N		112	14	3
113	\N		113	12	4
114	\N		114	10	5
115	\N		115	15	6
116	\N		116	11	7
117	\N		117	16	1
118	\N		118	5	8
119	\N		119	8	9
120	\N		120	2	10
121	\N		121	9	11
122	\N		122	7	12
123	\N		123	6	13
124	\N		124	13	2
125	\N		125	14	3
126	\N		126	12	4
127	\N		127	10	5
128	\N		128	15	6
129	\N		129	11	7
130	\N		130	16	1
131	\N		131	5	8
132	\N		132	8	9
133	\N		133	2	10
134	\N		134	9	11
135	\N		135	7	12
136	\N		136	6	13
137	\N		137	13	2
138	\N		138	14	3
139	\N		139	12	4
140	\N		140	10	5
141	\N		141	15	6
142	\N		142	11	7
143	\N		143	16	1
144	\N		144	5	\N
145	\N		145	8	\N
146	\N		146	2	\N
147	\N		147	9	\N
148	\N		148	7	\N
149	\N		149	6	\N
150	\N		150	13	\N
151	\N		151	14	\N
152	\N		152	12	\N
153	\N		153	10	\N
154	\N		154	15	\N
155	\N		155	11	\N
156	\N		156	16	\N
157	\N		157	17	27
\.


--
-- Name: core_candidate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_candidate_id_seq', 157, true);


--
-- Data for Name: core_deadline; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_deadline (id, deadline, text, deliveries_available_before_deadline, why_created, added_by_id, assignment_group_id) FROM stdin;
1	2014-11-11 14:15:00+01	\N	f	\N	\N	1
2	2014-11-11 14:15:00+01	\N	f	\N	\N	2
3	2014-11-11 14:15:00+01	\N	f	\N	\N	3
4	2014-11-11 14:15:00+01	\N	f	\N	\N	4
5	2014-11-11 14:15:00+01	\N	f	\N	\N	5
6	2014-11-11 14:15:00+01	\N	f	\N	\N	6
7	2014-11-11 14:15:00+01	\N	f	\N	\N	7
8	2014-11-11 14:15:00+01	\N	f	\N	\N	8
9	2014-11-11 14:15:00+01	\N	f	\N	\N	9
10	2014-11-11 14:15:00+01	\N	f	\N	\N	10
11	2014-11-11 14:15:00+01	\N	f	\N	\N	11
12	2014-11-11 14:15:00+01	\N	f	\N	\N	12
13	2014-11-11 14:15:00+01	\N	f	\N	\N	13
14	2014-11-18 14:15:00+01	\N	f	\N	\N	14
15	2014-11-18 14:15:00+01	\N	f	\N	\N	15
16	2014-11-18 14:15:00+01	\N	f	\N	\N	16
17	2014-11-18 14:15:00+01	\N	f	\N	\N	17
18	2014-11-18 14:15:00+01	\N	f	\N	\N	18
19	2014-11-18 14:15:00+01	\N	f	\N	\N	19
20	2014-11-18 14:15:00+01	\N	f	\N	\N	20
21	2014-11-18 14:15:00+01	\N	f	\N	\N	21
22	2014-11-18 14:15:00+01	\N	f	\N	\N	22
23	2014-11-18 14:15:00+01	\N	f	\N	\N	23
24	2014-11-18 14:15:00+01	\N	f	\N	\N	24
25	2014-11-18 14:15:00+01	\N	f	\N	\N	25
26	2014-11-18 14:15:00+01	\N	f	\N	\N	26
27	2014-11-25 14:15:00+01	\N	f	\N	\N	27
28	2014-11-25 14:15:00+01	\N	f	\N	\N	28
29	2014-11-25 14:15:00+01	\N	f	\N	\N	29
30	2014-11-25 14:15:00+01	\N	f	\N	\N	30
31	2014-11-25 14:15:00+01	\N	f	\N	\N	31
32	2014-11-25 14:15:00+01	\N	f	\N	\N	32
33	2014-11-25 14:15:00+01	\N	f	\N	\N	33
34	2014-11-25 14:15:00+01	\N	f	\N	\N	34
35	2014-11-25 14:15:00+01	\N	f	\N	\N	35
36	2014-11-25 14:15:00+01	\N	f	\N	\N	36
37	2014-11-25 14:15:00+01	\N	f	\N	\N	37
38	2014-11-25 14:15:00+01	\N	f	\N	\N	38
39	2014-11-25 14:15:00+01	\N	f	\N	\N	39
40	2014-12-02 14:15:00+01	\N	f	\N	\N	40
41	2014-12-02 14:15:00+01	\N	f	\N	\N	41
42	2014-12-02 14:15:00+01	\N	f	\N	\N	42
43	2014-12-02 14:15:00+01	\N	f	\N	\N	43
44	2014-12-02 14:15:00+01	\N	f	\N	\N	44
45	2014-12-02 14:15:00+01	\N	f	\N	\N	45
46	2014-12-02 14:15:00+01	\N	f	\N	\N	46
47	2014-12-02 14:15:00+01	\N	f	\N	\N	47
48	2014-12-02 14:15:00+01	\N	f	\N	\N	48
49	2014-12-02 14:15:00+01	\N	f	\N	\N	49
50	2014-12-02 14:15:00+01	\N	f	\N	\N	50
51	2014-12-02 14:15:00+01	\N	f	\N	\N	51
52	2014-12-02 14:15:00+01	\N	f	\N	\N	52
53	2014-12-16 14:15:00+01	\N	f	\N	\N	53
54	2014-12-16 14:15:00+01	\N	f	\N	\N	54
55	2014-12-16 14:15:00+01	\N	f	\N	\N	55
56	2014-12-16 14:15:00+01	\N	f	\N	\N	56
57	2014-12-16 14:15:00+01	\N	f	\N	\N	57
58	2014-12-16 14:15:00+01	\N	f	\N	\N	58
59	2014-12-16 14:15:00+01	\N	f	\N	\N	59
60	2014-12-16 14:15:00+01	\N	f	\N	\N	60
61	2014-12-16 14:15:00+01	\N	f	\N	\N	61
62	2014-12-16 14:15:00+01	\N	f	\N	\N	62
63	2014-12-16 14:15:00+01	\N	f	\N	\N	63
64	2014-12-16 14:15:00+01	\N	f	\N	\N	64
65	2014-12-16 14:15:00+01	\N	f	\N	\N	65
66	2015-12-22 14:15:00+01	\N	f	\N	\N	144
67	2015-12-22 14:15:00+01	\N	f	\N	\N	145
68	2015-12-22 14:15:00+01	\N	f	\N	\N	146
69	2015-12-22 14:15:00+01	\N	f	\N	\N	147
70	2015-12-22 14:15:00+01	\N	f	\N	\N	148
71	2015-12-22 14:15:00+01	\N	f	\N	\N	149
72	2015-12-22 14:15:00+01	\N	f	\N	\N	150
73	2015-12-22 14:15:00+01	\N	f	\N	\N	151
74	2015-12-22 14:15:00+01	\N	f	\N	\N	152
75	2015-12-22 14:15:00+01	\N	f	\N	\N	153
76	2015-12-22 14:15:00+01	\N	f	\N	\N	154
77	2015-12-22 14:15:00+01	\N	f	\N	\N	155
78	2015-12-22 14:15:00+01	\N	f	\N	\N	156
\.


--
-- Name: core_deadline_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_deadline_id_seq', 78, true);


--
-- Data for Name: core_delivery; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_delivery (id, delivery_type, time_of_delivery, number, successful, alias_delivery_id, copy_of_id, deadline_id, delivered_by_id, last_feedback_id) FROM stdin;
1	0	2014-11-10 13:15:00+01	1	t	\N	\N	1	\N	1
2	0	2014-11-10 08:15:00+01	1	t	\N	\N	2	\N	2
3	0	2014-11-11 12:15:00+01	1	t	\N	\N	3	\N	3
4	0	2014-11-11 00:15:00+01	1	t	\N	\N	4	\N	4
5	0	2014-11-10 10:15:00+01	1	t	\N	\N	5	\N	5
6	0	2014-11-11 02:15:00+01	1	t	\N	\N	6	\N	6
7	0	2014-11-11 01:15:00+01	1	t	\N	\N	7	\N	7
8	0	2014-11-10 19:15:00+01	1	t	\N	\N	8	\N	8
9	0	2014-11-11 11:15:00+01	1	t	\N	\N	9	\N	9
10	0	2014-11-10 12:15:00+01	1	t	\N	\N	10	\N	10
11	0	2014-11-10 15:15:00+01	1	t	\N	\N	11	\N	11
12	0	2014-11-11 06:15:00+01	1	t	\N	\N	12	\N	12
13	0	2014-11-10 16:15:00+01	1	t	\N	\N	13	\N	13
14	0	2014-11-18 03:15:00+01	1	t	\N	\N	14	\N	14
15	0	2014-11-18 12:15:00+01	1	t	\N	\N	15	\N	15
16	0	2014-11-17 23:15:00+01	1	t	\N	\N	16	\N	16
17	0	2014-11-17 09:15:00+01	1	t	\N	\N	17	\N	17
18	0	2014-11-17 13:15:00+01	1	t	\N	\N	18	\N	18
19	0	2014-11-18 01:15:00+01	1	t	\N	\N	19	\N	19
20	0	2014-11-18 10:15:00+01	1	t	\N	\N	20	\N	20
21	0	2014-11-17 17:15:00+01	1	t	\N	\N	21	\N	21
22	0	2014-11-18 05:15:00+01	1	t	\N	\N	22	\N	22
23	0	2014-11-18 03:15:00+01	1	t	\N	\N	23	\N	23
24	0	2014-11-17 13:15:00+01	1	t	\N	\N	24	\N	24
25	0	2014-11-17 20:15:00+01	1	t	\N	\N	25	\N	25
26	0	2014-11-17 14:15:00+01	1	t	\N	\N	26	\N	26
27	0	2014-11-24 10:15:00+01	1	t	\N	\N	27	\N	27
28	0	2014-11-25 06:15:00+01	1	t	\N	\N	28	\N	28
29	0	2014-11-24 08:15:00+01	1	t	\N	\N	29	\N	29
30	0	2014-11-24 13:15:00+01	1	t	\N	\N	30	\N	30
31	0	2014-11-24 16:15:00+01	1	t	\N	\N	31	\N	31
32	0	2014-11-24 17:15:00+01	1	t	\N	\N	32	\N	32
33	0	2014-11-25 11:15:00+01	1	t	\N	\N	33	\N	33
34	0	2014-11-25 06:15:00+01	1	t	\N	\N	34	\N	34
35	0	2014-11-24 23:15:00+01	1	t	\N	\N	35	\N	35
36	0	2014-11-25 04:15:00+01	1	t	\N	\N	36	\N	36
37	0	2014-11-24 20:15:00+01	1	t	\N	\N	37	\N	37
38	0	2014-11-24 20:15:00+01	1	t	\N	\N	38	\N	38
39	0	2014-11-25 09:15:00+01	1	t	\N	\N	39	\N	39
40	0	2014-12-02 13:15:00+01	1	t	\N	\N	40	\N	40
41	0	2014-12-01 22:15:00+01	1	t	\N	\N	41	\N	41
42	0	2014-12-01 09:15:00+01	1	t	\N	\N	42	\N	42
43	0	2014-12-02 13:15:00+01	1	t	\N	\N	43	\N	43
44	0	2014-12-02 10:15:00+01	1	t	\N	\N	44	\N	44
45	0	2014-12-02 04:15:00+01	1	t	\N	\N	45	\N	45
46	0	2014-12-01 14:15:00+01	1	t	\N	\N	46	\N	46
47	0	2014-12-01 08:15:00+01	1	t	\N	\N	47	\N	47
48	0	2014-12-02 07:15:00+01	1	t	\N	\N	48	\N	48
49	0	2014-12-01 18:15:00+01	1	t	\N	\N	49	\N	49
50	0	2014-12-02 10:15:00+01	1	t	\N	\N	50	\N	50
51	0	2014-12-02 03:15:00+01	1	t	\N	\N	51	\N	51
52	0	2014-12-01 23:15:00+01	1	t	\N	\N	52	\N	52
53	0	2014-12-16 10:15:00+01	1	t	\N	\N	53	\N	53
54	0	2014-12-16 00:15:00+01	1	t	\N	\N	54	\N	54
55	0	2014-12-15 21:15:00+01	1	t	\N	\N	55	\N	55
56	0	2014-12-15 16:15:00+01	1	t	\N	\N	56	\N	56
57	0	2014-12-16 07:15:00+01	1	t	\N	\N	57	\N	57
58	0	2014-12-15 23:15:00+01	1	t	\N	\N	58	\N	58
59	0	2014-12-15 08:15:00+01	1	t	\N	\N	59	\N	59
60	0	2014-12-16 05:15:00+01	1	t	\N	\N	60	\N	60
61	0	2014-12-16 03:15:00+01	1	t	\N	\N	61	\N	61
62	0	2014-12-16 04:15:00+01	1	t	\N	\N	62	\N	62
63	0	2014-12-16 03:15:00+01	1	t	\N	\N	63	\N	63
64	0	2014-12-16 12:15:00+01	1	t	\N	\N	64	\N	64
65	0	2014-12-16 02:15:00+01	1	t	\N	\N	65	\N	65
\.


--
-- Name: core_delivery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_delivery_id_seq', 65, true);


--
-- Data for Name: core_devilryuserprofile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_devilryuserprofile (id, full_name, languagecode, user_id) FROM stdin;
\.


--
-- Name: core_devilryuserprofile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_devilryuserprofile_id_seq', 1, false);


--
-- Data for Name: core_filemeta; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_filemeta (id, filename, size, delivery_id) FROM stdin;
1	test.py	12	1
2	Hello.java	110	1
3	demo.py	16	1
4	generate.py	76	1
5	Demo.java	239	2
6	test.py	12	2
7	count.py	154	2
8	demo.py	16	2
9	addtimes.py	56	3
10	generate.py	76	3
11	Hello.java	110	3
12	Demo.java	239	3
13	demo.py	16	4
14	addtimes.py	56	4
15	generate.py	76	4
16	hello.py	40	4
17	Hello.java	110	5
18	addtimes.py	56	5
19	generate.py	76	5
20	demo.py	16	5
21	sum.py	30	6
22	hello.py	40	6
23	generate.py	76	6
24	demo.py	16	6
25	demo.py	16	7
26	test.py	12	7
27	Demo.java	239	7
28	sum.py	30	7
29	addtimes.py	56	8
30	sum.py	30	8
31	hello.py	40	8
32	Hello.java	110	8
33	hello.py	40	9
34	Hello.java	110	9
35	count.py	154	9
36	demo.py	16	9
37	sum.py	30	10
38	Demo.java	239	10
39	demo.py	16	10
40	count.py	154	10
41	test.py	12	11
42	Demo.java	239	11
43	demo.py	16	11
44	hello.py	40	11
45	demo.py	16	12
46	generate.py	76	12
47	hello.py	40	12
48	Demo.java	239	12
49	hello.py	40	13
50	demo.py	16	13
51	Demo.java	239	13
52	generate.py	76	13
53	count.py	154	14
54	Hello.java	110	14
55	demo.py	16	15
56	test.py	12	15
57	demo.py	16	16
58	count.py	154	16
59	count.py	154	17
60	Demo.java	239	17
61	count.py	154	18
62	generate.py	76	18
63	demo.py	16	19
64	addtimes.py	56	19
65	addtimes.py	56	20
66	Demo.java	239	20
67	Demo.java	239	21
68	hello.py	40	21
69	count.py	154	22
70	Demo.java	239	22
71	addtimes.py	56	23
72	generate.py	76	23
73	test.py	12	24
74	count.py	154	24
75	hello.py	40	25
76	test.py	12	25
77	demo.py	16	26
78	Hello.java	110	26
79	Hello.java	110	27
80	addtimes.py	56	27
81	hello.py	40	27
82	demo.py	16	27
83	addtimes.py	56	28
84	Hello.java	110	28
85	generate.py	76	28
86	count.py	154	28
87	demo.py	16	29
88	count.py	154	29
89	addtimes.py	56	29
90	hello.py	40	29
91	Demo.java	239	30
92	generate.py	76	30
93	addtimes.py	56	30
94	sum.py	30	30
95	Demo.java	239	31
96	count.py	154	31
97	Hello.java	110	31
98	sum.py	30	31
99	count.py	154	32
100	Hello.java	110	32
101	hello.py	40	32
102	demo.py	16	32
103	test.py	12	33
104	count.py	154	33
105	demo.py	16	33
106	Hello.java	110	33
107	demo.py	16	34
108	generate.py	76	34
109	Demo.java	239	34
110	count.py	154	34
111	test.py	12	35
112	sum.py	30	35
113	generate.py	76	35
114	addtimes.py	56	35
115	count.py	154	36
116	demo.py	16	36
117	Hello.java	110	36
118	hello.py	40	36
119	generate.py	76	37
120	count.py	154	37
121	Demo.java	239	37
122	Hello.java	110	37
123	addtimes.py	56	38
124	count.py	154	38
125	demo.py	16	38
126	sum.py	30	38
127	Demo.java	239	39
128	demo.py	16	39
129	hello.py	40	39
130	count.py	154	39
131	addtimes.py	56	40
132	hello.py	40	40
133	count.py	154	40
134	test.py	12	40
135	Hello.java	110	40
136	generate.py	76	40
137	Demo.java	239	40
138	sum.py	30	40
139	sum.py	30	41
140	addtimes.py	56	41
141	Hello.java	110	41
142	generate.py	76	41
143	Demo.java	239	41
144	hello.py	40	41
145	test.py	12	41
146	count.py	154	41
147	sum.py	30	42
148	hello.py	40	42
149	addtimes.py	56	42
150	Demo.java	239	42
151	count.py	154	42
152	Hello.java	110	42
153	generate.py	76	42
154	demo.py	16	42
155	test.py	12	43
156	sum.py	30	43
157	addtimes.py	56	43
158	demo.py	16	43
159	Demo.java	239	43
160	hello.py	40	43
161	generate.py	76	43
162	count.py	154	43
163	Demo.java	239	44
164	count.py	154	44
165	test.py	12	44
166	hello.py	40	44
167	addtimes.py	56	44
168	Hello.java	110	44
169	sum.py	30	44
170	demo.py	16	44
171	sum.py	30	45
172	hello.py	40	45
173	generate.py	76	45
174	Demo.java	239	45
175	test.py	12	45
176	demo.py	16	45
177	count.py	154	45
178	addtimes.py	56	45
179	Demo.java	239	46
180	Hello.java	110	46
181	test.py	12	46
182	addtimes.py	56	46
183	sum.py	30	46
184	count.py	154	46
185	generate.py	76	46
186	demo.py	16	46
187	Demo.java	239	47
188	generate.py	76	47
189	sum.py	30	47
190	demo.py	16	47
191	addtimes.py	56	47
192	hello.py	40	47
193	Hello.java	110	47
194	test.py	12	47
195	Hello.java	110	48
196	Demo.java	239	48
197	demo.py	16	48
198	generate.py	76	48
199	hello.py	40	48
200	count.py	154	48
201	sum.py	30	48
202	addtimes.py	56	48
203	generate.py	76	49
204	test.py	12	49
205	count.py	154	49
206	demo.py	16	49
207	sum.py	30	49
208	addtimes.py	56	49
209	Demo.java	239	49
210	Hello.java	110	49
211	Demo.java	239	50
212	test.py	12	50
213	demo.py	16	50
214	count.py	154	50
215	generate.py	76	50
216	addtimes.py	56	50
217	Hello.java	110	50
218	sum.py	30	50
219	count.py	154	51
220	generate.py	76	51
221	Demo.java	239	51
222	hello.py	40	51
223	sum.py	30	51
224	test.py	12	51
225	addtimes.py	56	51
226	Hello.java	110	51
227	Hello.java	110	52
228	demo.py	16	52
229	sum.py	30	52
230	addtimes.py	56	52
231	generate.py	76	52
232	hello.py	40	52
233	test.py	12	52
234	count.py	154	52
235	hello.py	40	53
236	sum.py	30	54
237	addtimes.py	56	55
238	test.py	12	56
239	sum.py	30	57
240	sum.py	30	58
241	addtimes.py	56	59
242	Hello.java	110	60
243	hello.py	40	61
244	sum.py	30	62
245	demo.py	16	63
246	count.py	154	64
247	demo.py	16	65
\.


--
-- Name: core_filemeta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_filemeta_id_seq', 247, true);


--
-- Data for Name: core_groupinvite; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_groupinvite (id, sent_datetime, accepted, responded_datetime, group_id, sent_by_id, sent_to_id) FROM stdin;
\.


--
-- Name: core_groupinvite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_groupinvite_id_seq', 1, false);


--
-- Data for Name: core_node; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_node (id, short_name, long_name, etag, parentnode_id) FROM stdin;
1	duckburgh	University of Duckburgh	2015-12-15 14:15:15.634183+01	\N
\.


--
-- Data for Name: core_node_admins; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_node_admins (id, node_id, user_id) FROM stdin;
\.


--
-- Name: core_node_admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_node_admins_id_seq', 1, false);


--
-- Name: core_node_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_node_id_seq', 1, true);


--
-- Data for Name: core_period; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_period (id, short_name, long_name, start_time, end_time, etag, parentnode_id) FROM stdin;
1	testsemester	Testsemester	2015-09-16 14:15:15.9967+02	2016-03-14 14:15:15.996716+01	2015-12-15 14:15:15.997008+01	2
2	oldtestsemester	Old testsemester	2014-09-16 14:15:16.0458+02	2015-03-15 14:15:16.045816+01	2015-12-15 14:15:16.046094+01	2
3	testsemester	Testsemester	2015-09-16 14:15:43.808228+02	2016-03-14 14:15:43.808243+01	2015-12-15 14:15:43.808601+01	3
\.


--
-- Data for Name: core_period_admins; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_period_admins (id, period_id, user_id) FROM stdin;
\.


--
-- Name: core_period_admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_period_admins_id_seq', 1, false);


--
-- Name: core_period_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_period_id_seq', 3, true);


--
-- Data for Name: core_periodapplicationkeyvalue; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_periodapplicationkeyvalue (id, application, key, value, period_id) FROM stdin;
\.


--
-- Name: core_periodapplicationkeyvalue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_periodapplicationkeyvalue_id_seq', 1, false);


--
-- Data for Name: core_pointrangetograde; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_pointrangetograde (id, minimum_points, maximum_points, grade, point_to_grade_map_id) FROM stdin;
\.


--
-- Name: core_pointrangetograde_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_pointrangetograde_id_seq', 1, false);


--
-- Data for Name: core_pointtogrademap; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_pointtogrademap (id, invalid, assignment_id) FROM stdin;
\.


--
-- Name: core_pointtogrademap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_pointtogrademap_id_seq', 1, false);


--
-- Data for Name: core_relatedexaminer; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_relatedexaminer (id, tags, period_id, user_id, automatic_anonymous_id) FROM stdin;
1		1	2	
2	group1	1	3	
3	group2	1	4	
4		2	2	
5	group1	2	3	
6	group2	2	4	
7	\N	3	18	
8	\N	3	19	
\.


--
-- Name: core_relatedexaminer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedexaminer_id_seq', 8, true);


--
-- Data for Name: core_relatedexaminersyncsystemtag; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_relatedexaminersyncsystemtag (id, tag, relatedexaminer_id) FROM stdin;
\.


--
-- Name: core_relatedexaminersyncsystemtag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedexaminersyncsystemtag_id_seq', 1, false);


--
-- Data for Name: core_relatedstudent; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_relatedstudent (id, tags, candidate_id, automatic_anonymous_id, period_id, user_id, active) FROM stdin;
1	group1	\N		1	16	t
2	group1	\N		1	13	t
3	group1	\N		1	14	t
4	group1	\N		1	12	t
5	group1	\N		1	10	t
6	group1	\N		1	15	t
7	group1	\N		1	11	t
8	group2	\N		1	5	t
9	group2	\N		1	8	t
10	group2	\N		1	2	t
11	group2	\N		1	9	t
12	group2	\N		1	7	t
13	group2	\N		1	6	t
14	group1	\N		2	16	t
15	group1	\N		2	13	t
16	group1	\N		2	14	t
17	group1	\N		2	12	t
18	group1	\N		2	10	t
19	group1	\N		2	15	t
20	group1	\N		2	11	t
21	group2	\N		2	5	t
22	group2	\N		2	8	t
23	group2	\N		2	2	t
24	group2	\N		2	9	t
25	group2	\N		2	7	t
26	group2	\N		2	6	t
27	\N	\N		3	17	t
\.


--
-- Name: core_relatedstudent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedstudent_id_seq', 27, true);


--
-- Data for Name: core_relatedstudentkeyvalue; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_relatedstudentkeyvalue (id, application, key, value, student_can_read, relatedstudent_id) FROM stdin;
\.


--
-- Name: core_relatedstudentkeyvalue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedstudentkeyvalue_id_seq', 1, false);


--
-- Data for Name: core_relatedstudentsyncsystemtag; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_relatedstudentsyncsystemtag (id, tag, relatedstudent_id) FROM stdin;
\.


--
-- Name: core_relatedstudentsyncsystemtag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedstudentsyncsystemtag_id_seq', 1, false);


--
-- Data for Name: core_staticfeedback; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_staticfeedback (id, rendered_view, grade, points, is_passing_grade, save_timestamp, delivery_id, saved_by_id) FROM stdin;
1	<p>Aliquam delectus perspiciatis dolores eaque voluptate, esse ex dolor aliquam ipsa corrupti dolores eligendi. Eveniet magni consectetur accusantium aspernatur, fugiat itaque ipsum veniam accusamus facere minus quod ullam, incidunt culpa et placeat nihil quaerat id aperiam ab quibusdam asperiores, architecto quos quo nulla asperiores unde minus deserunt sint. Magni corrupti cupiditate illo obcaecati sequi odio natus quasi autem pariatur, ratione atque numquam quia eos inventore similique magnam quos tempore beatae sunt, cum ea quos labore, eaque reiciendis porro vero molestiae, reprehenderit reiciendis in deserunt.</p>\n<p>Commodi voluptate velit perspiciatis qui officia dolore soluta molestiae harum ea, praesentium quibusdam laborum nesciunt tempora vel, dolore rem officiis voluptates incidunt blanditiis alias porro illo deleniti ipsum aliquid, obcaecati debitis veniam culpa sed aut, similique delectus consequuntur aperiam debitis nemo saepe magnam laboriosam maxime repellendus? Voluptates qui soluta quia tempora natus illum.</p>	1/4	1	t	2015-12-15 14:15:16.371248+01	1	2
2	<p>Aut deserunt numquam atque distinctio, non tenetur quo officia saepe atque optio, blanditiis quod facilis corrupti dolor magnam sequi consequatur sapiente. Id sapiente tempore odio sint recusandae, cupiditate expedita minima ipsum recusandae amet sapiente illo?</p>\n<p>Sunt dignissimos eum aspernatur ea architecto doloribus ad, asperiores voluptatem non recusandae tempora itaque iure magni excepturi quis minus quas, similique nostrum optio culpa natus porro animi vel voluptas possimus ipsam, animi praesentium molestiae, eveniet quae doloremque ducimus modi veniam cupiditate quam ratione neque facilis.</p>\n<p>Similique at iure itaque est accusamus voluptatum assumenda ab quidem quae laudantium, ducimus qui minus facere numquam quas sunt voluptatum eius, qui dolore rerum odit pariatur quasi ex illum impedit? Veniam quia autem voluptas quas suscipit esse a et corrupti, sapiente nam recusandae eos dolorem assumenda architecto aliquid, vel dicta quod asperiores maxime dolore aliquid tenetur.</p>	0/4	0	f	2015-12-15 14:15:16.923008+01	2	4
3	<p>Nesciunt soluta blanditiis rem porro expedita doloremque impedit deserunt, quaerat voluptas alias maiores neque odit perspiciatis dolor asperiores, tenetur assumenda magnam voluptatum necessitatibus nemo porro dolorem distinctio sunt enim harum, consequuntur voluptas recusandae laudantium temporibus accusantium, fugit perspiciatis mollitia tenetur. Corrupti omnis voluptates cumque repellat quasi dignissimos vel sapiente, possimus veritatis commodi totam facilis velit, reiciendis incidunt hic sint quam maxime ratione amet velit a, soluta ipsam cumque numquam ex minima natus amet officiis, unde est nisi repellendus tempora sequi modi laborum mollitia ad. Ipsa laboriosam explicabo itaque tempore magni porro quaerat sit, ipsam cumque suscipit aut quia aliquid?</p>\n<p>Laudantium dolor sint. Sint quod culpa magni, quia explicabo ab dicta ex tenetur obcaecati dignissimos soluta saepe, illo maiores explicabo sequi?</p>	0/4	0	f	2015-12-15 14:15:17.209596+01	3	4
4	<p>Voluptate labore possimus minima minus quisquam impedit error nisi, odio corporis maxime alias eaque sequi architecto veniam repellat nemo, velit iusto iure fuga voluptates. Distinctio non quam nam voluptatibus perferendis amet dolores odit? Perferendis quod facilis earum quam distinctio est quasi ex dolores hic error, maxime nihil similique facilis aut unde quis dolorum eaque, nihil culpa neque ab iusto nesciunt rerum soluta provident laboriosam, doloremque eaque sequi ab repellendus animi nesciunt odio temporibus dolore laboriosam sit, illo pariatur suscipit maiores accusantium minus perspiciatis iusto quae? Totam dolore ex, inventore deleniti aut blanditiis molestiae nobis eum accusantium eaque totam, corrupti suscipit omnis adipisci reprehenderit ad officia non fugit explicabo ut perspiciatis, non natus cum impedit.</p>\n<p>Eligendi iusto quibusdam vero aperiam ducimus distinctio, ad fuga ducimus ratione corporis atque nemo aspernatur a incidunt, magni sapiente doloribus corrupti eveniet consequatur debitis beatae vero officiis, veritatis laboriosam amet quia saepe minus possimus eos consequuntur neque officiis? Optio suscipit nisi est odio fugit aspernatur excepturi debitis, sapiente dolores inventore, velit voluptates itaque corrupti voluptatum nam ab delectus ad doloremque consectetur ipsum, dolorum ipsa dicta facere nam pariatur, harum accusamus optio facilis? Quidem voluptates dicta quisquam architecto eligendi laboriosam, quae consequatur molestiae vitae quas ratione expedita ex adipisci ea minima iure, quidem aut praesentium debitis.</p>\n<p>Nemo natus similique veritatis veniam iure adipisci, exercitationem doloremque consequuntur quos architecto eius dolores quas sequi rerum unde delectus, adipisci iste necessitatibus aliquid doloremque delectus odit? Dolor accusamus beatae laudantium et consequatur, nobis quam dolorem sapiente eveniet tenetur quos harum et quibusdam impedit, animi alias perferendis? Rerum explicabo quod cumque aut fugit fuga quas similique esse, quisquam officiis veniam omnis, tempore dolorum vel nesciunt mollitia, velit eum quam nemo vitae at saepe voluptatem expedita? Iusto itaque nobis voluptates necessitatibus quae, veritatis aperiam culpa, illo quidem necessitatibus sapiente, praesentium molestias odit illum mollitia assumenda rem harum doloribus quidem maxime ut?</p>\n<p>Magni non esse iste dolorum eos corrupti inventore dolorem dicta omnis consequatur, quam necessitatibus molestiae exercitationem consequuntur ullam quae nulla adipisci consequatur totam cum, labore fugiat in ipsam aut.</p>\n<p>Iste non earum minima mollitia dolore repellendus beatae, vitae nulla libero id error nihil reiciendis quae suscipit doloribus accusantium debitis, at voluptates necessitatibus ipsum eos magni incidunt culpa itaque inventore? At itaque magnam debitis ratione tempore suscipit ea non rerum esse.</p>	2/4	2	t	2015-12-15 14:15:17.48977+01	4	2
5	<p>Sapiente nam voluptas in aperiam ad omnis libero provident, enim blanditiis quidem, excepturi voluptatum itaque culpa reiciendis voluptate modi minima, veritatis facere aliquam soluta molestiae beatae non sint amet, beatae accusamus ipsa quibusdam possimus quam deleniti hic consequuntur? Aperiam omnis impedit exercitationem soluta blanditiis, eum veniam magnam, eligendi assumenda minus. Maiores nam repellat hic magnam ducimus natus numquam quo sit atque assumenda, praesentium nisi nihil eos possimus omnis quam perferendis pariatur voluptatem officiis nobis, ipsam quod non, facilis modi eius inventore, repellat facere ab fugit velit nam. Facilis porro in fugiat non iure soluta, aperiam quos distinctio id ullam amet nam, iusto natus porro eos corporis vel dolorum non, natus sequi enim at possimus cumque quasi tenetur modi dolorem?</p>\n<p>Consequuntur quis tempora fuga aperiam in cum voluptate natus sequi? Minima rem repellat eaque commodi non accusamus maxime dicta rerum earum expedita, neque qui incidunt asperiores, quisquam aperiam quasi amet temporibus tempora assumenda vel laboriosam. Animi inventore assumenda minus veniam mollitia, voluptas rerum dolorum fugit voluptatibus magnam officiis molestias, similique laborum recusandae nulla voluptate cupiditate iste porro esse dolorem, alias ut atque necessitatibus quae eligendi?</p>\n<p>Incidunt unde sint? Sint quaerat doloribus sit laborum cum numquam optio voluptate eum ipsam illo, cum dolorum facere eveniet natus suscipit corporis praesentium tempore, tempora deleniti dignissimos quisquam id quaerat ut tempore nemo nihil fugiat, sit temporibus rerum perferendis praesentium dolorum magnam qui.</p>\n<p>Distinctio reprehenderit beatae est minus maxime quae optio ullam ex repudiandae? Aliquid deserunt tempora doloribus quas a voluptate est, nisi excepturi expedita laudantium aperiam quod, unde in dignissimos maiores eum praesentium rerum culpa vitae sint aut, esse expedita neque doloremque vitae?</p>	2/4	2	t	2015-12-15 14:15:17.772313+01	5	4
6	<p>Nostrum deserunt animi a, consequatur quis velit suscipit voluptates saepe deserunt vitae aspernatur adipisci praesentium.</p>\n<p>Consequuntur cum quis ut adipisci quisquam quas voluptatum amet voluptatibus, praesentium voluptatem quasi laudantium eos explicabo dolore quidem pariatur, corporis odit commodi enim adipisci neque dolorum labore quae. Beatae saepe laudantium assumenda maxime sapiente a, quam eveniet ducimus dolores debitis, debitis corrupti molestiae quis in, voluptate repellat ea atque, obcaecati consectetur ipsa aliquid eveniet illo placeat dolores eius dolor. Obcaecati nemo laboriosam dicta ratione modi nulla aliquid, harum ad corrupti labore perferendis veniam eligendi exercitationem expedita sed, assumenda quas iure eius asperiores aspernatur error quaerat nisi at vitae.</p>\n<p>Maxime beatae et unde nobis iste voluptatum id natus, magnam et qui quos doloribus fuga accusantium cum. Perspiciatis ducimus enim maiores a rerum provident eos aliquam non tempore.</p>\n<p>Minima in fuga corrupti cum ipsa explicabo tempora at delectus accusamus, consequuntur perferendis amet autem odit cum laudantium molestiae ad, dignissimos aut dicta ratione non? Dolor ad ducimus aut quisquam maxime saepe neque adipisci dolore corrupti, sint esse iure ipsa ipsum delectus non ducimus unde dolorem, excepturi soluta possimus pariatur perferendis praesentium, sequi quos voluptates accusamus impedit, possimus quasi quae odio consequatur eveniet ipsum explicabo incidunt aliquid eos laborum? Sint quod numquam cum cumque, natus dicta tempore fuga eligendi molestias numquam distinctio odio cupiditate corrupti, architecto maxime necessitatibus enim repellendus reprehenderit facilis voluptatibus, blanditiis quisquam porro obcaecati ad dolorum numquam, quo similique temporibus.</p>	0/4	0	f	2015-12-15 14:15:18.039621+01	6	3
41	<p>Totam minima minus voluptatem repellendus, officiis veritatis eligendi tempore porro distinctio sunt blanditiis aliquam praesentium veniam a.</p>	4/8	4	t	2015-12-15 14:15:27.157802+01	41	2
7	<p>Voluptates dignissimos nulla sequi maiores modi qui, nulla nobis nisi voluptatem non quas debitis velit sequi reprehenderit.</p>\n<p>Tenetur modi sint culpa libero quia at nesciunt odit cumque minima. Tempora ducimus minus dolorem? Voluptate eveniet repudiandae laboriosam facilis exercitationem provident error, minima praesentium et voluptatum rem eius ducimus perferendis, nulla eligendi atque dolore cum obcaecati ipsum delectus totam architecto laborum, iste labore blanditiis aliquam mollitia quibusdam et quasi nam reiciendis esse, veritatis exercitationem facere aliquid iusto quas?</p>\n<p>Et eaque minima asperiores modi. Natus at repellendus architecto veniam dicta quis provident, fuga totam corrupti numquam doloremque libero nemo maiores, beatae sapiente aliquid odit earum facilis omnis tempora a pariatur. Iusto laborum eum, id dolore quis placeat autem modi quod impedit laborum, sequi blanditiis neque saepe alias incidunt dignissimos enim aspernatur ipsam amet, explicabo itaque asperiores dignissimos tenetur quis magni fugiat delectus quam deleniti, eos error reiciendis cupiditate neque quidem dolore sapiente labore sequi.</p>	2/4	2	t	2015-12-15 14:15:18.326896+01	7	2
8	<p>Excepturi similique unde recusandae, ad quas debitis excepturi sunt et, incidunt reiciendis eligendi atque eum assumenda similique ipsum corporis accusantium placeat, quam numquam quo repellat adipisci voluptatum dolorem?</p>\n<p>Aliquam maxime earum impedit beatae? Qui numquam incidunt eveniet in, reprehenderit doloribus fugiat, sapiente suscipit numquam nobis aliquid cupiditate omnis asperiores earum? Nostrum veniam modi sunt consequatur animi perferendis fuga omnis voluptate, laudantium inventore perspiciatis voluptatem natus adipisci pariatur eius saepe. Sequi exercitationem officiis adipisci possimus, vitae maxime molestias nihil ut itaque aut, impedit expedita quis beatae.</p>\n<p>At repudiandae laboriosam ad tenetur nam earum ex, dolorum repudiandae sit consectetur fugit illum saepe animi commodi nostrum provident veritatis, reprehenderit pariatur aspernatur reiciendis magni hic sapiente soluta nesciunt, quisquam cupiditate laboriosam aut inventore.</p>	4/4	4	t	2015-12-15 14:15:18.587656+01	8	3
9	<p>Eaque sint eligendi debitis vero consectetur nisi unde, itaque amet enim voluptas in magni iure nemo nobis laborum laboriosam, ducimus quis nisi non blanditiis harum eos commodi eum quia obcaecati iure, vero corporis eveniet incidunt totam officiis mollitia tenetur quidem, iure corrupti quo dignissimos nulla architecto exercitationem.</p>\n<p>Illum numquam dolore saepe cumque natus quidem, recusandae et delectus, ullam praesentium necessitatibus ipsam aspernatur esse at quas obcaecati sequi id? Consequatur ipsa quod beatae quidem, asperiores autem cupiditate optio commodi? Perferendis impedit deleniti numquam eaque inventore, itaque molestias aliquam perferendis, numquam iusto voluptatum fuga fugiat quaerat sit veritatis repudiandae at?</p>	4/4	4	t	2015-12-15 14:15:18.830575+01	9	4
10	<p>Necessitatibus ducimus obcaecati?</p>\n<p>Repellendus officia ex doloremque qui facere labore inventore atque, non suscipit culpa cum corporis, et consequuntur placeat dolores alias perferendis nobis facere aperiam id, omnis alias nulla molestiae quaerat necessitatibus. Quasi soluta in itaque, numquam dolor quibusdam laborum sit corporis, placeat ducimus blanditiis? Laboriosam reprehenderit doloremque?</p>\n<p>Laborum repellendus quia ratione beatae qui sit vel, doloremque ipsum animi asperiores voluptas, nesciunt aspernatur amet libero quasi fugiat dicta.</p>\n<p>Consequuntur aliquid facilis nam quo, laboriosam tempora iste sequi earum culpa sint, provident voluptates nihil ipsum quam non eveniet unde enim neque, vel deserunt amet dolore, ut quasi voluptates accusamus reprehenderit repellat officiis perspiciatis quos maiores.</p>	4/4	4	t	2015-12-15 14:15:19.065471+01	10	4
11	<p>Quae rerum aut vel minima repellat similique exercitationem ut magnam accusamus et, eaque rerum incidunt hic rem, eum error fuga ea quia excepturi a nulla voluptates assumenda. Nemo fugit et rem eveniet culpa cum hic ab amet ex at, amet est perferendis iste neque ipsa aliquid quas vero officiis nulla, hic officiis rerum delectus commodi quis dolores qui dolor dicta ratione cumque? Ut est perferendis quae dolorem exercitationem fuga, doloribus blanditiis expedita earum perferendis tempora voluptatem deleniti. Perferendis ipsam animi temporibus laborum amet voluptate, eius repellendus debitis iure nemo perspiciatis excepturi officia corrupti nisi, magni fugiat laboriosam ipsum consequuntur, quos aliquid inventore soluta dolorum unde tempora maiores voluptatum dolor, sunt corrupti laudantium?</p>\n<p>Eaque laborum ullam voluptatem reiciendis et autem cum dolor rem eius facilis, earum impedit sapiente cum cupiditate voluptas, sunt perferendis minima dicta quibusdam eum nemo laboriosam neque, sit fugiat sequi nesciunt consequatur in veritatis molestiae ut id?</p>\n<p>Dignissimos reiciendis libero.</p>	2/4	2	t	2015-12-15 14:15:19.33818+01	11	4
12	<p>Iste optio non aperiam, nemo eius quidem vero qui sit enim, distinctio libero quae porro quis, tenetur iure mollitia soluta sequi totam temporibus, neque enim deserunt? Optio quidem alias dolores tempore repellat fugit, vero recusandae libero architecto rerum necessitatibus fugit fuga, doloribus magni pariatur corporis sapiente voluptate tempora quo optio nostrum temporibus soluta? Similique rem eaque nobis officia aliquid id ea, molestias modi beatae repellendus ipsa? Debitis non error vitae, placeat labore nihil maiores fuga amet tempore officia dolorum, totam ea ab ut sed iure necessitatibus laudantium, maxime placeat a est quas, impedit vero quas quae?</p>\n<p>Reiciendis placeat quia quibusdam sunt, voluptatum inventore delectus ex quas minus obcaecati labore ipsa quisquam quae. Illo quasi eveniet omnis harum aut id nulla eaque ipsum ad?</p>\n<p>Placeat tenetur quis esse aut explicabo, aliquam alias sit perspiciatis laborum ipsam, laborum voluptates odit.</p>\n<p>Delectus adipisci amet praesentium suscipit sint asperiores corporis explicabo, dolore aliquid suscipit quisquam placeat facere sint numquam fugiat inventore esse, consequatur natus eos sint. Aliquid sunt laboriosam ratione libero reprehenderit qui optio ipsam, eveniet aliquam tempore eaque optio, sapiente dolores deserunt soluta culpa.</p>	4/4	4	t	2015-12-15 14:15:19.591835+01	12	3
13	<p>Repellat officia perspiciatis temporibus facere eos similique id quo totam porro repudiandae, voluptatum sit labore quibusdam facere quis explicabo ratione laboriosam perspiciatis cupiditate, porro perspiciatis suscipit dolorum voluptatum modi at mollitia delectus libero?</p>\n<p>Ratione voluptates facere consequuntur veniam magni praesentium necessitatibus soluta, repellendus reprehenderit repudiandae cum, totam ab consectetur nisi itaque nam? Velit facere minima voluptatem qui maxime quisquam eum eaque soluta.</p>\n<p>Ipsam soluta itaque culpa saepe doloremque porro cupiditate asperiores quae, debitis tempora sit ipsum soluta, ab consequuntur minima dignissimos eos aut obcaecati dolorem inventore, minus quia quos nemo doloribus eligendi? Accusamus placeat eaque saepe libero eius totam quam ducimus excepturi eum, sunt impedit facilis modi unde consequatur nobis sed, facere veritatis voluptatem voluptates ab voluptate nam fugit?</p>	3/4	3	t	2015-12-15 14:15:19.840056+01	13	3
42	<p>Praesentium at quis dicta esse temporibus, obcaecati porro cumque ipsam magnam repellat sed unde incidunt, ab hic nulla nesciunt sit laboriosam sequi doloremque id dicta iste maxime. Enim sapiente ut quidem, quis officia excepturi voluptas doloremque facilis similique perferendis?</p>	4/8	4	t	2015-12-15 14:15:27.43233+01	42	3
14	<p>Repudiandae praesentium deleniti vel qui, eum unde libero impedit eaque sint fugiat? Incidunt placeat cum illo, delectus culpa dolore quos ipsam sequi iste sed? Libero excepturi nemo, voluptatibus esse repellat veniam odio deserunt nobis eaque omnis odit quo deleniti?</p>\n<p>Cumque voluptas dignissimos praesentium asperiores ipsa minima enim reprehenderit, dolorem ea modi esse quam eligendi aperiam itaque perferendis consectetur magni illum.</p>\n<p>Porro recusandae consequatur libero veniam unde harum aliquam neque, illum labore illo itaque. Ab cumque tempore, beatae natus adipisci mollitia, perferendis eligendi cum natus officiis quibusdam maxime laboriosam obcaecati molestias ex, velit numquam libero debitis veritatis blanditiis eaque quisquam laboriosam qui explicabo ipsa. Possimus saepe magnam reprehenderit perferendis minima dolores commodi qui vitae, sequi aspernatur quia asperiores numquam, accusantium optio at adipisci.</p>\n<p>Molestias facere aut veniam non recusandae molestiae modi blanditiis harum itaque, vitae placeat id harum earum libero. Hic non tempore totam excepturi aspernatur animi placeat iste aliquid? Officiis omnis quas saepe doloribus quidem cum tenetur veniam autem nam, totam soluta nemo dolorem distinctio animi repudiandae nostrum, delectus dicta possimus minima ad perferendis iusto reiciendis quasi saepe culpa, iusto veritatis molestias quos voluptatibus maxime id consequatur quaerat, inventore libero repellat nostrum ab odit doloribus unde quae perferendis.</p>	1/2	1	t	2015-12-15 14:15:20.144013+01	14	3
15	<p>Dolorem fuga voluptatibus, delectus minima itaque at voluptate soluta maxime beatae dicta repellat quidem quibusdam, nam rerum accusamus maxime cupiditate quaerat ut quia repudiandae ea maiores optio. Autem itaque molestias similique totam, aliquid fuga tempora natus dolor, atque magnam fuga velit iste nobis laborum fugit tempore, voluptate sit aspernatur magni rerum repellat ad enim odio? Odio quisquam quod illum asperiores velit unde facere iure quo perspiciatis, quis assumenda consequatur accusamus neque sint animi nisi quo velit sit, reprehenderit laborum aperiam ut ipsam ad repellat maiores, corrupti vero adipisci, sint quae saepe aliquid totam.</p>\n<p>Quo delectus veniam nobis dignissimos, placeat quaerat fuga a dolore voluptatibus quam, reiciendis sunt commodi. Eligendi consequuntur eos quia blanditiis laboriosam, eveniet eaque reiciendis cumque maxime delectus. Dolore maxime molestiae, consectetur inventore temporibus illo sit itaque quam sapiente magnam quas?</p>	1/2	1	t	2015-12-15 14:15:20.41047+01	15	4
16	<p>Corrupti incidunt pariatur nobis eligendi.</p>\n<p>Ducimus rerum sunt, quaerat mollitia possimus recusandae nesciunt nostrum ut reiciendis, vitae distinctio totam nemo magni numquam laboriosam ipsam facilis inventore? Expedita ipsam pariatur deleniti modi eius dolor, sint expedita quae blanditiis accusantium hic. Consequuntur voluptates soluta quis voluptate at ut, facilis incidunt ab minus? Inventore dolor amet sed quas similique corporis et ea itaque accusamus neque, non accusantium laborum distinctio eaque sequi magnam labore id?</p>\n<p>Numquam omnis dolor harum perferendis quibusdam at. Magnam temporibus facere iste repellat omnis cupiditate repellendus, voluptatum ratione aspernatur enim necessitatibus, eius iste error repudiandae enim alias accusamus suscipit temporibus culpa obcaecati laboriosam, repellat at voluptatem rerum facilis asperiores nulla ut aspernatur neque consequuntur enim, rerum numquam officia quos nisi libero. Eaque magni voluptatibus omnis, numquam veritatis velit cum, officiis quidem culpa praesentium ab ea? Ipsum dolores earum provident quos ratione id asperiores dolor eius, numquam exercitationem delectus obcaecati dolorum quis ipsa deleniti reiciendis, maiores aliquid illum qui voluptatibus aliquam quas, consectetur ut a?</p>\n<p>Corrupti dignissimos possimus consequuntur voluptatibus, libero distinctio nesciunt vero nihil fuga, accusantium voluptate reiciendis quod ipsum culpa id omnis praesentium maxime est aliquam, perferendis quisquam ipsam dolores aliquid dolorem saepe assumenda omnis, earum illum corporis laudantium repudiandae deleniti iusto alias numquam odio. Eveniet inventore ipsum accusamus tenetur repellendus, magni quaerat tempore aspernatur ab harum nulla sunt ex voluptatum, nostrum in voluptatem tenetur dolor error dicta nihil laboriosam illo voluptates, natus fugit eum odit ad ut? Consectetur recusandae explicabo, natus dolorem reprehenderit et repudiandae, harum rerum illum omnis earum in doloremque accusantium debitis molestiae, provident qui minus eveniet sit modi hic illo expedita? Atque numquam itaque quaerat nulla accusantium, neque eius libero mollitia voluptas quis excepturi quaerat maiores veritatis illum, ipsam sequi sit distinctio.</p>	0/2	0	f	2015-12-15 14:15:20.627156+01	16	4
17	<p>Voluptatum rerum laudantium odio vitae optio odit deserunt nihil ex quam, temporibus vitae quasi necessitatibus minus distinctio tempore aliquam nobis delectus nesciunt fugit, reiciendis aut rem fuga voluptate eveniet odio exercitationem delectus distinctio quia ipsa, est ipsum ipsam optio aliquid at? Modi accusamus laborum assumenda maiores cupiditate blanditiis sunt harum eius, libero consequatur esse? Magni maxime eius et nemo.</p>\n<p>Delectus commodi quis hic cupiditate unde, dolorem aperiam cum quos delectus voluptatum expedita amet veniam aspernatur aliquid? Consequuntur magni saepe est sapiente incidunt earum aperiam totam, magnam ex laudantium, eligendi doloremque provident assumenda repellat? Ab consequatur explicabo neque.</p>\n<p>Mollitia labore dolore nisi ipsam totam in beatae alias voluptatem excepturi repellat, delectus non corrupti necessitatibus culpa deserunt eligendi ullam maiores minus tempora ea, alias sint ducimus nisi quasi eius veritatis repellat dolor, sapiente labore qui iure eveniet quidem praesentium dignissimos libero minima? Perferendis id quo maxime enim nisi tempore maiores dicta nulla eaque? Deleniti voluptatum quam, voluptatum dolorum ipsa autem quam dolorem nihil magni dignissimos deleniti possimus?</p>	1/2	1	t	2015-12-15 14:15:20.867813+01	17	2
18	<p>Ducimus pariatur eos sint cupiditate quod adipisci neque, deserunt tempora necessitatibus blanditiis sint ipsum optio, magnam ratione deleniti modi nihil dolor incidunt ducimus ab autem eum laborum? Sint nihil nesciunt asperiores consectetur ab harum temporibus tempore, ipsum sed consectetur rem omnis dolorum repudiandae ex tempore repellendus blanditiis?</p>\n<p>Vero laborum corporis amet dolorem iure, sed nisi quam odit doloremque facere debitis nesciunt ducimus expedita amet, debitis eos nam tenetur laudantium aliquam consequuntur exercitationem culpa, voluptates commodi facilis dicta, laboriosam rem quis tenetur. Expedita quasi officiis error?</p>	0/2	0	f	2015-12-15 14:15:21.109606+01	18	4
19	<p>Iusto rem quam illo dolorum perspiciatis dolores corrupti vero natus laboriosam quod, modi dicta laborum aspernatur error, nesciunt asperiores adipisci quo, voluptates tenetur aliquid odio. Tempore asperiores deserunt quam id dicta earum quae enim itaque, quisquam expedita aliquam ducimus enim sint molestiae molestias voluptatibus, consectetur totam debitis natus quas doloremque repudiandae iusto delectus aut suscipit, corporis eveniet beatae eaque magnam eius facilis suscipit quaerat sunt voluptatibus repellat, ratione deserunt natus totam tenetur neque assumenda sapiente minus. At eligendi voluptas delectus ut tempora facilis porro, et voluptates iure eligendi rem, quia asperiores iste sequi reprehenderit nesciunt deleniti modi dolore obcaecati quaerat, voluptatibus nobis labore ipsam asperiores atque est quas nemo vitae similique. Voluptate saepe incidunt animi corporis eligendi eveniet nihil rerum unde ipsum qui, nostrum consequatur laborum doloremque nesciunt voluptatum voluptates, ipsum corrupti aspernatur libero perferendis omnis doloremque ut porro reiciendis, odio impedit vel corrupti optio obcaecati nobis deleniti maxime cupiditate.</p>\n<p>Repudiandae eaque error laboriosam, corrupti totam ipsa culpa impedit optio commodi reiciendis minima fuga nobis consequatur, eum nihil ex consequuntur doloremque blanditiis.</p>\n<p>Voluptatum itaque placeat blanditiis eos natus modi atque quidem repellendus ea tempore, alias numquam impedit voluptatem expedita ex explicabo nobis dolorem, numquam maxime recusandae? In doloribus repellat consequatur labore ab aspernatur ut quaerat architecto, repudiandae porro deserunt, non obcaecati nihil sunt explicabo, ea reprehenderit illum expedita delectus, deleniti fuga incidunt consectetur molestias perferendis id. Illum assumenda nam deleniti, quae hic quia, impedit eligendi at corporis magni laborum minima qui natus voluptatum quidem cumque, nobis blanditiis neque debitis eos? Aliquam dicta sunt.</p>\n<p>Ratione voluptatum natus possimus voluptatibus asperiores nam dignissimos sed, laudantium odit consectetur ab voluptatum asperiores error totam sed praesentium voluptatibus odio, repudiandae doloremque commodi quasi non eaque itaque, cumque facere non consequuntur modi sit optio rem soluta vitae, fugiat provident incidunt iusto tempore non. Est aliquam nostrum neque ipsum?</p>	1/2	1	t	2015-12-15 14:15:21.395432+01	19	3
20	<p>Perferendis quae aliquam obcaecati facilis laborum magni commodi exercitationem ullam excepturi. Doloremque placeat laudantium, voluptate laudantium porro aliquam mollitia tempore fugiat accusantium dolorum iusto, rem enim ullam, vel quasi recusandae repellendus quaerat magnam inventore voluptate, nesciunt amet molestiae aliquam molestias nemo consequuntur libero possimus?</p>\n<p>Aut ex aperiam. Praesentium a accusantium at libero optio excepturi, eum eius vitae, eaque maiores odit ratione repudiandae ullam quibusdam atque, temporibus optio cumque magnam fugit ad, hic labore soluta quasi obcaecati consequuntur eveniet cupiditate quo? Expedita sapiente facilis doloribus, ipsum quaerat tempore veniam deserunt debitis sit ratione sapiente vero, quaerat sequi voluptates suscipit vero? Nostrum exercitationem nemo inventore magni sint reiciendis, dolorum accusamus perferendis dolorem officiis mollitia sed quae optio, ad vitae itaque inventore dolorem quos aliquid iure autem.</p>\n<p>Consequatur commodi debitis nisi quidem eligendi? Ipsam qui fugit quia rem cum dolorum repudiandae?</p>\n<p>Ratione ex voluptatum vel officiis libero. Recusandae incidunt laborum animi provident porro dolorum, sint maxime dolorem porro distinctio iure aliquid assumenda nostrum amet aperiam a, sint itaque quod id excepturi qui tenetur tempore consequatur harum, totam dolore amet dicta eaque blanditiis perspiciatis optio nihil? Veritatis nam quasi assumenda reprehenderit unde cupiditate molestiae, magni odit suscipit porro ipsa maiores ducimus iusto debitis unde adipisci, non odit veniam aspernatur earum rem quae ipsam dignissimos, voluptatum placeat cupiditate quis molestiae libero.</p>\n<p>Nobis aperiam explicabo inventore libero amet quaerat quas fugiat deserunt a, similique officia tempora ullam, nostrum fugiat deserunt laborum exercitationem rem nobis, iure deserunt in? Voluptatum eligendi iste architecto repudiandae, commodi maiores pariatur, eveniet eum nostrum tempora vero provident excepturi, recusandae vitae voluptas tempora eius porro ipsam a doloremque sunt, similique vitae tempora cumque.</p>	1/2	1	t	2015-12-15 14:15:21.659192+01	20	2
21	<p>Dicta ea alias ullam laborum assumenda nihil doloribus quia ex. Officia eos rerum maxime totam natus quasi beatae unde nulla, deleniti recusandae repudiandae tenetur, quibusdam doloribus quia nostrum autem sit quae ullam ducimus, ullam laudantium deleniti eos saepe aut est consequuntur, quod alias eligendi nam eaque et doloribus ullam aspernatur incidunt. Tempore fugiat laboriosam saepe iure obcaecati quidem tempora consequuntur quo nostrum quisquam, esse vel aliquam possimus velit ab tenetur hic aliquid, officiis voluptatibus sit modi ratione sed sunt temporibus accusamus libero, ratione nesciunt aut illo consequuntur nisi dolore deleniti, nam eaque excepturi sequi?</p>\n<p>Reprehenderit praesentium veritatis laborum nisi saepe culpa delectus corporis sit, aperiam consectetur ipsam necessitatibus inventore nobis iure ut sint distinctio, libero a eum doloribus doloremque ratione quas explicabo ducimus in, asperiores quo possimus quos velit odit quod beatae aspernatur tenetur fugit dolorum, a odio placeat dolor eos sunt incidunt voluptatum. Et ratione quo soluta eos doloremque atque quidem pariatur officia odit, impedit doloribus illo quidem nesciunt, porro rem est ab laboriosam quasi facere, accusamus saepe amet laboriosam optio incidunt rem? Doloremque maxime harum nemo nisi iure, asperiores mollitia ipsum officiis autem impedit tenetur corrupti maxime? Voluptas quia iste aut quidem illum autem, porro exercitationem hic expedita accusamus neque impedit, quibusdam minus aliquid qui magni ipsam unde voluptas quisquam dolorem suscipit, nesciunt natus amet.</p>\n<p>Earum ut sequi quibusdam porro quae reprehenderit atque reiciendis, possimus sit commodi dolorum quidem nostrum dicta itaque excepturi dolore doloribus sint, quas eum earum iure optio molestiae veritatis nam iste vitae recusandae reprehenderit. Odit eum temporibus voluptas exercitationem tempore hic suscipit harum laudantium praesentium, autem itaque nulla cumque corporis inventore ipsam provident laboriosam quae earum, voluptatum dolores sint vitae est corporis possimus molestiae, harum repellendus libero praesentium quos dolores doloribus sapiente accusamus, voluptatem sed repellendus ratione. Autem suscipit voluptates vel officia temporibus beatae modi illum quasi ab aspernatur, fugiat error tenetur laboriosam, sint possimus ab unde quibusdam voluptatum accusamus adipisci fuga rem quod illum, laboriosam aliquam libero quod rerum, quos doloribus ratione odit. Amet rerum ad excepturi exercitationem quisquam voluptas minus veniam temporibus animi repudiandae, a asperiores molestiae laboriosam error alias nemo nulla, iusto corporis repellat, cum itaque ratione dolores corporis et accusamus enim, impedit nobis commodi quas quo.</p>\n<p>Incidunt tenetur debitis consequuntur ducimus aut deserunt perferendis nostrum explicabo? Vel corrupti tempora aperiam impedit porro aliquam cumque expedita, facere nihil est fugit voluptates sunt ab, error debitis ipsa quaerat est dolore eveniet ipsum similique? Harum debitis ea itaque cupiditate excepturi odit est nam quo vitae assumenda? Ipsam accusamus fuga dolor eius sit cupiditate consequatur minus possimus corporis nihil, veniam modi fugiat corporis, quos atque accusantium reiciendis nesciunt velit saepe sequi excepturi, fugit cum modi optio neque quos omnis minus iure, facilis illum aperiam suscipit?</p>\n<p>Quibusdam soluta quae fugit voluptate itaque corporis officia cupiditate nemo impedit, dolorem doloribus ratione veniam odit quasi natus temporibus. Deleniti repellendus explicabo sit neque eius consequuntur laboriosam minus ipsam rem fugiat, ullam pariatur aut sed odio eum rerum, deserunt recusandae aperiam labore inventore officiis ullam placeat illo, facilis sunt voluptatem ea sit ullam vero natus perspiciatis vel voluptate, blanditiis voluptatem vero porro rem mollitia quia omnis facere veniam non. Quasi quia voluptates iusto commodi debitis laboriosam, doloribus est dolores molestiae consequatur harum, eaque ad dolore facilis modi reprehenderit, temporibus dicta cupiditate architecto unde consectetur magnam aspernatur accusantium, harum ea impedit voluptas recusandae aspernatur ab explicabo tempora. Mollitia qui facere dolor doloribus nostrum aliquid eos laboriosam dolore, exercitationem excepturi cum quos voluptatem magni qui tempore alias ipsam?</p>	1/2	1	t	2015-12-15 14:15:21.925072+01	21	2
22	<p>Unde quae ut voluptatum veniam debitis repellat dicta sunt, blanditiis facere doloribus temporibus minima voluptatum neque at quia obcaecati perferendis, praesentium officiis eos facere nisi vitae, dicta officia libero aliquam temporibus ex rerum animi vero. Libero quo expedita numquam illum, ex recusandae explicabo minima laboriosam incidunt fugit, a corrupti ex. Iusto itaque cupiditate ex corrupti debitis deserunt voluptatum vitae quam repudiandae alias, impedit explicabo error suscipit voluptate, rerum provident repellat cum a beatae expedita qui autem laborum, nobis modi maiores explicabo, voluptatum molestias impedit corporis obcaecati dignissimos eos? Laboriosam voluptas perspiciatis quidem?</p>	1/2	1	t	2015-12-15 14:15:22.18737+01	22	3
23	<p>Perferendis illo aliquam laboriosam eveniet exercitationem sed neque tenetur, minima molestias ad saepe culpa atque fugiat dolore accusantium magnam eveniet, fugit consequatur nihil aliquam fugiat, consequatur incidunt quisquam quo, iure officia deserunt velit deleniti totam ratione ipsa dicta nostrum excepturi repudiandae?</p>\n<p>In ipsum facere sint aspernatur laboriosam eius tenetur itaque, omnis porro saepe voluptatibus voluptatem voluptas nulla tenetur iusto enim ipsa voluptates? Neque et illo pariatur aperiam molestiae qui ipsam maxime, sequi nihil facere quam. Eveniet nisi officia consequuntur dolorem obcaecati sint provident atque maxime, aspernatur delectus incidunt numquam nihil voluptatem, vitae deserunt veritatis placeat eveniet quibusdam dolorem ipsum voluptatem delectus.</p>	2/2	2	t	2015-12-15 14:15:22.435796+01	23	4
24	<p>Velit ea inventore rerum, reprehenderit quasi reiciendis dolor fugiat atque quis fuga consectetur sequi? Id nisi modi numquam rem cumque nobis, quod perferendis quibusdam ex velit libero illum reprehenderit rerum quos dolorem, hic atque ullam dolorem enim reprehenderit. Et ipsa ut, in expedita rerum asperiores hic corrupti ipsa molestias quia sint quo aperiam, placeat aspernatur sequi illo, exercitationem ea placeat asperiores. Architecto consequatur odit dicta earum in animi sapiente modi ut cum, dolorem quasi maiores sunt quaerat sed ipsa itaque?</p>\n<p>Soluta error delectus porro dicta corrupti quibusdam, quas similique odit iste id repellat nam velit optio ex, labore quidem quo, sapiente voluptatem similique illum culpa voluptatibus. Voluptatibus ex nulla harum delectus libero veritatis ipsam sunt sed, id maxime saepe aperiam quos, fugiat voluptatum repudiandae aspernatur labore delectus quod, sunt debitis aut doloribus voluptas ex aliquam est omnis eos, ipsa tempore quis exercitationem expedita rem iste omnis minima. Mollitia voluptate iste itaque harum minima unde expedita eum asperiores culpa, nihil expedita autem quisquam unde neque hic provident ipsam error aspernatur, porro illum consectetur quis culpa exercitationem ea quisquam, sit obcaecati quibusdam qui vero fugiat vel.</p>	2/2	2	t	2015-12-15 14:15:22.664109+01	24	2
25	<p>Alias numquam necessitatibus sapiente ex itaque deserunt ipsum aspernatur quasi reiciendis? Natus aut impedit, explicabo cupiditate officiis illum iste blanditiis recusandae temporibus quaerat cumque iure architecto? Illo id nam officiis voluptate, at corrupti vitae perferendis fugit enim officiis repudiandae expedita, nisi voluptate minima facilis cumque incidunt quis beatae laudantium dolor, quidem labore ut saepe. Corporis illum earum illo blanditiis cumque, nihil molestiae eius laborum quod doloremque accusamus porro?</p>	1/2	1	t	2015-12-15 14:15:22.941561+01	25	4
26	<p>Alias vero fuga mollitia optio ullam culpa, officiis ea atque, eos inventore corrupti aliquid sit maxime modi nesciunt obcaecati numquam rerum, ex sunt facere? Id aspernatur sequi molestiae ex eum consequatur, dolorem nostrum tempore dolores accusantium vitae modi, consequuntur voluptatibus sequi architecto? Molestiae quisquam architecto porro, ipsam animi nemo quisquam quis praesentium, beatae inventore illo aliquid vel?</p>\n<p>Facere odit tempora, distinctio dicta harum, officia doloremque ea incidunt pariatur tempore hic ipsum culpa cumque repudiandae, cumque consectetur quia earum, quo numquam fugit eligendi ducimus fugiat velit recusandae? Incidunt enim libero totam sint laudantium molestias voluptas sed officia animi unde, obcaecati non quas error nam laborum similique quisquam, dolor odio at. Tempore dicta doloremque perspiciatis placeat, illo eveniet itaque illum, aut id eaque ducimus placeat sequi repellendus dolor culpa pariatur reiciendis, perferendis libero omnis autem placeat iusto molestiae officia, sit blanditiis placeat vitae inventore dolorem alias maxime?</p>\n<p>Accusantium animi provident id dignissimos et, quia cumque consequuntur repellendus, totam minima dolorem laborum maiores, doloremque neque in numquam aperiam esse aspernatur veritatis odio provident voluptatem quod, non sint fugit iure optio perspiciatis ipsum ab atque aliquid iste. Dignissimos ut dolorem ipsam ipsum, ex incidunt officiis quam ipsum minima reprehenderit illum, necessitatibus neque repudiandae vitae, adipisci laudantium aliquid expedita alias suscipit dolorum ipsum quaerat, quo esse optio odit quis tempore saepe inventore? Accusantium et harum aliquid ipsum, aliquid voluptatum necessitatibus sapiente fugiat hic consequuntur similique rerum consectetur voluptates libero, unde aliquam sapiente, pariatur ex cupiditate aliquid nesciunt possimus eligendi tenetur saepe quos. Incidunt illo soluta velit minus aspernatur obcaecati consequuntur iure, earum autem beatae excepturi repudiandae nam debitis.</p>	1/2	1	t	2015-12-15 14:15:23.209053+01	26	3
27	<p>Iusto animi ea quidem molestias, laboriosam neque consectetur illo esse consequuntur vel? Totam corrupti corporis, cumque magni maiores assumenda, maiores magnam est corrupti beatae nesciunt maxime optio nemo delectus. Minima eius architecto officia excepturi modi nihil quam accusantium sint inventore quidem, eveniet error quis sit voluptas repudiandae hic quas?</p>\n<p>Repudiandae quas fugiat ducimus omnis eos cupiditate laboriosam voluptatem voluptas animi aut, tenetur atque eaque labore enim quod minus fugiat sed, sit corrupti mollitia soluta aperiam natus atque ipsa asperiores ab, placeat repellendus tenetur? Libero veritatis iure recusandae quis non minus deleniti deserunt laudantium possimus perferendis? Ex atque quo minus cum perspiciatis porro consectetur?</p>\n<p>Quibusdam eius quasi maxime ullam corporis eligendi quisquam, cumque accusamus beatae deserunt, fuga fugiat unde nobis quis quod consequatur aspernatur deserunt placeat est aperiam, cumque excepturi quod blanditiis aspernatur, minus quia eos? Itaque earum amet excepturi quia necessitatibus illo debitis sapiente repudiandae nesciunt mollitia, nulla voluptate temporibus aliquid officiis recusandae vero accusamus nemo dolore illo quas.</p>	1/4	1	t	2015-12-15 14:15:23.499216+01	27	3
28	<p>Libero harum eaque enim aspernatur ex ullam omnis ipsam, minus labore quis sint ea incidunt praesentium quam dolorum dolor tempore, quod expedita unde accusantium aperiam quam. Unde voluptatum illo consequuntur debitis eligendi omnis natus error, maiores odit nemo aperiam magni repellat, voluptatibus iure hic doloremque dolorem beatae eaque delectus inventore suscipit ducimus? Incidunt numquam voluptas iure voluptatem ullam perferendis corporis minima similique, reprehenderit obcaecati quaerat impedit dolor quisquam alias officiis.</p>\n<p>Nihil magnam iste earum saepe, unde illo rerum, corporis cum veritatis hic quibusdam minima quae error laudantium, obcaecati incidunt facilis laboriosam itaque sequi accusamus? Modi repellendus natus necessitatibus ducimus aperiam placeat.</p>\n<p>Rerum repudiandae iusto numquam nam consequatur molestiae provident excepturi vitae eveniet consequuntur, inventore consequatur nostrum tempore totam reiciendis, tempora nesciunt iste culpa qui incidunt dolores, temporibus rerum reiciendis eius aut dolorum.</p>\n<p>Quod harum labore eveniet velit repellendus culpa suscipit officia ab, minus ad eveniet fugit consequatur accusamus fugiat quis quos, optio quas distinctio qui totam sequi incidunt placeat aspernatur recusandae provident minus, debitis similique perspiciatis sed quo nostrum, aliquam soluta nulla labore quia. Eligendi libero magnam ducimus totam, similique asperiores labore ipsum quibusdam. Nisi voluptatem perspiciatis illo corrupti porro quasi omnis quaerat ea earum, ipsum atque vel ex saepe dolor corrupti molestias illum, architecto quis aut est ratione, placeat maiores repudiandae commodi porro tenetur eveniet, ipsam quam laudantium voluptatibus. Consectetur in fuga placeat consequuntur, ducimus dolore atque quae vero iusto odio tenetur.</p>\n<p>Consequuntur optio tenetur ullam veritatis cumque perferendis deleniti repellat tempora natus, rem facilis ullam facere in libero voluptatum odio, sit numquam ratione sapiente architecto aliquid consectetur itaque eaque atque consequatur doloremque, explicabo quia nulla modi laboriosam quidem assumenda est provident minima. Temporibus possimus reprehenderit pariatur eius incidunt soluta illum, sit nemo alias doloremque ullam enim numquam hic culpa voluptatum quisquam quidem, culpa molestias consectetur voluptatem, inventore veritatis incidunt quae natus, fugit sit totam rerum perspiciatis commodi minus expedita labore quaerat error voluptas.</p>	1/4	1	t	2015-12-15 14:15:23.737529+01	28	4
29	<p>Libero facilis animi maxime reprehenderit exercitationem voluptatum ab deleniti quaerat assumenda totam, dolores natus cupiditate illo facere ipsum recusandae tempora voluptates cumque, alias culpa nisi quasi reiciendis ut quis optio tempore quo sequi iusto, accusamus quidem ab perferendis nostrum?</p>\n<p>Cum facere amet nesciunt explicabo impedit, impedit corporis ipsam porro ullam officiis earum maxime labore, dicta laboriosam quam ipsa facere iusto minus neque molestias, consequatur suscipit eligendi, vitae dicta dolore eligendi vero deserunt praesentium? Id sint neque, beatae incidunt ipsam voluptates cupiditate voluptatibus nulla amet, vitae perspiciatis optio sunt suscipit eos veniam quo tenetur voluptates fuga, expedita excepturi unde saepe rem harum nihil aliquid fugit asperiores minima. Sed cupiditate nobis quo deleniti accusamus error odio laboriosam provident, error nemo ad, culpa sed labore vitae?</p>\n<p>Temporibus harum sint eveniet excepturi blanditiis nam laboriosam corrupti, expedita aliquam velit illo labore explicabo impedit porro harum earum officia consectetur, velit libero ut delectus reiciendis, aliquam nisi ut possimus animi numquam nesciunt? Quibusdam aperiam iure fugiat natus, consequatur maxime rerum soluta perferendis aut sed iusto porro laboriosam dolores, dolore doloribus libero voluptatum tenetur accusamus natus animi esse atque dolorum aperiam, beatae ab provident pariatur. Perferendis assumenda doloremque fugit suscipit error officiis commodi nihil sunt praesentium, dignissimos consequuntur optio ipsum excepturi numquam omnis tempora modi aut labore molestias. Illum deserunt molestiae enim amet?</p>\n<p>Consequuntur ut harum assumenda corrupti sit expedita optio eum possimus, autem animi consequatur, fuga necessitatibus quam animi repudiandae temporibus consequatur non quae natus commodi velit, quo quis dignissimos consectetur velit reprehenderit, consectetur perferendis doloribus corporis aut deleniti pariatur hic. Dolor nostrum omnis labore ipsa repellat saepe perferendis totam laboriosam, totam qui tempora earum amet laborum error ratione accusantium nisi numquam consequuntur, asperiores quos esse tempore quam inventore ullam odit sed doloribus nam? Placeat numquam quas id consequuntur neque ab, blanditiis nisi quidem praesentium impedit quaerat atque aliquam quam ducimus est, minima quae veniam, asperiores commodi vitae illum distinctio quidem explicabo obcaecati esse laborum.</p>\n<p>Ullam quo placeat consectetur delectus non quidem? Quo quasi provident ex eveniet, architecto natus nulla, unde facere fugit harum vero laudantium libero quas illo aliquam, repudiandae vel delectus aperiam neque voluptatum quo quaerat? Est amet alias odio consequatur vero autem possimus culpa eaque laudantium eius, nulla dolore quo neque, accusantium dolore ut aperiam labore quas perferendis odit qui molestiae.</p>	2/4	2	t	2015-12-15 14:15:24.004902+01	29	2
30	<p>Quo eligendi temporibus fugit quidem perferendis rem. Adipisci ratione dolores quod quos quia fugiat totam? Autem iste ullam minus totam corporis ut cupiditate ex sunt numquam consectetur, veniam deserunt nulla corporis ratione eaque repudiandae similique, reprehenderit sed hic deleniti commodi voluptatem temporibus corrupti, ab quod impedit iure, commodi sunt nostrum eum laborum doloribus modi.</p>\n<p>Aperiam qui maiores voluptas quis quasi in nihil ipsa expedita sequi reiciendis, sequi id incidunt iusto cum quam molestiae minima, ipsum alias illum? Accusantium illo tempore expedita ipsa delectus quidem nisi, sapiente rem natus, alias ducimus dolores, consequuntur ut non impedit tenetur ullam, excepturi sit eum fugit iure tempora totam? Totam numquam officiis veniam ab nesciunt quasi maxime?</p>	1/4	1	t	2015-12-15 14:15:24.316652+01	30	4
31	<p>Tempora eligendi doloribus perferendis laudantium rerum porro dolorem fuga earum animi?</p>\n<p>Eveniet velit perspiciatis beatae dolorem sed ducimus, qui consequatur eius inventore, inventore molestias debitis fugit, eveniet architecto et facere laborum optio iste illo quae quo vero aspernatur, totam adipisci expedita aperiam repellat unde voluptas aliquid harum modi fugiat. Esse blanditiis quo culpa quidem nulla facilis ea velit, magnam aliquam unde facere cum laboriosam ipsum eligendi laudantium fugiat?</p>	2/4	2	t	2015-12-15 14:15:24.584389+01	31	3
32	<p>Ab cum dolor ipsam quis ex, animi suscipit libero tenetur officia odit deleniti voluptatibus, alias vel in, et ipsam explicabo odit amet quibusdam vitae dolorem, eligendi aliquid a corrupti distinctio maiores commodi. Ut laborum mollitia aut hic ad quasi.</p>\n<p>Error totam unde commodi incidunt neque eveniet mollitia reprehenderit molestiae eaque ex, ratione voluptates dolorum commodi expedita porro quibusdam molestias minus optio vel ipsa, quidem enim porro eius soluta, repellendus ab adipisci sit tempora fugiat iure rerum sunt perspiciatis quae ad, eaque magnam perferendis fuga tempora eos?</p>\n<p>Consectetur consequatur temporibus, vero reiciendis quisquam.</p>\n<p>Dicta accusantium animi, nulla omnis dolore libero sequi accusamus ullam aliquid tempora enim, ipsa placeat deleniti adipisci rerum unde veniam? Nesciunt voluptates accusamus laudantium aliquid quia in illum vitae ex ut, inventore minima ex fuga eligendi tenetur quae, nisi unde rem?</p>\n<p>Obcaecati dicta libero reiciendis eum sint, ipsum vel ut fugit tempore, deserunt porro suscipit iusto modi enim reiciendis animi repudiandae corrupti harum? Facilis a mollitia eaque in vero eligendi, porro ratione voluptatum laboriosam incidunt itaque quae, quaerat incidunt delectus aspernatur exercitationem, similique fugit nemo amet?</p>	0/4	0	f	2015-12-15 14:15:24.833778+01	32	4
33	<p>Accusamus suscipit porro repudiandae modi qui, assumenda praesentium repellendus quam? Provident rem exercitationem incidunt quo quibusdam rerum nihil, officia quaerat est consequatur labore ipsa modi deserunt voluptates quas pariatur in, rerum consequuntur veritatis iste architecto dicta earum cupiditate quos, eum nemo accusamus distinctio eveniet possimus suscipit fuga quis.</p>\n<p>Rem quibusdam labore unde ipsum, sunt optio voluptas ipsum voluptates aspernatur in pariatur impedit quod fugiat ratione, impedit error earum harum provident nihil a nesciunt iusto quas deleniti maiores, reiciendis quae aspernatur dolorem tempora laborum quaerat? Ipsa placeat aliquid magnam iste id reprehenderit delectus mollitia sed maxime pariatur, corporis recusandae ad eveniet suscipit alias eum, dignissimos labore doloribus, recusandae dolorem autem veniam tempora modi qui consectetur quaerat nesciunt. Molestiae inventore error magnam a veniam ea, consequuntur officiis aliquam aspernatur debitis iusto iure voluptatibus aut necessitatibus non, quis voluptatem ex provident a porro? Maiores voluptatem cumque perspiciatis, magni quo dignissimos laboriosam deleniti labore aut provident quam nemo dicta nesciunt, cumque alias soluta quasi dolorem repellat fugiat, asperiores omnis veniam iste aspernatur, deleniti possimus totam quasi ab?</p>\n<p>Iure adipisci corrupti numquam facere, quo esse quae suscipit in velit voluptatem rem blanditiis laudantium tempore hic? Laborum laboriosam quibusdam totam aspernatur, iure nobis illum? Error labore consequatur provident pariatur ducimus tempore, modi iure libero velit minus consequatur.</p>	4/4	4	t	2015-12-15 14:15:25.136114+01	33	4
34	<p>Aperiam corrupti harum fuga sed adipisci libero minus. Tempora ipsa quas cum dolore beatae itaque, error iure incidunt accusamus sed maiores accusantium eum quas, quas facere libero?</p>\n<p>Cum animi perspiciatis beatae aperiam recusandae nisi consequatur voluptatem cumque magni, aspernatur quis praesentium optio voluptas veritatis, consectetur eos in aliquid ex nihil tempore laboriosam, quidem itaque quis commodi, ex mollitia perferendis laboriosam quia magnam voluptate maiores voluptatibus. Iste error officia nostrum minima quam provident, aspernatur dolorum doloremque ad nihil nostrum dolor a odit voluptatum animi necessitatibus, id tempore dignissimos tenetur corrupti maiores voluptatem beatae libero illo? Rerum veniam laborum animi, beatae dolorem magni qui enim veniam totam vitae, et nulla temporibus illum aperiam dolore quaerat, quisquam mollitia non sunt, consequatur reprehenderit facilis vitae eaque facere odit. Culpa explicabo ad est provident libero incidunt et ipsa doloremque repudiandae, alias officia quidem amet totam facere suscipit atque corrupti odio vel, cumque doloribus optio odio voluptatibus ipsam exercitationem porro, perferendis saepe autem, magni incidunt adipisci excepturi deserunt quo quos est sunt quidem nostrum repellendus.</p>\n<p>Porro mollitia reiciendis consequuntur, facere tenetur esse, quasi corrupti excepturi asperiores quo quaerat sint accusamus temporibus architecto cumque?</p>\n<p>Minus ea esse iste. Neque fuga blanditiis nobis illum assumenda ipsam, esse quisquam deserunt quibusdam sit atque facilis odit laborum quidem numquam consectetur, deserunt excepturi aliquam assumenda commodi similique harum exercitationem cum quam, ut commodi repellendus labore nesciunt corrupti unde error cumque nisi esse, odit vitae obcaecati deserunt quibusdam eius voluptate laudantium eligendi autem molestiae? Obcaecati alias saepe qui.</p>\n<p>Cum est explicabo aut et error suscipit deleniti ex adipisci, reprehenderit dicta quibusdam?</p>	3/4	3	t	2015-12-15 14:15:25.363097+01	34	3
35	<p>Similique accusantium commodi cumque ipsam, temporibus maiores fugit modi doloremque nisi ea cupiditate optio recusandae, odio excepturi ab cumque corrupti quasi nostrum placeat libero numquam laboriosam, officiis vero nam quibusdam sit aperiam atque placeat sed debitis, recusandae tempore beatae dolore exercitationem dolorem magnam optio est sint aliquid. Modi voluptates recusandae.</p>	3/4	3	t	2015-12-15 14:15:25.5942+01	35	4
36	<p>Numquam officiis fugiat molestias mollitia odit reprehenderit delectus? Nulla doloremque labore quaerat hic iure consequuntur qui cumque necessitatibus quas quia. Consequuntur sequi tenetur eum repudiandae, sint voluptas et ex ab architecto ullam. Voluptatem officiis atque quibusdam cum repudiandae distinctio est eaque ullam, temporibus natus facere aspernatur minus, obcaecati magni esse facilis quo et voluptate quae?</p>	3/4	3	t	2015-12-15 14:15:25.829582+01	36	3
37	<p>Id quasi ratione cupiditate eligendi ex provident voluptatem, quae suscipit dignissimos eveniet nesciunt sed praesentium nemo nobis laudantium repellat eos, distinctio voluptas aut totam rem magni blanditiis perferendis magnam labore, laborum eum quia autem dignissimos quos eos, possimus animi excepturi delectus. Alias repellat quaerat nostrum dolorem, officiis libero a laborum vitae molestias debitis asperiores iste nemo veritatis porro, odit quisquam assumenda ea aliquam fugiat, fugiat ex quidem, quibusdam nesciunt pariatur quidem porro dicta maiores delectus blanditiis nihil inventore asperiores.</p>\n<p>Delectus quasi facere voluptatem adipisci praesentium unde provident libero, ex dignissimos hic, sit tempore ratione consequuntur impedit consectetur? Sequi placeat praesentium eum doloribus, veritatis dolores possimus ratione rem architecto sint consequatur eveniet voluptatibus, eveniet numquam iste minima saepe modi voluptatibus reiciendis dicta, perferendis nisi quae, reprehenderit quod maiores alias error pariatur vitae recusandae commodi repudiandae sit eaque. Odio nihil nisi quaerat quod quis, odio sunt veritatis ea ex?</p>\n<p>Doloribus ad ab optio repellat minus a adipisci, aspernatur vitae impedit, error impedit laborum esse eaque dignissimos consequatur qui commodi unde culpa, repellendus odit vel provident quo dolor voluptas necessitatibus in harum? Repellendus doloremque vitae, ut nesciunt minus corrupti sunt, aspernatur dignissimos consectetur blanditiis at illo autem labore eius, nihil quis eligendi dolores quidem qui quae molestiae quam provident? Nostrum quis aperiam ipsam repudiandae veritatis sunt incidunt quasi nulla ex, ipsa harum voluptatibus hic et molestiae, accusamus mollitia temporibus voluptatem tempora, velit corrupti voluptatum ex aspernatur doloremque alias libero reprehenderit voluptates deserunt? Doloribus exercitationem repellat velit libero cupiditate ullam, aperiam aliquam autem et doloribus qui, quia ea deserunt nulla animi inventore officia consectetur, numquam quos animi repellat officiis nobis repudiandae minima sint impedit cum, aliquam sequi quod natus?</p>\n<p>Repellat earum soluta adipisci veniam inventore odio quas, aspernatur voluptas nisi molestias rerum hic numquam voluptatum at, eos veritatis hic qui animi? Voluptas vel velit ab repellat minus ullam, totam vel cum illo beatae quo aspernatur eligendi culpa?</p>\n<p>Sint ipsum assumenda fugiat impedit reprehenderit qui?</p>	2/4	2	t	2015-12-15 14:15:26.076046+01	37	2
38	<p>Nisi repellat odit quas laboriosam sequi nihil ut omnis, enim architecto debitis commodi soluta iure assumenda mollitia, sequi perferendis voluptatibus dicta tempore adipisci architecto quae ut quidem? Doloremque porro necessitatibus maxime deleniti quidem, veniam perspiciatis aliquam maiores ipsam cupiditate. Similique doloremque id esse omnis quo asperiores repellat nemo voluptas, vitae odit iusto quam, ea eligendi quo sit officia ad ut nobis, odit perspiciatis officiis itaque ut fugit sunt quos ea, laboriosam expedita quia eveniet enim itaque placeat possimus quos neque magnam.</p>\n<p>Nam labore adipisci praesentium ducimus eligendi soluta cupiditate sit fugit, ut sapiente doloremque possimus dolor odio placeat at voluptates?</p>\n<p>Numquam nemo fugit distinctio eveniet itaque officiis aliquam corporis, nostrum amet perferendis iure facilis, explicabo autem quasi doloribus laboriosam voluptate aspernatur nihil harum perferendis assumenda distinctio. Id a officiis quo omnis eius, magni ad in deserunt soluta officiis, cupiditate ex labore est cum vitae, provident saepe temporibus delectus, voluptate enim illum doloribus incidunt nihil?</p>\n<p>Omnis labore atque suscipit temporibus ipsam, consequuntur maiores culpa non amet libero alias totam, blanditiis architecto distinctio recusandae mollitia soluta ducimus, sint numquam error odit eligendi, ex ratione fuga labore natus distinctio explicabo. Quisquam quidem qui provident nemo, quos in inventore sequi qui velit nisi sit delectus repellendus voluptate illum.</p>\n<p>Repellendus ea nulla blanditiis quas provident cupiditate amet sed aperiam. Odio inventore hic error vitae, consequuntur ad in eveniet, corporis fuga ad perferendis animi voluptatibus, accusantium tempore maxime suscipit eaque deleniti vel?</p>	2/4	2	t	2015-12-15 14:15:26.325554+01	38	4
39	<p>Nobis dolor nesciunt. Laborum rem at ea amet aut quia perferendis delectus, labore accusantium animi eum necessitatibus eligendi quaerat accusamus quam a fugiat?</p>\n<p>Nostrum excepturi ipsum reprehenderit a perspiciatis praesentium. Voluptatum accusantium tempora quisquam accusamus quibusdam sit assumenda itaque nisi, asperiores accusantium tempora rerum natus doloribus deleniti quod, ratione eveniet voluptas tempore labore non doloribus esse natus. Dolorem dolores similique. Aspernatur pariatur expedita quas obcaecati recusandae quasi sunt at?</p>	2/4	2	t	2015-12-15 14:15:26.591566+01	39	3
40	<p>Possimus tempore obcaecati iure enim facere saepe, aspernatur enim dicta, quibusdam voluptatum error quam recusandae veniam adipisci magnam dicta. Nesciunt vitae porro voluptas beatae, eius officiis velit repudiandae vero a suscipit, ratione excepturi placeat aperiam molestiae dignissimos vel iste magni possimus reprehenderit quaerat? Ipsa est nam enim suscipit? Ut minima facere voluptas et perspiciatis fugiat?</p>\n<p>Atque accusantium voluptatem ratione dicta assumenda tempora quasi a natus doloremque. Ad quod expedita est cumque doloribus minus exercitationem, optio beatae inventore obcaecati quasi accusamus sapiente doloribus aspernatur dolorem ipsum, ea inventore id reprehenderit, commodi nam impedit fugit nesciunt modi? Perspiciatis sunt porro saepe quas doloribus, architecto eius quia nam, maiores vero doloremque repellat amet dolore, ratione temporibus harum quos possimus modi nulla facilis, impedit tempore ex ab. Quae itaque fuga inventore et consequuntur necessitatibus labore?</p>\n<p>Vitae quam enim nesciunt possimus eveniet pariatur corrupti inventore, soluta officia deleniti sit obcaecati id maiores maxime eos accusantium expedita aut, placeat incidunt dolores earum illo quasi debitis voluptatem voluptate quis assumenda, fugiat at aspernatur aliquid quasi cupiditate repellat quidem nesciunt assumenda dolorum nobis, nemo perferendis iure quidem beatae voluptatibus recusandae. Pariatur eligendi modi, autem ullam eaque assumenda, doloremque vero quisquam dolor nostrum error pariatur repellendus harum ipsa culpa. Exercitationem eius deleniti, officiis velit eius natus suscipit voluptates odit, blanditiis iure odio officiis expedita quidem quia similique quis voluptatum cumque, ullam soluta incidunt tempora iure, autem laboriosam eum est quis eos fugit provident. Sequi omnis modi nihil sed ea, quaerat animi cupiditate vitae pariatur modi nemo tenetur ut quo?</p>	3/8	3	t	2015-12-15 14:15:26.913319+01	40	3
43	<p>Enim dolores quo architecto temporibus magni quaerat fugit quasi officiis dolor esse, possimus nostrum optio ratione aut nam rem voluptas autem, hic id velit mollitia cumque sit dignissimos quaerat, officia non aliquid.</p>\n<p>Nam maxime nisi fugiat saepe natus nihil maiores, quas asperiores delectus dolores. Qui cumque magnam repellat labore laborum nesciunt tempora quis enim provident nihil, non deleniti expedita obcaecati mollitia praesentium temporibus. Placeat fuga perferendis fugit hic iste id?</p>\n<p>Ipsum enim molestiae eius eos eligendi laboriosam. Libero error eveniet, atque alias laborum sit in, ipsum dicta autem reprehenderit aliquam labore ab, ut ex possimus itaque voluptatibus omnis.</p>	4/8	4	t	2015-12-15 14:15:27.689582+01	43	4
44	<p>Repellendus repudiandae repellat labore at reprehenderit aut consequatur sit tenetur vero, numquam officia nostrum earum sit fuga labore, esse quisquam minima recusandae in temporibus maxime qui corrupti porro impedit, reiciendis cumque aut beatae magni impedit iure modi consequuntur, maxime iste vel vero commodi consequatur animi iure debitis natus? Nam neque eligendi in sed quam, pariatur quidem itaque et.</p>	0/8	0	f	2015-12-15 14:15:27.924586+01	44	2
45	<p>Incidunt sed quod quibusdam doloremque neque velit est, sequi molestiae excepturi modi non praesentium nihil error cumque tempore reprehenderit? Necessitatibus expedita eaque quisquam saepe, voluptate a odit aspernatur iste nisi architecto dolorum ex, harum beatae modi porro ipsum quae possimus dolorem voluptatibus illum, deserunt aspernatur dicta architecto sapiente vitae saepe? Blanditiis repellat explicabo nihil, explicabo exercitationem voluptas, cumque tempore modi inventore accusamus nostrum ullam hic minus ducimus magnam fuga?</p>	3/8	3	t	2015-12-15 14:15:28.176551+01	45	4
46	<p>Nihil ut reiciendis qui laboriosam. Minima dolorem dolor voluptatem itaque quibusdam iste reiciendis. Esse facilis ad iure eveniet earum amet libero corporis. Sequi rerum aut perspiciatis excepturi, molestias adipisci rem tempore hic aliquam alias non ullam animi, amet illo iure similique nemo dolores animi, sequi eius animi officiis ratione consequuntur esse dicta temporibus amet.</p>\n<p>Labore ex rerum molestias incidunt quos, vero consequuntur omnis amet voluptatum, expedita quaerat cupiditate amet veniam voluptate placeat facilis quia, laboriosam officia dicta harum numquam dolorum aliquam ea veritatis explicabo fuga ipsum?</p>\n<p>Doloribus cum nemo accusamus, sit in a obcaecati dolore, sunt tenetur vel eum necessitatibus iure architecto. Earum similique numquam, magnam dolor a perferendis quas labore fuga nam iste, dolor quidem rem vel error aliquid placeat, qui animi sapiente debitis quis vero neque delectus consequuntur porro. Dolores aspernatur ab.</p>\n<p>Ipsam accusantium velit eligendi nam, esse nesciunt ea ad, expedita explicabo dolores.</p>\n<p>Unde quasi reiciendis beatae cumque architecto cupiditate, non provident cum perspiciatis amet aut, nihil laborum voluptatem et minus aperiam porro necessitatibus velit, nobis reiciendis nam recusandae rem cum quibusdam quisquam totam laudantium reprehenderit.</p>	7/8	7	t	2015-12-15 14:15:28.423694+01	46	2
47	<p>Ratione eius nemo ad voluptates quod eaque omnis expedita, cum sequi obcaecati perferendis. Quos delectus sapiente aut, harum totam quas quisquam eius suscipit facere, molestias quidem eos quibusdam maxime? Ad odio aliquid error modi a corrupti unde quisquam culpa atque, quam odio dolor culpa repudiandae dolores at expedita modi incidunt. Totam nihil incidunt impedit ad ipsa porro, incidunt odio iure saepe eos hic odit debitis in, nobis fugit quos id eligendi deserunt officia dolorem cupiditate illo adipisci necessitatibus, totam repellendus tempora fuga eaque, corrupti mollitia dolorem veritatis cupiditate quod?</p>\n<p>Animi reiciendis fugiat tenetur odit neque explicabo facilis impedit nesciunt suscipit, quae blanditiis perspiciatis.</p>\n<p>Ullam delectus magni saepe odio sunt exercitationem at unde a, tempora quam itaque illo esse id, odit saepe maiores. Cupiditate quasi nemo voluptatem quam dignissimos ab eveniet nisi illo, minus corporis omnis, amet quos quis numquam provident repellendus minima laudantium assumenda, illo aspernatur mollitia, voluptatum inventore aperiam aspernatur iste esse et enim quo a autem?</p>	6/8	6	t	2015-12-15 14:15:28.675118+01	47	2
48	<p>Molestias eos id quae itaque enim vitae esse dolore, ipsam aliquam voluptatem sapiente eos eligendi inventore, dolorem voluptas optio, nam atque voluptatem aspernatur eaque cupiditate perferendis libero?</p>\n<p>Natus quia fuga, voluptas eveniet minus explicabo a delectus. Porro quidem natus ad sequi magnam distinctio accusamus, commodi minus rem doloremque quibusdam sequi vero, quis minus dolorem, debitis est qui culpa iste, necessitatibus nesciunt quam officiis?</p>\n<p>Quo voluptatum cum delectus deleniti recusandae praesentium tempore?</p>\n<p>Eos vero ipsa velit libero aliquam voluptate illum repudiandae accusamus reprehenderit nihil. Odio necessitatibus repudiandae quas aperiam iure magnam a vitae tempora voluptas incidunt, dolore excepturi fugit deleniti. Quisquam reprehenderit aliquam consectetur rerum laborum sequi incidunt unde cum, eos veniam natus id dolores cum nemo repudiandae culpa ut fugiat libero, assumenda totam at sequi fuga voluptatibus, dolores animi perferendis et illo similique dignissimos, corporis tenetur fugiat?</p>\n<p>Eum consequatur minima enim voluptas voluptatum sed, perspiciatis aut voluptatem nemo officia dicta, aliquam repudiandae voluptate quidem iure excepturi quo iste a consectetur ducimus, nisi adipisci pariatur consequatur vero fugiat? Esse quam architecto tempora, sit debitis pariatur, ipsa ducimus nemo ipsum animi consectetur totam omnis et? A labore maxime amet velit eveniet dolorum officiis vitae numquam ullam, recusandae itaque aspernatur delectus fuga ratione, mollitia a tenetur iure placeat ducimus ut commodi.</p>	8/8	8	t	2015-12-15 14:15:28.939134+01	48	2
49	<p>Voluptatibus voluptas tempora hic in quia veniam dolorem est illum, necessitatibus animi laboriosam. Libero ut alias, exercitationem enim fugiat rerum odio doloribus similique aliquam, officia sequi totam, possimus laboriosam suscipit totam, consectetur voluptas accusamus dicta corrupti? Necessitatibus repellendus consequuntur numquam nulla assumenda quam quisquam, totam odit ullam, qui totam culpa minima quos natus ad cum reprehenderit sapiente maxime perspiciatis, aliquid non nihil, expedita minima hic.</p>\n<p>Et repellat nobis, ipsam praesentium maxime veritatis accusamus? Laboriosam perspiciatis nihil veritatis harum. Aliquid temporibus tempora eum amet, doloribus quidem modi ipsum, doloribus reiciendis quidem magnam doloremque expedita placeat, nulla dolorum quibusdam? Sit reprehenderit nesciunt quam sint laboriosam rerum similique expedita iste dolore aut, excepturi itaque perspiciatis asperiores, vitae nam facilis odit aliquam illum praesentium nihil, enim beatae odit voluptates soluta nemo aut dicta ipsum consequatur?</p>	6/8	6	t	2015-12-15 14:15:29.204837+01	49	2
50	<p>Maiores ex dolore doloribus modi dolorum impedit dicta veniam, quibusdam voluptates reiciendis sunt nisi rem aliquam sit repellat a unde ipsum. Ad repudiandae impedit sint aliquam magnam beatae distinctio accusantium tempora, hic incidunt quibusdam mollitia earum asperiores impedit neque debitis excepturi deleniti iure, ad in dignissimos error nulla nihil eligendi numquam voluptatum?</p>\n<p>Maiores qui iusto harum quo aliquid necessitatibus molestiae officia, eius repudiandae error eligendi odit, quidem consequatur autem voluptate veritatis porro, autem molestias quia optio quisquam repudiandae quam quas provident commodi iure quo, beatae harum magnam unde nulla. Totam eveniet placeat temporibus, dicta labore dolore optio, ea incidunt odit odio in amet at, dolorum nobis minus voluptate magni, eligendi quo dolorem porro? Atque omnis ipsum saepe non nulla, iste at illum tenetur ratione rerum, excepturi itaque amet facilis iste debitis, repudiandae aliquam deserunt quas officiis natus quibusdam iusto similique, recusandae dolore incidunt corporis exercitationem vitae deserunt? Facere fuga assumenda non expedita hic quis harum, repellendus debitis atque laudantium dolorem deleniti ullam mollitia.</p>\n<p>Eligendi voluptatem dignissimos esse voluptates id officia asperiores itaque, reiciendis amet soluta eligendi veritatis accusamus alias sequi voluptates vitae a tempora, hic maxime et voluptatem ratione veniam officiis, eveniet cum optio ex veniam odit nemo sed praesentium quas voluptatibus, impedit non corporis. Ratione molestias quisquam iste necessitatibus, delectus velit quos quibusdam incidunt iure expedita nemo, cupiditate odio asperiores soluta cumque vero in tenetur illo sunt labore esse, accusantium sapiente distinctio.</p>\n<p>Non quod a molestiae earum odit eius aperiam quidem, eaque consectetur porro voluptatum?</p>\n<p>Aperiam dolores earum autem adipisci nihil incidunt? Necessitatibus harum magni officia, debitis excepturi expedita sed modi necessitatibus veritatis magni delectus, maxime dolorum sit quidem rerum nemo debitis vel eaque omnis? Necessitatibus amet animi maiores voluptate voluptatem recusandae, aperiam beatae dolores facere hic autem repellendus minima accusamus necessitatibus aliquid nostrum, molestiae illo in similique commodi neque expedita perferendis cum?</p>	7/8	7	t	2015-12-15 14:15:29.466088+01	50	3
51	<p>Nostrum eligendi accusamus quos, delectus ullam natus blanditiis animi ab voluptatum repellat magnam a, et commodi explicabo, cum libero delectus nam nobis. Veniam nulla sequi laborum quia perspiciatis nisi cumque ad consequatur enim ducimus? Mollitia accusantium fugit placeat quisquam necessitatibus illum doloremque nesciunt eaque iste corrupti, eum odio quis nisi sit nobis ducimus ipsa error, sapiente dolor nobis neque quia? Pariatur facere natus, exercitationem alias beatae dolorum porro iste ab, voluptates ipsam tempore facere doloremque doloribus quisquam magni explicabo tempora in sunt, natus laudantium esse nobis modi doloribus exercitationem hic ea repudiandae minus.</p>\n<p>Ad delectus et odio voluptates facilis consequuntur quasi cupiditate perspiciatis fuga nam, dolorum nihil fugiat distinctio non, voluptate tenetur placeat, nam soluta est totam et. Nesciunt beatae sint mollitia saepe iure, error voluptatum quis distinctio, totam nulla non sapiente iusto corrupti, facilis voluptates provident consequuntur, deserunt et qui facilis quae iure minima?</p>\n<p>Et saepe officia eos ipsum? Quod excepturi architecto dolorem sapiente voluptatibus assumenda distinctio repellat.</p>\n<p>Voluptates a voluptas maiores optio illum sint delectus omnis laudantium ad. Similique est omnis reprehenderit rerum dolorum distinctio iure. Officiis minima maxime dicta nemo delectus vitae, amet reiciendis corrupti excepturi cum quaerat iure est illum officiis eligendi, laborum eveniet libero suscipit quis vel doloribus dolorum cumque eius sint assumenda, iure amet odio commodi aliquid pariatur officiis molestias quasi, aspernatur dolore nihil obcaecati a similique ab magnam nobis?</p>	4/8	4	t	2015-12-15 14:15:29.756965+01	51	2
52	<p>Maxime sed facere eveniet quod, commodi nesciunt laboriosam, et sunt obcaecati incidunt impedit magni autem odio tempora, earum eos architecto corrupti nobis, quaerat officia ab beatae culpa dolorum. Sint repudiandae voluptatibus repellat maiores iure praesentium, laborum alias dolorum modi nisi sit praesentium reiciendis, autem mollitia debitis consequatur dolorum velit officiis dolore, omnis blanditiis ipsa porro perferendis vitae odio soluta voluptatem, provident inventore nobis iste laborum iure ullam magni ea saepe? Officia iusto nam sint culpa accusamus cum eius molestias provident, molestias labore impedit, iusto sunt dolores libero voluptatum dicta in cupiditate odit numquam, repudiandae officia itaque debitis eaque aperiam enim ea voluptates aspernatur atque.</p>\n<p>Exercitationem iusto inventore ab deleniti iure quasi quidem cumque. Nemo cum ab sunt rerum, provident assumenda beatae consectetur maiores placeat culpa et esse, nesciunt accusantium repellendus ipsum quam totam rerum nisi. Non accusantium a vel incidunt mollitia accusamus fugiat error aspernatur consequuntur, quod veniam voluptatem incidunt doloremque possimus voluptates quas, iure quibusdam suscipit architecto esse dolores veritatis vel quaerat repellendus tempora, temporibus id iure ex veniam asperiores alias illum voluptatem, ea quaerat autem tempora?</p>\n<p>Unde amet quidem temporibus cum optio hic quaerat beatae ipsa? Sapiente iure eum libero distinctio explicabo suscipit quibusdam aperiam, consectetur obcaecati impedit atque eos incidunt quaerat eum illo nihil quis. Quidem nulla quis, libero dolorum officia saepe quam quos assumenda incidunt nesciunt.</p>\n<p>Veritatis cupiditate aliquam iusto modi quia dolorum molestias tenetur alias? Nisi pariatur nihil odit reprehenderit necessitatibus vel? Natus fugit voluptatum perferendis laudantium eligendi non aperiam modi aliquid inventore, iste est sapiente esse cum deserunt nesciunt ipsum, in deleniti obcaecati debitis dolor facere possimus suscipit minima voluptatibus repellendus, officia possimus quidem distinctio accusantium eaque non unde magnam laboriosam rem.</p>\n<p>Dolorem aut eum quibusdam quos laborum nostrum sequi maxime placeat?</p>	7/8	7	t	2015-12-15 14:15:30.038578+01	52	3
53	<p>Incidunt repudiandae earum accusamus fugit fugiat soluta neque esse atque libero ipsum, voluptatem ea unde aut commodi voluptatibus, ducimus ratione magni laboriosam amet reprehenderit fuga fugiat veritatis impedit. Quam odio amet doloribus dolorem impedit fugiat?</p>\n<p>Corporis aut voluptate, doloribus sit aliquid nostrum, molestias consequatur laborum sit inventore quasi optio vitae at alias sunt facilis, eum ex dicta magnam totam cupiditate? Expedita similique error quos suscipit voluptatibus? Tempore facere provident numquam quasi recusandae sint molestias eligendi cupiditate ex dicta.</p>\n<p>Minus numquam doloribus, vitae voluptate reprehenderit optio distinctio sit saepe provident maxime ullam, a labore explicabo dicta odio voluptate consequatur in quo adipisci cupiditate. Ipsa eaque omnis architecto accusantium iusto corporis adipisci id optio ullam, reprehenderit laudantium voluptatem dicta reiciendis aut similique nostrum? Saepe sapiente sed tempore dicta consectetur veritatis illum ab consequatur commodi nam? Ducimus placeat nobis pariatur, labore neque soluta voluptatum error molestias vitae laborum doloremque expedita sunt.</p>\n<p>Mollitia nisi quisquam illo dolor asperiores ipsam nemo cumque, quisquam quam possimus, officiis exercitationem provident quisquam expedita, numquam molestiae ducimus, explicabo reprehenderit sapiente aut repudiandae harum ipsa provident omnis similique. Labore blanditiis quisquam neque praesentium vel reiciendis facilis totam, dolor temporibus assumenda consequatur delectus amet ab, a error molestias facilis eaque mollitia voluptate adipisci temporibus sed veritatis, esse distinctio corrupti aliquid eveniet rerum molestias? Inventore earum debitis numquam aut vitae assumenda enim mollitia, recusandae ullam nisi reprehenderit exercitationem quam delectus iusto vitae pariatur, iste porro iusto rerum voluptas iure, dicta reiciendis in optio, sapiente sed quaerat maxime numquam praesentium enim? Recusandae molestiae ducimus id rem quibusdam a veniam iure, error et suscipit, aperiam veritatis ipsa?</p>\n<p>Totam nisi enim eos odit, mollitia et ex cumque nisi, quis laboriosam dignissimos mollitia pariatur aliquid veniam expedita sapiente sed impedit doloribus? Maiores a reiciendis ea quia in saepe obcaecati suscipit necessitatibus quae. Ut rerum placeat expedita natus nisi molestiae tempore id vitae?</p>	0/1	0	f	2015-12-15 14:15:30.354106+01	53	2
54	<p>Voluptates cupiditate provident cum quos sit quaerat assumenda hic asperiores a. Accusantium architecto corrupti nesciunt odio similique accusamus. Officiis repudiandae voluptatibus sunt nostrum in, tenetur dignissimos dolorem reprehenderit vero consectetur maxime dolor rerum natus voluptatibus deserunt, culpa voluptatem voluptates quae possimus, corporis error ad nihil nobis facilis impedit voluptates vitae inventore sit.</p>	0/1	0	f	2015-12-15 14:15:30.614134+01	54	3
55	<p>Mollitia exercitationem officia deserunt beatae sequi voluptatibus voluptate.</p>	0/1	0	f	2015-12-15 14:15:30.884636+01	55	4
56	<p>Eius inventore possimus quod nemo aperiam saepe quisquam praesentium officiis, accusantium commodi labore natus voluptatum provident mollitia quibusdam, voluptatem placeat exercitationem itaque. Quae eveniet est voluptates non, ad quas aspernatur libero nihil recusandae ex soluta nemo fugit tempora, ut necessitatibus facilis, possimus fugit atque soluta excepturi dolor architecto, eaque alias quos officia nisi ullam corporis fuga modi. Officia deserunt laboriosam magnam alias voluptatibus tempore, necessitatibus laborum excepturi maiores, assumenda quasi atque voluptatum enim eligendi id animi nemo expedita consequatur fuga. Numquam quas voluptates illo distinctio explicabo debitis consequuntur perspiciatis, blanditiis facere quis possimus aliquam natus itaque, laboriosam id tempore officia iste perspiciatis perferendis minima blanditiis necessitatibus, ut ea asperiores dolore consequatur nam nostrum, provident tempore animi quas libero laboriosam officia?</p>\n<p>Quam eum ut consequuntur nostrum ipsam numquam amet eaque sint earum, voluptas a quo alias quam esse quod nobis delectus, alias dolorum quasi ipsa quisquam est aperiam hic, impedit quisquam quae voluptates in blanditiis aperiam reprehenderit natus, alias facilis ut doloribus quam? Nihil iure reprehenderit similique quod est. Accusantium labore similique quisquam, aliquid quidem veniam eum voluptates dolore eaque et quam explicabo asperiores sapiente, ad sapiente facilis, consectetur illum sed ea perferendis sint debitis.</p>\n<p>Reprehenderit dolorem voluptatibus nesciunt architecto quisquam provident quidem asperiores suscipit voluptas, perferendis qui est aperiam architecto illo dolore assumenda neque itaque rerum? Molestias libero doloremque fugiat officiis sit consequatur iure alias quae laborum minima, ab nam voluptatibus modi quisquam laborum placeat eligendi, expedita sapiente hic ducimus, perspiciatis tenetur ratione quia quaerat voluptatum earum officia similique quod deserunt ullam, labore eos aperiam nemo commodi ipsa.</p>\n<p>Quia eaque eveniet nihil velit qui dolore iusto saepe magni, corporis deserunt officia, cumque minima similique suscipit ducimus? Repellat est quibusdam. Nemo dicta dolorum esse voluptatem similique quo?</p>\n<p>Tenetur voluptates maxime officia quae culpa nemo voluptatibus, sunt voluptas voluptates quidem modi asperiores ipsum, at quis dicta, ipsum necessitatibus doloribus eveniet ut suscipit. Odit fugiat repellendus saepe officiis repudiandae optio qui assumenda, quia eius nostrum mollitia consectetur magni alias. Itaque nisi vitae tempora optio dolores cupiditate amet dolorum voluptas laborum alias, consequuntur architecto earum totam, mollitia alias cupiditate vitae fugiat dolore optio accusamus molestias, assumenda dolores unde fuga quia?</p>	0/1	0	f	2015-12-15 14:15:31.145935+01	56	3
57	<p>Cumque perspiciatis delectus omnis labore ipsum repudiandae provident, commodi itaque fuga libero expedita quam praesentium deserunt non saepe odit. Neque vel veritatis inventore consequatur deserunt officia, beatae nulla veniam eligendi dolor sint? Possimus ullam adipisci eveniet quidem laboriosam corrupti assumenda atque porro nam doloribus, quibusdam atque neque veniam repudiandae veritatis debitis ex dolorum natus nihil sed, accusamus nostrum excepturi quos nam suscipit eveniet beatae, adipisci autem in nisi repellendus cum quo.</p>\n<p>Fugit adipisci ratione esse vel ducimus ab nam neque amet optio quo, soluta totam odit perferendis laboriosam minima quasi ex magni nesciunt repellendus pariatur. Nobis assumenda nostrum accusamus repellendus earum atque alias numquam maxime distinctio omnis, adipisci hic distinctio commodi deleniti facere harum omnis, laborum odio aliquid pariatur ex ipsam animi eum suscipit harum, magni a autem cumque commodi numquam pariatur quasi nesciunt beatae ad, voluptates assumenda maiores repellendus est nam neque? Voluptatum aliquid nihil reprehenderit sed exercitationem magnam quis vel error, iusto iure dicta qui eius earum nemo aliquam quasi dolore rerum?</p>\n<p>Asperiores voluptas reprehenderit, labore vitae facilis itaque reprehenderit adipisci in quidem, voluptatum sequi facere quas quia laborum laboriosam explicabo vel repellendus facilis suscipit, laboriosam explicabo fugit impedit corrupti, deserunt laborum quod molestiae dignissimos beatae harum veniam nisi eaque? Odio harum molestiae totam sunt praesentium ex rerum autem, sit omnis animi, officiis veniam dicta earum quaerat tempore, repellat delectus natus laudantium placeat, doloribus beatae quod nesciunt aspernatur.</p>\n<p>Iure repellendus veritatis modi quaerat asperiores fugiat placeat ipsum? Veniam distinctio saepe recusandae omnis molestias libero nihil quod aut et, veritatis voluptas ea pariatur possimus, corrupti est soluta sed placeat ab, autem quaerat saepe est iusto nemo ipsam.</p>\n<p>Commodi officia incidunt doloribus minus quaerat necessitatibus facere quibusdam rerum dolore, unde tempora quaerat odit, rerum dolor omnis at quos ex assumenda ratione maxime distinctio, facilis animi qui ipsum necessitatibus, similique libero corrupti quod voluptate voluptatem fuga nesciunt quam eius atque. Dolor eaque laborum amet, eum nostrum sit voluptas esse quos. Sequi architecto nisi adipisci ipsa natus delectus vel quos harum quisquam atque?</p>	0/1	0	f	2015-12-15 14:15:31.400733+01	57	2
58	<p>Veniam neque cum quia veritatis delectus dignissimos natus nemo, nisi autem similique officiis minus ipsa, accusamus facilis aspernatur id praesentium quibusdam molestias eum atque sit. Praesentium explicabo unde illo, sed commodi delectus exercitationem nihil, iste in cupiditate suscipit aliquid commodi voluptatem quisquam et ducimus molestiae ullam?</p>\n<p>Consequuntur commodi maxime dignissimos sed, libero maiores magni ducimus delectus asperiores perferendis?</p>\n<p>Animi odio dolor tenetur ducimus magni earum temporibus tempora architecto voluptatem officiis, aliquam quasi molestias nesciunt distinctio modi earum quod repellendus, pariatur id dolore aliquam suscipit quod expedita dolorem quisquam mollitia sequi voluptates, ex nesciunt eos?</p>	0/1	0	f	2015-12-15 14:15:31.658371+01	58	2
59	<p>Voluptatum animi pariatur illo dignissimos sequi dolor autem fugiat iste maiores earum, rem autem non consequatur consectetur rerum id minus vitae, perferendis corporis dolor at quibusdam magnam dolorum nesciunt magni, odit amet assumenda ipsum iste vitae ex voluptate, repellendus voluptate dolorem animi inventore nobis officiis corrupti consequatur necessitatibus? Impedit reprehenderit nihil unde ipsam esse quis voluptates repellendus qui nesciunt, magni iure mollitia illo autem, vel cupiditate libero iusto assumenda quis quia amet nihil laborum, tenetur dolor quod magni molestias doloremque quas est? Exercitationem ex sequi veniam beatae facere doloremque nobis consequuntur nesciunt, in reiciendis provident excepturi exercitationem illum minima delectus sequi corporis adipisci, ullam autem tempore laudantium eaque obcaecati tempora debitis sed hic officia, nulla amet quae vero omnis repellendus excepturi asperiores sapiente repellat doloribus? Minima corporis labore quisquam illo quo, ipsam voluptate eos soluta culpa architecto nobis, aperiam in cum quas eos ullam quod, sunt ea quibusdam omnis fugit ipsa ex amet similique officiis modi porro, nisi illum autem in corporis nobis inventore ullam impedit excepturi?</p>\n<p>Qui veritatis ratione minus repellat impedit.</p>\n<p>Cupiditate dolores maxime id sequi culpa, rem qui atque consectetur rerum amet, dolores quae eligendi debitis voluptatum deserunt praesentium, consectetur unde praesentium quis quod ullam illum animi?</p>\n<p>Nulla dolorem incidunt, amet consequatur illo, repellendus molestias dolor quae nemo earum provident temporibus nobis voluptatibus. Consequatur ea rerum quaerat ullam placeat saepe iusto assumenda, voluptatem eius ab blanditiis distinctio assumenda quo vel sunt dicta explicabo molestiae, voluptates nam beatae hic, debitis optio reiciendis maxime, modi vitae ipsa maxime provident?</p>	0/1	0	f	2015-12-15 14:15:31.895065+01	59	3
60	<p>Commodi eum natus beatae nobis sunt vel aliquam ducimus modi iste ea, possimus itaque minus pariatur obcaecati sunt rem quas quod ullam libero, possimus doloribus recusandae quisquam modi esse. Tempore eum non unde atque nam nihil iure deserunt, ullam repellat mollitia cum necessitatibus error. Quasi aut sint corporis quia sed magni natus quisquam delectus doloribus, consequatur officiis voluptatum incidunt sed itaque voluptas maxime voluptate, eveniet ea eligendi suscipit delectus odio dolor perferendis eius, eaque ea reprehenderit alias excepturi neque commodi ipsum.</p>\n<p>Quasi vitae eum ducimus voluptatibus voluptas unde rem id, maiores repellendus incidunt facere ducimus dignissimos in voluptatibus accusantium nemo est? Veniam itaque atque fuga qui perferendis esse, laborum eligendi ducimus omnis repellat, nobis sunt eveniet neque est inventore optio nisi labore odit ea quam. Obcaecati nam autem enim doloribus, aliquid debitis voluptatibus impedit maiores cum hic? Repellat eligendi ipsa asperiores labore, soluta officia sequi rerum similique esse reprehenderit error dolor, dicta libero praesentium laudantium ex odio ipsum similique, expedita iste quasi commodi illo repellendus molestias itaque qui esse natus, unde autem ex assumenda est repellendus dolor veniam.</p>\n<p>Corrupti quas iste harum necessitatibus adipisci molestias earum dolor, dolore nemo itaque unde amet quis?</p>\n<p>Omnis natus itaque? Maxime autem ab veniam reiciendis rem quae voluptatum unde nisi, quas cumque inventore distinctio reprehenderit sit, odit magni rerum doloribus a nihil? Sint modi aperiam numquam suscipit placeat vel, dolor ab repellat nobis eaque quis non placeat molestiae aliquid cumque, placeat eaque animi omnis vel. Alias cupiditate impedit similique facere expedita fuga consequatur porro aperiam deserunt hic, est ad temporibus sunt provident iure nam aut minima maxime, molestiae aspernatur quae culpa excepturi?</p>	0/1	0	f	2015-12-15 14:15:32.164276+01	60	4
61	<p>Ex voluptatibus fuga at magni suscipit perferendis repellat praesentium, eius optio eligendi soluta consequatur voluptates sapiente, eveniet quae eius quibusdam aperiam non quis sint eligendi deserunt, sapiente id et harum quia, blanditiis nobis nesciunt? Fuga et enim quo deserunt culpa soluta tenetur dolore, consectetur dolores quod blanditiis ipsum reiciendis accusantium fugiat dolorem veniam corrupti quasi, corrupti eaque ipsa numquam cumque optio expedita aut rerum incidunt officiis, repudiandae voluptates laudantium. Ab reprehenderit dolor veritatis cumque beatae, labore saepe perferendis consequatur aspernatur ipsum possimus, adipisci deleniti debitis quaerat deserunt labore facere accusantium veritatis quas, incidunt nobis perferendis ullam pariatur.</p>\n<p>Atque ab rem ratione nemo beatae optio quibusdam perferendis id numquam? Qui vitae dolore itaque autem aperiam culpa sequi voluptatum cum praesentium aut, earum ducimus at commodi?</p>	0/1	0	f	2015-12-15 14:15:32.402429+01	61	4
62	<p>Perspiciatis quisquam iure.</p>	1/1	1	t	2015-12-15 14:15:32.627696+01	62	3
63	<p>Itaque possimus nobis, dicta labore maxime repellat. A aperiam corrupti possimus fugit modi inventore, maiores alias ipsum cupiditate cum quibusdam nulla corrupti modi est, ipsum et quae quibusdam quisquam optio reiciendis nam vel reprehenderit, obcaecati in suscipit. Nostrum obcaecati natus ea rerum blanditiis in unde iusto consectetur sed vero, magni pariatur veritatis libero iure atque nihil tempora facere, quidem harum a dicta fugit iste possimus impedit sit deleniti tempore autem? Doloribus ipsa consequuntur esse laboriosam illo, dolor a eos provident quibusdam corrupti obcaecati delectus reprehenderit libero nihil mollitia, cumque totam voluptatibus ducimus vitae quia?</p>\n<p>Dolorem quia odio iste nam exercitationem tempora, sint recusandae neque cumque, ex nostrum perferendis, iure modi accusantium quia aliquid fugiat dolores eligendi sed quae laborum, ex necessitatibus maxime iure? Rerum optio eveniet amet totam voluptates sit repellendus voluptate, consectetur ullam dolorem nihil vitae repellendus cum rerum amet ex officiis, repellendus nobis cumque quaerat, temporibus corporis quis ab quos molestiae.</p>\n<p>Reiciendis sit excepturi incidunt temporibus voluptatem ex omnis similique itaque officiis, officiis accusantium dignissimos quaerat id voluptatum reprehenderit, itaque animi omnis officiis molestiae vel, et eveniet ratione atque aliquam, sint illo eius neque doloremque fugit laboriosam dolore hic impedit cupiditate consequuntur? Architecto possimus ut natus totam facere, tenetur recusandae ipsum nisi quos reprehenderit facere at expedita architecto quas, tempora sunt ducimus officia dicta earum inventore in quod non dignissimos sequi.</p>\n<p>Voluptatem officiis iusto corporis quaerat assumenda aperiam obcaecati recusandae? Commodi impedit nobis doloribus quae repudiandae alias nisi, doloremque quia nisi delectus error ratione sunt quibusdam, commodi ea aliquid magni, illo sed mollitia quibusdam reiciendis cumque aspernatur unde sequi consectetur, voluptate fugiat id suscipit qui architecto facilis sequi sint ad corporis?</p>	0/1	0	f	2015-12-15 14:15:32.852585+01	63	2
64	<p>Molestias earum molestiae facere obcaecati repudiandae ratione eaque pariatur, itaque odit rem, pariatur amet numquam rerum quasi molestias odit cupiditate, quam vitae quo quis ad explicabo obcaecati aliquam, libero quod repellendus facere animi deserunt porro. Obcaecati eveniet officia optio ipsum non repellendus modi minima adipisci eligendi, ex culpa fugit harum voluptatibus aspernatur vel explicabo odio, explicabo adipisci quae nostrum dignissimos ex numquam distinctio nobis, quod laboriosam optio eius ipsum architecto vel veniam a alias ut expedita, perferendis unde porro nostrum est repellendus pariatur velit ab? Dolorum nam cum similique maxime, accusamus aliquid repudiandae reprehenderit vel minima ab est debitis, numquam voluptatum incidunt eius cum. Hic autem consequuntur aut voluptate odio nulla magnam sunt fugit?</p>	1/1	1	t	2015-12-15 14:15:33.083285+01	64	3
65	<p>Pariatur voluptates corrupti animi ad laboriosam saepe, nesciunt asperiores dolore eos beatae harum, blanditiis rerum culpa, vitae neque dicta sit veniam eveniet maxime quam rerum molestias minus suscipit, repellendus qui totam earum fugiat deserunt. Ab porro soluta ratione?</p>\n<p>Nihil labore asperiores, animi aspernatur exercitationem? Qui at in dolor sed soluta iste ea enim, eaque veniam illum maxime dolorem, nulla mollitia corrupti.</p>\n<p>Voluptatum ipsum fugit aspernatur officia sit eius quos magni, ipsam sit velit vero ab nihil tempora eius eaque sunt molestiae, blanditiis quas velit in sed harum incidunt, possimus iste nihil. Nobis adipisci vero optio voluptatum nihil officiis excepturi iusto labore suscipit, labore nam nihil quidem sequi laudantium porro alias repellendus hic ut, odio unde libero magni?</p>\n<p>Eos est cupiditate, sequi ea provident est aspernatur possimus maiores voluptate dolores amet eaque, sit odio inventore reprehenderit distinctio delectus in adipisci ea consequatur, ducimus repellendus cumque, dicta pariatur vero neque maiores ab excepturi quos atque harum consequuntur quas? Velit voluptatibus quidem omnis cupiditate deserunt veniam aperiam sapiente, distinctio odit ullam autem qui. Molestiae debitis rerum doloremque est quia repudiandae nemo optio similique hic commodi, minima iure placeat sed harum saepe velit?</p>\n<p>Excepturi recusandae eligendi laboriosam nesciunt sequi nisi non ab eum animi natus, optio officia culpa magnam consequuntur molestias sed? A nihil adipisci ipsa fugiat sint officia tempora? Impedit numquam repudiandae omnis laborum voluptatibus enim repellat, id autem voluptas et?</p>	1/1	1	t	2015-12-15 14:15:33.329022+01	65	3
\.


--
-- Name: core_staticfeedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_staticfeedback_id_seq', 65, true);


--
-- Data for Name: core_staticfeedbackfileattachment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_staticfeedbackfileattachment (id, filename, file, staticfeedback_id) FROM stdin;
\.


--
-- Name: core_staticfeedbackfileattachment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_staticfeedbackfileattachment_id_seq', 1, false);


--
-- Data for Name: core_subject; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_subject (id, short_name, long_name, etag, parentnode_id) FROM stdin;
1	democourse	DEMO101 - A demo course	2015-12-15 14:15:15.746316+01	1
2	duck1100	DUCK1100 - Programming for the natural sciences	2015-12-15 14:15:15.950045+01	1
3	inf7020	INF7020 Programming for World Domination and Crashing Non-Mutant Economy	2015-12-15 14:15:43.732852+01	1
\.


--
-- Data for Name: core_subject_admins; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_subject_admins (id, subject_id, user_id) FROM stdin;
1	1	2
2	2	2
\.


--
-- Name: core_subject_admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_subject_admins_id_seq', 2, true);


--
-- Name: core_subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_subject_id_seq', 3, true);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq', 1, false);


--
-- Data for Name: cradmin_generic_token_with_metadata_generictokenwithmetadata; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY cradmin_generic_token_with_metadata_generictokenwithmetadata (id, app, token, created_datetime, expiration_datetime, single_use, metadata_json, object_id, content_type_id) FROM stdin;
\.


--
-- Data for Name: cradmin_temporaryfileuploadstore_temporaryfile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY cradmin_temporaryfileuploadstore_temporaryfile (id, filename, file, mimetype, collection_id) FROM stdin;
\.


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('cradmin_temporaryfileuploadstore_temporaryfile_id_seq', 1, false);


--
-- Data for Name: cradmin_temporaryfileuploadstore_temporaryfilecollection; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY cradmin_temporaryfileuploadstore_temporaryfilecollection (id, created_datetime, minutes_to_live, accept, max_filename_length, unique_filenames, user_id, singlemode, max_filesize_bytes) FROM stdin;
\.


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq', 1, false);


--
-- Data for Name: devilry_account_periodpermissiongroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_periodpermissiongroup (id, period_id, permissiongroup_id) FROM stdin;
\.


--
-- Name: devilry_account_periodpermissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_periodpermissiongroup_id_seq', 1, false);


--
-- Data for Name: devilry_account_permissiongroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_permissiongroup (id, name, created_datetime, updated_datetime, syncsystem_update_datetime, grouptype, is_custom_manageable) FROM stdin;
1	Duckburgh Department Admins	2015-12-21 13:18:53.259494+01	2015-12-21 13:32:39.556138+01	\N	departmentadmin	f
\.


--
-- Name: devilry_account_permissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_permissiongroup_id_seq', 1, true);


--
-- Data for Name: devilry_account_permissiongroupuser; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_permissiongroupuser (id, permissiongroup_id, user_id) FROM stdin;
1	1	2
2	1	1
\.


--
-- Name: devilry_account_permissiongroupuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_permissiongroupuser_id_seq', 2, true);


--
-- Data for Name: devilry_account_subjectpermissiongroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_subjectpermissiongroup (id, permissiongroup_id, subject_id) FROM stdin;
1	1	2
\.


--
-- Name: devilry_account_subjectpermissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_subjectpermissiongroup_id_seq', 1, true);


--
-- Data for Name: devilry_account_user; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_user (id, password, last_login, is_superuser, shortname, fullname, lastname, datetime_joined, suspended_datetime, suspended_reason, languagecode) FROM stdin;
4	md5$HgWpraJxiAxe$c4b5a3f5e2dbd7d7dcdbc804fc489bbd	\N	f	scrooge@example.com	Scrooge McDuck	McDuck	2015-12-15 14:15:15.58154+01	\N		
5	md5$RPyXhM28V6tB$b13b5d05061cfdb54f8bc4114f05de15	\N	f	dewey@example.com	Dewey Duck	Duck	2015-12-15 14:15:15.585196+01	\N		
6	md5$lii396cBsqyI$727a331359153a07fb84f1763ada2352	\N	f	louie@example.com	Louie Duck	Duck	2015-12-15 14:15:15.588599+01	\N		
7	md5$DJU4PJmwcCGJ$73b8dee6ad83a2d00ff6ee16f19f12c0	\N	f	huey@example.com	Huey Duck	Duck	2015-12-15 14:15:15.591902+01	\N		
8	md5$GUbtm77CGs0c$cc3fce51a649e68c74722e28bf9989ec	\N	f	june@example.com	June Duck	Duck	2015-12-15 14:15:15.595389+01	\N		
9	md5$14UOApHMcChI$000186b4b04959b30a5c62cf672c3b55	\N	f	july@example.com	July Duck	Duck	2015-12-15 14:15:15.598571+01	\N		
10	md5$0t8zybeyiKQj$d8fa1a083209f1f219e84378ff0b4bf1	\N	f	baldr@example.com	God of Beauty	Beauty	2015-12-15 14:15:15.607867+01	\N		
11	md5$IblptVjzuzT3$253ef7027f2a214d72c3979afdaff11c	\N	f	freyja@example.com	Goddess of Love	Love	2015-12-15 14:15:15.611966+01	\N		
12	md5$wbWrCByNOye6$3d9d4a97e50342cd51d0f7d696bafecb	\N	f	freyr@example.com	God of Fertility	Fertility	2015-12-15 14:15:15.615097+01	\N		
13	md5$IaByQm8rq3F8$810285aab818ccf1f5e1170842cb3248	\N	f	kvasir@example.com	God of Inspiration	Inspiration	2015-12-15 14:15:15.618162+01	\N		
14	md5$DIFteVGClLrs$f79f956cc25616d653be3deef3bbed12	\N	f	loki@example.com	Trickster and god of Mischief	Mischief	2015-12-15 14:15:15.621594+01	\N		
15	md5$v8iOwudRll7e$1d373957f2a35af59457f01c26ed7e9d	\N	f	odin@example.com	The "All Father"	Father"	2015-12-15 14:15:15.624581+01	\N		
3	md5$gj0DrWWTVFGj$4382a111601870383e5a65d343a5fb3b	\N	f	donald@example.com	Donald Duck	Duck	2015-12-15 14:15:15.576523+01	\N		nb
16	md5$cwKqBvk99rVV$30fbe775725400886bf2fb8fb18f2344	\N	f	april@example.com	April Duck	Duck	2015-12-15 14:15:15.627473+01	\N		nb
17	md5$pEY8o8593Rp9$d6cb2525663c485777fad112bff07c30	\N	f	psylocke@example.com	Elisabeth Braddock	Braddock	2015-12-15 14:15:43.71966+01	\N		
18	md5$DVn6sZdYr9lc$0f32d367fc2146bbbd1aea3f1f6953e2	\N	f	magneto@example.com	Erik Lehnsherr	Lehnsherr	2015-12-15 14:15:43.724288+01	\N		
19	md5$K0UZAHaV14QX$67ca859f45cdf891806bd0232c4f36a6	\N	f	beast@example.com	Hank McCoy	McCoy	2015-12-15 14:15:43.727901+01	\N		
2	md5$60NFqVu8kIeZ$3b76e76648c0cfb5b0691160792ef1cc	2015-12-15 14:24:03.193906+01	f	thor@example.com	God of Thunder and Battle	Battle	2015-12-15 14:15:15.572086+01	\N		nb
1	md5$BzTth28hoiZn$e2b0d0d19a7f5c6b1b13e671c4b2ca65	2015-12-15 20:24:53.295245+01	t	grandma@example.com	Elvira "Grandma" Coot	Coot	2015-12-15 14:15:15.558661+01	\N		
\.


--
-- Name: devilry_account_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_user_id_seq', 19, true);


--
-- Data for Name: devilry_account_useremail; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_useremail (id, created_datetime, last_updated_datetime, email, use_for_notifications, is_primary, user_id) FROM stdin;
1	2015-12-15 14:15:15.569908+01	2015-12-15 14:15:15.569918+01	grandma@example.com	t	t	1
2	2015-12-15 14:15:15.574772+01	2015-12-15 14:15:15.574782+01	thor@example.com	t	t	2
3	2015-12-15 14:15:15.580062+01	2015-12-15 14:15:15.580077+01	donald@example.com	t	t	3
4	2015-12-15 14:15:15.583985+01	2015-12-15 14:15:15.583994+01	scrooge@example.com	t	t	4
5	2015-12-15 14:15:15.587461+01	2015-12-15 14:15:15.58747+01	dewey@example.com	t	t	5
6	2015-12-15 14:15:15.590861+01	2015-12-15 14:15:15.590871+01	louie@example.com	t	t	6
7	2015-12-15 14:15:15.594465+01	2015-12-15 14:15:15.594474+01	huey@example.com	t	t	7
8	2015-12-15 14:15:15.597582+01	2015-12-15 14:15:15.597592+01	june@example.com	t	t	8
9	2015-12-15 14:15:15.600777+01	2015-12-15 14:15:15.600786+01	july@example.com	t	t	9
10	2015-12-15 14:15:15.610826+01	2015-12-15 14:15:15.610838+01	baldr@example.com	t	t	10
11	2015-12-15 14:15:15.614114+01	2015-12-15 14:15:15.614123+01	freyja@example.com	t	t	11
12	2015-12-15 14:15:15.617169+01	2015-12-15 14:15:15.617178+01	freyr@example.com	t	t	12
13	2015-12-15 14:15:15.620637+01	2015-12-15 14:15:15.620648+01	kvasir@example.com	t	t	13
14	2015-12-15 14:15:15.623679+01	2015-12-15 14:15:15.623689+01	loki@example.com	t	t	14
15	2015-12-15 14:15:15.626579+01	2015-12-15 14:15:15.626588+01	odin@example.com	t	t	15
16	2015-12-15 14:15:15.629422+01	2015-12-15 14:15:15.629431+01	april@example.com	t	t	16
17	2015-12-15 14:15:43.723017+01	2015-12-15 14:15:43.723031+01	psylocke@example.com	t	t	17
18	2015-12-15 14:15:43.726827+01	2015-12-15 14:15:43.726838+01	magneto@example.com	t	t	18
19	2015-12-15 14:15:43.73156+01	2015-12-15 14:15:43.731571+01	beast@example.com	t	t	19
\.


--
-- Name: devilry_account_useremail_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_useremail_id_seq', 19, true);


--
-- Data for Name: devilry_account_username; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_username (id, created_datetime, last_updated_datetime, username, is_primary, user_id) FROM stdin;
\.


--
-- Name: devilry_account_username_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_username_id_seq', 1, false);


--
-- Data for Name: devilry_comment_comment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_comment_comment (id, text, created_datetime, published_datetime, user_role, comment_type, parent_id, user_id) FROM stdin;
1	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:33.546163+01	2014-12-12 14:15:33.545733+01	student	groupcomment	\N	5
2	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:33.549743+01	2014-12-13 12:15:33.549394+01	student	groupcomment	\N	5
3	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:33.552305+01	2014-12-12 22:15:33.551991+01	student	groupcomment	\N	5
4	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:33.560789+01	2014-12-14 14:15:33.56045+01	examiner	groupcomment	\N	3
5	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:33.64605+01	2014-12-12 14:15:33.645692+01	student	groupcomment	\N	8
6	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:33.654106+01	2014-12-13 12:15:33.653732+01	student	groupcomment	\N	8
7	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:33.658848+01	2014-12-13 12:15:33.658521+01	student	groupcomment	\N	8
8	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:33.663591+01	2014-12-12 22:15:33.663269+01	student	groupcomment	\N	8
9	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:33.6706+01	2014-12-14 14:15:33.670274+01	examiner	groupcomment	\N	2
10	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:33.730148+01	2014-12-12 14:15:33.729802+01	student	groupcomment	\N	2
11	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:33.732639+01	2014-12-14 14:15:33.732352+01	examiner	groupcomment	\N	2
12	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:33.87632+01	2014-12-12 14:15:33.875975+01	student	groupcomment	\N	9
13	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:33.884161+01	2014-12-12 18:15:33.883801+01	student	groupcomment	\N	9
14	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:33.890986+01	2014-12-14 14:15:33.890639+01	examiner	groupcomment	\N	4
15	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:33.954737+01	2014-12-12 14:15:33.954392+01	student	groupcomment	\N	7
16	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:33.962862+01	2014-12-12 22:15:33.962439+01	student	groupcomment	\N	7
17	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:33.968274+01	2014-12-12 17:15:33.967762+01	student	groupcomment	\N	7
18	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:33.970886+01	2014-12-13 06:15:33.970575+01	student	groupcomment	\N	7
19	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:33.976029+01	2014-12-13 05:15:33.975687+01	student	groupcomment	\N	7
20	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:33.983531+01	2014-12-14 14:15:33.98317+01	examiner	groupcomment	\N	3
58	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:34.931421+01	2015-10-30 14:15:34.931009+01	student	groupcomment	\N	8
21	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:34.057564+01	2014-12-12 14:15:34.057204+01	student	groupcomment	\N	6
22	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:34.063185+01	2014-12-12 23:15:34.062805+01	student	groupcomment	\N	6
23	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:34.070922+01	2014-12-13 01:15:34.070553+01	student	groupcomment	\N	6
24	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:34.073166+01	2014-12-12 22:15:34.072855+01	student	groupcomment	\N	6
25	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:34.075353+01	2014-12-12 21:15:34.075051+01	student	groupcomment	\N	6
26	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:34.082884+01	2014-12-14 14:15:34.082493+01	examiner	groupcomment	\N	3
27	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:34.15837+01	2014-12-12 14:15:34.157979+01	student	groupcomment	\N	13
28	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:34.166636+01	2014-12-13 06:15:34.166281+01	student	groupcomment	\N	13
29	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:34.174444+01	2014-12-12 21:15:34.174076+01	student	groupcomment	\N	13
30	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:34.17683+01	2014-12-12 17:15:34.176479+01	student	groupcomment	\N	13
31	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:34.179142+01	2014-12-14 14:15:34.17881+01	examiner	groupcomment	\N	4
32	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:34.256191+01	2014-12-12 14:15:34.255863+01	student	groupcomment	\N	14
33	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:34.258646+01	2014-12-14 14:15:34.258329+01	examiner	groupcomment	\N	2
34	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:34.331841+01	2014-12-12 14:15:34.331476+01	student	groupcomment	\N	12
35	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:34.336898+01	2014-12-14 14:15:34.336552+01	examiner	groupcomment	\N	3
36	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:34.419554+01	2014-12-12 14:15:34.419222+01	student	groupcomment	\N	10
37	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:34.424676+01	2014-12-12 18:15:34.424329+01	student	groupcomment	\N	10
59	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:34.934125+01	2015-10-31 03:15:34.933787+01	student	groupcomment	\N	8
38	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:34.427219+01	2014-12-12 22:15:34.426766+01	student	groupcomment	\N	10
39	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:34.429615+01	2014-12-13 01:15:34.429211+01	student	groupcomment	\N	10
40	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:34.434797+01	2014-12-13 07:15:34.434371+01	student	groupcomment	\N	10
41	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:34.437016+01	2014-12-14 14:15:34.43671+01	examiner	groupcomment	\N	3
42	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:34.51479+01	2014-12-12 14:15:34.514448+01	student	groupcomment	\N	15
43	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:34.51726+01	2014-12-12 17:15:34.516965+01	student	groupcomment	\N	15
44	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:34.519615+01	2014-12-12 16:15:34.519278+01	student	groupcomment	\N	15
45	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:34.52671+01	2014-12-13 03:15:34.526384+01	student	groupcomment	\N	15
46	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:34.531182+01	2014-12-13 08:15:34.530857+01	student	groupcomment	\N	15
47	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:34.53823+01	2014-12-14 14:15:34.537878+01	examiner	groupcomment	\N	3
48	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:34.613602+01	2014-12-12 14:15:34.613289+01	student	groupcomment	\N	11
49	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:34.621617+01	2014-12-14 14:15:34.621247+01	examiner	groupcomment	\N	3
50	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:34.681466+01	2014-12-12 14:15:34.681115+01	student	groupcomment	\N	16
51	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:34.686694+01	2014-12-14 14:15:34.686348+01	examiner	groupcomment	\N	3
52	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:34.81252+01	2015-10-30 14:15:34.81219+01	student	groupcomment	\N	5
53	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:34.815005+01	2015-10-30 22:15:34.814716+01	student	groupcomment	\N	5
54	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:34.820111+01	2015-10-31 09:15:34.819782+01	student	groupcomment	\N	5
55	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:34.822408+01	2015-10-31 14:15:34.822106+01	student	groupcomment	\N	5
56	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:34.827315+01	2015-10-30 19:15:34.826993+01	student	groupcomment	\N	5
57	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:34.835213+01	2015-11-01 14:15:34.834846+01	examiner	groupcomment	\N	3
60	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:34.941697+01	2015-10-30 23:15:34.941342+01	student	groupcomment	\N	8
61	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:34.943948+01	2015-10-31 03:15:34.94365+01	student	groupcomment	\N	8
62	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:34.946155+01	2015-11-01 14:15:34.945856+01	examiner	groupcomment	\N	4
63	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:35.011406+01	2015-10-30 14:15:35.011036+01	student	groupcomment	\N	2
64	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:35.019143+01	2015-10-31 14:15:35.018799+01	student	groupcomment	\N	2
65	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:35.023937+01	2015-10-31 08:15:35.02361+01	student	groupcomment	\N	2
66	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:35.030815+01	2015-11-01 14:15:35.030487+01	examiner	groupcomment	\N	2
67	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:35.094182+01	2015-10-30 14:15:35.093855+01	student	groupcomment	\N	9
68	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:35.102009+01	2015-10-31 01:15:35.101659+01	student	groupcomment	\N	9
69	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:35.106936+01	2015-10-30 22:15:35.106613+01	student	groupcomment	\N	9
70	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:35.109176+01	2015-10-31 05:15:35.108876+01	student	groupcomment	\N	9
71	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:35.113909+01	2015-10-31 07:15:35.113554+01	student	groupcomment	\N	9
72	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:35.120784+01	2015-11-01 14:15:35.120458+01	examiner	groupcomment	\N	4
73	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:35.192661+01	2015-10-30 14:15:35.192324+01	student	groupcomment	\N	7
74	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:35.198158+01	2015-10-31 11:15:35.197801+01	student	groupcomment	\N	7
75	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:35.203283+01	2015-11-01 14:15:35.202936+01	examiner	groupcomment	\N	4
76	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:35.277966+01	2015-10-30 14:15:35.277584+01	student	groupcomment	\N	6
77	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:35.283091+01	2015-10-30 20:15:35.282764+01	student	groupcomment	\N	6
155	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:36.965083+01	2015-11-07 14:15:36.96475+01	student	groupcomment	\N	12
78	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:35.287683+01	2015-11-01 14:15:35.287361+01	examiner	groupcomment	\N	2
79	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:35.3574+01	2015-10-30 14:15:35.357038+01	student	groupcomment	\N	13
80	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:35.362907+01	2015-10-31 14:15:35.362543+01	student	groupcomment	\N	13
81	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:35.37039+01	2015-10-30 19:15:35.370065+01	student	groupcomment	\N	13
82	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:35.377457+01	2015-10-31 11:15:35.377124+01	student	groupcomment	\N	13
83	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:35.384347+01	2015-11-01 14:15:35.384016+01	examiner	groupcomment	\N	3
84	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:35.462482+01	2015-10-30 14:15:35.462071+01	student	groupcomment	\N	14
85	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:35.468184+01	2015-10-31 02:15:35.467848+01	student	groupcomment	\N	14
86	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:35.473022+01	2015-10-30 18:15:35.47269+01	student	groupcomment	\N	14
87	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:35.477646+01	2015-10-31 03:15:35.477291+01	student	groupcomment	\N	14
88	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:35.48233+01	2015-10-31 03:15:35.482005+01	student	groupcomment	\N	14
89	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:35.484504+01	2015-11-01 14:15:35.484206+01	examiner	groupcomment	\N	2
90	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:35.559042+01	2015-10-30 14:15:35.558724+01	student	groupcomment	\N	12
91	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:35.564388+01	2015-10-30 21:15:35.564027+01	student	groupcomment	\N	12
92	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:35.569328+01	2015-10-31 10:15:35.568996+01	student	groupcomment	\N	12
93	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:35.576302+01	2015-11-01 14:15:35.575966+01	examiner	groupcomment	\N	4
94	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:35.653946+01	2015-10-30 14:15:35.653641+01	student	groupcomment	\N	10
95	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:35.662015+01	2015-10-31 13:15:35.661634+01	student	groupcomment	\N	10
96	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:35.669095+01	2015-10-31 13:15:35.668696+01	student	groupcomment	\N	10
97	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:35.673977+01	2015-10-30 23:15:35.673638+01	student	groupcomment	\N	10
98	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:35.676136+01	2015-11-01 14:15:35.675837+01	examiner	groupcomment	\N	2
99	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:35.776958+01	2015-10-30 14:15:35.776532+01	student	groupcomment	\N	15
100	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:35.782331+01	2015-10-31 09:15:35.781984+01	student	groupcomment	\N	15
101	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:35.784638+01	2015-10-31 03:15:35.784324+01	student	groupcomment	\N	15
102	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:35.791654+01	2015-10-31 07:15:35.791312+01	student	groupcomment	\N	15
103	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:35.796436+01	2015-10-31 09:15:35.796104+01	student	groupcomment	\N	15
104	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:35.80117+01	2015-11-01 14:15:35.800846+01	examiner	groupcomment	\N	4
105	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:35.911596+01	2015-10-30 14:15:35.911195+01	student	groupcomment	\N	11
106	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:35.917124+01	2015-10-31 05:15:35.91679+01	student	groupcomment	\N	11
107	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:35.919419+01	2015-10-30 18:15:35.919118+01	student	groupcomment	\N	11
108	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:35.924082+01	2015-10-31 05:15:35.923764+01	student	groupcomment	\N	11
109	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:35.931178+01	2015-10-31 10:15:35.930845+01	student	groupcomment	\N	11
110	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:35.93583+01	2015-11-01 14:15:35.935499+01	examiner	groupcomment	\N	3
111	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:35.996843+01	2015-10-30 14:15:35.996476+01	student	groupcomment	\N	16
112	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:35.999576+01	2015-10-30 16:15:35.999246+01	student	groupcomment	\N	16
113	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:36.007219+01	2015-10-30 17:15:36.006884+01	student	groupcomment	\N	16
114	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:36.009467+01	2015-11-01 14:15:36.009137+01	examiner	groupcomment	\N	3
154	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:36.962875+01	2015-11-07 09:15:36.962523+01	student	groupcomment	\N	12
115	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:36.125681+01	2015-11-06 14:15:36.125354+01	student	groupcomment	\N	5
116	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:36.133644+01	2015-11-06 22:15:36.133286+01	student	groupcomment	\N	5
117	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:36.138502+01	2015-11-07 01:15:36.138172+01	student	groupcomment	\N	5
118	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:36.140847+01	2015-11-06 20:15:36.140479+01	student	groupcomment	\N	5
119	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:36.143545+01	2015-11-08 14:15:36.143134+01	examiner	groupcomment	\N	3
120	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:36.24169+01	2015-11-06 14:15:36.241081+01	student	groupcomment	\N	8
121	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:36.252737+01	2015-11-07 05:15:36.252289+01	student	groupcomment	\N	8
122	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:36.263533+01	2015-11-07 06:15:36.262897+01	student	groupcomment	\N	8
123	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:36.270491+01	2015-11-06 23:15:36.270063+01	student	groupcomment	\N	8
124	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:36.279591+01	2015-11-06 20:15:36.279244+01	student	groupcomment	\N	8
125	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:36.284849+01	2015-11-08 14:15:36.284458+01	examiner	groupcomment	\N	2
126	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:36.366271+01	2015-11-06 14:15:36.365866+01	student	groupcomment	\N	2
127	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:36.372258+01	2015-11-06 19:15:36.371577+01	student	groupcomment	\N	2
128	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:36.377545+01	2015-11-06 16:15:36.377173+01	student	groupcomment	\N	2
129	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:36.38473+01	2015-11-06 18:15:36.384367+01	student	groupcomment	\N	2
130	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:36.387028+01	2015-11-06 22:15:36.386675+01	student	groupcomment	\N	2
131	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:36.395011+01	2015-11-08 14:15:36.394637+01	examiner	groupcomment	\N	4
132	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:36.474266+01	2015-11-06 14:15:36.47395+01	student	groupcomment	\N	9
133	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:36.476771+01	2015-11-07 05:15:36.476472+01	student	groupcomment	\N	9
134	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:36.481612+01	2015-11-08 14:15:36.481284+01	examiner	groupcomment	\N	2
135	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:36.562731+01	2015-11-06 14:15:36.562412+01	student	groupcomment	\N	7
136	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:36.571486+01	2015-11-07 04:15:36.571069+01	student	groupcomment	\N	7
137	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:36.576612+01	2015-11-07 03:15:36.576239+01	student	groupcomment	\N	7
138	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:36.581488+01	2015-11-08 14:15:36.581113+01	examiner	groupcomment	\N	4
139	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:36.669642+01	2015-11-06 14:15:36.669285+01	student	groupcomment	\N	6
140	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:36.67538+01	2015-11-07 13:15:36.674931+01	student	groupcomment	\N	6
141	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:36.681854+01	2015-11-08 14:15:36.681475+01	examiner	groupcomment	\N	3
142	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:36.749174+01	2015-11-06 14:15:36.748844+01	student	groupcomment	\N	13
143	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:36.756644+01	2015-11-07 04:15:36.756303+01	student	groupcomment	\N	13
144	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:36.761785+01	2015-11-07 08:15:36.761378+01	student	groupcomment	\N	13
145	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:36.766642+01	2015-11-08 14:15:36.76626+01	examiner	groupcomment	\N	4
146	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:36.863057+01	2015-11-06 14:15:36.862727+01	student	groupcomment	\N	14
147	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:36.867865+01	2015-11-06 16:15:36.867526+01	student	groupcomment	\N	14
148	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:36.872558+01	2015-11-07 03:15:36.872207+01	student	groupcomment	\N	14
149	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:36.8795+01	2015-11-07 13:15:36.879114+01	student	groupcomment	\N	14
150	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:36.881995+01	2015-11-07 05:15:36.881619+01	student	groupcomment	\N	14
151	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:36.884187+01	2015-11-08 14:15:36.883886+01	examiner	groupcomment	\N	2
152	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:36.950959+01	2015-11-06 14:15:36.950629+01	student	groupcomment	\N	12
153	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:36.958059+01	2015-11-07 07:15:36.957733+01	student	groupcomment	\N	12
156	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:36.969897+01	2015-11-08 14:15:36.969557+01	examiner	groupcomment	\N	4
157	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:37.064114+01	2015-11-06 14:15:37.063761+01	student	groupcomment	\N	10
158	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:37.066577+01	2015-11-07 02:15:37.066268+01	student	groupcomment	\N	10
159	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:37.068983+01	2015-11-07 09:15:37.068645+01	student	groupcomment	\N	10
160	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:37.074016+01	2015-11-07 14:15:37.073682+01	student	groupcomment	\N	10
161	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:37.076401+01	2015-11-08 14:15:37.076081+01	examiner	groupcomment	\N	2
162	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:37.136252+01	2015-11-06 14:15:37.135922+01	student	groupcomment	\N	15
163	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:37.144584+01	2015-11-07 03:15:37.1442+01	student	groupcomment	\N	15
164	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:37.146771+01	2015-11-07 02:15:37.146455+01	student	groupcomment	\N	15
165	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:37.153846+01	2015-11-08 14:15:37.153513+01	examiner	groupcomment	\N	2
166	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:37.224496+01	2015-11-06 14:15:37.22418+01	student	groupcomment	\N	11
167	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:37.227064+01	2015-11-08 14:15:37.226763+01	examiner	groupcomment	\N	4
168	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:37.29989+01	2015-11-06 14:15:37.299516+01	student	groupcomment	\N	16
169	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:37.302599+01	2015-11-08 14:15:37.302272+01	examiner	groupcomment	\N	3
170	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:37.434727+01	2015-11-13 14:15:37.434287+01	student	groupcomment	\N	5
171	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:37.440195+01	2015-11-15 14:15:37.439843+01	examiner	groupcomment	\N	4
172	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:37.517343+01	2015-11-13 14:15:37.516876+01	student	groupcomment	\N	8
173	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:37.52251+01	2015-11-14 06:15:37.522121+01	student	groupcomment	\N	8
174	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:37.529592+01	2015-11-13 19:15:37.529259+01	student	groupcomment	\N	8
175	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:37.531787+01	2015-11-13 20:15:37.531478+01	student	groupcomment	\N	8
176	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:37.536115+01	2015-11-15 14:15:37.535798+01	examiner	groupcomment	\N	2
315	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:41.029225+01	2015-12-04 14:15:41.028895+01	student	groupcomment	\N	10
177	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:37.613194+01	2015-11-13 14:15:37.61285+01	student	groupcomment	\N	2
178	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:37.618129+01	2015-11-13 16:15:37.617799+01	student	groupcomment	\N	2
179	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:37.620288+01	2015-11-13 23:15:37.619971+01	student	groupcomment	\N	2
180	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:37.62246+01	2015-11-15 14:15:37.622162+01	examiner	groupcomment	\N	4
181	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:37.706135+01	2015-11-13 14:15:37.705777+01	student	groupcomment	\N	9
182	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:37.711369+01	2015-11-13 23:15:37.711014+01	student	groupcomment	\N	9
183	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:37.718882+01	2015-11-13 22:15:37.718543+01	student	groupcomment	\N	9
184	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:37.726175+01	2015-11-15 14:15:37.725832+01	examiner	groupcomment	\N	2
185	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:37.790203+01	2015-11-13 14:15:37.789868+01	student	groupcomment	\N	7
186	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:37.798054+01	2015-11-14 03:15:37.797667+01	student	groupcomment	\N	7
187	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:37.806267+01	2015-11-15 14:15:37.805906+01	examiner	groupcomment	\N	3
188	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:38.160113+01	2015-11-13 14:15:38.159791+01	student	groupcomment	\N	6
189	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:38.162603+01	2015-11-14 06:15:38.162298+01	student	groupcomment	\N	6
190	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:38.170233+01	2015-11-14 00:15:38.169905+01	student	groupcomment	\N	6
191	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:38.174833+01	2015-11-14 01:15:38.174502+01	student	groupcomment	\N	6
192	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:38.182016+01	2015-11-15 14:15:38.181691+01	examiner	groupcomment	\N	3
193	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:38.244929+01	2015-11-13 14:15:38.244603+01	student	groupcomment	\N	13
194	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:38.247206+01	2015-11-14 00:15:38.246885+01	student	groupcomment	\N	13
195	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:38.249517+01	2015-11-14 02:15:38.249215+01	student	groupcomment	\N	13
196	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:38.254428+01	2015-11-13 20:15:38.254092+01	student	groupcomment	\N	13
197	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:38.259175+01	2015-11-15 14:15:38.25885+01	examiner	groupcomment	\N	2
198	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:38.329104+01	2015-11-13 14:15:38.328744+01	student	groupcomment	\N	14
199	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:38.337074+01	2015-11-13 17:15:38.336722+01	student	groupcomment	\N	14
200	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:38.339302+01	2015-11-13 23:15:38.338985+01	student	groupcomment	\N	14
201	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:38.346497+01	2015-11-13 16:15:38.346153+01	student	groupcomment	\N	14
202	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:38.351272+01	2015-11-14 00:15:38.350942+01	student	groupcomment	\N	14
203	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:38.358372+01	2015-11-15 14:15:38.358041+01	examiner	groupcomment	\N	3
204	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:38.430934+01	2015-11-13 14:15:38.430608+01	student	groupcomment	\N	12
205	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:38.433504+01	2015-11-15 14:15:38.433183+01	examiner	groupcomment	\N	3
206	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:38.502434+01	2015-11-13 14:15:38.50212+01	student	groupcomment	\N	10
207	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:38.504958+01	2015-11-13 17:15:38.504597+01	student	groupcomment	\N	10
208	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:38.510178+01	2015-11-15 14:15:38.509833+01	examiner	groupcomment	\N	2
209	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:38.579292+01	2015-11-13 14:15:38.578958+01	student	groupcomment	\N	15
210	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:38.587182+01	2015-11-14 11:15:38.586841+01	student	groupcomment	\N	15
211	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:38.594273+01	2015-11-14 10:15:38.593924+01	student	groupcomment	\N	15
212	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:38.599006+01	2015-11-15 14:15:38.598679+01	examiner	groupcomment	\N	3
213	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:38.672948+01	2015-11-13 14:15:38.67261+01	student	groupcomment	\N	11
214	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:38.681324+01	2015-11-14 00:15:38.680974+01	student	groupcomment	\N	11
215	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:38.683614+01	2015-11-14 01:15:38.683313+01	student	groupcomment	\N	11
216	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:38.69077+01	2015-11-14 00:15:38.690443+01	student	groupcomment	\N	11
217	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:38.695363+01	2015-11-15 14:15:38.695043+01	examiner	groupcomment	\N	4
218	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:38.773842+01	2015-11-13 14:15:38.773489+01	student	groupcomment	\N	16
219	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:38.781655+01	2015-11-14 09:15:38.781301+01	student	groupcomment	\N	16
220	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:38.786329+01	2015-11-14 07:15:38.78599+01	student	groupcomment	\N	16
221	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:38.793302+01	2015-11-15 14:15:38.792977+01	examiner	groupcomment	\N	3
222	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:38.91734+01	2015-11-20 14:15:38.917005+01	student	groupcomment	\N	5
223	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:38.919735+01	2015-11-22 14:15:38.919416+01	examiner	groupcomment	\N	2
224	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:39.011147+01	2015-11-20 14:15:39.010747+01	student	groupcomment	\N	8
225	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:39.013948+01	2015-11-21 06:15:39.013598+01	student	groupcomment	\N	8
226	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:39.016274+01	2015-11-20 16:15:39.01596+01	student	groupcomment	\N	8
227	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:39.018963+01	2015-11-21 07:15:39.018296+01	student	groupcomment	\N	8
228	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:39.02474+01	2015-11-22 14:15:39.02437+01	examiner	groupcomment	\N	4
229	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:39.092111+01	2015-11-20 14:15:39.091792+01	student	groupcomment	\N	2
230	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:39.100074+01	2015-11-22 14:15:39.099686+01	examiner	groupcomment	\N	4
231	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:39.191682+01	2015-11-20 14:15:39.191352+01	student	groupcomment	\N	9
232	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:39.194211+01	2015-11-20 22:15:39.193895+01	student	groupcomment	\N	9
233	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:39.202292+01	2015-11-21 08:15:39.201892+01	student	groupcomment	\N	9
234	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:39.204712+01	2015-11-20 18:15:39.204376+01	student	groupcomment	\N	9
235	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:39.206888+01	2015-11-22 14:15:39.206573+01	examiner	groupcomment	\N	3
236	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:39.269913+01	2015-11-20 14:15:39.269571+01	student	groupcomment	\N	7
237	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:39.275055+01	2015-11-20 17:15:39.274665+01	student	groupcomment	\N	7
238	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:39.283087+01	2015-11-21 13:15:39.282692+01	student	groupcomment	\N	7
239	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:39.285713+01	2015-11-21 10:15:39.285379+01	student	groupcomment	\N	7
240	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:39.288038+01	2015-11-22 14:15:39.28774+01	examiner	groupcomment	\N	4
241	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:39.356147+01	2015-11-20 14:15:39.355779+01	student	groupcomment	\N	6
242	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:39.365353+01	2015-11-20 16:15:39.365008+01	student	groupcomment	\N	6
243	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:39.370099+01	2015-11-22 14:15:39.369742+01	examiner	groupcomment	\N	3
244	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:39.441286+01	2015-11-20 14:15:39.440956+01	student	groupcomment	\N	13
245	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:39.446198+01	2015-11-22 14:15:39.445873+01	examiner	groupcomment	\N	2
246	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:39.520242+01	2015-11-20 14:15:39.519917+01	student	groupcomment	\N	14
247	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:39.527734+01	2015-11-21 07:15:39.527331+01	student	groupcomment	\N	14
248	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:39.534963+01	2015-11-22 14:15:39.534621+01	examiner	groupcomment	\N	3
249	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:39.609704+01	2015-11-20 14:15:39.609294+01	student	groupcomment	\N	12
250	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:39.615238+01	2015-11-21 12:15:39.614895+01	student	groupcomment	\N	12
251	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:39.620963+01	2015-11-21 09:15:39.620486+01	student	groupcomment	\N	12
252	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:39.63003+01	2015-11-20 18:15:39.629653+01	student	groupcomment	\N	12
253	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:39.637166+01	2015-11-20 21:15:39.636786+01	student	groupcomment	\N	12
254	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:39.641926+01	2015-11-22 14:15:39.641576+01	examiner	groupcomment	\N	3
255	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:39.715964+01	2015-11-20 14:15:39.715645+01	student	groupcomment	\N	10
256	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:39.718738+01	2015-11-21 00:15:39.718418+01	student	groupcomment	\N	10
257	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:39.723662+01	2015-11-22 14:15:39.723341+01	examiner	groupcomment	\N	2
258	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:39.800917+01	2015-11-20 14:15:39.800583+01	student	groupcomment	\N	15
259	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:39.80337+01	2015-11-21 01:15:39.803059+01	student	groupcomment	\N	15
260	And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. Hey, you add a one and two zeros to that or we walk! But existing is basically all I do! You can crush me but you can't crush my spirit!	2015-12-15 14:15:39.810925+01	2015-11-20 23:15:39.81059+01	student	groupcomment	\N	15
261	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:39.817968+01	2015-11-21 14:15:39.817624+01	student	groupcomment	\N	15
262	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:39.822755+01	2015-11-21 03:15:39.82241+01	student	groupcomment	\N	15
263	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:39.829732+01	2015-11-22 14:15:39.829399+01	examiner	groupcomment	\N	4
264	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:39.915166+01	2015-11-20 14:15:39.914846+01	student	groupcomment	\N	11
265	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:39.922391+01	2015-11-20 18:15:39.922051+01	student	groupcomment	\N	11
266	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:39.927032+01	2015-11-21 05:15:39.926685+01	student	groupcomment	\N	11
267	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:39.929363+01	2015-11-20 17:15:39.929052+01	student	groupcomment	\N	11
268	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:39.936493+01	2015-11-20 21:15:39.936161+01	student	groupcomment	\N	11
269	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:39.943488+01	2015-11-22 14:15:39.943153+01	examiner	groupcomment	\N	3
270	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:40.009117+01	2015-11-20 14:15:40.008809+01	student	groupcomment	\N	16
271	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:40.014455+01	2015-11-21 00:15:40.014126+01	student	groupcomment	\N	16
272	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:40.01682+01	2015-11-22 14:15:40.016534+01	examiner	groupcomment	\N	3
273	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:40.173378+01	2015-12-04 14:15:40.17305+01	student	groupcomment	\N	5
274	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:40.175978+01	2015-12-05 00:15:40.175658+01	student	groupcomment	\N	5
275	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:40.178651+01	2015-12-05 02:15:40.178232+01	student	groupcomment	\N	5
276	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:40.185688+01	2015-12-06 14:15:40.185362+01	examiner	groupcomment	\N	4
277	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:40.256543+01	2015-12-04 14:15:40.256176+01	student	groupcomment	\N	8
278	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:40.262636+01	2015-12-04 19:15:40.262247+01	student	groupcomment	\N	8
279	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:40.267635+01	2015-12-05 03:15:40.267302+01	student	groupcomment	\N	8
280	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:40.275105+01	2015-12-04 22:15:40.274735+01	student	groupcomment	\N	8
281	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:40.283102+01	2015-12-06 14:15:40.282669+01	examiner	groupcomment	\N	2
282	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:40.358514+01	2015-12-04 14:15:40.35794+01	student	groupcomment	\N	2
283	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:40.365769+01	2015-12-04 17:15:40.365375+01	student	groupcomment	\N	2
284	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:40.371123+01	2015-12-04 17:15:40.370696+01	student	groupcomment	\N	2
285	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:40.379175+01	2015-12-05 07:15:40.378784+01	student	groupcomment	\N	2
286	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:40.386605+01	2015-12-06 14:15:40.386245+01	examiner	groupcomment	\N	2
287	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:40.461991+01	2015-12-04 14:15:40.461582+01	student	groupcomment	\N	9
288	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:40.469836+01	2015-12-05 10:15:40.469483+01	student	groupcomment	\N	9
289	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:40.474601+01	2015-12-04 17:15:40.47426+01	student	groupcomment	\N	9
290	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:40.479639+01	2015-12-06 14:15:40.479279+01	examiner	groupcomment	\N	2
291	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:40.554549+01	2015-12-04 14:15:40.554207+01	student	groupcomment	\N	7
292	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:40.561981+01	2015-12-04 18:15:40.561638+01	student	groupcomment	\N	7
293	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:40.564308+01	2015-12-05 10:15:40.564006+01	student	groupcomment	\N	7
294	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:40.566552+01	2015-12-06 14:15:40.566252+01	examiner	groupcomment	\N	2
295	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:40.645784+01	2015-12-04 14:15:40.645422+01	student	groupcomment	\N	6
296	Maybe I love you so much I love you no matter who you are pretending to be. When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! Oh right. I forgot about the battle. THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN!	2015-12-15 14:15:40.653997+01	2015-12-04 18:15:40.653587+01	student	groupcomment	\N	6
297	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:40.662803+01	2015-12-05 03:15:40.662405+01	student	groupcomment	\N	6
298	Nay, I respect and admire Harold Zoid too much to beat him to death with his own Oscar. I had more, but you go ahead. Hey, whatcha watching?	2015-12-15 14:15:40.669752+01	2015-12-04 20:15:40.669431+01	student	groupcomment	\N	6
299	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:40.671945+01	2015-12-04 17:15:40.671627+01	student	groupcomment	\N	6
300	And yet you haven't said what I told you to say! How can any of us trust you? The key to victory is discipline, and that means a well made bed. You will practice until you can make your bed in your sleep. There, now he's trapped in a book I wrote: a crummy world of plot holes and spelling errors! Morbo can't understand his teleprompter because he forgot how you say that letter that's shaped like a man wearing a hat.	2015-12-15 14:15:40.674271+01	2015-12-06 14:15:40.673928+01	examiner	groupcomment	\N	4
301	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:40.750694+01	2015-12-04 14:15:40.750356+01	student	groupcomment	\N	13
302	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:40.755796+01	2015-12-05 01:15:40.755447+01	student	groupcomment	\N	13
303	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:40.762922+01	2015-12-06 14:15:40.762565+01	examiner	groupcomment	\N	2
304	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:40.852091+01	2015-12-04 14:15:40.851749+01	student	groupcomment	\N	14
305	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:40.854553+01	2015-12-05 10:15:40.854264+01	student	groupcomment	\N	14
306	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:40.856863+01	2015-12-05 13:15:40.856561+01	student	groupcomment	\N	14
307	Is today's hectic lifestyle making you tense and impatient? And so we say goodbye to our beloved pet, Nibbler, who's gone to a place where I, too, hope one day to go. The toilet. All I want is to be a monkey of moderate intelligence who wears a suit... that's why I'm transferring to business school! Can we have Bender Burgers again? Wow! A superpowers drug you can just rub onto your skin? You'd think it would be something you'd have to freebase. Have you ever tried just turning off the TV, sitting down with your children, and hitting them?	2015-12-15 14:15:40.85912+01	2015-12-05 01:15:40.858788+01	student	groupcomment	\N	14
308	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:40.861408+01	2015-12-04 19:15:40.861101+01	student	groupcomment	\N	14
309	Um, is this the boring, peaceful kind of taking to the streets? Man, I'm sore all over. I feel like I just went ten rounds with mighty Thor. Bender! Ship! Stop bickering or I'm going to come back there and change your opinions manually!	2015-12-15 14:15:40.866281+01	2015-12-06 14:15:40.865936+01	examiner	groupcomment	\N	3
310	Oh right. I forgot about the battle. And when we woke up, we had these bodies. Yep, I remember. They came in last at the Olympics, then retired to promote alcoholic beverages!	2015-12-15 14:15:40.926988+01	2015-12-04 14:15:40.92666+01	student	groupcomment	\N	12
311	You lived before you met me?! For one beautiful night I knew what it was like to be a grandmother. Subjugated, yet honored. Is today's hectic lifestyle making you tense and impatient? Good news, everyone! I've taught the toaster to feel love! Bender, you risked your life to save me! Shut up and get to the point!	2015-12-15 14:15:40.934852+01	2015-12-05 10:15:40.934522+01	student	groupcomment	\N	12
312	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:40.937233+01	2015-12-04 17:15:40.9369+01	student	groupcomment	\N	12
313	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:40.939564+01	2015-12-05 07:15:40.939226+01	student	groupcomment	\N	12
314	With a warning label this big, you know they gotta be fun! When I was first asked to make a film about my nephew, Hubert Farnsworth, I thought 'Why should I?' Then later, Leela made the film. But if I did make it, you can bet there would have been more topless women on motorcycles. Roll film! You are the last hope of the universe. I suppose I could part with 'one' and still be feared... I wish! It's a nickel.	2015-12-15 14:15:40.944311+01	2015-12-06 14:15:40.943894+01	examiner	groupcomment	\N	4
316	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:41.031884+01	2015-12-05 10:15:41.031577+01	student	groupcomment	\N	10
317	Alright, let's mafia things up a bit. Joey, burn down the ship. Clamps, burn down the crew. Maybe I love you so much I love you no matter who you are pretending to be. Your best is an idiot! Well, thanks to the Internet, I'm now bored with sex. Is there a place on the web that panders to my lust for violence?	2015-12-15 14:15:41.037195+01	2015-12-05 08:15:41.036855+01	student	groupcomment	\N	10
318	It's toe-tappingly tragic! Come, Comrade Bender! We must take to the streets! Hi, I'm a naughty nurse, and I really need someone to talk to. $9.95 a minute. Bender, you risked your life to save me! I videotape every customer that comes in here, so that I may blackmail them later. Actually, that's still true.	2015-12-15 14:15:41.044433+01	2015-12-06 14:15:41.044081+01	examiner	groupcomment	\N	3
319	No! The kind with looting and maybe starting a few fires! Why not indeed! Kids don't turn rotten just from watching TV.	2015-12-15 14:15:41.109178+01	2015-12-04 14:15:41.108837+01	student	groupcomment	\N	15
320	Is today's hectic lifestyle making you tense and impatient? Hey! I'm a porno-dealing monster, what do I care what you think? For the last time, I don't like lilacs! Your 'first' wife was the one who liked lilacs! Really?! Ah, yes! John Quincy Adding Machine. He struck a chord with the voters when he pledged not to go on a killing spree.	2015-12-15 14:15:41.11153+01	2015-12-05 09:15:41.111231+01	student	groupcomment	\N	15
321	But I know you in the future. I cleaned your poop. Say it in Russian! I don't know what you did, Fry, but once again, you screwed up! Now all the planets are gonna start cracking wise about our mamas. Aww, it's true. I've been hiding it for so long. Check it out, y'all. Everyone who was invited is here. Does anybody else feel jealous and aroused and worried?	2015-12-15 14:15:41.116611+01	2015-12-06 14:15:41.116281+01	examiner	groupcomment	\N	2
322	Well, then good news! It's a suppository. Oh, how awful. Did he at least die painlessly? ...To shreds, you say. Well, how is his wife holding up? ...To shreds, you say. And when we woke up, we had these bodies. Actually, that's still true. And yet you haven't said what I told you to say! How can any of us trust you?	2015-12-15 14:15:41.200939+01	2015-12-04 14:15:41.200601+01	student	groupcomment	\N	11
323	Noooooo! Dr. Zoidberg, that doesn't make sense. But, okay! That's right, baby. I ain't your loverboy Flexo, the guy you love so much. You even love anyone pretending to be him! Now that the, uh, garbage ball is in space, Doctor, perhaps you can help me with my sexual inhibitions? No! The cat shelter's on to me. Eeeee! Now say 'nuclear wessels'!	2015-12-15 14:15:41.20627+01	2015-12-06 14:15:41.205917+01	examiner	groupcomment	\N	2
324	You guys aren't Santa! You're not even robots. How dare you lie in front of Jesus? Shut up and get to the point! You're going back for the Countess, aren't you? Meh.	2015-12-15 14:15:41.270105+01	2015-12-04 14:15:41.269776+01	student	groupcomment	\N	16
325	I had more, but you go ahead. Now Fry, it's been a few years since medical school, so remind me. Disemboweling in your species: fatal or non-fatal? It's just like the story of the grasshopper and the octopus. All year long, the grasshopper kept burying acorns for winter, while the octopus mooched off his girlfriend and watched TV. But then the winter came, and the grasshopper died, and the octopus ate all his acorns. Also he got a race car. Is any of this getting through to you? We're rescuing ya. I'm sorry, guys. I never meant to hurt you. Just to destroy everything you ever believed in. Good news, everyone! There's a report on TV with some very bad news!	2015-12-15 14:15:41.278002+01	2015-12-05 09:15:41.277623+01	student	groupcomment	\N	16
326	So I really am important? How I feel when I'm drunk is correct? Check it out, y'all. Everyone who was invited is here. I'm Santa Claus! Spare me your space age technobabble, Attila the Hun! So, how 'bout them Knicks?	2015-12-15 14:15:41.283218+01	2015-12-05 09:15:41.282814+01	student	groupcomment	\N	16
327	Meh. Say it in Russian! THE BIG BRAIN AM WINNING AGAIN! I AM THE GREETEST! NOW I AM LEAVING EARTH, FOR NO RAISEN! Bender, being God isn't easy. If you do too much, people get dependent on you, and if you do nothing, they lose hope. You have to use a light touch. Like a safecracker, or a pickpocket. Is that a cooking show?	2015-12-15 14:15:41.29073+01	2015-12-06 14:15:41.29035+01	examiner	groupcomment	\N	3
328	I don't know how to solve this, can't I just use my private army?	2015-12-15 14:15:43.998888+01	2015-11-29 14:15:43.998417+01	student	groupcomment	\N	17
329	No no no, you're here to learn how to get domination using information technology. Later you will learn to use automate your abilities by programming them.	2015-12-15 14:15:44.001905+01	2015-11-29 14:15:44.001465+01	examiner	groupcomment	\N	18
330	Here my assignment! I think I have a great solution! =D	2015-12-15 14:15:44.004879+01	2015-11-30 13:15:44.004431+01	student	groupcomment	\N	17
331	Wuups! Forgot this file!	2015-12-15 14:15:44.011284+01	2015-12-03 11:15:44.010838+01	student	groupcomment	\N	17
332	You failed miserably! Try to actually understand the problem. Printing 'hello world, I own you now' everywhere won't get you anywhere!	2015-12-15 14:15:44.016756+01	2015-12-03 12:15:43.99691+01	examiner	groupcomment	\N	18
333	Noooooooo! New try pls?	2015-12-15 14:15:44.021572+01	2015-12-03 15:15:44.021219+01	student	groupcomment	\N	17
334	Ok, I'll give you a second try!	2015-12-15 14:15:44.023782+01	2015-12-03 16:15:44.023474+01	examiner	groupcomment	\N	18
335	Thanks!	2015-12-15 14:15:44.027314+01	2015-12-03 20:15:44.026951+01	student	groupcomment	\N	17
336	Do you like cashew nuts?	2015-12-15 14:15:44.029649+01	2015-12-03 22:15:44.029336+01	student	groupcomment	\N	17
337	Stay on topic please... But, yes...	2015-12-15 14:15:44.031788+01	2015-12-05 14:15:44.031486+01	examiner	groupcomment	\N	18
338	Here we go again!	2015-12-15 14:15:44.034035+01	2015-12-06 14:15:44.033695+01	student	groupcomment	\N	17
339	Great job! You must be the most evil mutant I have ever met! Keep going like this, and you'll own the entire planet in no time!	2015-12-15 14:15:44.041596+01	2015-12-12 14:15:44.025585+01	examiner	groupcomment	\N	18
340	Thanks! Sorry for the first delivery, I was so hungover when I worked on that!	2015-12-15 14:15:44.0465+01	2015-12-13 14:15:44.04614+01	student	groupcomment	\N	17
\.


--
-- Name: devilry_comment_comment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_comment_id_seq', 340, true);


--
-- Data for Name: devilry_comment_commentfile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_comment_commentfile (id, mimetype, file, filename, filesize, processing_started_datetime, processing_completed_datetime, processing_successful, comment_id) FROM stdin;
1		devilry_comment/3/1	DesignDocumentForObligN.pdf	10	\N	\N	f	3
2		devilry_comment/3/2	ObligN.py	16	\N	\N	f	3
3		devilry_comment/4/3	ObligNDelivery.py	12	\N	\N	f	4
4		devilry_comment/4/4_9eY9yGi	ObligN.py	16	\N	\N	f	4
5		devilry_comment/5/5_1Pih3z6	ObligN.py	16	\N	\N	f	5
6		devilry_comment/5/6	DesignDocumentForObligN.pdf	10	\N	\N	f	5
7		devilry_comment/6/7	ObligNDelivery.py	12	\N	\N	f	6
8		devilry_comment/7/8_g6Fzt3l	ObligN.py	16	\N	\N	f	7
9		devilry_comment/8/9_Z7HU6l5	DesignDocumentForObligN.pdf	10	\N	\N	f	8
10		devilry_comment/8/10_UoFjwyb	ObligNDelivery.py	12	\N	\N	f	8
11		devilry_comment/12/11_NOJvsLw	DesignDocumentForObligN.pdf	10	\N	\N	f	12
12		devilry_comment/12/12_fYJzRh7	ObligN.py	16	\N	\N	f	12
13		devilry_comment/13/13	ObligNDelivery.py	12	\N	\N	f	13
14		devilry_comment/13/14	DesignDocumentForObligN.pdf	10	\N	\N	f	13
15		devilry_comment/14/15	ObligNDelivery.py	12	\N	\N	f	14
16		devilry_comment/15/16	ObligN.py	16	\N	\N	f	15
17		devilry_comment/15/17	DesignDocumentForObligN.pdf	10	\N	\N	f	15
18		devilry_comment/16/18	DesignDocumentForObligN.pdf	10	\N	\N	f	16
19		devilry_comment/18/19	DesignDocumentForObligN.pdf	10	\N	\N	f	18
20		devilry_comment/19/20_LCWs1OY	ObligN.py	16	\N	\N	f	19
21		devilry_comment/19/21	DesignDocumentForObligN.pdf	10	\N	\N	f	19
22		devilry_comment/20/22	ObligNDelivery.py	12	\N	\N	f	20
23		devilry_comment/20/23	DesignDocumentForObligN.pdf	10	\N	\N	f	20
24		devilry_comment/21/24	ObligN.py	16	\N	\N	f	21
25		devilry_comment/22/25_qRcsS6w	ObligN.py	16	\N	\N	f	22
26		devilry_comment/22/26	ObligNDelivery.py	12	\N	\N	f	22
27		devilry_comment/25/27_Jgv0kjO	ObligN.py	16	\N	\N	f	25
28		devilry_comment/25/28_GVoJixJ	DesignDocumentForObligN.pdf	10	\N	\N	f	25
29		devilry_comment/26/29_nfQxnL0	ObligN.py	16	\N	\N	f	26
30		devilry_comment/27/30	ObligN.py	16	\N	\N	f	27
31		devilry_comment/27/31_5wNKN54	ObligNDelivery.py	12	\N	\N	f	27
32		devilry_comment/28/32_RrM9OnD	ObligNDelivery.py	12	\N	\N	f	28
33		devilry_comment/28/33_XdkdYVk	DesignDocumentForObligN.pdf	10	\N	\N	f	28
34		devilry_comment/31/34	ObligNDelivery.py	12	\N	\N	f	31
35		devilry_comment/31/35_NnwZw7v	DesignDocumentForObligN.pdf	10	\N	\N	f	31
36		devilry_comment/34/36	ObligNDelivery.py	12	\N	\N	f	34
37		devilry_comment/35/37	ObligN.py	16	\N	\N	f	35
38		devilry_comment/35/38_IgAVHcb	ObligNDelivery.py	12	\N	\N	f	35
39		devilry_comment/36/39_hpcPuQo	DesignDocumentForObligN.pdf	10	\N	\N	f	36
40		devilry_comment/39/40_UBr1IlN	ObligNDelivery.py	12	\N	\N	f	39
41		devilry_comment/41/41_zwecOhd	ObligN.py	16	\N	\N	f	41
42		devilry_comment/41/42_cHSkJ6E	ObligNDelivery.py	12	\N	\N	f	41
43		devilry_comment/44/43	DesignDocumentForObligN.pdf	10	\N	\N	f	44
44		devilry_comment/44/44	ObligN.py	16	\N	\N	f	44
45		devilry_comment/45/45	ObligN.py	16	\N	\N	f	45
46		devilry_comment/46/46	ObligN.py	16	\N	\N	f	46
47		devilry_comment/46/47	ObligNDelivery.py	12	\N	\N	f	46
48		devilry_comment/47/48	ObligN.py	16	\N	\N	f	47
49		devilry_comment/48/49	ObligN.py	16	\N	\N	f	48
50		devilry_comment/48/50	DesignDocumentForObligN.pdf	10	\N	\N	f	48
51		devilry_comment/50/51_eA3fSVc	ObligN.py	16	\N	\N	f	50
52		devilry_comment/51/52	ObligNDelivery.py	12	\N	\N	f	51
53		devilry_comment/51/53	DesignDocumentForObligN.pdf	10	\N	\N	f	51
54		devilry_comment/53/54	ObligN.py	16	\N	\N	f	53
55		devilry_comment/55/55_5lbKwqD	DesignDocumentForObligN.pdf	10	\N	\N	f	55
56		devilry_comment/56/56	ObligN.py	16	\N	\N	f	56
57		devilry_comment/56/57_wS18urP	DesignDocumentForObligN.pdf	10	\N	\N	f	56
58		devilry_comment/57/58	ObligNDelivery.py	12	\N	\N	f	57
59		devilry_comment/57/59	DesignDocumentForObligN.pdf	10	\N	\N	f	57
60		devilry_comment/59/60	ObligN.py	16	\N	\N	f	59
61		devilry_comment/59/61_G6w1gIA	DesignDocumentForObligN.pdf	10	\N	\N	f	59
62		devilry_comment/62/62	ObligNDelivery.py	12	\N	\N	f	62
63		devilry_comment/62/63_MZqu4h7	DesignDocumentForObligN.pdf	10	\N	\N	f	62
64		devilry_comment/63/64	DesignDocumentForObligN.pdf	10	\N	\N	f	63
65		devilry_comment/63/65	ObligNDelivery.py	12	\N	\N	f	63
66		devilry_comment/64/66_wv1M44n	DesignDocumentForObligN.pdf	10	\N	\N	f	64
67		devilry_comment/65/67	ObligNDelivery.py	12	\N	\N	f	65
68		devilry_comment/65/68	ObligN.py	16	\N	\N	f	65
69		devilry_comment/67/69_wRS4qBL	ObligNDelivery.py	12	\N	\N	f	67
70		devilry_comment/67/70	DesignDocumentForObligN.pdf	10	\N	\N	f	67
71		devilry_comment/68/71	ObligN.py	16	\N	\N	f	68
72		devilry_comment/70/72	ObligNDelivery.py	12	\N	\N	f	70
73		devilry_comment/71/73	ObligNDelivery.py	12	\N	\N	f	71
74		devilry_comment/71/74	DesignDocumentForObligN.pdf	10	\N	\N	f	71
75		devilry_comment/72/75	ObligN.py	16	\N	\N	f	72
76		devilry_comment/72/76	DesignDocumentForObligN.pdf	10	\N	\N	f	72
77		devilry_comment/73/77	ObligNDelivery.py	12	\N	\N	f	73
78		devilry_comment/74/78	DesignDocumentForObligN.pdf	10	\N	\N	f	74
79		devilry_comment/75/79	ObligN.py	16	\N	\N	f	75
80		devilry_comment/75/80	ObligNDelivery.py	12	\N	\N	f	75
81		devilry_comment/76/81	DesignDocumentForObligN.pdf	10	\N	\N	f	76
82		devilry_comment/77/82	ObligNDelivery.py	12	\N	\N	f	77
83		devilry_comment/79/83	ObligNDelivery.py	12	\N	\N	f	79
84		devilry_comment/80/84	DesignDocumentForObligN.pdf	10	\N	\N	f	80
85		devilry_comment/80/85	ObligN.py	16	\N	\N	f	80
86		devilry_comment/81/86	DesignDocumentForObligN.pdf	10	\N	\N	f	81
87		devilry_comment/81/87	ObligNDelivery.py	12	\N	\N	f	81
88		devilry_comment/82/88	DesignDocumentForObligN.pdf	10	\N	\N	f	82
89		devilry_comment/82/89	ObligN.py	16	\N	\N	f	82
90		devilry_comment/83/90	ObligN.py	16	\N	\N	f	83
91		devilry_comment/83/91	DesignDocumentForObligN.pdf	10	\N	\N	f	83
92		devilry_comment/84/92	ObligN.py	16	\N	\N	f	84
93		devilry_comment/85/93	ObligN.py	16	\N	\N	f	85
94		devilry_comment/86/94	ObligNDelivery.py	12	\N	\N	f	86
95		devilry_comment/87/95	DesignDocumentForObligN.pdf	10	\N	\N	f	87
96		devilry_comment/89/96	ObligNDelivery.py	12	\N	\N	f	89
97		devilry_comment/90/97	ObligN.py	16	\N	\N	f	90
98		devilry_comment/91/98	DesignDocumentForObligN.pdf	10	\N	\N	f	91
99		devilry_comment/92/99	ObligNDelivery.py	12	\N	\N	f	92
100		devilry_comment/92/100	DesignDocumentForObligN.pdf	10	\N	\N	f	92
101		devilry_comment/94/101	DesignDocumentForObligN.pdf	10	\N	\N	f	94
102		devilry_comment/94/102	ObligN.py	16	\N	\N	f	94
103		devilry_comment/95/103	ObligN.py	16	\N	\N	f	95
104		devilry_comment/95/104	DesignDocumentForObligN.pdf	10	\N	\N	f	95
105		devilry_comment/96/105	DesignDocumentForObligN.pdf	10	\N	\N	f	96
106		devilry_comment/98/106	DesignDocumentForObligN.pdf	10	\N	\N	f	98
107		devilry_comment/98/107	ObligN.py	16	\N	\N	f	98
108		devilry_comment/99/108	DesignDocumentForObligN.pdf	10	\N	\N	f	99
109		devilry_comment/101/109	ObligN.py	16	\N	\N	f	101
110		devilry_comment/101/110	ObligNDelivery.py	12	\N	\N	f	101
111		devilry_comment/102/111	ObligN.py	16	\N	\N	f	102
112		devilry_comment/103/112	ObligNDelivery.py	12	\N	\N	f	103
113		devilry_comment/104/113	ObligNDelivery.py	12	\N	\N	f	104
114		devilry_comment/105/114	ObligNDelivery.py	12	\N	\N	f	105
115		devilry_comment/107/115	DesignDocumentForObligN.pdf	10	\N	\N	f	107
116		devilry_comment/108/116	ObligN.py	16	\N	\N	f	108
117		devilry_comment/108/117	DesignDocumentForObligN.pdf	10	\N	\N	f	108
118		devilry_comment/109/118	ObligN.py	16	\N	\N	f	109
119		devilry_comment/112/119	ObligNDelivery.py	12	\N	\N	f	112
120		devilry_comment/112/120	DesignDocumentForObligN.pdf	10	\N	\N	f	112
121		devilry_comment/114/121_RDLV96q	ObligNDelivery.py	12	\N	\N	f	114
122		devilry_comment/115/122	ObligN.py	16	\N	\N	f	115
123		devilry_comment/115/123	DesignDocumentForObligN.pdf	10	\N	\N	f	115
124		devilry_comment/116/124	DesignDocumentForObligN.pdf	10	\N	\N	f	116
125		devilry_comment/119/125	ObligNDelivery.py	12	\N	\N	f	119
126		devilry_comment/120/126_Q9EzROb	DesignDocumentForObligN.pdf	10	\N	\N	f	120
127		devilry_comment/120/127	ObligN.py	16	\N	\N	f	120
128		devilry_comment/121/128_62H4BiR	DesignDocumentForObligN.pdf	10	\N	\N	f	121
129		devilry_comment/121/129	ObligN.py	16	\N	\N	f	121
130		devilry_comment/122/130	ObligN.py	16	\N	\N	f	122
131		devilry_comment/123/131	DesignDocumentForObligN.pdf	10	\N	\N	f	123
132		devilry_comment/123/132	ObligNDelivery.py	12	\N	\N	f	123
133		devilry_comment/124/133	ObligN.py	16	\N	\N	f	124
134		devilry_comment/125/134	DesignDocumentForObligN.pdf	10	\N	\N	f	125
135		devilry_comment/126/135	ObligN.py	16	\N	\N	f	126
136		devilry_comment/127/136	DesignDocumentForObligN.pdf	10	\N	\N	f	127
137		devilry_comment/128/137	ObligN.py	16	\N	\N	f	128
138		devilry_comment/128/138	ObligNDelivery.py	12	\N	\N	f	128
139		devilry_comment/130/139	ObligNDelivery.py	12	\N	\N	f	130
140		devilry_comment/130/140	ObligN.py	16	\N	\N	f	130
141		devilry_comment/131/141	ObligN.py	16	\N	\N	f	131
142		devilry_comment/133/142	ObligN.py	16	\N	\N	f	133
143		devilry_comment/135/143	DesignDocumentForObligN.pdf	10	\N	\N	f	135
144		devilry_comment/135/144	ObligN.py	16	\N	\N	f	135
145		devilry_comment/136/145	ObligNDelivery.py	12	\N	\N	f	136
146		devilry_comment/137/146	DesignDocumentForObligN.pdf	10	\N	\N	f	137
147		devilry_comment/138/147	ObligNDelivery.py	12	\N	\N	f	138
148		devilry_comment/139/148	ObligNDelivery.py	12	\N	\N	f	139
149		devilry_comment/140/149	ObligN.py	16	\N	\N	f	140
150		devilry_comment/141/150	ObligN.py	16	\N	\N	f	141
151		devilry_comment/141/151	DesignDocumentForObligN.pdf	10	\N	\N	f	141
152		devilry_comment/142/152	ObligN.py	16	\N	\N	f	142
153		devilry_comment/142/153	DesignDocumentForObligN.pdf	10	\N	\N	f	142
154		devilry_comment/143/154	ObligNDelivery.py	12	\N	\N	f	143
155		devilry_comment/144/155	DesignDocumentForObligN.pdf	10	\N	\N	f	144
156		devilry_comment/145/156	ObligNDelivery.py	12	\N	\N	f	145
157		devilry_comment/146/157	ObligN.py	16	\N	\N	f	146
158		devilry_comment/147/158	ObligN.py	16	\N	\N	f	147
159		devilry_comment/148/159	ObligNDelivery.py	12	\N	\N	f	148
160		devilry_comment/148/160	DesignDocumentForObligN.pdf	10	\N	\N	f	148
161		devilry_comment/151/161	DesignDocumentForObligN.pdf	10	\N	\N	f	151
162		devilry_comment/152/162	ObligN.py	16	\N	\N	f	152
163		devilry_comment/152/163	ObligNDelivery.py	12	\N	\N	f	152
164		devilry_comment/153/164	ObligN.py	16	\N	\N	f	153
165		devilry_comment/155/165	DesignDocumentForObligN.pdf	10	\N	\N	f	155
166		devilry_comment/156/166	DesignDocumentForObligN.pdf	10	\N	\N	f	156
167		devilry_comment/159/167	ObligNDelivery.py	12	\N	\N	f	159
168		devilry_comment/162/168_kmEO8wy	ObligN.py	16	\N	\N	f	162
169		devilry_comment/162/169	DesignDocumentForObligN.pdf	10	\N	\N	f	162
170		devilry_comment/164/170	DesignDocumentForObligN.pdf	10	\N	\N	f	164
171		devilry_comment/164/171_tO9GRzT	ObligN.py	16	\N	\N	f	164
172		devilry_comment/165/172	ObligN.py	16	\N	\N	f	165
173		devilry_comment/167/173	ObligNDelivery.py	12	\N	\N	f	167
174		devilry_comment/169/174	ObligNDelivery.py	12	\N	\N	f	169
175		devilry_comment/170/175	ObligNDelivery.py	12	\N	\N	f	170
176		devilry_comment/171/176	ObligNDelivery.py	12	\N	\N	f	171
177		devilry_comment/172/177	ObligN.py	16	\N	\N	f	172
178		devilry_comment/173/178	ObligNDelivery.py	12	\N	\N	f	173
179		devilry_comment/173/179	ObligN.py	16	\N	\N	f	173
180		devilry_comment/175/180	ObligNDelivery.py	12	\N	\N	f	175
181		devilry_comment/177/181	ObligN.py	16	\N	\N	f	177
182		devilry_comment/180/182_AqlbonF	ObligNDelivery.py	12	\N	\N	f	180
183		devilry_comment/181/183	DesignDocumentForObligN.pdf	10	\N	\N	f	181
184		devilry_comment/182/184	ObligNDelivery.py	12	\N	\N	f	182
185		devilry_comment/182/185	DesignDocumentForObligN.pdf	10	\N	\N	f	182
186		devilry_comment/183/186	DesignDocumentForObligN.pdf	10	\N	\N	f	183
187		devilry_comment/183/187_pXywgtD	ObligNDelivery.py	12	\N	\N	f	183
188		devilry_comment/185/188	DesignDocumentForObligN.pdf	10	\N	\N	f	185
189		devilry_comment/185/189	ObligN.py	16	\N	\N	f	185
190		devilry_comment/186/190	ObligNDelivery.py	12	\N	\N	f	186
191		devilry_comment/186/191_ZZ0npXd	DesignDocumentForObligN.pdf	10	\N	\N	f	186
192		devilry_comment/187/192_3VZDqvV	DesignDocumentForObligN.pdf	10	\N	\N	f	187
193		devilry_comment/187/193	ObligNDelivery.py	12	\N	\N	f	187
194		devilry_comment/189/194	DesignDocumentForObligN.pdf	10	\N	\N	f	189
195		devilry_comment/189/195	ObligN.py	16	\N	\N	f	189
196		devilry_comment/190/196	ObligNDelivery.py	12	\N	\N	f	190
197		devilry_comment/191/197	ObligN.py	16	\N	\N	f	191
198		devilry_comment/191/198	ObligNDelivery.py	12	\N	\N	f	191
199		devilry_comment/195/199	DesignDocumentForObligN.pdf	10	\N	\N	f	195
200		devilry_comment/196/200	ObligNDelivery.py	12	\N	\N	f	196
201		devilry_comment/197/201	ObligN.py	16	\N	\N	f	197
202		devilry_comment/198/202	DesignDocumentForObligN.pdf	10	\N	\N	f	198
203		devilry_comment/198/203_VLyOIXc	ObligN.py	16	\N	\N	f	198
204		devilry_comment/200/204_rPKKcFD	ObligNDelivery.py	12	\N	\N	f	200
205		devilry_comment/200/205_IuXMv7Z	ObligN.py	16	\N	\N	f	200
206		devilry_comment/201/206_jjcdjaC	ObligNDelivery.py	12	\N	\N	f	201
207		devilry_comment/202/207_QQbAxMP	ObligN.py	16	\N	\N	f	202
208		devilry_comment/202/208	ObligNDelivery.py	12	\N	\N	f	202
209		devilry_comment/203/209_UU7SWmY	DesignDocumentForObligN.pdf	10	\N	\N	f	203
210		devilry_comment/203/210	ObligN.py	16	\N	\N	f	203
211		devilry_comment/205/211_fqYUajX	ObligN.py	16	\N	\N	f	205
212		devilry_comment/207/212	ObligN.py	16	\N	\N	f	207
213		devilry_comment/209/213	ObligN.py	16	\N	\N	f	209
214		devilry_comment/209/214	DesignDocumentForObligN.pdf	10	\N	\N	f	209
215		devilry_comment/210/215	ObligN.py	16	\N	\N	f	210
216		devilry_comment/210/216	ObligNDelivery.py	12	\N	\N	f	210
217		devilry_comment/211/217	ObligN.py	16	\N	\N	f	211
218		devilry_comment/213/218	DesignDocumentForObligN.pdf	10	\N	\N	f	213
219		devilry_comment/213/219_NhUVTyv	ObligN.py	16	\N	\N	f	213
220		devilry_comment/215/220_8VyU7SM	ObligNDelivery.py	12	\N	\N	f	215
221		devilry_comment/215/221	ObligN.py	16	\N	\N	f	215
222		devilry_comment/216/222	ObligNDelivery.py	12	\N	\N	f	216
223		devilry_comment/217/223	ObligNDelivery.py	12	\N	\N	f	217
224		devilry_comment/217/224	DesignDocumentForObligN.pdf	10	\N	\N	f	217
225		devilry_comment/218/225	ObligNDelivery.py	12	\N	\N	f	218
226		devilry_comment/218/226	ObligN.py	16	\N	\N	f	218
227		devilry_comment/219/227	ObligNDelivery.py	12	\N	\N	f	219
228		devilry_comment/220/228	ObligN.py	16	\N	\N	f	220
229		devilry_comment/220/229	ObligNDelivery.py	12	\N	\N	f	220
230		devilry_comment/223/230	ObligNDelivery.py	12	\N	\N	f	223
231		devilry_comment/227/231	ObligN.py	16	\N	\N	f	227
232		devilry_comment/228/232	ObligN.py	16	\N	\N	f	228
233		devilry_comment/228/233	DesignDocumentForObligN.pdf	10	\N	\N	f	228
234		devilry_comment/229/234	DesignDocumentForObligN.pdf	10	\N	\N	f	229
235		devilry_comment/229/235	ObligN.py	16	\N	\N	f	229
236		devilry_comment/232/236	DesignDocumentForObligN.pdf	10	\N	\N	f	232
237		devilry_comment/232/237	ObligNDelivery.py	12	\N	\N	f	232
238		devilry_comment/235/238	ObligN.py	16	\N	\N	f	235
239		devilry_comment/236/239	ObligNDelivery.py	12	\N	\N	f	236
240		devilry_comment/237/240	ObligNDelivery.py	12	\N	\N	f	237
241		devilry_comment/237/241	DesignDocumentForObligN.pdf	10	\N	\N	f	237
242		devilry_comment/241/242	DesignDocumentForObligN.pdf	10	\N	\N	f	241
243		devilry_comment/241/243_7Gn03D1	ObligN.py	16	\N	\N	f	241
244		devilry_comment/242/244	ObligNDelivery.py	12	\N	\N	f	242
245		devilry_comment/244/245	DesignDocumentForObligN.pdf	10	\N	\N	f	244
246		devilry_comment/245/246	ObligNDelivery.py	12	\N	\N	f	245
247		devilry_comment/245/247	ObligN.py	16	\N	\N	f	245
248		devilry_comment/246/248	DesignDocumentForObligN.pdf	10	\N	\N	f	246
249		devilry_comment/246/249	ObligN.py	16	\N	\N	f	246
250		devilry_comment/247/250	ObligNDelivery.py	12	\N	\N	f	247
251		devilry_comment/247/251_LgPjlKg	ObligN.py	16	\N	\N	f	247
252		devilry_comment/248/252	DesignDocumentForObligN.pdf	10	\N	\N	f	248
253		devilry_comment/249/253_13ZwgL4	ObligNDelivery.py	12	\N	\N	f	249
254		devilry_comment/250/254	DesignDocumentForObligN.pdf	10	\N	\N	f	250
255		devilry_comment/251/255_mWWUxWf	ObligN.py	16	\N	\N	f	251
256		devilry_comment/251/256_uihPhXf	DesignDocumentForObligN.pdf	10	\N	\N	f	251
257		devilry_comment/252/257_yvw8Shd	ObligN.py	16	\N	\N	f	252
258		devilry_comment/252/258_39hdlxW	DesignDocumentForObligN.pdf	10	\N	\N	f	252
259		devilry_comment/253/259_Ltv0Rpl	DesignDocumentForObligN.pdf	10	\N	\N	f	253
260		devilry_comment/256/260	ObligNDelivery.py	12	\N	\N	f	256
261		devilry_comment/257/261	DesignDocumentForObligN.pdf	10	\N	\N	f	257
262		devilry_comment/259/262	ObligN.py	16	\N	\N	f	259
263		devilry_comment/259/263	DesignDocumentForObligN.pdf	10	\N	\N	f	259
264		devilry_comment/260/264	ObligNDelivery.py	12	\N	\N	f	260
265		devilry_comment/260/265	ObligN.py	16	\N	\N	f	260
266		devilry_comment/261/266	ObligN.py	16	\N	\N	f	261
267		devilry_comment/262/267	ObligN.py	16	\N	\N	f	262
268		devilry_comment/262/268_aRgueAL	ObligNDelivery.py	12	\N	\N	f	262
269		devilry_comment/263/269	ObligN.py	16	\N	\N	f	263
270		devilry_comment/263/270_XdxkI0H	DesignDocumentForObligN.pdf	10	\N	\N	f	263
271		devilry_comment/264/271	ObligN.py	16	\N	\N	f	264
272		devilry_comment/264/272	DesignDocumentForObligN.pdf	10	\N	\N	f	264
273		devilry_comment/265/273	ObligNDelivery.py	12	\N	\N	f	265
274		devilry_comment/267/274	ObligN.py	16	\N	\N	f	267
275		devilry_comment/267/275	DesignDocumentForObligN.pdf	10	\N	\N	f	267
276		devilry_comment/268/276	DesignDocumentForObligN.pdf	10	\N	\N	f	268
277		devilry_comment/268/277	ObligNDelivery.py	12	\N	\N	f	268
278		devilry_comment/269/278	ObligN.py	16	\N	\N	f	269
279		devilry_comment/270/279	ObligNDelivery.py	12	\N	\N	f	270
280		devilry_comment/272/280_WZm3JuW	ObligNDelivery.py	12	\N	\N	f	272
281		devilry_comment/275/281	ObligN.py	16	\N	\N	f	275
282		devilry_comment/275/282	DesignDocumentForObligN.pdf	10	\N	\N	f	275
283		devilry_comment/276/283	ObligNDelivery.py	12	\N	\N	f	276
284		devilry_comment/276/284_cvWOc9s	ObligN.py	16	\N	\N	f	276
285		devilry_comment/277/285	ObligN.py	16	\N	\N	f	277
286		devilry_comment/278/286	DesignDocumentForObligN.pdf	10	\N	\N	f	278
287		devilry_comment/279/287	ObligNDelivery.py	12	\N	\N	f	279
288		devilry_comment/279/288	DesignDocumentForObligN.pdf	10	\N	\N	f	279
289		devilry_comment/280/289	ObligN.py	16	\N	\N	f	280
290		devilry_comment/280/290	DesignDocumentForObligN.pdf	10	\N	\N	f	280
291		devilry_comment/281/291	DesignDocumentForObligN.pdf	10	\N	\N	f	281
292		devilry_comment/282/292	ObligNDelivery.py	12	\N	\N	f	282
293		devilry_comment/282/293	ObligN.py	16	\N	\N	f	282
294		devilry_comment/283/294_lyPAA0S	ObligN.py	16	\N	\N	f	283
295		devilry_comment/284/295_zbpwFFr	DesignDocumentForObligN.pdf	10	\N	\N	f	284
296		devilry_comment/284/296	ObligN.py	16	\N	\N	f	284
297		devilry_comment/285/297	ObligN.py	16	\N	\N	f	285
298		devilry_comment/285/298	DesignDocumentForObligN.pdf	10	\N	\N	f	285
299		devilry_comment/286/299	ObligNDelivery.py	12	\N	\N	f	286
300		devilry_comment/286/300	ObligN.py	16	\N	\N	f	286
301		devilry_comment/287/301	DesignDocumentForObligN.pdf	10	\N	\N	f	287
302		devilry_comment/287/302	ObligNDelivery.py	12	\N	\N	f	287
303		devilry_comment/288/303	ObligNDelivery.py	12	\N	\N	f	288
304		devilry_comment/289/304	ObligN.py	16	\N	\N	f	289
305		devilry_comment/290/305	ObligNDelivery.py	12	\N	\N	f	290
306		devilry_comment/291/306	ObligNDelivery.py	12	\N	\N	f	291
307		devilry_comment/291/307	ObligN.py	16	\N	\N	f	291
308		devilry_comment/294/308	DesignDocumentForObligN.pdf	10	\N	\N	f	294
309		devilry_comment/295/309	ObligNDelivery.py	12	\N	\N	f	295
310		devilry_comment/295/310	DesignDocumentForObligN.pdf	10	\N	\N	f	295
311		devilry_comment/296/311	ObligN.py	16	\N	\N	f	296
312		devilry_comment/296/312	ObligNDelivery.py	12	\N	\N	f	296
313		devilry_comment/297/313	ObligN.py	16	\N	\N	f	297
314		devilry_comment/297/314	ObligNDelivery.py	12	\N	\N	f	297
315		devilry_comment/301/315	ObligNDelivery.py	12	\N	\N	f	301
316		devilry_comment/302/316	DesignDocumentForObligN.pdf	10	\N	\N	f	302
317		devilry_comment/302/317	ObligN.py	16	\N	\N	f	302
318		devilry_comment/303/318	DesignDocumentForObligN.pdf	10	\N	\N	f	303
319		devilry_comment/308/319	DesignDocumentForObligN.pdf	10	\N	\N	f	308
320		devilry_comment/310/320_HRIbyHl	ObligN.py	16	\N	\N	f	310
321		devilry_comment/310/321	DesignDocumentForObligN.pdf	10	\N	\N	f	310
322		devilry_comment/313/322	ObligN.py	16	\N	\N	f	313
323		devilry_comment/316/323	DesignDocumentForObligN.pdf	10	\N	\N	f	316
324		devilry_comment/317/324	ObligNDelivery.py	12	\N	\N	f	317
325		devilry_comment/317/325	DesignDocumentForObligN.pdf	10	\N	\N	f	317
326		devilry_comment/318/326_CetsyqJ	DesignDocumentForObligN.pdf	10	\N	\N	f	318
327		devilry_comment/320/327	DesignDocumentForObligN.pdf	10	\N	\N	f	320
328		devilry_comment/322/328	ObligNDelivery.py	12	\N	\N	f	322
329		devilry_comment/323/329	DesignDocumentForObligN.pdf	10	\N	\N	f	323
330		devilry_comment/324/330	ObligNDelivery.py	12	\N	\N	f	324
331		devilry_comment/324/331	ObligN.py	16	\N	\N	f	324
332		devilry_comment/325/332	DesignDocumentForObligN.pdf	10	\N	\N	f	325
333		devilry_comment/326/333	ObligN.py	16	\N	\N	f	326
334		devilry_comment/326/334	DesignDocumentForObligN.pdf	10	\N	\N	f	326
335		devilry_comment/327/335	ObligN.py	16	\N	\N	f	327
336		devilry_comment/330/336	ObligNDelivery.py	12	\N	\N	f	330
337		devilry_comment/331/337	DesignDocumentForObligN.pdf	10	\N	\N	f	331
338		devilry_comment/332/338	DesignDocumentForObligN.pdf	10	\N	\N	f	332
339		devilry_comment/338/339	ObligNDelivery.py	12	\N	\N	f	338
340		devilry_comment/338/340	DesignDocumentForObligN.pdf	10	\N	\N	f	338
341		devilry_comment/339/341	ObligN.py	16	\N	\N	f	339
\.


--
-- Name: devilry_comment_commentfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_commentfile_id_seq', 341, true);


--
-- Data for Name: devilry_comment_commentfileimage; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_comment_commentfileimage (id, image, image_width, image_height, thumbnail, thumbnail_width, thumbnail_height, comment_file_id) FROM stdin;
\.


--
-- Name: devilry_comment_commentfileimage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_commentfileimage_id_seq', 1, false);


--
-- Data for Name: devilry_detektor_comparetwocacheitem; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_detektor_comparetwocacheitem (id, scaled_points, summary_json, language_id, parseresult1_id, parseresult2_id) FROM stdin;
\.


--
-- Name: devilry_detektor_comparetwocacheitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_detektor_comparetwocacheitem_id_seq', 1, false);


--
-- Data for Name: devilry_detektor_detektorassignment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_detektor_detektorassignment (id, status, processing_started_datetime, assignment_id, processing_started_by_id) FROM stdin;
\.


--
-- Name: devilry_detektor_detektorassignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_detektor_detektorassignment_id_seq', 1, false);


--
-- Data for Name: devilry_detektor_detektorassignmentcachelanguage; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_detektor_detektorassignmentcachelanguage (id, language, detektorassignment_id) FROM stdin;
\.


--
-- Name: devilry_detektor_detektorassignmentcachelanguage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_detektor_detektorassignmentcachelanguage_id_seq', 1, false);


--
-- Data for Name: devilry_detektor_detektordeliveryparseresult; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_detektor_detektordeliveryparseresult (id, language, operators_string, keywords_string, number_of_operators, number_of_keywords, operators_and_keywords_string, normalized_sourcecode, parsed_functions_json, delivery_id, detektorassignment_id) FROM stdin;
\.


--
-- Name: devilry_detektor_detektordeliveryparseresult_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_detektor_detektordeliveryparseresult_id_seq', 1, false);


--
-- Data for Name: devilry_gradingsystem_feedbackdraft; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_gradingsystem_feedbackdraft (id, feedbacktext_editor, feedbacktext_raw, feedbacktext_html, points, published, save_timestamp, delivery_id, saved_by_id, staticfeedback_id) FROM stdin;
\.


--
-- Name: devilry_gradingsystem_feedbackdraft_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_gradingsystem_feedbackdraft_id_seq', 1, false);


--
-- Data for Name: devilry_gradingsystem_feedbackdraftfile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_gradingsystem_feedbackdraftfile (id, filename, file, delivery_id, saved_by_id) FROM stdin;
\.


--
-- Name: devilry_gradingsystem_feedbackdraftfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_gradingsystem_feedbackdraftfile_id_seq', 1, false);


--
-- Data for Name: devilry_group_feedbackset; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_feedbackset (id, points, created_datetime, published_datetime, deadline_datetime, created_by_id, group_id, published_by_id) FROM stdin;
1	0	2015-12-15 14:15:33.543783+01	\N	2014-12-16 14:15:33.543549+01	3	66	3
2	1	2015-12-15 14:15:33.644399+01	\N	2014-12-16 14:15:33.644222+01	2	67	2
3	0	2015-12-15 14:15:33.728534+01	\N	2014-12-16 14:15:33.728338+01	2	68	2
4	1	2015-12-15 14:15:33.874703+01	\N	2014-12-16 14:15:33.874527+01	4	69	4
5	1	2015-12-15 14:15:33.953119+01	\N	2014-12-16 14:15:33.952937+01	3	70	3
6	0	2015-12-15 14:15:34.05601+01	\N	2014-12-16 14:15:34.05582+01	3	71	3
7	2	2015-12-15 14:15:34.156783+01	\N	2014-12-16 14:15:34.156563+01	4	72	4
8	2	2015-12-15 14:15:34.254872+01	\N	2014-12-16 14:15:34.254684+01	2	73	2
9	2	2015-12-15 14:15:34.33031+01	\N	2014-12-16 14:15:34.330107+01	3	74	3
10	1	2015-12-15 14:15:34.418151+01	\N	2014-12-16 14:15:34.417866+01	3	75	3
11	2	2015-12-15 14:15:34.513424+01	\N	2014-12-16 14:15:34.513246+01	3	76	3
12	1	2015-12-15 14:15:34.612089+01	\N	2014-12-16 14:15:34.611913+01	3	77	3
13	1	2015-12-15 14:15:34.679931+01	\N	2014-12-16 14:15:34.679724+01	3	78	3
14	2	2015-12-15 14:15:34.810987+01	\N	2015-11-03 14:15:34.810811+01	3	79	3
15	1	2015-12-15 14:15:34.92972+01	\N	2015-11-03 14:15:34.929493+01	4	80	4
16	0	2015-12-15 14:15:35.009833+01	\N	2015-11-03 14:15:35.009654+01	2	81	2
17	1	2015-12-15 14:15:35.092599+01	\N	2015-11-03 14:15:35.09242+01	4	82	4
18	1	2015-12-15 14:15:35.191099+01	\N	2015-11-03 14:15:35.190923+01	4	83	4
19	0	2015-12-15 14:15:35.276466+01	\N	2015-11-03 14:15:35.276282+01	2	84	2
20	3	2015-12-15 14:15:35.355572+01	\N	2015-11-03 14:15:35.355394+01	3	85	3
21	2	2015-12-15 14:15:35.460739+01	\N	2015-11-03 14:15:35.460497+01	2	86	2
22	4	2015-12-15 14:15:35.5576+01	\N	2015-11-03 14:15:35.557419+01	4	87	4
23	4	2015-12-15 14:15:35.652441+01	\N	2015-11-03 14:15:35.652264+01	2	88	2
24	2	2015-12-15 14:15:35.775255+01	\N	2015-11-03 14:15:35.775029+01	4	89	4
25	3	2015-12-15 14:15:35.909962+01	\N	2015-11-03 14:15:35.909749+01	3	90	3
26	2	2015-12-15 14:15:35.995385+01	\N	2015-11-03 14:15:35.995159+01	3	91	3
27	1	2015-12-15 14:15:36.124179+01	\N	2015-11-10 14:15:36.124002+01	3	92	3
28	1	2015-12-15 14:15:36.239625+01	\N	2015-11-10 14:15:36.239349+01	2	93	2
29	0	2015-12-15 14:15:36.364624+01	\N	2015-11-10 14:15:36.364319+01	4	94	4
30	0	2015-12-15 14:15:36.472872+01	\N	2015-11-10 14:15:36.472694+01	2	95	2
31	0	2015-12-15 14:15:36.561265+01	\N	2015-11-10 14:15:36.561087+01	4	96	4
32	0	2015-12-15 14:15:36.668197+01	\N	2015-11-10 14:15:36.66789+01	3	97	3
33	1	2015-12-15 14:15:36.747802+01	\N	2015-11-10 14:15:36.747614+01	4	98	4
34	1	2015-12-15 14:15:36.861583+01	\N	2015-11-10 14:15:36.861329+01	2	99	2
35	1	2015-12-15 14:15:36.949602+01	\N	2015-11-10 14:15:36.949417+01	4	100	4
36	2	2015-12-15 14:15:37.06268+01	\N	2015-11-10 14:15:37.062474+01	2	101	2
37	1	2015-12-15 14:15:37.134764+01	\N	2015-11-10 14:15:37.134482+01	2	102	2
38	2	2015-12-15 14:15:37.223058+01	\N	2015-11-10 14:15:37.22288+01	4	103	4
39	1	2015-12-15 14:15:37.29826+01	\N	2015-11-10 14:15:37.298025+01	3	104	3
40	1	2015-12-15 14:15:37.433003+01	\N	2015-11-17 14:15:37.432815+01	4	105	4
41	0	2015-12-15 14:15:37.51564+01	\N	2015-11-17 14:15:37.515441+01	2	106	2
42	1	2015-12-15 14:15:37.611761+01	\N	2015-11-17 14:15:37.611574+01	4	107	4
43	1	2015-12-15 14:15:37.704566+01	\N	2015-11-17 14:15:37.704368+01	2	108	2
44	2	2015-12-15 14:15:37.788719+01	\N	2015-11-17 14:15:37.788539+01	3	109	3
45	2	2015-12-15 14:15:38.158513+01	\N	2015-11-17 14:15:38.15833+01	3	110	3
46	4	2015-12-15 14:15:38.243595+01	\N	2015-11-17 14:15:38.243414+01	2	111	2
47	3	2015-12-15 14:15:38.327602+01	\N	2015-11-17 14:15:38.327389+01	3	112	3
48	4	2015-12-15 14:15:38.42944+01	\N	2015-11-17 14:15:38.429257+01	3	113	3
49	3	2015-12-15 14:15:38.500886+01	\N	2015-11-17 14:15:38.500708+01	2	114	2
50	3	2015-12-15 14:15:38.577919+01	\N	2015-11-17 14:15:38.577733+01	3	115	3
51	3	2015-12-15 14:15:38.67143+01	\N	2015-11-17 14:15:38.671233+01	4	116	4
52	3	2015-12-15 14:15:38.772382+01	\N	2015-11-17 14:15:38.772204+01	3	117	3
53	1	2015-12-15 14:15:38.916024+01	\N	2015-11-24 14:15:38.915833+01	2	118	2
54	0	2015-12-15 14:15:39.009593+01	\N	2015-11-24 14:15:39.009401+01	4	119	4
55	4	2015-12-15 14:15:39.090668+01	\N	2015-11-24 14:15:39.090468+01	4	120	4
56	4	2015-12-15 14:15:39.190351+01	\N	2015-11-24 14:15:39.190169+01	3	121	3
57	4	2015-12-15 14:15:39.268492+01	\N	2015-11-24 14:15:39.268285+01	4	122	4
58	1	2015-12-15 14:15:39.354649+01	\N	2015-11-24 14:15:39.354443+01	3	123	3
59	5	2015-12-15 14:15:39.439908+01	\N	2015-11-24 14:15:39.439725+01	2	124	2
60	7	2015-12-15 14:15:39.518923+01	\N	2015-11-24 14:15:39.518745+01	3	125	3
61	8	2015-12-15 14:15:39.60802+01	\N	2015-11-24 14:15:39.607775+01	3	126	3
62	8	2015-12-15 14:15:39.714507+01	\N	2015-11-24 14:15:39.714303+01	2	127	2
63	5	2015-12-15 14:15:39.799492+01	\N	2015-11-24 14:15:39.799294+01	4	128	4
64	5	2015-12-15 14:15:39.91374+01	\N	2015-11-24 14:15:39.913562+01	3	129	3
65	7	2015-12-15 14:15:40.007757+01	\N	2015-11-24 14:15:40.00758+01	3	130	3
66	1	2015-12-15 14:15:40.17207+01	\N	2015-12-08 14:15:40.171871+01	4	131	4
67	3	2015-12-15 14:15:40.25515+01	\N	2015-12-08 14:15:40.254967+01	2	132	2
68	0	2015-12-15 14:15:40.35694+01	\N	2015-12-08 14:15:40.356755+01	2	133	2
69	3	2015-12-15 14:15:40.460543+01	\N	2015-12-08 14:15:40.460342+01	2	134	2
70	2	2015-12-15 14:15:40.553188+01	\N	2015-12-08 14:15:40.552988+01	2	135	2
71	1	2015-12-15 14:15:40.644014+01	\N	2015-12-08 14:15:40.643824+01	4	136	4
72	6	2015-12-15 14:15:40.749392+01	\N	2015-12-08 14:15:40.749215+01	2	137	2
73	4	2015-12-15 14:15:40.850633+01	\N	2015-12-08 14:15:40.85044+01	3	138	3
74	5	2015-12-15 14:15:40.925494+01	\N	2015-12-08 14:15:40.925319+01	4	139	4
75	5	2015-12-15 14:15:41.027657+01	\N	2015-12-08 14:15:41.027446+01	3	140	3
76	6	2015-12-15 14:15:41.107684+01	\N	2015-12-08 14:15:41.107497+01	2	141	2
77	4	2015-12-15 14:15:41.199426+01	\N	2015-12-08 14:15:41.199241+01	2	142	2
78	4	2015-12-15 14:15:41.268617+01	\N	2015-12-08 14:15:41.26844+01	3	143	3
79	1	2015-11-17 14:15:43.996928+01	2015-12-03 12:15:43.99691+01	2015-11-30 14:15:43.732615+01	18	157	18
80	10	2015-12-03 17:15:44.025596+01	2015-12-12 14:15:44.025585+01	2015-12-08 14:15:44.025601+01	18	157	18
\.


--
-- Name: devilry_group_feedbackset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_group_feedbackset_id_seq', 80, true);


--
-- Data for Name: devilry_group_groupcomment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_groupcomment (comment_ptr_id, instant_publish, visible_for_students, feedback_set_id) FROM stdin;
1	t	t	1
2	t	t	1
3	t	t	1
4	t	t	1
5	t	t	2
6	t	t	2
7	t	t	2
8	t	t	2
9	f	t	2
10	t	t	3
11	t	t	3
12	t	t	4
13	t	t	4
14	f	t	4
15	t	t	5
16	t	t	5
17	t	t	5
18	t	t	5
19	t	t	5
20	t	t	5
21	t	t	6
22	t	t	6
23	t	t	6
24	t	t	6
25	t	t	6
26	f	t	6
27	t	t	7
28	t	t	7
29	t	t	7
30	t	t	7
31	t	t	7
32	t	t	8
33	f	t	8
34	t	t	9
35	t	t	9
36	t	t	10
37	t	t	10
38	t	t	10
39	t	t	10
40	t	t	10
41	t	t	10
42	t	t	11
43	t	t	11
44	t	t	11
45	t	t	11
46	t	t	11
47	t	t	11
48	t	t	12
49	f	t	12
50	t	t	13
51	f	t	13
52	t	t	14
53	t	t	14
54	t	t	14
55	t	t	14
56	t	t	14
57	f	t	14
58	t	t	15
59	t	t	15
60	t	t	15
61	t	t	15
62	f	t	15
63	t	t	16
64	t	t	16
65	t	t	16
66	t	t	16
67	t	t	17
68	t	t	17
69	t	t	17
70	t	t	17
71	t	t	17
72	f	t	17
73	t	t	18
74	t	t	18
75	f	t	18
76	t	t	19
77	t	t	19
78	f	t	19
79	t	t	20
80	t	t	20
81	t	t	20
82	t	t	20
83	t	t	20
84	t	t	21
85	t	t	21
86	t	t	21
87	t	t	21
88	t	t	21
89	t	t	21
90	t	t	22
91	t	t	22
92	t	t	22
93	f	t	22
94	t	t	23
95	t	t	23
96	t	t	23
97	t	t	23
98	f	t	23
99	t	t	24
100	t	t	24
101	t	t	24
102	t	t	24
103	t	t	24
104	t	t	24
105	t	t	25
106	t	t	25
107	t	t	25
108	t	t	25
109	t	t	25
110	f	t	25
111	t	t	26
112	t	t	26
113	t	t	26
114	f	t	26
115	t	t	27
116	t	t	27
117	t	t	27
118	t	t	27
119	t	t	27
120	t	t	28
121	t	t	28
122	t	t	28
123	t	t	28
124	t	t	28
125	f	t	28
126	t	t	29
127	t	t	29
128	t	t	29
129	t	t	29
130	t	t	29
131	f	t	29
132	t	t	30
133	t	t	30
134	t	t	30
135	t	t	31
136	t	t	31
137	t	t	31
138	t	t	31
139	t	t	32
140	t	t	32
141	f	t	32
142	t	t	33
143	t	t	33
144	t	t	33
145	t	t	33
146	t	t	34
147	t	t	34
148	t	t	34
149	t	t	34
150	t	t	34
151	f	t	34
152	t	t	35
153	t	t	35
154	t	t	35
155	t	t	35
156	t	t	35
157	t	t	36
158	t	t	36
159	t	t	36
160	t	t	36
161	t	t	36
162	t	t	37
163	t	t	37
164	t	t	37
165	t	t	37
166	t	t	38
167	f	t	38
168	t	t	39
169	f	t	39
170	t	t	40
171	t	t	40
172	t	t	41
173	t	t	41
174	t	t	41
175	t	t	41
176	t	t	41
177	t	t	42
178	t	t	42
179	t	t	42
180	f	t	42
181	t	t	43
182	t	t	43
183	t	t	43
184	t	t	43
185	t	t	44
186	t	t	44
187	t	t	44
188	t	t	45
189	t	t	45
190	t	t	45
191	t	t	45
192	f	t	45
193	t	t	46
194	t	t	46
195	t	t	46
196	t	t	46
197	f	t	46
198	t	t	47
199	t	t	47
200	t	t	47
201	t	t	47
202	t	t	47
203	f	t	47
204	t	t	48
205	t	t	48
206	t	t	49
207	t	t	49
208	f	t	49
209	t	t	50
210	t	t	50
211	t	t	50
212	f	t	50
213	t	t	51
214	t	t	51
215	t	t	51
216	t	t	51
217	t	t	51
218	t	t	52
219	t	t	52
220	t	t	52
221	t	t	52
222	t	t	53
223	t	t	53
224	t	t	54
225	t	t	54
226	t	t	54
227	t	t	54
228	f	t	54
229	t	t	55
230	f	t	55
231	t	t	56
232	t	t	56
233	t	t	56
234	t	t	56
235	t	t	56
236	t	t	57
237	t	t	57
238	t	t	57
239	t	t	57
240	f	t	57
241	t	t	58
242	t	t	58
243	f	t	58
244	t	t	59
245	t	t	59
246	t	t	60
247	t	t	60
248	t	t	60
249	t	t	61
250	t	t	61
251	t	t	61
252	t	t	61
253	t	t	61
254	f	t	61
255	t	t	62
256	t	t	62
257	t	t	62
258	t	t	63
259	t	t	63
260	t	t	63
261	t	t	63
262	t	t	63
263	t	t	63
264	t	t	64
265	t	t	64
266	t	t	64
267	t	t	64
268	t	t	64
269	t	t	64
270	t	t	65
271	t	t	65
272	f	t	65
273	t	t	66
274	t	t	66
275	t	t	66
276	f	t	66
277	t	t	67
278	t	t	67
279	t	t	67
280	t	t	67
281	f	t	67
282	t	t	68
283	t	t	68
284	t	t	68
285	t	t	68
286	t	t	68
287	t	t	69
288	t	t	69
289	t	t	69
290	f	t	69
291	t	t	70
292	t	t	70
293	t	t	70
294	f	t	70
295	t	t	71
296	t	t	71
297	t	t	71
298	t	t	71
299	t	t	71
300	f	t	71
301	t	t	72
302	t	t	72
303	t	t	72
304	t	t	73
305	t	t	73
306	t	t	73
307	t	t	73
308	t	t	73
309	f	t	73
310	t	t	74
311	t	t	74
312	t	t	74
313	t	t	74
314	f	t	74
315	t	t	75
316	t	t	75
317	t	t	75
318	t	t	75
319	t	t	76
320	t	t	76
321	t	t	76
322	t	t	77
323	t	t	77
324	t	t	78
325	t	t	78
326	t	t	78
327	f	t	78
328	t	t	79
329	t	t	79
330	t	t	79
331	t	t	79
332	t	t	79
333	t	t	79
334	t	t	79
335	t	t	80
336	t	t	80
337	t	t	80
338	t	t	80
339	t	t	80
340	t	t	80
\.


--
-- Data for Name: devilry_group_imageannotationcomment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_imageannotationcomment (comment_ptr_id, instant_publish, visible_for_students, x_coordinate, y_coordinate, feedback_set_id, image_id) FROM stdin;
\.


--
-- Data for Name: devilry_qualifiesforexam_deadlinetag; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_qualifiesforexam_deadlinetag (id, "timestamp", tag) FROM stdin;
\.


--
-- Name: devilry_qualifiesforexam_deadlinetag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_qualifiesforexam_deadlinetag_id_seq', 1, false);


--
-- Data for Name: devilry_qualifiesforexam_periodtag; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_qualifiesforexam_periodtag (period_id, deadlinetag_id) FROM stdin;
\.


--
-- Data for Name: devilry_qualifiesforexam_qualifiesforfinalexam; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_qualifiesforexam_qualifiesforfinalexam (id, qualifies, relatedstudent_id, status_id) FROM stdin;
\.


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_qualifiesforexam_qualifiesforfinalexam_id_seq', 1, false);


--
-- Data for Name: devilry_qualifiesforexam_status; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_qualifiesforexam_status (id, status, createtime, message, plugin, exported_timestamp, period_id, user_id) FROM stdin;
\.


--
-- Name: devilry_qualifiesforexam_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_qualifiesforexam_status_id_seq', 1, false);


--
-- Data for Name: devilry_student_uploadeddeliveryfile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_student_uploadeddeliveryfile (id, uploaded_datetime, uploaded_file, filename, deadline_id, user_id) FROM stdin;
\.


--
-- Name: devilry_student_uploadeddeliveryfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_student_uploadeddeliveryfile_id_seq', 1, false);


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2015-12-21 13:18:53.26733+01	1	Duckburgh Department Admins	1		36	1
2	2015-12-21 13:19:19.749762+01	1	Duckburgh Department Admins	2	Added Permission group user "thor@example.com in group Duckburgh Department Admins".	36	1
3	2015-12-21 13:30:01.26068+01	1	Group Duckburgh Department Admins assigned to duck1100	1		38	1
4	2015-12-21 13:32:39.5602+01	1	Duckburgh Department Admins (Department administrator group)	2	Added Permission group user "grandma@example.com in group Duckburgh Department Admins".	36	1
\.


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 4, true);


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY django_content_type (id, app_label, model) FROM stdin;
1	sessions	session
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	admin	logentry
6	cradmin_temporaryfileuploadstore	temporaryfilecollection
7	cradmin_temporaryfileuploadstore	temporaryfile
8	cradmin_generic_token_with_metadata	generictokenwithmetadata
9	core	node
10	core	subject
11	core	period
12	core	periodapplicationkeyvalue
13	core	relatedexaminer
14	core	relatedstudent
15	core	relatedexaminersyncsystemtag
16	core	relatedstudentsyncsystemtag
17	core	relatedstudentkeyvalue
18	core	assignment
19	core	pointtogrademap
20	core	pointrangetograde
21	core	assignmentgroup
22	core	assignmentgrouptag
23	core	deadline
24	core	filemeta
25	core	delivery
26	core	candidate
27	core	staticfeedback
28	core	staticfeedbackfileattachment
29	core	devilryuserprofile
30	core	examiner
31	core	groupinvite
32	devilry_account	user
33	devilry_account	useremail
34	devilry_account	username
35	devilry_account	permissiongroupuser
36	devilry_account	permissiongroup
37	devilry_account	periodpermissiongroup
38	devilry_account	subjectpermissiongroup
39	devilry_student	uploadeddeliveryfile
40	devilry_group	feedbackset
41	devilry_group	groupcomment
42	devilry_group	imageannotationcomment
43	devilry_comment	comment
44	devilry_comment	commentfile
45	devilry_comment	commentfileimage
46	devilry_qualifiesforexam	deadlinetag
47	devilry_qualifiesforexam	periodtag
48	devilry_qualifiesforexam	status
49	devilry_qualifiesforexam	qualifiesforfinalexam
50	devilry_gradingsystem	feedbackdraft
51	devilry_gradingsystem	feedbackdraftfile
52	devilry_detektor	detektorassignment
53	devilry_detektor	detektordeliveryparseresult
54	devilry_detektor	detektorassignmentcachelanguage
55	devilry_detektor	comparetwocacheitem
\.


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_content_type_id_seq', 55, true);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	devilry_account	0001_initial	2015-12-15 14:15:05.708678+01
2	contenttypes	0001_initial	2015-12-15 14:15:05.728372+01
3	admin	0001_initial	2015-12-15 14:15:05.757876+01
4	contenttypes	0002_remove_content_type_name	2015-12-15 14:15:05.82109+01
5	auth	0001_initial	2015-12-15 14:15:05.901318+01
6	auth	0002_alter_permission_name_max_length	2015-12-15 14:15:05.923081+01
7	auth	0003_alter_user_email_max_length	2015-12-15 14:15:05.955118+01
8	auth	0004_alter_user_username_opts	2015-12-15 14:15:05.978056+01
9	auth	0005_alter_user_last_login_null	2015-12-15 14:15:06.01243+01
10	auth	0006_require_contenttypes_0002	2015-12-15 14:15:06.015289+01
11	core	0001_initial	2015-12-15 14:15:08.727686+01
12	core	0002_auto_20150915_1127	2015-12-15 14:15:09.067446+01
13	core	0003_auto_20150917_1537	2015-12-15 14:15:09.531557+01
14	core	0004_examiner_relatedexaminer	2015-12-15 14:15:09.623577+01
15	core	0005_relatedexaminer_automatic_anonymous_id	2015-12-15 14:15:09.733118+01
16	core	0006_auto_20151112_1851	2015-12-15 14:15:09.820455+01
17	cradmin_generic_token_with_metadata	0001_initial	2015-12-15 14:15:09.908537+01
18	cradmin_temporaryfileuploadstore	0001_initial	2015-12-15 14:15:10.102266+01
19	cradmin_temporaryfileuploadstore	0002_temporaryfilecollection_singlemode	2015-12-15 14:15:10.201963+01
20	cradmin_temporaryfileuploadstore	0003_temporaryfilecollection_max_filesize_bytes	2015-12-15 14:15:10.290178+01
21	cradmin_temporaryfileuploadstore	0004_auto_20151017_1947	2015-12-15 14:15:10.382717+01
22	devilry_account	0002_auto_20150917_1731	2015-12-15 14:15:11.287675+01
23	devilry_account	0003_datamigrate-admins-into-permissiongroups	2015-12-15 14:15:11.301277+01
24	devilry_comment	0001_initial	2015-12-15 14:15:11.60564+01
25	devilry_detektor	0001_initial	2015-12-15 14:15:12.610976+01
26	devilry_gradingsystem	0001_initial	2015-12-15 14:15:12.853784+01
27	devilry_group	0001_initial	2015-12-15 14:15:13.218342+01
28	devilry_qualifiesforexam	0001_initial	2015-12-15 14:15:13.970939+01
29	devilry_student	0001_initial	2015-12-15 14:15:14.22089+01
30	sessions	0001_initial	2015-12-15 14:15:14.242772+01
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_migrations_id_seq', 30, true);


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
fl6doq89tyak366kf6k7ps343v1hbw5h	YWY3NDY4Y2M0OTQ5MzlkYTZiNTgzOTJkMjg3ZDYzNDk5ZmZlMzJjYzp7Il9hdXRoX3VzZXJfaGFzaCI6IjA0MzMwNDQ3MjA2OWM5N2ExYjAyZjZkNmU2YTU2NjBlNjZlMWNkYTciLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMSJ9	2015-12-29 20:24:53.297435+01
\.


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_codename_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: core_assignment_admins_assignment_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignment_admins
    ADD CONSTRAINT core_assignment_admins_assignment_id_user_id_key UNIQUE (assignment_id, user_id);


--
-- Name: core_assignment_admins_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignment_admins
    ADD CONSTRAINT core_assignment_admins_pkey PRIMARY KEY (id);


--
-- Name: core_assignment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignment
    ADD CONSTRAINT core_assignment_pkey PRIMARY KEY (id);


--
-- Name: core_assignment_short_name_1370cecf97cfafd_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignment
    ADD CONSTRAINT core_assignment_short_name_1370cecf97cfafd_uniq UNIQUE (short_name, parentnode_id);


--
-- Name: core_assignmentgroup_examiners_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT core_assignmentgroup_examiners_pkey PRIMARY KEY (id);


--
-- Name: core_assignmentgroup_examiners_user_id_661b98de00fa9407_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT core_assignmentgroup_examiners_user_id_661b98de00fa9407_uniq UNIQUE (user_id, assignmentgroup_id);


--
-- Name: core_assignmentgroup_feedback_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assignmentgroup_feedback_id_key UNIQUE (feedback_id);


--
-- Name: core_assignmentgroup_last_deadline_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assignmentgroup_last_deadline_id_key UNIQUE (last_deadline_id);


--
-- Name: core_assignmentgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assignmentgroup_pkey PRIMARY KEY (id);


--
-- Name: core_assignmentgroupt_assignment_group_id_27c175c3d5f47442_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgrouptag
    ADD CONSTRAINT core_assignmentgroupt_assignment_group_id_27c175c3d5f47442_uniq UNIQUE (assignment_group_id, tag);


--
-- Name: core_assignmentgrouptag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgrouptag
    ADD CONSTRAINT core_assignmentgrouptag_pkey PRIMARY KEY (id);


--
-- Name: core_candidate_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT core_candidate_pkey PRIMARY KEY (id);


--
-- Name: core_deadline_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_deadline
    ADD CONSTRAINT core_deadline_pkey PRIMARY KEY (id);


--
-- Name: core_delivery_last_feedback_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_delivery_last_feedback_id_key UNIQUE (last_feedback_id);


--
-- Name: core_delivery_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_delivery_pkey PRIMARY KEY (id);


--
-- Name: core_devilryuserprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_devilryuserprofile
    ADD CONSTRAINT core_devilryuserprofile_pkey PRIMARY KEY (id);


--
-- Name: core_devilryuserprofile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_devilryuserprofile
    ADD CONSTRAINT core_devilryuserprofile_user_id_key UNIQUE (user_id);


--
-- Name: core_filemeta_delivery_id_1954e8947150727e_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_filemeta
    ADD CONSTRAINT core_filemeta_delivery_id_1954e8947150727e_uniq UNIQUE (delivery_id, filename);


--
-- Name: core_filemeta_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_filemeta
    ADD CONSTRAINT core_filemeta_pkey PRIMARY KEY (id);


--
-- Name: core_groupinvite_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_groupinvite
    ADD CONSTRAINT core_groupinvite_pkey PRIMARY KEY (id);


--
-- Name: core_node_admins_node_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_node_admins
    ADD CONSTRAINT core_node_admins_node_id_user_id_key UNIQUE (node_id, user_id);


--
-- Name: core_node_admins_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_node_admins
    ADD CONSTRAINT core_node_admins_pkey PRIMARY KEY (id);


--
-- Name: core_node_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_node
    ADD CONSTRAINT core_node_pkey PRIMARY KEY (id);


--
-- Name: core_node_short_name_55c1f3c9f83a337a_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_node
    ADD CONSTRAINT core_node_short_name_55c1f3c9f83a337a_uniq UNIQUE (short_name, parentnode_id);


--
-- Name: core_period_admins_period_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_period_admins
    ADD CONSTRAINT core_period_admins_period_id_user_id_key UNIQUE (period_id, user_id);


--
-- Name: core_period_admins_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_period_admins
    ADD CONSTRAINT core_period_admins_pkey PRIMARY KEY (id);


--
-- Name: core_period_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_period
    ADD CONSTRAINT core_period_pkey PRIMARY KEY (id);


--
-- Name: core_period_short_name_7f17bb6a11b77159_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_period
    ADD CONSTRAINT core_period_short_name_7f17bb6a11b77159_uniq UNIQUE (short_name, parentnode_id);


--
-- Name: core_periodapplicationkeyvalue_period_id_1d119cce7d7c3cc9_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_periodapplicationkeyvalue
    ADD CONSTRAINT core_periodapplicationkeyvalue_period_id_1d119cce7d7c3cc9_uniq UNIQUE (period_id, application, key);


--
-- Name: core_periodapplicationkeyvalue_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_periodapplicationkeyvalue
    ADD CONSTRAINT core_periodapplicationkeyvalue_pkey PRIMARY KEY (id);


--
-- Name: core_pointrangetogr_point_to_grade_map_id_11d9dec2e994579b_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_pointrangetograde
    ADD CONSTRAINT core_pointrangetogr_point_to_grade_map_id_11d9dec2e994579b_uniq UNIQUE (point_to_grade_map_id, grade);


--
-- Name: core_pointrangetograde_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_pointrangetograde
    ADD CONSTRAINT core_pointrangetograde_pkey PRIMARY KEY (id);


--
-- Name: core_pointtogrademap_assignment_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_pointtogrademap
    ADD CONSTRAINT core_pointtogrademap_assignment_id_key UNIQUE (assignment_id);


--
-- Name: core_pointtogrademap_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_pointtogrademap
    ADD CONSTRAINT core_pointtogrademap_pkey PRIMARY KEY (id);


--
-- Name: core_relatedexaminer_period_id_686024ad5991feee_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedexaminer
    ADD CONSTRAINT core_relatedexaminer_period_id_686024ad5991feee_uniq UNIQUE (period_id, user_id);


--
-- Name: core_relatedexaminer_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedexaminer
    ADD CONSTRAINT core_relatedexaminer_pkey PRIMARY KEY (id);


--
-- Name: core_relatedexaminersy_relatedexaminer_id_12e1d6f77219149e_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedexaminersyncsystemtag
    ADD CONSTRAINT core_relatedexaminersy_relatedexaminer_id_12e1d6f77219149e_uniq UNIQUE (relatedexaminer_id, tag);


--
-- Name: core_relatedexaminersyncsystemtag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedexaminersyncsystemtag
    ADD CONSTRAINT core_relatedexaminersyncsystemtag_pkey PRIMARY KEY (id);


--
-- Name: core_relatedstudent_period_id_7bcf68a574802ebf_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedstudent
    ADD CONSTRAINT core_relatedstudent_period_id_7bcf68a574802ebf_uniq UNIQUE (period_id, user_id);


--
-- Name: core_relatedstudent_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedstudent
    ADD CONSTRAINT core_relatedstudent_pkey PRIMARY KEY (id);


--
-- Name: core_relatedstudentkeyv_relatedstudent_id_1b3fefef6a62d342_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedstudentkeyvalue
    ADD CONSTRAINT core_relatedstudentkeyv_relatedstudent_id_1b3fefef6a62d342_uniq UNIQUE (relatedstudent_id, application, key);


--
-- Name: core_relatedstudentkeyvalue_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedstudentkeyvalue
    ADD CONSTRAINT core_relatedstudentkeyvalue_pkey PRIMARY KEY (id);


--
-- Name: core_relatedstudentsync_relatedstudent_id_3bbd088d0b004096_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedstudentsyncsystemtag
    ADD CONSTRAINT core_relatedstudentsync_relatedstudent_id_3bbd088d0b004096_uniq UNIQUE (relatedstudent_id, tag);


--
-- Name: core_relatedstudentsyncsystemtag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_relatedstudentsyncsystemtag
    ADD CONSTRAINT core_relatedstudentsyncsystemtag_pkey PRIMARY KEY (id);


--
-- Name: core_staticfeedback_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_staticfeedback
    ADD CONSTRAINT core_staticfeedback_pkey PRIMARY KEY (id);


--
-- Name: core_staticfeedbackfileattachment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_staticfeedbackfileattachment
    ADD CONSTRAINT core_staticfeedbackfileattachment_pkey PRIMARY KEY (id);


--
-- Name: core_subject_admins_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_subject_admins
    ADD CONSTRAINT core_subject_admins_pkey PRIMARY KEY (id);


--
-- Name: core_subject_admins_subject_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_subject_admins
    ADD CONSTRAINT core_subject_admins_subject_id_user_id_key UNIQUE (subject_id, user_id);


--
-- Name: core_subject_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_subject
    ADD CONSTRAINT core_subject_pkey PRIMARY KEY (id);


--
-- Name: core_subject_short_name_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_subject
    ADD CONSTRAINT core_subject_short_name_key UNIQUE (short_name);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithm_token_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY cradmin_generic_token_with_metadata_generictokenwithmetadata
    ADD CONSTRAINT cradmin_generic_token_with_metadata_generictokenwithm_token_key UNIQUE (token);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetada_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY cradmin_generic_token_with_metadata_generictokenwithmetadata
    ADD CONSTRAINT cradmin_generic_token_with_metadata_generictokenwithmetada_pkey PRIMARY KEY (id);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfile
    ADD CONSTRAINT cradmin_temporaryfileuploadstore_temporaryfile_pkey PRIMARY KEY (id);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfilecollection
    ADD CONSTRAINT cradmin_temporaryfileuploadstore_temporaryfilecollection_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_period_permissiongroup_id_4a6525c29ab05fdc_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup
    ADD CONSTRAINT devilry_account_period_permissiongroup_id_4a6525c29ab05fdc_uniq UNIQUE (permissiongroup_id, period_id);


--
-- Name: devilry_account_periodpermissiongroup_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup
    ADD CONSTRAINT devilry_account_periodpermissiongroup_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_permis_permissiongroup_id_76525f84be59e6f6_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_permissiongroupuser
    ADD CONSTRAINT devilry_account_permis_permissiongroup_id_76525f84be59e6f6_uniq UNIQUE (permissiongroup_id, user_id);


--
-- Name: devilry_account_permissiongroup_name_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_permissiongroup
    ADD CONSTRAINT devilry_account_permissiongroup_name_key UNIQUE (name);


--
-- Name: devilry_account_permissiongroup_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_permissiongroup
    ADD CONSTRAINT devilry_account_permissiongroup_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_permissiongroupuser_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_permissiongroupuser
    ADD CONSTRAINT devilry_account_permissiongroupuser_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_subjec_permissiongroup_id_66aead092f6c883a_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup
    ADD CONSTRAINT devilry_account_subjec_permissiongroup_id_66aead092f6c883a_uniq UNIQUE (permissiongroup_id, subject_id);


--
-- Name: devilry_account_subjectpermissiongroup_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup
    ADD CONSTRAINT devilry_account_subjectpermissiongroup_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_user_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_user
    ADD CONSTRAINT devilry_account_user_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_user_shortname_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_user
    ADD CONSTRAINT devilry_account_user_shortname_key UNIQUE (shortname);


--
-- Name: devilry_account_useremail_email_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_useremail
    ADD CONSTRAINT devilry_account_useremail_email_key UNIQUE (email);


--
-- Name: devilry_account_useremail_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_useremail
    ADD CONSTRAINT devilry_account_useremail_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_useremail_user_id_5536c616df78a7e9_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_useremail
    ADD CONSTRAINT devilry_account_useremail_user_id_5536c616df78a7e9_uniq UNIQUE (user_id, is_primary);


--
-- Name: devilry_account_username_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_username
    ADD CONSTRAINT devilry_account_username_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_username_user_id_760100dbbc33fc25_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_username
    ADD CONSTRAINT devilry_account_username_user_id_760100dbbc33fc25_uniq UNIQUE (user_id, is_primary);


--
-- Name: devilry_account_username_username_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_account_username
    ADD CONSTRAINT devilry_account_username_username_key UNIQUE (username);


--
-- Name: devilry_comment_comment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_comment_comment
    ADD CONSTRAINT devilry_comment_comment_pkey PRIMARY KEY (id);


--
-- Name: devilry_comment_commentfile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_comment_commentfile
    ADD CONSTRAINT devilry_comment_commentfile_pkey PRIMARY KEY (id);


--
-- Name: devilry_comment_commentfileimage_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_comment_commentfileimage
    ADD CONSTRAINT devilry_comment_commentfileimage_pkey PRIMARY KEY (id);


--
-- Name: devilry_detektor_comparetwocacheitem_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_detektor_comparetwocacheitem
    ADD CONSTRAINT devilry_detektor_comparetwocacheitem_pkey PRIMARY KEY (id);


--
-- Name: devilry_detektor_de_detektorassignment_id_550f604c79f56784_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_detektor_detektorassignmentcachelanguage
    ADD CONSTRAINT devilry_detektor_de_detektorassignment_id_550f604c79f56784_uniq UNIQUE (detektorassignment_id, language);


--
-- Name: devilry_detektor_detektorassignment_assignment_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_detektor_detektorassignment
    ADD CONSTRAINT devilry_detektor_detektorassignment_assignment_id_key UNIQUE (assignment_id);


--
-- Name: devilry_detektor_detektorassignment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_detektor_detektorassignment
    ADD CONSTRAINT devilry_detektor_detektorassignment_pkey PRIMARY KEY (id);


--
-- Name: devilry_detektor_detektorassignmentcachelanguage_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_detektor_detektorassignmentcachelanguage
    ADD CONSTRAINT devilry_detektor_detektorassignmentcachelanguage_pkey PRIMARY KEY (id);


--
-- Name: devilry_detektor_detektordeli_delivery_id_73d630a72718f322_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_detektor_detektordeliveryparseresult
    ADD CONSTRAINT devilry_detektor_detektordeli_delivery_id_73d630a72718f322_uniq UNIQUE (delivery_id, language);


--
-- Name: devilry_detektor_detektordeliveryparseresult_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_detektor_detektordeliveryparseresult
    ADD CONSTRAINT devilry_detektor_detektordeliveryparseresult_pkey PRIMARY KEY (id);


--
-- Name: devilry_gradingsystem_feedbackdraft_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT devilry_gradingsystem_feedbackdraft_pkey PRIMARY KEY (id);


--
-- Name: devilry_gradingsystem_feedbackdraft_staticfeedback_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT devilry_gradingsystem_feedbackdraft_staticfeedback_id_key UNIQUE (staticfeedback_id);


--
-- Name: devilry_gradingsystem_feedbackdraftfile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraftfile
    ADD CONSTRAINT devilry_gradingsystem_feedbackdraftfile_pkey PRIMARY KEY (id);


--
-- Name: devilry_group_feedbackset_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devilry_group_feedbackset_pkey PRIMARY KEY (id);


--
-- Name: devilry_group_groupcomment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_group_groupcomment
    ADD CONSTRAINT devilry_group_groupcomment_pkey PRIMARY KEY (comment_ptr_id);


--
-- Name: devilry_group_imageannotationcomment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_group_imageannotationcomment
    ADD CONSTRAINT devilry_group_imageannotationcomment_pkey PRIMARY KEY (comment_ptr_id);


--
-- Name: devilry_qualifiesforexa_relatedstudent_id_487c8f68cac82075_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam
    ADD CONSTRAINT devilry_qualifiesforexa_relatedstudent_id_487c8f68cac82075_uniq UNIQUE (relatedstudent_id, status_id);


--
-- Name: devilry_qualifiesforexam_deadlinetag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_qualifiesforexam_deadlinetag
    ADD CONSTRAINT devilry_qualifiesforexam_deadlinetag_pkey PRIMARY KEY (id);


--
-- Name: devilry_qualifiesforexam_periodtag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_qualifiesforexam_periodtag
    ADD CONSTRAINT devilry_qualifiesforexam_periodtag_pkey PRIMARY KEY (period_id);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam
    ADD CONSTRAINT devilry_qualifiesforexam_qualifiesforfinalexam_pkey PRIMARY KEY (id);


--
-- Name: devilry_qualifiesforexam_status_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_qualifiesforexam_status
    ADD CONSTRAINT devilry_qualifiesforexam_status_pkey PRIMARY KEY (id);


--
-- Name: devilry_student_uploadeddeliv_deadline_id_5ceb94959540ad73_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile
    ADD CONSTRAINT devilry_student_uploadeddeliv_deadline_id_5ceb94959540ad73_uniq UNIQUE (deadline_id, user_id, filename);


--
-- Name: devilry_student_uploadeddeliveryfile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile
    ADD CONSTRAINT devilry_student_uploadeddeliveryfile_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_45f3b1d93ec8c61c_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_45f3b1d93ec8c61c_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: auth_group_name_253ae2a6331666e8_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX auth_group_name_253ae2a6331666e8_like ON auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_0e939a4f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX auth_group_permissions_0e939a4f ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_8373b171; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX auth_group_permissions_8373b171 ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_417f1b1c; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX auth_permission_417f1b1c ON auth_permission USING btree (content_type_id);


--
-- Name: core_assignment_2fc6351a; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_2fc6351a ON core_assignment USING btree (long_name);


--
-- Name: core_assignment_4698bac7; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_4698bac7 ON core_assignment USING btree (short_name);


--
-- Name: core_assignment_admins_93c4899b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_admins_93c4899b ON core_assignment_admins USING btree (assignment_id);


--
-- Name: core_assignment_admins_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_admins_e8701ad4 ON core_assignment_admins USING btree (user_id);


--
-- Name: core_assignment_b25d0d2b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_b25d0d2b ON core_assignment USING btree (parentnode_id);


--
-- Name: core_assignment_long_name_74ff61759131213c_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_long_name_74ff61759131213c_like ON core_assignment USING btree (long_name varchar_pattern_ops);


--
-- Name: core_assignment_short_name_5a022141fd10855d_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_short_name_5a022141fd10855d_like ON core_assignment USING btree (short_name varchar_pattern_ops);


--
-- Name: core_assignmentgroup_3dce5c8d; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgroup_3dce5c8d ON core_assignmentgroup USING btree (copied_from_id);


--
-- Name: core_assignmentgroup_b25d0d2b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgroup_b25d0d2b ON core_assignmentgroup USING btree (parentnode_id);


--
-- Name: core_assignmentgroup_examiners_5a4dbbf9; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgroup_examiners_5a4dbbf9 ON core_assignmentgroup_examiners USING btree (assignmentgroup_id);


--
-- Name: core_assignmentgroup_examiners_769693bb; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgroup_examiners_769693bb ON core_assignmentgroup_examiners USING btree (relatedexaminer_id);


--
-- Name: core_assignmentgroup_examiners_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgroup_examiners_e8701ad4 ON core_assignmentgroup_examiners USING btree (user_id);


--
-- Name: core_assignmentgrouptag_3f3b3700; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgrouptag_3f3b3700 ON core_assignmentgrouptag USING btree (assignment_group_id);


--
-- Name: core_assignmentgrouptag_e4d23e84; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgrouptag_e4d23e84 ON core_assignmentgrouptag USING btree (tag);


--
-- Name: core_assignmentgrouptag_tag_445a27de8f965a31_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgrouptag_tag_445a27de8f965a31_like ON core_assignmentgrouptag USING btree (tag varchar_pattern_ops);


--
-- Name: core_candidate_30a811f6; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_candidate_30a811f6 ON core_candidate USING btree (student_id);


--
-- Name: core_candidate_39cb6676; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_candidate_39cb6676 ON core_candidate USING btree (relatedstudent_id);


--
-- Name: core_candidate_3f3b3700; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_candidate_3f3b3700 ON core_candidate USING btree (assignment_group_id);


--
-- Name: core_deadline_0c5d7d4e; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_deadline_0c5d7d4e ON core_deadline USING btree (added_by_id);


--
-- Name: core_deadline_3f3b3700; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_deadline_3f3b3700 ON core_deadline USING btree (assignment_group_id);


--
-- Name: core_delivery_13a4f9cc; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_delivery_13a4f9cc ON core_delivery USING btree (deadline_id);


--
-- Name: core_delivery_37b4f50c; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_delivery_37b4f50c ON core_delivery USING btree (delivered_by_id);


--
-- Name: core_delivery_51ce87c1; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_delivery_51ce87c1 ON core_delivery USING btree (alias_delivery_id);


--
-- Name: core_delivery_8ea1f7aa; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_delivery_8ea1f7aa ON core_delivery USING btree (copy_of_id);


--
-- Name: core_filemeta_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_filemeta_7c4b99fe ON core_filemeta USING btree (delivery_id);


--
-- Name: core_groupinvite_0e939a4f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_groupinvite_0e939a4f ON core_groupinvite USING btree (group_id);


--
-- Name: core_groupinvite_a39b5ebd; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_groupinvite_a39b5ebd ON core_groupinvite USING btree (sent_to_id);


--
-- Name: core_groupinvite_d7ed4f1d; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_groupinvite_d7ed4f1d ON core_groupinvite USING btree (sent_by_id);


--
-- Name: core_node_2fc6351a; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_node_2fc6351a ON core_node USING btree (long_name);


--
-- Name: core_node_4698bac7; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_node_4698bac7 ON core_node USING btree (short_name);


--
-- Name: core_node_admins_c693ebc8; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_node_admins_c693ebc8 ON core_node_admins USING btree (node_id);


--
-- Name: core_node_admins_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_node_admins_e8701ad4 ON core_node_admins USING btree (user_id);


--
-- Name: core_node_b25d0d2b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_node_b25d0d2b ON core_node USING btree (parentnode_id);


--
-- Name: core_node_long_name_4f89f70ae716fabf_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_node_long_name_4f89f70ae716fabf_like ON core_node USING btree (long_name varchar_pattern_ops);


--
-- Name: core_node_short_name_636b489167fa620_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_node_short_name_636b489167fa620_like ON core_node USING btree (short_name varchar_pattern_ops);


--
-- Name: core_period_2fc6351a; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_period_2fc6351a ON core_period USING btree (long_name);


--
-- Name: core_period_4698bac7; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_period_4698bac7 ON core_period USING btree (short_name);


--
-- Name: core_period_admins_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_period_admins_b1efa79f ON core_period_admins USING btree (period_id);


--
-- Name: core_period_admins_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_period_admins_e8701ad4 ON core_period_admins USING btree (user_id);


--
-- Name: core_period_b25d0d2b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_period_b25d0d2b ON core_period USING btree (parentnode_id);


--
-- Name: core_period_long_name_5770388f6d0c1ee0_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_period_long_name_5770388f6d0c1ee0_like ON core_period USING btree (long_name varchar_pattern_ops);


--
-- Name: core_period_short_name_1e673681e8719241_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_period_short_name_1e673681e8719241_like ON core_period USING btree (short_name varchar_pattern_ops);


--
-- Name: core_periodapplicationkeyvalu_application_195ab7f853d68bd7_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_periodapplicationkeyvalu_application_195ab7f853d68bd7_like ON core_periodapplicationkeyvalue USING btree (application varchar_pattern_ops);


--
-- Name: core_periodapplicationkeyvalue_2063c160; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_periodapplicationkeyvalue_2063c160 ON core_periodapplicationkeyvalue USING btree (value);


--
-- Name: core_periodapplicationkeyvalue_3676d55f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_periodapplicationkeyvalue_3676d55f ON core_periodapplicationkeyvalue USING btree (application);


--
-- Name: core_periodapplicationkeyvalue_3c6e0b8a; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_periodapplicationkeyvalue_3c6e0b8a ON core_periodapplicationkeyvalue USING btree (key);


--
-- Name: core_periodapplicationkeyvalue_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_periodapplicationkeyvalue_b1efa79f ON core_periodapplicationkeyvalue USING btree (period_id);


--
-- Name: core_periodapplicationkeyvalue_key_7329f2bf53861cf8_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_periodapplicationkeyvalue_key_7329f2bf53861cf8_like ON core_periodapplicationkeyvalue USING btree (key varchar_pattern_ops);


--
-- Name: core_periodapplicationkeyvalue_value_3c6e96e7ba7f6690_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_periodapplicationkeyvalue_value_3c6e96e7ba7f6690_like ON core_periodapplicationkeyvalue USING btree (value text_pattern_ops);


--
-- Name: core_pointrangetograde_326d17f1; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_pointrangetograde_326d17f1 ON core_pointrangetograde USING btree (point_to_grade_map_id);


--
-- Name: core_relatedexaminer_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedexaminer_b1efa79f ON core_relatedexaminer USING btree (period_id);


--
-- Name: core_relatedexaminer_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedexaminer_e8701ad4 ON core_relatedexaminer USING btree (user_id);


--
-- Name: core_relatedexaminersyncsystemtag_769693bb; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedexaminersyncsystemtag_769693bb ON core_relatedexaminersyncsystemtag USING btree (relatedexaminer_id);


--
-- Name: core_relatedexaminersyncsystemtag_e4d23e84; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedexaminersyncsystemtag_e4d23e84 ON core_relatedexaminersyncsystemtag USING btree (tag);


--
-- Name: core_relatedexaminersyncsystemtag_tag_277a7dc13c66ef1d_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedexaminersyncsystemtag_tag_277a7dc13c66ef1d_like ON core_relatedexaminersyncsystemtag USING btree (tag varchar_pattern_ops);


--
-- Name: core_relatedstudent_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudent_b1efa79f ON core_relatedstudent USING btree (period_id);


--
-- Name: core_relatedstudent_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudent_e8701ad4 ON core_relatedstudent USING btree (user_id);


--
-- Name: core_relatedstudentkeyvalue_2063c160; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentkeyvalue_2063c160 ON core_relatedstudentkeyvalue USING btree (value);


--
-- Name: core_relatedstudentkeyvalue_3676d55f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentkeyvalue_3676d55f ON core_relatedstudentkeyvalue USING btree (application);


--
-- Name: core_relatedstudentkeyvalue_39cb6676; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentkeyvalue_39cb6676 ON core_relatedstudentkeyvalue USING btree (relatedstudent_id);


--
-- Name: core_relatedstudentkeyvalue_3c6e0b8a; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentkeyvalue_3c6e0b8a ON core_relatedstudentkeyvalue USING btree (key);


--
-- Name: core_relatedstudentkeyvalue_application_485c1d338d75ced_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentkeyvalue_application_485c1d338d75ced_like ON core_relatedstudentkeyvalue USING btree (application varchar_pattern_ops);


--
-- Name: core_relatedstudentkeyvalue_key_4d695a35117794a4_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentkeyvalue_key_4d695a35117794a4_like ON core_relatedstudentkeyvalue USING btree (key varchar_pattern_ops);


--
-- Name: core_relatedstudentkeyvalue_value_2e6d2220af915c34_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentkeyvalue_value_2e6d2220af915c34_like ON core_relatedstudentkeyvalue USING btree (value text_pattern_ops);


--
-- Name: core_relatedstudentsyncsystemtag_39cb6676; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentsyncsystemtag_39cb6676 ON core_relatedstudentsyncsystemtag USING btree (relatedstudent_id);


--
-- Name: core_relatedstudentsyncsystemtag_e4d23e84; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentsyncsystemtag_e4d23e84 ON core_relatedstudentsyncsystemtag USING btree (tag);


--
-- Name: core_relatedstudentsyncsystemtag_tag_4ac0f372e29bc146_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_relatedstudentsyncsystemtag_tag_4ac0f372e29bc146_like ON core_relatedstudentsyncsystemtag USING btree (tag varchar_pattern_ops);


--
-- Name: core_staticfeedback_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_staticfeedback_7c4b99fe ON core_staticfeedback USING btree (delivery_id);


--
-- Name: core_staticfeedback_bc7c970b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_staticfeedback_bc7c970b ON core_staticfeedback USING btree (saved_by_id);


--
-- Name: core_staticfeedbackfileattachment_a869bd9a; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_staticfeedbackfileattachment_a869bd9a ON core_staticfeedbackfileattachment USING btree (staticfeedback_id);


--
-- Name: core_subject_2fc6351a; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_subject_2fc6351a ON core_subject USING btree (long_name);


--
-- Name: core_subject_admins_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_subject_admins_e8701ad4 ON core_subject_admins USING btree (user_id);


--
-- Name: core_subject_admins_ffaba1d1; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_subject_admins_ffaba1d1 ON core_subject_admins USING btree (subject_id);


--
-- Name: core_subject_b25d0d2b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_subject_b25d0d2b ON core_subject USING btree (parentnode_id);


--
-- Name: core_subject_long_name_19cff4d64a1d8f4c_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_subject_long_name_19cff4d64a1d8f4c_like ON core_subject USING btree (long_name varchar_pattern_ops);


--
-- Name: core_subject_short_name_619954c9668d7b05_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_subject_short_name_619954c9668d7b05_like ON core_subject USING btree (short_name varchar_pattern_ops);


--
-- Name: cradmin_generic_token_with_metadata_g_app_4f5ee45a2fa39c00_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX cradmin_generic_token_with_metadata_g_app_4f5ee45a2fa39c00_like ON cradmin_generic_token_with_metadata_generictokenwithmetadata USING btree (app varchar_pattern_ops);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadatcb1d; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX cradmin_generic_token_with_metadata_generictokenwithmetadatcb1d ON cradmin_generic_token_with_metadata_generictokenwithmetadata USING btree (app);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadatf2be; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX cradmin_generic_token_with_metadata_generictokenwithmetadatf2be ON cradmin_generic_token_with_metadata_generictokenwithmetadata USING btree (content_type_id);


--
-- Name: cradmin_generic_token_with_metadata_token_4c62e4a4d20b64c8_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX cradmin_generic_token_with_metadata_token_4c62e4a4d20b64c8_like ON cradmin_generic_token_with_metadata_generictokenwithmetadata USING btree (token varchar_pattern_ops);


--
-- Name: cradmin_temporaryfileuploadstore_filename_3ca12967fd9be7b2_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX cradmin_temporaryfileuploadstore_filename_3ca12967fd9be7b2_like ON cradmin_temporaryfileuploadstore_temporaryfile USING btree (filename text_pattern_ops);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_0a1a4dd8; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX cradmin_temporaryfileuploadstore_temporaryfile_0a1a4dd8 ON cradmin_temporaryfileuploadstore_temporaryfile USING btree (collection_id);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_435ed7e9; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX cradmin_temporaryfileuploadstore_temporaryfile_435ed7e9 ON cradmin_temporaryfileuploadstore_temporaryfile USING btree (filename);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection_e8a4df; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX cradmin_temporaryfileuploadstore_temporaryfilecollection_e8a4df ON cradmin_temporaryfileuploadstore_temporaryfilecollection USING btree (user_id);


--
-- Name: devilry_account_periodpermissiongroup_3e7065db; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_periodpermissiongroup_3e7065db ON devilry_account_periodpermissiongroup USING btree (permissiongroup_id);


--
-- Name: devilry_account_periodpermissiongroup_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_periodpermissiongroup_b1efa79f ON devilry_account_periodpermissiongroup USING btree (period_id);


--
-- Name: devilry_account_permissiongroup_name_ef79acb69a7dd49_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_permissiongroup_name_ef79acb69a7dd49_like ON devilry_account_permissiongroup USING btree (name varchar_pattern_ops);


--
-- Name: devilry_account_permissiongroupuser_3e7065db; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_permissiongroupuser_3e7065db ON devilry_account_permissiongroupuser USING btree (permissiongroup_id);


--
-- Name: devilry_account_permissiongroupuser_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_permissiongroupuser_e8701ad4 ON devilry_account_permissiongroupuser USING btree (user_id);


--
-- Name: devilry_account_subjectpermissiongroup_3e7065db; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_subjectpermissiongroup_3e7065db ON devilry_account_subjectpermissiongroup USING btree (permissiongroup_id);


--
-- Name: devilry_account_subjectpermissiongroup_ffaba1d1; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_subjectpermissiongroup_ffaba1d1 ON devilry_account_subjectpermissiongroup USING btree (subject_id);


--
-- Name: devilry_account_user_shortname_343b9f8ebd9bbcb0_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_user_shortname_343b9f8ebd9bbcb0_like ON devilry_account_user USING btree (shortname varchar_pattern_ops);


--
-- Name: devilry_account_useremail_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_useremail_e8701ad4 ON devilry_account_useremail USING btree (user_id);


--
-- Name: devilry_account_useremail_email_1db096b7c69382_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_useremail_email_1db096b7c69382_like ON devilry_account_useremail USING btree (email varchar_pattern_ops);


--
-- Name: devilry_account_username_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_username_e8701ad4 ON devilry_account_username USING btree (user_id);


--
-- Name: devilry_account_username_username_107726b2079e7651_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_account_username_username_107726b2079e7651_like ON devilry_account_username USING btree (username varchar_pattern_ops);


--
-- Name: devilry_comment_comment_6be37982; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_comment_comment_6be37982 ON devilry_comment_comment USING btree (parent_id);


--
-- Name: devilry_comment_comment_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_comment_comment_e8701ad4 ON devilry_comment_comment USING btree (user_id);


--
-- Name: devilry_comment_commentfile_69b97d17; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_comment_commentfile_69b97d17 ON devilry_comment_commentfile USING btree (comment_id);


--
-- Name: devilry_comment_commentfileimage_b009b360; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_comment_commentfileimage_b009b360 ON devilry_comment_commentfileimage USING btree (comment_file_id);


--
-- Name: devilry_detektor_comparetwocacheitem_1228a18e; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_comparetwocacheitem_1228a18e ON devilry_detektor_comparetwocacheitem USING btree (parseresult1_id);


--
-- Name: devilry_detektor_comparetwocacheitem_468679bd; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_comparetwocacheitem_468679bd ON devilry_detektor_comparetwocacheitem USING btree (language_id);


--
-- Name: devilry_detektor_comparetwocacheitem_d16110ea; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_comparetwocacheitem_d16110ea ON devilry_detektor_comparetwocacheitem USING btree (parseresult2_id);


--
-- Name: devilry_detektor_detektorassignme_language_114b7a450cb9aef_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_detektorassignme_language_114b7a450cb9aef_like ON devilry_detektor_detektorassignmentcachelanguage USING btree (language varchar_pattern_ops);


--
-- Name: devilry_detektor_detektorassignment_dce7d5c6; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_detektorassignment_dce7d5c6 ON devilry_detektor_detektorassignment USING btree (processing_started_by_id);


--
-- Name: devilry_detektor_detektorassignmentcachelanguage_240acaf9; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_detektorassignmentcachelanguage_240acaf9 ON devilry_detektor_detektorassignmentcachelanguage USING btree (detektorassignment_id);


--
-- Name: devilry_detektor_detektorassignmentcachelanguage_8512ae7d; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_detektorassignmentcachelanguage_8512ae7d ON devilry_detektor_detektorassignmentcachelanguage USING btree (language);


--
-- Name: devilry_detektor_detektordeliver_language_3114eebc34f1a38a_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_detektordeliver_language_3114eebc34f1a38a_like ON devilry_detektor_detektordeliveryparseresult USING btree (language varchar_pattern_ops);


--
-- Name: devilry_detektor_detektordeliveryparseresult_240acaf9; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_detektordeliveryparseresult_240acaf9 ON devilry_detektor_detektordeliveryparseresult USING btree (detektorassignment_id);


--
-- Name: devilry_detektor_detektordeliveryparseresult_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_detektordeliveryparseresult_7c4b99fe ON devilry_detektor_detektordeliveryparseresult USING btree (delivery_id);


--
-- Name: devilry_detektor_detektordeliveryparseresult_8512ae7d; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_detektor_detektordeliveryparseresult_8512ae7d ON devilry_detektor_detektordeliveryparseresult USING btree (language);


--
-- Name: devilry_gradingsystem_feedbackdraft_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_gradingsystem_feedbackdraft_7c4b99fe ON devilry_gradingsystem_feedbackdraft USING btree (delivery_id);


--
-- Name: devilry_gradingsystem_feedbackdraft_bc7c970b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_gradingsystem_feedbackdraft_bc7c970b ON devilry_gradingsystem_feedbackdraft USING btree (saved_by_id);


--
-- Name: devilry_gradingsystem_feedbackdraftfile_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_gradingsystem_feedbackdraftfile_7c4b99fe ON devilry_gradingsystem_feedbackdraftfile USING btree (delivery_id);


--
-- Name: devilry_gradingsystem_feedbackdraftfile_bc7c970b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_gradingsystem_feedbackdraftfile_bc7c970b ON devilry_gradingsystem_feedbackdraftfile USING btree (saved_by_id);


--
-- Name: devilry_group_feedbackset_0e939a4f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_feedbackset_0e939a4f ON devilry_group_feedbackset USING btree (group_id);


--
-- Name: devilry_group_feedbackset_7dbe6d4c; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_feedbackset_7dbe6d4c ON devilry_group_feedbackset USING btree (published_by_id);


--
-- Name: devilry_group_feedbackset_e93cb7eb; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_feedbackset_e93cb7eb ON devilry_group_feedbackset USING btree (created_by_id);


--
-- Name: devilry_group_groupcomment_c08198b8; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_groupcomment_c08198b8 ON devilry_group_groupcomment USING btree (feedback_set_id);


--
-- Name: devilry_group_imageannotationcomment_c08198b8; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_imageannotationcomment_c08198b8 ON devilry_group_imageannotationcomment USING btree (feedback_set_id);


--
-- Name: devilry_group_imageannotationcomment_f33175e6; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_imageannotationcomment_f33175e6 ON devilry_group_imageannotationcomment USING btree (image_id);


--
-- Name: devilry_qualifiesforexam_periodtag_f2e8843d; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_qualifiesforexam_periodtag_f2e8843d ON devilry_qualifiesforexam_periodtag USING btree (deadlinetag_id);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_39cb6676; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_qualifiesforexam_qualifiesforfinalexam_39cb6676 ON devilry_qualifiesforexam_qualifiesforfinalexam USING btree (relatedstudent_id);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_dc91ed4b; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_qualifiesforexam_qualifiesforfinalexam_dc91ed4b ON devilry_qualifiesforexam_qualifiesforfinalexam USING btree (status_id);


--
-- Name: devilry_qualifiesforexam_status_9acb4454; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_qualifiesforexam_status_9acb4454 ON devilry_qualifiesforexam_status USING btree (status);


--
-- Name: devilry_qualifiesforexam_status_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_qualifiesforexam_status_b1efa79f ON devilry_qualifiesforexam_status USING btree (period_id);


--
-- Name: devilry_qualifiesforexam_status_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_qualifiesforexam_status_e8701ad4 ON devilry_qualifiesforexam_status USING btree (user_id);


--
-- Name: devilry_qualifiesforexam_status_status_2c1ff15028fbb430_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_qualifiesforexam_status_status_2c1ff15028fbb430_like ON devilry_qualifiesforexam_status USING btree (status varchar_pattern_ops);


--
-- Name: devilry_student_uploadeddeliveryfile_13a4f9cc; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_student_uploadeddeliveryfile_13a4f9cc ON devilry_student_uploadeddeliveryfile USING btree (deadline_id);


--
-- Name: devilry_student_uploadeddeliveryfile_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_student_uploadeddeliveryfile_e8701ad4 ON devilry_student_uploadeddeliveryfile USING btree (user_id);


--
-- Name: django_admin_log_417f1b1c; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX django_admin_log_417f1b1c ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX django_admin_log_e8701ad4 ON django_admin_log USING btree (user_id);


--
-- Name: django_session_de54fa62; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX django_session_de54fa62 ON django_session USING btree (expire_date);


--
-- Name: django_session_session_key_461cfeaa630ca218_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX django_session_session_key_461cfeaa630ca218_like ON django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: D181b2ae85af4a8c369c2bd09f842f6f; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroupuser
    ADD CONSTRAINT "D181b2ae85af4a8c369c2bd09f842f6f" FOREIGN KEY (permissiongroup_id) REFERENCES devilry_account_permissiongroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D1965e3e4638ee5be6b0f49cbdea7a37; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_detektorassignment
    ADD CONSTRAINT "D1965e3e4638ee5be6b0f49cbdea7a37" FOREIGN KEY (processing_started_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D20764de45e8d8a217e91823fd6c89e4; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_comparetwocacheitem
    ADD CONSTRAINT "D20764de45e8d8a217e91823fd6c89e4" FOREIGN KEY (parseresult1_id) REFERENCES devilry_detektor_detektordeliveryparseresult(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D219dbbaa875f1077d0f63778d98858a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouptag
    ADD CONSTRAINT "D219dbbaa875f1077d0f63778d98858a" FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D5e4a1a4b4d81269fe677b9b11bcf9dd; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_imageannotationcomment
    ADD CONSTRAINT "D5e4a1a4b4d81269fe677b9b11bcf9dd" FOREIGN KEY (feedback_set_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D5f5cf2622c65b08333d71d461503ad8; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_detektordeliveryparseresult
    ADD CONSTRAINT "D5f5cf2622c65b08333d71d461503ad8" FOREIGN KEY (detektorassignment_id) REFERENCES devilry_detektor_detektorassignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D732bd61cc9e1e86d0a2745a748ae7e9; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup
    ADD CONSTRAINT "D732bd61cc9e1e86d0a2745a748ae7e9" FOREIGN KEY (permissiongroup_id) REFERENCES devilry_account_permissiongroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D79d937271caab7986ef197c606f2644; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_groupcomment
    ADD CONSTRAINT "D79d937271caab7986ef197c606f2644" FOREIGN KEY (feedback_set_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D7a2e2c495420c609a4846787916da46; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_comparetwocacheitem
    ADD CONSTRAINT "D7a2e2c495420c609a4846787916da46" FOREIGN KEY (language_id) REFERENCES devilry_detektor_detektorassignmentcachelanguage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D7eb2452376d1d7e0038f38d5151e20b; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_deadline
    ADD CONSTRAINT "D7eb2452376d1d7e0038f38d5151e20b" FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D7ee9ff6a5732140884d0f0eb3eb9732; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_detektorassignmentcachelanguage
    ADD CONSTRAINT "D7ee9ff6a5732140884d0f0eb3eb9732" FOREIGN KEY (detektorassignment_id) REFERENCES devilry_detektor_detektorassignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D8ec1ffb7a00b82f7d4d23443f299188; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfile
    ADD CONSTRAINT "D8ec1ffb7a00b82f7d4d23443f299188" FOREIGN KEY (collection_id) REFERENCES cradmin_temporaryfileuploadstore_temporaryfilecollection(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: D933fe820df1d2bd50b8cf9434debe68; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT "D933fe820df1d2bd50b8cf9434debe68" FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: a3e107e91b77c6db5a281e5a98c442ab; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup
    ADD CONSTRAINT a3e107e91b77c6db5a281e5a98c442ab FOREIGN KEY (permissiongroup_id) REFERENCES devilry_account_permissiongroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: assignmentgroup_id_1a4ffb13b923185e_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT assignmentgroup_id_1a4ffb13b923185e_fk_core_assignmentgroup_id FOREIGN KEY (assignmentgroup_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_content_type_id_508cf46651277a81_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_content_type_id_508cf46651277a81_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissio_group_id_689710a9a73b7457_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_group_id_689710a9a73b7457_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: b192fa069cc9d03afa7e7517d7bed124; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_imageannotationcomment
    ADD CONSTRAINT b192fa069cc9d03afa7e7517d7bed124 FOREIGN KEY (image_id) REFERENCES devilry_comment_commentfileimage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: b863a82336ea177568feaa30e1e51c85; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam
    ADD CONSTRAINT b863a82336ea177568feaa30e1e51c85 FOREIGN KEY (status_id) REFERENCES devilry_qualifiesforexam_status(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: c5ab7e1e9bde26caa038c76c78d6bc7c; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfileimage
    ADD CONSTRAINT c5ab7e1e9bde26caa038c76c78d6bc7c FOREIGN KEY (comment_file_id) REFERENCES devilry_comment_commentfile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: co_relatedstudent_id_10993e5068bc33c2_fk_core_relatedstudent_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudentsyncsystemtag
    ADD CONSTRAINT co_relatedstudent_id_10993e5068bc33c2_fk_core_relatedstudent_id FOREIGN KEY (relatedstudent_id) REFERENCES core_relatedstudent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: co_relatedstudent_id_3e3e80d75676e0c9_fk_core_relatedstudent_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudentkeyvalue
    ADD CONSTRAINT co_relatedstudent_id_3e3e80d75676e0c9_fk_core_relatedstudent_id FOREIGN KEY (relatedstudent_id) REFERENCES core_relatedstudent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: co_relatedstudent_id_7e66ddf8f3442b99_fk_core_relatedstudent_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT co_relatedstudent_id_7e66ddf8f3442b99_fk_core_relatedstudent_id FOREIGN KEY (relatedstudent_id) REFERENCES core_relatedstudent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: co_staticfeedback_id_4a6ee82466877520_fk_core_staticfeedback_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedbackfileattachment
    ADD CONSTRAINT co_staticfeedback_id_4a6ee82466877520_fk_core_staticfeedback_id FOREIGN KEY (staticfeedback_id) REFERENCES core_staticfeedback(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cor_last_feedback_id_15c1864499fa3298_fk_core_staticfeedback_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT cor_last_feedback_id_15c1864499fa3298_fk_core_staticfeedback_id FOREIGN KEY (last_feedback_id) REFERENCES core_staticfeedback(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_ass_feedback_id_4f3eb4317ce05ffd_fk_core_staticfeedback_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_ass_feedback_id_4f3eb4317ce05ffd_fk_core_staticfeedback_id FOREIGN KEY (feedback_id) REFERENCES core_staticfeedback(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assig_assignment_id_712ee5b81efdf7d7_fk_core_assignment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment_admins
    ADD CONSTRAINT core_assig_assignment_id_712ee5b81efdf7d7_fk_core_assignment_id FOREIGN KEY (assignment_id) REFERENCES core_assignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assig_last_deadline_id_946dfcf7910964c_fk_core_deadline_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assig_last_deadline_id_946dfcf7910964c_fk_core_deadline_id FOREIGN KEY (last_deadline_id) REFERENCES core_deadline(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assig_parentnode_id_6e190fc057b9057c_fk_core_assignment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assig_parentnode_id_6e190fc057b9057c_fk_core_assignment_id FOREIGN KEY (parentnode_id) REFERENCES core_assignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assign_user_id_1a363f9e86525194_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT core_assign_user_id_1a363f9e86525194_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignm_user_id_51116d5a7e12d3b_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment_admins
    ADD CONSTRAINT core_assignm_user_id_51116d5a7e12d3b_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmen_parentnode_id_7072d3388816d25c_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment
    ADD CONSTRAINT core_assignmen_parentnode_id_7072d3388816d25c_fk_core_period_id FOREIGN KEY (parentnode_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_can_student_id_3cfef9dad22e18db_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT core_can_student_id_3cfef9dad22e18db_fk_devilry_account_user_id FOREIGN KEY (student_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_copied_from_id_21e068e4666502b2_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_copied_from_id_21e068e4666502b2_fk_core_assignmentgroup_id FOREIGN KEY (copied_from_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_de_added_by_id_5715a513f2acd9ff_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_deadline
    ADD CONSTRAINT core_de_added_by_id_5715a513f2acd9ff_fk_devilry_account_user_id FOREIGN KEY (added_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_del_alias_delivery_id_58e23cdc9faaee16_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_del_alias_delivery_id_58e23cdc9faaee16_fk_core_delivery_id FOREIGN KEY (alias_delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_deli_delivered_by_id_47605050cd8092f1_fk_core_candidate_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_deli_delivered_by_id_47605050cd8092f1_fk_core_candidate_id FOREIGN KEY (delivered_by_id) REFERENCES core_candidate(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_delivery_copy_of_id_4bdefcd646b758a3_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_delivery_copy_of_id_4bdefcd646b758a3_fk_core_delivery_id FOREIGN KEY (copy_of_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_delivery_deadline_id_3af0ef5599495505_fk_core_deadline_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_delivery_deadline_id_3af0ef5599495505_fk_core_deadline_id FOREIGN KEY (deadline_id) REFERENCES core_deadline(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_devilr_user_id_71c4199c1d6418ff_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_devilryuserprofile
    ADD CONSTRAINT core_devilr_user_id_71c4199c1d6418ff_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_filemeta_delivery_id_6601bb0f5e56d9fe_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_filemeta
    ADD CONSTRAINT core_filemeta_delivery_id_6601bb0f5e56d9fe_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_gro_sent_by_id_1efa01196ad2f009_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite
    ADD CONSTRAINT core_gro_sent_by_id_1efa01196ad2f009_fk_devilry_account_user_id FOREIGN KEY (sent_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_gro_sent_to_id_50bd8691e6283e67_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite
    ADD CONSTRAINT core_gro_sent_to_id_50bd8691e6283e67_fk_devilry_account_user_id FOREIGN KEY (sent_to_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_groupi_group_id_3650f45b11bc854_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite
    ADD CONSTRAINT core_groupi_group_id_3650f45b11bc854_fk_core_assignmentgroup_id FOREIGN KEY (group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_node_a_user_id_168b63ac6db71014_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_node_admins
    ADD CONSTRAINT core_node_a_user_id_168b63ac6db71014_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_node_admins_node_id_3473ea14d20400d3_fk_core_node_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_node_admins
    ADD CONSTRAINT core_node_admins_node_id_3473ea14d20400d3_fk_core_node_id FOREIGN KEY (node_id) REFERENCES core_node(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_node_parentnode_id_11910a14978a64d9_fk_core_node_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_node
    ADD CONSTRAINT core_node_parentnode_id_11910a14978a64d9_fk_core_node_id FOREIGN KEY (parentnode_id) REFERENCES core_node(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_period__user_id_eb067c4bde098ff_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period_admins
    ADD CONSTRAINT core_period__user_id_eb067c4bde098ff_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_period_admins_period_id_11596bf319c91d8f_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period_admins
    ADD CONSTRAINT core_period_admins_period_id_11596bf319c91d8f_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_period_parentnode_id_1844773fcb98c0b8_fk_core_subject_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period
    ADD CONSTRAINT core_period_parentnode_id_1844773fcb98c0b8_fk_core_subject_id FOREIGN KEY (parentnode_id) REFERENCES core_subject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_periodapplica_period_id_71495bf20087514e_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodapplicationkeyvalue
    ADD CONSTRAINT core_periodapplica_period_id_71495bf20087514e_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_point_assignment_id_45add1f59eb1ca29_fk_core_assignment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointtogrademap
    ADD CONSTRAINT core_point_assignment_id_45add1f59eb1ca29_fk_core_assignment_id FOREIGN KEY (assignment_id) REFERENCES core_assignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_relate_user_id_644ee92d6b54d587_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminer
    ADD CONSTRAINT core_relate_user_id_644ee92d6b54d587_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_related_user_id_66588181cfc595a_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudent
    ADD CONSTRAINT core_related_user_id_66588181cfc595a_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_relatedexamin_period_id_1608ffa9420f3529_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminer
    ADD CONSTRAINT core_relatedexamin_period_id_1608ffa9420f3529_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_relatedstuden_period_id_518a11c836f19f36_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudent
    ADD CONSTRAINT core_relatedstuden_period_id_518a11c836f19f36_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_st_saved_by_id_5c9526c62cf55415_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedback
    ADD CONSTRAINT core_st_saved_by_id_5c9526c62cf55415_fk_devilry_account_user_id FOREIGN KEY (saved_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_staticfee_delivery_id_76cd203e463381c6_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedback
    ADD CONSTRAINT core_staticfee_delivery_id_76cd203e463381c6_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_subjec_user_id_757b64082c3dd225_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject_admins
    ADD CONSTRAINT core_subjec_user_id_757b64082c3dd225_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_subject_admi_subject_id_30074ec6a2ab50f_fk_core_subject_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject_admins
    ADD CONSTRAINT core_subject_admi_subject_id_30074ec6a2ab50f_fk_core_subject_id FOREIGN KEY (subject_id) REFERENCES core_subject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_subject_parentnode_id_b1aed9c7f40b34c_fk_core_node_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject
    ADD CONSTRAINT core_subject_parentnode_id_b1aed9c7f40b34c_fk_core_node_id FOREIGN KEY (parentnode_id) REFERENCES core_node(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: crad_content_type_id_51aea07aab3596f7_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_generic_token_with_metadata_generictokenwithmetadata
    ADD CONSTRAINT crad_content_type_id_51aea07aab3596f7_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cradmin_tem_user_id_2dc5e0653dd71e89_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfilecollection
    ADD CONSTRAINT cradmin_tem_user_id_2dc5e0653dd71e89_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: d0e0aa08edad3ed1e6bdf96c03308582; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointrangetograde
    ADD CONSTRAINT d0e0aa08edad3ed1e6bdf96c03308582 FOREIGN KEY (point_to_grade_map_id) REFERENCES core_pointtogrademap(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: d_comment_ptr_id_1afa15ad1c07737e_fk_devilry_comment_comment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_imageannotationcomment
    ADD CONSTRAINT d_comment_ptr_id_1afa15ad1c07737e_fk_devilry_comment_comment_id FOREIGN KEY (comment_ptr_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: d_comment_ptr_id_77e73d4401d55a91_fk_devilry_comment_comment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_groupcomment
    ADD CONSTRAINT d_comment_ptr_id_77e73d4401d55a91_fk_devilry_comment_comment_id FOREIGN KEY (comment_ptr_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: de_relatedstudent_id_55ab211e0e76d3c5_fk_core_relatedstudent_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam
    ADD CONSTRAINT de_relatedstudent_id_55ab211e0e76d3c5_fk_core_relatedstudent_id FOREIGN KEY (relatedstudent_id) REFERENCES core_relatedstudent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: de_staticfeedback_id_43feb18645a3f2a4_fk_core_staticfeedback_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT de_staticfeedback_id_43feb18645a3f2a4_fk_core_staticfeedback_id FOREIGN KEY (staticfeedback_id) REFERENCES core_staticfeedback(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devi_published_by_id_2eb5ae2cfe02ede_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devi_published_by_id_2eb5ae2cfe02ede_fk_devilry_account_user_id FOREIGN KEY (published_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devil_comment_id_2e9f77d72415c03e_fk_devilry_comment_comment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfile
    ADD CONSTRAINT devil_comment_id_2e9f77d72415c03e_fk_devilry_comment_comment_id FOREIGN KEY (comment_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devil_created_by_id_65f4d92013118f3e_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devil_created_by_id_65f4d92013118f3e_fk_devilry_account_user_id FOREIGN KEY (created_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilr_parent_id_5b1213dd5232a472_fk_devilry_comment_comment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_comment
    ADD CONSTRAINT devilr_parent_id_5b1213dd5232a472_fk_devilry_comment_comment_id FOREIGN KEY (parent_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_acc_user_id_1639a4cd40d74025_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroupuser
    ADD CONSTRAINT devilry_acc_user_id_1639a4cd40d74025_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_acc_user_id_5199824be5bb3b9b_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_username
    ADD CONSTRAINT devilry_acc_user_id_5199824be5bb3b9b_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_acco_user_id_a38a81995988057_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_useremail
    ADD CONSTRAINT devilry_acco_user_id_a38a81995988057_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account__subject_id_305f1dc9fe3d5d33_fk_core_subject_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup
    ADD CONSTRAINT devilry_account__subject_id_305f1dc9fe3d5d33_fk_core_subject_id FOREIGN KEY (subject_id) REFERENCES core_subject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account_pe_period_id_2bc5882f60c3e215_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup
    ADD CONSTRAINT devilry_account_pe_period_id_2bc5882f60c3e215_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_com_user_id_22e2aceb29d9ed4d_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_comment
    ADD CONSTRAINT devilry_com_user_id_22e2aceb29d9ed4d_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_de_assignment_id_5c8bfb0575d0ce88_fk_core_assignment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_detektorassignment
    ADD CONSTRAINT devilry_de_assignment_id_5c8bfb0575d0ce88_fk_core_assignment_id FOREIGN KEY (assignment_id) REFERENCES core_assignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_detekt_delivery_id_2b9cbe5c25c606cd_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_detektordeliveryparseresult
    ADD CONSTRAINT devilry_detekt_delivery_id_2b9cbe5c25c606cd_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_gr_group_id_148fa5d5062a96f8_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devilry_gr_group_id_148fa5d5062a96f8_fk_core_assignmentgroup_id FOREIGN KEY (group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_gradin_delivery_id_31734762a96e190f_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT devilry_gradin_delivery_id_31734762a96e190f_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_gradin_delivery_id_65ac58b6a461891b_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraftfile
    ADD CONSTRAINT devilry_gradin_delivery_id_65ac58b6a461891b_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qua_user_id_522959bf05072244_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_status
    ADD CONSTRAINT devilry_qua_user_id_522959bf05072244_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qualifiesf_period_id_102beba2d8031066_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_periodtag
    ADD CONSTRAINT devilry_qualifiesf_period_id_102beba2d8031066_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qualifiesf_period_id_6a80472573c78154_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_status
    ADD CONSTRAINT devilry_qualifiesf_period_id_6a80472573c78154_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_saved_by_id_22ca281ac57fddb4_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraftfile
    ADD CONSTRAINT devilry_saved_by_id_22ca281ac57fddb4_fk_devilry_account_user_id FOREIGN KEY (saved_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_saved_by_id_2688417740fdf346_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT devilry_saved_by_id_2688417740fdf346_fk_devilry_account_user_id FOREIGN KEY (saved_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_stu_user_id_594ee6dafdf52417_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile
    ADD CONSTRAINT devilry_stu_user_id_594ee6dafdf52417_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_studen_deadline_id_73bb1a77ed86db5c_fk_core_deadline_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile
    ADD CONSTRAINT devilry_studen_deadline_id_73bb1a77ed86db5c_fk_core_deadline_id FOREIGN KEY (deadline_id) REFERENCES core_deadline(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: djan_content_type_id_697914295151027a_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT djan_content_type_id_697914295151027a_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admi_user_id_52fdd58701c5f563_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admi_user_id_52fdd58701c5f563_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: f015661466f55b1eb40c72265d9a004b; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_detektor_comparetwocacheitem
    ADD CONSTRAINT f015661466f55b1eb40c72265d9a004b FOREIGN KEY (parseresult2_id) REFERENCES devilry_detektor_detektordeliveryparseresult(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: f2a2267fbb3f8424a3f20a79ed9ed35d; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_periodtag
    ADD CONSTRAINT f2a2267fbb3f8424a3f20a79ed9ed35d FOREIGN KEY (deadlinetag_id) REFERENCES devilry_qualifiesforexam_deadlinetag(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: relatedexaminer_id_46b4afef8d47d182_fk_core_relatedexaminer_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT relatedexaminer_id_46b4afef8d47d182_fk_core_relatedexaminer_id FOREIGN KEY (relatedexaminer_id) REFERENCES core_relatedexaminer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: relatedexaminer_id_5ba8809c8b73032e_fk_core_relatedexaminer_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminersyncsystemtag
    ADD CONSTRAINT relatedexaminer_id_5ba8809c8b73032e_fk_core_relatedexaminer_id FOREIGN KEY (relatedexaminer_id) REFERENCES core_relatedexaminer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

