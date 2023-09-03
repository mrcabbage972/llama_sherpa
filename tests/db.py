from app.db.db import User, SessionLocal


def test_user():
    sess = SessionLocal()
    sess.add(User(username="h", password="h", email="g", is_superuser=False))
    sess.commit()
    users = sess.query(User).all()
    assert len(users) == 1
