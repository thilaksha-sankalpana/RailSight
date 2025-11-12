--
-- PostgreSQL database dump
--

\restrict fpzpQfyiHIq7uwp6H6eiWIqX8bXfaTIvfblISk3YvWpvR99pRroYcsQsUd3bGcq

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

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
-- Name: auth; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA auth;


--
-- Name: extensions; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA extensions;


--
-- Name: graphql; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA graphql;


--
-- Name: graphql_public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA graphql_public;


--
-- Name: pgbouncer; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA pgbouncer;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'Removed daily_schedules - replaced by schedule_capacity and segment_capacity';


--
-- Name: realtime; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA realtime;


--
-- Name: storage; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA storage;


--
-- Name: vault; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA vault;


--
-- Name: pg_graphql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_graphql WITH SCHEMA graphql;


--
-- Name: EXTENSION pg_graphql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_graphql IS 'pg_graphql: GraphQL support';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA extensions;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: supabase_vault; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS supabase_vault WITH SCHEMA vault;


--
-- Name: EXTENSION supabase_vault; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION supabase_vault IS 'Supabase Vault Extension';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA extensions;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: aal_level; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.aal_level AS ENUM (
    'aal1',
    'aal2',
    'aal3'
);


--
-- Name: code_challenge_method; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.code_challenge_method AS ENUM (
    's256',
    'plain'
);


--
-- Name: factor_status; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.factor_status AS ENUM (
    'unverified',
    'verified'
);


--
-- Name: factor_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.factor_type AS ENUM (
    'totp',
    'webauthn',
    'phone'
);


--
-- Name: oauth_authorization_status; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.oauth_authorization_status AS ENUM (
    'pending',
    'approved',
    'denied',
    'expired'
);


--
-- Name: oauth_client_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.oauth_client_type AS ENUM (
    'public',
    'confidential'
);


--
-- Name: oauth_registration_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.oauth_registration_type AS ENUM (
    'dynamic',
    'manual'
);


--
-- Name: oauth_response_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.oauth_response_type AS ENUM (
    'code'
);


--
-- Name: one_time_token_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.one_time_token_type AS ENUM (
    'confirmation_token',
    'reauthentication_token',
    'recovery_token',
    'email_change_token_new',
    'email_change_token_current',
    'phone_change_token'
);


--
-- Name: allocationstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.allocationstatus AS ENUM (
    'Provisional',
    'Confirmed',
    'Completed',
    'Cancelled'
);


--
-- Name: booking_platform; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.booking_platform AS ENUM (
    'Website',
    'Mobile App',
    'Counter',
    'Kiosk'
);


--
-- Name: bookingplatform; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.bookingplatform AS ENUM (
    'Web',
    'MobileApp',
    'Counter',
    'Kiosk'
);


--
-- Name: payment_method; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.payment_method AS ENUM (
    'Cash',
    'Card',
    'Online Banking',
    'Mobile Payment'
);


--
-- Name: payment_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.payment_status AS ENUM (
    'Paid',
    'Pending',
    'Refunded',
    'Failed',
    'Chargedbacked'
);


--
-- Name: paymentmethod; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.paymentmethod AS ENUM (
    'Cash',
    'Card',
    'OnlineBanking',
    'MobilePayment'
);


--
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.paymentstatus AS ENUM (
    'Paid',
    'Pending',
    'Refunded',
    'Failed',
    'Chargeback'
);


--
-- Name: schedule_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.schedule_status AS ENUM (
    'Active',
    'Inactive',
    'Cancelled',
    'Delayed'
);


--
-- Name: schedulestatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.schedulestatus AS ENUM (
    'Active',
    'Inactive',
    'Cancelled',
    'Delayed'
);


--
-- Name: seattype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.seattype AS ENUM (
    'Window',
    'Aisle',
    'Any',
    'Unreserved'
);


--
-- Name: ticket_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.ticket_status AS ENUM (
    'Completed',
    'Cancelled',
    'Refunded',
    'No-Show',
    'Pending'
);


--
-- Name: ticketstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.ticketstatus AS ENUM (
    'Pending',
    'Confirmed',
    'Completed',
    'Cancelled',
    'Refunded',
    'NoShow'
);


--
-- Name: train_class; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.train_class AS ENUM (
    'First',
    'Second',
    'Third'
);


--
-- Name: train_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.train_status AS ENUM (
    'Active',
    'Inactive',
    'Maintenance',
    'Retired'
);


--
-- Name: trainclass; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.trainclass AS ENUM (
    'first',
    'second',
    'third'
);


--
-- Name: trainstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.trainstatus AS ENUM (
    'Active',
    'Inactive',
    'Maintenance',
    'Retired'
);


--
-- Name: user_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.user_role AS ENUM (
    'admin',
    'operator',
    'ticket_agent',
    'manager'
);


--
-- Name: userrole; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.userrole AS ENUM (
    'admin',
    'operator',
    'ticket_agent',
    'manager'
);


--
-- Name: action; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.action AS ENUM (
    'INSERT',
    'UPDATE',
    'DELETE',
    'TRUNCATE',
    'ERROR'
);


--
-- Name: equality_op; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.equality_op AS ENUM (
    'eq',
    'neq',
    'lt',
    'lte',
    'gt',
    'gte',
    'in'
);


--
-- Name: user_defined_filter; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.user_defined_filter AS (
	column_name text,
	op realtime.equality_op,
	value text
);


--
-- Name: wal_column; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.wal_column AS (
	name text,
	type_name text,
	type_oid oid,
	value jsonb,
	is_pkey boolean,
	is_selectable boolean
);


--
-- Name: wal_rls; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.wal_rls AS (
	wal jsonb,
	is_rls_enabled boolean,
	subscription_ids uuid[],
	errors text[]
);


--
-- Name: buckettype; Type: TYPE; Schema: storage; Owner: -
--

CREATE TYPE storage.buckettype AS ENUM (
    'STANDARD',
    'ANALYTICS'
);


--
-- Name: email(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION auth.email() RETURNS text
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.email', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'email')
  )::text
$$;


--
-- Name: FUNCTION email(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION auth.email() IS 'Deprecated. Use auth.jwt() -> ''email'' instead.';


--
-- Name: jwt(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION auth.jwt() RETURNS jsonb
    LANGUAGE sql STABLE
    AS $$
  select 
    coalesce(
        nullif(current_setting('request.jwt.claim', true), ''),
        nullif(current_setting('request.jwt.claims', true), '')
    )::jsonb
$$;


--
-- Name: role(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION auth.role() RETURNS text
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.role', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role')
  )::text
$$;


--
-- Name: FUNCTION role(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION auth.role() IS 'Deprecated. Use auth.jwt() -> ''role'' instead.';


--
-- Name: uid(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION auth.uid() RETURNS uuid
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.sub', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')
  )::uuid
$$;


--
-- Name: FUNCTION uid(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION auth.uid() IS 'Deprecated. Use auth.jwt() -> ''sub'' instead.';


--
-- Name: grant_pg_cron_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.grant_pg_cron_access() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  IF EXISTS (
    SELECT
    FROM pg_event_trigger_ddl_commands() AS ev
    JOIN pg_extension AS ext
    ON ev.objid = ext.oid
    WHERE ext.extname = 'pg_cron'
  )
  THEN
    grant usage on schema cron to postgres with grant option;

    alter default privileges in schema cron grant all on tables to postgres with grant option;
    alter default privileges in schema cron grant all on functions to postgres with grant option;
    alter default privileges in schema cron grant all on sequences to postgres with grant option;

    alter default privileges for user supabase_admin in schema cron grant all
        on sequences to postgres with grant option;
    alter default privileges for user supabase_admin in schema cron grant all
        on tables to postgres with grant option;
    alter default privileges for user supabase_admin in schema cron grant all
        on functions to postgres with grant option;

    grant all privileges on all tables in schema cron to postgres with grant option;
    revoke all on table cron.job from postgres;
    grant select on table cron.job to postgres with grant option;
  END IF;
END;
$$;


--
-- Name: FUNCTION grant_pg_cron_access(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION extensions.grant_pg_cron_access() IS 'Grants access to pg_cron';


--
-- Name: grant_pg_graphql_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.grant_pg_graphql_access() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $_$
DECLARE
    func_is_graphql_resolve bool;
BEGIN
    func_is_graphql_resolve = (
        SELECT n.proname = 'resolve'
        FROM pg_event_trigger_ddl_commands() AS ev
        LEFT JOIN pg_catalog.pg_proc AS n
        ON ev.objid = n.oid
    );

    IF func_is_graphql_resolve
    THEN
        -- Update public wrapper to pass all arguments through to the pg_graphql resolve func
        DROP FUNCTION IF EXISTS graphql_public.graphql;
        create or replace function graphql_public.graphql(
            "operationName" text default null,
            query text default null,
            variables jsonb default null,
            extensions jsonb default null
        )
            returns jsonb
            language sql
        as $$
            select graphql.resolve(
                query := query,
                variables := coalesce(variables, '{}'),
                "operationName" := "operationName",
                extensions := extensions
            );
        $$;

        -- This hook executes when `graphql.resolve` is created. That is not necessarily the last
        -- function in the extension so we need to grant permissions on existing entities AND
        -- update default permissions to any others that are created after `graphql.resolve`
        grant usage on schema graphql to postgres, anon, authenticated, service_role;
        grant select on all tables in schema graphql to postgres, anon, authenticated, service_role;
        grant execute on all functions in schema graphql to postgres, anon, authenticated, service_role;
        grant all on all sequences in schema graphql to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on tables to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on functions to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on sequences to postgres, anon, authenticated, service_role;

        -- Allow postgres role to allow granting usage on graphql and graphql_public schemas to custom roles
        grant usage on schema graphql_public to postgres with grant option;
        grant usage on schema graphql to postgres with grant option;
    END IF;

END;
$_$;


--
-- Name: FUNCTION grant_pg_graphql_access(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION extensions.grant_pg_graphql_access() IS 'Grants access to pg_graphql';


--
-- Name: grant_pg_net_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.grant_pg_net_access() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_event_trigger_ddl_commands() AS ev
    JOIN pg_extension AS ext
    ON ev.objid = ext.oid
    WHERE ext.extname = 'pg_net'
  )
  THEN
    IF NOT EXISTS (
      SELECT 1
      FROM pg_roles
      WHERE rolname = 'supabase_functions_admin'
    )
    THEN
      CREATE USER supabase_functions_admin NOINHERIT CREATEROLE LOGIN NOREPLICATION;
    END IF;

    GRANT USAGE ON SCHEMA net TO supabase_functions_admin, postgres, anon, authenticated, service_role;

    IF EXISTS (
      SELECT FROM pg_extension
      WHERE extname = 'pg_net'
      -- all versions in use on existing projects as of 2025-02-20
      -- version 0.12.0 onwards don't need these applied
      AND extversion IN ('0.2', '0.6', '0.7', '0.7.1', '0.8', '0.10.0', '0.11.0')
    ) THEN
      ALTER function net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;
      ALTER function net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;

      ALTER function net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;
      ALTER function net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;

      REVOKE ALL ON FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) FROM PUBLIC;
      REVOKE ALL ON FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) FROM PUBLIC;

      GRANT EXECUTE ON FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) TO supabase_functions_admin, postgres, anon, authenticated, service_role;
      GRANT EXECUTE ON FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) TO supabase_functions_admin, postgres, anon, authenticated, service_role;
    END IF;
  END IF;
END;
$$;


--
-- Name: FUNCTION grant_pg_net_access(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION extensions.grant_pg_net_access() IS 'Grants access to pg_net';


--
-- Name: pgrst_ddl_watch(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.pgrst_ddl_watch() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN SELECT * FROM pg_event_trigger_ddl_commands()
  LOOP
    IF cmd.command_tag IN (
      'CREATE SCHEMA', 'ALTER SCHEMA'
    , 'CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO', 'ALTER TABLE'
    , 'CREATE FOREIGN TABLE', 'ALTER FOREIGN TABLE'
    , 'CREATE VIEW', 'ALTER VIEW'
    , 'CREATE MATERIALIZED VIEW', 'ALTER MATERIALIZED VIEW'
    , 'CREATE FUNCTION', 'ALTER FUNCTION'
    , 'CREATE TRIGGER'
    , 'CREATE TYPE', 'ALTER TYPE'
    , 'CREATE RULE'
    , 'COMMENT'
    )
    -- don't notify in case of CREATE TEMP table or other objects created on pg_temp
    AND cmd.schema_name is distinct from 'pg_temp'
    THEN
      NOTIFY pgrst, 'reload schema';
    END IF;
  END LOOP;
END; $$;


--
-- Name: pgrst_drop_watch(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.pgrst_drop_watch() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  obj record;
BEGIN
  FOR obj IN SELECT * FROM pg_event_trigger_dropped_objects()
  LOOP
    IF obj.object_type IN (
      'schema'
    , 'table'
    , 'foreign table'
    , 'view'
    , 'materialized view'
    , 'function'
    , 'trigger'
    , 'type'
    , 'rule'
    )
    AND obj.is_temporary IS false -- no pg_temp objects
    THEN
      NOTIFY pgrst, 'reload schema';
    END IF;
  END LOOP;
END; $$;


--
-- Name: set_graphql_placeholder(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.set_graphql_placeholder() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $_$
    DECLARE
    graphql_is_dropped bool;
    BEGIN
    graphql_is_dropped = (
        SELECT ev.schema_name = 'graphql_public'
        FROM pg_event_trigger_dropped_objects() AS ev
        WHERE ev.schema_name = 'graphql_public'
    );

    IF graphql_is_dropped
    THEN
        create or replace function graphql_public.graphql(
            "operationName" text default null,
            query text default null,
            variables jsonb default null,
            extensions jsonb default null
        )
            returns jsonb
            language plpgsql
        as $$
            DECLARE
                server_version float;
            BEGIN
                server_version = (SELECT (SPLIT_PART((select version()), ' ', 2))::float);

                IF server_version >= 14 THEN
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql extension is not enabled.'
                            )
                        )
                    );
                ELSE
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql is only available on projects running Postgres 14 onwards.'
                            )
                        )
                    );
                END IF;
            END;
        $$;
    END IF;

    END;
$_$;


