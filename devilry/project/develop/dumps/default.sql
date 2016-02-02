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


ALTER TABLE auth_group OWNER TO dbdev;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_group_id_seq OWNER TO dbdev;

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


ALTER TABLE auth_group_permissions OWNER TO dbdev;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_group_permissions_id_seq OWNER TO dbdev;

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


ALTER TABLE auth_permission OWNER TO dbdev;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_permission_id_seq OWNER TO dbdev;

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
    deprecated_field_anonymous boolean NOT NULL,
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
    gradeform_setup_json text,
    anonymizationmode character varying(15) NOT NULL,
    uses_custom_candidate_ids boolean NOT NULL,
    CONSTRAINT core_assignment_deadline_handling_check CHECK ((deadline_handling >= 0)),
    CONSTRAINT core_assignment_delivery_types_check CHECK ((delivery_types >= 0)),
    CONSTRAINT core_assignment_max_points_check CHECK ((max_points >= 0)),
    CONSTRAINT core_assignment_passing_grade_min_points_check CHECK ((passing_grade_min_points >= 0)),
    CONSTRAINT core_assignment_scale_points_percent_check CHECK ((scale_points_percent >= 0))
);


ALTER TABLE core_assignment OWNER TO dbdev;

--
-- Name: core_assignment_admins; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_assignment_admins (
    id integer NOT NULL,
    assignment_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE core_assignment_admins OWNER TO dbdev;

--
-- Name: core_assignment_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignment_admins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_assignment_admins_id_seq OWNER TO dbdev;

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


ALTER TABLE core_assignment_id_seq OWNER TO dbdev;

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
    parentnode_id integer NOT NULL,
    batchoperation_id integer
);


ALTER TABLE core_assignmentgroup OWNER TO dbdev;

--
-- Name: core_assignmentgroup_examiners; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_assignmentgroup_examiners (
    id integer NOT NULL,
    assignmentgroup_id integer NOT NULL,
    old_reference_not_in_use_user_id integer,
    relatedexaminer_id integer NOT NULL
);


ALTER TABLE core_assignmentgroup_examiners OWNER TO dbdev;

--
-- Name: core_assignmentgroup_examiners_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignmentgroup_examiners_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_assignmentgroup_examiners_id_seq OWNER TO dbdev;

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


ALTER TABLE core_assignmentgroup_id_seq OWNER TO dbdev;

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


ALTER TABLE core_assignmentgrouptag OWNER TO dbdev;

--
-- Name: core_assignmentgrouptag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignmentgrouptag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_assignmentgrouptag_id_seq OWNER TO dbdev;

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
    assignment_group_id integer NOT NULL,
    old_reference_not_in_use_student_id integer,
    relatedstudent_id integer NOT NULL
);


ALTER TABLE core_candidate OWNER TO dbdev;

--
-- Name: core_candidate_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_candidate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_candidate_id_seq OWNER TO dbdev;

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


ALTER TABLE core_deadline OWNER TO dbdev;

--
-- Name: core_deadline_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_deadline_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_deadline_id_seq OWNER TO dbdev;

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


ALTER TABLE core_delivery OWNER TO dbdev;

--
-- Name: core_delivery_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_delivery_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_delivery_id_seq OWNER TO dbdev;

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


ALTER TABLE core_devilryuserprofile OWNER TO dbdev;

--
-- Name: core_devilryuserprofile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_devilryuserprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_devilryuserprofile_id_seq OWNER TO dbdev;

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


ALTER TABLE core_filemeta OWNER TO dbdev;

--
-- Name: core_filemeta_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_filemeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_filemeta_id_seq OWNER TO dbdev;

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


ALTER TABLE core_groupinvite OWNER TO dbdev;

--
-- Name: core_groupinvite_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_groupinvite_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_groupinvite_id_seq OWNER TO dbdev;

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


ALTER TABLE core_node OWNER TO dbdev;

