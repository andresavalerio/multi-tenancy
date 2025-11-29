-- migrate:up
create extension "uuid-ossp";

create schema multitenancy;

create table multitenancy.tenants(
    id uuid not null default gen_random_uuid(),
    company_name text unique not null,
    created_at timestamp with time zone not null default current_timestamp,
    primary key(id)
);

create table multitenancy.groups(
    id uuid not null default gen_random_uuid(),
    group_name text not null,
    primary key(id)
);

create table multitenancy.users(
    id uuid not null default gen_random_uuid(),
    email text not null,
    pwd text not null,
    pwd_validity tstzrange not null,
    primary key(id)
);

create table multitenancy.TenantGroups(
	tenant_id uuid not null,
	group_id uuid not null,
	foreign key (tenant_id) references multitenancy.tenants(id) on delete cascade,
	foreign key (group_id) references multitenancy.groups(id) on delete cascade,
	primary key (tenant_id, group_id)
);

create table multitenancy.GroupUsers(
	group_id uuid not null,
	user_id uuid not null,
	foreign key (group_id) references multitenancy.groups(id) on delete cascade,
	foreign key (user_id) references multitenancy.users(id) on delete cascade,
	primary key (group_id, user_id)
);

-- migrate:down
drop table if exists multitenancy.GroupUsers;
drop table if exists multitenancy.TenantGroups;

drop table if exists multitenancy.users;
drop table if exists multitenancy.groups;
drop table if exists multitenancy.tenants;

drop schema multitenancy;

drop extension "uuid-ossp";