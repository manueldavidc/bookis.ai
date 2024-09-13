import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_file, jsonify, stream_with_context, Response
from flask_login import LoginManager, login_required, current_user
from models import db, User, Book
from forms import BookGenerationForm
from story_generator import generate_story
from image_generator import generate_images
from pdf_generator import generate_pdf
from content_moderator import moderate_content
from auth import auth as auth_blueprint
import logging
import json

app = Flask(__name__)
app.config.from_object('config.Config')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

app.register_blueprint(auth_blueprint)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    books = Book.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', books=books)

@app.route('/create_book', methods=['GET', 'POST'])
@login_required
def create_book():
    form = BookGenerationForm()
    if form.validate_on_submit():
        def generate():
            yield (jsonify({"progress": 5, "status": "Starting book creation..."}).data + b'\n')
            
            # Generate story and title
            yield (jsonify({"progress": 10, "status": "Generating story..."}).data + b'\n')
            try:
                title, story_pages = generate_story(form.educational_objective.data, form.age.data, 
                                                    form.characters.data, form.setting.data, form.book_length.data)
            except Exception as e:
                app.logger.error(f"Error generating story: {e}")
                yield (jsonify({"progress": 100, "status": "An error occurred while generating the story. Please try again."}).data + b'\n')
                return
            yield (jsonify({"progress": 25, "status": "Story generated successfully."}).data + b'\n')
            
            # Moderate content
            yield (jsonify({"progress": 30, "status": "Moderating content..."}).data + b'\n')
            story_text = ' '.join([page['text'] for page in story_pages])
            if not moderate_content(story_text):
                yield (jsonify({"progress": 100, "status": "The generated content was not appropriate. Please try again with different inputs."}).data + b'\n')
                return
            yield (jsonify({"progress": 40, "status": "Content moderation completed."}).data + b'\n')
            
            # Generate images
            yield (jsonify({"progress": 45, "status": "Generating images..."}).data + b'\n')
            image_prompts = [page['image_description'] for page in story_pages]
            image_urls = generate_images(image_prompts, form.age.data)
            
            if not image_urls:
                yield (jsonify({"progress": 100, "status": "Failed to generate images. Please try again."}).data + b'\n')
                return
            yield (jsonify({"progress": 60, "status": "Images generated successfully."}).data + b'\n')
            
            # Combine story pages with image URLs
            for page, image_url in zip(story_pages, image_urls):
                page['image_url'] = image_url
            
            # Generate PDF
            yield (jsonify({"progress": 70, "status": "Generating PDF..."}).data + b'\n')
            pdf_buffer = generate_pdf(title, story_pages, form.age.data)  # Updated line
            yield (jsonify({"progress": 80, "status": "PDF generated successfully."}).data + b'\n')
            
            # Save PDF to file
            pdf_filename = f"book_{current_user.id}_{title.replace(' ', '_')}.pdf"
            pdf_path = os.path.join(app.static_folder, 'pdfs', pdf_filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            with open(pdf_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            yield (jsonify({"progress": 90, "status": "PDF saved successfully."}).data + b'\n')
            
            # Create book
            new_book = Book(title=title, content=json.dumps(story_pages), 
                            user_id=current_user.id, pdf_path=pdf_path)
            db.session.add(new_book)
            db.session.commit()
            
            # Debug logging
            app.logger.debug(f"Book saved to database with ID: {new_book.id}")
            
            yield (jsonify({"progress": 100, "status": "Book created successfully!", "redirect": url_for('view_book', book_id=new_book.id)}).data + b'\n')

        return Response(stream_with_context(generate()), content_type='application/json', mimetype='application/json')
    
    return render_template('create_book.html', form=form)

@app.route('/view_book/<int:book_id>')
@login_required
def view_book(book_id):
    book = db.session.get(Book, book_id)
    
    # Debug logging
    app.logger.debug(f"Retrieving book with ID: {book_id}")
    if book:
        app.logger.debug(f"Book details: Title: {book.title}, Content length: {len(book.content)}")
    else:
        app.logger.debug(f"Book with ID {book_id} not found")
    
    if not book:
        flash('Book not found.')
        return redirect(url_for('dashboard'))
    if book.user_id != current_user.id:
        flash('You do not have permission to view this book.')
        return redirect(url_for('dashboard'))
    
    # Check if the book has content
    if not book.content:
        flash('The book content is missing.')
        return redirect(url_for('dashboard'))
    
    # Parse the JSON content
    book.pages = json.loads(book.content)
    
    return render_template('view_book.html', book=book)

@app.route('/download_pdf/<int:book_id>')
@login_required
def download_pdf(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash('Book not found.')
        return redirect(url_for('dashboard'))
    if book.user_id != current_user.id:
        flash('You do not have permission to download this book.')
        return redirect(url_for('dashboard'))
    return send_file(book.pdf_path, as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create all tables
    app.run(host='0.0.0.0', port=5000, debug=True)
