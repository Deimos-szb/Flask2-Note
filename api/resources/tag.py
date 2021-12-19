from api import Resource, abort, reqparse, auth
from api.models.tag import TagModel
from api.schemas.tag import TagSchema, TagRequestSchema, tag_schema, tags_schema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields

@doc(description='Api for tag.', tags=['Tags'])
class TagResource(MethodResource):

    @doc(summary="Get tag by id")
    @doc(responses={404: "Tag not found"})
    @marshal_with(TagSchema, code=200)
    def get(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if tag is None:
            abort(404, error=f"Tag with id={tag_id} not found")
        return tag, 200

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Edit tag by id")
    @doc(responses={404: "Tag not found"})
    @marshal_with(TagSchema, code=201)
    @use_kwargs({"name": fields.Str(required=True)}, location=("json"))
    def put(self, tag_id, **kwargs):
        tag = TagModel.query.get(tag_id)
        if tag is None:
            abort(404, error="Tag not found")
        tag.name = kwargs["name"]
        tag.save()
        return tag, 201

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Delete tag by id")
    @doc(responses={404: "Tag not found"})
    def delete(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if tag is None:
            abort(404, error="Tag not found")
        tag.delete()
        return f"Tag with id={tag_id} was deleted", 200


@doc(description='Api for tag.', tags=['Tags'])
class TagListResource(MethodResource):
    @doc(summary="Get all tags")
    @marshal_with(TagSchema(many=True), code=200)
    def get(self):
        tags = TagModel.query.all()
        return tags, 200

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Create new Tag")
    @doc(responses={400: "Tag already exist"})
    @marshal_with(TagSchema, code=201)
    @use_kwargs(TagRequestSchema, location=('json'))
    def post(self, **kwargs):
        tag = TagModel(**kwargs)
        tag.save()
        if not tag.id:
            abort(400, error=f"Tag with tagname:{tag.name} already exist")
        return tag, 201
