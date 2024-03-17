from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import chatbot
from dotenv import load_dotenv
import uuid
import hashlib
import mysql.connector
import pandas as pd
import configparser


app = Flask(__name__)
CORS(app)

# Configure the target folder for file uploads
PDF_FOLDER = 'pdf/'
app.config['PDF_FOLDER'] = PDF_FOLDER

IMAGE_FOLDER = 'image/'
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

# Check if the target folder exists, and create it if it doesn't
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)


@app.route('/upload_Image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'message': 'No image provided', 'state': 'failure'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No image selected', 'state': 'failure'})

    file.save(os.path.join(app.config['IMAGE_FOLDER'], file.filename))
    return jsonify({'message': f'Image {file.filename} uploaded successfully', 'state': 'success', 'image':f'{file.filename}'})
    
@app.route('/upload', methods=['POST'])
def upload_file():
    load_dotenv()
    uploaded_files = request.files.getlist('pdfFiles')

    if len(uploaded_files) == 0:
        return jsonify({'message': 'No files uploaded'})

    for file in uploaded_files:
        documents = []
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['PDF_FOLDER'], filename))
        documents.append(chatbot.get_pdf_text(PDF_FOLDER+'/'+filename))
    split_docs = chatbot.get_text_chunks(documents)
    vector_store = chatbot.get_vectorstore(split_docs)
    return jsonify({'message': 'Upload files successful!'})

@app.route('/get_answer', methods=['POST'])
def get_answer():
    load_dotenv()
    data = request.get_json()
    question = data.get('question')
    user_id = data.get('id')
    print(question)
    question = get_user_info(user_id)+question
    print(question)
    print(user_id)
    vector_store = chatbot.get_vectorstore(None)
    conversation = chatbot.get_conversation_chain(vector_store)
    output_dict = chatbot.question_analyze(question)
    answer, picture = chatbot.handle_userinput(question, conversation, output_dict)

    return jsonify({'answer': answer, 'picture': picture})


@app.route('/getImageRecipe', methods=['POST'])
def getImageRecipe():
    data = request.get_json()
    image = data.get('image')
    print(image)
    description = chatbot.image2text(image)
    
    question = """
	Below is a description of the picture. The picture shows the ingredients I have. 
	Please choose one or more of them and tell me a recipe.
	At beginning of your answer, briefly state what are in the picture.
	Description of the picture:
	"""
    question += f'{description}'
    print(question)
    vector_store = chatbot.get_vectorstore(None)
    conversation = chatbot.get_conversation_chain(vector_store)
    answer, picture = chatbot.handle_userinput(question, conversation)

    return jsonify({'answer': answer})
    

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print(data)
    age = data['age']
    gender = data['gender']
    name = data['name']
    username = data['username']
    password = data['password']
    food = data['food']
    allergen = data['allergen']
    
    if password == '':
        return jsonify({'state': False, 'reason':'password cannot be blank'})
    if username == '':
        return jsonify({'state': False, 'reason':'username cannot be blank'})
    
    # Connect to MySQL
    config = configparser.ConfigParser()
    config.read("Lab4.conf")

    conn = mysql.connector.connect(
	host=config['MySQL']['host'],
	user=config['MySQL']['user'],
	password=config['MySQL']['password']
    )
    cursor = conn.cursor()
    try:
        cursor.execute("USE chatbot")
        user_id = str(uuid.uuid4())

        encrypted_password = hashlib.md5(password.encode()).hexdigest()

        sql = "INSERT INTO user (id, username, password, name, age, gender, food, allergen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (user_id, username, encrypted_password, name, age, gender, food, allergen))
        conn.commit()
    finally:
        conn.close()
    return jsonify({'state': True})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(data)
    
    username = data['username']
    password = data['password']

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # Connect to MySQL
    config = configparser.ConfigParser()
    config.read("Lab4.conf")

    conn = mysql.connector.connect(
	host=config['MySQL']['host'],
	user=config['MySQL']['user'],
	password=config['MySQL']['password']
    )
    cursor = conn.cursor()
    cursor.execute("USE chatbot")
    try:
        

        sql = "SELECT id, name FROM user WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, hashed_password))
        result = cursor.fetchone()
        print(result)
        if result:
            return jsonify({"id": result[0], "name": result[1], 'state': True})
        else:
            return jsonify({'state': False, "message": "Incorrect User Name or Password"})
    finally:
        conn.close()


def get_user_info(user_id):
   # Connect to MySQL
    config = configparser.ConfigParser()
    config.read("Lab4.conf")

    conn = mysql.connector.connect(
	host=config['MySQL']['host'],
	user=config['MySQL']['user'],
	password=config['MySQL']['password']
    )
    cursor = conn.cursor()
    cursor.execute("USE chatbot")
    try:
        

        sql = "SELECT name, age, food, allergen FROM user WHERE id = '"+user_id+"'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            output = f"Hi, I am {result[0]}, I am {result[1]} years old, and my favorite food is: {result[2]}. However, I'm allergic to {result[3]}, my question is:"
            return output
        else:
            return ""
    finally:
        conn.close()

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)