--
-- Name: core_node_admins; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_node_admins (
    id integer NOT NULL,
    node_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE core_node_admins OWNER TO dbdev;

--
-- Name: core_node_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_node_admins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_node_admins_id_seq OWNER TO dbdev;

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


ALTER TABLE core_node_id_seq OWNER TO dbdev;

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


ALTER TABLE core_period OWNER TO dbdev;

--
-- Name: core_period_admins; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_period_admins (
    id integer NOT NULL,
    period_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE core_period_admins OWNER TO dbdev;

--
-- Name: core_period_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_period_admins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_period_admins_id_seq OWNER TO dbdev;

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


ALTER TABLE core_period_id_seq OWNER TO dbdev;

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


ALTER TABLE core_periodapplicationkeyvalue OWNER TO dbdev;

--
-- Name: core_periodapplicationkeyvalue_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_periodapplicationkeyvalue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_periodapplicationkeyvalue_id_seq OWNER TO dbdev;

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


ALTER TABLE core_pointrangetograde OWNER TO dbdev;

--
-- Name: core_pointrangetograde_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_pointrangetograde_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_pointrangetograde_id_seq OWNER TO dbdev;

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


ALTER TABLE core_pointtogrademap OWNER TO dbdev;

--
-- Name: core_pointtogrademap_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_pointtogrademap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_pointtogrademap_id_seq OWNER TO dbdev;

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
    automatic_anonymous_id character varying(255) NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE core_relatedexaminer OWNER TO dbdev;

--
-- Name: core_relatedexaminer_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedexaminer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_relatedexaminer_id_seq OWNER TO dbdev;

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


ALTER TABLE core_relatedexaminersyncsystemtag OWNER TO dbdev;

--
-- Name: core_relatedexaminersyncsystemtag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedexaminersyncsystemtag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_relatedexaminersyncsystemtag_id_seq OWNER TO dbdev;

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


ALTER TABLE core_relatedstudent OWNER TO dbdev;

--
-- Name: core_relatedstudent_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedstudent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_relatedstudent_id_seq OWNER TO dbdev;

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


ALTER TABLE core_relatedstudentkeyvalue OWNER TO dbdev;

--
-- Name: core_relatedstudentkeyvalue_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedstudentkeyvalue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_relatedstudentkeyvalue_id_seq OWNER TO dbdev;

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


ALTER TABLE core_relatedstudentsyncsystemtag OWNER TO dbdev;

--
-- Name: core_relatedstudentsyncsystemtag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_relatedstudentsyncsystemtag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_relatedstudentsyncsystemtag_id_seq OWNER TO dbdev;

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


ALTER TABLE core_staticfeedback OWNER TO dbdev;

--
-- Name: core_staticfeedback_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_staticfeedback_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_staticfeedback_id_seq OWNER TO dbdev;

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


ALTER TABLE core_staticfeedbackfileattachment OWNER TO dbdev;

--
-- Name: core_staticfeedbackfileattachment_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_staticfeedbackfileattachment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_staticfeedbackfileattachment_id_seq OWNER TO dbdev;

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
    parentnode_id integer
);


ALTER TABLE core_subject OWNER TO dbdev;

--
-- Name: core_subject_admins; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE core_subject_admins (
    id integer NOT NULL,
    subject_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE core_subject_admins OWNER TO dbdev;

--
-- Name: core_subject_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_subject_admins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_subject_admins_id_seq OWNER TO dbdev;

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


ALTER TABLE core_subject_id_seq OWNER TO dbdev;

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


ALTER TABLE cradmin_generic_token_with_metadata_generictokenwithmetadata OWNER TO dbdev;

--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq OWNER TO dbdev;

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


ALTER TABLE cradmin_temporaryfileuploadstore_temporaryfile OWNER TO dbdev;

--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE cradmin_temporaryfileuploadstore_temporaryfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE cradmin_temporaryfileuploadstore_temporaryfile_id_seq OWNER TO dbdev;

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


ALTER TABLE cradmin_temporaryfileuploadstore_temporaryfilecollection OWNER TO dbdev;

--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_account_periodpermissiongroup OWNER TO dbdev;

--
-- Name: devilry_account_periodpermissiongroup_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_periodpermissiongroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_account_periodpermissiongroup_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_account_permissiongroup OWNER TO dbdev;

--
-- Name: devilry_account_permissiongroup_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_permissiongroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_account_permissiongroup_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_account_permissiongroupuser OWNER TO dbdev;

--
-- Name: devilry_account_permissiongroupuser_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_permissiongroupuser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_account_permissiongroupuser_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_account_subjectpermissiongroup OWNER TO dbdev;

--
-- Name: devilry_account_subjectpermissiongroup_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_subjectpermissiongroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_account_subjectpermissiongroup_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_account_user OWNER TO dbdev;

--
-- Name: devilry_account_user_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_account_user_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_account_useremail OWNER TO dbdev;

--
-- Name: devilry_account_useremail_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_useremail_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_account_useremail_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_account_username OWNER TO dbdev;

--
-- Name: devilry_account_username_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_account_username_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_account_username_id_seq OWNER TO dbdev;

--
-- Name: devilry_account_username_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_account_username_id_seq OWNED BY devilry_account_username.id;


--
-- Name: devilry_comment_comment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_comment_comment (
    id integer NOT NULL,
    text text NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    published_datetime timestamp with time zone NOT NULL,
    user_role character varying(42) NOT NULL,
    comment_type character varying(42) NOT NULL,
    parent_id integer,
    user_id integer NOT NULL,
    draft_text text NOT NULL
);


ALTER TABLE devilry_comment_comment OWNER TO dbdev;

--
-- Name: devilry_comment_comment_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_comment_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_comment_comment_id_seq OWNER TO dbdev;

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
    created_datetime timestamp with time zone NOT NULL,
    CONSTRAINT devilry_comment_commentfile_filesize_check CHECK ((filesize >= 0))
);


ALTER TABLE devilry_comment_commentfile OWNER TO dbdev;

--
-- Name: devilry_comment_commentfile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_comment_commentfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_comment_commentfile_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_comment_commentfileimage OWNER TO dbdev;

--
-- Name: devilry_comment_commentfileimage_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_comment_commentfileimage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_comment_commentfileimage_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_detektor_comparetwocacheitem OWNER TO dbdev;

--
-- Name: devilry_detektor_comparetwocacheitem_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_detektor_comparetwocacheitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_detektor_comparetwocacheitem_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_detektor_detektorassignment OWNER TO dbdev;

--
-- Name: devilry_detektor_detektorassignment_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_detektor_detektorassignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_detektor_detektorassignment_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_detektor_detektorassignmentcachelanguage OWNER TO dbdev;

--
-- Name: devilry_detektor_detektorassignmentcachelanguage_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_detektor_detektorassignmentcachelanguage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_detektor_detektorassignmentcachelanguage_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_detektor_detektordeliveryparseresult OWNER TO dbdev;

--
-- Name: devilry_detektor_detektordeliveryparseresult_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_detektor_detektordeliveryparseresult_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_detektor_detektordeliveryparseresult_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_gradingsystem_feedbackdraft OWNER TO dbdev;

--
-- Name: devilry_gradingsystem_feedbackdraft_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_gradingsystem_feedbackdraft_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_gradingsystem_feedbackdraft_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_gradingsystem_feedbackdraftfile OWNER TO dbdev;

--
-- Name: devilry_gradingsystem_feedbackdraftfile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_gradingsystem_feedbackdraftfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_gradingsystem_feedbackdraftfile_id_seq OWNER TO dbdev;

--
-- Name: devilry_gradingsystem_feedbackdraftfile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_gradingsystem_feedbackdraftfile_id_seq OWNED BY devilry_gradingsystem_feedbackdraftfile.id;


--
-- Name: devilry_group_feedbackset; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_group_feedbackset (
    id integer NOT NULL,
    grading_points integer,
    created_datetime timestamp with time zone NOT NULL,
    grading_published_datetime timestamp with time zone,
    deadline_datetime timestamp with time zone,
    created_by_id integer NOT NULL,
    group_id integer NOT NULL,
    grading_published_by_id integer,
    gradeform_data_json text NOT NULL,
    is_last_in_group boolean,
    feedbackset_type character varying(50) NOT NULL,
    CONSTRAINT devilry_group_feedbackset_grading_points_697ae108a5fe85ff_check CHECK ((grading_points >= 0))
);


ALTER TABLE devilry_group_feedbackset OWNER TO dbdev;

--
-- Name: devilry_group_feedbackset_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_group_feedbackset_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_group_feedbackset_id_seq OWNER TO dbdev;

--
-- Name: devilry_group_feedbackset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_group_feedbackset_id_seq OWNED BY devilry_group_feedbackset.id;


--
-- Name: devilry_group_groupcomment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_group_groupcomment (
    comment_ptr_id integer NOT NULL,
    feedback_set_id integer NOT NULL,
    part_of_grading boolean NOT NULL,
    visibility character varying(50) NOT NULL
);


ALTER TABLE devilry_group_groupcomment OWNER TO dbdev;

--
-- Name: devilry_group_imageannotationcomment; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_group_imageannotationcomment (
    comment_ptr_id integer NOT NULL,
    x_coordinate integer NOT NULL,
    y_coordinate integer NOT NULL,
    feedback_set_id integer NOT NULL,
    image_id integer NOT NULL,
    part_of_grading boolean NOT NULL,
    visibility character varying(50) NOT NULL,
    CONSTRAINT devilry_group_imageannotationcomment_x_coordinate_check CHECK ((x_coordinate >= 0)),
    CONSTRAINT devilry_group_imageannotationcomment_y_coordinate_check CHECK ((y_coordinate >= 0))
);


ALTER TABLE devilry_group_imageannotationcomment OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_deadlinetag; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_qualifiesforexam_deadlinetag (
    id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    tag character varying(30)
);


ALTER TABLE devilry_qualifiesforexam_deadlinetag OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_deadlinetag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_qualifiesforexam_deadlinetag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_qualifiesforexam_deadlinetag_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_qualifiesforexam_periodtag OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE devilry_qualifiesforexam_qualifiesforfinalexam (
    id integer NOT NULL,
    qualifies boolean,
    relatedstudent_id integer NOT NULL,
    status_id integer NOT NULL
);


ALTER TABLE devilry_qualifiesforexam_qualifiesforfinalexam OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_qualifiesforexam_qualifiesforfinalexam_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_qualifiesforexam_qualifiesforfinalexam_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_qualifiesforexam_status OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_status_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_qualifiesforexam_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_qualifiesforexam_status_id_seq OWNER TO dbdev;

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


ALTER TABLE devilry_student_uploadeddeliveryfile OWNER TO dbdev;

--
-- Name: devilry_student_uploadeddeliveryfile_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_student_uploadeddeliveryfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_student_uploadeddeliveryfile_id_seq OWNER TO dbdev;

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


ALTER TABLE django_admin_log OWNER TO dbdev;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_admin_log_id_seq OWNER TO dbdev;

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


ALTER TABLE django_content_type OWNER TO dbdev;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_content_type_id_seq OWNER TO dbdev;

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


ALTER TABLE django_migrations OWNER TO dbdev;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_migrations_id_seq OWNER TO dbdev;

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


ALTER TABLE django_session OWNER TO dbdev;

--
-- Name: ievv_batchframework_batchoperation; Type: TABLE; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE TABLE ievv_batchframework_batchoperation (
    id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    started_running_datetime timestamp with time zone,
    finished_datetime timestamp with time zone,
    context_object_id integer,
    operationtype character varying(255) NOT NULL,
    status character varying(12) NOT NULL,
    result character varying(13) NOT NULL,
    input_data_json text NOT NULL,
    output_data_json text NOT NULL,
    context_content_type_id integer,
    started_by_id integer,
    CONSTRAINT ievv_batchframework_batchoperation_context_object_id_check CHECK ((context_object_id >= 0))
);


ALTER TABLE ievv_batchframework_batchoperation OWNER TO dbdev;

--
-- Name: ievv_batchframework_batchoperation_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE ievv_batchframework_batchoperation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ievv_batchframework_batchoperation_id_seq OWNER TO dbdev;

--
-- Name: ievv_batchframework_batchoperation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE ievv_batchframework_batchoperation_id_seq OWNED BY ievv_batchframework_batchoperation.id;


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
-- Name: id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_batchframework_batchoperation ALTER COLUMN id SET DEFAULT nextval('ievv_batchframework_batchoperation_id_seq'::regclass);


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
166	Can add batch operation	56	add_batchoperation
167	Can change batch operation	56	change_batchoperation
168	Can delete batch operation	56	delete_batchoperation
\.


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('auth_permission_id_seq', 168, true);


--
-- Data for Name: core_assignment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignment (id, short_name, long_name, publishing_time, deprecated_field_anonymous, students_can_see_points, delivery_types, deadline_handling, scale_points_percent, first_deadline, max_points, passing_grade_min_points, points_to_grade_mapper, grading_system_plugin_id, students_can_create_groups, students_can_not_create_groups_after, feedback_workflow, parentnode_id, gradeform_setup_json, anonymizationmode, uses_custom_candidate_ids) FROM stdin;
1	assignment1	Assignment 1	2015-12-27 03:35:27.525662+01	f	t	0	0	100	2040-01-31 12:30:00+01	1	1	passed-failed	devilry_gradingsystemplugin_approved	f	\N		1	\N	off	f
3	semi-anonymous-exam	Semi anonymous exam	2016-01-19 12:30:00+01	f	f	0	0	100	2040-03-02 15:30:00+01	1	1	passed-failed	devilry_gradingsystemplugin_approved	f	\N		1		semi_anonymous	f
4	fully-anonymous-exam	Fully anonymous exam	2016-01-20 00:20:00+01	f	f	0	0	100	2040-03-15 23:59:00+01	1	1	passed-failed	devilry_gradingsystemplugin_approved	f	\N		1		fully_anonymous	f
2	assignment2	Assignment 2	2016-01-03 04:41:40.730958+01	f	t	0	0	100	2040-02-14 12:30:00+01	1	1	passed-failed	devilry_gradingsystemplugin_approved	f	\N		1	\N	off	f
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

SELECT pg_catalog.setval('core_assignment_id_seq', 4, true);


--
-- Data for Name: core_assignmentgroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgroup (id, name, is_open, etag, delivery_status, created_datetime, copied_from_id, feedback_id, last_deadline_id, parentnode_id, batchoperation_id) FROM stdin;
1		t	2016-01-20 11:17:01.6896+01	\N	2016-01-20 11:17:01.689048+01	\N	\N	\N	1	1
2		t	2016-01-20 11:17:01.689643+01	\N	2016-01-20 11:17:01.689109+01	\N	\N	\N	1	1
3		t	2016-01-20 11:17:01.689683+01	\N	2016-01-20 11:17:01.689159+01	\N	\N	\N	1	1
4		t	2016-01-20 11:17:01.689714+01	\N	2016-01-20 11:17:01.689207+01	\N	\N	\N	1	1
5		t	2016-01-20 11:17:01.689744+01	\N	2016-01-20 11:17:01.689254+01	\N	\N	\N	1	1
6		t	2016-01-20 11:17:01.689774+01	\N	2016-01-20 11:17:01.689303+01	\N	\N	\N	1	1
7		t	2016-01-20 11:17:01.689804+01	\N	2016-01-20 11:17:01.689349+01	\N	\N	\N	1	1
8		t	2016-01-20 11:17:01.689833+01	\N	2016-01-20 11:17:01.689396+01	\N	\N	\N	1	1
\.


--
-- Data for Name: core_assignmentgroup_examiners; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgroup_examiners (id, assignmentgroup_id, old_reference_not_in_use_user_id, relatedexaminer_id) FROM stdin;
1	1	\N	1
2	2	\N	1
3	4	\N	1
4	7	\N	1
\.


--
-- Name: core_assignmentgroup_examiners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgroup_examiners_id_seq', 4, true);


--
-- Name: core_assignmentgroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgroup_id_seq', 8, true);


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

COPY core_candidate (id, candidate_id, assignment_group_id, old_reference_not_in_use_student_id, relatedstudent_id) FROM stdin;
1	\N	1	\N	1
2	\N	2	\N	2
3	\N	3	\N	3
4	\N	4	\N	4
5	\N	5	\N	5
6	\N	6	\N	6
7	\N	7	\N	7
8	\N	8	\N	8
\.


--
-- Name: core_candidate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_candidate_id_seq', 8, true);


--
-- Data for Name: core_deadline; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_deadline (id, deadline, text, deliveries_available_before_deadline, why_created, added_by_id, assignment_group_id) FROM stdin;
\.


--
-- Name: core_deadline_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_deadline_id_seq', 1, false);


--
-- Data for Name: core_delivery; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_delivery (id, delivery_type, time_of_delivery, number, successful, alias_delivery_id, copy_of_id, deadline_id, delivered_by_id, last_feedback_id) FROM stdin;
\.


--
-- Name: core_delivery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_delivery_id_seq', 1, false);


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
\.


--
-- Name: core_filemeta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_filemeta_id_seq', 1, false);


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

SELECT pg_catalog.setval('core_node_id_seq', 1, false);


--
-- Data for Name: core_period; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_period (id, short_name, long_name, start_time, end_time, etag, parentnode_id) FROM stdin;
1	springaaaa	Spring AAAA	2015-01-01 00:00:00+01	2080-12-31 23:59:00+01	2015-12-26 21:31:34.148678+01	1
2	springoooo	Spring OOOO	2000-01-01 00:05:00+01	2010-12-31 23:59:00+01	2016-02-02 12:41:49.921204+01	1
3	springffff	Spring FFFF	2050-01-01 01:35:00+01	2144-12-31 20:10:00+01	2016-02-02 12:43:03.846893+01	1
4	springaaaa0	Spring AAAA0	2012-01-01 12:00:00+01	2049-12-31 23:59:00+01	2016-02-02 12:44:54.478439+01	2
5	springaaaa	Spring AAAA	2015-01-01 12:45:00+01	2055-07-31 12:45:00+02	2016-02-02 12:45:37.331893+01	2
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

SELECT pg_catalog.setval('core_period_id_seq', 5, true);


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

COPY core_relatedexaminer (id, tags, period_id, user_id, automatic_anonymous_id, active) FROM stdin;
1		1	1		t
\.


--
-- Name: core_relatedexaminer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedexaminer_id_seq', 1, true);


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
1				1	5	t
2				1	2	t
3				1	6	t
4				1	7	t
5				1	13	t
6				1	8	t
7				1	17	t
8				1	16	t
\.


--
-- Name: core_relatedstudent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedstudent_id_seq', 8, true);


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
\.


--
-- Name: core_staticfeedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_staticfeedback_id_seq', 1, false);


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
2	duck1100	Duck 1100 - Mathematical programming	2015-12-22 19:58:18.525346+01	\N
1	duck1010	Duck 1010 - object oriented programming	2015-12-22 19:57:16.969003+01	\N
\.


--
-- Data for Name: core_subject_admins; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_subject_admins (id, subject_id, user_id) FROM stdin;
\.


--
-- Name: core_subject_admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_subject_admins_id_seq', 3, true);


--
-- Name: core_subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_subject_id_seq', 2, true);


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
1	1	2
\.


--
-- Name: devilry_account_periodpermissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_periodpermissiongroup_id_seq', 1, true);


--
-- Data for Name: devilry_account_permissiongroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_permissiongroup (id, name, created_datetime, updated_datetime, syncsystem_update_datetime, grouptype, is_custom_manageable) FROM stdin;
1	The grandmas	2015-12-22 20:28:12.198719+01	2015-12-29 18:36:56.731725+01	\N	departmentadmin	f
2	duck1010.springaaaa admins	2016-01-20 04:17:30.493374+01	2016-01-20 04:18:08.798354+01	\N	periodadmin	f
3	duck1010 administrators	2016-01-20 04:19:42.353192+01	2016-01-20 04:19:42.353219+01	\N	subjectadmin	f
\.


--
-- Name: devilry_account_permissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_permissiongroup_id_seq', 3, true);


--
-- Data for Name: devilry_account_permissiongroupuser; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_permissiongroupuser (id, permissiongroup_id, user_id) FROM stdin;
1	1	1
2	2	12
3	3	14
\.


--
-- Name: devilry_account_permissiongroupuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_permissiongroupuser_id_seq', 3, true);


--
-- Data for Name: devilry_account_subjectpermissiongroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_subjectpermissiongroup (id, permissiongroup_id, subject_id) FROM stdin;
1	1	1
2	1	2
3	3	1
\.


--
-- Name: devilry_account_subjectpermissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_subjectpermissiongroup_id_seq', 3, true);


--
-- Data for Name: devilry_account_user; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_user (id, password, last_login, is_superuser, shortname, fullname, lastname, datetime_joined, suspended_datetime, suspended_reason, languagecode) FROM stdin;
2	md5$3KRT0BYBVYuO$94583357915e72f337fcd49100121ffe	\N	f	dewey@example.com	Dewey Duck	Duck	2016-01-03 00:01:23.904395+01	\N		
3	md5$4kh8cjMMXX2M$7ebf58c36489254b715d79608c022101	\N	f	louie@example.com	Louie Duck	Duck	2016-01-03 00:01:23.920971+01	\N		
4	md5$EC1N1bbdDH1I$f178f7136b3691e18906166ee0efe5ca	\N	f	huey@example.com	Huey Duck	Duck	2016-01-03 00:01:23.924138+01	\N		
5	md5$t9KMIxJyNWXg$7136c7c30e463d0c9525f4744ef624b4	\N	f	april@example.com	April Duck	Duck	2016-01-03 00:01:23.92689+01	\N		
6	md5$23r9I32HRrRt$a5d639300faf27693592f4fbe6d4a219	\N	f	june@example.com	June Duck	Duck	2016-01-03 00:01:23.929449+01	\N		
7	md5$sYwPNZrUONMA$ece17aeedb49985694e73ccfb673762d	\N	f	july@example.com	July Duck	Duck	2016-01-03 00:01:23.932129+01	\N		
8	md5$bl0XFjiSsbGA$7e0f3030e8bfd0d54b91ca7843f001a3	\N	f	baldr@example.com	God of Beauty	Beauty	2016-01-03 00:01:23.934793+01	\N		
9	md5$b0e7QxZQhDjm$0a0c289438bb10acd7791166f22c9302	\N	f	freyja@example.com	Goddess of Love	Love	2016-01-03 00:01:23.937304+01	\N		
10	md5$jGBsBCPiCfD4$721eefd1556ba7a2dccba060f243263e	\N	f	freyr@example.com	God of Fertility	Fertility	2016-01-03 00:01:23.939944+01	\N		
11	md5$jTwxxR6ybeuX$7de276d388672758ce0e1991f92ee2da	\N	f	kvasir@example.com	God of Inspiration	Inspiration	2016-01-03 00:01:23.942802+01	\N		
13	md5$BVeSKhUc4Gkg$c5cfb847e6ef2a84bf2a0a3ab0424e8d	\N	f	thor@example.com	God of thunder and Battle	Battle	2016-01-03 00:01:23.948728+01	\N		
15	md5$FQJM96zqt39y$49c4ad86e2d8bc053addcab6431db38d	\N	f	donald@example.com	Donald Duck	Duck	2016-01-03 00:03:43.101396+01	\N		
16	md5$IwVKSAdD2ueB$5e32c9a5bfa4092cdb4b4bda8a0e122e	\N	f	scrooge@example.com	Scrooge McDuck	McDuck	2016-01-03 00:03:59.432752+01	\N		
17	md5$VNqEOHzoWJLP$742f1d1b4d56fb6f51cdb76efc2105fa	\N	f	noname@example.com			2016-01-04 15:08:14.258809+01	\N		
18	md5$smoA02BvKYtp$17bc79166daf9d1c3de87d695e9708f9	\N	f	missingname@example.com			2016-01-04 15:25:10.473858+01	\N		
12	md5$tT0zXYv0Zsuo$2b9bfb86f295cfd461b0ce2bb6ea2096	2016-01-20 04:29:30.662494+01	f	loki@example.com	Trickster and god of Mischief	Mischief	2016-01-03 00:01:23.945768+01	\N		
14	md5$ot0qeIMptbS0$736743011a752ac3929d119435424766	2016-01-20 04:29:49.250064+01	f	odin@example.com	The "All Father"	Father"	2016-01-03 00:01:23.951457+01	\N		
1	md5$wqtfXF0fIxXj$894c06ca065b6dfa906004e40da2e9a4	2016-02-02 12:40:17.940186+01	t	grandma@example.com			2015-12-21 18:01:21.212212+01	\N		
\.


--
-- Name: devilry_account_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_user_id_seq', 18, true);


--
-- Data for Name: devilry_account_useremail; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_useremail (id, created_datetime, last_updated_datetime, email, use_for_notifications, is_primary, user_id) FROM stdin;
1	2015-12-21 18:01:21.217373+01	2015-12-21 18:01:21.217387+01	grandma@example.com	t	t	1
2	2016-01-03 00:01:23.917396+01	2016-01-03 00:01:23.917407+01	dewey@example.com	t	t	2
3	2016-01-03 00:01:23.923218+01	2016-01-03 00:01:23.923227+01	louie@example.com	t	t	3
4	2016-01-03 00:01:23.926121+01	2016-01-03 00:01:23.926129+01	huey@example.com	t	t	4
5	2016-01-03 00:01:23.928645+01	2016-01-03 00:01:23.928653+01	april@example.com	t	t	5
6	2016-01-03 00:01:23.93128+01	2016-01-03 00:01:23.931289+01	june@example.com	t	t	6
7	2016-01-03 00:01:23.934002+01	2016-01-03 00:01:23.934011+01	july@example.com	t	t	7
8	2016-01-03 00:01:23.936541+01	2016-01-03 00:01:23.93655+01	baldr@example.com	t	t	8
9	2016-01-03 00:01:23.939125+01	2016-01-03 00:01:23.939133+01	freyja@example.com	t	t	9
10	2016-01-03 00:01:23.941789+01	2016-01-03 00:01:23.941798+01	freyr@example.com	t	t	10
11	2016-01-03 00:01:23.944933+01	2016-01-03 00:01:23.944942+01	kvasir@example.com	t	t	11
12	2016-01-03 00:01:23.947901+01	2016-01-03 00:01:23.94791+01	loki@example.com	t	t	12
13	2016-01-03 00:01:23.950623+01	2016-01-03 00:01:23.950632+01	thor@example.com	t	t	13
14	2016-01-03 00:01:23.953328+01	2016-01-03 00:01:23.953336+01	odin@example.com	t	t	14
15	2016-01-03 00:03:43.104203+01	2016-01-03 00:03:43.104212+01	donald@example.com	t	t	15
16	2016-01-03 00:03:59.437075+01	2016-01-03 00:03:59.437084+01	scrooge@example.com	t	t	16
17	2016-01-04 15:08:14.270742+01	2016-01-04 15:08:14.270751+01	noname@example.com	t	t	17
18	2016-01-04 15:25:10.478871+01	2016-01-04 15:25:10.478885+01	missingname@example.com	t	t	18
\.


--
-- Name: devilry_account_useremail_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_useremail_id_seq', 18, true);


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

COPY devilry_comment_comment (id, text, created_datetime, published_datetime, user_role, comment_type, parent_id, user_id, draft_text) FROM stdin;
\.


--
-- Name: devilry_comment_comment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_comment_id_seq', 1, false);


--
-- Data for Name: devilry_comment_commentfile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_comment_commentfile (id, mimetype, file, filename, filesize, processing_started_datetime, processing_completed_datetime, processing_successful, comment_id, created_datetime) FROM stdin;
\.


--
-- Name: devilry_comment_commentfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_commentfile_id_seq', 1, false);


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

COPY devilry_group_feedbackset (id, grading_points, created_datetime, grading_published_datetime, deadline_datetime, created_by_id, group_id, grading_published_by_id, gradeform_data_json, is_last_in_group, feedbackset_type) FROM stdin;
1	\N	2016-01-20 11:17:01.702251+01	\N	\N	1	1	\N		t	feedbackset_type_first_try
2	\N	2016-01-20 11:17:01.702318+01	\N	\N	1	2	\N		t	feedbackset_type_first_try
3	\N	2016-01-20 11:17:01.702364+01	\N	\N	1	3	\N		t	feedbackset_type_first_try
4	\N	2016-01-20 11:17:01.702407+01	\N	\N	1	4	\N		t	feedbackset_type_first_try
5	\N	2016-01-20 11:17:01.702449+01	\N	\N	1	5	\N		t	feedbackset_type_first_try
6	\N	2016-01-20 11:17:01.702492+01	\N	\N	1	6	\N		t	feedbackset_type_first_try
7	\N	2016-01-20 11:17:01.702533+01	\N	\N	1	7	\N		t	feedbackset_type_first_try
8	\N	2016-01-20 11:17:01.702574+01	\N	\N	1	8	\N		t	feedbackset_type_first_try
\.


--
-- Name: devilry_group_feedbackset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_group_feedbackset_id_seq', 8, true);


--
-- Data for Name: devilry_group_groupcomment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_groupcomment (comment_ptr_id, feedback_set_id, part_of_grading, visibility) FROM stdin;
\.


--
-- Data for Name: devilry_group_imageannotationcomment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_imageannotationcomment (comment_ptr_id, x_coordinate, y_coordinate, feedback_set_id, image_id, part_of_grading, visibility) FROM stdin;
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
\.


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, false);


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
56	ievv_batchframework	batchoperation
\.


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_content_type_id_seq', 56, true);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	devilry_account	0001_initial	2015-12-21 17:44:43.106078+01
2	contenttypes	0001_initial	2015-12-21 17:44:43.126407+01
3	admin	0001_initial	2015-12-21 17:44:43.149901+01
4	contenttypes	0002_remove_content_type_name	2015-12-21 17:44:43.199763+01
5	auth	0001_initial	2015-12-21 17:44:43.270091+01
6	auth	0002_alter_permission_name_max_length	2015-12-21 17:44:43.289221+01
7	auth	0003_alter_user_email_max_length	2015-12-21 17:44:43.455186+01
8	auth	0004_alter_user_username_opts	2015-12-21 17:44:43.472573+01
9	auth	0005_alter_user_last_login_null	2015-12-21 17:44:43.490837+01
10	auth	0006_require_contenttypes_0002	2015-12-21 17:44:43.492859+01
11	core	0001_initial	2015-12-21 17:44:46.261903+01
12	core	0002_auto_20150915_1127	2015-12-21 17:44:46.406716+01
13	core	0003_auto_20150917_1537	2015-12-21 17:44:46.860766+01
14	core	0004_examiner_relatedexaminer	2015-12-21 17:44:46.937217+01
15	core	0005_relatedexaminer_automatic_anonymous_id	2015-12-21 17:44:47.021884+01
16	core	0006_auto_20151112_1851	2015-12-21 17:44:47.11235+01
17	cradmin_generic_token_with_metadata	0001_initial	2015-12-21 17:44:47.210303+01
18	cradmin_temporaryfileuploadstore	0001_initial	2015-12-21 17:44:47.391053+01
19	cradmin_temporaryfileuploadstore	0002_temporaryfilecollection_singlemode	2015-12-21 17:44:47.484874+01
20	cradmin_temporaryfileuploadstore	0003_temporaryfilecollection_max_filesize_bytes	2015-12-21 17:44:47.745798+01
21	cradmin_temporaryfileuploadstore	0004_auto_20151017_1947	2015-12-21 17:44:47.825118+01
22	devilry_account	0002_auto_20150917_1731	2015-12-21 17:44:48.504331+01
23	devilry_account	0003_datamigrate-admins-into-permissiongroups	2015-12-21 17:44:48.518457+01
24	devilry_comment	0001_initial	2015-12-21 17:44:48.813191+01
25	devilry_detektor	0001_initial	2015-12-21 17:44:49.795022+01
26	devilry_gradingsystem	0001_initial	2015-12-21 17:44:50.032368+01
27	devilry_group	0001_initial	2015-12-21 17:44:50.387487+01
28	devilry_qualifiesforexam	0001_initial	2015-12-21 17:44:51.178281+01
29	devilry_student	0001_initial	2015-12-21 17:44:51.441099+01
30	sessions	0001_initial	2015-12-21 17:44:51.461004+01
31	core	0007_auto_20151222_1955	2015-12-22 19:55:40.275339+01
32	devilry_account	0004_auto_20151222_1955	2015-12-22 19:55:40.423018+01
33	ievv_batchframework	0001_initial	2016-01-20 04:16:29.598382+01
34	core	0007_assignment_gradeform_setup_json	2016-01-20 04:16:29.669148+01
35	core	0008_auto_20151222_1955	2016-01-20 04:16:29.75359+01
36	core	0009_assignmentgroup_batchoperation	2016-01-20 04:16:29.825241+01
37	core	0010_assignment_anonymizationmode	2016-01-20 04:16:29.906544+01
38	core	0011_datamigrate_anonymous_to_anonymizationmode	2016-01-20 04:16:29.921259+01
39	core	0012_auto_20160111_2019	2016-01-20 04:16:29.99346+01
40	core	0013_auto_20160111_2021	2016-01-20 04:16:30.066276+01
41	core	0014_auto_20160112_1052	2016-01-20 04:16:30.202121+01
42	core	0015_assignment_uses_custom_candidate_ids	2016-01-20 04:16:30.288533+01
43	core	0016_auto_20160112_1831	2016-01-20 04:16:30.378829+01
44	core	0017_candidate_relatedstudent_replaces_student_field	2016-01-20 04:16:30.390553+01
45	core	0018_auto_20160112_1923	2016-01-20 04:16:30.569663+01
46	core	0019_auto_20160113_2037	2016-01-20 04:16:30.638242+01
47	core	0020_relatedexaminer_active	2016-01-20 04:16:30.95714+01
48	core	0021_examiner_relatedexaminer_replaces_user_field	2016-01-20 04:16:30.970697+01
49	core	0022_auto_20160114_1520	2016-01-20 04:16:31.05956+01
50	core	0023_auto_20160114_1522	2016-01-20 04:16:31.148027+01
51	core	0024_auto_20160114_1524	2016-01-20 04:16:31.232045+01
52	core	0025_auto_20160114_1525	2016-01-20 04:16:31.31417+01
53	core	0026_auto_20160114_1528	2016-01-20 04:16:31.389432+01
54	core	0027_auto_20160116_1843	2016-01-20 04:16:31.452886+01
55	core	0028_auto_20160119_0337	2016-01-20 04:16:31.528123+01
56	devilry_account	0005_auto_20160113_2037	2016-01-20 04:16:31.611411+01
57	devilry_comment	0002_auto_20160109_1210	2016-01-20 04:16:31.878484+01
58	devilry_comment	0003_auto_20160109_1239	2016-01-20 04:16:32.061092+01
59	devilry_comment	0004_commentfile_created_datetime	2016-01-20 04:16:32.153837+01
60	devilry_group	0002_feedbackset_gradeform_json	2016-01-20 04:16:32.266148+01
61	devilry_group	0003_auto_20160106_1418	2016-01-20 04:16:32.736409+01
62	devilry_group	0004_auto_20160107_0918	2016-01-20 04:16:33.18398+01
63	devilry_group	0005_auto_20160107_0958	2016-01-20 04:16:33.292917+01
64	devilry_group	0006_auto_20160107_1000	2016-01-20 04:16:33.405345+01
65	devilry_group	0007_auto_20160107_1031	2016-01-20 04:16:33.855025+01
66	devilry_group	0008_auto_20160107_1053	2016-01-20 04:16:34.313824+01
67	devilry_group	0009_auto_20160107_1100	2016-01-20 04:16:34.534037+01
68	devilry_group	0010_auto_20160107_1106	2016-01-20 04:16:34.956665+01
69	devilry_group	0011_auto_20160107_1111	2016-01-20 04:16:35.397259+01
70	devilry_group	0012_auto_20160107_1129	2016-01-20 04:16:36.046402+01
71	devilry_group	0013_auto_20160110_1621	2016-01-20 04:16:36.269064+01
72	devilry_group	0014_feedbackset_grading_status	2016-01-20 04:16:36.387384+01
73	devilry_group	0015_auto_20160111_1245	2016-01-20 04:16:36.615454+01
74	devilry_group	0016_auto_20160114_2202	2016-01-20 04:16:36.940232+01
75	devilry_account	0006_auto_20160120_0424	2016-02-02 12:40:04.478957+01
76	devilry_comment	0005_auto_20160122_1709	2016-02-02 12:40:04.57152+01
77	devilry_group	0017_auto_20160122_1518	2016-02-02 12:40:04.783329+01
78	devilry_group	0018_auto_20160122_1712	2016-02-02 12:40:04.889591+01
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_migrations_id_seq', 78, true);


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
wa141zb8nabz6ki0bgfqjn2bj9h9kfzt	YzU4YTcxNTM2MzJjNDU3MzJiNzJjZGQ0ODBmY2Y4MDVhNTE1ZDhiYjp7Il9hdXRoX3VzZXJfaGFzaCI6IjgyZjlkZGFiMzllZTc1MjAwMjRhZGNhMGUyNTNiMmFkNTVkMGQxMTMiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMSJ9	2016-01-04 18:01:46.760409+01
j0jnngoym8g5pm6rmx0mckp9n36qtd78	YzU4YTcxNTM2MzJjNDU3MzJiNzJjZGQ0ODBmY2Y4MDVhNTE1ZDhiYjp7Il9hdXRoX3VzZXJfaGFzaCI6IjgyZjlkZGFiMzllZTc1MjAwMjRhZGNhMGUyNTNiMmFkNTVkMGQxMTMiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMSJ9	2016-01-05 19:38:59.556246+01
2nzg0111f2w6vke3qqqmflhw9gn4wq6a	NDJiYzE0MzEyNjdjM2E0NGQ0ODY3OWUzZGQ2MzkyNjIxZjljNTFjZDp7Il9hdXRoX3VzZXJfaGFzaCI6IjViMjA4NzZkYjI5ZGY2ZmJlNDE4N2U1YjE1ZTAzZTIyMGRiYjBiN2QiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMSJ9	2016-02-03 04:16:53.965856+01
qwoxswhsr9bc739dsaz7n3z6sd7qli0x	NDc0YWYzYzRmOTJhNzJhZDczYjM5NjA4ZmUyNWM5NmE3OWU2NjRmMjp7Il9hdXRoX3VzZXJfaGFzaCI6IjkzZWZkMGU4YjA1ZjNmYmU2ZGUwYzY2OTUxNDY3MmM4MzA0ZDRjMjQiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMTIifQ==	2016-02-03 04:29:30.663964+01
nptdszmzzip61o80paabkskynqzn7xsg	YjZiOTUzMzEwOGYyNDlkNWZmZDdkOGFlMTEwZGI2ZGE4MGIwNDZlNDp7Il9hdXRoX3VzZXJfaGFzaCI6IjI1OWE4ODA1YTUyOGU1NTExMzc0ZTk2YjBlYTdmZTRiMzQwMTI3ZGIiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMTQifQ==	2016-02-03 04:29:49.251302+01
r52h3rqcsuj4x8qil0yiq701rzx660rw	NDJiYzE0MzEyNjdjM2E0NGQ0ODY3OWUzZGQ2MzkyNjIxZjljNTFjZDp7Il9hdXRoX3VzZXJfaGFzaCI6IjViMjA4NzZkYjI5ZGY2ZmJlNDE4N2U1YjE1ZTAzZTIyMGRiYjBiN2QiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMSJ9	2016-02-16 12:40:17.945791+01
\.


