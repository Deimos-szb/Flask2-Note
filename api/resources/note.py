from api import auth, abort, g, Resource, reqparse, api
from api.models.note import NoteModel
from api.models.tag import TagModel
from api.schemas.note import NoteSchema, NoteRequestSchema, NoteEditSchema, note_schema, notes_schema
from webargs import fields
from flask_apispec import marshal_with, use_kwargs, doc
from flask_apispec.views import MethodResource
from helpers.shortcuts import get_or_404

@doc(description="API for Notes", tags=["Notes"])
class NoteResource(MethodResource):

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Get note by id from unique User")
    @doc(responses={403: {"description": "Forbidden for this User"}})
    @doc(responses={404: {"description": "Note not found"}})
    @marshal_with(NoteSchema, code=200)
    def get(self, note_id):
        """
        Пользователь может получить ТОЛЬКО свою заметку
        """
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        if note.author.id != author.id:
            abort(403, error="Forbidden for this User")
        return note, 200

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Edit note by id from unique User")
    @doc(responses={403: {"description": "Forbidden for this User"}})
    @doc(responses={404: {"description": "Note not found"}})
    @marshal_with(NoteSchema, code=201)
    @use_kwargs(NoteEditSchema, location=("json"))
    def put(self, note_id, **kwargs):
        """
        Пользователь может редактировать ТОЛЬКО свои заметки
        """
        author = g.user
        note = NoteModel.query.get(note_id)
        if note is None:
            abort(404, error=f"Note with id={note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden for this User")
        note.text = kwargs.get("text") or note.text
        note.private = kwargs.get("private") or note.private
        note.save()
        return note, 201

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Delete note by id from unique User")
    @doc(responses={403: {"description": "Forbidden for this User"}})
    @doc(responses={404: {"description": "Note not found"}})
    def delete(self, note_id):
        """
        Пользователь может удалять ТОЛЬКО свои заметки
        """
        author = g.user
        note = NoteModel.query.get(note_id)
        if note is None:
            abort(404, error=f"Note with id={note_id} not found")
        if author.id != note.author.id:
            abort(403, error="Forbidden for this User")
        note.delete()
        return "Note was deleted", 200

@doc(description="API for Notes", tags=["Notes"])
class NotesListResource(MethodResource):

    @auth.login_required()
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Get all Users notes")
    @marshal_with(NoteSchema(many=True), code=200)
    def get(self):
        notes = g.user.notes
        return notes, 200

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Create new note for unique User")
    @marshal_with(NoteSchema, code=201)
    @use_kwargs(NoteRequestSchema, location=("json"))
    def post(self, **kwargs):
        author = g.user
        note = NoteModel(author_id=author.id, **kwargs)
        note.save()
        return note, 201

@doc(tags=['Notes'])
class NoteSetTagsResource(MethodResource):
    @auth.login_required()
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Set tags to Note")
    @doc(responses={403: "Forbidden for this user"})
    @doc(responses={404: "Note not found"})
    @use_kwargs({"tags": fields.List(fields.Int())}, location=('json'))
    @marshal_with(NoteSchema, code=201)
    def put(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        if note.author != author:
            abort(403, error="Forbidden for this User")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            if tag is None:
                continue
            note.tags.append(tag)
        note.save()
        return note, 201

    @auth.login_required()
    @doc(security=[{"basicAuth": []}])
    @doc(summary="Delete tags from Note")
    @doc(responses={403: "Forbidden for this user"})
    @doc(responses={404: "Note not found"})
    @use_kwargs({"tags": fields.List(fields.Int())}, location=('json'))
    @marshal_with(NoteSchema, code=200)
    def delete(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        if note.author != author:
            abort(403, error="Forbidden for this User")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            if tag is None:
                continue
            try:
                note.tags.remove(tag)
            except ValueError:
                pass
        note.save()
        return note, 200


@doc(tags=['Notes'])
class NoteFilterResource(MethodResource):
    @doc(summary="Get all public notes of unique User")
    @marshal_with(NoteSchema(many=True), code=200)
    @use_kwargs({"username": fields.Str()}, location=('query'))
    def get(self, **kwargs):
        notes = NoteModel.query.filter_by(private = False).filter(NoteModel.author.has(**kwargs)).all()
        return notes, 200


@api.resource('/notes/<int:note_id>/archive') #DELETE
@doc(tags=['Notes'])
class NoteToArchive(MethodResource):
    @doc(summary="Move Note to archive")
    @marshal_with(NoteSchema, code=200)
    def delete(self, note_id):
        note = get_or_404(NoteModel, note_id)
        note.archive = True
        note.save()
        return note, 200

@api.resource('/notes/<int:note_id>/restore') #PUT
@doc(tags=['Notes'])
class NoteFromArchive(MethodResource):
    @doc(summary="Restore Note from archive")
    @marshal_with(NoteSchema, code=200)
    def put(self, note_id):
        # author = g.user
        note = get_or_404(NoteModel, note_id)
        # if note.author != author:
        #     abort(403, error="Forbidden for this User")
        note.archive = False
        note.save()
        return note, 200