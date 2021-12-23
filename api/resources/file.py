import os
from config import Config, ma_plugin
from api import api
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from marshmallow import fields


@ma_plugin.map_to_openapi_type('file', None)
class FileField(fields.Raw):
    pass

@api.resource('/upload') #PUT
@doc(tags=['Files'])
class UploadPictureResource(MethodResource):
    @use_kwargs({"image": FileField(required=True)}, location="files")
    def put(self, **kwargs):
        uploaded_file = kwargs["image"]
        if Config.UPLOAD_FOLDER:
            target = os.path.join(Config.UPLOAD_FOLDER, uploaded_file.filename)
        else:
            pass #TODO: Make folder automaticaly
        uploaded_file.save(target)
        return {"msg": "uploaded image successfully",
                "url": os.path.join(Config.UPLOAD_FOLDER_NAME, uploaded_file.filename)}, 200
