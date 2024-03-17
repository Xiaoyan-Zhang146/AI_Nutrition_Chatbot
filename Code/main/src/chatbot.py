import sys
import os
import glob
import pdfplumber
import requests
from transformers import pipeline
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
from langchain.schema.document import Document
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser 
from selenium.webdriver.chrome.options import Options




def image2text(img_url):
	imagetotext = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large")

	text = imagetotext(img_url)[0]["generated_text"]

	return text


def question_analyze(question):
	picture_schema = ResponseSchema(name = 'picture',
					description="Do you need a picture? If yes, answer 'True'; otherwise, answer 'False'.")
	keyWord_schema = ResponseSchema(name = 'keyWord',
					description="What are the keywords for the required pictures? If the information cannot be found or no picture is needed, please output 'None'.")
					
	response_schemas = [picture_schema, keyWord_schema]
	
	output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
	format_instructions = output_parser.get_format_instructions()
	
	template = """
	According to text, extract the following information:

	picture: Need generate a picture? If yes, answer 'True'; otherwise, answer 'False'.

	keyWord: What are the keywords for the required pictures? If the information cannot be found or no picture is needed, please output 'None'.
	
	text: {text}
	
	{format_instructions}
	
	"""
	Prompt_Template = ChatPromptTemplate.from_template(template = template)
	question_prompt = Prompt_Template.format_messages(text=question, format_instructions = format_instructions)
	
	print(question_prompt)
	llm=ChatOpenAI()
	response = llm(question_prompt)
	output_dict = output_parser.parse(response.content)
	return output_dict

def get_pdf_text(pdf_docs):
	raw_text = ''
	with pdfplumber.open(pdf_docs) as pdf:
		for page in pdf.pages:    	
			raw_text += page.extract_text()
			
	return Document(page_content=raw_text)


def get_text_chunks(documents):
	text_splitter = CharacterTextSplitter(
		separator="\n",
		chunk_size=1000,
		chunk_overlap=200,
		length_function=len
	)
	split_docs = text_splitter.split_documents(documents)
	return split_docs


def get_vectorstore(text_chunks):
	embeddings = OpenAIEmbeddings()
	if text_chunks:
		vectorstore = Chroma.from_documents(text_chunks, embeddings, persist_directory="vector_store/")
	else:
		vectorstore = Chroma(persist_directory="vector_store/", embedding_function=embeddings)
	return vectorstore


def get_conversation_chain(vectorstore):
    
	memory = ConversationBufferMemory(
		memory_key='chat_history', 
		return_messages=True
	)

	conversation_chain = ConversationalRetrievalChain.from_llm(
		llm=ChatOpenAI(), 
		retriever=vectorstore.as_retriever(), 
		memory=memory
	)
	return conversation_chain

def generate_pictures(output_dict):
	print(output_dict)
	if output_dict['picture'] == "False":
		return None
	url = 'https://www.google.com/search?tbm=isch&q='+ output_dict['keyWord'] 
	options = Options()
	options.add_argument('--headless=new')
	driver = webdriver.Chrome(options=options)
	#opt = webdriver.ChromeOptions()
	#opt.headless = True              
	#driver = webdriver.Chrome(options=opt) # Configure browser driver
	driver.implicitly_wait(30)
	driver.get(url)  # load web page
	locator = (By.CLASS_NAME, "rg_i.Q4LuWd")

	ele = WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))
	soup = BeautifulSoup(driver.page_source, "html.parser")
	
	img_tag = soup.find('img', class_='rg_i Q4LuWd')
	driver.quit()

	if img_tag:
		src_value = img_tag.get('src')
		return src_value
	
	return None
		
		
def handle_userinput(user_question, conversation, output_dict = None):
	response = conversation({"question": user_question})
	print(output_dict)
	if output_dict['picture'] == 'True':
		picture = generate_pictures(output_dict)
		return "This is the picture you needed. Additionally, is there anything specific you would like to know? I'm here to help with any questions you have in mind.", picture
	return response['answer'], None


