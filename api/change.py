from flask import send_file
from flask_login import login_required, current_user
from flask_restplus import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage

from config import Config
from database.model import ImageModel
import os, io
from PIL import Image
from workbench.deal import deal_args, deal

api = Namespace('change', description='Image related operations')

image_change = reqparse.RequestParser()
image_change.add_argument('image', location='files',
                          type=FileStorage, required=True,
                          help='PNG or JPG file')
image_change.add_argument('folder', required=False, default='',
                          help='Folder to save the changed image')
image_change.add_argument('asAttachment', type=bool, default=False)


@api.route('/')
class Change(Resource):

    @api.expect(image_change)
    def post(self):
        args = image_change.parse_args()
        as_attachment = args['asAttachment']
        GAN_arg = deal_args()
        GAN_arg.img_file = args['image']
        GAN_arg.save_dir = args['folder']
        print(GAN_arg.checkpoint_dir, "\n", GAN_arg.img_file, "\n", GAN_arg.save_dir)
        pil_image = Image.open(args['image'])
        width = pil_image.size[0]
        height = pil_image.size[1]
        changed_img = deal(GAN_arg.checkpoint_dir, GAN_arg.save_dir, GAN_arg.img_file, img_size=[width, height])
        pil_image = Image.open(changed_img)
        image_io = io.BytesIO()
        pil_image = pil_image.convert("RGB")
        pil_image.save(image_io, "JPEG", quality=90)
        image_io.seek(0)
        return send_file(image_io, attachment_filename="changed_image", as_attachment=as_attachment)

    @api.expect(image_change)
    def get(self):
        args = image_change.parse_args()
        image = args.image
        as_attachment = args.asAttachment
        pil_image = Image.open(image)
        image_io = io.BytesIO()
        pil_image = pil_image.convert("RGB")
        pil_image.save(image_io, "JPEG", quality=90)
        image_io.seek(0)
        return send_file(image_io, attachment_filename="changed_image", as_attachment=as_attachment)


