create table if not exists piece (
    piece_id int generated always as identity primary key
  , slug text not null unique
  , created_dt timestamptz not null default now()
  , updated_dt timestamptz not null default now()
  , deleted_dt timestamptz default 'infinity'
  , title text 
  , body text not null
);

create table if not exists tag (
    tag_id int generated always as identity primary key
  , tag text unique
  , created_dt timestamptz not null default now()
  , updated_dt timestamptz not null default now()
  , deleted_dt timestamptz default 'infinity' 
);

create table if not exists x_piece_tag (
    piece_id int references piece(piece_id)
  , tag_id int references tag(tag_id)
  , primary key (piece_id, tag_id)
);
