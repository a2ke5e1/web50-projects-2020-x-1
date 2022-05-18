-- auto-generated definition
create table book
(
    id     serial
        primary key,
    isbn   varchar(255),
    title  varchar(255),
    author varchar(255),
    year   integer
);

alter table book
    owner to qvjlqhyvmjuezz;



-- auto-generated definition
create table users
(
    id       serial
        constraint users_pk
            primary key,
    username varchar(255) not null,
    name     varchar(255),
    email    varchar(255),
    password varchar(512)
);

alter table users
    owner to qvjlqhyvmjuezz;

create unique index users_id_uindex
    on users (id);

create unique index users_username_uindex
    on users (username);


-- auto-generated definition
create table review
(
    id      serial
        constraint review_pk
            primary key,
    msg     text,
    score   double precision,
    book_id integer
        constraint book_id
            references book
            on update cascade on delete cascade,
    user_id integer
        constraint user_id
            references users
);

alter table review
    owner to qvjlqhyvmjuezz;

create unique index review_id_uindex
    on review (id);


