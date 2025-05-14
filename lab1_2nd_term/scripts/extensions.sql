--pg_trgm
create extension if not exists pg_trgm;

explain analyze select * from appliance where name ilike '%машина';
--Seq Scan on appliance  (cost=0.00..160114.00 rows=843667 width=121) (actual time=1.969..5603.860 rows=833588 loops=1)
--  Filter: (name ~~* '%машина'::text)
--  Rows Removed by Filter: 4166412
--Planning Time: 2.664 ms
--JIT:
--  Functions: 2
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 0.097 ms (Deform 0.042 ms), Inlining 0.000 ms, Optimization 0.149 ms, Emission 1.787 ms, Total 2.033 ms
--Execution Time: 5643.196 ms
create index gin_trgm_idx on appliance using gin(name gin_trgm_ops);
explain analyze select * from appliance where name ilike '%машина';
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
drop index if exists gin_trgm_idx;


--pg_bigm
create extension if not exists pg_bigm;
create index gin_bigm_idx on appliance using gin(name gin_bigm_ops);
explain analyze select * from appliance where name ilike '%машина';
--Seq Scan on appliance  (cost=0.00..160114.00 rows=843667 width=121) (actual time=1.982..5148.251 rows=833588 loops=1)
--  Filter: (name ~~* '%машина'::text)
--  Rows Removed by Filter: 4166412
--Planning Time: 5.221 ms
--JIT:
--  Functions: 2
--  Options: Inlining false, Optimization false, Expressions true, Deforming true
--  Timing: Generation 0.237 ms (Deform 0.074 ms), Inlining 0.000 ms, Optimization 0.200 ms, Emission 1.722 ms, Total 2.159 ms
--Execution Time: 5215.104 ms
drop index if exists gin_bigm_idx;


--pgcrypto
create extension if not exists pgcrypto;
create table encypted_appliance as 
select id, name, brand, pgp_sym_encrypt(price::text, 'dishwasher') as encrypted_price, saler_name, city, publishing_date from appliance limit 100;

select encrypted_price from encypted_appliance limit 5;
--Ã       ÆÝñ  ÆgÒ6 <PßëµuB¥ ã+=]ä6 xl °×so,Û ¦®  x0Éæ  ¤âÎ <¬~Õð!Öf¡ey O
--Ã     ÷ mÓ  j gÒ6 © ÊfH¹Ò bdZ½K ü"¥ÿö¯¨åÇ  =T 'OzýOÐàÒDô çSO)»Æ}t@| äÿB
--Ã       PHañ.>{Ò7 &ÇT'Vàç  ôIÜ  ¹¾k h{é³Hõ74T¯    Äu^²U   &-v#L-nÇ fÂµÕ¼
--Ã     3·~aÜ  ílÒ7 ÀF"]Ï^ M/  Þåà²ÑG | < / =zøâÕ  øC¾ öù ¦`P ;»ü© #U  ãå2
--Ã     IÉ[£ÏÄ0 hÒ6 °ös­ »J&xÅ ÍÏ_½ÓiÍ 4 Rþ  ¯]¿RÍ òp ë    M }ñõÿ° ô,x å?
select pgp_sym_decrypt(encrypted_price::bytea, 'dishwasher') from encypted_appliance limit 5;
--47103
--16633
--111116
--184540
--51671
