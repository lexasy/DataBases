create table users (
	user_id bigint generated always as identity primary key,
	username varchar(150) not null check (length(username) >= 3),
	password varchar(100) not null,
	rights varchar(10)
);