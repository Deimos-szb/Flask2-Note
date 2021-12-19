from api import Resource, abort, reqparse, auth, g
from api.models.user import UserModel
from api.schemas.user import user_schema, users_schema, UserSchema, UserRequestSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields

@doc(description='Api for users.', tags=['Users'])
class UserResource(MethodResource):
    @doc(summary="Get User by id", description="Return User with unique id")
    @doc(responses={404: {"description": "User not found"}})
    @marshal_with(UserSchema, code=200)
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if user is None:
            abort(404, error=f"User with id={user_id} not found")
        return user, 200

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Edit user by id")
    @doc(responses={404: {"description": "User not found"}})
    @use_kwargs({"username": fields.Str(), "role": fields.Str()})
    @marshal_with(UserSchema, code=201)
    def put(self, user_id, **kwargs):
        user = UserModel.query.get(user_id)
        if user is None:
            abort(404, error="User not found")
        user.username = kwargs.get("username") or user.username
        user.role = kwargs.get("role") or user.role
        user.save()
        return user, 201

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Delete user by id", description="Delete unique user")
    @doc(responses={200: {"description": "User Deleted"}})
    @doc(responses={401: {"description": "Not authorization"}})
    @doc(responses={404: {"description": "User not found"}})
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if user is None:
            abort(404, error=f"User with id={user_id} not found")
        if user_id != g.user.id and g.user.role != "admin":
            abort(401, error="Not authorization")
        user.delete()
        return f"User with id={user_id} was deleted", 200


@doc(description='Api for users.', tags=['Users'])
class UsersListResource(MethodResource):
    @doc(summary="Get list of all users")
    @marshal_with(UserSchema(many=True), code=200)
    def get(self):
        users = UserModel.query.all()
        return users, 200

    @doc(summary="Create new User")
    @doc(responses={400: {"description": "User already exist"}})
    @marshal_with(UserSchema, code=201)
    @use_kwargs(UserRequestSchema, location=('json'))
    def post(self, **kwargs):
        user = UserModel(**kwargs)
        user.save()
        if not user.id:
            abort(400, error=f"User with username:{user.username} already exist")
        return user, 201
