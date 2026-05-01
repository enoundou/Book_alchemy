import os
from datetime import datetime

from flask import Flask, request, render_template, flash, redirect, url_for
from sqlalchemy import or_

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SECRET_KEY'] = 'super-secret-key'

db.init_app(app)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    add new author
    :return: direct to add author if method= get, if post return success message within author information
    """
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            return f"Author name is required"

        birth_date = request.form.get('birth_date')
        if birth_date:
            birth_date = datetime.strptime(request.form.get('birth_date'), "%Y-%m-%d").date()
        else:
            birth_date = None

        date_of_death = request.form.get('date_of_death')
        if date_of_death:
            date_of_death = datetime.strptime(date_of_death, "%Y-%m-%d").date()
        else:
            date_of_death = None

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death)

        db.session.add(new_author)
        db.session.commit()

        flash(f"Author '{new_author.name}' was successfully added!", "success")
        return redirect(url_for('home'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    add new book
    :return: go to add book HTML if methods= get, if post return success message within book information
    """
    if request.method == 'POST':
        new_book = Book(
            title=request.form.get('title'),
            author_id=int(request.form.get('author_id')),
            isbn=request.form.get('isbn'),
            publication_year=int(request.form.get('publication_year')))

        db.session.add(new_book)
        db.session.commit()

        flash(f"Book '{new_book.title}' was successfully added!", "success")
        return redirect(url_for('home'))

    authors = Author.query.order_by(Author.name).all()
    return render_template('add_book.html', authors=authors)


@app.route('/', methods=['GET'])
def home():
    """
    get home page
    :return: go to home page
    """
    search_text = request.args.get('search')

    sort = request.args.get('sort')
    direction = request.args.get('direction')
    if sort and not direction:
        direction = 'asc'

    query = Book.query.join(Author)

    if search_text:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search_text}%"),
                Author.name.ilike(f"%{search_text}%"),
                Book.isbn.ilike(f"%{search_text}%")
            )
        )
    if sort == 'title':
        column = Book.title
    elif sort == 'author':
        column = Author.name
    else:
        column = None

    if column is not None:
        if direction == 'desc':
            column = column.desc()
        query = query.order_by(column)

    books = query.all()

    return render_template('home.html', books=books, direction=direction)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    delete book with id= book_id
    :param book_id: id of book
    :return: redirect to home page
    """
    book = db.session.get(Book, book_id)

    if not book:
        flash("Book not found", "error")
        return redirect(url_for('home'))

    title = book.title
    author = book.author

    db.session.delete(book)
    db.session.flush()

    if author and len(author.books) == 0:
        db.session.delete(author)

    db.session.commit()

    flash(f"Book '{title}' was successfully deleted!", "success")
    return redirect(url_for('home'))


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """
    delete author with id= author_id
    :param author_id: id of author
    :return: redirect to home page
    """
    author = db.session.get(Author, author_id)

    if not author:
        flash("Author not found", "error")
        return redirect(url_for('home'))

    name = author.name

    db.session.delete(author)
    db.session.commit()

    flash(f"Author '{name}' was successfully deleted!", "success")
    return redirect(url_for('home'))


def main():
    authors = [
        Author(name="Jane Austen", birth_date=datetime.strptime("1775-12-16", "%Y-%m-%d").date(),
               date_of_death=datetime.strptime("1817-07-18", "%Y-%m-%d").date()),
        Author(name="George Orwell", birth_date=datetime.strptime("1903-06-25", "%Y-%m-%d").date(),
               date_of_death=datetime.strptime("1950-01-21", "%Y-%m-%d").date()),
        Author(name="J.K. Rowling", birth_date=datetime.strptime("1965-07-31", "%Y-%m-%d").date(),
               date_of_death=None),
        Author(name="Mark Twain", birth_date=datetime.strptime("1835-11-30", "%Y-%m-%d").date(),
               date_of_death=datetime.strptime("1910-04-21", "%Y-%m-%d").date()),
        Author(name="Agatha Christie", birth_date=datetime.strptime("1890-09-15", "%Y-%m-%d").date(),
               date_of_death=datetime.strptime("1976-01-12", "%Y-%m-%d").date())
    ]
    db.session.add_all(authors)
    db.session.commit()

    books = [
        Book(author_id=authors[0].id, isbn="9780141439518", title="Pride and Prejudice",
             publication_year=1813),
        Book(author_id=authors[0].id, isbn="9780141439662", title="Sense and Sensibility",
             publication_year=1811),

        Book(author_id=authors[1].id, isbn="9780451524935", title="1984",
             publication_year=1949),
        Book(author_id=authors[1].id, isbn="9780451526342", title="Animal Farm",
             publication_year=1945),

        Book(author_id=authors[2].id, isbn="9780747532699", title="Harry Potter and the Philosopher's Stone",
             publication_year=1997),
        Book(author_id=authors[2].id, isbn="9780747538493", title="Harry Potter and the Chamber of Secrets",
             publication_year=1998),

        Book(author_id=authors[3].id, isbn="9780486280615", title="Adventures of Huckleberry Finn",
             publication_year=1884),
        Book(author_id=authors[3].id, isbn="9780486400778", title="The Adventures of Tom Sawyer",
             publication_year=1876),

        Book(author_id=authors[4].id, isbn="9780062073488", title="Murder on the Orient Express",
             publication_year=1934),
        Book(author_id=authors[4].id, isbn="9780062073501", title="And Then There Were None",
             publication_year=1939)
    ]

    db.session.add_all(books)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if db.session.query(Book.author_id).count() == 0:
            main()

    app.run(host="0.0.0.0", port=5000, debug=True)
