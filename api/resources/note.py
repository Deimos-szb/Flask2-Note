from api import auth, abort, g, Resource, reqparse
from api.models.note import NoteModel
from api.models.tag import TagModel
from api.schemas.note import NoteSchema, note_schema, notes_schema
from webargs import fields
from flask_apispec import marshal_with, use_kwargs, doc
from flask_apispec.views import MethodResource


class NoteResource(Resource):
    @auth.login_required
    def get(self, note_id):
        """
        Пользователь может получить ТОЛЬКО свою заметку
        """
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        author_notes = NoteModel.query.filter(NoteModel.author.has(id=author.id)).all()
        for author_note in author_notes:
            if author_note == note:
                return note_schema.dump(note), 200
        abort(403, error=f"Author with id {author.id} doesnt have note with id={note_id}")

    @auth.login_required
    def put(self, note_id):
        """
        Пользователь может редактировать ТОЛЬКО свои заметки
        """
        author = g.user
        parser = reqparse.RequestParser()
        parser.add_argument("text", required=True)
        parser.add_argument("private", type=bool)
        note_data = parser.parse_args()
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        note.text = note_data["text"]

        note.private = note_data.get("private") or note.private

        note.save()
        return note_schema.dump(note), 200

    @auth.login_required
    def delete(self, note_id):
        """
        Пользователь может удалять ТОЛЬКО свои заметки
        """
        author = g.user
        authors_notes = NoteModel.query.filter(NoteModel.author.has(id=author.id)).all()
        note_to_delete = NoteModel.query.get(note_id)
        if note_to_delete is None:
            abort(404, error=f"There is no note with id={note_id}")
        for note in authors_notes:
            if note == note_to_delete:
                note_to_delete.delete()
                break
        else:
            abort(403, error=f"User {author['name']} dont have note with id={note_id}")
        # raise NotImplemented("Метод не реализован")
        return note_schema.dump(note_to_delete), 200


class NotesListResource(Resource):
    def get(self):
        notes = NoteModel.query.all()
        return notes_schema.dump(notes), 200

    @auth.login_required
    def post(self):
        author = g.user
        parser = reqparse.RequestParser()
        parser.add_argument("text", required=True)
        # Подсказка: чтобы разобраться с private="False",
        #   смотрите тут: https://flask-restful.readthedocs.io/en/latest/reqparse.html#request-parsing
        parser.add_argument("private", type=bool, required=True)
        note_data = parser.parse_args()
        note = NoteModel(author_id=author.id, **note_data)
        note.save()
        return note_schema.dump(note), 201


@doc(tags=['Notes'])
class NoteSetTagsResource(MethodResource):
    @doc(summary="Set tags to Note")
    @use_kwargs({"tags": fields.List(fields.Int())}, location=('json'))
    @marshal_with(NoteSchema)
    def put(self, note_id, **kwargs):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        # print("note kwargs = ", kwargs)
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            if tag is None:
                continue
            note.tags.append(tag)
        note.save()
        return note, 200
