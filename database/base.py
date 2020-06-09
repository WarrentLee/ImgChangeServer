# from sqlalchemy import create_engine, MetaData
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# import os
#
# dir = os.getcwd()
# engine = create_engine("sqlite:///" + dir + "base.db", echo=True)  # 可以看到调试信息
# Base = declarative_base()
# metadata = MetaData(engine)
# Session = sessionmaker()
# Session.configure(bind=engine)
# session = Session()