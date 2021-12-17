from api import Resource, abort, reqparse, auth
from api.models.tag import TagModel
from api.schemas.tag import TagSchema, TagRequestSchema, tag_schema, tags_schema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc

@doc(description='Api for tag.', tags=['Tag'])
class TagResource(MethodResource):

    @marshal_with(TagSchema, code=200, description="Get tag by id")
    def get(self, tag_id):

        tag = TagModel.query.get(tag_id)
        if tag is None:
            abort(404, error=f"Tag with id={tag_id} not found")
        return tag, 200

    def put(self, tag_id):
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True)
        tag_data = parser.parse_args()
        tag = TagModel.query.get(tag_id)
        if tag is None:
            abort(404, error="Tag not found")
        tag.name = tag_data["name"]
        tag.save()
        return tag_schema.dump(tag), 200

    @auth.login_required
    def delete(self, tag_id):
        tag = TagModel.query.get(tag_id)
        tag.delete()
        return f"Tag with id={tag_id} was deleted", 200


@doc(description='Api for tag.', tags=['Tag'])
class TagListResource(MethodResource):
    def get(self):
        tags = TagModel.query.all()
        return tags_schema.dump(tags), 200    
    
    @doc(description="Create new Tag")
    @marshal_with(TagSchema, code=201)
    @use_kwargs(TagRequestSchema, location=('json'))
    def post(self, **kwargs):
        tag = TagModel(**kwargs)
        tag.save()
        if not tag.id:
            abort(400, error=f"Tag with tagname:{tag.name} already exist")
        return tag, 201