--
-- Data for Name: ievv_batchframework_batchoperation; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY ievv_batchframework_batchoperation (id, created_datetime, started_running_datetime, finished_datetime, context_object_id, operationtype, status, result, input_data_json, output_data_json, context_content_type_id, started_by_id) FROM stdin;
1	2016-01-20 11:17:01.683541+01	2016-01-20 11:17:01.681915+01	2016-01-20 11:17:01.708512+01	1	create-groups-with-candidate-and-feedbackset	running	successful			18	\N
\.


--
-- Name: ievv_batchframework_batchoperation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('ievv_batchframework_batchoperation_id_seq', 1, true);


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
-- Name: core_assignmentgroup_e_relatedexaminer_id_74db942d2f73e0d1_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT core_assignmentgroup_e_relatedexaminer_id_74db942d2f73e0d1_uniq UNIQUE (relatedexaminer_id, assignmentgroup_id);


--
-- Name: core_assignmentgroup_examiners_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT core_assignmentgroup_examiners_pkey PRIMARY KEY (id);


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
-- Name: devilry_group_feedbackset_group_id_4b67c434a334f6c0_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devilry_group_feedbackset_group_id_4b67c434a334f6c0_uniq UNIQUE (group_id, is_last_in_group);


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
-- Name: ievv_batchframework_batchoperation_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev; Tablespace: 
--

