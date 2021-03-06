#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from flask_cors import CORS
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError
from model.piece import create_piece, delete_piece, edit_piece, get_pieces

# TODO:
# - resource URLs in responses


class PieceSchema(Schema):
    """Require body in POST request to /piece/ endpoint
    """

    body = fields.String(required=True)
    title = fields.String(missing=None)
    tags = fields.List(fields.String, missing=[])


class IsoFormatEncoder(JSONEncoder):
    """Return date(time)s in ISO 8601 format
    """

    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        else:
            return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.config.from_object(__name__)
app.json_encoder = IsoFormatEncoder
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/piece/", methods=["GET", "POST"])
@app.route("/piece/<slug>", methods=["GET", "POST", "PUT", "DELETE"])
def piece(slug=None):
    """ Content piece enpoint
    """

    if request.method == "POST":
        params = request.json or request.args.to_dict()
        try:
            params = PieceSchema().load(params)
        except ValidationError as e:
            return jsonify(e.normalized_messages()), 400
        created = create_piece(
            body=params["body"], title=params["title"], tags=params["tags"]
        )
        return jsonify(created)

    elif request.method == "PUT":
        params = request.json or request.args.to_dict()
        try:
            piece = get_pieces(slug=slug)[0]
        except IndexError:
            return jsonify({"error": f"Piece {slug} not found"}), 404

        piece.update(params)
        edited_piece = edit_piece(
            slug=slug, body=piece["body"], title=piece["title"], tags=piece["tags"],
        )
        return edited_piece

    elif request.method == "DELETE":
        try:
            delete = delete_piece(slug=slug)[0]
            return jsonify(delete)
        except IndexError:
            return jsonify({"error": f"Piece {slug} not found"}), 404

    else:
        if slug:
            return jsonify(get_pieces(slug=slug))
        return jsonify(get_pieces())
