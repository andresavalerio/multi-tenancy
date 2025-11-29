-- migrate:up
insert into multitenancy.tenants(id, company_name)
    values
        ('24098e53-f4f4-475f-9e86-6de143168450', 'Company1'),
        ('98edad80-8f7e-4519-8a1c-7c5580789619', 'Company2');

insert into multitenancy.groups(id, group_name)
    values
        ('b5bb8b37-f75e-4687-9c07-4003f7332dce', 'Group1'),
        ('840d370a-8664-4f07-8108-8200e171f3f0', 'Group2');

insert into multitenancy.users(id, email, pwd, pwd_validity) 
    values(
        'd392e8e0-000d-4744-835c-bacec750a962'
        , 'myuser@mail.com'
        , 'teste123'
        , tstzrange(current_timestamp, current_timestamp + (interval '30 days'))
    ),(
        'df0c4eb2-0a9e-4972-a915-c69388ef744c'
        , 'myuser2@mail.com'
        , 'teste123'
        , tstzrange(current_timestamp, current_timestamp + (interval '30 days'))
    );

insert into multitenancy.TenantGroups(tenant_id, group_id)
	values
		('24098e53-f4f4-475f-9e86-6de143168450', 'b5bb8b37-f75e-4687-9c07-4003f7332dce'),
		('98edad80-8f7e-4519-8a1c-7c5580789619', '840d370a-8664-4f07-8108-8200e171f3f0');

insert into multitenancy.GroupUsers(group_id, user_id)
	values
		('b5bb8b37-f75e-4687-9c07-4003f7332dce', 'd392e8e0-000d-4744-835c-bacec750a962'),
		('840d370a-8664-4f07-8108-8200e171f3f0', 'df0c4eb2-0a9e-4972-a915-c69388ef744c');
	

-- migrate:down
truncate multitenancy.GroupUsers;
truncate multitenancy.TenantGroups;

delete from multitenancy.users
    where email in ('myuser@mail.com');

delete from multitenancy.groups
    where group_name in ('Group1', 'Group2');

delete from multitenancy.tenants
    where company_name in ('Company1', 'Company2');
