# Лабораторная работа №1
### Часть 0: Генерация и загрузка данных
В прошлом семетре темой моей курсовой работы была "Сервис по продаже бытовой техники". После тщетных попыток найти датасет на 5000000 записей по этой теме, я решил сгенерировать данные с помощью языка `Python` и библиотеки `faker`, которая не позволит допустить сезонности и остальные недостатки синтетических данных. По итогу получилась таблица с такими полями:

- `id (BIGINT)` - уникальный идентификатор записи в таблице;
- `name (TEXT)` - наименование бытовой техники, при генерации берется рандомно из набора наименований;
- `brand (TEXT)` - бренд бытовой техники, аналогично наименованию, при генерации рандомно берется из списка брендов;
- `price (BIGINT)` - цена за единицу бытовой техники, при генерации выбирается как рандомное число от 5000 до 200000;
- `saler_name (TEXT)` - ФИО продавца, который продает бытовую технику, генерируется с помощью генерации имен в библиотеке `faker`;
- `city (TEXT)` - город, в котором продается бытовая техника, генерируется с помощью генерации городов в библиотеке `faker`;
- `publishing_date (DATE)` - дата размещения объявления о продаже бытовой техники, генерируется рандомно с помощью библиотеки `faker` из интервала в 2 года от текущей даты.

