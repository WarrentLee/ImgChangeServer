import sys
sys.path.append("..")
print(sys.path)
from flask import Blueprint, Flask, render_template
from authentication import login_manager
from flask_restplus import Api
import requests, os
from api.utils import create_app
from api.user import api as ns_user
from api.image import api as ns_img
from api.change import api as ns_change
from config import Config

os.environ['DATABASE_URL'] = 'sqlite:///' + Config.DATABASE_DIRECTORY
blueprint = Blueprint('api', __name__, url_prefix='/api')  # 创建一个falsk蓝图

# 将蓝图生成api
api = Api(
    blueprint,
    title='ImgChange',
    version='1.0',
)

# Remove default namespace
api.namespaces.pop(0)

# Setup API namespaces
api.add_namespace(ns_user)
api.add_namespace(ns_img)
api.add_namespace(ns_change)
# 创建一个flask应用并注册蓝图生成的api
app = create_app(__name__)
login_manager.init_app(app)  # 初始化应用
login_manager.login_view = 'login'  # 设置用户登录视图函数 endpoint
app.register_blueprint(blueprint)

if __name__ == '__main__':  # 建立项目时选择了flask项目，此处不会直接执行这个py文件，而是递交给flask框架去执行
    app.run(host="0.0.0.0")
