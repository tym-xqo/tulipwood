#!/usr/bin/env python
# -*- coding: utf-8 -*-
import secrets
from raw import db


def create_piece(body, title=None, tags=[]):
    slug = secrets.token_hex(4)[:7]
    piece_sql = (
        "insert into piece (slug, title, body)"
        "  values (:slug, :title, :body) "
        "returning piece_id"
    )
    save_piece = db.result(piece_sql, slug=slug, title=title, body=body)[0]

    tag_sql = (
        "insert into tag (tag)"
        "  values (:tag) "
        "on conflict (tag) do update "
        "set tag = :tag "
        "returning tag_id"
    )
    piece_tag_sql = "insert into x_piece_tag values (:piece_id, :tag_id)"

    for tag in tags:
        save_tag = db.result(tag_sql, tag=tag)[0]
        db.result(
            piece_tag_sql, piece_id=save_piece["piece_id"], tag_id=save_tag["tag_id"]
        )

    result = get_pieces(slug=slug)[0]
    return result


def delete_piece(slug):
    sql = (
        "update piece"
        "   set deleted_at = now()"
        "     , updated_at = now()"
        " where slug = :slug "
        "returning piece_id, slug, deleted_at"
    )
    result = db.result(sql, slug=slug)
    return result


def get_pieces(slug=None, tag=None):
    sql = (
        "select p.piece_id"
        "     , slug"
        "     , title"
        "     , left(body, 40) as snippet"
        "     , body"
        "     , array_agg(tag) as tags"
        "     , p.created_at"
        "     , p.updated_at"
        " from piece p left"
        " join x_piece_tag x using (piece_id) left"
        " join tag using (tag_id) "
        "where p.deleted_at > now() "
        "{% if tag %} "
        "  and tag = :tag "
        "{% endif %} "
        "{% if slug %} "
        "  and slug = :slug "
        "{% endif %} "
        "group by 1, 2, 3 "
        "order by created_at"
    )
    result = db.result(sql, jinja=True, tag=tag, slug=slug)
    return result


def edit_piece(slug, body, title=None, tags=[]):
    piece_sql = (
        "update piece "
        "   set title = :title"
        "     , body = :body"
        "     , updated_at = now()"
        " where slug = :slug "
        "returning piece_id"
    )
    save_piece = db.result(piece_sql, slug=slug, title=title, body=body)[0]
    tag_sql = (
        "insert into tag (tag)"
        "  values (:tag) "
        "on conflict (tag) do update "
        "set tag = :tag "
        "returning tag_id"
    )
    piece_tag_sql = "insert into x_piece_tag values (:piece_id, :tag_id)"

    if tags:
        db.result(
            "delete from x_piece_tag where piece_id = :piece_id",
            piece_id=save_piece["piece_id"],
        )
        for tag in tags:
            save_tag = db.result(tag_sql, tag=tag)[0]
            db.result(
                piece_tag_sql,
                piece_id=save_piece["piece_id"],
                tag_id=save_tag["tag_id"],
            )

    result = get_pieces(slug=slug)[0]
    return result


if __name__ == "__main__":
    body = (
        "otaku convenience store towards 3D-printed city "
        "soul-delay courier voodoo god girl"
    )
    tags = ["baz", "quux"]
    slug = "582e283"
    p = edit_piece(slug=slug, body=body, tags=tags)
    print(p)
