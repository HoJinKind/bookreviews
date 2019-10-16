from flask import Blueprint, render_template, redirect, session, url_for, request, jsonify
from werkzeug.security import generate_password_hash
from books.data_service import get_first_10_books
from books.data_service import get_book_by_asin
from application import db
from books.models import Review

book_app = Blueprint('book_app', __name__)

'''
@book_app.route('/book/<asin>/reviews', methods=['GET'])
def get_reviews(asin):
    results = Review.query.filter_by(asin=asin)
    reviews = []
    for result in results:
        reviews.append(result.serialize())
    return jsonify(reviews)
    #return render_template('book.html', reviews=reviews)
'''


@book_app.route('/browse', methods=['GET'])
def get_meta_data():
    msg=''
    if request.args:
        msg= request.args['msg']

    first_10_books = get_first_10_books()
    books =[]   
    for book in first_10_books:
        books.append(book.serialize())
    return render_template('browse.html', arrayOfBooks= books, msg=msg)

@book_app.route('/searchbyasin', methods=['GET'])
def get_byasin():
    first_10_books = get_book_by_asin('B0002IQ15S')
    books =[]
    for book in first_10_books:
        books.append(book.serialize())
    return render_template('browse.html', arrayOfBooks= books)


@book_app.route('/books/<asin>', methods=['GET', 'POST'])
def get_book(asin):

    # if a review is submitted
    if request.method == 'POST':
        asin = asin
        reviewText = request.form['reviewText']
        review = Review(asin, reviewText)
        db.session.add(review)
        db.session.commit()

    # query asin from mongo and mysql 
    book = get_book_by_asin(asin) 

    # if a book is found
    if (len(book) > 0):
        book = book[0]
        reviews = Review.query.filter_by(asin=asin).all()
        reviews = reviews[::-1] #sort by latest
        return render_template('book.html', reviews=reviews, book=book)
    else:
        err_msg = 'Book not found.'
        return redirect(url_for('.get_meta_data', msg=err_msg))

"""
#add a book review
@book_app.route('/add/', methods=['GET','POST'])
def add_review():
    if request.method == 'POST':
        asin = request.form['asin']
        summary = request.form['summary']
        print(request.form['summary'])
        print(summary)
        review = Review(asin, summary)
        db.session.add(review)
        db.session.commit()
        print(f'review_id: {review.id}')
        return f'review_id: {review.id}'


    return render_template('add_review_test.html')

"""