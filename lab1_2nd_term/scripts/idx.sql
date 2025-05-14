-- BTREE, BRIN
-- explain analyze select * from appliance where price between 90000 and 110000;
explain analyze select * from appliance where publishing_date between '2024-01-01' and '2024-01-31';
-- Gather  (cost=1000.00..149914.30 rows=200503 width=121) (actual time=7.318..3373.973 rows=212442 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Seq Scan on appliance  (cost=0.00..128864.00 rows=83543 width=121) (actual time=49.565..2809.035 rows=70814 loops=3)
--        Filter: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
--        Rows Removed by Filter: 1595853
-- Planning Time: 0.368 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 3.297 ms (Deform 0.511 ms), Inlining 0.000 ms, Optimization 0.983 ms, Emission 146.994 ms, Total 151.274 ms
-- Execution Time: 3385.992 ms
create index btree_idx on appliance using btree(publishing_date);
explain analyze select * from appliance where publishing_date between '2024-01-01' and '2024-01-31';
-- Gather  (cost=3743.59..142588.26 rows=200503 width=121) (actual time=137.688..5219.189 rows=212442 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Bitmap Heap Scan on appliance  (cost=2743.59..121537.96 rows=83543 width=121) (actual time=49.114..5083.270 rows=70814 loops=3)
--        Recheck Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
--        Rows Removed by Index Recheck: 537297
--        Heap Blocks: exact=19189 lossy=11933
--        ->  Bitmap Index Scan on btree_idx  (cost=0.00..2693.46 rows=200503 width=0) (actual time=119.469..119.470 rows=212442 loops=1)
--              Index Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
-- Planning Time: 0.177 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 4.122 ms (Deform 0.381 ms), Inlining 0.000 ms, Optimization 5.834 ms, Emission 19.364 ms, Total 29.320 ms
-- Execution Time: 5236.771 ms
drop index if exists btree_idx;

create index brin_idx on appliance using brin(publishing_date);
explain analyze select * from appliance where publishing_date between '2024-01-01' and '2024-01-31';
-- explain analyze select * from appliance where publishing_date between '2024-01-01' and '2024-01-31';
-- Gather  (cost=1000.00..149914.30 rows=200503 width=121) (actual time=7.447..3306.761 rows=212442 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Seq Scan on appliance  (cost=0.00..128864.00 rows=83543 width=121) (actual time=33.258..3067.989 rows=70814 loops=3)
--        Filter: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
--        Rows Removed by Filter: 1595853
-- Planning Time: 3.393 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 1.273 ms (Deform 0.336 ms), Inlining 0.000 ms, Optimization 0.711 ms, Emission 98.951 ms, Total 100.936 ms
-- Execution Time: 3318.754 ms
drop index if exists brin_idx;
-- brin не применился, так как проверяемые данные не отсортированы



create table brin_test as select * from appliance order by publishing_date;
explain analyze select * from brin_test where publishing_date between '2024-01-01' and '2024-01-31';
-- Gather  (cost=1000.00..151515.48 rows=215504 width=121) (actual time=1366.847..3471.202 rows=212442 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Seq Scan on brin_test  (cost=0.00..128965.07 rows=89793 width=121) (actual time=1122.486..2443.108 rows=70814 loops=3)
--        Filter: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
--        Rows Removed by Filter: 1595853
-- Planning Time: 1.714 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 13.588 ms (Deform 3.166 ms), Inlining 0.000 ms, Optimization 11.542 ms, Emission 64.864 ms, Total 89.995 ms
-- Execution Time: 3501.486 ms
create index brin_idx on brin_test using brin(publishing_date);
explain analyze select * from brin_test where publishing_date between '2024-01-01' and '2024-01-31';
-- Gather  (cost=1070.93..141555.92 rows=215490 width=121) (actual time=11.084..572.383 rows=212442 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Bitmap Heap Scan on brin_test  (cost=70.93..119006.92 rows=89788 width=121) (actual time=5.334..300.581 rows=70814 loops=3)
--        Recheck Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
--        Rows Removed by Index Recheck: 1265
--        Heap Blocks: lossy=2133
--        ->  Bitmap Index Scan on brin_idx  (cost=0.00..17.06 rows=215969 width=0) (actual time=0.657..0.659 rows=42240 loops=1)
--              Index Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
-- Planning Time: 0.275 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 1.202 ms (Deform 0.442 ms), Inlining 0.000 ms, Optimization 0.591 ms, Emission 6.924 ms, Total 8.717 ms
-- Execution Time: 583.268 ms
drop index if exists brin_idx;

create index btree_idx on brin_test using btree(publishing_date);
explain analyze select * from brin_test where publishing_date between '2024-01-01' and '2024-01-31';
-- Index Scan using btree_idx on brin_test  (cost=0.43..9265.23 rows=215490 width=121) (actual time=0.106..25.354 rows=212442 loops=1)
--  Index Cond: ((publishing_date >= '2024-01-01'::date) AND (publishing_date <= '2024-01-31'::date))
-- Planning Time: 0.709 ms
-- Execution Time: 29.475 ms
drop index if exists btree_idx;



explain analyze select * from appliance where name = 'Посудомоечня машина';
-- Gather  (cost=1000.00..145705.67 rows=210500 width=121) (actual time=7.937..4428.827 rows=208285 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Seq Scan on appliance  (cost=0.00..123655.67 rows=87708 width=121) (actual time=4.292..4139.566 rows=69428 loops=3)
--        Filter: (name = 'Посудомоечня машина'::text)
--        Rows Removed by Filter: 1597238
-- Planning Time: 0.884 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 0.628 ms (Deform 0.201 ms), Inlining 0.000 ms, Optimization 0.550 ms, Emission 11.889 ms, Total 13.068 ms
-- Execution Time: 4525.512 ms

create index btree_idx on appliance using btree(name);
-- Gather  (cost=3367.81..139699.59 rows=210500 width=121) (actual time=61.615..6770.366 rows=208285 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Bitmap Heap Scan on appliance  (cost=2367.81..117649.59 rows=87708 width=121) (actual time=22.049..6567.023 rows=69428 loops=3)
--        Recheck Cond: (name = 'Посудомоечня машина'::text)
--        Rows Removed by Index Recheck: 537576
--        Heap Blocks: exact=19064 lossy=11973
--        ->  Bitmap Index Scan on btree_idx  (cost=0.00..2315.18 rows=210500 width=0) (actual time=28.303..28.304 rows=208285 loops=1)
--              Index Cond: (name = 'Посудомоечня машина'::text)
-- Planning Time: 2.222 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 1.686 ms (Deform 0.208 ms), Inlining 0.000 ms, Optimization 9.618 ms, Emission 18.867 ms, Total 30.171 ms
-- Execution Time: 6840.680 ms
drop index if exists btree_idx;



explain analyze select * from appliance where name = 'Посудомоечня машина' and price >= 90000;
-- Gather  (cost=1000.00..141741.00 rows=118770 width=121) (actual time=2.753..3418.815 rows=117331 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Seq Scan on appliance  (cost=0.00..128864.00 rows=49488 width=121) (actual time=30.140..3360.463 rows=39110 loops=3)
--        Filter: ((price >= 90000) AND (name = 'Посудомоечня машина'::text))
--        Rows Removed by Filter: 1627556
-- Planning Time: 0.105 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 1.119 ms (Deform 0.233 ms), Inlining 0.000 ms, Optimization 0.736 ms, Emission 89.335 ms, Total 91.189 ms
-- Execution Time: 3426.669 ms
create index btree_idx on appliance using btree(name, price);
explain analyze select * from appliance where name = 'Посудомоечня машина' and price >= 90000;
-- Gather  (cost=4433.95..136719.05 rows=118770 width=121) (actual time=102.045..8025.154 rows=117331 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Bitmap Heap Scan on appliance  (cost=3433.95..123842.05 rows=49488 width=121) (actual time=35.584..7781.777 rows=39110 loops=3)
--        Recheck Cond: ((name = 'Посудомоечня машина'::text) AND (price >= 90000))
--        Rows Removed by Index Recheck: 546555
--        Heap Blocks: exact=12536 lossy=11568
--        ->  Bitmap Index Scan on btree_idx  (cost=0.00..3404.26 rows=118770 width=0) (actual time=25.462..25.462 rows=117331 loops=1)
--              Index Cond: ((name = 'Посудомоечня машина'::text) AND (price >= 90000))
-- Planning Time: 3.231 ms
-- JIT:
--  Functions: 6
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 6.890 ms (Deform 0.532 ms), Inlining 0.000 ms, Optimization 11.495 ms, Emission 101.460 ms, Total 119.845 ms
-- Execution Time: 8046.581 ms
drop index if exists btree_idx;


--GIN
explain analyze select * from appliance where to_tsvector('russian', name) @@ to_tsquery('russian', 'Обувная & электросушилка');
-- Gather  (cost=1000.00..645501.50 rows=125 width=121) (actual time=820.503..23506.119 rows=208072 loops=1)
--  Workers Planned: 2
--  Workers Launched: 2
--  ->  Parallel Seq Scan on appliance  (cost=0.00..644489.00 rows=52 width=121) (actual time=808.610..23331.508 rows=69357 loops=3)
--        Filter: (to_tsvector('russian'::regconfig, name) @@ '''обувн'' & ''электросушилк'''::tsquery)
--        Rows Removed by Filter: 1597309
-- Planning Time: 10.817 ms
-- JIT:
--  Functions: 6
--  Options: Inlining true, Optimization true, Expressions true, Deforming true
--  Timing: Generation 1.102 ms (Deform 0.191 ms), Inlining 1301.866 ms, Optimization 708.285 ms, Emission 413.116 ms, Total 2424.368 ms
-- Execution Time: 23519.832 ms
create index gin_idx on appliance using gin(to_tsvector('russian', name));
explain analyze select * from appliance where to_tsvector('russian', name) @@ to_tsquery('russian', 'Обувная & электросушилка');
-- Bitmap Heap Scan on appliance  (cost=364.21..883.60 rows=125 width=121) (actual time=37.889..7921.315 rows=208072 loops=1)
--  Recheck Cond: (to_tsvector('russian'::regconfig, name) @@ '''обувн'' & ''электросушилк'''::tsquery)
--  Rows Removed by Index Recheck: 1612804
--  Heap Blocks: exact=53695 lossy=33058
--  ->  Bitmap Index Scan on gin_idx  (cost=0.00..364.18 rows=125 width=0) (actual time=30.931..30.932 rows=208072 loops=1)
--        Index Cond: (to_tsvector('russian'::regconfig, name) @@ '''обувн'' & ''электросушилк'''::tsquery)
-- Planning Time: 4.270 ms
-- Execution Time: 7934.386 ms
drop index if exists gin_idx;

