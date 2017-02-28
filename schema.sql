drop table if exists definitions;
create table definitions (
  id integer primary key autoincrement,
  definition text not null,
  created_by text not null,
  submission_date text not null
);

drop table if exists neologisms;
create table neologisms (
  id integer primary key autoincrement,
  neologism text not null,
  parent_definition integer not null,
  created_by text not null,
  submission_date integer not null
);

drop table if exists upvotes;
create table upvotes (
  id integer primary key autoincrement,
  parent_neologism integer not null,
  created_by text not null,
  submission_date integer not null
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  email text not null,
  password text not null
);