ALTER TABLE ONLY ievv_batchframework_batchoperation
    ADD CONSTRAINT ievv_batchframework_batchoperation_pkey PRIMARY KEY (id);


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
-- Name: core_assignment_ed066e54; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_ed066e54 ON core_assignment USING btree (anonymizationmode);


--
-- Name: core_assignment_long_name_74ff61759131213c_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_long_name_74ff61759131213c_like ON core_assignment USING btree (long_name varchar_pattern_ops);


--
-- Name: core_assignment_short_name_5a022141fd10855d_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignment_short_name_5a022141fd10855d_like ON core_assignment USING btree (short_name varchar_pattern_ops);


--
-- Name: core_assignmentgroup_3850dbd3; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX core_assignmentgroup_3850dbd3 ON core_assignmentgroup USING btree (batchoperation_id);


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

CREATE INDEX core_assignmentgroup_examiners_e8701ad4 ON core_assignmentgroup_examiners USING btree (old_reference_not_in_use_user_id);


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

CREATE INDEX core_candidate_30a811f6 ON core_candidate USING btree (old_reference_not_in_use_student_id);


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
-- Name: devilry_group_feedbackset_0069413d; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_feedbackset_0069413d ON devilry_group_feedbackset USING btree (feedbackset_type);


--
-- Name: devilry_group_feedbackset_0e939a4f; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_feedbackset_0e939a4f ON devilry_group_feedbackset USING btree (group_id);