Процесс генерации можно посмотреть в файле [generator.py](generator.py).
Затем, с помощью библиотеки `sqlalchemy` мы переносим данные из файлов `.csv` в таблицу в базе данных. Процесс загрузки данных можно посмотреть в файле [loader.py](loader.py).
### Часть 1: Индексы
Все, что будет сейчас описано можно посмотреть в файле [idx.sql](scripts/idx.sql).
Для начала опишем необходимые типы индексов и область их применения, а затем перейдем к практике.
**B-TREE** - это самый распространенный тип индекса в PostgreSQL. Он поддерживает все стандартные операции сравнения (>, <, >=, <=, =, <>) и может использоваться с большинством типов данных. B-tree индексы могут быть использованы для сортировки, ограничений уникальности и поиска по диапазону значений.
**GIN** - GIN-индексы применяются для полнотекстового поиска и поиска по массивам, JSON и триграммам. Они обеспечивают высокую производительность при поиске в больших объемах данных.
**BRIN** - BRIN-индексы используются для компактного представления больших объемов данных, особенно когда значения в таблице имеют определенный порядок. Они эффективны для хранения и обработки временных рядов и географических данных.
Без индексов, базе данных приходится выполнять полное сканирование таблицы (sequential scan), чтобы найти нужные данные. Это может быть медленным и ресурсоемким процессом, особенно для больших таблиц. Индексы позволяют существенно ускорить поиск, так как они предоставляют структуру данных, которая указывает на местоположение нужной информации в таблице.
Теперь перейдем к практике. Чтобы отслеживать изменение производительности при запросе, будем использовать планировщик. Итак, первый запрос, выберем технику, которую выложили в определенные промежуток дат:
```sql
explain analyze select * from appliance where publishing_date between '2024-01-01' and '2024-01-31';
```
Получаем вот такой результат:
```
Gather  (cost=1000.00..149914.30 rows=200503 width=121) (actual time=7.318..3373.973 rows=212442 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Seq Scan on appliance  (cost=0.00..128864.00 rows=83543 width=121) (actual time=49.565..2809.035 rows=70814 loops=3)
       Filter: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
       Rows Removed by Filter: 1595853
Planning Time: 0.368 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 3.297 ms (Deform 0.511 ms), Inlining 0.000 ms, Optimization 0.983 ms, Emission 146.994 ms, Total 151.274 ms
Execution Time: 3385.992 ms
```
Видим, что не используются никакие индексы, и идет полное сканирование таблицы, для выявления необходимых данных. Запрос будет выполняться около 3385мс. Теперь попробуем применить индекс `B-TREE` и выполнить тот же запрос:
```sql
create index btree_idx on appliance using btree(publishing_date);
explain analyze select * from appliance where publishing_date between '2024-01-01' and '2024-01-31';
```
Как видно из запроса, мы применяем индекс к колонке `publishing_date`, по которой у нас идет фильтрация в запросе. Потенциально, применение индекса `B-TREE` на этот столбец выглядит логичным, так как мы можем производить операции сравнения над датами. Посмотрим на результат:
```
Gather  (cost=3743.59..142588.26 rows=200503 width=121) (actual time=137.688..5219.189 rows=212442 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Bitmap Heap Scan on appliance  (cost=2743.59..121537.96 rows=83543 width=121) (actual time=49.114..5083.270 rows=70814 loops=3)
       Recheck Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
       Rows Removed by Index Recheck: 537297
       Heap Blocks: exact=19189 lossy=11933
       ->  Bitmap Index Scan on btree_idx  (cost=0.00..2693.46 rows=200503 width=0) (actual time=119.469..119.470 rows=212442 loops=1)
             Index Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
Planning Time: 0.177 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 4.122 ms (Deform 0.381 ms), Inlining 0.000 ms, Optimization 5.834 ms, Emission 19.364 ms, Total 29.320 ms
Execution Time: 5236.771 ms
```
Видим, что при поиске использовался индекс, но при этом мы не получили прироста производительности, а даже наоборот. Это неудивительно, так как индексы не гарантируют стабильный прирост в производительности в любых запросах. Это может зависеть как от самого запроса, так и от распределения данных в таблице и от их количества. Факторов довольно много. Теперь попробуем применить другой тип индексов, а именно `BRIN`. Выполним тот же самый запрос и посмотрим на результат:
```sql
create index brin_idx on appliance using brin(publishing_date);
explain analyze select * from appliance where publishing_date between '2024-01-01' and '2024-01-31';
```
Результат:
```
explain analyze select * from appliance where publishing_date between '2024-01-01' and '2024-01-31';
Gather  (cost=1000.00..149914.30 rows=200503 width=121) (actual time=7.447..3306.761 rows=212442 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Seq Scan on appliance  (cost=0.00..128864.00 rows=83543 width=121) (actual time=33.258..3067.989 rows=70814 loops=3)
       Filter: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
       Rows Removed by Filter: 1595853
Planning Time: 3.393 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 1.273 ms (Deform 0.336 ms), Inlining 0.000 ms, Optimization 0.711 ms, Emission 98.951 ms, Total 100.936 ms
Execution Time: 3318.754 ms
```
И тут, неожиданно, мы видим, что никакой индекс не применился, но почему? Все дело в том, что как описано выше, `BRIN` работает с упорядоченными данными, что в нашей таблице не выполнено. Попробуем создать новую таблицу, которая будет содержать наши упорядоченные по датам данные и посмотрим на результат выполнения запроса без индекса, а потом с индексом:
```sql
create table brin_test as select * from appliance order by publishing_date;
explain analyze select * from brin_test where publishing_date between '2024-01-01' and '2024-01-31';
```
Результат без индекса:
```
Gather  (cost=1000.00..151515.48 rows=215504 width=121) (actual time=1366.847..3471.202 rows=212442 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Seq Scan on brin_test  (cost=0.00..128965.07 rows=89793 width=121) (actual time=1122.486..2443.108 rows=70814 loops=3)
       Filter: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
       Rows Removed by Filter: 1595853
Planning Time: 1.714 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 13.588 ms (Deform 3.166 ms), Inlining 0.000 ms, Optimization 11.542 ms, Emission 64.864 ms, Total 89.995 ms
Execution Time: 3501.486 ms
```
В принципе, ничего не поменялось. Посмотрим как повлияет индекс:
```sql
create index brin_idx on brin_test using brin(publishing_date);
explain analyze select * from brin_test where publishing_date between '2024-01-01' and '2024-01-31';
```
Результат с индексом:
```
Gather  (cost=1070.93..141555.92 rows=215490 width=121) (actual time=11.084..572.383 rows=212442 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Bitmap Heap Scan on brin_test  (cost=70.93..119006.92 rows=89788 width=121) (actual time=5.334..300.581 rows=70814 loops=3)
       Recheck Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
       Rows Removed by Index Recheck: 1265
       Heap Blocks: lossy=2133
       ->  Bitmap Index Scan on brin_idx  (cost=0.00..17.06 rows=215969 width=0) (actual time=0.657..0.659 rows=42240 loops=1)
             Index Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
Planning Time: 0.275 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 1.202 ms (Deform 0.442 ms), Inlining 0.000 ms, Optimization 0.591 ms, Emission 6.924 ms, Total 8.717 ms
Execution Time: 583.268 ms
```
Как мы видим индекс применился, а запрос сработал примерно в 7 раз быстрее. Это значит, что индекс `BRIN` дал прирост производительности на отсортированных данных. Теперь, ради интереса, попробуем применить индекс `B-TREE` еще раз, но только теперь уже на отсортированные данные:
```sql
create index btree_idx on brin_test using btree(publishing_date);
explain analyze select * from brin_test where publishing_date between '2024-01-01' and '2024-01-31';
```
Результат:
```
Index Scan using btree_idx on brin_test  (cost=0.43..9265.23 rows=215490 width=121) (actual time=0.106..25.354 rows=212442 loops=1)
 Index Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
Planning Time: 0.709 ms
Execution Time: 29.475 ms
```
На отсортированных данных индекс `B-TREE` сработал еще быстрее. Я могу лишь предположить, что по отсортированным данным получается строить дерево быстрее, и из за этого, запрос срабатывает так быстро.
Попробуем еще поэкспериментировать с индексом `BTREE` на неупорядоченной таблице. Попробуем применить его на строковый столбец, так как он тоже подвергается операциям сравнения. Выполним такой запрос без индекса:
```sql
explain analyze select * from appliance where name = 'Посудомоечня машина';
```
Результат:
```
Gather  (cost=1000.00..145705.67 rows=210500 width=121) (actual time=7.937..4428.827 rows=208285 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Seq Scan on appliance  (cost=0.00..123655.67 rows=87708 width=121) (actual time=4.292..4139.566 rows=69428 loops=3)
       Filter: (name = 'Посудомоечня машина'::text)
       Rows Removed by Filter: 1597238
Planning Time: 0.884 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 0.628 ms (Deform 0.201 ms), Inlining 0.000 ms, Optimization 0.550 ms, Emission 11.889 ms, Total 13.068 ms
Execution Time: 4525.512 ms
```
Теперь попробуем применить индекс `B-TREE` и посмотрим на изменение производительности:
```sql
create index btree_idx on appliance using btree(name);
explain analyze select * from appliance where name = 'Посудомоечня машина';
```
Результат:
```
Gather  (cost=3367.81..139699.59 rows=210500 width=121) (actual time=61.615..6770.366 rows=208285 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Bitmap Heap Scan on appliance  (cost=2367.81..117649.59 rows=87708 width=121) (actual time=22.049..6567.023 rows=69428 loops=3)
       Recheck Cond: (name = 'Посудомоечня машина'::text)
       Rows Removed by Index Recheck: 537576
       Heap Blocks: exact=19064 lossy=11973
       ->  Bitmap Index Scan on btree_idx  (cost=0.00..2315.18 rows=210500 width=0) (actual time=28.303..28.304 rows=208285 loops=1)
             Index Cond: (name = 'Посудомоечня машина'::text)
Planning Time: 2.222 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 1.686 ms (Deform 0.208 ms), Inlining 0.000 ms, Optimization 9.618 ms, Emission 18.867 ms, Total 30.171 ms
Execution Time: 6840.680 ms
```
Видим, что опять индекс сделал только хуже. Как я уже говорил ранее, причин такого поведения может быть много. Теперь посмотрим, что будет, если применить индекс сразу к двум столбцам, например, к целочисленному и строковому:
```sql
explain analyze select * from appliance where name = 'Посудомоечня машина' and price >= 90000;
```
Результат без индекса:
```
Gather  (cost=1000.00..141741.00 rows=118770 width=121) (actual time=2.753..3418.815 rows=117331 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Seq Scan on appliance  (cost=0.00..128864.00 rows=49488 width=121) (actual time=30.140..3360.463 rows=39110 loops=3)
       Filter: ((price >= 90000) AND (name = 'Посудомоечня машина'::text))
       Rows Removed by Filter: 1627556
Planning Time: 0.105 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 1.119 ms (Deform 0.233 ms), Inlining 0.000 ms, Optimization 0.736 ms, Emission 89.335 ms, Total 91.189 ms
Execution Time: 3426.669 ms
```
Теперь применим индекс:
```sql
create index btree_idx on appliance using btree(name, price);
explain analyze select * from appliance where name = 'Посудомоечня машина' and price >= 90000;
```
Результат с индексом:
```
Gather  (cost=4433.95..136719.05 rows=118770 width=121) (actual time=102.045..8025.154 rows=117331 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Bitmap Heap Scan on appliance  (cost=3433.95..123842.05 rows=49488 width=121) (actual time=35.584..7781.777 rows=39110 loops=3)
       Recheck Cond: ((name = 'Посудомоечня машина'::text) AND (price >= 90000))
       Rows Removed by Index Recheck: 546555
       Heap Blocks: exact=12536 lossy=11568
       ->  Bitmap Index Scan on btree_idx  (cost=0.00..3404.26 rows=118770 width=0) (actual time=25.462..25.462 rows=117331 loops=1)
             Index Cond: ((name = 'Посудомоечня машина'::text) AND (price >= 90000))
Planning Time: 3.231 ms
JIT:
 Functions: 6
 Options: Inlining false, Optimization false, Expressions true, Deforming true
 Timing: Generation 6.890 ms (Deform 0.532 ms), Inlining 0.000 ms, Optimization 11.495 ms, Emission 101.460 ms, Total 119.845 ms
Execution Time: 8046.581 ms
```
И опять индекс все испортил, но при этом видим, что он работает уже с двумя столбцами.
Из экспериментов с `B-TREE` индексом, можно сделать вывод, что не стоит судорожно применять индексы в бд, когда у нее наблюдаются проблемы с производительностью. Стоит поискать причины такого поведения и более надежные способы это исправить.
Перейдем к последнему индексу, а именно к `GIN`, который оперирует полнотекствовым поиском. Попробуем выполнить вот такой запрос:
```sql
explain analyze select * from appliance where to_tsvector('russian', name) @@ to_tsquery('russian', 'Обувная & электросушилка');
```
Функция `to_tsvector` переводит строку в полнотекстовый вектор, а функция `to_tsquery` составляет запрос по входным данным, который будет выполнять полнотекстовый поиск в векторе, который мы ранее составили. В данном случае, будет производиться поиск значений, которые содержат в себе производные от слов обувная и электросушилка. Посмотрим на результат запроса:
```
Gather  (cost=1000.00..645501.50 rows=125 width=121) (actual time=820.503..23506.119 rows=208072 loops=1)
 Workers Planned: 2
 Workers Launched: 2
 ->  Parallel Seq Scan on appliance  (cost=0.00..644489.00 rows=52 width=121) (actual time=808.610..23331.508 rows=69357 loops=3)
       Filter: (to_tsvector('russian'::regconfig, name) @@ '''обувн'' & ''электросушилк'''::tsquery)
       Rows Removed by Filter: 1597309
Planning Time: 10.817 ms
JIT:
 Functions: 6
 Options: Inlining true, Optimization true, Expressions true, Deforming true
 Timing: Generation 1.102 ms (Deform 0.191 ms), Inlining 1301.866 ms, Optimization 708.285 ms, Emission 413.116 ms, Total 2424.368 ms
Execution Time: 23519.832 ms
```
Теперь попробуем выполнить запрос, используя индекс `GIN`:
```sql
create index gin_idx on appliance using gin(to_tsvector('russian', name));
explain analyze select * from appliance where to_tsvector('russian', name) @@ to_tsquery('russian', 'Обувная & электросушилка');
```
Результат:
```
Bitmap Heap Scan on appliance  (cost=364.21..883.60 rows=125 width=121) (actual time=37.889..7921.315 rows=208072 loops=1)
 Recheck Cond: (to_tsvector('russian'::regconfig, name) @@ '''обувн'' & ''электросушилк'''::tsquery)
 Rows Removed by Index Recheck: 1612804
 Heap Blocks: exact=53695 lossy=33058
 ->  Bitmap Index Scan on gin_idx  (cost=0.00..364.18 rows=125 width=0) (actual time=30.931..30.932 rows=208072 loops=1)
       Index Cond: (to_tsvector('russian'::regconfig, name) @@ '''обувн'' & ''электросушилк'''::tsquery)
Planning Time: 4.270 ms
Execution Time: 7934.386 ms
```
Видим, что индекс применился, а запрос выполнился быстрее. Значит в данном случае применение индекса было оправданным.
Индексы - полезная вещь, но нельзя ею злоупотреблять, так как она может и ускорить выполнение запросов, так и замедлить.
### Часть 2: Транзакции
Транзакция - с точки зрения запроса это просто блок кода. Но если капнуть глубже, то это, грубо говоря, архив запросов к бд. Запрос можно как выполнить окончательно, так и откатить изменения, которые были внесены этим запросом.
[transactions.sql](scripts/transactions.sql)
Попробуем применить несколько транзакций к нашей таблице.
```sql
begin;

insert into appliance (id, name, brand, price, saler_name, city, publishing_date)
values (5000001, 'Посудомоечная машина', 'LG', 30000, 'Владимир Дмитриев', 'г. Москва', '2025-02-15');
update appliance set price = price * 1.1 where name = 'Посудомоечная машина';
```
Данный блок кода добавляет новую посудомойку и повышает цены на все посудомойки. Теперь мы можем сделать два действия: `commit` или `rollback`. После `commit` мы уже не сможем вернуть таблицу, в состояние, которое было до выполнения запроса. Если же мы сделаем `rollback`, то мы откатим таблицу к состоянию, которое было до выполнения запроса. Также, в случае ошибки в данном блоке кода, мы не сможем закоммитить или же выполнить транзакцию еще раз, пока мы ее не откатим к исходному состоянию. Это может быть полезным при выполнении банковских операций, когда мы не можем тратить деньги, которых у нас нет.
Выполним теперь такую транзакцию:
```sql
do $$
begin
	if exists (select 1 from appliance where id = 5000002) then
		raise exception 'Appliance with id 5000002 already exists!';
	end if;

	insert into appliance (id, name, brand, price, saler_name, city, publishing_date)
	values (5000002, 'Посудомоечная машина', 'LG', 30000, 'Владимир Дмитриев', 'г. Москва', '2025-02-15');
	
end $$;
```
Здесь мы опять пытаемся добавить новую посудомойку, но при этом, обрабатываем исключение, если запись с таким идентификатором уже существует (согласен, пример не особо реальный, так как в реальности айдишник инкрементируется автоматически, и он не сможет быть неуникальным). Если мы ловим исключение, то мы не сможем выполнить транзакцию заново или же закоммитить ее. Очевидно, что такое может быть полезным.
Теперь попробуем выполнить транзакцию с удалением:
```sql
do $$
begin
	if not exists (select 1 from appliance where id = 5000002) then
		raise exception 'Appliance with id 5000002 not exists!';
	end if;

	delete from appliance where id = 5000002;
	
end $$;
```
Здем мы ловим исключение, когда мы хотим удалить несуществующую технику. В принципе, если мы словим исключение, то откатывать тут и нечего, но до того как мы ловим исключение, могут быть еще какие-то запросы, которые вносят изменения в таблицу, и в случае неудачного удаления должны откатиться.
Теперь посмотрим на некоторые аномалии, которые могут возникнуть при работе с несколькими транзакциями одновременно. Здесь же и попробуем транзакции с разными уровнями изоляции.
[isolation_level1.sql](scripts/isolation_level1.sql), [isolation_level2.sql](scripts/isolation_level2.sql)
Определим три уровня изоляции. Есть еще и четвертый, но в PostgreSQL он не представлен.
**READ COMMITTED** - на этом уровне транзакция может читать только те изменения в других параллельных транзакциях, которые уже были закоммичены. Используется по умолчанию. 
**REPEATABLE READ** - этот уровень означает, что пока транзакция не завершится, никто параллельно не может изменять или удалять строки, которые транзакция уже прочитала.
**SERIALIZABLE** - блокирует любые действия, пока запущена транзакция — получается, транзакции идут строго одна за другой и максимально изолируются друг от друга.
Теперь посмотрим на некоторые аномалии.
Сначала посмотрим на аномалию фантомного чтения, когда в одной транзакции два одинаковых запроса возвращают разные результаты:
```sql
-- Transaction 1
begin isolation level read committed;
update appliance set price = 1234 where id = 5000001;

select * from appliance where id = 5000001;
--5000001	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15
-- Transaction 2
begin isolation level read committed;
select * from appliance where id = 5000001;
--5000001	Посудомоечная машина	LG	33000	Владимир Дмитриев	г. Москва	2025-02-15
--После коммита первой транзакции
--5000001	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15
```
Теперь посмотрим на проблему фантомного чтения с уровнем изоляции `repeatable_read`:
```sql
-- Transaction 1
begin isolation level repeatable read;
insert into appliance (id, name, brand, price, saler_name, city, publishing_date)
values (5000002, 'Посудомоечная машина', 'LG', 30000, 'Владимир Дмитриев', 'г. Москва', '2025-02-15');
-- Transaction 2
begin isolation level repeatable read;
select * from appliance where id = 5000001 or 5000002;
--до начала выполнения параллельной транзакции
--5000001	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15
--После коммита первой транзакции
--5000001	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15
--5000002	Посудомоечная машина	LG	1234	Владимир Дмитриев	г. Москва	2025-02-15
```
Из определения уровня изоляции `repeatable read` можно подумать, что мы избавились от проблемы фантомного чтения, так как транзакция не позволит делать изменения, в данных, которые он считала, но при этом можно вставить новые данные, которые она не считала, и на два одинаковых запроса мы получим один и тот же результат.
Теперь посмотрим на аномалию несогласованной записи на уровне `repeatable read`:
```sql
-- Transaction 1
begin isolation level repeatable read;
select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234
update appliance set price = price * 1000  where id = 5000001;
commit;

select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234000
-- Transaction 2
begin isolation level repeatable read;
select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234
update appliance set price = price * 1000  where id = 5000002;
commit;

select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234000
```
Теперь посмотрим на уровень изоляции `SERIALIZABLE`, у которого нет никаких аномалий:
```sql
-- Transaction1
begin isolation level serializable;
select sum(price) from appliance where id = 5000001 or id = 5000002;
--31234
update appliance set price = price * 1000  where id = 5000002;
commit;

select sum(price) from appliance where id = 5000001 or id = 5000002;
--30001234
-- Transaction 2
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
```
Но такие транзакции самые тяжелые и самые медленные для БД.
Транзакция полезная вещь, когда нужно соблюдать какое-то условие, например, неотрицательный баланс или что то подобное. Поможет избежать лишних багов и сделать приложение менее уязвимым.
### Часть 3: Расширения
[extensions.sql](scripts/extensions.sql)
**PG_TRGM**
С помощью данного расширения можно искать похожие друг на друга строки, разбивая из на триграммы - комбинации из трех букв. Попробуем внедрить индекс `GIN` используя инструменты расширения `pg_trgm`:
```sql
explain analyze select * from appliance where name ilike '%машина';
```
Результат без индекса:
```
--Seq Scan on appliance  (cost=0.00..160114.00 rows=843667 width=121) (actual time=1.969..5603.860 rows=833588 loops=1)
--  Filter: (name ~~* '%машина'::text)
--  Rows Removed by Filter: 4166412
--Planning Time: 2.664 ms
--JIT:
--  Functions: 2
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 0.097 ms (Deform 0.042 ms), Inlining 0.000 ms, Optimization 0.149 ms, Emission 1.787 ms, Total 2.033 ms
--Execution Time: 5643.196 ms
```
Применим индекс:
```sql
create index gin_trgm_idx on appliance using gin(name gin_trgm_ops);
explain analyze select * from appliance where name ilike '%машина';
```
Результат с индексом:
```
--Bitmap Heap Scan on appliance  (cost=5730.09..148403.61 rows=843667 width=121) (actual time=279.777..3899.350 rows=833588 loops=1)
--  Recheck Cond: (name ~~* '%машина'::text)
--  Rows Removed by Index Recheck: 1408832
--  Heap Blocks: exact=64581 lossy=33026
--  ->  Bitmap Index Scan on gin_trgm_idx  (cost=0.00..5519.17 rows=843667 width=0) (actual time=212.974..212.975 rows=833588 loops=1)
--        Index Cond: (name ~~* '%машина'::text)
--Planning Time: 3.551 ms
--JIT:
--  Functions: 2
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 8.429 ms (Deform 0.139 ms), Inlining 0.000 ms, Optimization 13.596 ms, Emission 40.798 ms, Total 62.822 ms
--Execution Time: 3927.597 ms
```
Получили прирост в производительности. С иднексом `GIN` значительно ускоряется поиск с использованием триграмм. Расширение довольно полезное, но может медленно работать с короткими текстами, так как количество уникальных триграмм ограничено.
**PG_BIGM**
Расширение аналогичное `pg_trgm`, но только вместо триграмм используются биграммы - комбинации из двух символов. Попробуем выполнить такой же запрос, применив индекс `GIN`:
```sql
create index gin_bigm_idx on appliance using gin(name gin_bigm_ops);
explain analyze select * from appliance where name ilike '%машина';
```
Получили вот такой результат:
```
--Seq Scan on appliance  (cost=0.00..160114.00 rows=843667 width=121) (actual time=1.982..5148.251 rows=833588 loops=1)
--  Filter: (name ~~* '%машина'::text)
--  Rows Removed by Filter: 4166412
--Planning Time: 5.221 ms
--JIT:
--  Functions: 2
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 0.237 ms (Deform 0.074 ms), Inlining 0.000 ms, Optimization 0.200 ms, Emission 1.722 ms, Total 2.159 ms
--Execution Time: 5215.104 ms
```
В принципе, прирост есть, но он невелик. Таблица очень большая, и при таких условия поиск с помощью биграмм может быть неэффективен даже с индексом `GIN`.
**PGCRYPTO**
Данное расширение нужно для шифрования данных, с помощью ключа шифрования, который мы можем придумать самостоятельно. Таким образом, даже если произойдет утечка базы данных, с ней не смогут ничего сделать без ключа шифрования. Создадим маленькую таблицу и зашифруем в ней колонку с ценой за единицу техники:
```sql
create table encypted_appliance as 
select id, name, brand, pgp_sym_encrypt(price::text, 'dishwasher') as encrypted_price, saler_name, city, publishing_date from appliance limit 100;
```
В качестве ключа шифрования я использовал строку `dishwasher`. Посмотрим, что теперь хранится в нашей таблице:
```sql
select encrypted_price from encypted_appliance limit 5;
--Ã       ÆÝñ  ÆgÒ6 <PßëµuB¥ ã+=]ä6 xl °×so,Û ¦®  x0Éæ  ¤âÎ <¬~Õð!Öf¡ey O
--Ã     ÷ mÓ  j gÒ6 © ÊfH¹Ò bdZ½K ü"¥ÿö¯¨åÇ  =T 'OzýOÐàÒDô çSO)»Æ}t@| äÿB
--Ã       PHañ.>{Ò7 &ÇT'Vàç  ôIÜ  ¹¾k h{é³Hõ74T¯    Äu^²U   &-v#L-nÇ fÂµÕ¼
--Ã     3·~aÜ  ílÒ7 ÀF"]Ï^ M/  Þåà²ÑG | < / =zøâÕ  øC¾ öù ¦`P ;»ü© #U  ãå2
--Ã     IÉ[£ÏÄ0 hÒ6 °ös­ »J&xÅ ÍÏ_½ÓiÍ 4 Rþ  ¯]¿RÍ òp ë    M }ñõÿ° ô,x å?
```
Как мы видим, данные зашифрованы и их не получится никак расшифровать без ключа шифрования. Попробуем расшифровать представленные данные с помощью такого запроса:
```sql
select pgp_sym_decrypt(encrypted_price::bytea, 'dishwasher') from encypted_appliance limit 5;
--47103
--16633
--111116
--184540
--51671
```
Видим, что с помощью ключа шифрования получили исходные данные в человекочитаемом формате.
Данное расширение может быть полезным, если необходимо хранить чувствительные данные.