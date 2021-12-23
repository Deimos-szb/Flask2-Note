from api import api, app, docs
from api.resources import note
from api.resources.user import UserResource, UsersListResource, UsersSearchResource
from api.resources.auth import TokenResource
from api.resources.tag import TagResource, TagListResource
from api.resources.file import UploadPictureResource
from config import Config
from flask import render_template, send_from_directory

# CRUD

# Create --> POST
# Read --> GET
# Update --> PUT
# Delete --> DELETE
api.add_resource(UsersListResource,
                 '/users')  # GET, POST
api.add_resource(UserResource,
                 '/users/<int:user_id>')  # GET, PUT, DELETE


api.add_resource(TokenResource,
                 '/auth/token')  # GET

api.add_resource(note.NotesListResource,
                 '/notes',  # GET, POST
                 )
api.add_resource(note.NoteResource,
                 '/notes/<int:note_id>',  # GET, PUT, DELETE
                 )

api.add_resource(TagListResource,
                 '/tags')  # GET, POST
api.add_resource(TagResource,
                 '/tags/<int:tag_id>')  # GET, PUT, DELETE

api.add_resource(note.NoteSetTagsResource,
                 '/notes/<int:note_id>/tags')  # PUT, DELETE

api.add_resource(note.NoteFilterResource,
                 '/notes/public/filter') #GET

api.add_resource(UsersSearchResource,
                 '/users/search') #GET

docs.register(UserResource)
docs.register(UsersListResource)
docs.register(note.NoteResource)
docs.register(note.NotesListResource)
docs.register(TagResource)
docs.register(TagListResource)
docs.register(note.NoteSetTagsResource)
docs.register(note.NoteFilterResource)
docs.register(note.NoteToArchive)
docs.register(note.NoteFromArchive)
docs.register(UploadPictureResource)
docs.register(UsersSearchResource)


@app.route('/uploads/<path:filename>')
def download_file(filename):
   return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)
