from sqlalchemy import orm

TestGlobalSession = orm.scoped_session(orm.sessionmaker())