--
-- Name: devilry_group_feedbackset_7dbe6d4c; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_feedbackset_7dbe6d4c ON devilry_group_feedbackset USING btree (grading_published_by_id);


--
-- Name: devilry_group_feedbackset_e93cb7eb; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_feedbackset_e93cb7eb ON devilry_group_feedbackset USING btree (created_by_id);


--
-- Name: devilry_group_groupcomment_c08198b8; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_groupcomment_c08198b8 ON devilry_group_groupcomment USING btree (feedback_set_id);


--
-- Name: devilry_group_groupcomment_f79b1d64; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_groupcomment_f79b1d64 ON devilry_group_groupcomment USING btree (visibility);


--
-- Name: devilry_group_imageannotationcomment_c08198b8; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_imageannotationcomment_c08198b8 ON devilry_group_imageannotationcomment USING btree (feedback_set_id);


--
-- Name: devilry_group_imageannotationcomment_f33175e6; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_imageannotationcomment_f33175e6 ON devilry_group_imageannotationcomment USING btree (image_id);


--
-- Name: devilry_group_imageannotationcomment_f79b1d64; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX devilry_group_imageannotationcomment_f79b1d64 ON devilry_group_imageannotationcomment USING btree (visibility);


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
-- Name: ievv_batchframework_batchope_operationtype_86db17563402048_like; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX ievv_batchframework_batchope_operationtype_86db17563402048_like ON ievv_batchframework_batchoperation USING btree (operationtype varchar_pattern_ops);


