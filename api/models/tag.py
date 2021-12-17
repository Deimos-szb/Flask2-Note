from api import db
from sqlalchemy.exc import IntegrityError

# class BaseModel(db.Model):
#    def save(self):
#       try:
#          db.session.add(self)
#          db.session.commit()
#       except IntegrityError:  # Обработка ошибки "создание пользователя с НЕ уникальным именем"
#          db.session.rollback()

class TagModel(db.Model):
   __tablename__ = 'tag'
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(64), unique=True, nullable=False)

   def save(self):
      try:
         db.session.add(self)
         db.session.commit()
      except IntegrityError:  # Обработка ошибки "создание пользователя с НЕ уникальным именем"
         db.session.rollback()