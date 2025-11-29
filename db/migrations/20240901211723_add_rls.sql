-- migrate:up
create role application_user with login password 'mypwd' nobypassrls;

revoke all on schema public from application_user;
revoke all on all tables in schema public from application_user;

grant usage on schema application to application_user;
grant select, insert, update, delete on all tables in schema application to application_user;
grant usage, select, update on all sequences in schema application to application_user;

grant usage on schema multitenancy to application_user;
grant select on all tables in schema multitenancy to application_user;

alter table application.machines enable row level security;

create policy select_machines_isolation_policy
    on application.machines
    as permissive
    for select
    to application_user
    using (tenant_id::text = current_setting('app.current_tenant', true));

create policy insert_machines_isolation_policy
    on application.machines
    as permissive
    for insert
    to application_user
    with check (tenant_id::text = current_setting('app.current_tenant', true));

-- migrate:down
drop policy if exists insert_machines_isolation_policy on application.machines;
drop policy if exists select_machines_isolation_policy on application.machines;

alter table application.machines disable row level security;

revoke usage on schema multitenancy from application_user;
revoke select on all tables in schema multitenancy from application_user;

revoke usage on schema application from application_user;
revoke select, insert, update, delete on all tables in schema application from application_user;
revoke usage, select, update on all sequences in schema application from application_user;

drop role application_user;