--
-- Name: ievv_batchframework_batchoperation_62c990b1; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX ievv_batchframework_batchoperation_62c990b1 ON ievv_batchframework_batchoperation USING btree (started_by_id);


--
-- Name: ievv_batchframework_batchoperation_651b6541; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX ievv_batchframework_batchoperation_651b6541 ON ievv_batchframework_batchoperation USING btree (context_content_type_id);


--
-- Name: ievv_batchframework_batchoperation_e9e6a554; Type: INDEX; Schema: public; Owner: dbdev; Tablespace: 
--

CREATE INDEX ievv_batchframework_batchoperation_e9e6a554 ON ievv_batchframework_batchoperation USING btree (operationtype);


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
-- Name: D3ec90dcce686786fa6cfc7940d91960; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT "D3ec90dcce686786fa6cfc7940d91960" FOREIGN KEY (batchoperation_id) REFERENCES ievv_batchframework_batchoperation(id) DEFERRABLE INITIALLY DEFERRED;


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
-- Name: D5fa89d5f0632cab40e16a17b5422861; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT "D5fa89d5f0632cab40e16a17b5422861" FOREIGN KEY (old_reference_not_in_use_student_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


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
-- Name: D8d96d0a9bf59345ab08863cddcf9249; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_batchframework_batchoperation
    ADD CONSTRAINT "D8d96d0a9bf59345ab08863cddcf9249" FOREIGN KEY (context_content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


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
-- Name: a8d214959af9e0c40bfad12ee683c8a0; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT a8d214959af9e0c40bfad12ee683c8a0 FOREIGN KEY (grading_published_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


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
-- Name: e2e901148f6cd8765ee8ce180b39118d; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT e2e901148f6cd8765ee8ce180b39118d FOREIGN KEY (old_reference_not_in_use_user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


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
-- Name: ievv__started_by_id_453323e9bb289a44_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_batchframework_batchoperation
    ADD CONSTRAINT ievv__started_by_id_453323e9bb289a44_fk_devilry_account_user_id FOREIGN KEY (started_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


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

