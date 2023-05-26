--
-- PostgreSQL database dump
--

-- Dumped from database version 10.1
-- Dumped by pg_dump version 10.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: devilry__assignment_first_deadline_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__assignment_first_deadline_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.first_deadline != OLD.first_deadline THEN
      UPDATE devilry_group_feedbackset
      SET deadline_datetime = NEW.first_deadline
      WHERE id IN (
              SELECT devilry_group_feedbackset.id
              FROM devilry_group_feedbackset
              INNER JOIN core_assignmentgroup ON
                  core_assignmentgroup.id = devilry_group_feedbackset.group_id
              WHERE
                core_assignmentgroup.parentnode_id = NEW.id
                AND
                feedbackset_type = 'first_attempt'
                AND
                deadline_datetime = OLD.first_deadline
          );
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__assignment_first_deadline_update() OWNER TO dbdev;

--
-- Name: devilry__collect_groupcachedata(integer); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__collect_groupcachedata(param_group_id integer) RETURNS record
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_groupcachedata RECORD;
BEGIN
    SELECT
        (
            SELECT id
            FROM devilry_group_feedbackset AS first_feedbackset
            WHERE group_id = param_group_id
            ORDER BY deadline_datetime ASC NULLS FIRST
            LIMIT 1
        ) AS first_feedbackset_id,
        (
            SELECT id
            FROM devilry_group_feedbackset AS last_feedbackset
            WHERE group_id = param_group_id and (
              last_feedbackset.feedbackset_type = 'first_attempt' OR
              last_feedbackset.feedbackset_type = 'new_attempt' OR
              last_feedbackset.feedbackset_type = 're_edit'
            )
            ORDER BY deadline_datetime DESC NULLS LAST
            LIMIT 1
        ) AS last_feedbackset_id,
        (
            SELECT id
            FROM devilry_group_feedbackset AS last_published_feedbackset
            WHERE
                group_id = param_group_id
                AND
                grading_published_datetime IS NOT NULL
            ORDER BY deadline_datetime DESC NULLS LAST
            LIMIT 1
        ) AS last_published_feedbackset_id,
        (
            SELECT COUNT(id)
            FROM devilry_group_feedbackset
            WHERE
                group_id = param_group_id
                AND
                feedbackset_type not like 'merge_%'
                AND
                feedbackset_type = 'new_attempt'
        ) AS new_attempt_count,
        (
            SELECT COUNT(devilry_group_groupcomment.comment_ptr_id)
            FROM devilry_group_groupcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_groupcomment.visibility = 'visible-to-everyone'
        ) AS public_total_comment_count,
        (
            SELECT COUNT(devilry_group_groupcomment.comment_ptr_id)
            FROM devilry_group_groupcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_groupcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_groupcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.text != ''
                AND
                devilry_comment_comment.user_role = 'student'
        ) AS public_student_comment_count,
        (
            SELECT COUNT(devilry_group_groupcomment.comment_ptr_id)
            FROM devilry_group_groupcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_groupcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_groupcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'examiner'
        ) AS public_examiner_comment_count,
        (
            SELECT COUNT(devilry_group_groupcomment.comment_ptr_id)
            FROM devilry_group_groupcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_groupcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_groupcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'admin'
        ) AS public_admin_comment_count,
        (
            SELECT COUNT(devilry_group_imageannotationcomment.comment_ptr_id)
            FROM devilry_group_imageannotationcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_imageannotationcomment.feedback_set_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_imageannotationcomment.visibility = 'visible-to-everyone'
        ) AS public_total_imageannotationcomment_count,
        (
            SELECT COUNT(devilry_group_imageannotationcomment.comment_ptr_id)
            FROM devilry_group_imageannotationcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_imageannotationcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_imageannotationcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_imageannotationcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'student'
        ) AS public_student_imageannotationcomment_count,
        (
            SELECT COUNT(devilry_group_imageannotationcomment.comment_ptr_id)
            FROM devilry_group_imageannotationcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_imageannotationcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_imageannotationcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_imageannotationcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'examiner'
        ) AS public_examiner_imageannotationcomment_count,
        (
            SELECT COUNT(devilry_group_imageannotationcomment.comment_ptr_id)
            FROM devilry_group_imageannotationcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_imageannotationcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_imageannotationcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_imageannotationcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'admin'
        ) AS public_admin_imageannotationcomment_count,
        (
            SELECT COUNT(devilry_comment_commentfile.id)
            FROM devilry_comment_commentfile
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_comment_commentfile.comment_id
            INNER JOIN devilry_group_groupcomment
                ON devilry_group_groupcomment.comment_ptr_id = devilry_comment_comment.id
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_groupcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'student'
        ) AS public_student_file_upload_count,
        (
            SELECT devilry_comment_comment.published_datetime
            FROM devilry_group_groupcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_groupcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_groupcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'student'
            ORDER BY devilry_comment_comment.published_datetime DESC NULLS LAST
            LIMIT 1
        ) AS last_public_groupcomment_by_student_datetime,
        (
            SELECT devilry_comment_comment.published_datetime
            FROM devilry_group_imageannotationcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_imageannotationcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_imageannotationcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_imageannotationcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'student'
            ORDER BY devilry_comment_comment.published_datetime DESC NULLS LAST
            LIMIT 1
        ) AS last_public_imageannotationcomment_by_student_datetime,
        (
            SELECT devilry_comment_comment.published_datetime
            FROM devilry_group_groupcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_groupcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_groupcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'examiner'
            ORDER BY devilry_comment_comment.published_datetime DESC NULLS LAST
            LIMIT 1
        ) AS last_public_groupcomment_by_examiner_datetime,
        (
            SELECT devilry_comment_comment.published_datetime
            FROM devilry_group_imageannotationcomment
            INNER JOIN devilry_group_feedbackset
                ON devilry_group_feedbackset.id = devilry_group_imageannotationcomment.feedback_set_id
            INNER JOIN devilry_comment_comment
                ON devilry_comment_comment.id = devilry_group_imageannotationcomment.comment_ptr_id
            WHERE
                devilry_group_feedbackset.group_id = param_group_id
                AND
                devilry_group_imageannotationcomment.visibility = 'visible-to-everyone'
                AND
                devilry_comment_comment.user_role = 'examiner'
            ORDER BY devilry_comment_comment.published_datetime DESC NULLS LAST
            LIMIT 1
        ) AS last_public_imageannotationcomment_by_examiner_datetime,
        (
            SELECT COUNT(id)
            FROM core_assignmentgroup_examiners
            WHERE
                assignmentgroup_id = param_group_id
        ) AS examiner_count,
        (
            SELECT COUNT(id)
            FROM core_candidate
            WHERE
                assignment_group_id = param_group_id
        ) AS candidate_count

    FROM core_assignmentgroup AS assignmentgroup
    WHERE id = param_group_id
    INTO var_groupcachedata;

    RETURN var_groupcachedata;
END
$$;


ALTER FUNCTION public.devilry__collect_groupcachedata(param_group_id integer) OWNER TO dbdev;

