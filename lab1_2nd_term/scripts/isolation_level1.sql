begin isolation level read committed;
update appliance set price = 1234 where id = 5000001;

select * from appliance where id = 5000001;
--5000001	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15

commit;
rollback;


begin isolation level repeatable read;
insert into appliance (id, name, brand, price, saler_name, city, publishing_date)
values (5000002, 'Посудомоечная машина', 'LG', 30000, 'Владимир Дмитриев', 'г. Москва', '2025-02-15');

commit;
rollback;


begin isolation level repeatable read;
select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234
update appliance set price = price * 1000  where id = 5000002;
commit;

select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234000

update appliance set price = 1234  where id = 5000001;
update appliance set price = 30000  where id = 5000002;


begin isolation level serializable;
select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234
update appliance set price = price * 1000  where id = 5000002;
commit;

select sum(price) from appliance where id = 5000001 or id = 5000002;
--30001234