--
-- Name: FUNCTION set_graphql_placeholder(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION extensions.set_graphql_placeholder() IS 'Reintroduces placeholder function for graphql_public.graphql';


--
-- Name: get_auth(text); Type: FUNCTION; Schema: pgbouncer; Owner: -
--

CREATE FUNCTION pgbouncer.get_auth(p_usename text) RETURNS TABLE(username text, password text)
    LANGUAGE plpgsql SECURITY DEFINER
    AS $_$
begin
    raise debug 'PgBouncer auth request: %', p_usename;

    return query
    select 
        rolname::text, 
        case when rolvaliduntil < now() 
            then null 
            else rolpassword::text 
        end 
    from pg_authid 
    where rolname=$1 and rolcanlogin;
end;
$_$;


--
-- Name: schedule_operates_on_date(character varying, date); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.schedule_operates_on_date(p_schedule_id character varying, p_date date) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_schedule RECORD;
    v_day_name TEXT;
    v_is_poya BOOLEAN;
    v_is_holiday BOOLEAN;
BEGIN
    -- Get schedule record
    SELECT * INTO v_schedule
    FROM train_schedules
    WHERE train_schedule_id = p_schedule_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Get day of week (lowercase)
    v_day_name := LOWER(TO_CHAR(p_date, 'Day'));
    v_day_name := TRIM(v_day_name);

    -- Check if schedule operates on this day of week
    CASE v_day_name
        WHEN 'monday' THEN
            IF v_schedule.monday THEN RETURN TRUE; END IF;
        WHEN 'tuesday' THEN
            IF v_schedule.tuesday THEN RETURN TRUE; END IF;
        WHEN 'wednesday' THEN
            IF v_schedule.wednesday THEN RETURN TRUE; END IF;
        WHEN 'thursday' THEN
            IF v_schedule.thursday THEN RETURN TRUE; END IF;
        WHEN 'friday' THEN
            IF v_schedule.friday THEN RETURN TRUE; END IF;
        WHEN 'saturday' THEN
            IF v_schedule.saturday THEN RETURN TRUE; END IF;
        WHEN 'sunday' THEN
            IF v_schedule.sunday THEN RETURN TRUE; END IF;
    END CASE;

    -- TODO: Check if date is Poya day (requires Calendarific API integration)
    -- For now, assume backend will handle Poya day checking
    -- IF v_schedule.poya_day AND v_is_poya THEN RETURN TRUE; END IF;

    -- TODO: Check if date is holiday (requires Calendarific API integration)
    -- For now, assume backend will handle holiday checking
    -- IF v_schedule.holiday AND v_is_holiday THEN RETURN TRUE; END IF;

    RETURN FALSE;
END;
$$;


--
-- Name: FUNCTION schedule_operates_on_date(p_schedule_id character varying, p_date date); Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON FUNCTION public.schedule_operates_on_date(p_schedule_id character varying, p_date date) IS 'Check if a train schedule operates on a specific date based on day of week, Poya day, and holiday flags';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: validate_schedule_capacity(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validate_schedule_capacity() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if schedule actually operates on this date
    IF NOT schedule_operates_on_date(NEW.schedule_id, NEW.schedule_date) THEN
        RAISE EXCEPTION 'Schedule % does not operate on date %', NEW.schedule_id, NEW.schedule_date;
    END IF;

    RETURN NEW;
END;
$$;


--
-- Name: apply_rls(jsonb, integer); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer DEFAULT (1024 * 1024)) RETURNS SETOF realtime.wal_rls
    LANGUAGE plpgsql
    AS $$
declare
-- Regclass of the table e.g. public.notes
entity_ regclass = (quote_ident(wal ->> 'schema') || '.' || quote_ident(wal ->> 'table'))::regclass;

-- I, U, D, T: insert, update ...
action realtime.action = (
    case wal ->> 'action'
        when 'I' then 'INSERT'
        when 'U' then 'UPDATE'
        when 'D' then 'DELETE'
        else 'ERROR'
    end
);

-- Is row level security enabled for the table
is_rls_enabled bool = relrowsecurity from pg_class where oid = entity_;

subscriptions realtime.subscription[] = array_agg(subs)
    from
        realtime.subscription subs
    where
        subs.entity = entity_;

-- Subscription vars
roles regrole[] = array_agg(distinct us.claims_role::text)
    from
        unnest(subscriptions) us;

working_role regrole;
claimed_role regrole;
claims jsonb;

subscription_id uuid;
subscription_has_access bool;
visible_to_subscription_ids uuid[] = '{}';

-- structured info for wal's columns
columns realtime.wal_column[];
-- previous identity values for update/delete
old_columns realtime.wal_column[];

error_record_exceeds_max_size boolean = octet_length(wal::text) > max_record_bytes;

-- Primary jsonb output for record
output jsonb;

begin
perform set_config('role', null, true);

columns =
    array_agg(
        (
            x->>'name',
            x->>'type',
            x->>'typeoid',
            realtime.cast(
                (x->'value') #>> '{}',
                coalesce(
                    (x->>'typeoid')::regtype, -- null when wal2json version <= 2.4
                    (x->>'type')::regtype
                )
            ),
            (pks ->> 'name') is not null,
            true
        )::realtime.wal_column
    )
    from
        jsonb_array_elements(wal -> 'columns') x
        left join jsonb_array_elements(wal -> 'pk') pks
            on (x ->> 'name') = (pks ->> 'name');

old_columns =
    array_agg(
        (
            x->>'name',
            x->>'type',
            x->>'typeoid',
            realtime.cast(
                (x->'value') #>> '{}',
                coalesce(
                    (x->>'typeoid')::regtype, -- null when wal2json version <= 2.4
                    (x->>'type')::regtype
                )
            ),
            (pks ->> 'name') is not null,
            true
        )::realtime.wal_column
    )
    from
        jsonb_array_elements(wal -> 'identity') x
        left join jsonb_array_elements(wal -> 'pk') pks
            on (x ->> 'name') = (pks ->> 'name');

for working_role in select * from unnest(roles) loop

    -- Update `is_selectable` for columns and old_columns
    columns =
        array_agg(
            (
                c.name,
                c.type_name,
                c.type_oid,
                c.value,
                c.is_pkey,
                pg_catalog.has_column_privilege(working_role, entity_, c.name, 'SELECT')
            )::realtime.wal_column
        )
        from
            unnest(columns) c;

    old_columns =
            array_agg(
                (
                    c.name,
                    c.type_name,
                    c.type_oid,
                    c.value,
                    c.is_pkey,
                    pg_catalog.has_column_privilege(working_role, entity_, c.name, 'SELECT')
                )::realtime.wal_column
            )
            from
                unnest(old_columns) c;

    if action <> 'DELETE' and count(1) = 0 from unnest(columns) c where c.is_pkey then
        return next (
            jsonb_build_object(
                'schema', wal ->> 'schema',
                'table', wal ->> 'table',
                'type', action
            ),
            is_rls_enabled,
            -- subscriptions is already filtered by entity
            (select array_agg(s.subscription_id) from unnest(subscriptions) as s where claims_role = working_role),
            array['Error 400: Bad Request, no primary key']
        )::realtime.wal_rls;

    -- The claims role does not have SELECT permission to the primary key of entity
    elsif action <> 'DELETE' and sum(c.is_selectable::int) <> count(1) from unnest(columns) c where c.is_pkey then
        return next (
            jsonb_build_object(
                'schema', wal ->> 'schema',
                'table', wal ->> 'table',
                'type', action
            ),
            is_rls_enabled,
            (select array_agg(s.subscription_id) from unnest(subscriptions) as s where claims_role = working_role),
            array['Error 401: Unauthorized']
        )::realtime.wal_rls;

    else
        output = jsonb_build_object(
            'schema', wal ->> 'schema',
            'table', wal ->> 'table',
            'type', action,
            'commit_timestamp', to_char(
                ((wal ->> 'timestamp')::timestamptz at time zone 'utc'),
                'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'
            ),
            'columns', (
                select
                    jsonb_agg(
                        jsonb_build_object(
                            'name', pa.attname,
                            'type', pt.typname
                        )
                        order by pa.attnum asc
                    )
                from
                    pg_attribute pa
                    join pg_type pt
                        on pa.atttypid = pt.oid
                where
                    attrelid = entity_
                    and attnum > 0
                    and pg_catalog.has_column_privilege(working_role, entity_, pa.attname, 'SELECT')
            )
        )
        -- Add "record" key for insert and update
        || case
            when action in ('INSERT', 'UPDATE') then
                jsonb_build_object(
                    'record',
                    (
                        select
                            jsonb_object_agg(
                                -- if unchanged toast, get column name and value from old record
                                coalesce((c).name, (oc).name),
                                case
                                    when (c).name is null then (oc).value
                                    else (c).value
                                end
                            )
                        from
                            unnest(columns) c
                            full outer join unnest(old_columns) oc
                                on (c).name = (oc).name
                        where
                            coalesce((c).is_selectable, (oc).is_selectable)
                            and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                    )
                )
            else '{}'::jsonb
        end
        -- Add "old_record" key for update and delete
        || case
            when action = 'UPDATE' then
                jsonb_build_object(
                        'old_record',
                        (
                            select jsonb_object_agg((c).name, (c).value)
                            from unnest(old_columns) c
                            where
                                (c).is_selectable
                                and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                        )
                    )
            when action = 'DELETE' then
                jsonb_build_object(
                    'old_record',
                    (
                        select jsonb_object_agg((c).name, (c).value)
                        from unnest(old_columns) c
                        where
                            (c).is_selectable
                            and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                            and ( not is_rls_enabled or (c).is_pkey ) -- if RLS enabled, we can't secure deletes so filter to pkey
                    )
                )
            else '{}'::jsonb
        end;

        -- Create the prepared statement
        if is_rls_enabled and action <> 'DELETE' then
            if (select 1 from pg_prepared_statements where name = 'walrus_rls_stmt' limit 1) > 0 then
                deallocate walrus_rls_stmt;
            end if;
            execute realtime.build_prepared_statement_sql('walrus_rls_stmt', entity_, columns);
        end if;

        visible_to_subscription_ids = '{}';

        for subscription_id, claims in (
                select
                    subs.subscription_id,
                    subs.claims
                from
                    unnest(subscriptions) subs
                where
                    subs.entity = entity_
                    and subs.claims_role = working_role
                    and (
                        realtime.is_visible_through_filters(columns, subs.filters)
                        or (
                          action = 'DELETE'
                          and realtime.is_visible_through_filters(old_columns, subs.filters)
                        )
                    )
        ) loop

            if not is_rls_enabled or action = 'DELETE' then
                visible_to_subscription_ids = visible_to_subscription_ids || subscription_id;
            else
                -- Check if RLS allows the role to see the record
                perform
                    -- Trim leading and trailing quotes from working_role because set_config
                    -- doesn't recognize the role as valid if they are included
                    set_config('role', trim(both '"' from working_role::text), true),
                    set_config('request.jwt.claims', claims::text, true);

                execute 'execute walrus_rls_stmt' into subscription_has_access;

                if subscription_has_access then
                    visible_to_subscription_ids = visible_to_subscription_ids || subscription_id;
                end if;
            end if;
        end loop;

        perform set_config('role', null, true);

        return next (
            output,
            is_rls_enabled,
            visible_to_subscription_ids,
            case
                when error_record_exceeds_max_size then array['Error 413: Payload Too Large']
                else '{}'
            end
        )::realtime.wal_rls;

    end if;
end loop;

perform set_config('role', null, true);
end;
$$;


--
-- Name: broadcast_changes(text, text, text, text, text, record, record, text); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.broadcast_changes(topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text DEFAULT 'ROW'::text) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    -- Declare a variable to hold the JSONB representation of the row
    row_data jsonb := '{}'::jsonb;
BEGIN
    IF level = 'STATEMENT' THEN
        RAISE EXCEPTION 'function can only be triggered for each row, not for each statement';
    END IF;
    -- Check the operation type and handle accordingly
    IF operation = 'INSERT' OR operation = 'UPDATE' OR operation = 'DELETE' THEN
        row_data := jsonb_build_object('old_record', OLD, 'record', NEW, 'operation', operation, 'table', table_name, 'schema', table_schema);
        PERFORM realtime.send (row_data, event_name, topic_name);
    ELSE
        RAISE EXCEPTION 'Unexpected operation type: %', operation;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to process the row: %', SQLERRM;
END;

$$;


--
-- Name: build_prepared_statement_sql(text, regclass, realtime.wal_column[]); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) RETURNS text
    LANGUAGE sql
    AS $$
      /*
      Builds a sql string that, if executed, creates a prepared statement to
      tests retrive a row from *entity* by its primary key columns.
      Example
          select realtime.build_prepared_statement_sql('public.notes', '{"id"}'::text[], '{"bigint"}'::text[])
      */
          select
      'prepare ' || prepared_statement_name || ' as
          select
              exists(
                  select
                      1
                  from
                      ' || entity || '
                  where
                      ' || string_agg(quote_ident(pkc.name) || '=' || quote_nullable(pkc.value #>> '{}') , ' and ') || '
              )'
          from
              unnest(columns) pkc
          where
              pkc.is_pkey
          group by
              entity
      $$;


--
-- Name: cast(text, regtype); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime."cast"(val text, type_ regtype) RETURNS jsonb
    LANGUAGE plpgsql IMMUTABLE
    AS $$
    declare
      res jsonb;
    begin
      execute format('select to_jsonb(%L::'|| type_::text || ')', val)  into res;
      return res;
    end
    $$;


--
-- Name: check_equality_op(realtime.equality_op, regtype, text, text); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) RETURNS boolean
    LANGUAGE plpgsql IMMUTABLE
    AS $$
      /*
      Casts *val_1* and *val_2* as type *type_* and check the *op* condition for truthiness
      */
      declare
          op_symbol text = (
              case
                  when op = 'eq' then '='
                  when op = 'neq' then '!='
                  when op = 'lt' then '<'
                  when op = 'lte' then '<='
                  when op = 'gt' then '>'
                  when op = 'gte' then '>='
                  when op = 'in' then '= any'
                  else 'UNKNOWN OP'
              end
          );
          res boolean;
      begin
          execute format(
              'select %L::'|| type_::text || ' ' || op_symbol
              || ' ( %L::'
              || (
                  case
                      when op = 'in' then type_::text || '[]'
                      else type_::text end
              )
              || ')', val_1, val_2) into res;
          return res;
      end;
      $$;


--
-- Name: is_visible_through_filters(realtime.wal_column[], realtime.user_defined_filter[]); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) RETURNS boolean
    LANGUAGE sql IMMUTABLE
    AS $_$
    /*
    Should the record be visible (true) or filtered out (false) after *filters* are applied
    */
        select
            -- Default to allowed when no filters present
            $2 is null -- no filters. this should not happen because subscriptions has a default
            or array_length($2, 1) is null -- array length of an empty array is null
            or bool_and(
                coalesce(
                    realtime.check_equality_op(
                        op:=f.op,
                        type_:=coalesce(
                            col.type_oid::regtype, -- null when wal2json version <= 2.4
                            col.type_name::regtype
                        ),
                        -- cast jsonb to text
                        val_1:=col.value #>> '{}',
                        val_2:=f.value
                    ),
                    false -- if null, filter does not match
                )
            )
        from
            unnest(filters) f
            join unnest(columns) col
                on f.column_name = col.name;
    $_$;


--
-- Name: list_changes(name, name, integer, integer); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.list_changes(publication name, slot_name name, max_changes integer, max_record_bytes integer) RETURNS SETOF realtime.wal_rls
    LANGUAGE sql
    SET log_min_messages TO 'fatal'
    AS $$
      with pub as (
        select
          concat_ws(
            ',',
            case when bool_or(pubinsert) then 'insert' else null end,
            case when bool_or(pubupdate) then 'update' else null end,
            case when bool_or(pubdelete) then 'delete' else null end
          ) as w2j_actions,
          coalesce(
            string_agg(
              realtime.quote_wal2json(format('%I.%I', schemaname, tablename)::regclass),
              ','
            ) filter (where ppt.tablename is not null and ppt.tablename not like '% %'),
            ''
          ) w2j_add_tables
        from
          pg_publication pp
          left join pg_publication_tables ppt
            on pp.pubname = ppt.pubname
        where
          pp.pubname = publication
        group by
          pp.pubname
        limit 1
      ),
      w2j as (
        select
          x.*, pub.w2j_add_tables
        from
          pub,
          pg_logical_slot_get_changes(
            slot_name, null, max_changes,
            'include-pk', 'true',
            'include-transaction', 'false',
            'include-timestamp', 'true',
            'include-type-oids', 'true',
            'format-version', '2',
            'actions', pub.w2j_actions,
            'add-tables', pub.w2j_add_tables
          ) x
      )
      select
        xyz.wal,
        xyz.is_rls_enabled,
        xyz.subscription_ids,
        xyz.errors
      from
        w2j,
        realtime.apply_rls(
          wal := w2j.data::jsonb,
          max_record_bytes := max_record_bytes
        ) xyz(wal, is_rls_enabled, subscription_ids, errors)
      where
        w2j.w2j_add_tables <> ''
        and xyz.subscription_ids[1] is not null
    $$;


--
-- Name: quote_wal2json(regclass); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.quote_wal2json(entity regclass) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
      select
        (
          select string_agg('' || ch,'')
          from unnest(string_to_array(nsp.nspname::text, null)) with ordinality x(ch, idx)
          where
            not (x.idx = 1 and x.ch = '"')
            and not (
              x.idx = array_length(string_to_array(nsp.nspname::text, null), 1)
              and x.ch = '"'
            )
        )
        || '.'
        || (
          select string_agg('' || ch,'')
          from unnest(string_to_array(pc.relname::text, null)) with ordinality x(ch, idx)
          where
            not (x.idx = 1 and x.ch = '"')
            and not (
              x.idx = array_length(string_to_array(nsp.nspname::text, null), 1)
              and x.ch = '"'
            )
          )
      from
        pg_class pc
        join pg_namespace nsp
          on pc.relnamespace = nsp.oid
      where
        pc.oid = entity
    $$;


--
-- Name: send(jsonb, text, text, boolean); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.send(payload jsonb, event text, topic text, private boolean DEFAULT true) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
  generated_id uuid;
  final_payload jsonb;
BEGIN
  BEGIN
    -- Generate a new UUID for the id
    generated_id := gen_random_uuid();

    -- Check if payload has an 'id' key, if not, add the generated UUID
    IF payload ? 'id' THEN
      final_payload := payload;
    ELSE
      final_payload := jsonb_set(payload, '{id}', to_jsonb(generated_id));
    END IF;

    -- Set the topic configuration
    EXECUTE format('SET LOCAL realtime.topic TO %L', topic);

    -- Attempt to insert the message
    INSERT INTO realtime.messages (id, payload, event, topic, private, extension)
    VALUES (generated_id, final_payload, event, topic, private, 'broadcast');
  EXCEPTION
    WHEN OTHERS THEN
      -- Capture and notify the error
      RAISE WARNING 'ErrorSendingBroadcastMessage: %', SQLERRM;
  END;
END;
$$;


--
-- Name: subscription_check_filters(); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.subscription_check_filters() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    /*
    Validates that the user defined filters for a subscription:
    - refer to valid columns that the claimed role may access
    - values are coercable to the correct column type
    */
    declare
        col_names text[] = coalesce(
                array_agg(c.column_name order by c.ordinal_position),
                '{}'::text[]
            )
            from
                information_schema.columns c
            where
                format('%I.%I', c.table_schema, c.table_name)::regclass = new.entity
                and pg_catalog.has_column_privilege(
                    (new.claims ->> 'role'),
                    format('%I.%I', c.table_schema, c.table_name)::regclass,
                    c.column_name,
                    'SELECT'
                );
        filter realtime.user_defined_filter;
        col_type regtype;

        in_val jsonb;
    begin
        for filter in select * from unnest(new.filters) loop
            -- Filtered column is valid
            if not filter.column_name = any(col_names) then
                raise exception 'invalid column for filter %', filter.column_name;
            end if;

            -- Type is sanitized and safe for string interpolation
            col_type = (
                select atttypid::regtype
                from pg_catalog.pg_attribute
                where attrelid = new.entity
                      and attname = filter.column_name
            );
            if col_type is null then
                raise exception 'failed to lookup type for column %', filter.column_name;
            end if;

            -- Set maximum number of entries for in filter
            if filter.op = 'in'::realtime.equality_op then
                in_val = realtime.cast(filter.value, (col_type::text || '[]')::regtype);
                if coalesce(jsonb_array_length(in_val), 0) > 100 then
                    raise exception 'too many values for `in` filter. Maximum 100';
                end if;
            else
                -- raises an exception if value is not coercable to type
                perform realtime.cast(filter.value, col_type);
            end if;

        end loop;

        -- Apply consistent order to filters so the unique constraint on
        -- (subscription_id, entity, filters) can't be tricked by a different filter order
        new.filters = coalesce(
            array_agg(f order by f.column_name, f.op, f.value),
            '{}'
        ) from unnest(new.filters) f;

        return new;
    end;
    $$;


--
-- Name: to_regrole(text); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.to_regrole(role_name text) RETURNS regrole
    LANGUAGE sql IMMUTABLE
    AS $$ select role_name::regrole $$;


--
-- Name: topic(); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.topic() RETURNS text
    LANGUAGE sql STABLE
    AS $$
select nullif(current_setting('realtime.topic', true), '')::text;
$$;