--
-- Name: devilry__create_first_feedbackset_in_group(integer, integer); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__create_first_feedbackset_in_group(param_group_id integer, param_assignment_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_assignment_first_deadline TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT first_deadline
    FROM core_assignment
    WHERE id = param_assignment_id
    INTO var_assignment_first_deadline;

    INSERT INTO devilry_group_feedbackset (
        group_id,
        created_datetime,
        deadline_datetime,
        feedbackset_type,
        gradeform_data_json,
        ignored,
        ignored_reason)
    VALUES (
        param_group_id,
        now(),
        var_assignment_first_deadline,
        'first_attempt',
        '',
        FALSE,
        '');
END
$$;


ALTER FUNCTION public.devilry__create_first_feedbackset_in_group(param_group_id integer, param_assignment_id integer) OWNER TO dbdev;

--
-- Name: devilry__get_group_id_from_comment_id(integer); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__get_group_id_from_comment_id(param_comment_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    SELECT devilry_group_feedbackset.group_id
    FROM devilry_comment_commentfile
    INNER JOIN devilry_comment_comment
        ON devilry_comment_comment.id = devilry_comment_commentfile.comment_id
    INNER JOIN devilry_group_groupcomment
        ON devilry_group_groupcomment.comment_ptr_id = devilry_comment_comment.id
    INNER JOIN devilry_group_feedbackset
        ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
    WHERE
        devilry_comment_comment.id = param_comment_id
    INTO var_group_id;

    RETURN var_group_id;
END
$$;


ALTER FUNCTION public.devilry__get_group_id_from_comment_id(param_comment_id integer) OWNER TO dbdev;

--
-- Name: devilry__get_group_id_from_feedbackset_id(integer); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__get_group_id_from_feedbackset_id(param_feedbackset_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    SELECT group_id
    FROM devilry_group_feedbackset
    WHERE id = param_feedbackset_id
    INTO var_group_id;

    RETURN var_group_id;
END
$$;


ALTER FUNCTION public.devilry__get_group_id_from_feedbackset_id(param_feedbackset_id integer) OWNER TO dbdev;

--
-- Name: devilry__largest_datetime(timestamp with time zone, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__largest_datetime(param_datetime1 timestamp with time zone, param_datetime2 timestamp with time zone) RETURNS timestamp with time zone
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF param_datetime1 IS NULL THEN
        RETURN param_datetime2;
    END IF;
    IF param_datetime2 IS NULL THEN
        RETURN param_datetime1;
    END IF;
    IF param_datetime1 > param_datetime2 THEN
        RETURN param_datetime1;
    END IF;
    return param_datetime2;
END
$$;


ALTER FUNCTION public.devilry__largest_datetime(param_datetime1 timestamp with time zone, param_datetime2 timestamp with time zone) OWNER TO dbdev;

--
-- Name: devilry__on_candidate_after_delete(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_candidate_after_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.assignment_group_id);
    RETURN OLD;
END
$$;


ALTER FUNCTION public.devilry__on_candidate_after_delete() OWNER TO dbdev;

--
-- Name: devilry__on_candidate_after_insert_or_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_candidate_after_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(NEW.assignment_group_id);
    IF TG_OP = 'UPDATE' AND NEW.assignment_group_id != OLD.assignment_group_id THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.assignment_group_id);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_candidate_after_insert_or_update() OWNER TO dbdev;

--
-- Name: devilry__on_candidate_delete_add_history(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_candidate_delete_add_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF EXISTS (
              SELECT 1
              FROM core_assignmentgroup
              WHERE id = OLD.assignment_group_id AND internal_is_being_deleted = TRUE
            ) THEN
            RETURN NULL;
        END IF;

        SELECT user_id
        FROM core_relatedstudent
        WHERE id = OLD.relatedstudent_id
        INTO var_user_id;
        INSERT INTO core_candidateassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            OLD.assignment_group_id,
            var_user_id,
            now(),
            FALSE);
        RETURN OLD;
    END IF;
END
$$;


ALTER FUNCTION public.devilry__on_candidate_delete_add_history() OWNER TO dbdev;

--
-- Name: devilry__on_candidate_insert_add_history(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_candidate_insert_add_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT user_id
        FROM core_relatedstudent
        WHERE id = NEW.relatedstudent_id
        INTO var_user_id;
        INSERT INTO core_candidateassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            NEW.assignment_group_id,
            var_user_id,
            now(),
            TRUE);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_candidate_insert_add_history() OWNER TO dbdev;

--
-- Name: devilry__on_candidate_update_add_history(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_candidate_update_add_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.assignment_group_id <> OLD.assignment_group_id THEN
        SELECT user_id
        FROM core_relatedstudent
        WHERE id = NEW.relatedstudent_id
        INTO var_user_id;

        -- We create a history entry for the group the user was added to.
        INSERT INTO core_candidateassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            NEW.assignment_group_id,
            var_user_id,
            now(),
            TRUE);

        -- And we create a history entry for the group the user was removed from.
        INSERT INTO core_candidateassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            OLD.assignment_group_id,
            var_user_id,
            now(),
            FALSE);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_candidate_update_add_history() OWNER TO dbdev;

--
-- Name: devilry__on_comment_text_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_comment_text_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_existing_commentedithistory_id INTEGER;
BEGIN
    IF OLD.id != NEW.id THEN
        RAISE EXCEPTION 'OLD.id #% != NEW.id #%', OLD.id, NEW.id;
    END IF;

    SELECT id
    FROM devilry_comment_commentedithistory
    WHERE edited_datetime = now() AND comment_id = NEW.id
    INTO var_existing_commentedithistory_id;

    IF TG_OP = 'UPDATE' AND var_existing_commentedithistory_id IS NULL THEN
        INSERT INTO devilry_comment_commentedithistory (
            comment_id,
            edited_by_id,
            edited_datetime,
            pre_edit_text,
            post_edit_text)
        VALUES (
            NEW.id,
            NEW.user_id,
            now(),
            OLD.text,
            NEW.text);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_comment_text_update() OWNER TO dbdev;

--
-- Name: devilry__on_commentfile_after_delete(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_commentfile_after_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_comment_id(OLD.comment_id);
    IF var_group_id IS NOT NULL THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    END IF;
    RETURN OLD;
END
$$;


ALTER FUNCTION public.devilry__on_commentfile_after_delete() OWNER TO dbdev;

--
-- Name: devilry__on_commentfile_after_insert_or_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_commentfile_after_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_comment_id(NEW.comment_id);
    IF var_group_id IS NOT NULL THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_commentfile_after_insert_or_update() OWNER TO dbdev;

--
-- Name: devilry__on_examiner_after_delete(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_examiner_after_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.assignmentgroup_id);
    RETURN OLD;
END
$$;


ALTER FUNCTION public.devilry__on_examiner_after_delete() OWNER TO dbdev;

--
-- Name: devilry__on_examiner_after_insert_or_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_examiner_after_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(NEW.assignmentgroup_id);
    IF TG_OP = 'UPDATE' AND NEW.assignmentgroup_id != OLD.assignmentgroup_id THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.assignmentgroup_id);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_examiner_after_insert_or_update() OWNER TO dbdev;

--
-- Name: devilry__on_examiner_delete_add_history(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_examiner_delete_add_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF EXISTS (
                SELECT 1
                FROM core_assignmentgroup
                WHERE id = OLD.assignmentgroup_id AND internal_is_being_deleted = TRUE
            ) THEN
            RETURN NULL;
        END IF;

        SELECT user_id
        FROM core_relatedexaminer
        WHERE id = OLD.relatedexaminer_id
        INTO var_user_id;
        INSERT INTO core_examinerassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            OLD.assignmentgroup_id,
            var_user_id,
            now(),
            FALSE);
        RETURN OLD;
    END IF;
END
$$;


ALTER FUNCTION public.devilry__on_examiner_delete_add_history() OWNER TO dbdev;

--
-- Name: devilry__on_examiner_insert_add_history(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_examiner_insert_add_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT user_id
        FROM core_relatedexaminer
        WHERE id = NEW.relatedexaminer_id
        INTO var_user_id;
        INSERT INTO core_examinerassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            NEW.assignmentgroup_id,
            var_user_id,
            now(),
            TRUE);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_examiner_insert_add_history() OWNER TO dbdev;

--
-- Name: devilry__on_examiner_update_add_history(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_examiner_update_add_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.assignmentgroup_id <> OLD.assignmentgroup_id THEN
        SELECT user_id
        FROM core_relatedexaminer
        WHERE id = NEW.relatedexaminer_id
        INTO var_user_id;

        -- We create a history entry for the group the user was added to.
        INSERT INTO core_examinerassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            NEW.assignmentgroup_id,
            var_user_id,
            now(),
            TRUE);

        -- And we create a history entry for the group the user was removed from.
        INSERT INTO core_examinerassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            OLD.assignmentgroup_id,
            var_user_id,
            now(),
            FALSE);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_examiner_update_add_history() OWNER TO dbdev;

--
-- Name: devilry__on_feedbackset_after_delete(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_feedbackset_after_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.group_id);
    RETURN OLD;
END
$$;


ALTER FUNCTION public.devilry__on_feedbackset_after_delete() OWNER TO dbdev;

--
-- Name: devilry__on_feedbackset_after_insert_or_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_feedbackset_after_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(NEW.group_id);
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_feedbackset_after_insert_or_update() OWNER TO dbdev;

--
-- Name: devilry__on_feedbackset_before_insert_or_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_feedbackset_before_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF pg_trigger_depth() = 1 THEN
        -- We do not validate when this is triggered via another trigger.
        -- We assume the other trigger creates/updates the feedbackset
        -- correctly.
        PERFORM devilry__validate_feedbackset_change(NEW, TG_OP);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_feedbackset_before_insert_or_update() OWNER TO dbdev;

--
-- Name: devilry__on_feedbackset_deadline_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_feedbackset_deadline_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.deadline_datetime <> OLD.deadline_datetime THEN
        INSERT INTO devilry_group_feedbacksetdeadlinehistory (
            feedback_set_id,
            changed_datetime,
            changed_by_id,
            deadline_old,
            deadline_new)
        VALUES (
            NEW.id,
            now(),
            NEW.last_updated_by_id,
            OLD.deadline_datetime,
            NEW.deadline_datetime);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_feedbackset_deadline_update() OWNER TO dbdev;

--
-- Name: devilry__on_feedbackset_grading_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_feedbackset_grading_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.grading_points <> OLD.grading_points THEN
        INSERT INTO devilry_group_feedbacksetgradingupdatehistory (
            feedback_set_id,
            updated_by_id,
            updated_datetime,
            old_grading_points,
            old_grading_published_by_id,
            old_grading_published_datetime)
        VALUES (
            NEW.id,
            NEW.last_updated_by_id,
            now(),
            OLD.grading_points,
            OLD.grading_published_by_id,
            OLD.grading_published_datetime);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_feedbackset_grading_update() OWNER TO dbdev;

--
-- Name: devilry__on_group_comment_text_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_group_comment_text_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_comment_edit_history_id INTEGER;
BEGIN
    IF OLD.comment_ptr_id != NEW.comment_ptr_id THEN
        RAISE EXCEPTION 'OLD.comment_ptr_id #% != NEW.comment_ptr_id #%', OLD.comment_ptr_id, NEW.comment_ptr_id;
    END IF;

    SELECT id
    FROM devilry_comment_commentedithistory
    WHERE comment_id = NEW.comment_ptr_id AND edited_datetime = now()
    INTO var_comment_edit_history_id;

    IF TG_OP = 'UPDATE' AND var_comment_edit_history_id IS NOT NULL THEN
        INSERT INTO devilry_group_groupcommentedithistory (
            commentedithistory_ptr_id,
            group_comment_id,
            visibility)
        VALUES (
            var_comment_edit_history_id,
            OLD.comment_ptr_id,
            OLD.VISIBILITY);
    END IF;
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_group_comment_text_update() OWNER TO dbdev;

--
-- Name: devilry__on_groupcomment_after_delete(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_groupcomment_after_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_feedbackset_id(OLD.feedback_set_id);
    PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    RETURN OLD;
END
$$;


ALTER FUNCTION public.devilry__on_groupcomment_after_delete() OWNER TO dbdev;

--
-- Name: devilry__on_groupcomment_after_insert_or_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_groupcomment_after_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_feedbackset_id(NEW.feedback_set_id);
    PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_groupcomment_after_insert_or_update() OWNER TO dbdev;

--
-- Name: devilry__on_imageannotationcomment_after_delete(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_imageannotationcomment_after_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_feedbackset_id(OLD.feedback_set_id);
    PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    RETURN OLD;
END
$$;


ALTER FUNCTION public.devilry__on_imageannotationcomment_after_delete() OWNER TO dbdev;

--
-- Name: devilry__on_imageannotationcomment_after_insert_or_update(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__on_imageannotationcomment_after_insert_or_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_feedbackset_id(NEW.feedback_set_id);
    PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry__on_imageannotationcomment_after_insert_or_update() OWNER TO dbdev;

--
-- Name: devilry__rebuild_assignmentgroupcacheddata(integer); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__rebuild_assignmentgroupcacheddata(param_group_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_groupcachedata RECORD;
    var_last_public_comment_by_student_datetime timestamp with time zone;
    var_last_public_comment_by_examiner_datetime timestamp with time zone;

BEGIN
    IF EXISTS (SELECT 1 FROM core_assignmentgroup WHERE id = param_group_id AND internal_is_being_deleted = true) THEN
        RETURN;
    END IF;

    var_groupcachedata = devilry__collect_groupcachedata(param_group_id);
    var_last_public_comment_by_student_datetime = devilry__largest_datetime(
        var_groupcachedata.last_public_groupcomment_by_student_datetime,
        var_groupcachedata.last_public_imageannotationcomment_by_student_datetime
    );
    var_last_public_comment_by_examiner_datetime = devilry__largest_datetime(
        var_groupcachedata.last_public_groupcomment_by_examiner_datetime,
        var_groupcachedata.last_public_imageannotationcomment_by_examiner_datetime
    );
    IF EXISTS (SELECT 1 FROM core_assignmentgroup WHERE id = param_group_id) THEN
        INSERT INTO devilry_dbcache_assignmentgroupcacheddata (
            group_id,
            first_feedbackset_id,
            last_feedbackset_id,
            last_published_feedbackset_id,
            new_attempt_count,
            public_total_comment_count,
            public_student_comment_count,
            public_examiner_comment_count,
            public_admin_comment_count,
            public_student_file_upload_count,
            last_public_comment_by_student_datetime,
            last_public_comment_by_examiner_datetime,
            examiner_count,
            candidate_count)
        VALUES (
            param_group_id,
            var_groupcachedata.first_feedbackset_id,
            var_groupcachedata.last_feedbackset_id,
            var_groupcachedata.last_published_feedbackset_id,
            var_groupcachedata.new_attempt_count,
            var_groupcachedata.public_total_comment_count + var_groupcachedata.public_total_imageannotationcomment_count,
            var_groupcachedata.public_student_comment_count + var_groupcachedata.public_student_imageannotationcomment_count,
            var_groupcachedata.public_examiner_comment_count + var_groupcachedata.public_examiner_imageannotationcomment_count,
            var_groupcachedata.public_admin_comment_count + var_groupcachedata.public_admin_imageannotationcomment_count,
            var_groupcachedata.public_student_file_upload_count,
            var_last_public_comment_by_student_datetime,
            var_last_public_comment_by_examiner_datetime,
            var_groupcachedata.examiner_count,
            var_groupcachedata.candidate_count
        )
        ON CONFLICT(group_id)
        DO UPDATE SET
            first_feedbackset_id = var_groupcachedata.first_feedbackset_id,
            last_feedbackset_id = var_groupcachedata.last_feedbackset_id,
            last_published_feedbackset_id = var_groupcachedata.last_published_feedbackset_id,
            new_attempt_count = var_groupcachedata.new_attempt_count,
            public_total_comment_count = var_groupcachedata.public_total_comment_count + var_groupcachedata.public_total_imageannotationcomment_count,
            public_student_comment_count = var_groupcachedata.public_student_comment_count + var_groupcachedata.public_student_imageannotationcomment_count,
            public_examiner_comment_count = var_groupcachedata.public_examiner_comment_count + var_groupcachedata.public_examiner_imageannotationcomment_count,
            public_admin_comment_count = var_groupcachedata.public_admin_comment_count + var_groupcachedata.public_admin_imageannotationcomment_count,
            public_student_file_upload_count = var_groupcachedata.public_student_file_upload_count,
            last_public_comment_by_student_datetime = var_last_public_comment_by_student_datetime,
            last_public_comment_by_examiner_datetime = var_last_public_comment_by_examiner_datetime,
            examiner_count = var_groupcachedata.examiner_count,
            candidate_count = var_groupcachedata.candidate_count;
    END IF;
END
$$;


ALTER FUNCTION public.devilry__rebuild_assignmentgroupcacheddata(param_group_id integer) OWNER TO dbdev;

--
-- Name: devilry__rebuild_assignmentgroupcacheddata_for_period(integer); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__rebuild_assignmentgroupcacheddata_for_period(param_period_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    var_group_id integer;
BEGIN
    RAISE NOTICE 'Rebuilding data cache all AssignmentGroups in Period#% into table AssignmentGroupCachedData.', param_period_id;

    FOR var_group_id IN
        SELECT
            core_assignmentgroup.id
        FROM core_assignmentgroup
        INNER JOIN core_assignment
            ON core_assignment.id = core_assignmentgroup.parentnode_id
        WHERE
            core_assignment.parentnode_id = param_period_id
    LOOP
        PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    END LOOP;

    RAISE NOTICE 'Rebuilding data cache for Period#% finished.', param_period_id;
END
$$;


ALTER FUNCTION public.devilry__rebuild_assignmentgroupcacheddata_for_period(param_period_id integer) OWNER TO dbdev;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: devilry_group_feedbackset; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_group_feedbackset (
    id integer NOT NULL,
    grading_points integer,
    created_datetime timestamp with time zone NOT NULL,
    grading_published_datetime timestamp with time zone,
    deadline_datetime timestamp with time zone NOT NULL,
    created_by_id integer,
    group_id integer NOT NULL,
    grading_published_by_id integer,
    gradeform_data_json text NOT NULL,
    feedbackset_type character varying(50) NOT NULL,
    ignored boolean NOT NULL,
    ignored_reason text NOT NULL,
    ignored_datetime timestamp with time zone,
    last_updated_by_id integer,
    CONSTRAINT devilry_group_feedbackset_grading_points_697ae108a5fe85ff_check CHECK ((grading_points >= 0))
);


ALTER TABLE devilry_group_feedbackset OWNER TO dbdev;

--
-- Name: devilry__validate_feedbackset_change(devilry_group_feedbackset, text); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry__validate_feedbackset_change(param_feedbackset devilry_group_feedbackset, param_tg_op text) RETURNS void
    LANGUAGE plpgsql
    AS $$
-- DECLARE
--     var_first_feedbackset_id integer;
--     var_draft_feedbackset_id integer;
--     var_is_first_feedbackset boolean;
BEGIN

--     SELECT id
--     FROM devilry_group_feedbackset
--     WHERE group_id = param_feedbackset.group_id
--     ORDER BY deadline_datetime ASC NULLS FIRST
--     LIMIT 1
--     INTO var_first_feedbackset_id;
--
--     var_is_first_feedbackset = false;
--     IF var_first_feedbackset_id IS NULL THEN
--         var_is_first_feedbackset = true;
--     ELSE
--         IF param_tg_op = 'UPDATE' AND param_feedbackset.id = var_first_feedbackset_id THEN
--             var_is_first_feedbackset = true;
--         END IF;
--     END IF;
--
--     IF var_is_first_feedbackset THEN
--         IF param_feedbackset.deadline_datetime IS NOT NULL THEN
--             RAISE EXCEPTION integrity_constraint_violation
--                 USING MESSAGE = 'The first FeedbackSet in an AssignmentGroup must have deadline_datetime=NULL';
--         END IF;
--     ELSE
--         IF param_feedbackset.deadline_datetime IS NULL THEN
--             RAISE EXCEPTION integrity_constraint_violation
--                 USING MESSAGE = 'Only the first FeedbackSet in an AssignmentGroup can have deadline_datetime=NULL';
--         END IF;
--     END IF;

-- --     RAISE LOG 'param_feedbackset: %', param_feedbackset;
-- --     RAISE LOG 'var_is_first_feedbackset: %', var_is_first_feedbackset;
END
$$;


ALTER FUNCTION public.devilry__validate_feedbackset_change(param_feedbackset devilry_group_feedbackset, param_tg_op text) OWNER TO dbdev;

--
-- Name: devilry_dbcache_on_assignmentgroup_insert(); Type: FUNCTION; Schema: public; Owner: dbdev
--

CREATE FUNCTION devilry_dbcache_on_assignmentgroup_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM devilry__create_first_feedbackset_in_group(NEW.id, NEW.parentnode_id);
    RETURN NEW;
END
$$;


ALTER FUNCTION public.devilry_dbcache_on_assignmentgroup_insert() OWNER TO dbdev;

--
-- Name: account_emailaddress; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE account_emailaddress (
    id integer NOT NULL,
    email character varying(254) NOT NULL,
    verified boolean NOT NULL,
    "primary" boolean NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE account_emailaddress OWNER TO dbdev;

--
-- Name: account_emailaddress_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE account_emailaddress_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE account_emailaddress_id_seq OWNER TO dbdev;

--
-- Name: account_emailaddress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE account_emailaddress_id_seq OWNED BY account_emailaddress.id;


--
-- Name: account_emailconfirmation; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE account_emailconfirmation (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    sent timestamp with time zone,
    key character varying(64) NOT NULL,
    email_address_id integer NOT NULL
);


ALTER TABLE account_emailconfirmation OWNER TO dbdev;

--
-- Name: account_emailconfirmation_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE account_emailconfirmation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE account_emailconfirmation_id_seq OWNER TO dbdev;

--
-- Name: account_emailconfirmation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE account_emailconfirmation_id_seq OWNED BY account_emailconfirmation.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_assignment; Type: TABLE; Schema: public; Owner: dbdev
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
    first_deadline timestamp with time zone NOT NULL,
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
-- Name: core_assignment_admins; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_assignmentgroup; Type: TABLE; Schema: public; Owner: dbdev
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
    batchoperation_id integer,
    internal_is_being_deleted boolean NOT NULL
);


ALTER TABLE core_assignmentgroup OWNER TO dbdev;

--
-- Name: core_assignmentgroup_examiners; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_assignmentgrouphistory; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE core_assignmentgrouphistory (
    id integer NOT NULL,
    merge_history_json text NOT NULL,
    assignment_group_id integer NOT NULL
);


ALTER TABLE core_assignmentgrouphistory OWNER TO dbdev;

--
-- Name: core_assignmentgrouphistory_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_assignmentgrouphistory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_assignmentgrouphistory_id_seq OWNER TO dbdev;

--
-- Name: core_assignmentgrouphistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_assignmentgrouphistory_id_seq OWNED BY core_assignmentgrouphistory.id;


--
-- Name: core_assignmentgrouptag; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_candidate; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_candidateassignmentgrouphistory; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE core_candidateassignmentgrouphistory (
    id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    is_add boolean NOT NULL,
    assignment_group_id integer NOT NULL,
    user_id integer
);


ALTER TABLE core_candidateassignmentgrouphistory OWNER TO dbdev;

--
-- Name: core_candidateassignmentgrouphistory_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_candidateassignmentgrouphistory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_candidateassignmentgrouphistory_id_seq OWNER TO dbdev;

--
-- Name: core_candidateassignmentgrouphistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_candidateassignmentgrouphistory_id_seq OWNED BY core_candidateassignmentgrouphistory.id;


--
-- Name: core_deadline; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_delivery; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_devilryuserprofile; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_examinerassignmentgrouphistory; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE core_examinerassignmentgrouphistory (
    id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    is_add boolean NOT NULL,
    assignment_group_id integer NOT NULL,
    user_id integer
);


ALTER TABLE core_examinerassignmentgrouphistory OWNER TO dbdev;

--
-- Name: core_examinerassignmentgrouphistory_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_examinerassignmentgrouphistory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_examinerassignmentgrouphistory_id_seq OWNER TO dbdev;

--
-- Name: core_examinerassignmentgrouphistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_examinerassignmentgrouphistory_id_seq OWNED BY core_examinerassignmentgrouphistory.id;


--
-- Name: core_filemeta; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_groupinvite; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_period; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_period_admins; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_periodapplicationkeyvalue; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_periodtag; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE core_periodtag (
    id integer NOT NULL,
    prefix character varying(30) NOT NULL,
    tag text NOT NULL,
    is_hidden boolean NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    modified_datetime timestamp with time zone,
    period_id integer NOT NULL
);


ALTER TABLE core_periodtag OWNER TO dbdev;

--
-- Name: core_periodtag_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_periodtag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_periodtag_id_seq OWNER TO dbdev;

--
-- Name: core_periodtag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_periodtag_id_seq OWNED BY core_periodtag.id;


--
-- Name: core_periodtag_relatedexaminers; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE core_periodtag_relatedexaminers (
    id integer NOT NULL,
    periodtag_id integer NOT NULL,
    relatedexaminer_id integer NOT NULL
);


ALTER TABLE core_periodtag_relatedexaminers OWNER TO dbdev;

--
-- Name: core_periodtag_relatedexaminers_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_periodtag_relatedexaminers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_periodtag_relatedexaminers_id_seq OWNER TO dbdev;

--
-- Name: core_periodtag_relatedexaminers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_periodtag_relatedexaminers_id_seq OWNED BY core_periodtag_relatedexaminers.id;


--
-- Name: core_periodtag_relatedstudents; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE core_periodtag_relatedstudents (
    id integer NOT NULL,
    periodtag_id integer NOT NULL,
    relatedstudent_id integer NOT NULL
);


ALTER TABLE core_periodtag_relatedstudents OWNER TO dbdev;

--
-- Name: core_periodtag_relatedstudents_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE core_periodtag_relatedstudents_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE core_periodtag_relatedstudents_id_seq OWNER TO dbdev;

--
-- Name: core_periodtag_relatedstudents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE core_periodtag_relatedstudents_id_seq OWNED BY core_periodtag_relatedstudents.id;


--
-- Name: core_pointrangetograde; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_pointtogrademap; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_relatedexaminer; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_relatedstudent; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_relatedstudentkeyvalue; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_staticfeedback; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_staticfeedbackfileattachment; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: core_subject; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE core_subject (
    id integer NOT NULL,
    short_name character varying(20) NOT NULL,
    long_name character varying(100) NOT NULL,
    etag timestamp with time zone NOT NULL
);


ALTER TABLE core_subject OWNER TO dbdev;

--
-- Name: core_subject_admins; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadata; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: cradmin_temporaryfileuploadstore_temporaryfile; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_account_periodpermissiongroup; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_account_permissiongroup; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_account_permissiongroupuser; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_account_subjectpermissiongroup; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_account_user; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_account_useremail; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_account_username; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_comment_comment; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_comment_comment (
    id integer NOT NULL,
    text text NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    published_datetime timestamp with time zone NOT NULL,
    user_role character varying(42) NOT NULL,
    comment_type character varying(42) NOT NULL,
    parent_id integer,
    user_id integer,
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
-- Name: devilry_comment_commentedithistory; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_comment_commentedithistory (
    id integer NOT NULL,
    edited_datetime timestamp with time zone NOT NULL,
    post_edit_text text NOT NULL,
    pre_edit_text text NOT NULL,
    comment_id integer NOT NULL,
    edited_by_id integer
);


ALTER TABLE devilry_comment_commentedithistory OWNER TO dbdev;

--
-- Name: devilry_comment_commentedithistory_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_comment_commentedithistory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_comment_commentedithistory_id_seq OWNER TO dbdev;

--
-- Name: devilry_comment_commentedithistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_comment_commentedithistory_id_seq OWNED BY devilry_comment_commentedithistory.id;


--
-- Name: devilry_comment_commentfile; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_comment_commentfile (
    id integer NOT NULL,
    mimetype character varying(255) NOT NULL,
    file character varying(512) NOT NULL,
    filename character varying(255) NOT NULL,
    filesize integer NOT NULL,
    processing_started_datetime timestamp with time zone,
    processing_completed_datetime timestamp with time zone,
    processing_successful boolean NOT NULL,
    comment_id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    v2_id character varying(255) NOT NULL,
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
-- Name: devilry_comment_commentfileimage; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_compressionutil_compressedarchivemeta; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_compressionutil_compressedarchivemeta (
    id integer NOT NULL,
    content_object_id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    archive_name character varying(200) NOT NULL,
    archive_path character varying(200) NOT NULL,
    archive_size bigint NOT NULL,
    content_type_id integer NOT NULL,
    backend_id character varying(100) NOT NULL,
    deleted_datetime timestamp with time zone,
    created_by_id integer,
    created_by_role character varying(255) NOT NULL,
    CONSTRAINT devilry_compressionutil_compressedarchi_content_object_id_check CHECK ((content_object_id >= 0))
);


ALTER TABLE devilry_compressionutil_compressedarchivemeta OWNER TO dbdev;

--
-- Name: devilry_compressionutil_compressedarchivemeta_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_compressionutil_compressedarchivemeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_compressionutil_compressedarchivemeta_id_seq OWNER TO dbdev;

--
-- Name: devilry_compressionutil_compressedarchivemeta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_compressionutil_compressedarchivemeta_id_seq OWNED BY devilry_compressionutil_compressedarchivemeta.id;


--
-- Name: devilry_dbcache_assignmentgroupcacheddata; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_dbcache_assignmentgroupcacheddata (
    id integer NOT NULL,
    new_attempt_count integer NOT NULL,
    public_total_comment_count integer NOT NULL,
    public_student_comment_count integer NOT NULL,
    public_examiner_comment_count integer NOT NULL,
    public_admin_comment_count integer NOT NULL,
    public_student_file_upload_count integer NOT NULL,
    first_feedbackset_id integer,
    group_id integer NOT NULL,
    last_feedbackset_id integer,
    last_published_feedbackset_id integer,
    last_public_comment_by_examiner_datetime timestamp with time zone,
    last_public_comment_by_student_datetime timestamp with time zone,
    candidate_count integer NOT NULL,
    examiner_count integer NOT NULL,
    CONSTRAINT devilry_dbcache_assignmentgr_public_examiner_comment_coun_check CHECK ((public_examiner_comment_count >= 0)),
    CONSTRAINT devilry_dbcache_assignmentgr_public_student_comment_count_check CHECK ((public_student_comment_count >= 0)),
    CONSTRAINT devilry_dbcache_assignmentgr_public_student_file_upload_c_check CHECK ((public_student_file_upload_count >= 0)),
    CONSTRAINT devilry_dbcache_assignmentgrou_public_admin_comment_count_check CHECK ((public_admin_comment_count >= 0)),
    CONSTRAINT devilry_dbcache_assignmentgrou_public_total_comment_count_check CHECK ((public_total_comment_count >= 0)),
    CONSTRAINT devilry_dbcache_assignmentgroupcachedda_new_attempt_count_check CHECK ((new_attempt_count >= 0)),
    CONSTRAINT devilry_dbcache_assignmentgroupcacheddata_candidate_count_check CHECK ((candidate_count >= 0)),
    CONSTRAINT devilry_dbcache_assignmentgroupcacheddata_examiner_count_check CHECK ((examiner_count >= 0))
);


ALTER TABLE devilry_dbcache_assignmentgroupcacheddata OWNER TO dbdev;

--
-- Name: devilry_dbcache_assignmentgroupcacheddata_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_dbcache_assignmentgroupcacheddata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_dbcache_assignmentgroupcacheddata_id_seq OWNER TO dbdev;

--
-- Name: devilry_dbcache_assignmentgroupcacheddata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_dbcache_assignmentgroupcacheddata_id_seq OWNED BY devilry_dbcache_assignmentgroupcacheddata.id;


--
-- Name: devilry_gradingsystem_feedbackdraft; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_gradingsystem_feedbackdraftfile; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_group_feedbacksetdeadlinehistory; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_group_feedbacksetdeadlinehistory (
    id integer NOT NULL,
    changed_datetime timestamp with time zone NOT NULL,
    deadline_old timestamp with time zone NOT NULL,
    deadline_new timestamp with time zone NOT NULL,
    changed_by_id integer,
    feedback_set_id integer NOT NULL
);


ALTER TABLE devilry_group_feedbacksetdeadlinehistory OWNER TO dbdev;

--
-- Name: devilry_group_feedbacksetdeadlinehistory_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_group_feedbacksetdeadlinehistory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_group_feedbacksetdeadlinehistory_id_seq OWNER TO dbdev;

--
-- Name: devilry_group_feedbacksetdeadlinehistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_group_feedbacksetdeadlinehistory_id_seq OWNED BY devilry_group_feedbacksetdeadlinehistory.id;


--
-- Name: devilry_group_feedbacksetgradingupdatehistory; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_group_feedbacksetgradingupdatehistory (
    id integer NOT NULL,
    updated_datetime timestamp with time zone NOT NULL,
    old_grading_points integer NOT NULL,
    old_grading_published_datetime timestamp with time zone NOT NULL,
    feedback_set_id integer NOT NULL,
    old_grading_published_by_id integer,
    updated_by_id integer,
    CONSTRAINT devilry_group_feedbacksetgradingupdate_old_grading_points_check CHECK ((old_grading_points >= 0))
);


ALTER TABLE devilry_group_feedbacksetgradingupdatehistory OWNER TO dbdev;

--
-- Name: devilry_group_feedbacksetgradingupdatehistory_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_group_feedbacksetgradingupdatehistory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_group_feedbacksetgradingupdatehistory_id_seq OWNER TO dbdev;

--
-- Name: devilry_group_feedbacksetgradingupdatehistory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_group_feedbacksetgradingupdatehistory_id_seq OWNED BY devilry_group_feedbacksetgradingupdatehistory.id;


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_group_feedbacksetpassedpreviousperiod (
    id integer NOT NULL,
    assignment_short_name character varying(20) NOT NULL,
    assignment_long_name character varying(100) NOT NULL,
    assignment_max_points integer,
    assignment_passing_grade_min_points integer,
    period_short_name character varying(20) NOT NULL,
    period_long_name character varying(100) NOT NULL,
    period_start_time timestamp with time zone,
    period_end_time timestamp with time zone,
    grading_points integer,
    grading_published_datetime timestamp with time zone,
    feedbackset_id integer,
    grading_published_by_id integer,
    created_by_id integer,
    created_datetime timestamp with time zone NOT NULL,
    passed_previous_period_type character varying(255) NOT NULL,
    CONSTRAINT devilry_group_feedbacksetpas_assignment_passing_grade_min_check CHECK ((assignment_passing_grade_min_points >= 0)),
    CONSTRAINT devilry_group_feedbacksetpassedprev_assignment_max_points_check CHECK ((assignment_max_points >= 0)),
    CONSTRAINT devilry_group_feedbacksetpassedpreviousper_grading_points_check CHECK ((grading_points >= 0))
);


ALTER TABLE devilry_group_feedbacksetpassedpreviousperiod OWNER TO dbdev;

--
-- Name: devilry_group_feedbacksetpassedpreviousperiod_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_group_feedbacksetpassedpreviousperiod_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_group_feedbacksetpassedpreviousperiod_id_seq OWNER TO dbdev;

--
-- Name: devilry_group_feedbacksetpassedpreviousperiod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_group_feedbacksetpassedpreviousperiod_id_seq OWNED BY devilry_group_feedbacksetpassedpreviousperiod.id;


--
-- Name: devilry_group_groupcomment; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_group_groupcomment (
    comment_ptr_id integer NOT NULL,
    feedback_set_id integer NOT NULL,
    part_of_grading boolean NOT NULL,
    visibility character varying(50) NOT NULL,
    v2_id character varying(255) NOT NULL
);


ALTER TABLE devilry_group_groupcomment OWNER TO dbdev;

--
-- Name: devilry_group_groupcommentedithistory; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_group_groupcommentedithistory (
    commentedithistory_ptr_id integer NOT NULL,
    visibility character varying(50) NOT NULL,
    group_comment_id integer NOT NULL
);


ALTER TABLE devilry_group_groupcommentedithistory OWNER TO dbdev;

--
-- Name: devilry_group_imageannotationcomment; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_import_v2database_importedmodel; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_import_v2database_importedmodel (
    id integer NOT NULL,
    content_object_id integer NOT NULL,
    data jsonb NOT NULL,
    content_type_id integer NOT NULL,
    CONSTRAINT devilry_import_v2database_importedmodel_content_object_id_check CHECK ((content_object_id >= 0))
);


ALTER TABLE devilry_import_v2database_importedmodel OWNER TO dbdev;

--
-- Name: devilry_import_v2database_importedmodel_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE devilry_import_v2database_importedmodel_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE devilry_import_v2database_importedmodel_id_seq OWNER TO dbdev;

--
-- Name: devilry_import_v2database_importedmodel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE devilry_import_v2database_importedmodel_id_seq OWNED BY devilry_import_v2database_importedmodel.id;


--
-- Name: devilry_qualifiesforexam_deadlinetag; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_qualifiesforexam_periodtag; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE devilry_qualifiesforexam_periodtag (
    period_id integer NOT NULL,
    deadlinetag_id integer NOT NULL
);


ALTER TABLE devilry_qualifiesforexam_periodtag OWNER TO dbdev;

--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_qualifiesforexam_status; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: devilry_student_uploadeddeliveryfile; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: django_session; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE django_session OWNER TO dbdev;

--
-- Name: django_site; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE django_site OWNER TO dbdev;

--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE django_site_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_site_id_seq OWNER TO dbdev;

--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: ievv_batchframework_batchoperation; Type: TABLE; Schema: public; Owner: dbdev
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
-- Name: ievv_developemail_developemail; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE ievv_developemail_developemail (
    id integer NOT NULL,
    created_datetime timestamp with time zone NOT NULL,
    subject text NOT NULL,
    from_email text NOT NULL,
    to_emails text NOT NULL,
    raw_message text NOT NULL
);


ALTER TABLE ievv_developemail_developemail OWNER TO dbdev;

--
-- Name: ievv_developemail_developemail_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE ievv_developemail_developemail_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ievv_developemail_developemail_id_seq OWNER TO dbdev;

--
-- Name: ievv_developemail_developemail_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE ievv_developemail_developemail_id_seq OWNED BY ievv_developemail_developemail.id;


--
-- Name: socialaccount_socialaccount; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE socialaccount_socialaccount (
    id integer NOT NULL,
    provider character varying(30) NOT NULL,
    uid character varying(191) NOT NULL,
    last_login timestamp with time zone NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    extra_data text NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE socialaccount_socialaccount OWNER TO dbdev;

--
-- Name: socialaccount_socialaccount_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE socialaccount_socialaccount_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE socialaccount_socialaccount_id_seq OWNER TO dbdev;

--
-- Name: socialaccount_socialaccount_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE socialaccount_socialaccount_id_seq OWNED BY socialaccount_socialaccount.id;


--
-- Name: socialaccount_socialapp; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE socialaccount_socialapp (
    id integer NOT NULL,
    provider character varying(30) NOT NULL,
    name character varying(40) NOT NULL,
    client_id character varying(191) NOT NULL,
    secret character varying(191) NOT NULL,
    key character varying(191) NOT NULL
);


ALTER TABLE socialaccount_socialapp OWNER TO dbdev;

--
-- Name: socialaccount_socialapp_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE socialaccount_socialapp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE socialaccount_socialapp_id_seq OWNER TO dbdev;

--
-- Name: socialaccount_socialapp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE socialaccount_socialapp_id_seq OWNED BY socialaccount_socialapp.id;


--
-- Name: socialaccount_socialapp_sites; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE socialaccount_socialapp_sites (
    id integer NOT NULL,
    socialapp_id integer NOT NULL,
    site_id integer NOT NULL
);


ALTER TABLE socialaccount_socialapp_sites OWNER TO dbdev;

--
-- Name: socialaccount_socialapp_sites_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE socialaccount_socialapp_sites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE socialaccount_socialapp_sites_id_seq OWNER TO dbdev;

--
-- Name: socialaccount_socialapp_sites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE socialaccount_socialapp_sites_id_seq OWNED BY socialaccount_socialapp_sites.id;


--
-- Name: socialaccount_socialtoken; Type: TABLE; Schema: public; Owner: dbdev
--

CREATE TABLE socialaccount_socialtoken (
    id integer NOT NULL,
    token text NOT NULL,
    token_secret text NOT NULL,
    expires_at timestamp with time zone,
    account_id integer NOT NULL,
    app_id integer NOT NULL
);


ALTER TABLE socialaccount_socialtoken OWNER TO dbdev;

--
-- Name: socialaccount_socialtoken_id_seq; Type: SEQUENCE; Schema: public; Owner: dbdev
--

CREATE SEQUENCE socialaccount_socialtoken_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE socialaccount_socialtoken_id_seq OWNER TO dbdev;

--
-- Name: socialaccount_socialtoken_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dbdev
--

ALTER SEQUENCE socialaccount_socialtoken_id_seq OWNED BY socialaccount_socialtoken.id;


--
-- Name: account_emailaddress id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY account_emailaddress ALTER COLUMN id SET DEFAULT nextval('account_emailaddress_id_seq'::regclass);


--
-- Name: account_emailconfirmation id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY account_emailconfirmation ALTER COLUMN id SET DEFAULT nextval('account_emailconfirmation_id_seq'::regclass);


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: core_assignment id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment ALTER COLUMN id SET DEFAULT nextval('core_assignment_id_seq'::regclass);


--
-- Name: core_assignment_admins id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment_admins ALTER COLUMN id SET DEFAULT nextval('core_assignment_admins_id_seq'::regclass);


--
-- Name: core_assignmentgroup id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup ALTER COLUMN id SET DEFAULT nextval('core_assignmentgroup_id_seq'::regclass);


--
-- Name: core_assignmentgroup_examiners id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners ALTER COLUMN id SET DEFAULT nextval('core_assignmentgroup_examiners_id_seq'::regclass);


--
-- Name: core_assignmentgrouphistory id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouphistory ALTER COLUMN id SET DEFAULT nextval('core_assignmentgrouphistory_id_seq'::regclass);


--
-- Name: core_assignmentgrouptag id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouptag ALTER COLUMN id SET DEFAULT nextval('core_assignmentgrouptag_id_seq'::regclass);


--
-- Name: core_candidate id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate ALTER COLUMN id SET DEFAULT nextval('core_candidate_id_seq'::regclass);


--
-- Name: core_candidateassignmentgrouphistory id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidateassignmentgrouphistory ALTER COLUMN id SET DEFAULT nextval('core_candidateassignmentgrouphistory_id_seq'::regclass);


--
-- Name: core_deadline id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_deadline ALTER COLUMN id SET DEFAULT nextval('core_deadline_id_seq'::regclass);


--
-- Name: core_delivery id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery ALTER COLUMN id SET DEFAULT nextval('core_delivery_id_seq'::regclass);


--
-- Name: core_devilryuserprofile id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_devilryuserprofile ALTER COLUMN id SET DEFAULT nextval('core_devilryuserprofile_id_seq'::regclass);


--
-- Name: core_examinerassignmentgrouphistory id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_examinerassignmentgrouphistory ALTER COLUMN id SET DEFAULT nextval('core_examinerassignmentgrouphistory_id_seq'::regclass);


--
-- Name: core_filemeta id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_filemeta ALTER COLUMN id SET DEFAULT nextval('core_filemeta_id_seq'::regclass);


--
-- Name: core_groupinvite id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite ALTER COLUMN id SET DEFAULT nextval('core_groupinvite_id_seq'::regclass);


--
-- Name: core_period id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period ALTER COLUMN id SET DEFAULT nextval('core_period_id_seq'::regclass);


--
-- Name: core_period_admins id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period_admins ALTER COLUMN id SET DEFAULT nextval('core_period_admins_id_seq'::regclass);


--
-- Name: core_periodapplicationkeyvalue id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodapplicationkeyvalue ALTER COLUMN id SET DEFAULT nextval('core_periodapplicationkeyvalue_id_seq'::regclass);


--
-- Name: core_periodtag id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag ALTER COLUMN id SET DEFAULT nextval('core_periodtag_id_seq'::regclass);


--
-- Name: core_periodtag_relatedexaminers id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedexaminers ALTER COLUMN id SET DEFAULT nextval('core_periodtag_relatedexaminers_id_seq'::regclass);


--
-- Name: core_periodtag_relatedstudents id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedstudents ALTER COLUMN id SET DEFAULT nextval('core_periodtag_relatedstudents_id_seq'::regclass);


--
-- Name: core_pointrangetograde id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointrangetograde ALTER COLUMN id SET DEFAULT nextval('core_pointrangetograde_id_seq'::regclass);


--
-- Name: core_pointtogrademap id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointtogrademap ALTER COLUMN id SET DEFAULT nextval('core_pointtogrademap_id_seq'::regclass);


--
-- Name: core_relatedexaminer id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminer ALTER COLUMN id SET DEFAULT nextval('core_relatedexaminer_id_seq'::regclass);


--
-- Name: core_relatedstudent id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudent ALTER COLUMN id SET DEFAULT nextval('core_relatedstudent_id_seq'::regclass);


--
-- Name: core_relatedstudentkeyvalue id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudentkeyvalue ALTER COLUMN id SET DEFAULT nextval('core_relatedstudentkeyvalue_id_seq'::regclass);


--
-- Name: core_staticfeedback id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedback ALTER COLUMN id SET DEFAULT nextval('core_staticfeedback_id_seq'::regclass);


--
-- Name: core_staticfeedbackfileattachment id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedbackfileattachment ALTER COLUMN id SET DEFAULT nextval('core_staticfeedbackfileattachment_id_seq'::regclass);


--
-- Name: core_subject id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject ALTER COLUMN id SET DEFAULT nextval('core_subject_id_seq'::regclass);


--
-- Name: core_subject_admins id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject_admins ALTER COLUMN id SET DEFAULT nextval('core_subject_admins_id_seq'::regclass);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadata id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_generic_token_with_metadata_generictokenwithmetadata ALTER COLUMN id SET DEFAULT nextval('cradmin_generic_token_with_metadata_generictokenwithmeta_id_seq'::regclass);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfile ALTER COLUMN id SET DEFAULT nextval('cradmin_temporaryfileuploadstore_temporaryfile_id_seq'::regclass);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfilecollection ALTER COLUMN id SET DEFAULT nextval('cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq'::regclass);


--
-- Name: devilry_account_periodpermissiongroup id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup ALTER COLUMN id SET DEFAULT nextval('devilry_account_periodpermissiongroup_id_seq'::regclass);


--
-- Name: devilry_account_permissiongroup id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroup ALTER COLUMN id SET DEFAULT nextval('devilry_account_permissiongroup_id_seq'::regclass);


--
-- Name: devilry_account_permissiongroupuser id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroupuser ALTER COLUMN id SET DEFAULT nextval('devilry_account_permissiongroupuser_id_seq'::regclass);


--
-- Name: devilry_account_subjectpermissiongroup id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup ALTER COLUMN id SET DEFAULT nextval('devilry_account_subjectpermissiongroup_id_seq'::regclass);


--
-- Name: devilry_account_user id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_user ALTER COLUMN id SET DEFAULT nextval('devilry_account_user_id_seq'::regclass);


--
-- Name: devilry_account_useremail id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_useremail ALTER COLUMN id SET DEFAULT nextval('devilry_account_useremail_id_seq'::regclass);


--
-- Name: devilry_account_username id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_username ALTER COLUMN id SET DEFAULT nextval('devilry_account_username_id_seq'::regclass);


--
-- Name: devilry_comment_comment id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_comment ALTER COLUMN id SET DEFAULT nextval('devilry_comment_comment_id_seq'::regclass);


--
-- Name: devilry_comment_commentedithistory id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentedithistory ALTER COLUMN id SET DEFAULT nextval('devilry_comment_commentedithistory_id_seq'::regclass);


--
-- Name: devilry_comment_commentfile id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfile ALTER COLUMN id SET DEFAULT nextval('devilry_comment_commentfile_id_seq'::regclass);


--
-- Name: devilry_comment_commentfileimage id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfileimage ALTER COLUMN id SET DEFAULT nextval('devilry_comment_commentfileimage_id_seq'::regclass);


--
-- Name: devilry_compressionutil_compressedarchivemeta id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_compressionutil_compressedarchivemeta ALTER COLUMN id SET DEFAULT nextval('devilry_compressionutil_compressedarchivemeta_id_seq'::regclass);


--
-- Name: devilry_dbcache_assignmentgroupcacheddata id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_dbcache_assignmentgroupcacheddata ALTER COLUMN id SET DEFAULT nextval('devilry_dbcache_assignmentgroupcacheddata_id_seq'::regclass);


--
-- Name: devilry_gradingsystem_feedbackdraft id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft ALTER COLUMN id SET DEFAULT nextval('devilry_gradingsystem_feedbackdraft_id_seq'::regclass);


--
-- Name: devilry_gradingsystem_feedbackdraftfile id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraftfile ALTER COLUMN id SET DEFAULT nextval('devilry_gradingsystem_feedbackdraftfile_id_seq'::regclass);


--
-- Name: devilry_group_feedbackset id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset ALTER COLUMN id SET DEFAULT nextval('devilry_group_feedbackset_id_seq'::regclass);


--
-- Name: devilry_group_feedbacksetdeadlinehistory id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetdeadlinehistory ALTER COLUMN id SET DEFAULT nextval('devilry_group_feedbacksetdeadlinehistory_id_seq'::regclass);


--
-- Name: devilry_group_feedbacksetgradingupdatehistory id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetgradingupdatehistory ALTER COLUMN id SET DEFAULT nextval('devilry_group_feedbacksetgradingupdatehistory_id_seq'::regclass);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetpassedpreviousperiod ALTER COLUMN id SET DEFAULT nextval('devilry_group_feedbacksetpassedpreviousperiod_id_seq'::regclass);


--
-- Name: devilry_import_v2database_importedmodel id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_import_v2database_importedmodel ALTER COLUMN id SET DEFAULT nextval('devilry_import_v2database_importedmodel_id_seq'::regclass);


--
-- Name: devilry_qualifiesforexam_deadlinetag id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_deadlinetag ALTER COLUMN id SET DEFAULT nextval('devilry_qualifiesforexam_deadlinetag_id_seq'::regclass);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam ALTER COLUMN id SET DEFAULT nextval('devilry_qualifiesforexam_qualifiesforfinalexam_id_seq'::regclass);


--
-- Name: devilry_qualifiesforexam_status id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_status ALTER COLUMN id SET DEFAULT nextval('devilry_qualifiesforexam_status_id_seq'::regclass);


--
-- Name: devilry_student_uploadeddeliveryfile id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile ALTER COLUMN id SET DEFAULT nextval('devilry_student_uploadeddeliveryfile_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


--
-- Name: django_site id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: ievv_batchframework_batchoperation id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_batchframework_batchoperation ALTER COLUMN id SET DEFAULT nextval('ievv_batchframework_batchoperation_id_seq'::regclass);


--
-- Name: ievv_developemail_developemail id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_developemail_developemail ALTER COLUMN id SET DEFAULT nextval('ievv_developemail_developemail_id_seq'::regclass);


--
-- Name: socialaccount_socialaccount id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialaccount ALTER COLUMN id SET DEFAULT nextval('socialaccount_socialaccount_id_seq'::regclass);


--
-- Name: socialaccount_socialapp id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialapp ALTER COLUMN id SET DEFAULT nextval('socialaccount_socialapp_id_seq'::regclass);


--
-- Name: socialaccount_socialapp_sites id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialapp_sites ALTER COLUMN id SET DEFAULT nextval('socialaccount_socialapp_sites_id_seq'::regclass);


--
-- Name: socialaccount_socialtoken id; Type: DEFAULT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialtoken ALTER COLUMN id SET DEFAULT nextval('socialaccount_socialtoken_id_seq'::regclass);


--
-- Data for Name: account_emailaddress; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY account_emailaddress (id, email, verified, "primary", user_id) FROM stdin;
\.


--
-- Data for Name: account_emailconfirmation; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY account_emailconfirmation (id, created, sent, key, email_address_id) FROM stdin;
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


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
169	Can add assignment group cached data	57	add_assignmentgroupcacheddata
170	Can change assignment group cached data	57	change_assignmentgroupcacheddata
171	Can delete assignment group cached data	57	delete_assignmentgroupcacheddata
172	Can add assignment group history	58	add_assignmentgrouphistory
173	Can change assignment group history	58	change_assignmentgrouphistory
174	Can delete assignment group history	58	delete_assignmentgrouphistory
175	Can add compressed archive meta	59	add_compressedarchivemeta
176	Can change compressed archive meta	59	change_compressedarchivemeta
177	Can delete compressed archive meta	59	delete_compressedarchivemeta
178	Can add feedbackset passed previous period	60	add_feedbacksetpassedpreviousperiod
179	Can change feedbackset passed previous period	60	change_feedbacksetpassedpreviousperiod
180	Can delete feedbackset passed previous period	60	delete_feedbacksetpassedpreviousperiod
181	Can add feedback set deadline history	61	add_feedbacksetdeadlinehistory
182	Can change feedback set deadline history	61	change_feedbacksetdeadlinehistory
183	Can delete feedback set deadline history	61	delete_feedbacksetdeadlinehistory
184	Can add period tag	62	add_periodtag
185	Can change period tag	62	change_periodtag
186	Can delete period tag	62	delete_periodtag
187	Can add site	63	add_site
188	Can change site	63	change_site
189	Can delete site	63	delete_site
190	Can add imported model	64	add_importedmodel
191	Can change imported model	64	change_importedmodel
192	Can delete imported model	64	delete_importedmodel
193	Can add email address	65	add_emailaddress
194	Can change email address	65	change_emailaddress
195	Can delete email address	65	delete_emailaddress
196	Can add email confirmation	66	add_emailconfirmation
197	Can change email confirmation	66	change_emailconfirmation
198	Can delete email confirmation	66	delete_emailconfirmation
199	Can add social application	67	add_socialapp
200	Can change social application	67	change_socialapp
201	Can delete social application	67	delete_socialapp
202	Can add social account	68	add_socialaccount
203	Can change social account	68	change_socialaccount
204	Can delete social account	68	delete_socialaccount
205	Can add social application token	69	add_socialtoken
206	Can change social application token	69	change_socialtoken
207	Can delete social application token	69	delete_socialtoken
208	Can add Candidate group history	70	add_candidateassignmentgrouphistory
209	Can change Candidate group history	70	change_candidateassignmentgrouphistory
210	Can delete Candidate group history	70	delete_candidateassignmentgrouphistory
211	Can add Examiner assignment group history	71	add_examinerassignmentgrouphistory
212	Can change Examiner assignment group history	71	change_examinerassignmentgrouphistory
213	Can delete Examiner assignment group history	71	delete_examinerassignmentgrouphistory
214	Can add feedback set grading update history	72	add_feedbacksetgradingupdatehistory
215	Can change feedback set grading update history	72	change_feedbacksetgradingupdatehistory
216	Can delete feedback set grading update history	72	delete_feedbacksetgradingupdatehistory
217	Can add develop email	73	add_developemail
218	Can change develop email	73	change_developemail
219	Can delete develop email	73	delete_developemail
220	Can add group comment edit history	74	add_groupcommentedithistory
221	Can change group comment edit history	74	change_groupcommentedithistory
222	Can delete group comment edit history	74	delete_groupcommentedithistory
223	Can add comment edit history	75	add_commentedithistory
224	Can change comment edit history	75	change_commentedithistory
225	Can delete comment edit history	75	delete_commentedithistory
\.


--
-- Data for Name: core_assignment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignment (id, short_name, long_name, publishing_time, deprecated_field_anonymous, students_can_see_points, delivery_types, deadline_handling, scale_points_percent, first_deadline, max_points, passing_grade_min_points, points_to_grade_mapper, grading_system_plugin_id, students_can_create_groups, students_can_not_create_groups_after, feedback_workflow, parentnode_id, gradeform_setup_json, anonymizationmode, uses_custom_candidate_ids) FROM stdin;
1	assignment1	Assignment 1	2015-12-27 03:35:27.525662+01	f	t	0	0	100	2040-01-31 12:30:00+01	1	1	passed-failed	devilry_gradingsystemplugin_approved	f	\N		1	\N	off	f
2	assignment2	Assignment 2	2016-01-03 04:41:40.730958+01	f	t	0	0	100	2040-02-14 12:30:00+01	1	1	passed-failed	devilry_gradingsystemplugin_approved	f	\N		1	\N	off	f
4	fully-anonymous-exam	Fully anonymous exam	2016-01-20 00:20:00+01	f	f	0	0	100	2040-03-15 23:59:00+01	100	30	custom-table	devilry_gradingsystemplugin_points	f	\N		1		fully_anonymous	f
3	semi-anonymous-exam	Semi anonymous exam	2016-01-19 12:30:00+01	f	f	0	0	100	2040-03-02 15:30:00+01	100	38	raw-points	devilry_gradingsystemplugin_points	f	\N		1		semi_anonymous	f
5	assignment0	Assignment 0	2016-02-08 20:58:20.423164+01	f	f	0	0	100	2016-02-08 20:00:00+01	1	1	passed-failed	devilry_gradingsystemplugin_approved	f	\N		1	\N	off	f
\.


--
-- Data for Name: core_assignment_admins; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignment_admins (id, assignment_id, user_id) FROM stdin;
\.


--
-- Data for Name: core_assignmentgroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgroup (id, name, is_open, etag, delivery_status, created_datetime, copied_from_id, feedback_id, last_deadline_id, parentnode_id, batchoperation_id, internal_is_being_deleted) FROM stdin;
3		t	2016-01-20 11:17:01.689683+01	\N	2016-01-20 11:17:01.689159+01	\N	\N	\N	1	1	f
4		t	2016-01-20 11:17:01.689714+01	\N	2016-01-20 11:17:01.689207+01	\N	\N	\N	1	1	f
5		t	2016-01-20 11:17:01.689744+01	\N	2016-01-20 11:17:01.689254+01	\N	\N	\N	1	1	f
6		t	2016-01-20 11:17:01.689774+01	\N	2016-01-20 11:17:01.689303+01	\N	\N	\N	1	1	f
7		t	2016-01-20 11:17:01.689804+01	\N	2016-01-20 11:17:01.689349+01	\N	\N	\N	1	1	f
8		t	2016-01-20 11:17:01.689833+01	\N	2016-01-20 11:17:01.689396+01	\N	\N	\N	1	1	f
9		t	2016-02-06 14:29:23.917938+01	\N	2016-02-06 14:29:23.917324+01	\N	\N	\N	1	2	f
10		t	2016-02-06 15:10:23.046051+01	\N	2016-02-06 15:10:23.045796+01	\N	\N	\N	2	3	f
11		t	2016-02-06 15:10:32.178895+01	\N	2016-02-06 15:10:32.178657+01	\N	\N	\N	4	4	f
12		t	2016-02-08 11:42:11.577236+01	\N	2016-02-08 11:42:11.576999+01	\N	\N	\N	3	5	f
14		t	2016-02-08 20:55:47.52143+01	\N	2016-02-08 20:55:47.520825+01	\N	\N	\N	5	6	f
15		t	2016-02-08 20:55:47.521462+01	\N	2016-02-08 20:55:47.520881+01	\N	\N	\N	5	6	f
16		t	2016-02-08 20:55:47.521482+01	\N	2016-02-08 20:55:47.520927+01	\N	\N	\N	5	6	f
17		t	2016-02-08 20:55:47.521501+01	\N	2016-02-08 20:55:47.520961+01	\N	\N	\N	5	6	f
18		t	2016-02-08 20:55:47.521521+01	\N	2016-02-08 20:55:47.520993+01	\N	\N	\N	5	6	f
19		t	2016-02-08 20:55:47.52154+01	\N	2016-02-08 20:55:47.521024+01	\N	\N	\N	5	6	f
20		t	2016-02-08 20:55:47.521559+01	\N	2016-02-08 20:55:47.521055+01	\N	\N	\N	5	6	f
21		t	2016-02-08 20:55:47.521578+01	\N	2016-02-08 20:55:47.521085+01	\N	\N	\N	5	6	f
22		t	2016-02-08 20:55:47.521597+01	\N	2016-02-08 20:55:47.521115+01	\N	\N	\N	5	6	f
23		t	2016-02-08 20:55:47.521616+01	\N	2016-02-08 20:55:47.521146+01	\N	\N	\N	5	6	f
24		t	2016-02-08 20:55:47.521635+01	\N	2016-02-08 20:55:47.521176+01	\N	\N	\N	5	6	f
25		t	2016-02-08 21:02:42.625796+01	\N	2016-02-08 21:02:42.625394+01	\N	\N	\N	5	7	f
\.


--
-- Data for Name: core_assignmentgroup_examiners; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgroup_examiners (id, assignmentgroup_id, old_reference_not_in_use_user_id, relatedexaminer_id) FROM stdin;
17	3	\N	3
18	4	\N	3
19	7	\N	3
20	9	\N	3
21	5	\N	2
22	6	\N	2
23	8	\N	2
24	12	\N	3
37	14	\N	3
38	18	\N	3
39	21	\N	3
40	25	\N	3
41	15	\N	2
42	17	\N	2
43	19	\N	2
44	20	\N	2
45	16	\N	4
46	22	\N	4
47	23	\N	4
\.


--
-- Data for Name: core_assignmentgrouphistory; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgrouphistory (id, merge_history_json, assignment_group_id) FROM stdin;
\.


--
-- Data for Name: core_assignmentgrouptag; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_assignmentgrouptag (id, tag, assignment_group_id) FROM stdin;
\.


--
-- Data for Name: core_candidate; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_candidate (id, candidate_id, assignment_group_id, old_reference_not_in_use_student_id, relatedstudent_id) FROM stdin;
3	\N	3	\N	3
4	\N	4	\N	4
5	\N	5	\N	5
6	\N	6	\N	6
7	\N	7	\N	7
8	\N	8	\N	8
9	\N	9	\N	1
10	\N	10	\N	1
11	\N	11	\N	1
12	\N	12	\N	1
14	\N	14	\N	2
15	\N	15	\N	12
16	\N	16	\N	3
17	\N	17	\N	4
18	\N	18	\N	6
19	\N	19	\N	10
20	\N	20	\N	11
21	\N	21	\N	9
22	\N	22	\N	8
23	\N	23	\N	7
24	\N	24	\N	5
25	\N	25	\N	1
\.


--
-- Data for Name: core_candidateassignmentgrouphistory; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_candidateassignmentgrouphistory (id, created_datetime, is_add, assignment_group_id, user_id) FROM stdin;
\.


--
-- Data for Name: core_deadline; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_deadline (id, deadline, text, deliveries_available_before_deadline, why_created, added_by_id, assignment_group_id) FROM stdin;
\.


--
-- Data for Name: core_delivery; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_delivery (id, delivery_type, time_of_delivery, number, successful, alias_delivery_id, copy_of_id, deadline_id, delivered_by_id, last_feedback_id) FROM stdin;
\.


--
-- Data for Name: core_devilryuserprofile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_devilryuserprofile (id, full_name, languagecode, user_id) FROM stdin;
\.


--
-- Data for Name: core_examinerassignmentgrouphistory; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_examinerassignmentgrouphistory (id, created_datetime, is_add, assignment_group_id, user_id) FROM stdin;
1	2018-10-15 11:52:22.277483+02	f	14	13
2	2018-10-15 11:52:22.277483+02	f	15	13
3	2018-10-15 11:52:22.277483+02	f	16	13
4	2018-10-15 11:52:22.277483+02	f	17	13
5	2018-10-15 11:52:22.277483+02	f	18	13
6	2018-10-15 11:52:22.277483+02	f	19	13
7	2018-10-15 11:52:22.277483+02	f	20	13
8	2018-10-15 11:52:22.277483+02	f	21	13
9	2018-10-15 11:52:22.277483+02	f	22	13
10	2018-10-15 11:52:22.277483+02	f	23	13
11	2018-10-15 11:52:22.277483+02	f	24	13
12	2018-10-15 11:52:31.89498+02	t	14	13
13	2018-10-15 11:52:31.89498+02	t	18	13
14	2018-10-15 11:52:31.89498+02	t	21	13
15	2018-10-15 11:52:31.89498+02	t	25	13
16	2018-10-15 11:52:53.60067+02	t	15	12
17	2018-10-15 11:52:53.60067+02	t	17	12
18	2018-10-15 11:52:53.60067+02	t	19	12
19	2018-10-15 11:52:53.60067+02	t	20	12
20	2018-10-15 11:53:32.391664+02	t	16	14
21	2018-10-15 11:53:32.391664+02	t	22	14
22	2018-10-15 11:53:32.391664+02	t	23	14
\.


--
-- Data for Name: core_filemeta; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_filemeta (id, filename, size, delivery_id) FROM stdin;
\.


--
-- Data for Name: core_groupinvite; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_groupinvite (id, sent_datetime, accepted, responded_datetime, group_id, sent_by_id, sent_to_id) FROM stdin;
\.


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
-- Data for Name: core_periodapplicationkeyvalue; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_periodapplicationkeyvalue (id, application, key, value, period_id) FROM stdin;
\.


--
-- Data for Name: core_periodtag; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_periodtag (id, prefix, tag, is_hidden, created_datetime, modified_datetime, period_id) FROM stdin;
\.


--
-- Data for Name: core_periodtag_relatedexaminers; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_periodtag_relatedexaminers (id, periodtag_id, relatedexaminer_id) FROM stdin;
\.


--
-- Data for Name: core_periodtag_relatedstudents; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_periodtag_relatedstudents (id, periodtag_id, relatedstudent_id) FROM stdin;
\.


--
-- Data for Name: core_pointrangetograde; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_pointrangetograde (id, minimum_points, maximum_points, grade, point_to_grade_map_id) FROM stdin;
1	0	30	F	1
2	31	45	E	1
3	46	60	D	1
4	61	80	C	1
6	91	100	A	1
5	81	90	B	1
\.


--
-- Data for Name: core_pointtogrademap; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_pointtogrademap (id, invalid, assignment_id) FROM stdin;
1	t	4
\.


--
-- Data for Name: core_relatedexaminer; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_relatedexaminer (id, tags, period_id, user_id, automatic_anonymous_id, active) FROM stdin;
1		1	1		t
2	\N	1	12		t
3	\N	1	13		t
4	\N	1	14		t
\.


--
-- Data for Name: core_relatedstudent; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_relatedstudent (id, tags, candidate_id, automatic_anonymous_id, period_id, user_id, active) FROM stdin;
1				1	5	t
2				1	2	t
3				1	6	t
4				1	7	t
6				1	8	t
7				1	17	t
8				1	16	t
5				1	13	f
9	\N	\N		1	15	t
10	\N	\N		1	9	t
11	\N	\N		1	10	t
12	\N	\N		1	4	t
13	\N	\N		3	5	t
14	\N	\N		2	5	t
\.


--
-- Data for Name: core_relatedstudentkeyvalue; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_relatedstudentkeyvalue (id, application, key, value, student_can_read, relatedstudent_id) FROM stdin;
\.


--
-- Data for Name: core_staticfeedback; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_staticfeedback (id, rendered_view, grade, points, is_passing_grade, save_timestamp, delivery_id, saved_by_id) FROM stdin;
\.


--
-- Data for Name: core_staticfeedbackfileattachment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_staticfeedbackfileattachment (id, filename, file, staticfeedback_id) FROM stdin;
\.


--
-- Data for Name: core_subject; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_subject (id, short_name, long_name, etag) FROM stdin;
1	duck1010	DUCK1010 - Object Oriented Programming	2015-12-22 19:57:16.969003+01
2	duck1100	DUCK1100 - Mathematical programming	2015-12-22 19:58:18.525346+01
\.


--
-- Data for Name: core_subject_admins; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY core_subject_admins (id, subject_id, user_id) FROM stdin;
\.


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
-- Data for Name: cradmin_temporaryfileuploadstore_temporaryfilecollection; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY cradmin_temporaryfileuploadstore_temporaryfilecollection (id, created_datetime, minutes_to_live, accept, max_filename_length, unique_filenames, user_id, singlemode, max_filesize_bytes) FROM stdin;
\.


--
-- Data for Name: devilry_account_periodpermissiongroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_periodpermissiongroup (id, period_id, permissiongroup_id) FROM stdin;
1	1	2
2	1	4
\.


--
-- Data for Name: devilry_account_permissiongroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_permissiongroup (id, name, created_datetime, updated_datetime, syncsystem_update_datetime, grouptype, is_custom_manageable) FROM stdin;
1	The grandmas	2015-12-22 20:28:12.198719+01	2015-12-29 18:36:56.731725+01	\N	departmentadmin	f
2	duck1010.springaaaa admins	2016-01-20 04:17:30.493374+01	2016-01-20 04:18:08.798354+01	\N	periodadmin	f
3	duck1010 administrators	2016-01-20 04:19:42.353192+01	2016-01-20 04:19:42.353219+01	\N	subjectadmin	f
4	Custom manageable permissiongroup for Period#1	2016-02-03 17:56:01.40892+01	2016-02-03 17:56:01.408938+01	\N	periodadmin	t
\.


--
-- Data for Name: devilry_account_permissiongroupuser; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_permissiongroupuser (id, permissiongroup_id, user_id) FROM stdin;
1	1	1
2	2	12
3	3	14
4	4	10
\.


--
-- Data for Name: devilry_account_subjectpermissiongroup; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_subjectpermissiongroup (id, permissiongroup_id, subject_id) FROM stdin;
1	1	1
2	1	2
3	3	1
\.


--
-- Data for Name: devilry_account_user; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_user (id, password, last_login, is_superuser, shortname, fullname, lastname, datetime_joined, suspended_datetime, suspended_reason, languagecode) FROM stdin;
2	md5$3KRT0BYBVYuO$94583357915e72f337fcd49100121ffe	\N	f	dewey@example.com	Dewey Duck	Duck	2016-01-03 00:01:23.904395+01	\N		
3	md5$4kh8cjMMXX2M$7ebf58c36489254b715d79608c022101	\N	f	louie@example.com	Louie Duck	Duck	2016-01-03 00:01:23.920971+01	\N		
4	md5$EC1N1bbdDH1I$f178f7136b3691e18906166ee0efe5ca	\N	f	huey@example.com	Huey Duck	Duck	2016-01-03 00:01:23.924138+01	\N		
6	md5$23r9I32HRrRt$a5d639300faf27693592f4fbe6d4a219	\N	f	june@example.com	June Duck	Duck	2016-01-03 00:01:23.929449+01	\N		
7	md5$sYwPNZrUONMA$ece17aeedb49985694e73ccfb673762d	\N	f	july@example.com	July Duck	Duck	2016-01-03 00:01:23.932129+01	\N		
8	md5$bl0XFjiSsbGA$7e0f3030e8bfd0d54b91ca7843f001a3	\N	f	baldr@example.com	God of Beauty	Beauty	2016-01-03 00:01:23.934793+01	\N		
9	md5$b0e7QxZQhDjm$0a0c289438bb10acd7791166f22c9302	\N	f	freyja@example.com	Goddess of Love	Love	2016-01-03 00:01:23.937304+01	\N		
10	md5$jGBsBCPiCfD4$721eefd1556ba7a2dccba060f243263e	\N	f	freyr@example.com	God of Fertility	Fertility	2016-01-03 00:01:23.939944+01	\N		
11	md5$jTwxxR6ybeuX$7de276d388672758ce0e1991f92ee2da	\N	f	kvasir@example.com	God of Inspiration	Inspiration	2016-01-03 00:01:23.942802+01	\N		
15	md5$FQJM96zqt39y$49c4ad86e2d8bc053addcab6431db38d	\N	f	donald@example.com	Donald Duck	Duck	2016-01-03 00:03:43.101396+01	\N		
16	md5$IwVKSAdD2ueB$5e32c9a5bfa4092cdb4b4bda8a0e122e	\N	f	scrooge@example.com	Scrooge McDuck	McDuck	2016-01-03 00:03:59.432752+01	\N		
17	md5$VNqEOHzoWJLP$742f1d1b4d56fb6f51cdb76efc2105fa	\N	f	noname@example.com			2016-01-04 15:08:14.258809+01	\N		
18	md5$smoA02BvKYtp$17bc79166daf9d1c3de87d695e9708f9	\N	f	missingname@example.com			2016-01-04 15:25:10.473858+01	\N		
5	md5$t9KMIxJyNWXg$7136c7c30e463d0c9525f4744ef624b4	2016-02-08 20:20:46.753706+01	f	april@example.com	April Duck	Duck	2016-01-03 00:01:23.92689+01	\N		
1	md5$wqtfXF0fIxXj$894c06ca065b6dfa906004e40da2e9a4	2018-10-15 11:45:11.357639+02	t	grandma@example.com			2015-12-21 18:01:21.212212+01	\N		
13	md5$BVeSKhUc4Gkg$c5cfb847e6ef2a84bf2a0a3ab0424e8d	2018-10-15 11:53:46.91748+02	f	thor@example.com	God of thunder and Battle	Battle	2016-01-03 00:01:23.948728+01	\N		
14	md5$ot0qeIMptbS0$736743011a752ac3929d119435424766	2018-10-15 11:54:48.177013+02	f	odin@example.com	The "All Father"	Father"	2016-01-03 00:01:23.951457+01	\N		
12	md5$tT0zXYv0Zsuo$2b9bfb86f295cfd461b0ce2bb6ea2096	2018-10-15 11:55:13.707392+02	f	loki@example.com	Trickster and god of Mischief	Mischief	2016-01-03 00:01:23.945768+01	\N		
\.


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
-- Data for Name: devilry_account_username; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_account_username (id, created_datetime, last_updated_datetime, username, is_primary, user_id) FROM stdin;
\.


--
-- Data for Name: devilry_comment_comment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_comment_comment (id, text, created_datetime, published_datetime, user_role, comment_type, parent_id, user_id, draft_text) FROM stdin;
1	Here is my delivery :)	2016-02-08 11:26:30.912519+01	2016-02-08 11:25:23.021072+01	student	groupcomment	\N	5	
2	Very good work.	2016-02-08 11:28:23.712892+01	2016-02-08 11:27:11.75299+01	examiner	groupcomment	\N	13	
3	Nice	2018-10-15 11:54:00.846717+02	2018-10-15 11:54:00+02	examiner	groupcomment	\N	13	
4	Bad	2018-10-15 11:54:11.801794+02	2018-10-15 11:54:11+02	examiner	groupcomment	\N	13	
5	Nice	2018-10-15 11:54:21.464666+02	2018-10-15 11:54:21+02	examiner	groupcomment	\N	13	
6	Bad	2018-10-15 11:54:31.218192+02	2018-10-15 11:54:31+02	examiner	groupcomment	\N	13	
7	Delivery has been corrected.	2018-10-15 11:55:03.797507+02	2018-10-15 11:55:03+02	examiner	groupcomment	\N	14	
8	Delivery has been corrected.	2018-10-15 11:55:03.816266+02	2018-10-15 11:55:03+02	examiner	groupcomment	\N	14	
9	Delivery has been corrected.	2018-10-15 11:55:03.830782+02	2018-10-15 11:55:03+02	examiner	groupcomment	\N	14	
10	Delivery has been corrected.	2018-10-15 11:55:29.424082+02	2018-10-15 11:55:29+02	examiner	groupcomment	\N	12	
11	Delivery has been corrected.	2018-10-15 11:55:29.442387+02	2018-10-15 11:55:29+02	examiner	groupcomment	\N	12	
12	Delivery has been corrected.	2018-10-15 11:55:29.457167+02	2018-10-15 11:55:29+02	examiner	groupcomment	\N	12	
13	Delivery has been corrected.	2018-10-15 11:55:29.471886+02	2018-10-15 11:55:29+02	examiner	groupcomment	\N	12	
\.


--
-- Data for Name: devilry_comment_commentedithistory; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_comment_commentedithistory (id, edited_datetime, post_edit_text, pre_edit_text, comment_id, edited_by_id) FROM stdin;
1	2018-10-15 11:54:00.96895+02	Nice	Nice	3	13
2	2018-10-15 11:54:11.922541+02	Bad	Bad	4	13
3	2018-10-15 11:54:21.579822+02	Nice	Nice	5	13
4	2018-10-15 11:54:31.337457+02	Bad	Bad	6	13
\.


--
-- Data for Name: devilry_comment_commentfile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_comment_commentfile (id, mimetype, file, filename, filesize, processing_started_datetime, processing_completed_datetime, processing_successful, comment_id, created_datetime, v2_id) FROM stdin;
\.


--
-- Data for Name: devilry_comment_commentfileimage; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_comment_commentfileimage (id, image, image_width, image_height, thumbnail, thumbnail_width, thumbnail_height, comment_file_id) FROM stdin;
\.


--
-- Data for Name: devilry_compressionutil_compressedarchivemeta; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_compressionutil_compressedarchivemeta (id, content_object_id, created_datetime, archive_name, archive_path, archive_size, content_type_id, backend_id, deleted_datetime, created_by_id, created_by_role) FROM stdin;
\.


--
-- Data for Name: devilry_dbcache_assignmentgroupcacheddata; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_dbcache_assignmentgroupcacheddata (id, new_attempt_count, public_total_comment_count, public_student_comment_count, public_examiner_comment_count, public_admin_comment_count, public_student_file_upload_count, first_feedbackset_id, group_id, last_feedbackset_id, last_published_feedbackset_id, last_public_comment_by_examiner_datetime, last_public_comment_by_student_datetime, candidate_count, examiner_count) FROM stdin;
100	0	1	0	1	0	0	14	15	14	14	2018-10-15 11:55:29+02	\N	1	1
102	0	1	0	1	0	0	16	17	16	16	2018-10-15 11:55:29+02	\N	1	1
104	0	1	0	1	0	0	18	19	18	18	2018-10-15 11:55:29+02	\N	1	1
105	0	1	0	1	0	0	19	20	19	19	2018-10-15 11:55:29+02	\N	1	1
89	0	0	0	0	0	0	3	3	3	\N	\N	\N	1	1
90	0	0	0	0	0	0	4	4	4	\N	\N	\N	1	1
91	0	0	0	0	0	0	5	5	5	\N	\N	\N	1	1
92	0	0	0	0	0	0	6	6	6	\N	\N	\N	1	1
93	0	0	0	0	0	0	7	7	7	\N	\N	\N	1	1
94	0	0	0	0	0	0	8	8	8	\N	\N	\N	1	1
95	0	2	1	1	0	0	9	9	9	9	2016-02-08 11:27:11.75299+01	2016-02-08 11:25:23.021072+01	1	1
96	0	0	0	0	0	0	10	10	10	\N	\N	\N	1	0
97	0	0	0	0	0	0	11	11	11	\N	\N	\N	1	0
98	0	0	0	0	0	0	12	12	12	12	\N	\N	1	1
109	0	0	0	0	0	0	23	24	23	\N	\N	\N	1	0
110	0	1	0	1	0	0	24	25	24	24	2018-10-15 11:54:00+02	\N	1	1
99	0	1	0	1	0	0	13	14	13	13	2018-10-15 11:54:11+02	\N	1	1
106	0	1	0	1	0	0	20	21	20	20	2018-10-15 11:54:21+02	\N	1	1
103	0	1	0	1	0	0	17	18	17	17	2018-10-15 11:54:31+02	\N	1	1
101	0	1	0	1	0	0	15	16	15	15	2018-10-15 11:55:03+02	\N	1	1
107	0	1	0	1	0	0	21	22	21	21	2018-10-15 11:55:03+02	\N	1	1
108	0	1	0	1	0	0	22	23	22	22	2018-10-15 11:55:03+02	\N	1	1
\.


--
-- Data for Name: devilry_gradingsystem_feedbackdraft; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_gradingsystem_feedbackdraft (id, feedbacktext_editor, feedbacktext_raw, feedbacktext_html, points, published, save_timestamp, delivery_id, saved_by_id, staticfeedback_id) FROM stdin;
\.


--
-- Data for Name: devilry_gradingsystem_feedbackdraftfile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_gradingsystem_feedbackdraftfile (id, filename, file, delivery_id, saved_by_id) FROM stdin;
\.


--
-- Data for Name: devilry_group_feedbackset; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_feedbackset (id, grading_points, created_datetime, grading_published_datetime, deadline_datetime, created_by_id, group_id, grading_published_by_id, gradeform_data_json, feedbackset_type, ignored, ignored_reason, ignored_datetime, last_updated_by_id) FROM stdin;
10	\N	2016-02-06 15:10:23.06143+01	\N	2040-02-14 12:30:00+01	1	10	\N		first_attempt	f		\N	\N
11	\N	2016-02-06 15:10:32.192129+01	\N	2040-03-15 23:59:00+01	1	11	\N		first_attempt	f		\N	\N
9	1	2016-02-06 14:29:23.932176+01	2016-02-08 11:28:00+01	2040-01-31 12:30:00+01	1	9	13		first_attempt	f		\N	\N
12	80	2016-02-08 11:42:11.589679+01	2016-02-08 11:44:00+01	2040-03-02 15:30:00+01	1	12	13		first_attempt	f		\N	\N
3	\N	2016-01-20 11:17:01.702364+01	\N	2040-01-31 12:30:00+01	1	3	\N		first_attempt	f		\N	\N
4	\N	2016-01-20 11:17:01.702407+01	\N	2040-01-31 12:30:00+01	1	4	\N		first_attempt	f		\N	\N
5	\N	2016-01-20 11:17:01.702449+01	\N	2040-01-31 12:30:00+01	1	5	\N		first_attempt	f		\N	\N
6	\N	2016-01-20 11:17:01.702492+01	\N	2040-01-31 12:30:00+01	1	6	\N		first_attempt	f		\N	\N
7	\N	2016-01-20 11:17:01.702533+01	\N	2040-01-31 12:30:00+01	1	7	\N		first_attempt	f		\N	\N
8	\N	2016-01-20 11:17:01.702574+01	\N	2040-01-31 12:30:00+01	1	8	\N		first_attempt	f		\N	\N
23	\N	2016-02-08 20:55:47.544612+01	\N	2016-02-08 20:00:00+01	1	24	\N		first_attempt	f		\N	\N
24	1	2016-02-08 21:02:42.643666+01	2018-10-15 11:54:00.000002+02	2016-02-08 20:00:00+01	1	25	13		first_attempt	f		\N	\N
13	0	2016-02-08 20:55:47.543902+01	2018-10-15 11:54:11.000002+02	2016-02-08 20:00:00+01	1	14	13		first_attempt	f		\N	\N
20	1	2016-02-08 20:55:47.544461+01	2018-10-15 11:54:21.000002+02	2016-02-08 20:00:00+01	1	21	13		first_attempt	f		\N	\N
17	0	2016-02-08 20:55:47.544193+01	2018-10-15 11:54:31.000002+02	2016-02-08 20:00:00+01	1	18	13		first_attempt	f		\N	\N
15	1	2016-02-08 20:55:47.544065+01	2018-10-15 11:55:03.000001+02	2016-02-08 20:00:00+01	1	16	14		first_attempt	f		\N	\N
21	1	2016-02-08 20:55:47.544541+01	2018-10-15 11:55:03.000001+02	2016-02-08 20:00:00+01	1	22	14		first_attempt	f		\N	\N
22	1	2016-02-08 20:55:47.544574+01	2018-10-15 11:55:03.000001+02	2016-02-08 20:00:00+01	1	23	14		first_attempt	f		\N	\N
14	0	2016-02-08 20:55:47.544012+01	2018-10-15 11:55:29.000001+02	2016-02-08 20:00:00+01	1	15	12		first_attempt	f		\N	\N
16	0	2016-02-08 20:55:47.544145+01	2018-10-15 11:55:29.000001+02	2016-02-08 20:00:00+01	1	17	12		first_attempt	f		\N	\N
18	0	2016-02-08 20:55:47.544262+01	2018-10-15 11:55:29.000001+02	2016-02-08 20:00:00+01	1	19	12		first_attempt	f		\N	\N
19	0	2016-02-08 20:55:47.544383+01	2018-10-15 11:55:29.000001+02	2016-02-08 20:00:00+01	1	20	12		first_attempt	f		\N	\N
\.


--
-- Data for Name: devilry_group_feedbacksetdeadlinehistory; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_feedbacksetdeadlinehistory (id, changed_datetime, deadline_old, deadline_new, changed_by_id, feedback_set_id) FROM stdin;
\.


--
-- Data for Name: devilry_group_feedbacksetgradingupdatehistory; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_feedbacksetgradingupdatehistory (id, updated_datetime, old_grading_points, old_grading_published_datetime, feedback_set_id, old_grading_published_by_id, updated_by_id) FROM stdin;
\.


--
-- Data for Name: devilry_group_feedbacksetpassedpreviousperiod; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_feedbacksetpassedpreviousperiod (id, assignment_short_name, assignment_long_name, assignment_max_points, assignment_passing_grade_min_points, period_short_name, period_long_name, period_start_time, period_end_time, grading_points, grading_published_datetime, feedbackset_id, grading_published_by_id, created_by_id, created_datetime, passed_previous_period_type) FROM stdin;
\.


--
-- Data for Name: devilry_group_groupcomment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_groupcomment (comment_ptr_id, feedback_set_id, part_of_grading, visibility, v2_id) FROM stdin;
1	9	f	visible-to-everyone	
2	9	t	visible-to-everyone	
3	24	t	visible-to-everyone	
4	13	t	visible-to-everyone	
5	20	t	visible-to-everyone	
6	17	t	visible-to-everyone	
7	15	t	visible-to-everyone	
8	21	t	visible-to-everyone	
9	22	t	visible-to-everyone	
10	14	t	visible-to-everyone	
11	16	t	visible-to-everyone	
12	18	t	visible-to-everyone	
13	19	t	visible-to-everyone	
\.


--
-- Data for Name: devilry_group_groupcommentedithistory; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_groupcommentedithistory (commentedithistory_ptr_id, visibility, group_comment_id) FROM stdin;
1	private	3
2	private	4
3	private	5
4	private	6
\.


--
-- Data for Name: devilry_group_imageannotationcomment; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_group_imageannotationcomment (comment_ptr_id, x_coordinate, y_coordinate, feedback_set_id, image_id, part_of_grading, visibility) FROM stdin;
\.


--
-- Data for Name: devilry_import_v2database_importedmodel; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_import_v2database_importedmodel (id, content_object_id, data, content_type_id) FROM stdin;
\.


--
-- Data for Name: devilry_qualifiesforexam_deadlinetag; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_qualifiesforexam_deadlinetag (id, "timestamp", tag) FROM stdin;
\.


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
-- Data for Name: devilry_qualifiesforexam_status; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_qualifiesforexam_status (id, status, createtime, message, plugin, exported_timestamp, period_id, user_id) FROM stdin;
\.


--
-- Data for Name: devilry_student_uploadeddeliveryfile; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY devilry_student_uploadeddeliveryfile (id, uploaded_datetime, uploaded_file, filename, deadline_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


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
10	core	subject
11	core	period
12	core	periodapplicationkeyvalue
13	core	relatedexaminer
14	core	relatedstudent
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
57	devilry_dbcache	assignmentgroupcacheddata
58	core	assignmentgrouphistory
59	devilry_compressionutil	compressedarchivemeta
60	devilry_group	feedbacksetpassedpreviousperiod
61	devilry_group	feedbacksetdeadlinehistory
62	core	periodtag
63	sites	site
64	devilry_import_v2database	importedmodel
65	account	emailaddress
66	account	emailconfirmation
67	socialaccount	socialapp
68	socialaccount	socialaccount
69	socialaccount	socialtoken
70	core	candidateassignmentgrouphistory
71	core	examinerassignmentgrouphistory
72	devilry_group	feedbacksetgradingupdatehistory
73	ievv_developemail	developemail
74	devilry_group	groupcommentedithistory
75	devilry_comment	commentedithistory
\.


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
79	ievv_batchframework	0002_auto_20160413_0154	2016-08-06 13:27:18.143708+02
80	admin	0002_logentry_remove_auto_add	2017-02-23 11:12:47.154476+01
81	auth	0007_alter_validators_add_error_messages	2017-02-23 11:12:47.246541+01
82	core	0029_assignmentgrouphistory	2017-02-23 11:12:49.999847+01
83	core	0030_auto_20170124_1504	2017-02-23 11:12:50.117932+01
84	core	0031_auto_20170125_1601	2017-02-23 11:12:50.248653+01
85	core	0032_datamigrate_update_for_no_none_values_in_assignment_firstdeadline	2017-02-23 11:12:50.257053+01
86	core	0033_auto_20170220_1330	2017-02-23 11:12:50.349272+01
87	devilry_compressionutil	0001_initial	2017-02-23 11:12:51.846805+01
88	devilry_compressionutil	0002_auto_20170119_1202	2017-02-23 11:12:51.963664+01
89	devilry_compressionutil	0003_auto_20170119_1648	2017-02-23 11:12:52.19674+01
90	devilry_compressionutil	0004_auto_20170120_1733	2017-02-23 11:12:52.273303+01
91	devilry_group	0019_auto_20160912_1649	2017-02-23 11:12:54.813404+01
92	devilry_group	0020_feedbackset_ignored_datetime	2017-02-23 11:12:54.87953+01
93	devilry_group	0019_auto_20160822_1945	2017-02-23 11:12:54.957138+01
94	devilry_group	0021_merge	2017-02-23 11:12:54.958724+01
95	devilry_group	0022_auto_20170103_2308	2017-02-23 11:12:55.08844+01
96	devilry_group	0023_auto_20170104_0551	2017-02-23 11:12:55.207978+01
97	devilry_group	0024_auto_20170107_1838	2017-02-23 11:12:55.398607+01
98	devilry_dbcache	0001_initial	2017-02-23 11:12:55.482241+01
99	devilry_dbcache	0002_auto_20170108_0948	2017-02-23 11:12:56.534261+01
100	devilry_dbcache	0003_auto_20170108_1341	2017-02-23 11:12:56.757143+01
101	devilry_dbcache	0004_auto_20170108_1453	2017-02-23 11:12:56.887533+01
102	devilry_dbcache	0005_auto_20170124_1504	2017-02-23 11:12:57.022274+01
103	devilry_gradingsystem	0002_auto_20170108_0948	2017-02-23 11:12:57.709615+01
104	devilry_group	0025_auto_20170124_1504	2017-02-23 11:12:57.778301+01
105	devilry_group	0026_datamigrate_update_for_no_none_values_in_feedbackset_deadline	2017-02-23 11:12:57.865661+01
106	devilry_group	0027_auto_20170207_1951	2017-02-23 11:12:58.094522+01
107	devilry_group	0028_auto_20170208_1344	2017-02-23 11:12:58.27748+01
108	devilry_group	0027_auto_20170206_1146	2017-02-23 11:12:58.485549+01
109	devilry_group	0029_merge	2017-02-23 11:12:58.48727+01
110	devilry_qualifiesforexam	0002_auto_20170223_1112	2017-02-23 11:12:58.960632+01
111	core	0034_auto_20170303_1308	2017-03-16 17:21:16.651963+01
112	account	0001_initial	2017-12-20 14:55:58.761333+01
113	account	0002_email_max_length	2017-12-20 14:55:58.779718+01
114	core	0035_auto_20170523_1747	2017-12-20 14:56:04.190048+01
115	core	0036_auto_20170523_1748	2017-12-20 14:56:04.270296+01
116	core	0037_auto_20170620_1515	2017-12-20 14:56:04.609168+01
117	core	0038_auto_20170621_1720	2017-12-20 14:56:04.84382+01
118	devilry_comment	0006_auto_20170621_1720	2017-12-20 14:56:06.859034+01
119	devilry_comment	0007_auto_20170630_0309	2017-12-20 14:56:06.941546+01
120	devilry_comment	0008_commentfile_v2_id	2017-12-20 14:56:07.029252+01
121	devilry_group	0030_auto_20170621_1734	2017-12-20 14:56:15.913851+01
122	devilry_group	0031_groupcomment_v2_id	2017-12-20 14:56:16.026993+01
123	devilry_import_v2database	0001_initial	2017-12-20 14:56:16.14273+01
124	devilry_qualifiesforexam	0003_auto_20170629_1914	2017-12-20 14:56:17.069517+01
125	sites	0001_initial	2017-12-20 14:56:17.39184+01
126	sites	0002_alter_domain_unique	2017-12-20 14:56:17.414393+01
127	socialaccount	0001_initial	2017-12-20 14:56:18.151191+01
128	socialaccount	0002_token_max_lengths	2017-12-20 14:56:18.650575+01
129	socialaccount	0003_extra_data_default_dict	2017-12-20 14:56:18.773531+01
130	auth	0008_alter_user_username_max_length	2018-04-09 14:35:15.147066+02
131	core	0039_assignmentgroup_internal_is_being_deleted	2018-04-09 14:35:15.208431+02
132	core	0040_auto_20180214_1654	2018-04-09 14:35:15.296201+02
133	core	0041_auto_20180220_0651	2018-04-09 14:35:15.339996+02
134	core	0042_candidateassignmentgrouphistory_examinerassignmentgrouphistory	2018-04-09 14:35:15.472738+02
135	core	0043_auto_20180302_1139	2018-04-09 14:35:15.529072+02
136	devilry_compressionutil	0005_compressedarchivemeta_created_by	2018-04-09 14:35:15.638413+02
137	devilry_detektor	0002_auto_20180119_1137	2018-04-09 14:35:16.634929+02
138	devilry_group	0032_auto_20180214_1654	2018-04-09 14:35:17.71991+02
139	devilry_group	0033_feedbacksetgradingupdatehistory	2018-04-09 14:35:17.807989+02
140	devilry_group	0034_feedbackset_last_updated_by	2018-04-09 14:35:17.889712+02
141	devilry_comment	0009_auto_20180509_1528	2018-10-15 11:44:59.641584+02
142	devilry_comment	0010_commentedithistory	2018-10-15 11:44:59.763116+02
143	devilry_compressionutil	0006_compressedarchivemeta_created_by_role	2018-10-15 11:44:59.861162+02
144	devilry_compressionutil	0007_auto_20181002_1053	2018-10-15 11:44:59.962584+02
145	devilry_group	0035_groupcommentedithistory	2018-10-15 11:45:00.081119+02
146	ievv_developemail	0001_initial	2018-10-15 11:45:00.106411+02
\.


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
3q3ee45capchabq9iioxrhosyrsg6vtx	YWVlMWMzY2UwODBjYmZiOTRhNDRmZDVmNTRhNTI3OTFiMjQ1NGQ0Yjp7Il9hdXRoX3VzZXJfaGFzaCI6ImQwODJmYTFjOTgxNzI3NmU2ODg3MDkzM2NiNDgzN2VmMjczMzdjMmMiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiNSJ9	2016-02-20 14:28:33.710084+01
p95ggs9ihvz07g7qur3sp8pgeor2ji21	NDc0YWYzYzRmOTJhNzJhZDczYjM5NjA4ZmUyNWM5NmE3OWU2NjRmMjp7Il9hdXRoX3VzZXJfaGFzaCI6IjkzZWZkMGU4YjA1ZjNmYmU2ZGUwYzY2OTUxNDY3MmM4MzA0ZDRjMjQiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMTIifQ==	2016-02-20 18:04:02.497419+01
b7f56fzonivzzldphn6dzbk84lnqwzz1	YWVlMWMzY2UwODBjYmZiOTRhNDRmZDVmNTRhNTI3OTFiMjQ1NGQ0Yjp7Il9hdXRoX3VzZXJfaGFzaCI6ImQwODJmYTFjOTgxNzI3NmU2ODg3MDkzM2NiNDgzN2VmMjczMzdjMmMiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiNSJ9	2016-02-22 20:20:46.760111+01
i2m531v3ae0tk0bc8iqt3shjekhipet7	NGZmOGZlZWUzMTAyN2RhODYyNmZmNTIyZmVjMmEwYmFlOWY5ZmM2Mjp7Il9hdXRoX3VzZXJfaGFzaCI6ImMzYmE2MTgxYWExNjc4YmI0YzhiMDZiMzc3NDNiNWRmOTJhNTFkZTYiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMTMifQ==	2016-02-22 20:21:32.441645+01
njzxgphcbque9ci5jvpdwqi1btswmeor	NDJiYzE0MzEyNjdjM2E0NGQ0ODY3OWUzZGQ2MzkyNjIxZjljNTFjZDp7Il9hdXRoX3VzZXJfaGFzaCI6IjViMjA4NzZkYjI5ZGY2ZmJlNDE4N2U1YjE1ZTAzZTIyMGRiYjBiN2QiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMSJ9	2016-02-22 20:24:20.873582+01
vetesjwpl7lf4cg2xdur1esdv2rgu1yk	NDJiYzE0MzEyNjdjM2E0NGQ0ODY3OWUzZGQ2MzkyNjIxZjljNTFjZDp7Il9hdXRoX3VzZXJfaGFzaCI6IjViMjA4NzZkYjI5ZGY2ZmJlNDE4N2U1YjE1ZTAzZTIyMGRiYjBiN2QiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMSJ9	2016-08-20 14:34:40.183926+02
5jlmwud9l9rfsx5koc11ogxjn6xmubh5	NDJiYzE0MzEyNjdjM2E0NGQ0ODY3OWUzZGQ2MzkyNjIxZjljNTFjZDp7Il9hdXRoX3VzZXJfaGFzaCI6IjViMjA4NzZkYjI5ZGY2ZmJlNDE4N2U1YjE1ZTAzZTIyMGRiYjBiN2QiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMSJ9	2018-10-29 10:45:11.366386+01
y57wv1xi201u53k81ux3p3ikvmoingnd	NGZmOGZlZWUzMTAyN2RhODYyNmZmNTIyZmVjMmEwYmFlOWY5ZmM2Mjp7Il9hdXRoX3VzZXJfaGFzaCI6ImMzYmE2MTgxYWExNjc4YmI0YzhiMDZiMzc3NDNiNWRmOTJhNTFkZTYiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMTMifQ==	2018-10-29 10:53:46.924582+01
r6omvn9yt1zeovokq7xitv5whwwt7aye	YjZiOTUzMzEwOGYyNDlkNWZmZDdkOGFlMTEwZGI2ZGE4MGIwNDZlNDp7Il9hdXRoX3VzZXJfaGFzaCI6IjI1OWE4ODA1YTUyOGU1NTExMzc0ZTk2YjBlYTdmZTRiMzQwMTI3ZGIiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMTQifQ==	2018-10-29 10:54:48.183565+01
q7dtzrm2ucdskl0qupy0qz9hdmu5codc	NDc0YWYzYzRmOTJhNzJhZDczYjM5NjA4ZmUyNWM5NmE3OWU2NjRmMjp7Il9hdXRoX3VzZXJfaGFzaCI6IjkzZWZkMGU4YjA1ZjNmYmU2ZGUwYzY2OTUxNDY3MmM4MzA0ZDRjMjQiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkZXZpbHJ5LmRldmlscnlfYWNjb3VudC5hdXRoYmFja2VuZC5kZWZhdWx0LkVtYWlsQXV0aEJhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMTIifQ==	2018-10-29 10:55:13.715883+01
\.


--
-- Data for Name: django_site; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY django_site (id, domain, name) FROM stdin;
1	devilry.test:8000	Primary domain
\.


--
-- Data for Name: ievv_batchframework_batchoperation; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY ievv_batchframework_batchoperation (id, created_datetime, started_running_datetime, finished_datetime, context_object_id, operationtype, status, result, input_data_json, output_data_json, context_content_type_id, started_by_id) FROM stdin;
1	2016-01-20 11:17:01.683541+01	2016-01-20 11:17:01.681915+01	2016-01-20 11:17:01.708512+01	1	create-groups-with-candidate-and-feedbackset	running	successful			18	\N
2	2016-02-06 14:29:23.908585+01	2016-02-06 14:29:23.900239+01	2016-02-06 14:29:23.938409+01	1	create-groups-with-candidate-and-feedbackset	running	successful			18	\N
3	2016-02-06 15:10:23.040357+01	2016-02-06 15:10:23.03399+01	2016-02-06 15:10:23.067831+01	2	create-groups-with-candidate-and-feedbackset	running	successful			18	\N
4	2016-02-06 15:10:32.172524+01	2016-02-06 15:10:32.172383+01	2016-02-06 15:10:32.197123+01	4	create-groups-with-candidate-and-feedbackset	running	successful			18	\N
5	2016-02-08 11:42:11.57229+01	2016-02-08 11:42:11.565759+01	2016-02-08 11:42:11.594385+01	3	create-groups-with-candidate-and-feedbackset	running	successful			18	\N
6	2016-02-08 20:55:47.514322+01	2016-02-08 20:55:47.500494+01	2016-02-08 20:55:47.556552+01	5	create-groups-with-candidate-and-feedbackset	running	successful			18	\N
7	2016-02-08 21:02:42.62018+01	2016-02-08 21:02:42.620075+01	2016-02-08 21:02:42.648642+01	5	create-groups-with-candidate-and-feedbackset	running	successful			18	\N
\.


--
-- Data for Name: ievv_developemail_developemail; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY ievv_developemail_developemail (id, created_datetime, subject, from_email, to_emails, raw_message) FROM stdin;
1	2018-10-15 11:54:01.350945+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	april@example.com	Content-Type: multipart/alternative;\n boundary="===============4578215951615561901=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: april@example.com\nDate: Mon, 15 Oct 2018 09:54:01 -0000\nMessage-ID: <20181015095401.4876.65718@Stians-MacBook-Pro.local>\n\n--===============4578215951615561901==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: passed  \nCorrected datetime: Monday October 15, 2018, 11:54  \nDeadline datetime: Monday February 8, 2016, 20:00  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://thor.test:8000/devilry_group/student/25/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============4578215951615561901==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: passed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Monday October 15, 2018, 11:54\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Monday February 8, 2016, 20:00\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://thor.test:8000/devilry_group/student/25/feedbackfeed/">http://thor.test:8000/devilry_group/student/25/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============4578215951615561901==--\n
2	2018-10-15 11:54:12.052415+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	dewey@example.com	Content-Type: multipart/alternative;\n boundary="===============4028887874929833982=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: dewey@example.com\nDate: Mon, 15 Oct 2018 09:54:12 -0000\nMessage-ID: <20181015095412.4884.44271@Stians-MacBook-Pro.local>\n\n--===============4028887874929833982==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: failed  \nCorrected datetime: Monday October 15, 2018, 11:54  \nDeadline datetime: Monday February 8, 2016, 20:00  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://thor.test:8000/devilry_group/student/14/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============4028887874929833982==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: failed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Monday October 15, 2018, 11:54\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Monday February 8, 2016, 20:00\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://thor.test:8000/devilry_group/student/14/feedbackfeed/">http://thor.test:8000/devilry_group/student/14/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============4028887874929833982==--\n
3	2018-10-15 11:54:21.715808+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	donald@example.com	Content-Type: multipart/alternative;\n boundary="===============5382767832481345423=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: donald@example.com\nDate: Mon, 15 Oct 2018 09:54:21 -0000\nMessage-ID: <20181015095421.4893.85432@Stians-MacBook-Pro.local>\n\n--===============5382767832481345423==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: passed  \nCorrected datetime: Monday October 15, 2018, 11:54  \nDeadline datetime: Monday February 8, 2016, 20:00  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://thor.test:8000/devilry_group/student/21/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============5382767832481345423==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: passed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Monday October 15, 2018, 11:54\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Monday February 8, 2016, 20:00\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://thor.test:8000/devilry_group/student/21/feedbackfeed/">http://thor.test:8000/devilry_group/student/21/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============5382767832481345423==--\n
4	2018-10-15 11:54:31.466136+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	baldr@example.com	Content-Type: multipart/alternative;\n boundary="===============7632835851092272038=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: baldr@example.com\nDate: Mon, 15 Oct 2018 09:54:31 -0000\nMessage-ID: <20181015095431.4903.7918@Stians-MacBook-Pro.local>\n\n--===============7632835851092272038==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: failed  \nCorrected datetime: Monday October 15, 2018, 11:54  \nDeadline datetime: Monday February 8, 2016, 20:00  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://thor.test:8000/devilry_group/student/18/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============7632835851092272038==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: failed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Monday October 15, 2018, 11:54\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Monday February 8, 2016, 20:00\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://thor.test:8000/devilry_group/student/18/feedbackfeed/">http://thor.test:8000/devilry_group/student/18/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============7632835851092272038==--\n
5	2018-10-15 11:55:04.212908+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	june@example.com	Content-Type: multipart/alternative;\n boundary="===============4568666112183036233=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: june@example.com\nDate: Mon, 15 Oct 2018 09:55:04 -0000\nMessage-ID: <20181015095504.4924.60765@Stians-MacBook-Pro.local>\n\n--===============4568666112183036233==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: passed  \nCorrected datetime: Oct. 15, 2018, 11:55 a.m.  \nDeadline datetime: Feb. 8, 2016, 8 p.m.  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://odin.test:8000/devilry_group/student/16/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============4568666112183036233==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: passed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Oct. 15, 2018, 11:55 a.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Feb. 8, 2016, 8 p.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://odin.test:8000/devilry_group/student/16/feedbackfeed/">http://odin.test:8000/devilry_group/student/16/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============4568666112183036233==--\n
6	2018-10-15 11:55:04.254317+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	scrooge@example.com	Content-Type: multipart/alternative;\n boundary="===============5335110649855291189=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: scrooge@example.com\nDate: Mon, 15 Oct 2018 09:55:04 -0000\nMessage-ID: <20181015095504.4926.90983@Stians-MacBook-Pro.local>\n\n--===============5335110649855291189==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: passed  \nCorrected datetime: Oct. 15, 2018, 11:55 a.m.  \nDeadline datetime: Feb. 8, 2016, 8 p.m.  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://odin.test:8000/devilry_group/student/22/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============5335110649855291189==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: passed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Oct. 15, 2018, 11:55 a.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Feb. 8, 2016, 8 p.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://odin.test:8000/devilry_group/student/22/feedbackfeed/">http://odin.test:8000/devilry_group/student/22/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============5335110649855291189==--\n
7	2018-10-15 11:55:04.296823+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	noname@example.com	Content-Type: multipart/alternative;\n boundary="===============3180773209921931295=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: noname@example.com\nDate: Mon, 15 Oct 2018 09:55:04 -0000\nMessage-ID: <20181015095504.4928.74255@Stians-MacBook-Pro.local>\n\n--===============3180773209921931295==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: passed  \nCorrected datetime: Oct. 15, 2018, 11:55 a.m.  \nDeadline datetime: Feb. 8, 2016, 8 p.m.  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://odin.test:8000/devilry_group/student/23/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============3180773209921931295==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: passed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Oct. 15, 2018, 11:55 a.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Feb. 8, 2016, 8 p.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://odin.test:8000/devilry_group/student/23/feedbackfeed/">http://odin.test:8000/devilry_group/student/23/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============3180773209921931295==--\n
8	2018-10-15 11:55:29.875851+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	huey@example.com	Content-Type: multipart/alternative;\n boundary="===============7812806904017256756=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: huey@example.com\nDate: Mon, 15 Oct 2018 09:55:29 -0000\nMessage-ID: <20181015095529.4953.97156@Stians-MacBook-Pro.local>\n\n--===============7812806904017256756==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: failed  \nCorrected datetime: Oct. 15, 2018, 11:55 a.m.  \nDeadline datetime: Feb. 8, 2016, 8 p.m.  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://loki.test:8000/devilry_group/student/15/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============7812806904017256756==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: failed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Oct. 15, 2018, 11:55 a.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Feb. 8, 2016, 8 p.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://loki.test:8000/devilry_group/student/15/feedbackfeed/">http://loki.test:8000/devilry_group/student/15/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============7812806904017256756==--\n
9	2018-10-15 11:55:29.919454+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	july@example.com	Content-Type: multipart/alternative;\n boundary="===============2319111864300599081=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: july@example.com\nDate: Mon, 15 Oct 2018 09:55:29 -0000\nMessage-ID: <20181015095529.4955.26700@Stians-MacBook-Pro.local>\n\n--===============2319111864300599081==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: failed  \nCorrected datetime: Oct. 15, 2018, 11:55 a.m.  \nDeadline datetime: Feb. 8, 2016, 8 p.m.  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://loki.test:8000/devilry_group/student/17/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============2319111864300599081==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: failed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Oct. 15, 2018, 11:55 a.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Feb. 8, 2016, 8 p.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://loki.test:8000/devilry_group/student/17/feedbackfeed/">http://loki.test:8000/devilry_group/student/17/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============2319111864300599081==--\n
10	2018-10-15 11:55:29.95864+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	freyja@example.com	Content-Type: multipart/alternative;\n boundary="===============5753589789946783123=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: freyja@example.com\nDate: Mon, 15 Oct 2018 09:55:29 -0000\nMessage-ID: <20181015095529.4957.59834@Stians-MacBook-Pro.local>\n\n--===============5753589789946783123==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: failed  \nCorrected datetime: Oct. 15, 2018, 11:55 a.m.  \nDeadline datetime: Feb. 8, 2016, 8 p.m.  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://loki.test:8000/devilry_group/student/19/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============5753589789946783123==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: failed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Oct. 15, 2018, 11:55 a.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Feb. 8, 2016, 8 p.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://loki.test:8000/devilry_group/student/19/feedbackfeed/">http://loki.test:8000/devilry_group/student/19/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============5753589789946783123==--\n
11	2018-10-15 11:55:29.997476+02	[Devilry] Feedback for Assignment 0	devilry-support@example.com	freyr@example.com	Content-Type: multipart/alternative;\n boundary="===============2240908055631145015=="\nMIME-Version: 1.0\nSubject: [Devilry] Feedback for Assignment 0\nFrom: devilry-support@example.com\nTo: freyr@example.com\nDate: Mon, 15 Oct 2018 09:55:29 -0000\nMessage-ID: <20181015095529.4959.29269@Stians-MacBook-Pro.local>\n\n--===============2240908055631145015==\nContent-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\nResult: failed  \nCorrected datetime: Oct. 15, 2018, 11:55 a.m.  \nDeadline datetime: Feb. 8, 2016, 8 p.m.  \nAssignment: Assignment 0  \nSubject: DUCK1010 - Object Oriented Programming  \nSee the delivery feed for more details:\n<http://loki.test:8000/devilry_group/student/20/feedbackfeed/>  \n  \n\\--  \nThis is a message from the Devilry assignment delivery system. Please do not\nrespond to this email.\n\n\n--===============2240908055631145015==\nContent-Type: text/html; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\n\n\n\n<span class="devilry_email_feedback_result">\n    Result: failed\n</span>\n\n<br>\n<span class="devilry_email_feedback_corrected_datetime">\n    Corrected datetime: Oct. 15, 2018, 11:55 a.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_deadline_datetime">\n    Deadline datetime: Feb. 8, 2016, 8 p.m.\n</span>\n\n<br>\n<span class="devilry_email_feedback_assignment">\n    Assignment: Assignment 0\n</span>\n\n<br>\n<span class="devilry_email_feedback_subject">\n    Subject: DUCK1010 - Object Oriented Programming\n</span>\n\n<br>\n<span class="devilry_email_feedback_detail_text">\n    See the delivery feed for more details:\n</span>\n<span class="devilry_email_feedback_detail_url"><a href="http://loki.test:8000/devilry_group/student/20/feedbackfeed/">http://loki.test:8000/devilry_group/student/20/feedbackfeed/</a></span>\n<br><br>--<br>This is a message from the Devilry assignment delivery system. Please do not respond to this email.\n--===============2240908055631145015==--\n
\.


--
-- Data for Name: socialaccount_socialaccount; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY socialaccount_socialaccount (id, provider, uid, last_login, date_joined, extra_data, user_id) FROM stdin;
\.


--
-- Data for Name: socialaccount_socialapp; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY socialaccount_socialapp (id, provider, name, client_id, secret, key) FROM stdin;
\.


--
-- Data for Name: socialaccount_socialapp_sites; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY socialaccount_socialapp_sites (id, socialapp_id, site_id) FROM stdin;
\.


--
-- Data for Name: socialaccount_socialtoken; Type: TABLE DATA; Schema: public; Owner: dbdev
--

COPY socialaccount_socialtoken (id, token, token_secret, expires_at, account_id, app_id) FROM stdin;
\.


--
-- Name: account_emailaddress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('account_emailaddress_id_seq', 1, false);


--
-- Name: account_emailconfirmation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('account_emailconfirmation_id_seq', 1, false);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('auth_permission_id_seq', 225, true);


--
-- Name: core_assignment_admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignment_admins_id_seq', 1, false);


--
-- Name: core_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignment_id_seq', 5, true);


--
-- Name: core_assignmentgroup_examiners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgroup_examiners_id_seq', 47, true);


--
-- Name: core_assignmentgroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgroup_id_seq', 25, true);


--
-- Name: core_assignmentgrouphistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgrouphistory_id_seq', 1, false);


--
-- Name: core_assignmentgrouptag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_assignmentgrouptag_id_seq', 1, false);


--
-- Name: core_candidate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_candidate_id_seq', 25, true);


--
-- Name: core_candidateassignmentgrouphistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_candidateassignmentgrouphistory_id_seq', 1, false);


--
-- Name: core_deadline_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_deadline_id_seq', 1, false);


--
-- Name: core_delivery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_delivery_id_seq', 1, false);


--
-- Name: core_devilryuserprofile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_devilryuserprofile_id_seq', 1, false);


--
-- Name: core_examinerassignmentgrouphistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_examinerassignmentgrouphistory_id_seq', 22, true);


--
-- Name: core_filemeta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_filemeta_id_seq', 1, false);


--
-- Name: core_groupinvite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_groupinvite_id_seq', 1, false);


--
-- Name: core_period_admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_period_admins_id_seq', 1, false);


--
-- Name: core_period_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_period_id_seq', 5, true);


--
-- Name: core_periodapplicationkeyvalue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_periodapplicationkeyvalue_id_seq', 1, false);


--
-- Name: core_periodtag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_periodtag_id_seq', 1, false);


--
-- Name: core_periodtag_relatedexaminers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_periodtag_relatedexaminers_id_seq', 1, false);


--
-- Name: core_periodtag_relatedstudents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_periodtag_relatedstudents_id_seq', 1, false);


--
-- Name: core_pointrangetograde_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_pointrangetograde_id_seq', 6, true);


--
-- Name: core_pointtogrademap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_pointtogrademap_id_seq', 1, true);


--
-- Name: core_relatedexaminer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedexaminer_id_seq', 4, true);


--
-- Name: core_relatedstudent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedstudent_id_seq', 14, true);


--
-- Name: core_relatedstudentkeyvalue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_relatedstudentkeyvalue_id_seq', 1, false);


--
-- Name: core_staticfeedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_staticfeedback_id_seq', 1, false);


--
-- Name: core_staticfeedbackfileattachment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('core_staticfeedbackfileattachment_id_seq', 1, false);


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
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('cradmin_temporaryfileuploadstore_temporaryfile_id_seq', 1, false);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('cradmin_temporaryfileuploadstore_temporaryfilecollection_id_seq', 1, false);


--
-- Name: devilry_account_periodpermissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_periodpermissiongroup_id_seq', 2, true);


--
-- Name: devilry_account_permissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_permissiongroup_id_seq', 4, true);


--
-- Name: devilry_account_permissiongroupuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_permissiongroupuser_id_seq', 4, true);


--
-- Name: devilry_account_subjectpermissiongroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_subjectpermissiongroup_id_seq', 3, true);


--
-- Name: devilry_account_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_user_id_seq', 18, true);


--
-- Name: devilry_account_useremail_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_useremail_id_seq', 18, true);


--
-- Name: devilry_account_username_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_account_username_id_seq', 1, false);


--
-- Name: devilry_comment_comment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_comment_id_seq', 13, true);


--
-- Name: devilry_comment_commentedithistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_commentedithistory_id_seq', 4, true);


--
-- Name: devilry_comment_commentfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_commentfile_id_seq', 1, false);


--
-- Name: devilry_comment_commentfileimage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_comment_commentfileimage_id_seq', 1, false);


--
-- Name: devilry_compressionutil_compressedarchivemeta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_compressionutil_compressedarchivemeta_id_seq', 1, false);


--
-- Name: devilry_dbcache_assignmentgroupcacheddata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_dbcache_assignmentgroupcacheddata_id_seq', 158, true);


--
-- Name: devilry_gradingsystem_feedbackdraft_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_gradingsystem_feedbackdraft_id_seq', 1, false);


--
-- Name: devilry_gradingsystem_feedbackdraftfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_gradingsystem_feedbackdraftfile_id_seq', 1, false);


--
-- Name: devilry_group_feedbackset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_group_feedbackset_id_seq', 24, true);


--
-- Name: devilry_group_feedbacksetdeadlinehistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_group_feedbacksetdeadlinehistory_id_seq', 1, false);


--
-- Name: devilry_group_feedbacksetgradingupdatehistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_group_feedbacksetgradingupdatehistory_id_seq', 1, false);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_group_feedbacksetpassedpreviousperiod_id_seq', 1, false);


--
-- Name: devilry_import_v2database_importedmodel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_import_v2database_importedmodel_id_seq', 1, false);


--
-- Name: devilry_qualifiesforexam_deadlinetag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_qualifiesforexam_deadlinetag_id_seq', 1, false);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_qualifiesforexam_qualifiesforfinalexam_id_seq', 1, false);


--
-- Name: devilry_qualifiesforexam_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_qualifiesforexam_status_id_seq', 1, false);


--
-- Name: devilry_student_uploadeddeliveryfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('devilry_student_uploadeddeliveryfile_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_content_type_id_seq', 75, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_migrations_id_seq', 146, true);


--
-- Name: django_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('django_site_id_seq', 1, true);


--
-- Name: ievv_batchframework_batchoperation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('ievv_batchframework_batchoperation_id_seq', 7, true);


--
-- Name: ievv_developemail_developemail_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('ievv_developemail_developemail_id_seq', 11, true);


--
-- Name: socialaccount_socialaccount_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('socialaccount_socialaccount_id_seq', 1, false);


--
-- Name: socialaccount_socialapp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('socialaccount_socialapp_id_seq', 1, false);


--
-- Name: socialaccount_socialapp_sites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('socialaccount_socialapp_sites_id_seq', 1, false);


--
-- Name: socialaccount_socialtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dbdev
--

SELECT pg_catalog.setval('socialaccount_socialtoken_id_seq', 1, false);


--
-- Name: account_emailaddress account_emailaddress_email_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY account_emailaddress
    ADD CONSTRAINT account_emailaddress_email_key UNIQUE (email);


--
-- Name: account_emailaddress account_emailaddress_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY account_emailaddress
    ADD CONSTRAINT account_emailaddress_pkey PRIMARY KEY (id);


--
-- Name: account_emailconfirmation account_emailconfirmation_key_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY account_emailconfirmation
    ADD CONSTRAINT account_emailconfirmation_key_key UNIQUE (key);


--
-- Name: account_emailconfirmation account_emailconfirmation_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY account_emailconfirmation
    ADD CONSTRAINT account_emailconfirmation_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: core_assignment_admins core_assignment_admins_assignment_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment_admins
    ADD CONSTRAINT core_assignment_admins_assignment_id_user_id_key UNIQUE (assignment_id, user_id);


--
-- Name: core_assignment_admins core_assignment_admins_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment_admins
    ADD CONSTRAINT core_assignment_admins_pkey PRIMARY KEY (id);


--
-- Name: core_assignment core_assignment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment
    ADD CONSTRAINT core_assignment_pkey PRIMARY KEY (id);


--
-- Name: core_assignment core_assignment_short_name_1370cecf97cfafd_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment
    ADD CONSTRAINT core_assignment_short_name_1370cecf97cfafd_uniq UNIQUE (short_name, parentnode_id);


--
-- Name: core_assignmentgroup_examiners core_assignmentgroup_e_relatedexaminer_id_74db942d2f73e0d1_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT core_assignmentgroup_e_relatedexaminer_id_74db942d2f73e0d1_uniq UNIQUE (relatedexaminer_id, assignmentgroup_id);


--
-- Name: core_assignmentgroup_examiners core_assignmentgroup_examiners_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT core_assignmentgroup_examiners_pkey PRIMARY KEY (id);


--
-- Name: core_assignmentgroup core_assignmentgroup_feedback_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assignmentgroup_feedback_id_key UNIQUE (feedback_id);


--
-- Name: core_assignmentgroup core_assignmentgroup_last_deadline_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assignmentgroup_last_deadline_id_key UNIQUE (last_deadline_id);


--
-- Name: core_assignmentgroup core_assignmentgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assignmentgroup_pkey PRIMARY KEY (id);


--
-- Name: core_assignmentgrouphistory core_assignmentgrouphistory_assignment_group_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouphistory
    ADD CONSTRAINT core_assignmentgrouphistory_assignment_group_id_key UNIQUE (assignment_group_id);


--
-- Name: core_assignmentgrouphistory core_assignmentgrouphistory_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouphistory
    ADD CONSTRAINT core_assignmentgrouphistory_pkey PRIMARY KEY (id);


--
-- Name: core_assignmentgrouptag core_assignmentgroupt_assignment_group_id_27c175c3d5f47442_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouptag
    ADD CONSTRAINT core_assignmentgroupt_assignment_group_id_27c175c3d5f47442_uniq UNIQUE (assignment_group_id, tag);


--
-- Name: core_assignmentgrouptag core_assignmentgrouptag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouptag
    ADD CONSTRAINT core_assignmentgrouptag_pkey PRIMARY KEY (id);


--
-- Name: core_candidate core_candidate_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT core_candidate_pkey PRIMARY KEY (id);


--
-- Name: core_candidateassignmentgrouphistory core_candidateassignmentgrouphistory_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidateassignmentgrouphistory
    ADD CONSTRAINT core_candidateassignmentgrouphistory_pkey PRIMARY KEY (id);


--
-- Name: core_deadline core_deadline_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_deadline
    ADD CONSTRAINT core_deadline_pkey PRIMARY KEY (id);


--
-- Name: core_delivery core_delivery_last_feedback_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_delivery_last_feedback_id_key UNIQUE (last_feedback_id);


--
-- Name: core_delivery core_delivery_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_delivery_pkey PRIMARY KEY (id);


--
-- Name: core_devilryuserprofile core_devilryuserprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_devilryuserprofile
    ADD CONSTRAINT core_devilryuserprofile_pkey PRIMARY KEY (id);


--
-- Name: core_devilryuserprofile core_devilryuserprofile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_devilryuserprofile
    ADD CONSTRAINT core_devilryuserprofile_user_id_key UNIQUE (user_id);


--
-- Name: core_examinerassignmentgrouphistory core_examinerassignmentgrouphistory_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_examinerassignmentgrouphistory
    ADD CONSTRAINT core_examinerassignmentgrouphistory_pkey PRIMARY KEY (id);


--
-- Name: core_filemeta core_filemeta_delivery_id_1954e8947150727e_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_filemeta
    ADD CONSTRAINT core_filemeta_delivery_id_1954e8947150727e_uniq UNIQUE (delivery_id, filename);


--
-- Name: core_filemeta core_filemeta_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_filemeta
    ADD CONSTRAINT core_filemeta_pkey PRIMARY KEY (id);


--
-- Name: core_groupinvite core_groupinvite_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite
    ADD CONSTRAINT core_groupinvite_pkey PRIMARY KEY (id);


--
-- Name: core_period_admins core_period_admins_period_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period_admins
    ADD CONSTRAINT core_period_admins_period_id_user_id_key UNIQUE (period_id, user_id);


--
-- Name: core_period_admins core_period_admins_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period_admins
    ADD CONSTRAINT core_period_admins_pkey PRIMARY KEY (id);


--
-- Name: core_period core_period_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period
    ADD CONSTRAINT core_period_pkey PRIMARY KEY (id);


--
-- Name: core_period core_period_short_name_7f17bb6a11b77159_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period
    ADD CONSTRAINT core_period_short_name_7f17bb6a11b77159_uniq UNIQUE (short_name, parentnode_id);


--
-- Name: core_periodapplicationkeyvalue core_periodapplicationkeyvalue_period_id_1d119cce7d7c3cc9_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodapplicationkeyvalue
    ADD CONSTRAINT core_periodapplicationkeyvalue_period_id_1d119cce7d7c3cc9_uniq UNIQUE (period_id, application, key);


--
-- Name: core_periodapplicationkeyvalue core_periodapplicationkeyvalue_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodapplicationkeyvalue
    ADD CONSTRAINT core_periodapplicationkeyvalue_pkey PRIMARY KEY (id);


--
-- Name: core_periodtag core_periodtag_period_id_85a8db44_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag
    ADD CONSTRAINT core_periodtag_period_id_85a8db44_uniq UNIQUE (period_id, prefix, tag);


--
-- Name: core_periodtag core_periodtag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag
    ADD CONSTRAINT core_periodtag_pkey PRIMARY KEY (id);


--
-- Name: core_periodtag_relatedexaminers core_periodtag_relatedexaminers_periodtag_id_a5a9b5ab_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedexaminers
    ADD CONSTRAINT core_periodtag_relatedexaminers_periodtag_id_a5a9b5ab_uniq UNIQUE (periodtag_id, relatedexaminer_id);


--
-- Name: core_periodtag_relatedexaminers core_periodtag_relatedexaminers_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedexaminers
    ADD CONSTRAINT core_periodtag_relatedexaminers_pkey PRIMARY KEY (id);


--
-- Name: core_periodtag_relatedstudents core_periodtag_relatedstudents_periodtag_id_91082554_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedstudents
    ADD CONSTRAINT core_periodtag_relatedstudents_periodtag_id_91082554_uniq UNIQUE (periodtag_id, relatedstudent_id);


--
-- Name: core_periodtag_relatedstudents core_periodtag_relatedstudents_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedstudents
    ADD CONSTRAINT core_periodtag_relatedstudents_pkey PRIMARY KEY (id);


--
-- Name: core_pointrangetograde core_pointrangetogr_point_to_grade_map_id_11d9dec2e994579b_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointrangetograde
    ADD CONSTRAINT core_pointrangetogr_point_to_grade_map_id_11d9dec2e994579b_uniq UNIQUE (point_to_grade_map_id, grade);


--
-- Name: core_pointrangetograde core_pointrangetograde_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointrangetograde
    ADD CONSTRAINT core_pointrangetograde_pkey PRIMARY KEY (id);


--
-- Name: core_pointtogrademap core_pointtogrademap_assignment_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointtogrademap
    ADD CONSTRAINT core_pointtogrademap_assignment_id_key UNIQUE (assignment_id);


--
-- Name: core_pointtogrademap core_pointtogrademap_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointtogrademap
    ADD CONSTRAINT core_pointtogrademap_pkey PRIMARY KEY (id);


--
-- Name: core_relatedexaminer core_relatedexaminer_period_id_686024ad5991feee_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminer
    ADD CONSTRAINT core_relatedexaminer_period_id_686024ad5991feee_uniq UNIQUE (period_id, user_id);


--
-- Name: core_relatedexaminer core_relatedexaminer_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminer
    ADD CONSTRAINT core_relatedexaminer_pkey PRIMARY KEY (id);


--
-- Name: core_relatedstudent core_relatedstudent_period_id_7bcf68a574802ebf_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudent
    ADD CONSTRAINT core_relatedstudent_period_id_7bcf68a574802ebf_uniq UNIQUE (period_id, user_id);


--
-- Name: core_relatedstudent core_relatedstudent_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudent
    ADD CONSTRAINT core_relatedstudent_pkey PRIMARY KEY (id);


--
-- Name: core_relatedstudentkeyvalue core_relatedstudentkeyv_relatedstudent_id_1b3fefef6a62d342_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudentkeyvalue
    ADD CONSTRAINT core_relatedstudentkeyv_relatedstudent_id_1b3fefef6a62d342_uniq UNIQUE (relatedstudent_id, application, key);


--
-- Name: core_relatedstudentkeyvalue core_relatedstudentkeyvalue_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudentkeyvalue
    ADD CONSTRAINT core_relatedstudentkeyvalue_pkey PRIMARY KEY (id);


--
-- Name: core_staticfeedback core_staticfeedback_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedback
    ADD CONSTRAINT core_staticfeedback_pkey PRIMARY KEY (id);


--
-- Name: core_staticfeedbackfileattachment core_staticfeedbackfileattachment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedbackfileattachment
    ADD CONSTRAINT core_staticfeedbackfileattachment_pkey PRIMARY KEY (id);


--
-- Name: core_subject_admins core_subject_admins_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject_admins
    ADD CONSTRAINT core_subject_admins_pkey PRIMARY KEY (id);


--
-- Name: core_subject_admins core_subject_admins_subject_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject_admins
    ADD CONSTRAINT core_subject_admins_subject_id_user_id_key UNIQUE (subject_id, user_id);


--
-- Name: core_subject core_subject_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject
    ADD CONSTRAINT core_subject_pkey PRIMARY KEY (id);


--
-- Name: core_subject core_subject_short_name_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject
    ADD CONSTRAINT core_subject_short_name_key UNIQUE (short_name);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadata cradmin_generic_token_with_metadata_generictokenwithm_token_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_generic_token_with_metadata_generictokenwithmetadata
    ADD CONSTRAINT cradmin_generic_token_with_metadata_generictokenwithm_token_key UNIQUE (token);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadata cradmin_generic_token_with_metadata_generictokenwithmetada_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_generic_token_with_metadata_generictokenwithmetadata
    ADD CONSTRAINT cradmin_generic_token_with_metadata_generictokenwithmetada_pkey PRIMARY KEY (id);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile cradmin_temporaryfileuploadstore_temporaryfile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfile
    ADD CONSTRAINT cradmin_temporaryfileuploadstore_temporaryfile_pkey PRIMARY KEY (id);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection cradmin_temporaryfileuploadstore_temporaryfilecollection_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfilecollection
    ADD CONSTRAINT cradmin_temporaryfileuploadstore_temporaryfilecollection_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_periodpermissiongroup devilry_account_period_permissiongroup_id_4a6525c29ab05fdc_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup
    ADD CONSTRAINT devilry_account_period_permissiongroup_id_4a6525c29ab05fdc_uniq UNIQUE (permissiongroup_id, period_id);


--
-- Name: devilry_account_periodpermissiongroup devilry_account_periodpermissiongroup_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup
    ADD CONSTRAINT devilry_account_periodpermissiongroup_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_permissiongroupuser devilry_account_permis_permissiongroup_id_76525f84be59e6f6_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroupuser
    ADD CONSTRAINT devilry_account_permis_permissiongroup_id_76525f84be59e6f6_uniq UNIQUE (permissiongroup_id, user_id);


--
-- Name: devilry_account_permissiongroup devilry_account_permissiongroup_name_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroup
    ADD CONSTRAINT devilry_account_permissiongroup_name_key UNIQUE (name);


--
-- Name: devilry_account_permissiongroup devilry_account_permissiongroup_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroup
    ADD CONSTRAINT devilry_account_permissiongroup_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_permissiongroupuser devilry_account_permissiongroupuser_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroupuser
    ADD CONSTRAINT devilry_account_permissiongroupuser_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_subjectpermissiongroup devilry_account_subjec_permissiongroup_id_66aead092f6c883a_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup
    ADD CONSTRAINT devilry_account_subjec_permissiongroup_id_66aead092f6c883a_uniq UNIQUE (permissiongroup_id, subject_id);


--
-- Name: devilry_account_subjectpermissiongroup devilry_account_subjectpermissiongroup_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup
    ADD CONSTRAINT devilry_account_subjectpermissiongroup_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_user devilry_account_user_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_user
    ADD CONSTRAINT devilry_account_user_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_user devilry_account_user_shortname_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_user
    ADD CONSTRAINT devilry_account_user_shortname_key UNIQUE (shortname);


--
-- Name: devilry_account_useremail devilry_account_useremail_email_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_useremail
    ADD CONSTRAINT devilry_account_useremail_email_key UNIQUE (email);


--
-- Name: devilry_account_useremail devilry_account_useremail_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_useremail
    ADD CONSTRAINT devilry_account_useremail_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_useremail devilry_account_useremail_user_id_5536c616df78a7e9_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_useremail
    ADD CONSTRAINT devilry_account_useremail_user_id_5536c616df78a7e9_uniq UNIQUE (user_id, is_primary);


--
-- Name: devilry_account_username devilry_account_username_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_username
    ADD CONSTRAINT devilry_account_username_pkey PRIMARY KEY (id);


--
-- Name: devilry_account_username devilry_account_username_user_id_760100dbbc33fc25_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_username
    ADD CONSTRAINT devilry_account_username_user_id_760100dbbc33fc25_uniq UNIQUE (user_id, is_primary);


--
-- Name: devilry_account_username devilry_account_username_username_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_username
    ADD CONSTRAINT devilry_account_username_username_key UNIQUE (username);


--
-- Name: devilry_comment_comment devilry_comment_comment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_comment
    ADD CONSTRAINT devilry_comment_comment_pkey PRIMARY KEY (id);


--
-- Name: devilry_comment_commentedithistory devilry_comment_commentedithistory_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentedithistory
    ADD CONSTRAINT devilry_comment_commentedithistory_pkey PRIMARY KEY (id);


--
-- Name: devilry_comment_commentfile devilry_comment_commentfile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfile
    ADD CONSTRAINT devilry_comment_commentfile_pkey PRIMARY KEY (id);


--
-- Name: devilry_comment_commentfileimage devilry_comment_commentfileimage_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfileimage
    ADD CONSTRAINT devilry_comment_commentfileimage_pkey PRIMARY KEY (id);


--
-- Name: devilry_compressionutil_compressedarchivemeta devilry_compressionutil_compressedarchivemeta_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_compressionutil_compressedarchivemeta
    ADD CONSTRAINT devilry_compressionutil_compressedarchivemeta_pkey PRIMARY KEY (id);


--
-- Name: devilry_dbcache_assignmentgroupcacheddata devilry_dbcache_assignmentgroupcacheddata_group_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_dbcache_assignmentgroupcacheddata
    ADD CONSTRAINT devilry_dbcache_assignmentgroupcacheddata_group_id_key UNIQUE (group_id);


--
-- Name: devilry_dbcache_assignmentgroupcacheddata devilry_dbcache_assignmentgroupcacheddata_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_dbcache_assignmentgroupcacheddata
    ADD CONSTRAINT devilry_dbcache_assignmentgroupcacheddata_pkey PRIMARY KEY (id);


--
-- Name: devilry_gradingsystem_feedbackdraft devilry_gradingsystem_feedbackdraft_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT devilry_gradingsystem_feedbackdraft_pkey PRIMARY KEY (id);


--
-- Name: devilry_gradingsystem_feedbackdraft devilry_gradingsystem_feedbackdraft_staticfeedback_id_key; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT devilry_gradingsystem_feedbackdraft_staticfeedback_id_key UNIQUE (staticfeedback_id);


--
-- Name: devilry_gradingsystem_feedbackdraftfile devilry_gradingsystem_feedbackdraftfile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraftfile
    ADD CONSTRAINT devilry_gradingsystem_feedbackdraftfile_pkey PRIMARY KEY (id);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod devilry_group_feedbackse_feedbackset_id_2c6e12d3_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetpassedpreviousperiod
    ADD CONSTRAINT devilry_group_feedbackse_feedbackset_id_2c6e12d3_uniq UNIQUE (feedbackset_id);


--
-- Name: devilry_group_feedbackset devilry_group_feedbackset_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devilry_group_feedbackset_pkey PRIMARY KEY (id);


--
-- Name: devilry_group_feedbacksetdeadlinehistory devilry_group_feedbacksetdeadlinehistory_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetdeadlinehistory
    ADD CONSTRAINT devilry_group_feedbacksetdeadlinehistory_pkey PRIMARY KEY (id);


--
-- Name: devilry_group_feedbacksetgradingupdatehistory devilry_group_feedbacksetgradingupdatehistory_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetgradingupdatehistory
    ADD CONSTRAINT devilry_group_feedbacksetgradingupdatehistory_pkey PRIMARY KEY (id);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod devilry_group_feedbacksetpassedpreviousperiod_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetpassedpreviousperiod
    ADD CONSTRAINT devilry_group_feedbacksetpassedpreviousperiod_pkey PRIMARY KEY (id);


--
-- Name: devilry_group_groupcomment devilry_group_groupcomment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_groupcomment
    ADD CONSTRAINT devilry_group_groupcomment_pkey PRIMARY KEY (comment_ptr_id);


--
-- Name: devilry_group_groupcommentedithistory devilry_group_groupcommentedithistory_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_groupcommentedithistory
    ADD CONSTRAINT devilry_group_groupcommentedithistory_pkey PRIMARY KEY (commentedithistory_ptr_id);


--
-- Name: devilry_group_imageannotationcomment devilry_group_imageannotationcomment_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_imageannotationcomment
    ADD CONSTRAINT devilry_group_imageannotationcomment_pkey PRIMARY KEY (comment_ptr_id);


--
-- Name: devilry_import_v2database_importedmodel devilry_import_v2database_importedmodel_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_import_v2database_importedmodel
    ADD CONSTRAINT devilry_import_v2database_importedmodel_pkey PRIMARY KEY (id);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam devilry_qualifiesforexa_relatedstudent_id_487c8f68cac82075_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam
    ADD CONSTRAINT devilry_qualifiesforexa_relatedstudent_id_487c8f68cac82075_uniq UNIQUE (relatedstudent_id, status_id);


--
-- Name: devilry_qualifiesforexam_deadlinetag devilry_qualifiesforexam_deadlinetag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_deadlinetag
    ADD CONSTRAINT devilry_qualifiesforexam_deadlinetag_pkey PRIMARY KEY (id);


--
-- Name: devilry_qualifiesforexam_periodtag devilry_qualifiesforexam_periodtag_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_periodtag
    ADD CONSTRAINT devilry_qualifiesforexam_periodtag_pkey PRIMARY KEY (period_id);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam devilry_qualifiesforexam_qualifiesforfinalexam_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam
    ADD CONSTRAINT devilry_qualifiesforexam_qualifiesforfinalexam_pkey PRIMARY KEY (id);


--
-- Name: devilry_qualifiesforexam_status devilry_qualifiesforexam_status_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_status
    ADD CONSTRAINT devilry_qualifiesforexam_status_pkey PRIMARY KEY (id);


--
-- Name: devilry_student_uploadeddeliveryfile devilry_student_uploadeddeliv_deadline_id_5ceb94959540ad73_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile
    ADD CONSTRAINT devilry_student_uploadeddeliv_deadline_id_5ceb94959540ad73_uniq UNIQUE (deadline_id, user_id, filename);


--
-- Name: devilry_student_uploadeddeliveryfile devilry_student_uploadeddeliveryfile_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile
    ADD CONSTRAINT devilry_student_uploadeddeliveryfile_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_45f3b1d93ec8c61c_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_45f3b1d93ec8c61c_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site django_site_domain_a2e37b91_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_domain_a2e37b91_uniq UNIQUE (domain);


--
-- Name: django_site django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: ievv_batchframework_batchoperation ievv_batchframework_batchoperation_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_batchframework_batchoperation
    ADD CONSTRAINT ievv_batchframework_batchoperation_pkey PRIMARY KEY (id);


--
-- Name: ievv_developemail_developemail ievv_developemail_developemail_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_developemail_developemail
    ADD CONSTRAINT ievv_developemail_developemail_pkey PRIMARY KEY (id);


--
-- Name: socialaccount_socialaccount socialaccount_socialaccount_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socialaccount_pkey PRIMARY KEY (id);


--
-- Name: socialaccount_socialaccount socialaccount_socialaccount_provider_fc810c6e_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socialaccount_provider_fc810c6e_uniq UNIQUE (provider, uid);


--
-- Name: socialaccount_socialapp socialaccount_socialapp_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialapp
    ADD CONSTRAINT socialaccount_socialapp_pkey PRIMARY KEY (id);


--
-- Name: socialaccount_socialapp_sites socialaccount_socialapp_sites_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_socialapp_sites_pkey PRIMARY KEY (id);


--
-- Name: socialaccount_socialapp_sites socialaccount_socialapp_sites_socialapp_id_71a9a768_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_socialapp_sites_socialapp_id_71a9a768_uniq UNIQUE (socialapp_id, site_id);


--
-- Name: socialaccount_socialtoken socialaccount_socialtoken_app_id_fca4e0ac_uniq; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_socialtoken_app_id_fca4e0ac_uniq UNIQUE (app_id, account_id);


--
-- Name: socialaccount_socialtoken socialaccount_socialtoken_pkey; Type: CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_socialtoken_pkey PRIMARY KEY (id);


--
-- Name: account_emailaddress_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX account_emailaddress_e8701ad4 ON account_emailaddress USING btree (user_id);


--
-- Name: account_emailaddress_email_03be32b2_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX account_emailaddress_email_03be32b2_like ON account_emailaddress USING btree (email varchar_pattern_ops);


--
-- Name: account_emailconfirmation_6f1edeac; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX account_emailconfirmation_6f1edeac ON account_emailconfirmation USING btree (email_address_id);


--
-- Name: account_emailconfirmation_key_f43612bd_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX account_emailconfirmation_key_f43612bd_like ON account_emailconfirmation USING btree (key varchar_pattern_ops);


--
-- Name: auth_group_name_253ae2a6331666e8_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX auth_group_name_253ae2a6331666e8_like ON auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_0e939a4f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX auth_group_permissions_0e939a4f ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_8373b171; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX auth_group_permissions_8373b171 ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_417f1b1c; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX auth_permission_417f1b1c ON auth_permission USING btree (content_type_id);


--
-- Name: core_assignment_2fc6351a; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignment_2fc6351a ON core_assignment USING btree (long_name);


--
-- Name: core_assignment_4698bac7; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignment_4698bac7 ON core_assignment USING btree (short_name);


--
-- Name: core_assignment_admins_93c4899b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignment_admins_93c4899b ON core_assignment_admins USING btree (assignment_id);


--
-- Name: core_assignment_admins_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignment_admins_e8701ad4 ON core_assignment_admins USING btree (user_id);


--
-- Name: core_assignment_b25d0d2b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignment_b25d0d2b ON core_assignment USING btree (parentnode_id);


--
-- Name: core_assignment_ed066e54; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignment_ed066e54 ON core_assignment USING btree (anonymizationmode);


--
-- Name: core_assignment_long_name_74ff61759131213c_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignment_long_name_74ff61759131213c_like ON core_assignment USING btree (long_name varchar_pattern_ops);


--
-- Name: core_assignment_short_name_5a022141fd10855d_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignment_short_name_5a022141fd10855d_like ON core_assignment USING btree (short_name varchar_pattern_ops);


--
-- Name: core_assignmentgroup_3850dbd3; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgroup_3850dbd3 ON core_assignmentgroup USING btree (batchoperation_id);


--
-- Name: core_assignmentgroup_3dce5c8d; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgroup_3dce5c8d ON core_assignmentgroup USING btree (copied_from_id);


--
-- Name: core_assignmentgroup_b25d0d2b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgroup_b25d0d2b ON core_assignmentgroup USING btree (parentnode_id);


--
-- Name: core_assignmentgroup_examiners_5a4dbbf9; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgroup_examiners_5a4dbbf9 ON core_assignmentgroup_examiners USING btree (assignmentgroup_id);


--
-- Name: core_assignmentgroup_examiners_769693bb; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgroup_examiners_769693bb ON core_assignmentgroup_examiners USING btree (relatedexaminer_id);


--
-- Name: core_assignmentgroup_examiners_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgroup_examiners_e8701ad4 ON core_assignmentgroup_examiners USING btree (old_reference_not_in_use_user_id);


--
-- Name: core_assignmentgrouptag_3f3b3700; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgrouptag_3f3b3700 ON core_assignmentgrouptag USING btree (assignment_group_id);


--
-- Name: core_assignmentgrouptag_e4d23e84; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgrouptag_e4d23e84 ON core_assignmentgrouptag USING btree (tag);


--
-- Name: core_assignmentgrouptag_tag_445a27de8f965a31_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_assignmentgrouptag_tag_445a27de8f965a31_like ON core_assignmentgrouptag USING btree (tag varchar_pattern_ops);


--
-- Name: core_candidate_30a811f6; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_candidate_30a811f6 ON core_candidate USING btree (old_reference_not_in_use_student_id);


--
-- Name: core_candidate_39cb6676; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_candidate_39cb6676 ON core_candidate USING btree (relatedstudent_id);


--
-- Name: core_candidate_3f3b3700; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_candidate_3f3b3700 ON core_candidate USING btree (assignment_group_id);


--
-- Name: core_candidateassignmentgr_assignment_group_id_98c373a5; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_candidateassignmentgr_assignment_group_id_98c373a5 ON core_candidateassignmentgrouphistory USING btree (assignment_group_id);


--
-- Name: core_candidateassignmentgrouphistory_user_id_7a3668f9; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_candidateassignmentgrouphistory_user_id_7a3668f9 ON core_candidateassignmentgrouphistory USING btree (user_id);


--
-- Name: core_deadline_0c5d7d4e; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_deadline_0c5d7d4e ON core_deadline USING btree (added_by_id);


--
-- Name: core_deadline_3f3b3700; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_deadline_3f3b3700 ON core_deadline USING btree (assignment_group_id);


--
-- Name: core_delivery_13a4f9cc; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_delivery_13a4f9cc ON core_delivery USING btree (deadline_id);


--
-- Name: core_delivery_37b4f50c; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_delivery_37b4f50c ON core_delivery USING btree (delivered_by_id);


--
-- Name: core_delivery_51ce87c1; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_delivery_51ce87c1 ON core_delivery USING btree (alias_delivery_id);


--
-- Name: core_delivery_8ea1f7aa; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_delivery_8ea1f7aa ON core_delivery USING btree (copy_of_id);


--
-- Name: core_examinerassignmentgro_assignment_group_id_eb832a6e; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_examinerassignmentgro_assignment_group_id_eb832a6e ON core_examinerassignmentgrouphistory USING btree (assignment_group_id);


--
-- Name: core_examinerassignmentgrouphistory_user_id_1636fd1b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_examinerassignmentgrouphistory_user_id_1636fd1b ON core_examinerassignmentgrouphistory USING btree (user_id);


--
-- Name: core_filemeta_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_filemeta_7c4b99fe ON core_filemeta USING btree (delivery_id);


--
-- Name: core_groupinvite_0e939a4f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_groupinvite_0e939a4f ON core_groupinvite USING btree (group_id);


--
-- Name: core_groupinvite_a39b5ebd; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_groupinvite_a39b5ebd ON core_groupinvite USING btree (sent_to_id);


--
-- Name: core_groupinvite_d7ed4f1d; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_groupinvite_d7ed4f1d ON core_groupinvite USING btree (sent_by_id);


--
-- Name: core_period_2fc6351a; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_period_2fc6351a ON core_period USING btree (long_name);


--
-- Name: core_period_4698bac7; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_period_4698bac7 ON core_period USING btree (short_name);


--
-- Name: core_period_admins_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_period_admins_b1efa79f ON core_period_admins USING btree (period_id);


--
-- Name: core_period_admins_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_period_admins_e8701ad4 ON core_period_admins USING btree (user_id);


--
-- Name: core_period_b25d0d2b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_period_b25d0d2b ON core_period USING btree (parentnode_id);


--
-- Name: core_period_long_name_5770388f6d0c1ee0_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_period_long_name_5770388f6d0c1ee0_like ON core_period USING btree (long_name varchar_pattern_ops);


--
-- Name: core_period_short_name_1e673681e8719241_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_period_short_name_1e673681e8719241_like ON core_period USING btree (short_name varchar_pattern_ops);


--
-- Name: core_periodapplicationkeyvalu_application_195ab7f853d68bd7_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodapplicationkeyvalu_application_195ab7f853d68bd7_like ON core_periodapplicationkeyvalue USING btree (application varchar_pattern_ops);


--
-- Name: core_periodapplicationkeyvalue_2063c160; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodapplicationkeyvalue_2063c160 ON core_periodapplicationkeyvalue USING btree (value);


--
-- Name: core_periodapplicationkeyvalue_3676d55f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodapplicationkeyvalue_3676d55f ON core_periodapplicationkeyvalue USING btree (application);


--
-- Name: core_periodapplicationkeyvalue_3c6e0b8a; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodapplicationkeyvalue_3c6e0b8a ON core_periodapplicationkeyvalue USING btree (key);


--
-- Name: core_periodapplicationkeyvalue_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodapplicationkeyvalue_b1efa79f ON core_periodapplicationkeyvalue USING btree (period_id);


--
-- Name: core_periodapplicationkeyvalue_key_7329f2bf53861cf8_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodapplicationkeyvalue_key_7329f2bf53861cf8_like ON core_periodapplicationkeyvalue USING btree (key varchar_pattern_ops);


--
-- Name: core_periodapplicationkeyvalue_value_3c6e96e7ba7f6690_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodapplicationkeyvalue_value_3c6e96e7ba7f6690_like ON core_periodapplicationkeyvalue USING btree (value text_pattern_ops);


--
-- Name: core_periodtag_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodtag_b1efa79f ON core_periodtag USING btree (period_id);


--
-- Name: core_periodtag_e4d23e84; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodtag_e4d23e84 ON core_periodtag USING btree (tag);


--
-- Name: core_periodtag_relatedexaminers_769693bb; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodtag_relatedexaminers_769693bb ON core_periodtag_relatedexaminers USING btree (relatedexaminer_id);


--
-- Name: core_periodtag_relatedexaminers_97a799e1; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodtag_relatedexaminers_97a799e1 ON core_periodtag_relatedexaminers USING btree (periodtag_id);


--
-- Name: core_periodtag_relatedstudents_39cb6676; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodtag_relatedstudents_39cb6676 ON core_periodtag_relatedstudents USING btree (relatedstudent_id);


--
-- Name: core_periodtag_relatedstudents_97a799e1; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodtag_relatedstudents_97a799e1 ON core_periodtag_relatedstudents USING btree (periodtag_id);


--
-- Name: core_periodtag_tag_b42bbccb_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_periodtag_tag_b42bbccb_like ON core_periodtag USING btree (tag varchar_pattern_ops);


--
-- Name: core_pointrangetograde_326d17f1; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_pointrangetograde_326d17f1 ON core_pointrangetograde USING btree (point_to_grade_map_id);


--
-- Name: core_relatedexaminer_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedexaminer_b1efa79f ON core_relatedexaminer USING btree (period_id);


--
-- Name: core_relatedexaminer_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedexaminer_e8701ad4 ON core_relatedexaminer USING btree (user_id);


--
-- Name: core_relatedstudent_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudent_b1efa79f ON core_relatedstudent USING btree (period_id);


--
-- Name: core_relatedstudent_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudent_e8701ad4 ON core_relatedstudent USING btree (user_id);


--
-- Name: core_relatedstudentkeyvalue_2063c160; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudentkeyvalue_2063c160 ON core_relatedstudentkeyvalue USING btree (value);


--
-- Name: core_relatedstudentkeyvalue_3676d55f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudentkeyvalue_3676d55f ON core_relatedstudentkeyvalue USING btree (application);


--
-- Name: core_relatedstudentkeyvalue_39cb6676; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudentkeyvalue_39cb6676 ON core_relatedstudentkeyvalue USING btree (relatedstudent_id);


--
-- Name: core_relatedstudentkeyvalue_3c6e0b8a; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudentkeyvalue_3c6e0b8a ON core_relatedstudentkeyvalue USING btree (key);


--
-- Name: core_relatedstudentkeyvalue_application_485c1d338d75ced_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudentkeyvalue_application_485c1d338d75ced_like ON core_relatedstudentkeyvalue USING btree (application varchar_pattern_ops);


--
-- Name: core_relatedstudentkeyvalue_key_4d695a35117794a4_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudentkeyvalue_key_4d695a35117794a4_like ON core_relatedstudentkeyvalue USING btree (key varchar_pattern_ops);


--
-- Name: core_relatedstudentkeyvalue_value_2e6d2220af915c34_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_relatedstudentkeyvalue_value_2e6d2220af915c34_like ON core_relatedstudentkeyvalue USING btree (value text_pattern_ops);


--
-- Name: core_staticfeedback_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_staticfeedback_7c4b99fe ON core_staticfeedback USING btree (delivery_id);


--
-- Name: core_staticfeedback_bc7c970b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_staticfeedback_bc7c970b ON core_staticfeedback USING btree (saved_by_id);


--
-- Name: core_staticfeedbackfileattachment_a869bd9a; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_staticfeedbackfileattachment_a869bd9a ON core_staticfeedbackfileattachment USING btree (staticfeedback_id);


--
-- Name: core_subject_2fc6351a; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_subject_2fc6351a ON core_subject USING btree (long_name);


--
-- Name: core_subject_admins_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_subject_admins_e8701ad4 ON core_subject_admins USING btree (user_id);


--
-- Name: core_subject_admins_ffaba1d1; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_subject_admins_ffaba1d1 ON core_subject_admins USING btree (subject_id);


--
-- Name: core_subject_long_name_19cff4d64a1d8f4c_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_subject_long_name_19cff4d64a1d8f4c_like ON core_subject USING btree (long_name varchar_pattern_ops);


--
-- Name: core_subject_short_name_619954c9668d7b05_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX core_subject_short_name_619954c9668d7b05_like ON core_subject USING btree (short_name varchar_pattern_ops);


--
-- Name: cradmin_generic_token_with_metadata_g_app_4f5ee45a2fa39c00_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX cradmin_generic_token_with_metadata_g_app_4f5ee45a2fa39c00_like ON cradmin_generic_token_with_metadata_generictokenwithmetadata USING btree (app varchar_pattern_ops);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadatcb1d; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX cradmin_generic_token_with_metadata_generictokenwithmetadatcb1d ON cradmin_generic_token_with_metadata_generictokenwithmetadata USING btree (app);


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadatf2be; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX cradmin_generic_token_with_metadata_generictokenwithmetadatf2be ON cradmin_generic_token_with_metadata_generictokenwithmetadata USING btree (content_type_id);


--
-- Name: cradmin_generic_token_with_metadata_token_4c62e4a4d20b64c8_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX cradmin_generic_token_with_metadata_token_4c62e4a4d20b64c8_like ON cradmin_generic_token_with_metadata_generictokenwithmetadata USING btree (token varchar_pattern_ops);


--
-- Name: cradmin_temporaryfileuploadstore_filename_3ca12967fd9be7b2_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX cradmin_temporaryfileuploadstore_filename_3ca12967fd9be7b2_like ON cradmin_temporaryfileuploadstore_temporaryfile USING btree (filename text_pattern_ops);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_0a1a4dd8; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX cradmin_temporaryfileuploadstore_temporaryfile_0a1a4dd8 ON cradmin_temporaryfileuploadstore_temporaryfile USING btree (collection_id);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile_435ed7e9; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX cradmin_temporaryfileuploadstore_temporaryfile_435ed7e9 ON cradmin_temporaryfileuploadstore_temporaryfile USING btree (filename);


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection_e8a4df; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX cradmin_temporaryfileuploadstore_temporaryfilecollection_e8a4df ON cradmin_temporaryfileuploadstore_temporaryfilecollection USING btree (user_id);


--
-- Name: devilry_account_periodpermissiongroup_3e7065db; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_periodpermissiongroup_3e7065db ON devilry_account_periodpermissiongroup USING btree (permissiongroup_id);


--
-- Name: devilry_account_periodpermissiongroup_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_periodpermissiongroup_b1efa79f ON devilry_account_periodpermissiongroup USING btree (period_id);


--
-- Name: devilry_account_permissiongroup_name_ef79acb69a7dd49_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_permissiongroup_name_ef79acb69a7dd49_like ON devilry_account_permissiongroup USING btree (name varchar_pattern_ops);


--
-- Name: devilry_account_permissiongroupuser_3e7065db; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_permissiongroupuser_3e7065db ON devilry_account_permissiongroupuser USING btree (permissiongroup_id);


--
-- Name: devilry_account_permissiongroupuser_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_permissiongroupuser_e8701ad4 ON devilry_account_permissiongroupuser USING btree (user_id);


--
-- Name: devilry_account_subjectpermissiongroup_3e7065db; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_subjectpermissiongroup_3e7065db ON devilry_account_subjectpermissiongroup USING btree (permissiongroup_id);


--
-- Name: devilry_account_subjectpermissiongroup_ffaba1d1; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_subjectpermissiongroup_ffaba1d1 ON devilry_account_subjectpermissiongroup USING btree (subject_id);


--
-- Name: devilry_account_user_shortname_343b9f8ebd9bbcb0_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_user_shortname_343b9f8ebd9bbcb0_like ON devilry_account_user USING btree (shortname varchar_pattern_ops);


--
-- Name: devilry_account_useremail_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_useremail_e8701ad4 ON devilry_account_useremail USING btree (user_id);


--
-- Name: devilry_account_useremail_email_1db096b7c69382_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_useremail_email_1db096b7c69382_like ON devilry_account_useremail USING btree (email varchar_pattern_ops);


--
-- Name: devilry_account_username_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_username_e8701ad4 ON devilry_account_username USING btree (user_id);


--
-- Name: devilry_account_username_username_107726b2079e7651_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_account_username_username_107726b2079e7651_like ON devilry_account_username USING btree (username varchar_pattern_ops);


--
-- Name: devilry_comment_comment_6be37982; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_comment_comment_6be37982 ON devilry_comment_comment USING btree (parent_id);


--
-- Name: devilry_comment_comment_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_comment_comment_e8701ad4 ON devilry_comment_comment USING btree (user_id);


--
-- Name: devilry_comment_commentedithistory_comment_id_91baeb5a; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_comment_commentedithistory_comment_id_91baeb5a ON devilry_comment_commentedithistory USING btree (comment_id);


--
-- Name: devilry_comment_commentedithistory_edited_by_id_2e51be6c; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_comment_commentedithistory_edited_by_id_2e51be6c ON devilry_comment_commentedithistory USING btree (edited_by_id);


--
-- Name: devilry_comment_commentfile_69b97d17; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_comment_commentfile_69b97d17 ON devilry_comment_commentfile USING btree (comment_id);


--
-- Name: devilry_comment_commentfileimage_b009b360; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_comment_commentfileimage_b009b360 ON devilry_comment_commentfileimage USING btree (comment_file_id);


--
-- Name: devilry_compressionutil_co_created_by_id_edfcbf68; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_compressionutil_co_created_by_id_edfcbf68 ON devilry_compressionutil_compressedarchivemeta USING btree (created_by_id);


--
-- Name: devilry_compressionutil_compressedarchivemeta_417f1b1c; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_compressionutil_compressedarchivemeta_417f1b1c ON devilry_compressionutil_compressedarchivemeta USING btree (content_type_id);


--
-- Name: devilry_dbcache_assignmentgroupcacheddata_1f1b65ab; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_dbcache_assignmentgroupcacheddata_1f1b65ab ON devilry_dbcache_assignmentgroupcacheddata USING btree (last_published_feedbackset_id);


--
-- Name: devilry_dbcache_assignmentgroupcacheddata_5da8f6f1; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_dbcache_assignmentgroupcacheddata_5da8f6f1 ON devilry_dbcache_assignmentgroupcacheddata USING btree (first_feedbackset_id);


--
-- Name: devilry_dbcache_assignmentgroupcacheddata_ce0430ee; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_dbcache_assignmentgroupcacheddata_ce0430ee ON devilry_dbcache_assignmentgroupcacheddata USING btree (last_feedbackset_id);


--
-- Name: devilry_gradingsystem_feedbackdraft_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_gradingsystem_feedbackdraft_7c4b99fe ON devilry_gradingsystem_feedbackdraft USING btree (delivery_id);


--
-- Name: devilry_gradingsystem_feedbackdraft_bc7c970b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_gradingsystem_feedbackdraft_bc7c970b ON devilry_gradingsystem_feedbackdraft USING btree (saved_by_id);


--
-- Name: devilry_gradingsystem_feedbackdraftfile_7c4b99fe; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_gradingsystem_feedbackdraftfile_7c4b99fe ON devilry_gradingsystem_feedbackdraftfile USING btree (delivery_id);


--
-- Name: devilry_gradingsystem_feedbackdraftfile_bc7c970b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_gradingsystem_feedbackdraftfile_bc7c970b ON devilry_gradingsystem_feedbackdraftfile USING btree (saved_by_id);


--
-- Name: devilry_group_feedbackset_0069413d; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbackset_0069413d ON devilry_group_feedbackset USING btree (feedbackset_type);


--
-- Name: devilry_group_feedbackset_0e939a4f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbackset_0e939a4f ON devilry_group_feedbackset USING btree (group_id);


--
-- Name: devilry_group_feedbackset_7dbe6d4c; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbackset_7dbe6d4c ON devilry_group_feedbackset USING btree (grading_published_by_id);


--
-- Name: devilry_group_feedbackset_e93cb7eb; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbackset_e93cb7eb ON devilry_group_feedbackset USING btree (created_by_id);


--
-- Name: devilry_group_feedbackset_last_updated_by_id_960089c6; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbackset_last_updated_by_id_960089c6 ON devilry_group_feedbackset USING btree (last_updated_by_id);


--
-- Name: devilry_group_feedbacksetdeadlinehistory_4e893a26; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetdeadlinehistory_4e893a26 ON devilry_group_feedbacksetdeadlinehistory USING btree (changed_by_id);


--
-- Name: devilry_group_feedbacksetdeadlinehistory_c08198b8; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetdeadlinehistory_c08198b8 ON devilry_group_feedbacksetdeadlinehistory USING btree (feedback_set_id);


--
-- Name: devilry_group_feedbacksetg_feedback_set_id_24f4c349; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetg_feedback_set_id_24f4c349 ON devilry_group_feedbacksetgradingupdatehistory USING btree (feedback_set_id);


--
-- Name: devilry_group_feedbacksetg_old_grading_published_by_i_f855818b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetg_old_grading_published_by_i_f855818b ON devilry_group_feedbacksetgradingupdatehistory USING btree (old_grading_published_by_id);


--
-- Name: devilry_group_feedbacksetg_updated_by_id_5aa2ab0f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetg_updated_by_id_5aa2ab0f ON devilry_group_feedbacksetgradingupdatehistory USING btree (updated_by_id);


--
-- Name: devilry_group_feedbacksetp_created_by_id_b8572995; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetp_created_by_id_b8572995 ON devilry_group_feedbacksetpassedpreviousperiod USING btree (created_by_id);


--
-- Name: devilry_group_feedbacksetpa_assignment_short_name_be9f985a_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpa_assignment_short_name_be9f985a_like ON devilry_group_feedbacksetpassedpreviousperiod USING btree (assignment_short_name varchar_pattern_ops);


--
-- Name: devilry_group_feedbacksetpas_assignment_long_name_adac6ed1_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpas_assignment_long_name_adac6ed1_like ON devilry_group_feedbacksetpassedpreviousperiod USING btree (assignment_long_name varchar_pattern_ops);


--
-- Name: devilry_group_feedbacksetpassed_period_short_name_a541d96e_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpassed_period_short_name_a541d96e_like ON devilry_group_feedbacksetpassedpreviousperiod USING btree (period_short_name varchar_pattern_ops);


--
-- Name: devilry_group_feedbacksetpassedp_period_long_name_c7d4b92b_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpassedp_period_long_name_c7d4b92b_like ON devilry_group_feedbacksetpassedpreviousperiod USING btree (period_long_name varchar_pattern_ops);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod_054dba96; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpassedpreviousperiod_054dba96 ON devilry_group_feedbacksetpassedpreviousperiod USING btree (assignment_short_name);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod_1336f3d8; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpassedpreviousperiod_1336f3d8 ON devilry_group_feedbacksetpassedpreviousperiod USING btree (assignment_long_name);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod_134162fd; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpassedpreviousperiod_134162fd ON devilry_group_feedbacksetpassedpreviousperiod USING btree (period_long_name);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod_c74421d4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpassedpreviousperiod_c74421d4 ON devilry_group_feedbacksetpassedpreviousperiod USING btree (period_short_name);


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod_fa900df0; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_feedbacksetpassedpreviousperiod_fa900df0 ON devilry_group_feedbacksetpassedpreviousperiod USING btree (grading_published_by_id);


--
-- Name: devilry_group_groupcomment_c08198b8; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_groupcomment_c08198b8 ON devilry_group_groupcomment USING btree (feedback_set_id);


--
-- Name: devilry_group_groupcomment_f79b1d64; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_groupcomment_f79b1d64 ON devilry_group_groupcomment USING btree (visibility);


--
-- Name: devilry_group_groupcommentedithistory_group_comment_id_123b9b0d; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_groupcommentedithistory_group_comment_id_123b9b0d ON devilry_group_groupcommentedithistory USING btree (group_comment_id);


--
-- Name: devilry_group_groupcommentedithistory_visibility_fddebfac; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_groupcommentedithistory_visibility_fddebfac ON devilry_group_groupcommentedithistory USING btree (visibility);


--
-- Name: devilry_group_groupcommentedithistory_visibility_fddebfac_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_groupcommentedithistory_visibility_fddebfac_like ON devilry_group_groupcommentedithistory USING btree (visibility varchar_pattern_ops);


--
-- Name: devilry_group_imageannotationcomment_c08198b8; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_imageannotationcomment_c08198b8 ON devilry_group_imageannotationcomment USING btree (feedback_set_id);


--
-- Name: devilry_group_imageannotationcomment_f33175e6; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_imageannotationcomment_f33175e6 ON devilry_group_imageannotationcomment USING btree (image_id);


--
-- Name: devilry_group_imageannotationcomment_f79b1d64; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_group_imageannotationcomment_f79b1d64 ON devilry_group_imageannotationcomment USING btree (visibility);


--
-- Name: devilry_import_v2database_importedmodel_417f1b1c; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_import_v2database_importedmodel_417f1b1c ON devilry_import_v2database_importedmodel USING btree (content_type_id);


--
-- Name: devilry_qualifiesforexam_periodtag_f2e8843d; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_qualifiesforexam_periodtag_f2e8843d ON devilry_qualifiesforexam_periodtag USING btree (deadlinetag_id);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_39cb6676; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_qualifiesforexam_qualifiesforfinalexam_39cb6676 ON devilry_qualifiesforexam_qualifiesforfinalexam USING btree (relatedstudent_id);


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam_dc91ed4b; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_qualifiesforexam_qualifiesforfinalexam_dc91ed4b ON devilry_qualifiesforexam_qualifiesforfinalexam USING btree (status_id);


--
-- Name: devilry_qualifiesforexam_status_b1efa79f; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_qualifiesforexam_status_b1efa79f ON devilry_qualifiesforexam_status USING btree (period_id);


--
-- Name: devilry_qualifiesforexam_status_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_qualifiesforexam_status_e8701ad4 ON devilry_qualifiesforexam_status USING btree (user_id);


--
-- Name: devilry_student_uploadeddeliveryfile_13a4f9cc; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_student_uploadeddeliveryfile_13a4f9cc ON devilry_student_uploadeddeliveryfile USING btree (deadline_id);


--
-- Name: devilry_student_uploadeddeliveryfile_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX devilry_student_uploadeddeliveryfile_e8701ad4 ON devilry_student_uploadeddeliveryfile USING btree (user_id);


--
-- Name: django_admin_log_417f1b1c; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX django_admin_log_417f1b1c ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX django_admin_log_e8701ad4 ON django_admin_log USING btree (user_id);


--
-- Name: django_session_de54fa62; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX django_session_de54fa62 ON django_session USING btree (expire_date);


--
-- Name: django_session_session_key_461cfeaa630ca218_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX django_session_session_key_461cfeaa630ca218_like ON django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: django_site_domain_a2e37b91_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX django_site_domain_a2e37b91_like ON django_site USING btree (domain varchar_pattern_ops);


--
-- Name: ievv_batchframework_batchope_operationtype_86db17563402048_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX ievv_batchframework_batchope_operationtype_86db17563402048_like ON ievv_batchframework_batchoperation USING btree (operationtype varchar_pattern_ops);


--
-- Name: ievv_batchframework_batchoperation_62c990b1; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX ievv_batchframework_batchoperation_62c990b1 ON ievv_batchframework_batchoperation USING btree (started_by_id);


--
-- Name: ievv_batchframework_batchoperation_651b6541; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX ievv_batchframework_batchoperation_651b6541 ON ievv_batchframework_batchoperation USING btree (context_content_type_id);


--
-- Name: ievv_batchframework_batchoperation_e9e6a554; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX ievv_batchframework_batchoperation_e9e6a554 ON ievv_batchframework_batchoperation USING btree (operationtype);


--
-- Name: ievv_developemail_developemail_from_email_981952b3; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX ievv_developemail_developemail_from_email_981952b3 ON ievv_developemail_developemail USING btree (from_email);


--
-- Name: ievv_developemail_developemail_from_email_981952b3_like; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX ievv_developemail_developemail_from_email_981952b3_like ON ievv_developemail_developemail USING btree (from_email text_pattern_ops);


--
-- Name: socialaccount_socialaccount_e8701ad4; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX socialaccount_socialaccount_e8701ad4 ON socialaccount_socialaccount USING btree (user_id);


--
-- Name: socialaccount_socialapp_sites_9365d6e7; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX socialaccount_socialapp_sites_9365d6e7 ON socialaccount_socialapp_sites USING btree (site_id);


--
-- Name: socialaccount_socialapp_sites_fe95b0a0; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX socialaccount_socialapp_sites_fe95b0a0 ON socialaccount_socialapp_sites USING btree (socialapp_id);


--
-- Name: socialaccount_socialtoken_8a089c2a; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX socialaccount_socialtoken_8a089c2a ON socialaccount_socialtoken USING btree (account_id);


--
-- Name: socialaccount_socialtoken_f382adfe; Type: INDEX; Schema: public; Owner: dbdev
--

CREATE INDEX socialaccount_socialtoken_f382adfe ON socialaccount_socialtoken USING btree (app_id);


--
-- Name: core_assignment devilry__assignment_first_deadline_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__assignment_first_deadline_update_trigger AFTER UPDATE ON core_assignment FOR EACH ROW EXECUTE PROCEDURE devilry__assignment_first_deadline_update();


--
-- Name: core_candidate devilry__on_candidate_after_delete; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_candidate_after_delete AFTER DELETE ON core_candidate FOR EACH ROW EXECUTE PROCEDURE devilry__on_candidate_after_delete();


--
-- Name: core_candidate devilry__on_candidate_after_insert_or_update; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_candidate_after_insert_or_update AFTER INSERT OR UPDATE ON core_candidate FOR EACH ROW EXECUTE PROCEDURE devilry__on_candidate_after_insert_or_update();


--
-- Name: core_candidate devilry__on_candidate_delete_add_history_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_candidate_delete_add_history_trigger AFTER DELETE ON core_candidate FOR EACH ROW EXECUTE PROCEDURE devilry__on_candidate_delete_add_history();


--
-- Name: core_candidate devilry__on_candidate_insert_add_history_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_candidate_insert_add_history_trigger AFTER INSERT ON core_candidate FOR EACH ROW EXECUTE PROCEDURE devilry__on_candidate_insert_add_history();


--
-- Name: core_candidate devilry__on_candidate_update_add_history_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_candidate_update_add_history_trigger AFTER UPDATE ON core_candidate FOR EACH ROW EXECUTE PROCEDURE devilry__on_candidate_update_add_history();


--
-- Name: devilry_comment_comment devilry__on_comment_text_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_comment_text_update_trigger AFTER UPDATE ON devilry_comment_comment FOR EACH ROW EXECUTE PROCEDURE devilry__on_comment_text_update();


--
-- Name: devilry_comment_commentfile devilry__on_commentfile_after_delete; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_commentfile_after_delete AFTER DELETE ON devilry_comment_commentfile FOR EACH ROW EXECUTE PROCEDURE devilry__on_commentfile_after_delete();


--
-- Name: devilry_comment_commentfile devilry__on_commentfile_after_insert_or_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_commentfile_after_insert_or_update_trigger AFTER INSERT OR UPDATE ON devilry_comment_commentfile FOR EACH ROW EXECUTE PROCEDURE devilry__on_commentfile_after_insert_or_update();


--
-- Name: core_assignmentgroup_examiners devilry__on_examiner_after_delete; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_examiner_after_delete AFTER DELETE ON core_assignmentgroup_examiners FOR EACH ROW EXECUTE PROCEDURE devilry__on_examiner_after_delete();


--
-- Name: core_assignmentgroup_examiners devilry__on_examiner_after_insert_or_update; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_examiner_after_insert_or_update AFTER INSERT OR UPDATE ON core_assignmentgroup_examiners FOR EACH ROW EXECUTE PROCEDURE devilry__on_examiner_after_insert_or_update();


--
-- Name: core_assignmentgroup_examiners devilry__on_examiner_delete_add_history_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_examiner_delete_add_history_trigger AFTER DELETE ON core_assignmentgroup_examiners FOR EACH ROW EXECUTE PROCEDURE devilry__on_examiner_delete_add_history();


--
-- Name: core_assignmentgroup_examiners devilry__on_examiner_insert_add_history_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_examiner_insert_add_history_trigger AFTER INSERT ON core_assignmentgroup_examiners FOR EACH ROW EXECUTE PROCEDURE devilry__on_examiner_insert_add_history();


--
-- Name: core_assignmentgroup_examiners devilry__on_examiner_update_add_history_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_examiner_update_add_history_trigger AFTER UPDATE ON core_assignmentgroup_examiners FOR EACH ROW EXECUTE PROCEDURE devilry__on_examiner_update_add_history();


--
-- Name: devilry_group_feedbackset devilry__on_feedbackset_after_delete; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_feedbackset_after_delete AFTER DELETE ON devilry_group_feedbackset FOR EACH ROW EXECUTE PROCEDURE devilry__on_feedbackset_after_delete();


--
-- Name: devilry_group_feedbackset devilry__on_feedbackset_after_insert_or_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_feedbackset_after_insert_or_update_trigger AFTER INSERT OR UPDATE ON devilry_group_feedbackset FOR EACH ROW EXECUTE PROCEDURE devilry__on_feedbackset_after_insert_or_update();


--
-- Name: devilry_group_feedbackset devilry__on_feedbackset_before_insert_or_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_feedbackset_before_insert_or_update_trigger BEFORE INSERT OR UPDATE ON devilry_group_feedbackset FOR EACH ROW EXECUTE PROCEDURE devilry__on_feedbackset_before_insert_or_update();


--
-- Name: devilry_group_feedbackset devilry__on_feedbackset_deadline_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_feedbackset_deadline_update_trigger AFTER UPDATE ON devilry_group_feedbackset FOR EACH ROW EXECUTE PROCEDURE devilry__on_feedbackset_deadline_update();


--
-- Name: devilry_group_feedbackset devilry__on_feedbackset_grading_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_feedbackset_grading_update_trigger AFTER UPDATE ON devilry_group_feedbackset FOR EACH ROW EXECUTE PROCEDURE devilry__on_feedbackset_grading_update();


--
-- Name: devilry_group_groupcomment devilry__on_group_comment_text_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_group_comment_text_update_trigger AFTER UPDATE ON devilry_group_groupcomment FOR EACH ROW EXECUTE PROCEDURE devilry__on_group_comment_text_update();


--
-- Name: devilry_group_groupcomment devilry__on_groupcomment_after_delete; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_groupcomment_after_delete AFTER DELETE ON devilry_group_groupcomment FOR EACH ROW EXECUTE PROCEDURE devilry__on_groupcomment_after_delete();


--
-- Name: devilry_group_groupcomment devilry__on_groupcomment_after_insert_or_update_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_groupcomment_after_insert_or_update_trigger AFTER INSERT OR UPDATE ON devilry_group_groupcomment FOR EACH ROW EXECUTE PROCEDURE devilry__on_groupcomment_after_insert_or_update();


--
-- Name: devilry_group_imageannotationcomment devilry__on_imageannotationcomment_after_delete; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_imageannotationcomment_after_delete AFTER DELETE ON devilry_group_imageannotationcomment FOR EACH ROW EXECUTE PROCEDURE devilry__on_imageannotationcomment_after_delete();


--
-- Name: devilry_group_imageannotationcomment devilry__on_imageannotationcomment_after_insert_or_update_trigg; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry__on_imageannotationcomment_after_insert_or_update_trigg AFTER INSERT OR UPDATE ON devilry_group_imageannotationcomment FOR EACH ROW EXECUTE PROCEDURE devilry__on_imageannotationcomment_after_insert_or_update();


--
-- Name: core_assignmentgroup devilry_dbcache_on_assignmentgroup_insert_trigger; Type: TRIGGER; Schema: public; Owner: dbdev
--

CREATE TRIGGER devilry_dbcache_on_assignmentgroup_insert_trigger AFTER INSERT ON core_assignmentgroup FOR EACH ROW EXECUTE PROCEDURE devilry_dbcache_on_assignmentgroup_insert();


--
-- Name: devilry_account_permissiongroupuser D181b2ae85af4a8c369c2bd09f842f6f; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroupuser
    ADD CONSTRAINT "D181b2ae85af4a8c369c2bd09f842f6f" FOREIGN KEY (permissiongroup_id) REFERENCES devilry_account_permissiongroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgrouptag D219dbbaa875f1077d0f63778d98858a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouptag
    ADD CONSTRAINT "D219dbbaa875f1077d0f63778d98858a" FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgroup D3ec90dcce686786fa6cfc7940d91960; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT "D3ec90dcce686786fa6cfc7940d91960" FOREIGN KEY (batchoperation_id) REFERENCES ievv_batchframework_batchoperation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_imageannotationcomment D5e4a1a4b4d81269fe677b9b11bcf9dd; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_imageannotationcomment
    ADD CONSTRAINT "D5e4a1a4b4d81269fe677b9b11bcf9dd" FOREIGN KEY (feedback_set_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_candidate D5fa89d5f0632cab40e16a17b5422861; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT "D5fa89d5f0632cab40e16a17b5422861" FOREIGN KEY (old_reference_not_in_use_student_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account_periodpermissiongroup D732bd61cc9e1e86d0a2745a748ae7e9; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup
    ADD CONSTRAINT "D732bd61cc9e1e86d0a2745a748ae7e9" FOREIGN KEY (permissiongroup_id) REFERENCES devilry_account_permissiongroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_groupcomment D79d937271caab7986ef197c606f2644; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_groupcomment
    ADD CONSTRAINT "D79d937271caab7986ef197c606f2644" FOREIGN KEY (feedback_set_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_deadline D7eb2452376d1d7e0038f38d5151e20b; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_deadline
    ADD CONSTRAINT "D7eb2452376d1d7e0038f38d5151e20b" FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ievv_batchframework_batchoperation D8d96d0a9bf59345ab08863cddcf9249; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_batchframework_batchoperation
    ADD CONSTRAINT "D8d96d0a9bf59345ab08863cddcf9249" FOREIGN KEY (context_content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfile D8ec1ffb7a00b82f7d4d23443f299188; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfile
    ADD CONSTRAINT "D8ec1ffb7a00b82f7d4d23443f299188" FOREIGN KEY (collection_id) REFERENCES cradmin_temporaryfileuploadstore_temporaryfilecollection(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_candidate D933fe820df1d2bd50b8cf9434debe68; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT "D933fe820df1d2bd50b8cf9434debe68" FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account_subjectpermissiongroup a3e107e91b77c6db5a281e5a98c442ab; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup
    ADD CONSTRAINT a3e107e91b77c6db5a281e5a98c442ab FOREIGN KEY (permissiongroup_id) REFERENCES devilry_account_permissiongroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_dbcache_assignmentgroupcacheddata ac97fc0f77c7d2cb785f2d11c6af5dac; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_dbcache_assignmentgroupcacheddata
    ADD CONSTRAINT ac97fc0f77c7d2cb785f2d11c6af5dac FOREIGN KEY (last_published_feedbackset_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: account_emailconfirmation account_em_email_address_id_5b7f8c58_fk_account_emailaddress_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY account_emailconfirmation
    ADD CONSTRAINT account_em_email_address_id_5b7f8c58_fk_account_emailaddress_id FOREIGN KEY (email_address_id) REFERENCES account_emailaddress(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: account_emailaddress account_emailaddres_user_id_2c513194_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY account_emailaddress
    ADD CONSTRAINT account_emailaddres_user_id_2c513194_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgroup_examiners assignmentgroup_id_1a4ffb13b923185e_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT assignmentgroup_id_1a4ffb13b923185e_fk_core_assignmentgroup_id FOREIGN KEY (assignmentgroup_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_content_type_id_508cf46651277a81_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_content_type_id_508cf46651277a81_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissio_group_id_689710a9a73b7457_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_group_id_689710a9a73b7457_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_imageannotationcomment b192fa069cc9d03afa7e7517d7bed124; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_imageannotationcomment
    ADD CONSTRAINT b192fa069cc9d03afa7e7517d7bed124 FOREIGN KEY (image_id) REFERENCES devilry_comment_commentfileimage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam b863a82336ea177568feaa30e1e51c85; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam
    ADD CONSTRAINT b863a82336ea177568feaa30e1e51c85 FOREIGN KEY (status_id) REFERENCES devilry_qualifiesforexam_status(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_comment_commentfileimage c5ab7e1e9bde26caa038c76c78d6bc7c; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfileimage
    ADD CONSTRAINT c5ab7e1e9bde26caa038c76c78d6bc7c FOREIGN KEY (comment_file_id) REFERENCES devilry_comment_commentfile(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_relatedstudentkeyvalue co_relatedstudent_id_3e3e80d75676e0c9_fk_core_relatedstudent_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudentkeyvalue
    ADD CONSTRAINT co_relatedstudent_id_3e3e80d75676e0c9_fk_core_relatedstudent_id FOREIGN KEY (relatedstudent_id) REFERENCES core_relatedstudent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_candidate co_relatedstudent_id_7e66ddf8f3442b99_fk_core_relatedstudent_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidate
    ADD CONSTRAINT co_relatedstudent_id_7e66ddf8f3442b99_fk_core_relatedstudent_id FOREIGN KEY (relatedstudent_id) REFERENCES core_relatedstudent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_staticfeedbackfileattachment co_staticfeedback_id_4a6ee82466877520_fk_core_staticfeedback_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedbackfileattachment
    ADD CONSTRAINT co_staticfeedback_id_4a6ee82466877520_fk_core_staticfeedback_id FOREIGN KEY (staticfeedback_id) REFERENCES core_staticfeedback(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_delivery cor_last_feedback_id_15c1864499fa3298_fk_core_staticfeedback_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT cor_last_feedback_id_15c1864499fa3298_fk_core_staticfeedback_id FOREIGN KEY (last_feedback_id) REFERENCES core_staticfeedback(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgrouphistory core_as_assignment_group_id_1a5bc40e_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgrouphistory
    ADD CONSTRAINT core_as_assignment_group_id_1a5bc40e_fk_core_assignmentgroup_id FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgroup core_ass_feedback_id_4f3eb4317ce05ffd_fk_core_staticfeedback_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_ass_feedback_id_4f3eb4317ce05ffd_fk_core_staticfeedback_id FOREIGN KEY (feedback_id) REFERENCES core_staticfeedback(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignment_admins core_assig_assignment_id_712ee5b81efdf7d7_fk_core_assignment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment_admins
    ADD CONSTRAINT core_assig_assignment_id_712ee5b81efdf7d7_fk_core_assignment_id FOREIGN KEY (assignment_id) REFERENCES core_assignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgroup core_assig_last_deadline_id_946dfcf7910964c_fk_core_deadline_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assig_last_deadline_id_946dfcf7910964c_fk_core_deadline_id FOREIGN KEY (last_deadline_id) REFERENCES core_deadline(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgroup core_assig_parentnode_id_6e190fc057b9057c_fk_core_assignment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_assig_parentnode_id_6e190fc057b9057c_fk_core_assignment_id FOREIGN KEY (parentnode_id) REFERENCES core_assignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignment_admins core_assignm_user_id_51116d5a7e12d3b_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment_admins
    ADD CONSTRAINT core_assignm_user_id_51116d5a7e12d3b_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignment core_assignmen_parentnode_id_7072d3388816d25c_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignment
    ADD CONSTRAINT core_assignmen_parentnode_id_7072d3388816d25c_fk_core_period_id FOREIGN KEY (parentnode_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_candidateassignmentgrouphistory core_candidateassign_assignment_group_id_98c373a5_fk_core_assi; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidateassignmentgrouphistory
    ADD CONSTRAINT core_candidateassign_assignment_group_id_98c373a5_fk_core_assi FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_candidateassignmentgrouphistory core_candidateassign_user_id_7a3668f9_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_candidateassignmentgrouphistory
    ADD CONSTRAINT core_candidateassign_user_id_7a3668f9_fk_devilry_a FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgroup core_copied_from_id_21e068e4666502b2_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup
    ADD CONSTRAINT core_copied_from_id_21e068e4666502b2_fk_core_assignmentgroup_id FOREIGN KEY (copied_from_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_deadline core_de_added_by_id_5715a513f2acd9ff_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_deadline
    ADD CONSTRAINT core_de_added_by_id_5715a513f2acd9ff_fk_devilry_account_user_id FOREIGN KEY (added_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_delivery core_del_alias_delivery_id_58e23cdc9faaee16_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_del_alias_delivery_id_58e23cdc9faaee16_fk_core_delivery_id FOREIGN KEY (alias_delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_delivery core_deli_delivered_by_id_47605050cd8092f1_fk_core_candidate_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_deli_delivered_by_id_47605050cd8092f1_fk_core_candidate_id FOREIGN KEY (delivered_by_id) REFERENCES core_candidate(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_delivery core_delivery_copy_of_id_4bdefcd646b758a3_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_delivery_copy_of_id_4bdefcd646b758a3_fk_core_delivery_id FOREIGN KEY (copy_of_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_delivery core_delivery_deadline_id_3af0ef5599495505_fk_core_deadline_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_delivery
    ADD CONSTRAINT core_delivery_deadline_id_3af0ef5599495505_fk_core_deadline_id FOREIGN KEY (deadline_id) REFERENCES core_deadline(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_devilryuserprofile core_devilr_user_id_71c4199c1d6418ff_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_devilryuserprofile
    ADD CONSTRAINT core_devilr_user_id_71c4199c1d6418ff_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_examinerassignmentgrouphistory core_examinerassignm_assignment_group_id_eb832a6e_fk_core_assi; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_examinerassignmentgrouphistory
    ADD CONSTRAINT core_examinerassignm_assignment_group_id_eb832a6e_fk_core_assi FOREIGN KEY (assignment_group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_examinerassignmentgrouphistory core_examinerassignm_user_id_1636fd1b_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_examinerassignmentgrouphistory
    ADD CONSTRAINT core_examinerassignm_user_id_1636fd1b_fk_devilry_a FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_filemeta core_filemeta_delivery_id_6601bb0f5e56d9fe_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_filemeta
    ADD CONSTRAINT core_filemeta_delivery_id_6601bb0f5e56d9fe_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_groupinvite core_gro_sent_by_id_1efa01196ad2f009_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite
    ADD CONSTRAINT core_gro_sent_by_id_1efa01196ad2f009_fk_devilry_account_user_id FOREIGN KEY (sent_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_groupinvite core_gro_sent_to_id_50bd8691e6283e67_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite
    ADD CONSTRAINT core_gro_sent_to_id_50bd8691e6283e67_fk_devilry_account_user_id FOREIGN KEY (sent_to_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_groupinvite core_groupi_group_id_3650f45b11bc854_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_groupinvite
    ADD CONSTRAINT core_groupi_group_id_3650f45b11bc854_fk_core_assignmentgroup_id FOREIGN KEY (group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_periodtag_relatedexaminers core_per_relatedexaminer_id_faa47fdc_fk_core_relatedexaminer_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedexaminers
    ADD CONSTRAINT core_per_relatedexaminer_id_faa47fdc_fk_core_relatedexaminer_id FOREIGN KEY (relatedexaminer_id) REFERENCES core_relatedexaminer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_periodtag_relatedstudents core_perio_relatedstudent_id_fceab87a_fk_core_relatedstudent_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedstudents
    ADD CONSTRAINT core_perio_relatedstudent_id_fceab87a_fk_core_relatedstudent_id FOREIGN KEY (relatedstudent_id) REFERENCES core_relatedstudent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_period_admins core_period__user_id_eb067c4bde098ff_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period_admins
    ADD CONSTRAINT core_period__user_id_eb067c4bde098ff_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_period_admins core_period_admins_period_id_11596bf319c91d8f_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period_admins
    ADD CONSTRAINT core_period_admins_period_id_11596bf319c91d8f_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_period core_period_parentnode_id_1844773fcb98c0b8_fk_core_subject_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_period
    ADD CONSTRAINT core_period_parentnode_id_1844773fcb98c0b8_fk_core_subject_id FOREIGN KEY (parentnode_id) REFERENCES core_subject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_periodapplicationkeyvalue core_periodapplica_period_id_71495bf20087514e_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodapplicationkeyvalue
    ADD CONSTRAINT core_periodapplica_period_id_71495bf20087514e_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_periodtag core_periodtag_period_id_d7a1e8c9_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag
    ADD CONSTRAINT core_periodtag_period_id_d7a1e8c9_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_periodtag_relatedstudents core_periodtag_relat_periodtag_id_0aacb973_fk_core_periodtag_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedstudents
    ADD CONSTRAINT core_periodtag_relat_periodtag_id_0aacb973_fk_core_periodtag_id FOREIGN KEY (periodtag_id) REFERENCES core_periodtag(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_periodtag_relatedexaminers core_periodtag_relat_periodtag_id_d532c009_fk_core_periodtag_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_periodtag_relatedexaminers
    ADD CONSTRAINT core_periodtag_relat_periodtag_id_d532c009_fk_core_periodtag_id FOREIGN KEY (periodtag_id) REFERENCES core_periodtag(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_pointtogrademap core_point_assignment_id_45add1f59eb1ca29_fk_core_assignment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointtogrademap
    ADD CONSTRAINT core_point_assignment_id_45add1f59eb1ca29_fk_core_assignment_id FOREIGN KEY (assignment_id) REFERENCES core_assignment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_relatedexaminer core_relate_user_id_644ee92d6b54d587_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminer
    ADD CONSTRAINT core_relate_user_id_644ee92d6b54d587_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_relatedstudent core_related_user_id_66588181cfc595a_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudent
    ADD CONSTRAINT core_related_user_id_66588181cfc595a_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_relatedexaminer core_relatedexamin_period_id_1608ffa9420f3529_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedexaminer
    ADD CONSTRAINT core_relatedexamin_period_id_1608ffa9420f3529_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_relatedstudent core_relatedstuden_period_id_518a11c836f19f36_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_relatedstudent
    ADD CONSTRAINT core_relatedstuden_period_id_518a11c836f19f36_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_staticfeedback core_st_saved_by_id_5c9526c62cf55415_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedback
    ADD CONSTRAINT core_st_saved_by_id_5c9526c62cf55415_fk_devilry_account_user_id FOREIGN KEY (saved_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_staticfeedback core_staticfee_delivery_id_76cd203e463381c6_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_staticfeedback
    ADD CONSTRAINT core_staticfee_delivery_id_76cd203e463381c6_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_subject_admins core_subjec_user_id_757b64082c3dd225_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject_admins
    ADD CONSTRAINT core_subjec_user_id_757b64082c3dd225_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_subject_admins core_subject_admi_subject_id_30074ec6a2ab50f_fk_core_subject_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_subject_admins
    ADD CONSTRAINT core_subject_admi_subject_id_30074ec6a2ab50f_fk_core_subject_id FOREIGN KEY (subject_id) REFERENCES core_subject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cradmin_generic_token_with_metadata_generictokenwithmetadata crad_content_type_id_51aea07aab3596f7_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_generic_token_with_metadata_generictokenwithmetadata
    ADD CONSTRAINT crad_content_type_id_51aea07aab3596f7_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cradmin_temporaryfileuploadstore_temporaryfilecollection cradmin_tem_user_id_2dc5e0653dd71e89_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY cradmin_temporaryfileuploadstore_temporaryfilecollection
    ADD CONSTRAINT cradmin_tem_user_id_2dc5e0653dd71e89_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_pointrangetograde d0e0aa08edad3ed1e6bdf96c03308582; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_pointrangetograde
    ADD CONSTRAINT d0e0aa08edad3ed1e6bdf96c03308582 FOREIGN KEY (point_to_grade_map_id) REFERENCES core_pointtogrademap(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_imageannotationcomment d_comment_ptr_id_1afa15ad1c07737e_fk_devilry_comment_comment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_imageannotationcomment
    ADD CONSTRAINT d_comment_ptr_id_1afa15ad1c07737e_fk_devilry_comment_comment_id FOREIGN KEY (comment_ptr_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_groupcomment d_comment_ptr_id_77e73d4401d55a91_fk_devilry_comment_comment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_groupcomment
    ADD CONSTRAINT d_comment_ptr_id_77e73d4401d55a91_fk_devilry_comment_comment_id FOREIGN KEY (comment_ptr_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_dbcache_assignmentgroupcacheddata d_first_feedbackset_id_89c38dc7_fk_devilry_group_feedbackset_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_dbcache_assignmentgroupcacheddata
    ADD CONSTRAINT d_first_feedbackset_id_89c38dc7_fk_devilry_group_feedbackset_id FOREIGN KEY (first_feedbackset_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_dbcache_assignmentgroupcacheddata de_last_feedbackset_id_6961c179_fk_devilry_group_feedbackset_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_dbcache_assignmentgroupcacheddata
    ADD CONSTRAINT de_last_feedbackset_id_6961c179_fk_devilry_group_feedbackset_id FOREIGN KEY (last_feedbackset_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qualifiesforexam_qualifiesforfinalexam de_relatedstudent_id_55ab211e0e76d3c5_fk_core_relatedstudent_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_qualifiesforfinalexam
    ADD CONSTRAINT de_relatedstudent_id_55ab211e0e76d3c5_fk_core_relatedstudent_id FOREIGN KEY (relatedstudent_id) REFERENCES core_relatedstudent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_gradingsystem_feedbackdraft de_staticfeedback_id_43feb18645a3f2a4_fk_core_staticfeedback_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT de_staticfeedback_id_43feb18645a3f2a4_fk_core_staticfeedback_id FOREIGN KEY (staticfeedback_id) REFERENCES core_staticfeedback(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbackset dev_grading_published_by_id_75176877_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT dev_grading_published_by_id_75176877_fk_devilry_account_user_id FOREIGN KEY (grading_published_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_comment_commentfile devil_comment_id_2e9f77d72415c03e_fk_devilry_comment_comment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentfile
    ADD CONSTRAINT devil_comment_id_2e9f77d72415c03e_fk_devilry_comment_comment_id FOREIGN KEY (comment_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbacksetdeadlinehistory devilr_feedback_set_id_52741ef3_fk_devilry_group_feedbackset_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetdeadlinehistory
    ADD CONSTRAINT devilr_feedback_set_id_52741ef3_fk_devilry_group_feedbackset_id FOREIGN KEY (feedback_set_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_comment_comment devilr_parent_id_5b1213dd5232a472_fk_devilry_comment_comment_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_comment
    ADD CONSTRAINT devilr_parent_id_5b1213dd5232a472_fk_devilry_comment_comment_id FOREIGN KEY (parent_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account_permissiongroupuser devilry_acc_user_id_1639a4cd40d74025_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_permissiongroupuser
    ADD CONSTRAINT devilry_acc_user_id_1639a4cd40d74025_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account_username devilry_acc_user_id_5199824be5bb3b9b_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_username
    ADD CONSTRAINT devilry_acc_user_id_5199824be5bb3b9b_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account_useremail devilry_acco_user_id_a38a81995988057_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_useremail
    ADD CONSTRAINT devilry_acco_user_id_a38a81995988057_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account_subjectpermissiongroup devilry_account__subject_id_305f1dc9fe3d5d33_fk_core_subject_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_subjectpermissiongroup
    ADD CONSTRAINT devilry_account__subject_id_305f1dc9fe3d5d33_fk_core_subject_id FOREIGN KEY (subject_id) REFERENCES core_subject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_account_periodpermissiongroup devilry_account_pe_period_id_2bc5882f60c3e215_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_account_periodpermissiongroup
    ADD CONSTRAINT devilry_account_pe_period_id_2bc5882f60c3e215_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_comment_comment devilry_comment_com_user_id_ddc7b6b0_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_comment
    ADD CONSTRAINT devilry_comment_com_user_id_ddc7b6b0_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_comment_commentedithistory devilry_comment_comm_comment_id_91baeb5a_fk_devilry_c; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentedithistory
    ADD CONSTRAINT devilry_comment_comm_comment_id_91baeb5a_fk_devilry_c FOREIGN KEY (comment_id) REFERENCES devilry_comment_comment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_comment_commentedithistory devilry_comment_comm_edited_by_id_2e51be6c_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_comment_commentedithistory
    ADD CONSTRAINT devilry_comment_comm_edited_by_id_2e51be6c_fk_devilry_a FOREIGN KEY (edited_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_compressionutil_compressedarchivemeta devilry_comp_content_type_id_dc562e1b_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_compressionutil_compressedarchivemeta
    ADD CONSTRAINT devilry_comp_content_type_id_dc562e1b_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_compressionutil_compressedarchivemeta devilry_compressionu_created_by_id_edfcbf68_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_compressionutil_compressedarchivemeta
    ADD CONSTRAINT devilry_compressionu_created_by_id_edfcbf68_fk_devilry_a FOREIGN KEY (created_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_dbcache_assignmentgroupcacheddata devilry_dbcache_as_group_id_cfe8ca20_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_dbcache_assignmentgroupcacheddata
    ADD CONSTRAINT devilry_dbcache_as_group_id_cfe8ca20_fk_core_assignmentgroup_id FOREIGN KEY (group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbackset devilry_gr_group_id_148fa5d5062a96f8_fk_core_assignmentgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devilry_gr_group_id_148fa5d5062a96f8_fk_core_assignmentgroup_id FOREIGN KEY (group_id) REFERENCES core_assignmentgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_gradingsystem_feedbackdraft devilry_gradin_delivery_id_31734762a96e190f_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT devilry_gradin_delivery_id_31734762a96e190f_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_gradingsystem_feedbackdraftfile devilry_gradin_delivery_id_65ac58b6a461891b_fk_core_delivery_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraftfile
    ADD CONSTRAINT devilry_gradin_delivery_id_65ac58b6a461891b_fk_core_delivery_id FOREIGN KEY (delivery_id) REFERENCES core_delivery(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbacksetdeadlinehistory devilry_group_changed_by_id_8dd1df9c_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetdeadlinehistory
    ADD CONSTRAINT devilry_group_changed_by_id_8dd1df9c_fk_devilry_account_user_id FOREIGN KEY (changed_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbackset devilry_group_created_by_id_650ceed9_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devilry_group_created_by_id_650ceed9_fk_devilry_account_user_id FOREIGN KEY (created_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod devilry_group_feedba_created_by_id_b8572995_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetpassedpreviousperiod
    ADD CONSTRAINT devilry_group_feedba_created_by_id_b8572995_fk_devilry_a FOREIGN KEY (created_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbacksetgradingupdatehistory devilry_group_feedba_feedback_set_id_24f4c349_fk_devilry_g; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetgradingupdatehistory
    ADD CONSTRAINT devilry_group_feedba_feedback_set_id_24f4c349_fk_devilry_g FOREIGN KEY (feedback_set_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod devilry_group_feedba_feedbackset_id_2c6e12d3_fk_devilry_g; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetpassedpreviousperiod
    ADD CONSTRAINT devilry_group_feedba_feedbackset_id_2c6e12d3_fk_devilry_g FOREIGN KEY (feedbackset_id) REFERENCES devilry_group_feedbackset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbacksetpassedpreviousperiod devilry_group_feedba_grading_published_by_4090bbe2_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetpassedpreviousperiod
    ADD CONSTRAINT devilry_group_feedba_grading_published_by_4090bbe2_fk_devilry_a FOREIGN KEY (grading_published_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbackset devilry_group_feedba_last_updated_by_id_960089c6_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbackset
    ADD CONSTRAINT devilry_group_feedba_last_updated_by_id_960089c6_fk_devilry_a FOREIGN KEY (last_updated_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbacksetgradingupdatehistory devilry_group_feedba_old_grading_publishe_f855818b_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetgradingupdatehistory
    ADD CONSTRAINT devilry_group_feedba_old_grading_publishe_f855818b_fk_devilry_a FOREIGN KEY (old_grading_published_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_feedbacksetgradingupdatehistory devilry_group_feedba_updated_by_id_5aa2ab0f_fk_devilry_a; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_feedbacksetgradingupdatehistory
    ADD CONSTRAINT devilry_group_feedba_updated_by_id_5aa2ab0f_fk_devilry_a FOREIGN KEY (updated_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_groupcommentedithistory devilry_group_groupc_commentedithistory_p_6eca5a90_fk_devilry_c; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_groupcommentedithistory
    ADD CONSTRAINT devilry_group_groupc_commentedithistory_p_6eca5a90_fk_devilry_c FOREIGN KEY (commentedithistory_ptr_id) REFERENCES devilry_comment_commentedithistory(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_group_groupcommentedithistory devilry_group_groupc_group_comment_id_123b9b0d_fk_devilry_g; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_group_groupcommentedithistory
    ADD CONSTRAINT devilry_group_groupc_group_comment_id_123b9b0d_fk_devilry_g FOREIGN KEY (group_comment_id) REFERENCES devilry_group_groupcomment(comment_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_import_v2database_importedmodel devilry_impo_content_type_id_28663f30_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_import_v2database_importedmodel
    ADD CONSTRAINT devilry_impo_content_type_id_28663f30_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qualifiesforexam_status devilry_qua_user_id_522959bf05072244_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_status
    ADD CONSTRAINT devilry_qua_user_id_522959bf05072244_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qualifiesforexam_periodtag devilry_qualifiesf_period_id_102beba2d8031066_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_periodtag
    ADD CONSTRAINT devilry_qualifiesf_period_id_102beba2d8031066_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qualifiesforexam_status devilry_qualifiesf_period_id_6a80472573c78154_fk_core_period_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_status
    ADD CONSTRAINT devilry_qualifiesf_period_id_6a80472573c78154_fk_core_period_id FOREIGN KEY (period_id) REFERENCES core_period(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_gradingsystem_feedbackdraftfile devilry_saved_by_id_22ca281ac57fddb4_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraftfile
    ADD CONSTRAINT devilry_saved_by_id_22ca281ac57fddb4_fk_devilry_account_user_id FOREIGN KEY (saved_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_gradingsystem_feedbackdraft devilry_saved_by_id_2688417740fdf346_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_gradingsystem_feedbackdraft
    ADD CONSTRAINT devilry_saved_by_id_2688417740fdf346_fk_devilry_account_user_id FOREIGN KEY (saved_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_student_uploadeddeliveryfile devilry_stu_user_id_594ee6dafdf52417_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile
    ADD CONSTRAINT devilry_stu_user_id_594ee6dafdf52417_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_student_uploadeddeliveryfile devilry_studen_deadline_id_73bb1a77ed86db5c_fk_core_deadline_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_student_uploadeddeliveryfile
    ADD CONSTRAINT devilry_studen_deadline_id_73bb1a77ed86db5c_fk_core_deadline_id FOREIGN KEY (deadline_id) REFERENCES core_deadline(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log djan_content_type_id_697914295151027a_fk_django_content_type_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT djan_content_type_id_697914295151027a_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admi_user_id_52fdd58701c5f563_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admi_user_id_52fdd58701c5f563_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgroup_examiners e2e901148f6cd8765ee8ce180b39118d; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT e2e901148f6cd8765ee8ce180b39118d FOREIGN KEY (old_reference_not_in_use_user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: devilry_qualifiesforexam_periodtag f2a2267fbb3f8424a3f20a79ed9ed35d; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY devilry_qualifiesforexam_periodtag
    ADD CONSTRAINT f2a2267fbb3f8424a3f20a79ed9ed35d FOREIGN KEY (deadlinetag_id) REFERENCES devilry_qualifiesforexam_deadlinetag(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ievv_batchframework_batchoperation ievv__started_by_id_453323e9bb289a44_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY ievv_batchframework_batchoperation
    ADD CONSTRAINT ievv__started_by_id_453323e9bb289a44_fk_devilry_account_user_id FOREIGN KEY (started_by_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_assignmentgroup_examiners relatedexaminer_id_46b4afef8d47d182_fk_core_relatedexaminer_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY core_assignmentgroup_examiners
    ADD CONSTRAINT relatedexaminer_id_46b4afef8d47d182_fk_core_relatedexaminer_id FOREIGN KEY (relatedexaminer_id) REFERENCES core_relatedexaminer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccount_socialtoken socialacc_account_id_951f210e_fk_socialaccount_socialaccount_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialtoken
    ADD CONSTRAINT socialacc_account_id_951f210e_fk_socialaccount_socialaccount_id FOREIGN KEY (account_id) REFERENCES socialaccount_socialaccount(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccount_socialapp_sites socialaccou_socialapp_id_97fb6e7d_fk_socialaccount_socialapp_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccou_socialapp_id_97fb6e7d_fk_socialaccount_socialapp_id FOREIGN KEY (socialapp_id) REFERENCES socialaccount_socialapp(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccount_socialtoken socialaccount_soc_app_id_636a42d7_fk_socialaccount_socialapp_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialtoken
    ADD CONSTRAINT socialaccount_soc_app_id_636a42d7_fk_socialaccount_socialapp_id FOREIGN KEY (app_id) REFERENCES socialaccount_socialapp(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccount_socialaccount socialaccount_socia_user_id_8146e70c_fk_devilry_account_user_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialaccount
    ADD CONSTRAINT socialaccount_socia_user_id_8146e70c_fk_devilry_account_user_id FOREIGN KEY (user_id) REFERENCES devilry_account_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: socialaccount_socialapp_sites socialaccount_socialapp_site_site_id_2579dee5_fk_django_site_id; Type: FK CONSTRAINT; Schema: public; Owner: dbdev
--

ALTER TABLE ONLY socialaccount_socialapp_sites
    ADD CONSTRAINT socialaccount_socialapp_site_site_id_2579dee5_fk_django_site_id FOREIGN KEY (site_id) REFERENCES django_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

