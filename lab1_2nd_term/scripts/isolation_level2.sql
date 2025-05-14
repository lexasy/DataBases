begin isolation level read committed;
select * from appliance where id = 5000001;
--5000001	Посудомоечная машина	LG	33000	Владимир Дмитриев	г. Москва	2025-02-15
--После коммита первой транзакции
--5000001	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15

begin isolation level repeatable read;
select * from appliance where id = 5000001 or 5000002;
--до начала выполнения параллельной транзакции
--5000001	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15
--После коммита первой транзакции
--5000001	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15
--5000002	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15


begin isolation level repeatable read;
select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234
update appliance set price = price * 1000  where id = 5000001;
commit;

select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234000


begin isolation level serializable;
select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234
update appliance set price = price * 1000  where id = 5000001;
commit;
--SQL Error [40001]: ERROR: could not serialize access due to read/write dependencies among transactions
--  Подробности: Reason code: Canceled on identification as a pivot, during commit attempt.
--  Подсказка: The transaction might succeed if retried.
-- избежали несогласованной записи
select sum(price) from appliance where id = 5000001 or id = 5000002;
--30001234