--
-- Name: add_prefixes(text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.add_prefixes(_bucket_id text, _name text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    prefixes text[];
BEGIN
    prefixes := "storage"."get_prefixes"("_name");

    IF array_length(prefixes, 1) > 0 THEN
        INSERT INTO storage.prefixes (name, bucket_id)
        SELECT UNNEST(prefixes) as name, "_bucket_id" ON CONFLICT DO NOTHING;
    END IF;
END;
$$;


--
-- Name: can_insert_object(text, text, uuid, jsonb); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.can_insert_object(bucketid text, name text, owner uuid, metadata jsonb) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  INSERT INTO "storage"."objects" ("bucket_id", "name", "owner", "metadata") VALUES (bucketid, name, owner, metadata);
  -- hack to rollback the successful insert
  RAISE sqlstate 'PT200' using
  message = 'ROLLBACK',
  detail = 'rollback successful insert';
END
$$;


--
-- Name: delete_leaf_prefixes(text[], text[]); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.delete_leaf_prefixes(bucket_ids text[], names text[]) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_rows_deleted integer;
BEGIN
    LOOP
        WITH candidates AS (
            SELECT DISTINCT
                t.bucket_id,
                unnest(storage.get_prefixes(t.name)) AS name
            FROM unnest(bucket_ids, names) AS t(bucket_id, name)
        ),
        uniq AS (
             SELECT
                 bucket_id,
                 name,
                 storage.get_level(name) AS level
             FROM candidates
             WHERE name <> ''
             GROUP BY bucket_id, name
        ),
        leaf AS (
             SELECT
                 p.bucket_id,
                 p.name,
                 p.level
             FROM storage.prefixes AS p
                  JOIN uniq AS u
                       ON u.bucket_id = p.bucket_id
                           AND u.name = p.name
                           AND u.level = p.level
             WHERE NOT EXISTS (
                 SELECT 1
                 FROM storage.objects AS o
                 WHERE o.bucket_id = p.bucket_id
                   AND o.level = p.level + 1
                   AND o.name COLLATE "C" LIKE p.name || '/%'
             )
             AND NOT EXISTS (
                 SELECT 1
                 FROM storage.prefixes AS c
                 WHERE c.bucket_id = p.bucket_id
                   AND c.level = p.level + 1
                   AND c.name COLLATE "C" LIKE p.name || '/%'
             )
        )
        DELETE
        FROM storage.prefixes AS p
            USING leaf AS l
        WHERE p.bucket_id = l.bucket_id
          AND p.name = l.name
          AND p.level = l.level;

        GET DIAGNOSTICS v_rows_deleted = ROW_COUNT;
        EXIT WHEN v_rows_deleted = 0;
    END LOOP;
END;
$$;


--
-- Name: delete_prefix(text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.delete_prefix(_bucket_id text, _name text) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    -- Check if we can delete the prefix
    IF EXISTS(
        SELECT FROM "storage"."prefixes"
        WHERE "prefixes"."bucket_id" = "_bucket_id"
          AND level = "storage"."get_level"("_name") + 1
          AND "prefixes"."name" COLLATE "C" LIKE "_name" || '/%'
        LIMIT 1
    )
    OR EXISTS(
        SELECT FROM "storage"."objects"
        WHERE "objects"."bucket_id" = "_bucket_id"
          AND "storage"."get_level"("objects"."name") = "storage"."get_level"("_name") + 1
          AND "objects"."name" COLLATE "C" LIKE "_name" || '/%'
        LIMIT 1
    ) THEN
    -- There are sub-objects, skip deletion
    RETURN false;
    ELSE
        DELETE FROM "storage"."prefixes"
        WHERE "prefixes"."bucket_id" = "_bucket_id"
          AND level = "storage"."get_level"("_name")
          AND "prefixes"."name" = "_name";
        RETURN true;
    END IF;
END;
$$;


--
-- Name: delete_prefix_hierarchy_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.delete_prefix_hierarchy_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    prefix text;
BEGIN
    prefix := "storage"."get_prefix"(OLD."name");

    IF coalesce(prefix, '') != '' THEN
        PERFORM "storage"."delete_prefix"(OLD."bucket_id", prefix);
    END IF;

    RETURN OLD;
END;
$$;


--
-- Name: enforce_bucket_name_length(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.enforce_bucket_name_length() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
    if length(new.name) > 100 then
        raise exception 'bucket name "%" is too long (% characters). Max is 100.', new.name, length(new.name);
    end if;
    return new;
end;
$$;


--
-- Name: extension(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.extension(name text) RETURNS text
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    _parts text[];
    _filename text;
BEGIN
    SELECT string_to_array(name, '/') INTO _parts;
    SELECT _parts[array_length(_parts,1)] INTO _filename;
    RETURN reverse(split_part(reverse(_filename), '.', 1));
END
$$;


--
-- Name: filename(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.filename(name text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
_parts text[];
BEGIN
	select string_to_array(name, '/') into _parts;
	return _parts[array_length(_parts,1)];
END
$$;


--
-- Name: foldername(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.foldername(name text) RETURNS text[]
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    _parts text[];
BEGIN
    -- Split on "/" to get path segments
    SELECT string_to_array(name, '/') INTO _parts;
    -- Return everything except the last segment
    RETURN _parts[1 : array_length(_parts,1) - 1];
END
$$;


--
-- Name: get_level(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.get_level(name text) RETURNS integer
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
SELECT array_length(string_to_array("name", '/'), 1);
$$;


--
-- Name: get_prefix(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.get_prefix(name text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
SELECT
    CASE WHEN strpos("name", '/') > 0 THEN
             regexp_replace("name", '[\/]{1}[^\/]+\/?$', '')
         ELSE
             ''
        END;
$_$;


--
-- Name: get_prefixes(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.get_prefixes(name text) RETURNS text[]
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $$
DECLARE
    parts text[];
    prefixes text[];
    prefix text;
BEGIN
    -- Split the name into parts by '/'
    parts := string_to_array("name", '/');
    prefixes := '{}';

    -- Construct the prefixes, stopping one level below the last part
    FOR i IN 1..array_length(parts, 1) - 1 LOOP
            prefix := array_to_string(parts[1:i], '/');
            prefixes := array_append(prefixes, prefix);
    END LOOP;

    RETURN prefixes;
END;
$$;


--
-- Name: get_size_by_bucket(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.get_size_by_bucket() RETURNS TABLE(size bigint, bucket_id text)
    LANGUAGE plpgsql STABLE
    AS $$
BEGIN
    return query
        select sum((metadata->>'size')::bigint) as size, obj.bucket_id
        from "storage".objects as obj
        group by obj.bucket_id;
END
$$;


--
-- Name: list_multipart_uploads_with_delimiter(text, text, text, integer, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.list_multipart_uploads_with_delimiter(bucket_id text, prefix_param text, delimiter_param text, max_keys integer DEFAULT 100, next_key_token text DEFAULT ''::text, next_upload_token text DEFAULT ''::text) RETURNS TABLE(key text, id text, created_at timestamp with time zone)
    LANGUAGE plpgsql
    AS $_$
BEGIN
    RETURN QUERY EXECUTE
        'SELECT DISTINCT ON(key COLLATE "C") * from (
            SELECT
                CASE
                    WHEN position($2 IN substring(key from length($1) + 1)) > 0 THEN
                        substring(key from 1 for length($1) + position($2 IN substring(key from length($1) + 1)))
                    ELSE
                        key
                END AS key, id, created_at
            FROM
                storage.s3_multipart_uploads
            WHERE
                bucket_id = $5 AND
                key ILIKE $1 || ''%'' AND
                CASE
                    WHEN $4 != '''' AND $6 = '''' THEN
                        CASE
                            WHEN position($2 IN substring(key from length($1) + 1)) > 0 THEN
                                substring(key from 1 for length($1) + position($2 IN substring(key from length($1) + 1))) COLLATE "C" > $4
                            ELSE
                                key COLLATE "C" > $4
                            END
                    ELSE
                        true
                END AND
                CASE
                    WHEN $6 != '''' THEN
                        id COLLATE "C" > $6
                    ELSE
                        true
                    END
            ORDER BY
                key COLLATE "C" ASC, created_at ASC) as e order by key COLLATE "C" LIMIT $3'
        USING prefix_param, delimiter_param, max_keys, next_key_token, bucket_id, next_upload_token;
END;
$_$;


--
-- Name: list_objects_with_delimiter(text, text, text, integer, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.list_objects_with_delimiter(bucket_id text, prefix_param text, delimiter_param text, max_keys integer DEFAULT 100, start_after text DEFAULT ''::text, next_token text DEFAULT ''::text) RETURNS TABLE(name text, id uuid, metadata jsonb, updated_at timestamp with time zone)
    LANGUAGE plpgsql
    AS $_$
BEGIN
    RETURN QUERY EXECUTE
        'SELECT DISTINCT ON(name COLLATE "C") * from (
            SELECT
                CASE
                    WHEN position($2 IN substring(name from length($1) + 1)) > 0 THEN
                        substring(name from 1 for length($1) + position($2 IN substring(name from length($1) + 1)))
                    ELSE
                        name
                END AS name, id, metadata, updated_at
            FROM
                storage.objects
            WHERE
                bucket_id = $5 AND
                name ILIKE $1 || ''%'' AND
                CASE
                    WHEN $6 != '''' THEN
                    name COLLATE "C" > $6
                ELSE true END
                AND CASE
                    WHEN $4 != '''' THEN
                        CASE
                            WHEN position($2 IN substring(name from length($1) + 1)) > 0 THEN
                                substring(name from 1 for length($1) + position($2 IN substring(name from length($1) + 1))) COLLATE "C" > $4
                            ELSE
                                name COLLATE "C" > $4
                            END
                    ELSE
                        true
                END
            ORDER BY
                name COLLATE "C" ASC) as e order by name COLLATE "C" LIMIT $3'
        USING prefix_param, delimiter_param, max_keys, next_token, bucket_id, start_after;
END;
$_$;


--
-- Name: lock_top_prefixes(text[], text[]); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.lock_top_prefixes(bucket_ids text[], names text[]) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_bucket text;
    v_top text;
BEGIN
    FOR v_bucket, v_top IN
        SELECT DISTINCT t.bucket_id,
            split_part(t.name, '/', 1) AS top
        FROM unnest(bucket_ids, names) AS t(bucket_id, name)
        WHERE t.name <> ''
        ORDER BY 1, 2
        LOOP
            PERFORM pg_advisory_xact_lock(hashtextextended(v_bucket || '/' || v_top, 0));
        END LOOP;
END;
$$;


--
-- Name: objects_delete_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_delete_cleanup() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_bucket_ids text[];
    v_names      text[];
BEGIN
    IF current_setting('storage.gc.prefixes', true) = '1' THEN
        RETURN NULL;
    END IF;

    PERFORM set_config('storage.gc.prefixes', '1', true);

    SELECT COALESCE(array_agg(d.bucket_id), '{}'),
           COALESCE(array_agg(d.name), '{}')
    INTO v_bucket_ids, v_names
    FROM deleted AS d
    WHERE d.name <> '';

    PERFORM storage.lock_top_prefixes(v_bucket_ids, v_names);
    PERFORM storage.delete_leaf_prefixes(v_bucket_ids, v_names);

    RETURN NULL;
END;
$$;


--
-- Name: objects_insert_prefix_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_insert_prefix_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    NEW.level := "storage"."get_level"(NEW."name");

    RETURN NEW;
END;
$$;


--
-- Name: objects_update_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_update_cleanup() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    -- NEW - OLD (destinations to create prefixes for)
    v_add_bucket_ids text[];
    v_add_names      text[];

    -- OLD - NEW (sources to prune)
    v_src_bucket_ids text[];
    v_src_names      text[];
BEGIN
    IF TG_OP <> 'UPDATE' THEN
        RETURN NULL;
    END IF;

    -- 1) Compute NEW−OLD (added paths) and OLD−NEW (moved-away paths)
    WITH added AS (
        SELECT n.bucket_id, n.name
        FROM new_rows n
        WHERE n.name <> '' AND position('/' in n.name) > 0
        EXCEPT
        SELECT o.bucket_id, o.name FROM old_rows o WHERE o.name <> ''
    ),
    moved AS (
         SELECT o.bucket_id, o.name
         FROM old_rows o
         WHERE o.name <> ''
         EXCEPT
         SELECT n.bucket_id, n.name FROM new_rows n WHERE n.name <> ''
    )
    SELECT
        -- arrays for ADDED (dest) in stable order
        COALESCE( (SELECT array_agg(a.bucket_id ORDER BY a.bucket_id, a.name) FROM added a), '{}' ),
        COALESCE( (SELECT array_agg(a.name      ORDER BY a.bucket_id, a.name) FROM added a), '{}' ),
        -- arrays for MOVED (src) in stable order
        COALESCE( (SELECT array_agg(m.bucket_id ORDER BY m.bucket_id, m.name) FROM moved m), '{}' ),
        COALESCE( (SELECT array_agg(m.name      ORDER BY m.bucket_id, m.name) FROM moved m), '{}' )
    INTO v_add_bucket_ids, v_add_names, v_src_bucket_ids, v_src_names;

    -- Nothing to do?
    IF (array_length(v_add_bucket_ids, 1) IS NULL) AND (array_length(v_src_bucket_ids, 1) IS NULL) THEN
        RETURN NULL;
    END IF;

    -- 2) Take per-(bucket, top) locks: ALL prefixes in consistent global order to prevent deadlocks
    DECLARE
        v_all_bucket_ids text[];
        v_all_names text[];
    BEGIN
        -- Combine source and destination arrays for consistent lock ordering
        v_all_bucket_ids := COALESCE(v_src_bucket_ids, '{}') || COALESCE(v_add_bucket_ids, '{}');
        v_all_names := COALESCE(v_src_names, '{}') || COALESCE(v_add_names, '{}');

        -- Single lock call ensures consistent global ordering across all transactions
        IF array_length(v_all_bucket_ids, 1) IS NOT NULL THEN
            PERFORM storage.lock_top_prefixes(v_all_bucket_ids, v_all_names);
        END IF;
    END;

    -- 3) Create destination prefixes (NEW−OLD) BEFORE pruning sources
    IF array_length(v_add_bucket_ids, 1) IS NOT NULL THEN
        WITH candidates AS (
            SELECT DISTINCT t.bucket_id, unnest(storage.get_prefixes(t.name)) AS name
            FROM unnest(v_add_bucket_ids, v_add_names) AS t(bucket_id, name)
            WHERE name <> ''
        )
        INSERT INTO storage.prefixes (bucket_id, name)
        SELECT c.bucket_id, c.name
        FROM candidates c
        ON CONFLICT DO NOTHING;
    END IF;

    -- 4) Prune source prefixes bottom-up for OLD−NEW
    IF array_length(v_src_bucket_ids, 1) IS NOT NULL THEN
        -- re-entrancy guard so DELETE on prefixes won't recurse
        IF current_setting('storage.gc.prefixes', true) <> '1' THEN
            PERFORM set_config('storage.gc.prefixes', '1', true);
        END IF;

        PERFORM storage.delete_leaf_prefixes(v_src_bucket_ids, v_src_names);
    END IF;

    RETURN NULL;
END;
$$;


--
-- Name: objects_update_level_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_update_level_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Ensure this is an update operation and the name has changed
    IF TG_OP = 'UPDATE' AND (NEW."name" <> OLD."name" OR NEW."bucket_id" <> OLD."bucket_id") THEN
        -- Set the new level
        NEW."level" := "storage"."get_level"(NEW."name");
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: objects_update_prefix_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_update_prefix_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    old_prefixes TEXT[];
BEGIN
    -- Ensure this is an update operation and the name has changed
    IF TG_OP = 'UPDATE' AND (NEW."name" <> OLD."name" OR NEW."bucket_id" <> OLD."bucket_id") THEN
        -- Retrieve old prefixes
        old_prefixes := "storage"."get_prefixes"(OLD."name");

        -- Remove old prefixes that are only used by this object
        WITH all_prefixes as (
            SELECT unnest(old_prefixes) as prefix
        ),
        can_delete_prefixes as (
             SELECT prefix
             FROM all_prefixes
             WHERE NOT EXISTS (
                 SELECT 1 FROM "storage"."objects"
                 WHERE "bucket_id" = OLD."bucket_id"
                   AND "name" <> OLD."name"
                   AND "name" LIKE (prefix || '%')
             )
         )
        DELETE FROM "storage"."prefixes" WHERE name IN (SELECT prefix FROM can_delete_prefixes);

        -- Add new prefixes
        PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    END IF;
    -- Set the new level
    NEW."level" := "storage"."get_level"(NEW."name");

    RETURN NEW;
END;
$$;


--
-- Name: operation(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.operation() RETURNS text
    LANGUAGE plpgsql STABLE
    AS $$
BEGIN
    RETURN current_setting('storage.operation', true);
END;
$$;


--
-- Name: prefixes_delete_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.prefixes_delete_cleanup() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_bucket_ids text[];
    v_names      text[];
BEGIN
    IF current_setting('storage.gc.prefixes', true) = '1' THEN
        RETURN NULL;
    END IF;

    PERFORM set_config('storage.gc.prefixes', '1', true);

    SELECT COALESCE(array_agg(d.bucket_id), '{}'),
           COALESCE(array_agg(d.name), '{}')
    INTO v_bucket_ids, v_names
    FROM deleted AS d
    WHERE d.name <> '';

    PERFORM storage.lock_top_prefixes(v_bucket_ids, v_names);
    PERFORM storage.delete_leaf_prefixes(v_bucket_ids, v_names);

    RETURN NULL;
END;
$$;


--
-- Name: prefixes_insert_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.prefixes_insert_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    RETURN NEW;
END;
$$;


--
-- Name: search(text, text, integer, integer, integer, text, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.search(prefix text, bucketname text, limits integer DEFAULT 100, levels integer DEFAULT 1, offsets integer DEFAULT 0, search text DEFAULT ''::text, sortcolumn text DEFAULT 'name'::text, sortorder text DEFAULT 'asc'::text) RETURNS TABLE(name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql
    AS $$
declare
    can_bypass_rls BOOLEAN;
begin
    SELECT rolbypassrls
    INTO can_bypass_rls
    FROM pg_roles
    WHERE rolname = coalesce(nullif(current_setting('role', true), 'none'), current_user);

    IF can_bypass_rls THEN
        RETURN QUERY SELECT * FROM storage.search_v1_optimised(prefix, bucketname, limits, levels, offsets, search, sortcolumn, sortorder);
    ELSE
        RETURN QUERY SELECT * FROM storage.search_legacy_v1(prefix, bucketname, limits, levels, offsets, search, sortcolumn, sortorder);
    END IF;
end;
$$;


--
-- Name: search_legacy_v1(text, text, integer, integer, integer, text, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.search_legacy_v1(prefix text, bucketname text, limits integer DEFAULT 100, levels integer DEFAULT 1, offsets integer DEFAULT 0, search text DEFAULT ''::text, sortcolumn text DEFAULT 'name'::text, sortorder text DEFAULT 'asc'::text) RETURNS TABLE(name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $_$
declare
    v_order_by text;
    v_sort_order text;
begin
    case
        when sortcolumn = 'name' then
            v_order_by = 'name';
        when sortcolumn = 'updated_at' then
            v_order_by = 'updated_at';
        when sortcolumn = 'created_at' then
            v_order_by = 'created_at';
        when sortcolumn = 'last_accessed_at' then
            v_order_by = 'last_accessed_at';
        else
            v_order_by = 'name';
        end case;

    case
        when sortorder = 'asc' then
            v_sort_order = 'asc';
        when sortorder = 'desc' then
            v_sort_order = 'desc';
        else
            v_sort_order = 'asc';
        end case;

    v_order_by = v_order_by || ' ' || v_sort_order;

    return query execute
        'with folders as (
           select path_tokens[$1] as folder
           from storage.objects
             where objects.name ilike $2 || $3 || ''%''
               and bucket_id = $4
               and array_length(objects.path_tokens, 1) <> $1
           group by folder
           order by folder ' || v_sort_order || '
     )
     (select folder as "name",
            null as id,
            null as updated_at,
            null as created_at,
            null as last_accessed_at,
            null as metadata from folders)
     union all
     (select path_tokens[$1] as "name",
            id,
            updated_at,
            created_at,
            last_accessed_at,
            metadata
     from storage.objects
     where objects.name ilike $2 || $3 || ''%''
       and bucket_id = $4
       and array_length(objects.path_tokens, 1) = $1
     order by ' || v_order_by || ')
     limit $5
     offset $6' using levels, prefix, search, bucketname, limits, offsets;
end;
$_$;


--
-- Name: search_v1_optimised(text, text, integer, integer, integer, text, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.search_v1_optimised(prefix text, bucketname text, limits integer DEFAULT 100, levels integer DEFAULT 1, offsets integer DEFAULT 0, search text DEFAULT ''::text, sortcolumn text DEFAULT 'name'::text, sortorder text DEFAULT 'asc'::text) RETURNS TABLE(name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $_$
declare
    v_order_by text;
    v_sort_order text;
begin
    case
        when sortcolumn = 'name' then
            v_order_by = 'name';
        when sortcolumn = 'updated_at' then
            v_order_by = 'updated_at';
        when sortcolumn = 'created_at' then
            v_order_by = 'created_at';
        when sortcolumn = 'last_accessed_at' then
            v_order_by = 'last_accessed_at';
        else
            v_order_by = 'name';
        end case;

    case
        when sortorder = 'asc' then
            v_sort_order = 'asc';
        when sortorder = 'desc' then
            v_sort_order = 'desc';
        else
            v_sort_order = 'asc';
        end case;

    v_order_by = v_order_by || ' ' || v_sort_order;

    return query execute
        'with folders as (
           select (string_to_array(name, ''/''))[level] as name
           from storage.prefixes
             where lower(prefixes.name) like lower($2 || $3) || ''%''
               and bucket_id = $4
               and level = $1
           order by name ' || v_sort_order || '
     )
     (select name,
            null as id,
            null as updated_at,
            null as created_at,
            null as last_accessed_at,
            null as metadata from folders)
     union all
     (select path_tokens[level] as "name",
            id,
            updated_at,
            created_at,
            last_accessed_at,
            metadata
     from storage.objects
     where lower(objects.name) like lower($2 || $3) || ''%''
       and bucket_id = $4
       and level = $1
     order by ' || v_order_by || ')
     limit $5
     offset $6' using levels, prefix, search, bucketname, limits, offsets;
end;
$_$;


--
-- Name: search_v2(text, text, integer, integer, text, text, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.search_v2(prefix text, bucket_name text, limits integer DEFAULT 100, levels integer DEFAULT 1, start_after text DEFAULT ''::text, sort_order text DEFAULT 'asc'::text, sort_column text DEFAULT 'name'::text, sort_column_after text DEFAULT ''::text) RETURNS TABLE(key text, name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $_$
DECLARE
    sort_col text;
    sort_ord text;
    cursor_op text;
    cursor_expr text;
    sort_expr text;
BEGIN
    -- Validate sort_order
    sort_ord := lower(sort_order);
    IF sort_ord NOT IN ('asc', 'desc') THEN
        sort_ord := 'asc';
    END IF;

    -- Determine cursor comparison operator
    IF sort_ord = 'asc' THEN
        cursor_op := '>';
    ELSE
        cursor_op := '<';
    END IF;
    
    sort_col := lower(sort_column);
    -- Validate sort column  
    IF sort_col IN ('updated_at', 'created_at') THEN
        cursor_expr := format(
            '($5 = '''' OR ROW(date_trunc(''milliseconds'', %I), name COLLATE "C") %s ROW(COALESCE(NULLIF($6, '''')::timestamptz, ''epoch''::timestamptz), $5))',
            sort_col, cursor_op
        );
        sort_expr := format(
            'COALESCE(date_trunc(''milliseconds'', %I), ''epoch''::timestamptz) %s, name COLLATE "C" %s',
            sort_col, sort_ord, sort_ord
        );
    ELSE
        cursor_expr := format('($5 = '''' OR name COLLATE "C" %s $5)', cursor_op);
        sort_expr := format('name COLLATE "C" %s', sort_ord);
    END IF;

    RETURN QUERY EXECUTE format(
        $sql$
        SELECT * FROM (
            (
                SELECT
                    split_part(name, '/', $4) AS key,
                    name,
                    NULL::uuid AS id,
                    updated_at,
                    created_at,
                    NULL::timestamptz AS last_accessed_at,
                    NULL::jsonb AS metadata
                FROM storage.prefixes
                WHERE name COLLATE "C" LIKE $1 || '%%'
                    AND bucket_id = $2
                    AND level = $4
                    AND %s
                ORDER BY %s
                LIMIT $3
            )
            UNION ALL
            (
                SELECT
                    split_part(name, '/', $4) AS key,
                    name,
                    id,
                    updated_at,
                    created_at,
                    last_accessed_at,
                    metadata
                FROM storage.objects
                WHERE name COLLATE "C" LIKE $1 || '%%'
                    AND bucket_id = $2
                    AND level = $4
                    AND %s
                ORDER BY %s
                LIMIT $3
            )
        ) obj
        ORDER BY %s
        LIMIT $3
        $sql$,
        cursor_expr,    -- prefixes WHERE
        sort_expr,      -- prefixes ORDER BY
        cursor_expr,    -- objects WHERE
        sort_expr,      -- objects ORDER BY
        sort_expr       -- final ORDER BY
    )
    USING prefix, bucket_name, limits, levels, start_after, sort_column_after;
END;
$_$;


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW; 
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_log_entries; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.audit_log_entries (
    instance_id uuid,
    id uuid NOT NULL,
    payload json,
    created_at timestamp with time zone,
    ip_address character varying(64) DEFAULT ''::character varying NOT NULL
);


--
-- Name: TABLE audit_log_entries; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.audit_log_entries IS 'Auth: Audit trail for user actions.';


--
-- Name: flow_state; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.flow_state (
    id uuid NOT NULL,
    user_id uuid,
    auth_code text NOT NULL,
    code_challenge_method auth.code_challenge_method NOT NULL,
    code_challenge text NOT NULL,
    provider_type text NOT NULL,
    provider_access_token text,
    provider_refresh_token text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    authentication_method text NOT NULL,
    auth_code_issued_at timestamp with time zone
);


--
-- Name: TABLE flow_state; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.flow_state IS 'stores metadata for pkce logins';


--
-- Name: identities; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.identities (
    provider_id text NOT NULL,
    user_id uuid NOT NULL,
    identity_data jsonb NOT NULL,
    provider text NOT NULL,
    last_sign_in_at timestamp with time zone,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    email text GENERATED ALWAYS AS (lower((identity_data ->> 'email'::text))) STORED,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


--
-- Name: TABLE identities; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.identities IS 'Auth: Stores identities associated to a user.';


--
-- Name: COLUMN identities.email; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.identities.email IS 'Auth: Email is a generated column that references the optional email property in the identity_data';


--
-- Name: instances; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.instances (
    id uuid NOT NULL,
    uuid uuid,
    raw_base_config text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: TABLE instances; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.instances IS 'Auth: Manages users across multiple sites.';


--
-- Name: mfa_amr_claims; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.mfa_amr_claims (
    session_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    authentication_method text NOT NULL,
    id uuid NOT NULL
);


--
-- Name: TABLE mfa_amr_claims; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.mfa_amr_claims IS 'auth: stores authenticator method reference claims for multi factor authentication';


--
-- Name: mfa_challenges; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.mfa_challenges (
    id uuid NOT NULL,
    factor_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    verified_at timestamp with time zone,
    ip_address inet NOT NULL,
    otp_code text,
    web_authn_session_data jsonb
);


--
-- Name: TABLE mfa_challenges; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.mfa_challenges IS 'auth: stores metadata about challenge requests made';


--
-- Name: mfa_factors; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.mfa_factors (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    friendly_name text,
    factor_type auth.factor_type NOT NULL,
    status auth.factor_status NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    secret text,
    phone text,
    last_challenged_at timestamp with time zone,
    web_authn_credential jsonb,
    web_authn_aaguid uuid,
    last_webauthn_challenge_data jsonb
);


--
-- Name: TABLE mfa_factors; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.mfa_factors IS 'auth: stores metadata about factors';


--
-- Name: COLUMN mfa_factors.last_webauthn_challenge_data; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.mfa_factors.last_webauthn_challenge_data IS 'Stores the latest WebAuthn challenge data including attestation/assertion for customer verification';


--
-- Name: oauth_authorizations; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.oauth_authorizations (
    id uuid NOT NULL,
    authorization_id text NOT NULL,
    client_id uuid NOT NULL,
    user_id uuid,
    redirect_uri text NOT NULL,
    scope text NOT NULL,
    state text,
    resource text,
    code_challenge text,
    code_challenge_method auth.code_challenge_method,
    response_type auth.oauth_response_type DEFAULT 'code'::auth.oauth_response_type NOT NULL,
    status auth.oauth_authorization_status DEFAULT 'pending'::auth.oauth_authorization_status NOT NULL,
    authorization_code text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '00:03:00'::interval) NOT NULL,
    approved_at timestamp with time zone,
    CONSTRAINT oauth_authorizations_authorization_code_length CHECK ((char_length(authorization_code) <= 255)),
    CONSTRAINT oauth_authorizations_code_challenge_length CHECK ((char_length(code_challenge) <= 128)),
    CONSTRAINT oauth_authorizations_expires_at_future CHECK ((expires_at > created_at)),
    CONSTRAINT oauth_authorizations_redirect_uri_length CHECK ((char_length(redirect_uri) <= 2048)),
    CONSTRAINT oauth_authorizations_resource_length CHECK ((char_length(resource) <= 2048)),
    CONSTRAINT oauth_authorizations_scope_length CHECK ((char_length(scope) <= 4096)),
    CONSTRAINT oauth_authorizations_state_length CHECK ((char_length(state) <= 4096))
);


--
-- Name: oauth_clients; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.oauth_clients (
    id uuid NOT NULL,
    client_secret_hash text,
    registration_type auth.oauth_registration_type NOT NULL,
    redirect_uris text NOT NULL,
    grant_types text NOT NULL,
    client_name text,
    client_uri text,
    logo_uri text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    client_type auth.oauth_client_type DEFAULT 'confidential'::auth.oauth_client_type NOT NULL,
    CONSTRAINT oauth_clients_client_name_length CHECK ((char_length(client_name) <= 1024)),
    CONSTRAINT oauth_clients_client_uri_length CHECK ((char_length(client_uri) <= 2048)),
    CONSTRAINT oauth_clients_logo_uri_length CHECK ((char_length(logo_uri) <= 2048))
);


--
-- Name: oauth_consents; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.oauth_consents (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    client_id uuid NOT NULL,
    scopes text NOT NULL,
    granted_at timestamp with time zone DEFAULT now() NOT NULL,
    revoked_at timestamp with time zone,
    CONSTRAINT oauth_consents_revoked_after_granted CHECK (((revoked_at IS NULL) OR (revoked_at >= granted_at))),
    CONSTRAINT oauth_consents_scopes_length CHECK ((char_length(scopes) <= 2048)),
    CONSTRAINT oauth_consents_scopes_not_empty CHECK ((char_length(TRIM(BOTH FROM scopes)) > 0))
);


--
-- Name: one_time_tokens; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.one_time_tokens (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    token_type auth.one_time_token_type NOT NULL,
    token_hash text NOT NULL,
    relates_to text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT one_time_tokens_token_hash_check CHECK ((char_length(token_hash) > 0))
);


--
-- Name: refresh_tokens; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.refresh_tokens (
    instance_id uuid,
    id bigint NOT NULL,
    token character varying(255),
    user_id character varying(255),
    revoked boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    parent character varying(255),
    session_id uuid
);


--
-- Name: TABLE refresh_tokens; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.refresh_tokens IS 'Auth: Store of tokens used to refresh JWT tokens once they expire.';


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: auth; Owner: -
--

CREATE SEQUENCE auth.refresh_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: -
--

ALTER SEQUENCE auth.refresh_tokens_id_seq OWNED BY auth.refresh_tokens.id;


--
-- Name: saml_providers; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.saml_providers (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    entity_id text NOT NULL,
    metadata_xml text NOT NULL,
    metadata_url text,
    attribute_mapping jsonb,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    name_id_format text,
    CONSTRAINT "entity_id not empty" CHECK ((char_length(entity_id) > 0)),
    CONSTRAINT "metadata_url not empty" CHECK (((metadata_url = NULL::text) OR (char_length(metadata_url) > 0))),
    CONSTRAINT "metadata_xml not empty" CHECK ((char_length(metadata_xml) > 0))
);


--
-- Name: TABLE saml_providers; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.saml_providers IS 'Auth: Manages SAML Identity Provider connections.';


--
-- Name: saml_relay_states; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.saml_relay_states (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    request_id text NOT NULL,
    for_email text,
    redirect_to text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    flow_state_id uuid,
    CONSTRAINT "request_id not empty" CHECK ((char_length(request_id) > 0))
);


--
-- Name: TABLE saml_relay_states; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.saml_relay_states IS 'Auth: Contains SAML Relay State information for each Service Provider initiated login.';


--
-- Name: schema_migrations; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.schema_migrations (
    version character varying(255) NOT NULL
);


--
-- Name: TABLE schema_migrations; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.schema_migrations IS 'Auth: Manages updates to the auth system.';


--
-- Name: sessions; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.sessions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    factor_id uuid,
    aal auth.aal_level,
    not_after timestamp with time zone,
    refreshed_at timestamp without time zone,
    user_agent text,
    ip inet,
    tag text,
    oauth_client_id uuid,
    refresh_token_hmac_key text,
    refresh_token_counter bigint
);


--
-- Name: TABLE sessions; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.sessions IS 'Auth: Stores session data associated to a user.';


--
-- Name: COLUMN sessions.not_after; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.sessions.not_after IS 'Auth: Not after is a nullable column that contains a timestamp after which the session should be regarded as expired.';


--
-- Name: COLUMN sessions.refresh_token_hmac_key; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.sessions.refresh_token_hmac_key IS 'Holds a HMAC-SHA256 key used to sign refresh tokens for this session.';


--
-- Name: COLUMN sessions.refresh_token_counter; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.sessions.refresh_token_counter IS 'Holds the ID (counter) of the last issued refresh token.';


--
-- Name: sso_domains; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.sso_domains (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    domain text NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    CONSTRAINT "domain not empty" CHECK ((char_length(domain) > 0))
);


--
-- Name: TABLE sso_domains; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.sso_domains IS 'Auth: Manages SSO email address domain mapping to an SSO Identity Provider.';


--
-- Name: sso_providers; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.sso_providers (
    id uuid NOT NULL,
    resource_id text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    disabled boolean,
    CONSTRAINT "resource_id not empty" CHECK (((resource_id = NULL::text) OR (char_length(resource_id) > 0)))
);


--
-- Name: TABLE sso_providers; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.sso_providers IS 'Auth: Manages SSO identity provider information; see saml_providers for SAML.';


--
-- Name: COLUMN sso_providers.resource_id; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.sso_providers.resource_id IS 'Auth: Uniquely identifies a SSO provider according to a user-chosen resource ID (case insensitive), useful in infrastructure as code.';


--
-- Name: users; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.users (
    instance_id uuid,
    id uuid NOT NULL,
    aud character varying(255),
    role character varying(255),
    email character varying(255),
    encrypted_password character varying(255),
    email_confirmed_at timestamp with time zone,
    invited_at timestamp with time zone,
    confirmation_token character varying(255),
    confirmation_sent_at timestamp with time zone,
    recovery_token character varying(255),
    recovery_sent_at timestamp with time zone,
    email_change_token_new character varying(255),
    email_change character varying(255),
    email_change_sent_at timestamp with time zone,
    last_sign_in_at timestamp with time zone,
    raw_app_meta_data jsonb,
    raw_user_meta_data jsonb,
    is_super_admin boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    phone text DEFAULT NULL::character varying,
    phone_confirmed_at timestamp with time zone,
    phone_change text DEFAULT ''::character varying,
    phone_change_token character varying(255) DEFAULT ''::character varying,
    phone_change_sent_at timestamp with time zone,
    confirmed_at timestamp with time zone GENERATED ALWAYS AS (LEAST(email_confirmed_at, phone_confirmed_at)) STORED,
    email_change_token_current character varying(255) DEFAULT ''::character varying,
    email_change_confirm_status smallint DEFAULT 0,
    banned_until timestamp with time zone,
    reauthentication_token character varying(255) DEFAULT ''::character varying,
    reauthentication_sent_at timestamp with time zone,
    is_sso_user boolean DEFAULT false NOT NULL,
    deleted_at timestamp with time zone,
    is_anonymous boolean DEFAULT false NOT NULL,
    CONSTRAINT users_email_change_confirm_status_check CHECK (((email_change_confirm_status >= 0) AND (email_change_confirm_status <= 2)))
);


--
-- Name: TABLE users; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.users IS 'Auth: Stores user login data within a secure schema.';


--
-- Name: COLUMN users.is_sso_user; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.users.is_sso_user IS 'Auth: Set this column to true when the account comes from SSO. These accounts can have duplicate emails.';


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    user_id uuid,
    table_name character varying(100) NOT NULL,
    record_id character varying(50),
    action character varying(20) NOT NULL,
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT audit_log_action_check CHECK (((action)::text = ANY ((ARRAY['INSERT'::character varying, 'UPDATE'::character varying, 'DELETE'::character varying])::text[])))
);


--
-- Name: TABLE audit_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.audit_log IS 'System audit trail for all data modifications';


--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: schedule_capacity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_capacity (
    id integer NOT NULL,
    schedule_id character varying(20) NOT NULL,
    schedule_date date NOT NULL,
    train_id character varying(20),
    model_id character varying(10),
    allocation_status character varying(20) DEFAULT 'Provisional'::character varying NOT NULL,
    planned_first_class_seats integer DEFAULT 0,
    planned_second_class_seats integer DEFAULT 0,
    planned_third_class_seats integer DEFAULT 0,
    planned_first_class_compartments integer DEFAULT 0,
    planned_second_class_compartments integer DEFAULT 0,
    planned_third_class_compartments integer DEFAULT 0,
    allocated_first_class_compartments integer DEFAULT 0,
    allocated_second_class_compartments integer DEFAULT 0,
    allocated_third_class_compartments integer DEFAULT 0,
    allocated_first_class_seats integer DEFAULT 0,
    allocated_second_class_seats integer DEFAULT 0,
    allocated_third_class_seats integer DEFAULT 0,
    booked_first_class integer DEFAULT 0,
    booked_second_class integer DEFAULT 0,
    booked_third_class integer DEFAULT 0,
    total_bookings integer DEFAULT 0,
    confirmed_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_bookings_not_exceed_capacity CHECK (((((allocation_status)::text = 'Provisional'::text) AND (booked_first_class <= planned_first_class_seats) AND (booked_second_class <= planned_second_class_seats) AND (booked_third_class <= planned_third_class_seats)) OR (((allocation_status)::text = ANY ((ARRAY['Confirmed'::character varying, 'Completed'::character varying])::text[])) AND (booked_first_class <= allocated_first_class_seats) AND (booked_second_class <= allocated_second_class_seats) AND (booked_third_class <= allocated_third_class_seats)) OR ((allocation_status)::text = 'Cancelled'::text))),
    CONSTRAINT schedule_capacity_allocated_first_class_compartments_check CHECK ((allocated_first_class_compartments >= 0)),
    CONSTRAINT schedule_capacity_allocated_first_class_seats_check CHECK ((allocated_first_class_seats >= 0)),
    CONSTRAINT schedule_capacity_allocated_second_class_compartments_check CHECK ((allocated_second_class_compartments >= 0)),
    CONSTRAINT schedule_capacity_allocated_second_class_seats_check CHECK ((allocated_second_class_seats >= 0)),
    CONSTRAINT schedule_capacity_allocated_third_class_compartments_check CHECK ((allocated_third_class_compartments >= 0)),
    CONSTRAINT schedule_capacity_allocated_third_class_seats_check CHECK ((allocated_third_class_seats >= 0)),
    CONSTRAINT schedule_capacity_allocation_status_check CHECK (((allocation_status)::text = ANY ((ARRAY['Provisional'::character varying, 'Confirmed'::character varying, 'Completed'::character varying, 'Cancelled'::character varying])::text[]))),
    CONSTRAINT schedule_capacity_booked_first_class_check CHECK ((booked_first_class >= 0)),
    CONSTRAINT schedule_capacity_booked_second_class_check CHECK ((booked_second_class >= 0)),
    CONSTRAINT schedule_capacity_booked_third_class_check CHECK ((booked_third_class >= 0)),
    CONSTRAINT schedule_capacity_planned_first_class_compartments_check CHECK ((planned_first_class_compartments >= 0)),
    CONSTRAINT schedule_capacity_planned_first_class_seats_check CHECK ((planned_first_class_seats >= 0)),
    CONSTRAINT schedule_capacity_planned_second_class_compartments_check CHECK ((planned_second_class_compartments >= 0)),
    CONSTRAINT schedule_capacity_planned_second_class_seats_check CHECK ((planned_second_class_seats >= 0)),
    CONSTRAINT schedule_capacity_planned_third_class_compartments_check CHECK ((planned_third_class_compartments >= 0)),
    CONSTRAINT schedule_capacity_planned_third_class_seats_check CHECK ((planned_third_class_seats >= 0)),
    CONSTRAINT schedule_capacity_total_bookings_check CHECK ((total_bookings >= 0))
);


--
-- Name: TABLE schedule_capacity; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.schedule_capacity IS 'Capacity tracking for advance bookings and train allocation management';


--
-- Name: COLUMN schedule_capacity.schedule_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.schedule_capacity.schedule_id IS 'Reference to train_schedules.train_schedule_id';


--
-- Name: COLUMN schedule_capacity.schedule_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.schedule_capacity.schedule_date IS 'Specific date this schedule operates';


--
-- Name: COLUMN schedule_capacity.allocation_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.schedule_capacity.allocation_status IS 'Provisional = estimated capacity for advance bookings, Confirmed = train assigned with actual capacity, Completed = schedule finished, Cancelled = schedule cancelled';


--
-- Name: COLUMN schedule_capacity.planned_first_class_seats; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.schedule_capacity.planned_first_class_seats IS 'Estimated/default seat capacity used for advance bookings (before train assignment)';


--
-- Name: COLUMN schedule_capacity.allocated_first_class_seats; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.schedule_capacity.allocated_first_class_seats IS 'Actual seat capacity after train assignment confirmation (24-48h before departure)';


--
-- Name: COLUMN schedule_capacity.booked_first_class; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.schedule_capacity.booked_first_class IS 'Total bookings across entire schedule (sum of all segment peaks)';


--
-- Name: train_routes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.train_routes (
    route_id character varying(10) NOT NULL,
    route_name character varying(255) NOT NULL,
    route character varying(500) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE train_routes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.train_routes IS 'Defined train routes with descriptions';


--
-- Name: COLUMN train_routes.route_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_routes.route_id IS 'Unique route identifier (e.g., R01, R02)';


--
-- Name: COLUMN train_routes.route_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_routes.route_name IS 'Name of the route (e.g., Main Line)';


--
-- Name: COLUMN train_routes.route; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_routes.route IS 'Full route description (e.g., Colombo Fort To Badulla)';


--
-- Name: train_schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.train_schedules (
    train_schedule_id character varying(20) NOT NULL,
    route_id character varying(10) NOT NULL,
    train_schedule character varying(255) NOT NULL,
    origin_station_id character varying(10) NOT NULL,
    origin_station character varying(255) NOT NULL,
    origin_departure time without time zone NOT NULL,
    destination_station_id character varying(10) NOT NULL,
    destination_station character varying(255) NOT NULL,
    destination_departure time without time zone NOT NULL,
    monday boolean DEFAULT false,
    tuesday boolean DEFAULT false,
    wednesday boolean DEFAULT false,
    thursday boolean DEFAULT false,
    friday boolean DEFAULT false,
    saturday boolean DEFAULT false,
    sunday boolean DEFAULT false,
    poya_day boolean DEFAULT false,
    holiday boolean DEFAULT false,
    status public.schedule_status DEFAULT 'Active'::public.schedule_status NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_at_least_one_day CHECK ((monday OR tuesday OR wednesday OR thursday OR friday OR saturday OR sunday OR poya_day OR holiday)),
    CONSTRAINT chk_different_stations CHECK (((origin_station_id)::text <> (destination_station_id)::text))
);


--
-- Name: TABLE train_schedules; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.train_schedules IS 'Master schedule of train services with operational days';


--
-- Name: COLUMN train_schedules.train_schedule_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_schedules.train_schedule_id IS 'Unique schedule identifier (e.g., SCH1001)';


--
-- Name: COLUMN train_schedules.train_schedule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_schedules.train_schedule IS 'Human-readable schedule name';


--
-- Name: COLUMN train_schedules.origin_departure; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_schedules.origin_departure IS 'Departure time from origin station';


--
-- Name: COLUMN train_schedules.destination_departure; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_schedules.destination_departure IS 'Departure time from final station (for return calculation)';


--
-- Name: capacity_analytics; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.capacity_analytics AS
 SELECT sc.schedule_date,
    sc.schedule_id,
    ts.train_schedule,
    ts.route_id,
    tr.route_name,
    sc.allocation_status,
    sc.train_id,
    sc.allocated_first_class_seats AS first_class_capacity,
    sc.booked_first_class AS first_class_booked,
    (sc.allocated_first_class_seats - sc.booked_first_class) AS first_class_available,
        CASE
            WHEN (sc.allocated_first_class_seats > 0) THEN round((((sc.booked_first_class)::numeric / (sc.allocated_first_class_seats)::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS first_class_utilization_pct,
    sc.allocated_second_class_seats AS second_class_capacity,
    sc.booked_second_class AS second_class_booked,
    (sc.allocated_second_class_seats - sc.booked_second_class) AS second_class_available,
        CASE
            WHEN (sc.allocated_second_class_seats > 0) THEN round((((sc.booked_second_class)::numeric / (sc.allocated_second_class_seats)::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS second_class_utilization_pct,
    sc.allocated_third_class_seats AS third_class_capacity,
    sc.booked_third_class AS third_class_booked,
    (sc.allocated_third_class_seats - sc.booked_third_class) AS third_class_available,
        CASE
            WHEN (sc.allocated_third_class_seats > 0) THEN round((((sc.booked_third_class)::numeric / (sc.allocated_third_class_seats)::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS third_class_utilization_pct,
    ((sc.allocated_first_class_seats + sc.allocated_second_class_seats) + sc.allocated_third_class_seats) AS total_capacity,
    sc.total_bookings,
        CASE
            WHEN (((sc.allocated_first_class_seats + sc.allocated_second_class_seats) + sc.allocated_third_class_seats) > 0) THEN round((((sc.total_bookings)::numeric / (((sc.allocated_first_class_seats + sc.allocated_second_class_seats) + sc.allocated_third_class_seats))::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS overall_utilization_pct
   FROM ((public.schedule_capacity sc
     JOIN public.train_schedules ts ON (((sc.schedule_id)::text = (ts.train_schedule_id)::text)))
     JOIN public.train_routes tr ON (((ts.route_id)::text = (tr.route_id)::text)))
  WHERE ((sc.allocation_status)::text = ANY ((ARRAY['Provisional'::character varying, 'Confirmed'::character varying, 'Completed'::character varying])::text[]));


--
-- Name: VIEW capacity_analytics; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.capacity_analytics IS 'Detailed capacity and utilization analytics per schedule and date';


--
-- Name: default_schedule_capacity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.default_schedule_capacity (
    id integer NOT NULL,
    train_schedule_id character varying(20) NOT NULL,
    route_id character varying(10),
    first_class_compartments integer DEFAULT 0,
    seating_passengers_per_first_class integer DEFAULT 0,
    standing_passengers_per_first_class integer DEFAULT 0,
    second_class_compartments integer DEFAULT 0,
    seating_passengers_per_second_class integer DEFAULT 0,
    standing_passengers_per_second_class integer DEFAULT 0,
    third_class_compartments integer DEFAULT 0,
    seating_passengers_per_third_class integer DEFAULT 0,
    standing_passengers_per_third_class integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT default_schedule_capacity_first_class_compartments_check CHECK ((first_class_compartments >= 0)),
    CONSTRAINT default_schedule_capacity_seating_passengers_per_first_cl_check CHECK ((seating_passengers_per_first_class >= 0)),
    CONSTRAINT default_schedule_capacity_seating_passengers_per_second_c_check CHECK ((seating_passengers_per_second_class >= 0)),
    CONSTRAINT default_schedule_capacity_seating_passengers_per_third_cl_check CHECK ((seating_passengers_per_third_class >= 0)),
    CONSTRAINT default_schedule_capacity_second_class_compartments_check CHECK ((second_class_compartments >= 0)),
    CONSTRAINT default_schedule_capacity_standing_passengers_per_first_c_check CHECK ((standing_passengers_per_first_class >= 0)),
    CONSTRAINT default_schedule_capacity_standing_passengers_per_second__check CHECK ((standing_passengers_per_second_class >= 0)),
    CONSTRAINT default_schedule_capacity_standing_passengers_per_third_c_check CHECK ((standing_passengers_per_third_class >= 0)),
    CONSTRAINT default_schedule_capacity_third_class_compartments_check CHECK ((third_class_compartments >= 0))
);


--
-- Name: TABLE default_schedule_capacity; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.default_schedule_capacity IS 'Default capacity configuration for each specific train schedule. Used for planned seat allocation and initial capacity setup before actual train assignment.';


--
-- Name: COLUMN default_schedule_capacity.train_schedule_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.default_schedule_capacity.train_schedule_id IS 'References a specific train schedule (e.g. SCH1001, SCH1002). Each schedule has one default capacity record.';


--
-- Name: COLUMN default_schedule_capacity.seating_passengers_per_first_class; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.default_schedule_capacity.seating_passengers_per_first_class IS 'Number of seated passengers per first class compartment';


--
-- Name: COLUMN default_schedule_capacity.standing_passengers_per_first_class; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.default_schedule_capacity.standing_passengers_per_first_class IS 'Number of standing passengers per first class compartment (usually 0 for first class)';


--
-- Name: default_schedule_capacity_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.default_schedule_capacity_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: default_schedule_capacity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.default_schedule_capacity_id_seq OWNED BY public.default_schedule_capacity.id;


--
-- Name: operational_trains; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.operational_trains (
    train_id character varying(20) NOT NULL,
    model_id character varying(10) NOT NULL,
    compartments_per_unit integer NOT NULL,
    status public.train_status DEFAULT 'Active'::public.train_status NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT operational_trains_compartments_per_unit_check CHECK ((compartments_per_unit > 0))
);


--
-- Name: TABLE operational_trains; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.operational_trains IS 'Individual train units in the operational fleet';


--
-- Name: COLUMN operational_trains.train_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.operational_trains.train_id IS 'Unique train identifier (e.g., S14-01, S14-02)';


--
-- Name: COLUMN operational_trains.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.operational_trains.status IS 'Current operational status of the train';


--
-- Name: passenger_demand_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.passenger_demand_history (
    id integer NOT NULL,
    date date NOT NULL,
    schedule_id character varying(20) NOT NULL,
    route_id character varying(10) NOT NULL,
    train_id character varying(20),
    total_passengers integer NOT NULL,
    first_class_passengers integer DEFAULT 0,
    second_class_passengers integer DEFAULT 0,
    third_class_passengers integer DEFAULT 0,
    total_capacity integer NOT NULL,
    load_factor numeric(5,2),
    revenue numeric(12,2),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT passenger_demand_history_first_class_passengers_check CHECK ((first_class_passengers >= 0)),
    CONSTRAINT passenger_demand_history_load_factor_check CHECK (((load_factor >= (0)::numeric) AND (load_factor <= (100)::numeric))),
    CONSTRAINT passenger_demand_history_revenue_check CHECK ((revenue >= (0)::numeric)),
    CONSTRAINT passenger_demand_history_second_class_passengers_check CHECK ((second_class_passengers >= 0)),
    CONSTRAINT passenger_demand_history_third_class_passengers_check CHECK ((third_class_passengers >= 0)),
    CONSTRAINT passenger_demand_history_total_capacity_check CHECK ((total_capacity > 0)),
    CONSTRAINT passenger_demand_history_total_passengers_check CHECK ((total_passengers >= 0))
);


--
-- Name: TABLE passenger_demand_history; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.passenger_demand_history IS 'Historical passenger demand data for forecasting and analytics';


--
-- Name: COLUMN passenger_demand_history.load_factor; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.passenger_demand_history.load_factor IS 'Percentage of capacity utilized (0-100)';


--
-- Name: passenger_demand_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.passenger_demand_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: passenger_demand_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.passenger_demand_history_id_seq OWNED BY public.passenger_demand_history.id;


--
-- Name: schedule_capacity_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.schedule_capacity_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: schedule_capacity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.schedule_capacity_id_seq OWNED BY public.schedule_capacity.id;


--
-- Name: segment_capacity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.segment_capacity (
    id integer NOT NULL,
    schedule_capacity_id integer NOT NULL,
    schedule_id character varying(20) NOT NULL,
    schedule_date date NOT NULL,
    segment_order integer NOT NULL,
    origin_station_id character varying(10) NOT NULL,
    origin_station character varying(255) NOT NULL,
    destination_station_id character varying(10) NOT NULL,
    destination_station character varying(255) NOT NULL,
    first_class_load integer DEFAULT 0,
    second_class_load integer DEFAULT 0,
    third_class_load integer DEFAULT 0,
    total_load integer DEFAULT 0,
    max_first_class integer DEFAULT 0 NOT NULL,
    max_second_class integer DEFAULT 0 NOT NULL,
    max_third_class integer DEFAULT 0 NOT NULL,
    max_total integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_different_segment_stations CHECK (((origin_station_id)::text <> (destination_station_id)::text)),
    CONSTRAINT chk_load_not_exceed_max CHECK (((first_class_load <= max_first_class) AND (second_class_load <= max_second_class) AND (third_class_load <= max_third_class) AND (total_load <= max_total))),
    CONSTRAINT chk_total_load_matches_sum CHECK ((total_load = ((first_class_load + second_class_load) + third_class_load))),
    CONSTRAINT segment_capacity_first_class_load_check CHECK ((first_class_load >= 0)),
    CONSTRAINT segment_capacity_max_first_class_check CHECK ((max_first_class >= 0)),
    CONSTRAINT segment_capacity_max_second_class_check CHECK ((max_second_class >= 0)),
    CONSTRAINT segment_capacity_max_third_class_check CHECK ((max_third_class >= 0)),
    CONSTRAINT segment_capacity_max_total_check CHECK ((max_total >= 0)),
    CONSTRAINT segment_capacity_second_class_load_check CHECK ((second_class_load >= 0)),
    CONSTRAINT segment_capacity_segment_order_check CHECK ((segment_order > 0)),
    CONSTRAINT segment_capacity_third_class_load_check CHECK ((third_class_load >= 0)),
    CONSTRAINT segment_capacity_total_load_check CHECK ((total_load >= 0))
);


--
-- Name: TABLE segment_capacity; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.segment_capacity IS 'Track passenger load per route segment (station-to-station) to prevent overbooking on overlapping routes';


--
-- Name: COLUMN segment_capacity.segment_order; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.segment_capacity.segment_order IS 'Sequential order of segment in the full route (1, 2, 3...) for route A-B-C-D: 1=A-B, 2=B-C, 3=C-D';


--
-- Name: COLUMN segment_capacity.first_class_load; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.segment_capacity.first_class_load IS 'Current number of first class passengers ON the train during this segment';


--
-- Name: COLUMN segment_capacity.max_first_class; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.segment_capacity.max_first_class IS 'Maximum first class capacity: compartments × (seating_passengers + standing_passengers)';


--
-- Name: segment_capacity_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.segment_capacity_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: segment_capacity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.segment_capacity_id_seq OWNED BY public.segment_capacity.id;


--
-- Name: segment_load_analysis; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.segment_load_analysis AS
 SELECT seg.schedule_id,
    seg.schedule_date,
    ts.train_schedule,
    seg.segment_order,
    seg.origin_station,
    seg.destination_station,
    seg.first_class_load,
    seg.max_first_class,
    (seg.max_first_class - seg.first_class_load) AS first_class_available,
        CASE
            WHEN (seg.max_first_class > 0) THEN round((((seg.first_class_load)::numeric / (seg.max_first_class)::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS first_class_utilization_pct,
    seg.second_class_load,
    seg.max_second_class,
    (seg.max_second_class - seg.second_class_load) AS second_class_available,
        CASE
            WHEN (seg.max_second_class > 0) THEN round((((seg.second_class_load)::numeric / (seg.max_second_class)::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS second_class_utilization_pct,
    seg.third_class_load,
    seg.max_third_class,
    (seg.max_third_class - seg.third_class_load) AS third_class_available,
        CASE
            WHEN (seg.max_third_class > 0) THEN round((((seg.third_class_load)::numeric / (seg.max_third_class)::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS third_class_utilization_pct,
    seg.total_load,
    seg.max_total,
    (seg.max_total - seg.total_load) AS total_available,
        CASE
            WHEN (seg.max_total > 0) THEN round((((seg.total_load)::numeric / (seg.max_total)::numeric) * (100)::numeric), 2)
            ELSE (0)::numeric
        END AS overall_utilization_pct
   FROM (public.segment_capacity seg
     JOIN public.train_schedules ts ON (((seg.schedule_id)::text = (ts.train_schedule_id)::text)))
  ORDER BY seg.schedule_date, seg.schedule_id, seg.segment_order;


--
-- Name: VIEW segment_load_analysis; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.segment_load_analysis IS 'Detailed segment-by-segment load analysis showing bottlenecks';


--
-- Name: tickets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tickets (
    ticket_id character varying(20) NOT NULL,
    nic character varying(20),
    passport character varying(20),
    is_child boolean DEFAULT false,
    contact_number character varying(20),
    schedule_id character varying(20),
    origin_station_id character varying(10),
    destination_station_id character varying(10),
    origin_departure time without time zone,
    destination_departure time without time zone,
    schedule_date date,
    class public.train_class,
    fee numeric(10,2),
    payment_method public.payment_method,
    payment_status public.payment_status DEFAULT 'Pending'::public.payment_status NOT NULL,
    issue_date date,
    status public.ticket_status DEFAULT 'Pending'::public.ticket_status NOT NULL,
    booking_platform public.booking_platform,
    issued_by character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_passenger_id CHECK (((nic IS NOT NULL) OR (passport IS NOT NULL))),
    CONSTRAINT chk_schedule_date_after_issue CHECK (((schedule_date IS NULL) OR (issue_date IS NULL) OR (schedule_date >= issue_date))),
    CONSTRAINT tickets_fee_check CHECK ((fee >= (0)::numeric))
);


--
-- Name: TABLE tickets; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tickets IS 'Issued passenger tickets';


--
-- Name: COLUMN tickets.nic; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tickets.nic IS 'National Identity Card number (Sri Lankan passengers)';


--
-- Name: COLUMN tickets.passport; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tickets.passport IS 'Passport number (foreign passengers)';


--
-- Name: COLUMN tickets.is_child; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tickets.is_child IS 'Whether this is a child ticket (discounted)';


--
-- Name: COLUMN tickets.schedule_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tickets.schedule_date IS 'Date of travel';


--
-- Name: ticket_sales_summary; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.ticket_sales_summary AS
 SELECT schedule_date,
    schedule_id,
    class,
    count(*) AS tickets_sold,
    sum(fee) AS total_revenue,
    avg(fee) AS avg_ticket_price,
    count(
        CASE
            WHEN is_child THEN 1
            ELSE NULL::integer
        END) AS child_tickets,
    count(
        CASE
            WHEN (NOT is_child) THEN 1
            ELSE NULL::integer
        END) AS adult_tickets
   FROM public.tickets
  WHERE (status <> ALL (ARRAY['Cancelled'::public.ticket_status, 'Refunded'::public.ticket_status]))
  GROUP BY schedule_date, schedule_id, class;


--
-- Name: VIEW ticket_sales_summary; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.ticket_sales_summary IS 'Summary of ticket sales by date, schedule, and class';


--
-- Name: todays_schedule; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.todays_schedule AS
 SELECT sc.id,
    sc.schedule_date AS date,
    sc.schedule_id,
    ts.train_schedule,
    ts.route_id,
    tr.route_name,
    ts.origin_station_id,
    ts.origin_departure,
    ts.destination_station_id,
    ts.destination_departure,
    sc.train_id,
    ot.model_id,
    ot.status AS train_status,
    sc.allocation_status,
    sc.allocated_first_class_compartments AS first_class_compartments,
    sc.allocated_second_class_compartments AS second_class_compartments,
    sc.allocated_third_class_compartments AS third_class_compartments,
    ((sc.allocated_first_class_seats + sc.allocated_second_class_seats) + sc.allocated_third_class_seats) AS total_passengers_per_train,
    sc.booked_first_class,
    sc.booked_second_class,
    sc.booked_third_class,
    sc.total_bookings
   FROM (((public.schedule_capacity sc
     JOIN public.train_schedules ts ON (((sc.schedule_id)::text = (ts.train_schedule_id)::text)))
     JOIN public.train_routes tr ON (((ts.route_id)::text = (tr.route_id)::text)))
     LEFT JOIN public.operational_trains ot ON (((sc.train_id)::text = (ot.train_id)::text)))
  WHERE ((sc.schedule_date = CURRENT_DATE) AND ((sc.allocation_status)::text = ANY ((ARRAY['Confirmed'::character varying, 'Completed'::character varying])::text[])));


--
-- Name: VIEW todays_schedule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.todays_schedule IS 'Complete view of today''s operational schedule with capacity info';


--
-- Name: train_allocation_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.train_allocation_history (
    id integer NOT NULL,
    date date NOT NULL,
    schedule_id character varying(20) NOT NULL,
    train_id character varying(20) NOT NULL,
    model_id character varying(10) NOT NULL,
    first_class_compartments integer NOT NULL,
    second_class_compartments integer NOT NULL,
    third_class_compartments integer NOT NULL,
    allocation_reason text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT train_allocation_history_first_class_compartments_check CHECK ((first_class_compartments >= 0)),
    CONSTRAINT train_allocation_history_second_class_compartments_check CHECK ((second_class_compartments >= 0)),
    CONSTRAINT train_allocation_history_third_class_compartments_check CHECK ((third_class_compartments >= 0))
);


--
-- Name: TABLE train_allocation_history; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.train_allocation_history IS 'Historical train allocation decisions for optimization';


--
-- Name: train_allocation_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.train_allocation_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: train_allocation_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.train_allocation_history_id_seq OWNED BY public.train_allocation_history.id;


--
-- Name: train_models; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.train_models (
    model_id character varying(10) NOT NULL,
    model_name character varying(255) NOT NULL,
    model_type character varying(100) NOT NULL,
    manufacturer character varying(255) NOT NULL,
    country_of_origin character varying(100) NOT NULL,
    operational_units integer NOT NULL,
    compartments_per_unit integer NOT NULL,
    total_compartments_assigned_per_model integer NOT NULL,
    seating_passengers_per_compartment integer NOT NULL,
    standing_passengers_per_compartment integer NOT NULL,
    total_passengers_per_compartment integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    r01 boolean DEFAULT false,
    r02 boolean DEFAULT false,
    r03 boolean DEFAULT false,
    r04 boolean DEFAULT false,
    r05 boolean DEFAULT false,
    r06 boolean DEFAULT false,
    r07 boolean DEFAULT false,
    r08 boolean DEFAULT false,
    r09 boolean DEFAULT false,
    CONSTRAINT train_models_compartments_per_unit_check CHECK ((compartments_per_unit > 0)),
    CONSTRAINT train_models_operational_units_check CHECK ((operational_units >= 0)),
    CONSTRAINT train_models_seating_passengers_per_compartment_check CHECK ((seating_passengers_per_compartment >= 0)),
    CONSTRAINT train_models_standing_passengers_per_compartment_check CHECK ((standing_passengers_per_compartment >= 0)),
    CONSTRAINT train_models_total_compartments_assigned_per_model_check CHECK ((total_compartments_assigned_per_model >= 0)),
    CONSTRAINT train_models_total_passengers_per_compartment_check CHECK ((total_passengers_per_compartment >= 0))
);


--
-- Name: TABLE train_models; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.train_models IS 'Train model specifications and configurations';


--
-- Name: COLUMN train_models.model_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_models.model_id IS 'Unique model identifier (e.g., S14, S13)';


--
-- Name: COLUMN train_models.operational_units; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_models.operational_units IS 'Number of operational units of this model';


--
-- Name: COLUMN train_models.compartments_per_unit; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_models.compartments_per_unit IS 'Number of compartments per train unit';


--
-- Name: COLUMN train_models.seating_passengers_per_compartment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_models.seating_passengers_per_compartment IS 'Seated capacity per compartment';


--
-- Name: COLUMN train_models.standing_passengers_per_compartment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_models.standing_passengers_per_compartment IS 'Standing capacity per compartment';


--
-- Name: train_schedule_by_station; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.train_schedule_by_station (
    id integer NOT NULL,
    train_schedule_id character varying(20) NOT NULL,
    train_schedule character varying(255) NOT NULL,
    origin_station_id character varying(10) NOT NULL,
    origin_station character varying(255) NOT NULL,
    origin_departure time without time zone NOT NULL,
    destination_station_id character varying(10) NOT NULL,
    destination_station character varying(255) NOT NULL,
    destination_departure time without time zone NOT NULL,
    duration interval NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE train_schedule_by_station; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.train_schedule_by_station IS 'Detailed station-by-station timing for each schedule';


--
-- Name: COLUMN train_schedule_by_station.duration; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_schedule_by_station.duration IS 'Travel time between origin and destination stations';


--
-- Name: train_schedule_by_station_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.train_schedule_by_station_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: train_schedule_by_station_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.train_schedule_by_station_id_seq OWNED BY public.train_schedule_by_station.id;


--
-- Name: train_station_ticket_prices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.train_station_ticket_prices (
    id integer NOT NULL,
    origin_station_id character varying(10) NOT NULL,
    destination_station_id character varying(10) NOT NULL,
    distance numeric(10,2) NOT NULL,
    first_class_fee numeric(10,2) DEFAULT 0,
    second_class_fee numeric(10,2) DEFAULT 0,
    third_class_fee numeric(10,2) DEFAULT 0,
    effective_from date DEFAULT CURRENT_DATE NOT NULL,
    effective_to date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_different_price_stations CHECK (((origin_station_id)::text <> (destination_station_id)::text)),
    CONSTRAINT chk_effective_dates CHECK (((effective_to IS NULL) OR (effective_to > effective_from))),
    CONSTRAINT train_station_ticket_prices_distance_check CHECK ((distance >= (0)::numeric)),
    CONSTRAINT train_station_ticket_prices_first_class_fee_check CHECK ((first_class_fee >= (0)::numeric)),
    CONSTRAINT train_station_ticket_prices_second_class_fee_check CHECK ((second_class_fee >= (0)::numeric)),
    CONSTRAINT train_station_ticket_prices_third_class_fee_check CHECK ((third_class_fee >= (0)::numeric))
);


--
-- Name: TABLE train_station_ticket_prices; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.train_station_ticket_prices IS 'Ticket pricing between stations by class';


--
-- Name: COLUMN train_station_ticket_prices.distance; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_station_ticket_prices.distance IS 'Distance in kilometers between stations';


--
-- Name: COLUMN train_station_ticket_prices.effective_from; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_station_ticket_prices.effective_from IS 'Date when this price becomes effective';


--
-- Name: COLUMN train_station_ticket_prices.effective_to; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_station_ticket_prices.effective_to IS 'Date when this price expires (NULL = no expiry)';


--
-- Name: train_station_ticket_prices_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.train_station_ticket_prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: train_station_ticket_prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.train_station_ticket_prices_id_seq OWNED BY public.train_station_ticket_prices.id;


--
-- Name: train_stations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.train_stations (
    station_id character varying(10) NOT NULL,
    station_name character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE train_stations; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.train_stations IS 'All railway stations in the network';


--
-- Name: COLUMN train_stations.station_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_stations.station_id IS 'Unique station identifier (e.g., S01, S02)';


--
-- Name: COLUMN train_stations.station_name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.train_stations.station_name IS 'Full name of the station';


--
-- Name: train_utilization; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.train_utilization AS
 SELECT t.train_id,
    t.model_id,
    tm.model_name,
    t.status,
    count(DISTINCT sc.schedule_date) AS days_operated,
    avg(
        CASE
            WHEN (((sc.allocated_first_class_seats + sc.allocated_second_class_seats) + sc.allocated_third_class_seats) > 0) THEN (((((sc.booked_first_class + sc.booked_second_class) + sc.booked_third_class))::numeric / (((sc.allocated_first_class_seats + sc.allocated_second_class_seats) + sc.allocated_third_class_seats))::numeric) * (100)::numeric)
            ELSE (0)::numeric
        END) AS avg_load_factor,
    sum(pdh.revenue) AS total_revenue
   FROM (((public.operational_trains t
     LEFT JOIN public.train_models tm ON (((t.model_id)::text = (tm.model_id)::text)))
     LEFT JOIN public.schedule_capacity sc ON (((t.train_id)::text = (sc.train_id)::text)))
     LEFT JOIN public.passenger_demand_history pdh ON ((((sc.schedule_id)::text = (pdh.schedule_id)::text) AND (sc.schedule_date = pdh.date))))
  WHERE ((sc.allocation_status)::text = ANY ((ARRAY['Confirmed'::character varying, 'Completed'::character varying])::text[]))
  GROUP BY t.train_id, t.model_id, tm.model_name, t.status;


--
-- Name: VIEW train_utilization; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW public.train_utilization IS 'Train utilization metrics including days operated and load factors';


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_profiles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    contact_number character varying(20),
    role public.user_role DEFAULT 'operator'::public.user_role NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    password_hash text
);


--
-- Name: TABLE user_profiles; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.user_profiles IS 'User account profiles extending Supabase Auth';


--
-- Name: messages; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE realtime.messages (
    topic text NOT NULL,
    extension text NOT NULL,
    payload jsonb,
    event text,
    private boolean DEFAULT false,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    inserted_at timestamp without time zone DEFAULT now() NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL
)
PARTITION BY RANGE (inserted_at);


--
-- Name: schema_migrations; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE realtime.schema_migrations (
    version bigint NOT NULL,
    inserted_at timestamp(0) without time zone
);


--
-- Name: subscription; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE realtime.subscription (
    id bigint NOT NULL,
    subscription_id uuid NOT NULL,
    entity regclass NOT NULL,
    filters realtime.user_defined_filter[] DEFAULT '{}'::realtime.user_defined_filter[] NOT NULL,
    claims jsonb NOT NULL,
    claims_role regrole GENERATED ALWAYS AS (realtime.to_regrole((claims ->> 'role'::text))) STORED NOT NULL,
    created_at timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);


--
-- Name: subscription_id_seq; Type: SEQUENCE; Schema: realtime; Owner: -
--

ALTER TABLE realtime.subscription ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME realtime.subscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: buckets; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.buckets (
    id text NOT NULL,
    name text NOT NULL,
    owner uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    public boolean DEFAULT false,
    avif_autodetection boolean DEFAULT false,
    file_size_limit bigint,
    allowed_mime_types text[],
    owner_id text,
    type storage.buckettype DEFAULT 'STANDARD'::storage.buckettype NOT NULL
);


--
-- Name: COLUMN buckets.owner; Type: COMMENT; Schema: storage; Owner: -
--

COMMENT ON COLUMN storage.buckets.owner IS 'Field is deprecated, use owner_id instead';


--
-- Name: buckets_analytics; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.buckets_analytics (
    id text NOT NULL,
    type storage.buckettype DEFAULT 'ANALYTICS'::storage.buckettype NOT NULL,
    format text DEFAULT 'ICEBERG'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: migrations; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.migrations (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    hash character varying(40) NOT NULL,
    executed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: objects; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.objects (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    bucket_id text,
    name text,
    owner uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_accessed_at timestamp with time zone DEFAULT now(),
    metadata jsonb,
    path_tokens text[] GENERATED ALWAYS AS (string_to_array(name, '/'::text)) STORED,
    version text,
    owner_id text,
    user_metadata jsonb,
    level integer
);


--
-- Name: COLUMN objects.owner; Type: COMMENT; Schema: storage; Owner: -
--

COMMENT ON COLUMN storage.objects.owner IS 'Field is deprecated, use owner_id instead';


--
-- Name: prefixes; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.prefixes (
    bucket_id text NOT NULL,
    name text NOT NULL COLLATE pg_catalog."C",
    level integer GENERATED ALWAYS AS (storage.get_level(name)) STORED NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: s3_multipart_uploads; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.s3_multipart_uploads (
    id text NOT NULL,
    in_progress_size bigint DEFAULT 0 NOT NULL,
    upload_signature text NOT NULL,
    bucket_id text NOT NULL,
    key text NOT NULL COLLATE pg_catalog."C",
    version text NOT NULL,
    owner_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_metadata jsonb
);


--
-- Name: s3_multipart_uploads_parts; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.s3_multipart_uploads_parts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    upload_id text NOT NULL,
    size bigint DEFAULT 0 NOT NULL,
    part_number integer NOT NULL,
    bucket_id text NOT NULL,
    key text NOT NULL COLLATE pg_catalog."C",
    etag text NOT NULL,
    owner_id text,
    version text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('auth.refresh_tokens_id_seq'::regclass);


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: default_schedule_capacity id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.default_schedule_capacity ALTER COLUMN id SET DEFAULT nextval('public.default_schedule_capacity_id_seq'::regclass);


--
-- Name: passenger_demand_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.passenger_demand_history ALTER COLUMN id SET DEFAULT nextval('public.passenger_demand_history_id_seq'::regclass);


--
-- Name: schedule_capacity id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_capacity ALTER COLUMN id SET DEFAULT nextval('public.schedule_capacity_id_seq'::regclass);


--
-- Name: segment_capacity id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.segment_capacity ALTER COLUMN id SET DEFAULT nextval('public.segment_capacity_id_seq'::regclass);


--
-- Name: train_allocation_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_allocation_history ALTER COLUMN id SET DEFAULT nextval('public.train_allocation_history_id_seq'::regclass);


--
-- Name: train_schedule_by_station id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedule_by_station ALTER COLUMN id SET DEFAULT nextval('public.train_schedule_by_station_id_seq'::regclass);


--
-- Name: train_station_ticket_prices id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_station_ticket_prices ALTER COLUMN id SET DEFAULT nextval('public.train_station_ticket_prices_id_seq'::regclass);


--
-- Name: mfa_amr_claims amr_id_pk; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT amr_id_pk PRIMARY KEY (id);


--
-- Name: audit_log_entries audit_log_entries_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.audit_log_entries
    ADD CONSTRAINT audit_log_entries_pkey PRIMARY KEY (id);


--
-- Name: flow_state flow_state_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.flow_state
    ADD CONSTRAINT flow_state_pkey PRIMARY KEY (id);


--
-- Name: identities identities_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_pkey PRIMARY KEY (id);


--
-- Name: identities identities_provider_id_provider_unique; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_provider_id_provider_unique UNIQUE (provider_id, provider);


--
-- Name: instances instances_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.instances
    ADD CONSTRAINT instances_pkey PRIMARY KEY (id);


--
-- Name: mfa_amr_claims mfa_amr_claims_session_id_authentication_method_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT mfa_amr_claims_session_id_authentication_method_pkey UNIQUE (session_id, authentication_method);


--
-- Name: mfa_challenges mfa_challenges_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_challenges
    ADD CONSTRAINT mfa_challenges_pkey PRIMARY KEY (id);


--
-- Name: mfa_factors mfa_factors_last_challenged_at_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_last_challenged_at_key UNIQUE (last_challenged_at);


--
-- Name: mfa_factors mfa_factors_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_pkey PRIMARY KEY (id);


--
-- Name: oauth_authorizations oauth_authorizations_authorization_code_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_authorization_code_key UNIQUE (authorization_code);


--
-- Name: oauth_authorizations oauth_authorizations_authorization_id_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_authorization_id_key UNIQUE (authorization_id);


--
-- Name: oauth_authorizations oauth_authorizations_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_pkey PRIMARY KEY (id);


--
-- Name: oauth_clients oauth_clients_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_clients
    ADD CONSTRAINT oauth_clients_pkey PRIMARY KEY (id);


--
-- Name: oauth_consents oauth_consents_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_pkey PRIMARY KEY (id);


--
-- Name: oauth_consents oauth_consents_user_client_unique; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_user_client_unique UNIQUE (user_id, client_id);


--
-- Name: one_time_tokens one_time_tokens_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.one_time_tokens
    ADD CONSTRAINT one_time_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_token_unique; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_token_unique UNIQUE (token);


--
-- Name: saml_providers saml_providers_entity_id_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_entity_id_key UNIQUE (entity_id);


--
-- Name: saml_providers saml_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_pkey PRIMARY KEY (id);


--
-- Name: saml_relay_states saml_relay_states_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: sso_domains sso_domains_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sso_domains
    ADD CONSTRAINT sso_domains_pkey PRIMARY KEY (id);


--
-- Name: sso_providers sso_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sso_providers
    ADD CONSTRAINT sso_providers_pkey PRIMARY KEY (id);


--
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: default_schedule_capacity default_schedule_capacity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.default_schedule_capacity
    ADD CONSTRAINT default_schedule_capacity_pkey PRIMARY KEY (id);


--
-- Name: default_schedule_capacity default_schedule_capacity_train_schedule_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.default_schedule_capacity
    ADD CONSTRAINT default_schedule_capacity_train_schedule_id_key UNIQUE (train_schedule_id);


--
-- Name: operational_trains operational_trains_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operational_trains
    ADD CONSTRAINT operational_trains_pkey PRIMARY KEY (train_id);


--
-- Name: passenger_demand_history passenger_demand_history_date_schedule_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.passenger_demand_history
    ADD CONSTRAINT passenger_demand_history_date_schedule_id_key UNIQUE (date, schedule_id);


--
-- Name: passenger_demand_history passenger_demand_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.passenger_demand_history
    ADD CONSTRAINT passenger_demand_history_pkey PRIMARY KEY (id);


--
-- Name: schedule_capacity schedule_capacity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_capacity
    ADD CONSTRAINT schedule_capacity_pkey PRIMARY KEY (id);


--
-- Name: schedule_capacity schedule_capacity_schedule_id_schedule_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_capacity
    ADD CONSTRAINT schedule_capacity_schedule_id_schedule_date_key UNIQUE (schedule_id, schedule_date);


--
-- Name: segment_capacity segment_capacity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.segment_capacity
    ADD CONSTRAINT segment_capacity_pkey PRIMARY KEY (id);


--
-- Name: segment_capacity segment_capacity_schedule_capacity_id_origin_station_id_des_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.segment_capacity
    ADD CONSTRAINT segment_capacity_schedule_capacity_id_origin_station_id_des_key UNIQUE (schedule_capacity_id, origin_station_id, destination_station_id);


--
-- Name: segment_capacity segment_capacity_schedule_capacity_id_segment_order_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.segment_capacity
    ADD CONSTRAINT segment_capacity_schedule_capacity_id_segment_order_key UNIQUE (schedule_capacity_id, segment_order);


--
-- Name: tickets tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_pkey PRIMARY KEY (ticket_id);


--
-- Name: train_allocation_history train_allocation_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_allocation_history
    ADD CONSTRAINT train_allocation_history_pkey PRIMARY KEY (id);


--
-- Name: train_models train_models_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_models
    ADD CONSTRAINT train_models_pkey PRIMARY KEY (model_id);


--
-- Name: train_routes train_routes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_routes
    ADD CONSTRAINT train_routes_pkey PRIMARY KEY (route_id);


--
-- Name: train_schedule_by_station train_schedule_by_station_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedule_by_station
    ADD CONSTRAINT train_schedule_by_station_pkey PRIMARY KEY (id);


--
-- Name: train_schedule_by_station train_schedule_by_station_train_schedule_id_origin_station__key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedule_by_station
    ADD CONSTRAINT train_schedule_by_station_train_schedule_id_origin_station__key UNIQUE (train_schedule_id, origin_station_id, destination_station_id);


--
-- Name: train_schedules train_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedules
    ADD CONSTRAINT train_schedules_pkey PRIMARY KEY (train_schedule_id);


--
-- Name: train_station_ticket_prices train_station_ticket_prices_origin_station_id_destination_s_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_station_ticket_prices
    ADD CONSTRAINT train_station_ticket_prices_origin_station_id_destination_s_key UNIQUE (origin_station_id, destination_station_id, effective_from);


--
-- Name: train_station_ticket_prices train_station_ticket_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_station_ticket_prices
    ADD CONSTRAINT train_station_ticket_prices_pkey PRIMARY KEY (id);


--
-- Name: train_stations train_stations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_stations
    ADD CONSTRAINT train_stations_pkey PRIMARY KEY (station_id);


--
-- Name: train_stations train_stations_station_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_stations
    ADD CONSTRAINT train_stations_station_name_key UNIQUE (station_name);


--
-- Name: user_profiles user_profiles_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_email_key UNIQUE (email);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY realtime.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id, inserted_at);


--
-- Name: subscription pk_subscription; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY realtime.subscription
    ADD CONSTRAINT pk_subscription PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY realtime.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: buckets_analytics buckets_analytics_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.buckets_analytics
    ADD CONSTRAINT buckets_analytics_pkey PRIMARY KEY (id);


--
-- Name: buckets buckets_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.buckets
    ADD CONSTRAINT buckets_pkey PRIMARY KEY (id);


--
-- Name: migrations migrations_name_key; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.migrations
    ADD CONSTRAINT migrations_name_key UNIQUE (name);


--
-- Name: migrations migrations_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.migrations
    ADD CONSTRAINT migrations_pkey PRIMARY KEY (id);


--
-- Name: objects objects_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.objects
    ADD CONSTRAINT objects_pkey PRIMARY KEY (id);


--
-- Name: prefixes prefixes_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.prefixes
    ADD CONSTRAINT prefixes_pkey PRIMARY KEY (bucket_id, level, name);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_pkey PRIMARY KEY (id);


--
-- Name: s3_multipart_uploads s3_multipart_uploads_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads
    ADD CONSTRAINT s3_multipart_uploads_pkey PRIMARY KEY (id);


--
-- Name: audit_logs_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX audit_logs_instance_id_idx ON auth.audit_log_entries USING btree (instance_id);


--
-- Name: confirmation_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX confirmation_token_idx ON auth.users USING btree (confirmation_token) WHERE ((confirmation_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: email_change_token_current_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX email_change_token_current_idx ON auth.users USING btree (email_change_token_current) WHERE ((email_change_token_current)::text !~ '^[0-9 ]*$'::text);


--
-- Name: email_change_token_new_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX email_change_token_new_idx ON auth.users USING btree (email_change_token_new) WHERE ((email_change_token_new)::text !~ '^[0-9 ]*$'::text);


--
-- Name: factor_id_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX factor_id_created_at_idx ON auth.mfa_factors USING btree (user_id, created_at);


--
-- Name: flow_state_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX flow_state_created_at_idx ON auth.flow_state USING btree (created_at DESC);


--
-- Name: identities_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX identities_email_idx ON auth.identities USING btree (email text_pattern_ops);


--
-- Name: INDEX identities_email_idx; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON INDEX auth.identities_email_idx IS 'Auth: Ensures indexed queries on the email column';


--
-- Name: identities_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX identities_user_id_idx ON auth.identities USING btree (user_id);


--
-- Name: idx_auth_code; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX idx_auth_code ON auth.flow_state USING btree (auth_code);


--
-- Name: idx_user_id_auth_method; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX idx_user_id_auth_method ON auth.flow_state USING btree (user_id, authentication_method);


--
-- Name: mfa_challenge_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX mfa_challenge_created_at_idx ON auth.mfa_challenges USING btree (created_at DESC);


--
-- Name: mfa_factors_user_friendly_name_unique; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX mfa_factors_user_friendly_name_unique ON auth.mfa_factors USING btree (friendly_name, user_id) WHERE (TRIM(BOTH FROM friendly_name) <> ''::text);


--
-- Name: mfa_factors_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX mfa_factors_user_id_idx ON auth.mfa_factors USING btree (user_id);


--
-- Name: oauth_auth_pending_exp_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_auth_pending_exp_idx ON auth.oauth_authorizations USING btree (expires_at) WHERE (status = 'pending'::auth.oauth_authorization_status);


--
-- Name: oauth_clients_deleted_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_clients_deleted_at_idx ON auth.oauth_clients USING btree (deleted_at);


--
-- Name: oauth_consents_active_client_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_consents_active_client_idx ON auth.oauth_consents USING btree (client_id) WHERE (revoked_at IS NULL);


--
-- Name: oauth_consents_active_user_client_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_consents_active_user_client_idx ON auth.oauth_consents USING btree (user_id, client_id) WHERE (revoked_at IS NULL);


--
-- Name: oauth_consents_user_order_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_consents_user_order_idx ON auth.oauth_consents USING btree (user_id, granted_at DESC);


--
-- Name: one_time_tokens_relates_to_hash_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX one_time_tokens_relates_to_hash_idx ON auth.one_time_tokens USING hash (relates_to);


--
-- Name: one_time_tokens_token_hash_hash_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX one_time_tokens_token_hash_hash_idx ON auth.one_time_tokens USING hash (token_hash);


--
-- Name: one_time_tokens_user_id_token_type_key; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX one_time_tokens_user_id_token_type_key ON auth.one_time_tokens USING btree (user_id, token_type);


--
-- Name: reauthentication_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX reauthentication_token_idx ON auth.users USING btree (reauthentication_token) WHERE ((reauthentication_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: recovery_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX recovery_token_idx ON auth.users USING btree (recovery_token) WHERE ((recovery_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: refresh_tokens_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_instance_id_idx ON auth.refresh_tokens USING btree (instance_id);


--
-- Name: refresh_tokens_instance_id_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_instance_id_user_id_idx ON auth.refresh_tokens USING btree (instance_id, user_id);


--
-- Name: refresh_tokens_parent_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_parent_idx ON auth.refresh_tokens USING btree (parent);


--
-- Name: refresh_tokens_session_id_revoked_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_session_id_revoked_idx ON auth.refresh_tokens USING btree (session_id, revoked);


--
-- Name: refresh_tokens_updated_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_updated_at_idx ON auth.refresh_tokens USING btree (updated_at DESC);


--
-- Name: saml_providers_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX saml_providers_sso_provider_id_idx ON auth.saml_providers USING btree (sso_provider_id);


--
-- Name: saml_relay_states_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX saml_relay_states_created_at_idx ON auth.saml_relay_states USING btree (created_at DESC);


--
-- Name: saml_relay_states_for_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX saml_relay_states_for_email_idx ON auth.saml_relay_states USING btree (for_email);


--
-- Name: saml_relay_states_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX saml_relay_states_sso_provider_id_idx ON auth.saml_relay_states USING btree (sso_provider_id);


--
-- Name: sessions_not_after_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sessions_not_after_idx ON auth.sessions USING btree (not_after DESC);


--
-- Name: sessions_oauth_client_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sessions_oauth_client_id_idx ON auth.sessions USING btree (oauth_client_id);


--
-- Name: sessions_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sessions_user_id_idx ON auth.sessions USING btree (user_id);


--
-- Name: sso_domains_domain_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX sso_domains_domain_idx ON auth.sso_domains USING btree (lower(domain));


--
-- Name: sso_domains_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sso_domains_sso_provider_id_idx ON auth.sso_domains USING btree (sso_provider_id);


--
-- Name: sso_providers_resource_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX sso_providers_resource_id_idx ON auth.sso_providers USING btree (lower(resource_id));


--
-- Name: sso_providers_resource_id_pattern_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sso_providers_resource_id_pattern_idx ON auth.sso_providers USING btree (resource_id text_pattern_ops);


--
-- Name: unique_phone_factor_per_user; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX unique_phone_factor_per_user ON auth.mfa_factors USING btree (user_id, phone);


--
-- Name: user_id_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX user_id_created_at_idx ON auth.sessions USING btree (user_id, created_at);


--
-- Name: users_email_partial_key; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX users_email_partial_key ON auth.users USING btree (email) WHERE (is_sso_user = false);


--
-- Name: INDEX users_email_partial_key; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON INDEX auth.users_email_partial_key IS 'Auth: A partial unique index that applies only when is_sso_user is false';


--
-- Name: users_instance_id_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_instance_id_email_idx ON auth.users USING btree (instance_id, lower((email)::text));


--
-- Name: users_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_instance_id_idx ON auth.users USING btree (instance_id);


--
-- Name: users_is_anonymous_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_is_anonymous_idx ON auth.users USING btree (is_anonymous);


--
-- Name: idx_allocation_history_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_allocation_history_date ON public.train_allocation_history USING btree (date);


--
-- Name: idx_allocation_history_schedule; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_allocation_history_schedule ON public.train_allocation_history USING btree (schedule_id);


--
-- Name: idx_allocation_history_train; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_allocation_history_train ON public.train_allocation_history USING btree (train_id);


--
-- Name: idx_audit_log_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_action ON public.audit_log USING btree (action);


--
-- Name: idx_audit_log_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_created ON public.audit_log USING btree (created_at);


--
-- Name: idx_audit_log_table; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_table ON public.audit_log USING btree (table_name);


--
-- Name: idx_audit_log_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_user ON public.audit_log USING btree (user_id);


--
-- Name: idx_default_capacity_route; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_default_capacity_route ON public.default_schedule_capacity USING btree (route_id);


--
-- Name: idx_default_capacity_schedule; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_default_capacity_schedule ON public.default_schedule_capacity USING btree (train_schedule_id);


--
-- Name: idx_demand_history_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_demand_history_date ON public.passenger_demand_history USING btree (date);


--
-- Name: idx_demand_history_route; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_demand_history_route ON public.passenger_demand_history USING btree (route_id);


--
-- Name: idx_demand_history_schedule; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_demand_history_schedule ON public.passenger_demand_history USING btree (schedule_id);


--
-- Name: idx_demand_history_train; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_demand_history_train ON public.passenger_demand_history USING btree (train_id);


--
-- Name: idx_operational_trains_model; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_operational_trains_model ON public.operational_trains USING btree (model_id);


--
-- Name: idx_operational_trains_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_operational_trains_status ON public.operational_trains USING btree (status);


--
-- Name: idx_schedule_by_station_dest; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_by_station_dest ON public.train_schedule_by_station USING btree (destination_station_id);


--
-- Name: idx_schedule_by_station_origin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_by_station_origin ON public.train_schedule_by_station USING btree (origin_station_id);


--
-- Name: idx_schedule_by_station_schedule; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_by_station_schedule ON public.train_schedule_by_station USING btree (train_schedule_id);


--
-- Name: idx_schedule_capacity_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_capacity_date ON public.schedule_capacity USING btree (schedule_date);


--
-- Name: idx_schedule_capacity_date_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_capacity_date_status ON public.schedule_capacity USING btree (schedule_date, allocation_status);


--
-- Name: idx_schedule_capacity_schedule; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_capacity_schedule ON public.schedule_capacity USING btree (schedule_id);


--
-- Name: idx_schedule_capacity_schedule_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_capacity_schedule_date ON public.schedule_capacity USING btree (schedule_id, schedule_date);


--
-- Name: idx_schedule_capacity_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_capacity_status ON public.schedule_capacity USING btree (allocation_status);


--
-- Name: idx_schedule_capacity_train; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_schedule_capacity_train ON public.schedule_capacity USING btree (train_id);


--
-- Name: idx_segment_capacity_destination; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_segment_capacity_destination ON public.segment_capacity USING btree (destination_station_id);


--
-- Name: idx_segment_capacity_load; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_segment_capacity_load ON public.segment_capacity USING btree (schedule_id, schedule_date, first_class_load, second_class_load, third_class_load);


--
-- Name: idx_segment_capacity_order; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_segment_capacity_order ON public.segment_capacity USING btree (schedule_capacity_id, segment_order);


--
-- Name: idx_segment_capacity_origin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_segment_capacity_origin ON public.segment_capacity USING btree (origin_station_id);


--
-- Name: idx_segment_capacity_schedule_cap; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_segment_capacity_schedule_cap ON public.segment_capacity USING btree (schedule_capacity_id);


--
-- Name: idx_segment_capacity_schedule_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_segment_capacity_schedule_date ON public.segment_capacity USING btree (schedule_id, schedule_date);


--
-- Name: idx_ticket_prices_destination; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ticket_prices_destination ON public.train_station_ticket_prices USING btree (destination_station_id);


--
-- Name: idx_ticket_prices_effective; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ticket_prices_effective ON public.train_station_ticket_prices USING btree (effective_from, effective_to);


--
-- Name: idx_ticket_prices_origin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ticket_prices_origin ON public.train_station_ticket_prices USING btree (origin_station_id);


--
-- Name: idx_tickets_destination; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_destination ON public.tickets USING btree (destination_station_id);


--
-- Name: idx_tickets_issue_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_issue_date ON public.tickets USING btree (issue_date);


--
-- Name: idx_tickets_nic; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_nic ON public.tickets USING btree (nic);


--
-- Name: idx_tickets_origin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_origin ON public.tickets USING btree (origin_station_id);


--
-- Name: idx_tickets_passport; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_passport ON public.tickets USING btree (passport);


--
-- Name: idx_tickets_payment_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_payment_status ON public.tickets USING btree (payment_status);


--
-- Name: idx_tickets_schedule; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_schedule ON public.tickets USING btree (schedule_id);


--
-- Name: idx_tickets_schedule_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_schedule_date ON public.tickets USING btree (schedule_date);


--
-- Name: idx_tickets_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tickets_status ON public.tickets USING btree (status);


--
-- Name: idx_train_models_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_models_name ON public.train_models USING btree (model_name);


--
-- Name: idx_train_models_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_models_type ON public.train_models USING btree (model_type);


--
-- Name: idx_train_routes_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_routes_name ON public.train_routes USING btree (route_name);


--
-- Name: idx_train_schedules_destination; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_schedules_destination ON public.train_schedules USING btree (destination_station_id);


--
-- Name: idx_train_schedules_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_schedules_name ON public.train_schedules USING btree (train_schedule);


--
-- Name: idx_train_schedules_origin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_schedules_origin ON public.train_schedules USING btree (origin_station_id);


--
-- Name: idx_train_schedules_route; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_schedules_route ON public.train_schedules USING btree (route_id);


--
-- Name: idx_train_schedules_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_schedules_status ON public.train_schedules USING btree (status);


--
-- Name: idx_train_stations_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_train_stations_name ON public.train_stations USING btree (station_name);


--
-- Name: idx_user_profiles_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_profiles_email ON public.user_profiles USING btree (email);


--
-- Name: idx_user_profiles_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_profiles_role ON public.user_profiles USING btree (role);


--
-- Name: ix_realtime_subscription_entity; Type: INDEX; Schema: realtime; Owner: -
--

CREATE INDEX ix_realtime_subscription_entity ON realtime.subscription USING btree (entity);


--
-- Name: messages_inserted_at_topic_index; Type: INDEX; Schema: realtime; Owner: -
--

CREATE INDEX messages_inserted_at_topic_index ON ONLY realtime.messages USING btree (inserted_at DESC, topic) WHERE ((extension = 'broadcast'::text) AND (private IS TRUE));


--
-- Name: subscription_subscription_id_entity_filters_key; Type: INDEX; Schema: realtime; Owner: -
--

CREATE UNIQUE INDEX subscription_subscription_id_entity_filters_key ON realtime.subscription USING btree (subscription_id, entity, filters);


--
-- Name: bname; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX bname ON storage.buckets USING btree (name);


--
-- Name: bucketid_objname; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX bucketid_objname ON storage.objects USING btree (bucket_id, name);


--
-- Name: idx_multipart_uploads_list; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX idx_multipart_uploads_list ON storage.s3_multipart_uploads USING btree (bucket_id, key, created_at);


--
-- Name: idx_name_bucket_level_unique; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX idx_name_bucket_level_unique ON storage.objects USING btree (name COLLATE "C", bucket_id, level);


--
-- Name: idx_objects_bucket_id_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX idx_objects_bucket_id_name ON storage.objects USING btree (bucket_id, name COLLATE "C");


--
-- Name: idx_objects_lower_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX idx_objects_lower_name ON storage.objects USING btree ((path_tokens[level]), lower(name) text_pattern_ops, bucket_id, level);


--
-- Name: idx_prefixes_lower_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX idx_prefixes_lower_name ON storage.prefixes USING btree (bucket_id, level, ((string_to_array(name, '/'::text))[level]), lower(name) text_pattern_ops);


--
-- Name: name_prefix_search; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX name_prefix_search ON storage.objects USING btree (name text_pattern_ops);


--
-- Name: objects_bucket_id_level_idx; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX objects_bucket_id_level_idx ON storage.objects USING btree (bucket_id, level, name COLLATE "C");


--
-- Name: default_schedule_capacity update_default_schedule_capacity_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_default_schedule_capacity_timestamp BEFORE UPDATE ON public.default_schedule_capacity FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: passenger_demand_history update_demand_history_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_demand_history_timestamp BEFORE UPDATE ON public.passenger_demand_history FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: operational_trains update_operational_trains_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_operational_trains_timestamp BEFORE UPDATE ON public.operational_trains FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: schedule_capacity update_schedule_capacity_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_schedule_capacity_timestamp BEFORE UPDATE ON public.schedule_capacity FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: segment_capacity update_segment_capacity_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_segment_capacity_timestamp BEFORE UPDATE ON public.segment_capacity FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: train_station_ticket_prices update_ticket_prices_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_ticket_prices_timestamp BEFORE UPDATE ON public.train_station_ticket_prices FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: tickets update_tickets_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_tickets_timestamp BEFORE UPDATE ON public.tickets FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: train_models update_train_models_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_train_models_timestamp BEFORE UPDATE ON public.train_models FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: train_routes update_train_routes_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_train_routes_timestamp BEFORE UPDATE ON public.train_routes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: train_schedule_by_station update_train_schedule_by_station_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_train_schedule_by_station_timestamp BEFORE UPDATE ON public.train_schedule_by_station FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: train_schedules update_train_schedules_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_train_schedules_timestamp BEFORE UPDATE ON public.train_schedules FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: train_stations update_train_stations_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_train_stations_timestamp BEFORE UPDATE ON public.train_stations FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: user_profiles update_user_profiles_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_user_profiles_timestamp BEFORE UPDATE ON public.user_profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: schedule_capacity validate_schedule_capacity_before_insert; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER validate_schedule_capacity_before_insert BEFORE INSERT ON public.schedule_capacity FOR EACH ROW EXECUTE FUNCTION public.validate_schedule_capacity();


--
-- Name: TRIGGER validate_schedule_capacity_before_insert ON schedule_capacity; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TRIGGER validate_schedule_capacity_before_insert ON public.schedule_capacity IS 'Validates that schedule operates on the specified date before creating capacity record';


--
-- Name: subscription tr_check_filters; Type: TRIGGER; Schema: realtime; Owner: -
--

CREATE TRIGGER tr_check_filters BEFORE INSERT OR UPDATE ON realtime.subscription FOR EACH ROW EXECUTE FUNCTION realtime.subscription_check_filters();


--
-- Name: buckets enforce_bucket_name_length_trigger; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER enforce_bucket_name_length_trigger BEFORE INSERT OR UPDATE OF name ON storage.buckets FOR EACH ROW EXECUTE FUNCTION storage.enforce_bucket_name_length();


--
-- Name: objects objects_delete_delete_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER objects_delete_delete_prefix AFTER DELETE ON storage.objects FOR EACH ROW EXECUTE FUNCTION storage.delete_prefix_hierarchy_trigger();


--
-- Name: objects objects_insert_create_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER objects_insert_create_prefix BEFORE INSERT ON storage.objects FOR EACH ROW EXECUTE FUNCTION storage.objects_insert_prefix_trigger();


--
-- Name: objects objects_update_create_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER objects_update_create_prefix BEFORE UPDATE ON storage.objects FOR EACH ROW WHEN (((new.name <> old.name) OR (new.bucket_id <> old.bucket_id))) EXECUTE FUNCTION storage.objects_update_prefix_trigger();


--
-- Name: prefixes prefixes_create_hierarchy; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER prefixes_create_hierarchy BEFORE INSERT ON storage.prefixes FOR EACH ROW WHEN ((pg_trigger_depth() < 1)) EXECUTE FUNCTION storage.prefixes_insert_trigger();


--
-- Name: prefixes prefixes_delete_hierarchy; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER prefixes_delete_hierarchy AFTER DELETE ON storage.prefixes FOR EACH ROW EXECUTE FUNCTION storage.delete_prefix_hierarchy_trigger();


--
-- Name: objects update_objects_updated_at; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER update_objects_updated_at BEFORE UPDATE ON storage.objects FOR EACH ROW EXECUTE FUNCTION storage.update_updated_at_column();


--
-- Name: identities identities_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: mfa_amr_claims mfa_amr_claims_session_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT mfa_amr_claims_session_id_fkey FOREIGN KEY (session_id) REFERENCES auth.sessions(id) ON DELETE CASCADE;


--
-- Name: mfa_challenges mfa_challenges_auth_factor_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_challenges
    ADD CONSTRAINT mfa_challenges_auth_factor_id_fkey FOREIGN KEY (factor_id) REFERENCES auth.mfa_factors(id) ON DELETE CASCADE;


--
-- Name: mfa_factors mfa_factors_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: oauth_authorizations oauth_authorizations_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_client_id_fkey FOREIGN KEY (client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: oauth_authorizations oauth_authorizations_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: oauth_consents oauth_consents_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_client_id_fkey FOREIGN KEY (client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: oauth_consents oauth_consents_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: one_time_tokens one_time_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.one_time_tokens
    ADD CONSTRAINT one_time_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: refresh_tokens refresh_tokens_session_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_session_id_fkey FOREIGN KEY (session_id) REFERENCES auth.sessions(id) ON DELETE CASCADE;


--
-- Name: saml_providers saml_providers_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: saml_relay_states saml_relay_states_flow_state_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_flow_state_id_fkey FOREIGN KEY (flow_state_id) REFERENCES auth.flow_state(id) ON DELETE CASCADE;


--
-- Name: saml_relay_states saml_relay_states_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_oauth_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_oauth_client_id_fkey FOREIGN KEY (oauth_client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: sso_domains sso_domains_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sso_domains
    ADD CONSTRAINT sso_domains_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: audit_log audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_profiles(id) ON DELETE SET NULL;


--
-- Name: default_schedule_capacity default_schedule_capacity_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.default_schedule_capacity
    ADD CONSTRAINT default_schedule_capacity_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.train_routes(route_id) ON DELETE SET NULL;


--
-- Name: default_schedule_capacity default_schedule_capacity_train_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.default_schedule_capacity
    ADD CONSTRAINT default_schedule_capacity_train_schedule_id_fkey FOREIGN KEY (train_schedule_id) REFERENCES public.train_schedules(train_schedule_id) ON DELETE CASCADE;


--
-- Name: operational_trains operational_trains_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operational_trains
    ADD CONSTRAINT operational_trains_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.train_models(model_id) ON DELETE RESTRICT;


--
-- Name: passenger_demand_history passenger_demand_history_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.passenger_demand_history
    ADD CONSTRAINT passenger_demand_history_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.train_routes(route_id) ON DELETE CASCADE;


--
-- Name: passenger_demand_history passenger_demand_history_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.passenger_demand_history
    ADD CONSTRAINT passenger_demand_history_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.train_schedules(train_schedule_id) ON DELETE CASCADE;


--
-- Name: passenger_demand_history passenger_demand_history_train_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.passenger_demand_history
    ADD CONSTRAINT passenger_demand_history_train_id_fkey FOREIGN KEY (train_id) REFERENCES public.operational_trains(train_id) ON DELETE SET NULL;


--
-- Name: schedule_capacity schedule_capacity_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_capacity
    ADD CONSTRAINT schedule_capacity_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.train_models(model_id) ON DELETE SET NULL;


--
-- Name: schedule_capacity schedule_capacity_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_capacity
    ADD CONSTRAINT schedule_capacity_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.train_schedules(train_schedule_id) ON DELETE CASCADE;


--
-- Name: schedule_capacity schedule_capacity_train_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_capacity
    ADD CONSTRAINT schedule_capacity_train_id_fkey FOREIGN KEY (train_id) REFERENCES public.operational_trains(train_id) ON DELETE SET NULL;


--
-- Name: segment_capacity segment_capacity_destination_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.segment_capacity
    ADD CONSTRAINT segment_capacity_destination_station_id_fkey FOREIGN KEY (destination_station_id) REFERENCES public.train_stations(station_id) ON DELETE RESTRICT;


--
-- Name: segment_capacity segment_capacity_origin_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.segment_capacity
    ADD CONSTRAINT segment_capacity_origin_station_id_fkey FOREIGN KEY (origin_station_id) REFERENCES public.train_stations(station_id) ON DELETE RESTRICT;


--
-- Name: segment_capacity segment_capacity_schedule_capacity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.segment_capacity
    ADD CONSTRAINT segment_capacity_schedule_capacity_id_fkey FOREIGN KEY (schedule_capacity_id) REFERENCES public.schedule_capacity(id) ON DELETE CASCADE;


--
-- Name: segment_capacity segment_capacity_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.segment_capacity
    ADD CONSTRAINT segment_capacity_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.train_schedules(train_schedule_id) ON DELETE CASCADE;


--
-- Name: tickets tickets_destination_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_destination_station_id_fkey FOREIGN KEY (destination_station_id) REFERENCES public.train_stations(station_id) ON DELETE SET NULL;


--
-- Name: tickets tickets_origin_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_origin_station_id_fkey FOREIGN KEY (origin_station_id) REFERENCES public.train_stations(station_id) ON DELETE SET NULL;


--
-- Name: tickets tickets_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.train_schedules(train_schedule_id) ON DELETE SET NULL;


--
-- Name: train_allocation_history train_allocation_history_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_allocation_history
    ADD CONSTRAINT train_allocation_history_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.train_models(model_id) ON DELETE CASCADE;


--
-- Name: train_allocation_history train_allocation_history_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_allocation_history
    ADD CONSTRAINT train_allocation_history_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.train_schedules(train_schedule_id) ON DELETE CASCADE;


--
-- Name: train_allocation_history train_allocation_history_train_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_allocation_history
    ADD CONSTRAINT train_allocation_history_train_id_fkey FOREIGN KEY (train_id) REFERENCES public.operational_trains(train_id) ON DELETE CASCADE;


--
-- Name: train_schedule_by_station train_schedule_by_station_destination_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedule_by_station
    ADD CONSTRAINT train_schedule_by_station_destination_station_id_fkey FOREIGN KEY (destination_station_id) REFERENCES public.train_stations(station_id) ON DELETE RESTRICT;


--
-- Name: train_schedule_by_station train_schedule_by_station_origin_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedule_by_station
    ADD CONSTRAINT train_schedule_by_station_origin_station_id_fkey FOREIGN KEY (origin_station_id) REFERENCES public.train_stations(station_id) ON DELETE RESTRICT;


--
-- Name: train_schedule_by_station train_schedule_by_station_train_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedule_by_station
    ADD CONSTRAINT train_schedule_by_station_train_schedule_id_fkey FOREIGN KEY (train_schedule_id) REFERENCES public.train_schedules(train_schedule_id) ON DELETE CASCADE;


--
-- Name: train_schedules train_schedules_destination_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedules
    ADD CONSTRAINT train_schedules_destination_station_id_fkey FOREIGN KEY (destination_station_id) REFERENCES public.train_stations(station_id) ON DELETE RESTRICT;


--
-- Name: train_schedules train_schedules_origin_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedules
    ADD CONSTRAINT train_schedules_origin_station_id_fkey FOREIGN KEY (origin_station_id) REFERENCES public.train_stations(station_id) ON DELETE RESTRICT;


--
-- Name: train_schedules train_schedules_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_schedules
    ADD CONSTRAINT train_schedules_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.train_routes(route_id) ON DELETE RESTRICT;


--
-- Name: train_station_ticket_prices train_station_ticket_prices_destination_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_station_ticket_prices
    ADD CONSTRAINT train_station_ticket_prices_destination_station_id_fkey FOREIGN KEY (destination_station_id) REFERENCES public.train_stations(station_id) ON DELETE RESTRICT;


--
-- Name: train_station_ticket_prices train_station_ticket_prices_origin_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.train_station_ticket_prices
    ADD CONSTRAINT train_station_ticket_prices_origin_station_id_fkey FOREIGN KEY (origin_station_id) REFERENCES public.train_stations(station_id) ON DELETE RESTRICT;


--
-- Name: objects objects_bucketId_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.objects
    ADD CONSTRAINT "objects_bucketId_fkey" FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: prefixes prefixes_bucketId_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.prefixes
    ADD CONSTRAINT "prefixes_bucketId_fkey" FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads s3_multipart_uploads_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads
    ADD CONSTRAINT s3_multipart_uploads_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_upload_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES storage.s3_multipart_uploads(id) ON DELETE CASCADE;


--
-- Name: audit_log_entries; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.audit_log_entries ENABLE ROW LEVEL SECURITY;

--
-- Name: flow_state; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.flow_state ENABLE ROW LEVEL SECURITY;

--
-- Name: identities; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.identities ENABLE ROW LEVEL SECURITY;

--
-- Name: instances; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.instances ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_amr_claims; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.mfa_amr_claims ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_challenges; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.mfa_challenges ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_factors; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.mfa_factors ENABLE ROW LEVEL SECURITY;

--
-- Name: one_time_tokens; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.one_time_tokens ENABLE ROW LEVEL SECURITY;

--
-- Name: refresh_tokens; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.refresh_tokens ENABLE ROW LEVEL SECURITY;

--
-- Name: saml_providers; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.saml_providers ENABLE ROW LEVEL SECURITY;

--
-- Name: saml_relay_states; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.saml_relay_states ENABLE ROW LEVEL SECURITY;

--
-- Name: schema_migrations; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.schema_migrations ENABLE ROW LEVEL SECURITY;

--
-- Name: sessions; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.sessions ENABLE ROW LEVEL SECURITY;

--
-- Name: sso_domains; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.sso_domains ENABLE ROW LEVEL SECURITY;

--
-- Name: sso_providers; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.sso_providers ENABLE ROW LEVEL SECURITY;

--
-- Name: users; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

--
-- Name: default_schedule_capacity Admins full access default capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access default capacity" ON public.default_schedule_capacity TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: train_models Admins full access models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access models" ON public.train_models TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: train_station_ticket_prices Admins full access prices; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access prices" ON public.train_station_ticket_prices TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: train_routes Admins full access routes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access routes" ON public.train_routes TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: train_schedule_by_station Admins full access schedule by station; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access schedule by station" ON public.train_schedule_by_station TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: schedule_capacity Admins full access schedule capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access schedule capacity" ON public.schedule_capacity TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: train_schedules Admins full access schedules; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access schedules" ON public.train_schedules TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: segment_capacity Admins full access segment capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access segment capacity" ON public.segment_capacity TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: train_stations Admins full access stations; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access stations" ON public.train_stations TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: operational_trains Admins full access trains; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Admins full access trains" ON public.operational_trains TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = 'admin'::public.user_role)))));


--
-- Name: default_schedule_capacity Authenticated users can view default capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view default capacity" ON public.default_schedule_capacity FOR SELECT TO authenticated USING (true);


--
-- Name: train_models Authenticated users can view models; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view models" ON public.train_models FOR SELECT TO authenticated USING (true);


--
-- Name: train_station_ticket_prices Authenticated users can view prices; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view prices" ON public.train_station_ticket_prices FOR SELECT TO authenticated USING (true);


--
-- Name: train_routes Authenticated users can view routes; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view routes" ON public.train_routes FOR SELECT TO authenticated USING (true);


--
-- Name: train_schedule_by_station Authenticated users can view schedule by station; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view schedule by station" ON public.train_schedule_by_station FOR SELECT TO authenticated USING (true);


--
-- Name: schedule_capacity Authenticated users can view schedule capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view schedule capacity" ON public.schedule_capacity FOR SELECT TO authenticated USING (true);


--
-- Name: train_schedules Authenticated users can view schedules; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view schedules" ON public.train_schedules FOR SELECT TO authenticated USING (true);


--
-- Name: segment_capacity Authenticated users can view segment capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view segment capacity" ON public.segment_capacity FOR SELECT TO authenticated USING (true);


--
-- Name: train_stations Authenticated users can view stations; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view stations" ON public.train_stations FOR SELECT TO authenticated USING (true);


--
-- Name: tickets Authenticated users can view tickets; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view tickets" ON public.tickets FOR SELECT TO authenticated USING (true);


--
-- Name: operational_trains Authenticated users can view trains; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Authenticated users can view trains" ON public.operational_trains FOR SELECT TO authenticated USING (true);


--
-- Name: tickets Ticket agents can create tickets; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Ticket agents can create tickets" ON public.tickets FOR INSERT TO authenticated WITH CHECK ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = ANY (ARRAY['admin'::public.user_role, 'ticket_agent'::public.user_role, 'operator'::public.user_role]))))));


--
-- Name: schedule_capacity Ticket agents can manage schedule capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Ticket agents can manage schedule capacity" ON public.schedule_capacity FOR INSERT TO authenticated WITH CHECK ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = ANY (ARRAY['admin'::public.user_role, 'ticket_agent'::public.user_role, 'operator'::public.user_role]))))));


--
-- Name: segment_capacity Ticket agents can manage segment capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Ticket agents can manage segment capacity" ON public.segment_capacity TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = ANY (ARRAY['admin'::public.user_role, 'ticket_agent'::public.user_role, 'operator'::public.user_role]))))));


--
-- Name: schedule_capacity Ticket agents can update schedule capacity; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Ticket agents can update schedule capacity" ON public.schedule_capacity FOR UPDATE TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = ANY (ARRAY['admin'::public.user_role, 'ticket_agent'::public.user_role, 'operator'::public.user_role]))))));


--
-- Name: tickets Ticket agents can update tickets; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Ticket agents can update tickets" ON public.tickets FOR UPDATE TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.user_profiles
  WHERE ((user_profiles.id = auth.uid()) AND (user_profiles.role = ANY (ARRAY['admin'::public.user_role, 'ticket_agent'::public.user_role, 'operator'::public.user_role]))))));


--
-- Name: user_profiles Users can update own profile; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can update own profile" ON public.user_profiles FOR UPDATE USING ((auth.uid() = id));


--
-- Name: user_profiles Users can view own profile; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can view own profile" ON public.user_profiles FOR SELECT USING ((auth.uid() = id));


--
-- Name: audit_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.audit_log ENABLE ROW LEVEL SECURITY;

--
-- Name: default_schedule_capacity; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.default_schedule_capacity ENABLE ROW LEVEL SECURITY;

--
-- Name: operational_trains; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.operational_trains ENABLE ROW LEVEL SECURITY;

--
-- Name: passenger_demand_history; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.passenger_demand_history ENABLE ROW LEVEL SECURITY;

--
-- Name: schedule_capacity; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.schedule_capacity ENABLE ROW LEVEL SECURITY;

--
-- Name: segment_capacity; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.segment_capacity ENABLE ROW LEVEL SECURITY;

--
-- Name: tickets; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;

--
-- Name: train_allocation_history; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.train_allocation_history ENABLE ROW LEVEL SECURITY;

--
-- Name: train_models; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.train_models ENABLE ROW LEVEL SECURITY;

--
-- Name: train_routes; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.train_routes ENABLE ROW LEVEL SECURITY;

--
-- Name: train_schedule_by_station; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.train_schedule_by_station ENABLE ROW LEVEL SECURITY;

--
-- Name: train_schedules; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.train_schedules ENABLE ROW LEVEL SECURITY;

--
-- Name: train_station_ticket_prices; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.train_station_ticket_prices ENABLE ROW LEVEL SECURITY;

--
-- Name: train_stations; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.train_stations ENABLE ROW LEVEL SECURITY;

--
-- Name: user_profiles; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

--
-- Name: messages; Type: ROW SECURITY; Schema: realtime; Owner: -
--

ALTER TABLE realtime.messages ENABLE ROW LEVEL SECURITY;

--
-- Name: buckets; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.buckets ENABLE ROW LEVEL SECURITY;

--
-- Name: buckets_analytics; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.buckets_analytics ENABLE ROW LEVEL SECURITY;

--
-- Name: migrations; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.migrations ENABLE ROW LEVEL SECURITY;

--
-- Name: objects; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

--
-- Name: prefixes; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.prefixes ENABLE ROW LEVEL SECURITY;

--
-- Name: s3_multipart_uploads; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.s3_multipart_uploads ENABLE ROW LEVEL SECURITY;

--
-- Name: s3_multipart_uploads_parts; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.s3_multipart_uploads_parts ENABLE ROW LEVEL SECURITY;

--
-- Name: supabase_realtime; Type: PUBLICATION; Schema: -; Owner: -
--

CREATE PUBLICATION supabase_realtime WITH (publish = 'insert, update, delete, truncate');


--
-- Name: issue_graphql_placeholder; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER issue_graphql_placeholder ON sql_drop
         WHEN TAG IN ('DROP EXTENSION')
   EXECUTE FUNCTION extensions.set_graphql_placeholder();


--
-- Name: issue_pg_cron_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER issue_pg_cron_access ON ddl_command_end
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION extensions.grant_pg_cron_access();


--
-- Name: issue_pg_graphql_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER issue_pg_graphql_access ON ddl_command_end
         WHEN TAG IN ('CREATE FUNCTION')
   EXECUTE FUNCTION extensions.grant_pg_graphql_access();


--
-- Name: issue_pg_net_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER issue_pg_net_access ON ddl_command_end
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION extensions.grant_pg_net_access();


--
-- Name: pgrst_ddl_watch; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER pgrst_ddl_watch ON ddl_command_end
   EXECUTE FUNCTION extensions.pgrst_ddl_watch();


--
-- Name: pgrst_drop_watch; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER pgrst_drop_watch ON sql_drop
   EXECUTE FUNCTION extensions.pgrst_drop_watch();


--
-- PostgreSQL database dump complete
--

\unrestrict fpzpQfyiHIq7uwp6H6eiWIqX8bXfaTIvfblISk3YvWpvR99pRroYcsQsUd3bGcq

