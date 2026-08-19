-- Database-level invariant assertions. Run as a release gate.
--
-- These enforce two PRD invariants at the schema level rather than in
-- application tests, because a schema-level guarantee cannot be bypassed by a
-- code path added later:
--
--   INV-012 / FR-501  evidentiary records are append-only
--   INV-001 / FR-001  tenant isolation is enforced by row-level security
--
-- Each block is a no-op while the table it guards does not yet exist, so this
-- file is safe to run against an empty database and becomes live as the schema
-- lands.

\set ON_ERROR_STOP on

-- ---------------------------------------------------------------------------
-- INV-012 — no role may hold UPDATE or DELETE on an evidentiary table.
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    evidentiary text[] := ARRAY[
        'jornada',
        'lista_asistencia',
        'movimiento',
        'archivo_idse',
        'salario',
        'desviacion',
        'autorizacion_horas_extra',
        'audit_log'
    ];
    offending text;
BEGIN
    SELECT string_agg(format('%s.%s -> %s (%s)', table_schema, table_name, grantee, privilege_type), E'\n  ')
      INTO offending
      FROM information_schema.role_table_grants
     WHERE table_name = ANY (evidentiary)
       AND privilege_type IN ('UPDATE', 'DELETE');

    IF offending IS NOT NULL THEN
        RAISE EXCEPTION E'INV-012 violated: UPDATE/DELETE granted on evidentiary tables:\n  %', offending;
    END IF;
END $$;

-- ---------------------------------------------------------------------------
-- INV-001 — every tenant table has row-level security enabled AND at least one
-- policy. RLS enabled with no policy denies everything; a policy without RLS
-- enabled is inert. Both are defects, and both are silent.
--
-- A table is considered tenant-scoped if it carries a company identifier
-- column. Control-plane tables legitimately have none and are skipped.
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    missing text;
BEGIN
    SELECT string_agg(format('%s.%s (%s)', t.schemaname, t.tablename,
                             CASE WHEN NOT t.rowsecurity THEN 'RLS disabled'
                                  ELSE 'no policy' END), E'\n  ')
      INTO missing
      FROM pg_tables t
      JOIN information_schema.columns c
        ON c.table_schema = t.schemaname
       AND c.table_name = t.tablename
       AND c.column_name IN ('company_id', 'empresa_id', 'tenant_id')
     WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
       AND (
             NOT t.rowsecurity
             OR NOT EXISTS (
                 SELECT 1 FROM pg_policies p
                  WHERE p.schemaname = t.schemaname
                    AND p.tablename = t.tablename
             )
           );

    IF missing IS NOT NULL THEN
        RAISE EXCEPTION E'INV-001 violated: tenant tables without enforced RLS:\n  %', missing;
    END IF;
END $$;

SELECT 'db invariants OK' AS result;
