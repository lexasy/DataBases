begin;

insert into appliance (id, name, brand, price, saler_name, city, publishing_date)
values (5000001, 'Посудомоечная машина', 'LG', 30000, 'Владимир Дмитриев', 'г. Москва', '2025-02-15');
update appliance set price = price * 1.1 where name = 'Посудомоечная машина';

commit;
rollback;

do $$
begin
	if exists (select 1 from appliance where id = 5000002) then
		raise exception 'Appliance with id 5000002 already exists!';
	end if;

	insert into appliance (id, name, brand, price, saler_name, city, publishing_date)
	values (5000002, 'Посудомоечная машина', 'LG', 30000, 'Владимир Дмитриев', 'г. Москва', '2025-02-15');
	
end $$;

commit;
rollback;

do $$
begin
	if not exists (select 1 from appliance where id = 5000002) then
		raise exception 'Appliance with id 5000002 not exists!';
	end if;

	delete from appliance where id = 5000002;
	
end $$;

commit;
rollback;


	
