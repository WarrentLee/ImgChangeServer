from flask import send_file
from flask_login import login_required, current_user
from flask_restplus import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage

from config import Config
from database.model import ImageModel
import os, io
from PIL import Image

api = Namespace('image', description='Image related operations')

image_all = reqparse.RequestParser()
image_all.add_argument('page', default=1, type=int)
image_all.add_argument('per_page', default=50, type=int, required=False)

image_upload = reqparse.RequestParser()
image_upload.add_argument('image', location='files',
                          type=FileStorage, required=True,
                          help='PNG or JPG file')
image_upload.add_argument('folder', required=False, default='',
                          help='Folder to insert photo into')

image_download = reqparse.RequestParser()
image_download.add_argument('asAttachment', type=bool, default=False)
# image_download.add_argument('thumbnail', type=bool, default=False)
image_download.add_argument('width', type=int)
image_download.add_argument('height', type=int)


@api.route('/')
class Images(Resource):

    @api.expect(image_all)
    @login_required
    def get(self):
        """ Returns all images """
        args = image_all.parse_args()
        per_page = args['per_page']
        page = args['page'] - 1

        images = current_user.images
        total = len(images)
        pages = int(total / per_page) + 1
        if (page + 1) * per_page < total:
            images = images[page * per_page:(page + 1) * per_page]
        else:
            images = images[page * per_page:]
        img_ids = []
        for i in images:
            img_ids.append(i.id)
        return {
            "user_id": current_user.id,
            "total": total,
            "pages": pages,
            "page": page,
            "per_page": per_page,
            "images": img_ids
        }

    @api.expect(image_upload)
    @login_required
    def post(self):
        """ Creates an image """
        args = image_upload.parse_args()
        image = args['image']

        folder = args['folder']
        if len(folder) > 0:
            folder = folder[0].strip('/') + folder[1:]

        directory = os.path.join(Config.DATASET_DIRECTORY, current_user.username + folder)
        path = os.path.join(directory, image.filename)

        if os.path.exists(path):
            return {'message': 'file already exists'}, 400

        if not os.path.exists(directory):
            os.makedirs(directory)

        pil_image = Image.open(io.BytesIO(image.read()))

        image_model = ImageModel(
            user_id=current_user.id,
            file_name=image.filename,
            width=pil_image.size[0],
            height=pil_image.size[1],
            img_uri=path
        )

        image_model.save()
        pil_image.save(path)

        image.close()
        pil_image.close()
        return {'success': True,
                "user_id": current_user.id,
                "file_name": image.filename,
                "width": pil_image.size[0],
                "height": pil_image.size[1]
                }


@api.route('/<int:image_id>')
class ImageId(Resource):

    @api.expect(image_download)
    @login_required
    def get(self, image_id):
        """ Returns an image by ID """
        args = image_download.parse_args()
        as_attachment = args.get('asAttachment')
        image = ImageModel()
        for img in current_user.images:
            if img.id == image_id:
                image = img
                break

        if image is None:
            return {'success': False}, 400

        width = args.get('width')
        height = args.get('height')

        if not width:
            width = image.width
        if not height:
            height = image.height

        pil_image = Image.open(image.img_uri)
        pil_image.thumbnail((width, height), Image.ANTIALIAS)
        image_io = io.BytesIO()
        pil_image = pil_image.convert("RGB")
        pil_image.save(image_io, "JPEG", quality=90)
        image_io.seek(0)

        return send_file(image_io, attachment_filename=image.file_name, as_attachment=as_attachment)

    @login_required
    def delete(self, image_id):
        """ Deletes an image by ID """
        image = ImageModel()
        flag = 0
        for img in current_user.images:
            if img.id == image_id:
                image = img
                flag = 1
                break
        if flag == 0:
            return {"message": "Invalid image id"}, 400

        # if not current_user.can_delete(image):
        #     return {"message": "You do not have permission to download the image"}, 403
        image.remove()
        path = image.img_uri  # 文件路径
        if os.path.exists(path):  # 如果文件存在
            # 删除文件，可使用以下两种方法。
            os.remove(path)
            # os.unlink(path)
            return {"success": True}
        else:
            return{'no such image:(%s)%s' % (current_user.username, image_id)}  # 则返回文件不存在


