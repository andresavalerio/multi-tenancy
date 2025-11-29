-- migrate:up
create schema application;

create table application.machines(
    macaddr macaddr8 not null,
    ip inet not null,
    os text not null,
    os_ver text not null,
    owner uuid not null,
    last_access timestamp with time zone not null default current_timestamp,
    active boolean not null default true,
    tenant_id uuid not null,
    foreign key (tenant_id) references multitenancy.tenants(id) on delete cascade,
    foreign key (owner) references multitenancy.users(id) on delete cascade,
    primary key(macaddr)
);

insert into application.machines(macaddr, ip, os, os_ver, owner, tenant_id)
    values
        ('19:de:fc:0d:24:9b', '141.121.74.88', 'nixos', '24.05', 'd392e8e0-000d-4744-835c-bacec750a962', '24098e53-f4f4-475f-9e86-6de143168450'),
        ('a3:2e:14:26:e6:88', '185.124.232.12', 'nixos', '23.11', 'df0c4eb2-0a9e-4972-a915-c69388ef744c', '98edad80-8f7e-4519-8a1c-7c5580789619');

-- migrate:down
truncate application.machines;

drop table if exists application.machines;

drop schema application;

