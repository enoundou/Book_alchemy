from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model): # type: ignore
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"Author({self.name}, {self.birth_date}, {self.date_of_death})"

    def __str__(self):
        return (f"Author id: {self.id}, name: {self.name}, birthdate: {self.birth_date},"
                f" date of death: {self.date_of_death}")




class Book(db.Model):   # type: ignore
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    isbn = db.Column(db.String(100), unique=True, nullable=True)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)

    author = db.relationship('Author', backref=db.backref('books', cascade="all, delete-orphan"))

    def __repr__(self):
        return f"Book({self.isbn}, {self.author_id}, {self.title}, {self.publication_year })"

    def __str__(self):
        author_name = self.author.name if self.author else None
        return f"{self.title} ({author_name}, {self.publication_year})"




