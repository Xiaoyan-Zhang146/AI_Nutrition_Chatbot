# ChefMate: Your Exclusive AI Nutritionist

## Introduction

ChefMate is an innovative web application that serves as your exclusive AI Nutritionist. It's designed to answer your culinary questions and provide personalized nutrition advice, making your meal planning and cooking experience more informed and enjoyable.

## Project Structure

The project includes various HTML files for the user interface, a Python Flask backend, and other assets as outlined below:

```
.
├── data
│   ├── Chatbot.jpg
│   ├── ChefMate.jpg
│   ├── material.jpg
│   └── User.jpg
├── main
│   ├── index.html
│   ├── login.html
│   ├── Q_A.html
│   ├── signup.html
│   ├── src
│   │   ├── app.py
│   │   ├── chatbot.py
│   │   ├── create_database.py
│   │   ├── .env
│   │   ├── Lab4.conf
│   │   └── vector_store
│   ├── styles.css
│   └── upload.html
└── index.html

```


## Installation and Compilation

### Prerequisites

Ensure Python 3.x and pip are installed on your system.

### Steps

1. **Install Required Libraries**:
    ```bash
    pip install Flask mysql-connector-python python-dotenv pdfplumber requests transformers BeautifulSoup4 selenium langchain
2. **Configure Database**:

    - Navigate to main/src.
    - Edit Lab4.conf with your MySQL username and password.
3. **Create Database**:
    ```bash
   python3 create_database.py
4. **Set Up Environment Variables**:
    - Create or edit the .env file.
    - Add your OpenAI API key: OPENAI_API_KEY=[Your OPENAI_API_KEY].
5. **Run the Application**:
    - Open two terminal windows.
    - In the first terminal, navigate to the Project folder and run:
    ```bash
   python3 -m http.server 8000
    ```
    - In the second terminal, navigate to Project/main/src and run:
    ```bash
    python3 app.py
    ```
## Usage Instructions
1. Open your web browser and navigate to [localhost:8000/](localhost:8000/).
2. If you're a new user, please register first.
3. Log in to ChefMate.
4. Start interacting with ChefMate by asking questions to receive the answers and advice you need.

## Project Archive
The complete project archive, including all documents and source code, can be accessed [here](https://drive.google.com/drive/folders/1r-FrOgO_aauR28h2X80xMKZyKa_5UIYA?usp=sharing).