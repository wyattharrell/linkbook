from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import os
import pyrebase

"""
WEBSCRAPING LIBRARIES
"""
api_key = ""
from newspaper import Article

import lxml
import urllib3
import webbrowser
import requests
import nltk
import argparse

from bs4 import BeautifulSoup
from googleapiclient.discovery import build

"""
FLASK VARIABLES
"""

app = Flask(__name__)

footer = "Copyright 2019 Linkbook. All rights reserved."

class store:
    def __init__(self):
        self.link_name = ""
        self.count = 0

    def clear(self):
        self.link_name = ""
        self.count = 0

    def increment(self):
        self.count += 1

    def name_change(self, name):
        self.link_name = name


Storage = store()

class user:
	def __init__(self):
		self.user = ""

	def setUser(self, user):
		self.user = user

	def clearUser(self):
		self.user = ""

	def getUser(self):
		return self.user

User = user()

"""
FIREBASE CONFIGURATION 
"""

config = {
	"apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": ""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
accountID = None

"""
FLASK PAGES // TEMPLATES
"""

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Linkbook - Home', footer=footer)

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""
	MESSAGES
	"""
	global accountID
	unsuccessful = 'Invalid username or password'
	successful = 'Login successful'
	"""
	IF LOGIN ATTEMPTED
	"""
	if request.method == 'POST':
		email = request.form['name']
		password = request.form['pass']
		try:
			user = auth.sign_in_with_email_and_password(email, password)
			# accountID = auth.get_account_info(user['idToken'])
			accountID = email.replace('.', '')
			User.setUser(accountID)
			return redirect('categories')
		except:
			return render_template('login.html', us=unsuccessful)
	return render_template('login.html', title='Linkbook - Log In', footer=footer)

@app.route('/register', methods=['GET', 'POST'])
def register():
	"""
	MESSAGES
	"""
	unsuccessful = 'Invalid username or password'
	successful = 'Login successful'
	"""
	IF REGISTER ATTEMPTED
	"""
	if request.method == 'POST':
		email = request.form['name']
		password = request.form['pass']
		try:
			user = auth.create_user_with_email_and_password(email, password)
			auth.send_email_verification(user['idToken'])
			# accountID = auth.get_account_info(user['idToken'])
			accountID = email.replace('.', '')
			User.setUser(accountID)
			return redirect('categories')
		except:
			return render_template('register.html', us=unsuccessful)
	return render_template('register.html', title='Linkbook - Register', footer=footer)

@app.route('/categories', methods=['GET', 'POST'])
def categories():
	"""
	IF USER IS NOT LOGGED IN
	"""
	if (User.getUser() == ""):
		return redirect('login')
	"""
	RETRIEVE CATEGORIES FROM DATABASE
	"""
	listOfCategories = []
	try:
		categories = db.child(User.getUser()).child("Categories").get()
		for x in categories.each():
			listOfCategories.append(x.key())
	except:
		listOfCategories.append("Try Adding a Category!")
	"""
	DELETE CATEGORY FROM DATABASE
	"""
	clickedDelete = request.args.get('delete')
	clickedCategory = request.args.get('type')

	if clickedDelete == 'True':
		db.child(User.getUser()).child("Categories").child(clickedCategory).remove()
		clickedDelete = 'False'
		return redirect('categories')
	"""
	CREATE NEW CATEGORY VIA FORM
	"""
	if request.method == 'POST':
		global newCategory
		newCategory = request.form['category']
		return redirect('links')
	return render_template('categories.html', title='Linkbook - Categories', footer=footer, listOfCategories=listOfCategories)

@app.route('/links', methods=['GET', 'POST'])
def links():
	"""
	IF USER IS NOT LOGGED IN
	"""
	if (User.getUser() == ""):
		return redirect('login')
	#REVISIT FROM CATEGORIES PAGE
	global newCategory
	listOfLinks = []
	"""
	ADD NEW LINK TO DATABASE
	"""
	if request.method == 'POST':
		url = request.form['link']
		title = getTitle(url)
		summary = getSummary(url)
		imageLocation = getScreenshot(url)
		if imageLocation == "":
			imageLocation = "static/none.png"
		host = getHost(url)
		data = {
		    "TITLE": title, 
		    "SUMMARY": summary, 
		    "URL": url,
		    "IMAGE": imageLocation,
		    "HOST": host
		}
		hashedURL = hash(url);
		db.child(User.getUser()).child("Categories").child(newCategory).child(hashedURL).set(data)
	"""
	DELETE LINK FROM DATABASE OR RELATED
	"""
	clickedDelete = request.args.get('delete')
	clickedShare = request.args.get('share')

	clickedCategory = request.args.get('type')
	clickedLink = request.args.get('title')

	if clickedDelete == 'True':
		linkToDelete = db.child(User.getUser()).child("Categories").child(clickedCategory).order_by_child("TITLE").equal_to(clickedLink).get()
		print(linkToDelete)
		clickedDelete = 'False'
	if clickedShare == 'True':
		title = clickedLink[:15] if len(clickedLink) > 20 else clickedLink
		recommend(title)
		clickedShare == 'False'
		return redirect('links')
	"""
	CATEGORY CLICKED FROM /CATEGORIES PAGE
	"""
	clickedCategory = request.args.get('type')
	global categoryClickCounts
	if clickedCategory not in categoryClickCounts.keys():
  		categoryClickCounts[clickedCategory] = 0
	categoryClickCounts[clickedCategory] += 1

	if clickedCategory != None:
		newCategory=clickedCategory
		getLinks(listOfLinks,newCategory)
		return render_template('links.html', title='Linkbook', footer=footer, category=clickedCategory, listOfLinks=listOfLinks)
	
	getLinks(listOfLinks,newCategory)
	return render_template('links.html', title='Linkbook', footer=footer, category=newCategory, listOfLinks=listOfLinks)

@app.route('/all')
def all():
	"""
	IF USER IS NOT LOGGED IN
	"""
	if (User.getUser() == ""):
		return redirect('login')
	"""
	FETCH ALL LINKS
	"""
	listOfLinks = []
	numberOfLinks=0
	numOfCategories=0
	cats = db.child(User.getUser()).child("Categories").shallow().get()
	keys = list(cats.val())
	numOfCategories = len(keys)
	for x in keys:
		links = db.child(User.getUser()).child("Categories").child(x).get()
		for x in links.each():
			listOfLinks.append(x.val())
			numberOfLinks = numberOfLinks + 1

	"""
	DELETE LINK FROM DATABASE OR RELATED
	"""
	clickedDelete = request.args.get('delete')
	clickedShare = request.args.get('share')

	clickedCategory = request.args.get('type')
	clickedLink = request.args.get('title')

	if clickedDelete == 'True':
		linkToDelete = db.child(User.getUser()).child("Categories").child(clickedCategory).order_by_child("TITLE").equal_to(clickedLink).get()
		print(linkToDelete)
		clickedDelete = 'False'
	if clickedShare == 'True':
		title = clickedLink[:15] if len(clickedLink) > 20 else clickedLink
		recommend(title)
		clickedShare == 'False'
		return redirect('links')

	return render_template('all.html', title='Linkbook - All Links', footer=footer, category=newCategory, listOfLinks=listOfLinks, numberOfLinks=numberOfLinks, numOfCategories=numOfCategories)

@app.route('/dashboard')
def dashboard():
	"""
	IF USER IS NOT LOGGED IN
	"""
	if (User.getUser() == ""):
		return redirect('login')
	"""
	DELETE ALL FROM DATABASE
	"""
	clickedDelete = request.args.get('delete')

	if clickedDelete == 'True':
		db.child(User.getUser()).child("Categories").remove()
		clickedDelete = 'False'
		return redirect('categories')
	"""
	GET DATA FOR GRAPHS
	"""
	try:
		cats = db.child(User.getUser()).child("Categories").shallow().get()
		keys = list(cats.val())

		numOfCategories = len(keys)

		numberOfLinks = []
		maxY = 0
		listOfLinks = []
		counter = 0
		totalNumberOfLinks = 0
		for x in keys:
			links = db.child(User.getUser()).child("Categories").child(x).get()
			for x in links.each():
				# print(x.key())
				counter = counter + 1
				totalNumberOfLinks = totalNumberOfLinks + 1
			numberOfLinks.append(counter)
			if maxY < counter:
				maxY = counter
			counter = 0

		lengthOfBars = 100 / numOfCategories
		totalNumberOfCategories = numOfCategories

		listOfClicks = []
		maxClicks = 0
		for x in categoryClickCounts.values():
			listOfClicks.append(x)
			if x > maxClicks:
				maxClicks = x

		maxY = maxY + 5 # for graph y value
		maxClicks = maxClicks + 5 # for graph y value
		return render_template('dashboard.html', title='Linkbook - Dashboard', footer=footer, keys=keys, numOfCategories=numOfCategories, lengthOfBars=lengthOfBars, numberOfLinks=numberOfLinks, maxY=maxY, totalNumberOfLinks=totalNumberOfLinks, totalNumberOfCategories=totalNumberOfCategories, listOfClicks=listOfClicks, maxClicks=maxClicks)
	except:
		pass
	return render_template('dashboard.html', title='Linkbook - Dashboard', footer=footer)

@app.route('/logout')
def logout():
	User.clearUser()
	return render_template('home.html', title='Linkbook - Home', footer=footer)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

"""
HELPER FUNCTIONS
"""
def getLinks(listOfLinks,newCategory):	
	try:
		links = db.child(User.getUser()).child("Categories").child(newCategory).get()
		for x in links.each():
			# print(x.key())
			listOfLinks.append(x.val())
	except:
		pass

def getHost(newURL):
	host = newURL
	host = host.split("//")[-1].split("/")[0].split('?')[0]
	host = host.replace('www.', '')
	return host

def getTitle(newURL): 
	try:
		result = requests.get(newURL)
		src = result.content
		soup = BeautifulSoup(src, 'lxml')
		title = soup.title.string
		#title = (title[:64] + '..') if len(title) > 20 else title
		return title
	except:
		title = getHost(newURL)
		return title

def getSummary(newURL): 
	try:
		article = Article(newURL)
		article.download() #Downloads the link’s HTML content
		article.parse() #Parse the article
		#nltk.download('punkt') #1 time download of the sentence tokenizer
		article.nlp()#  Keyword extraction wrapper
		summary = article.summary
		summary = summary.replace('#Description: ', '')
		summary = (summary[:98] + '..') if len(summary) > 20 else summary
		return summary
	except:
		summary = "Error: No summary could be gathered."
		return summary

def getScreenshot(newURL):
	try:
		article = Article(newURL)
		article.download() #Downloads the link’s HTML content
		article.parse() #Parse the article
		#nltk.download('punkt') #1 time download of the sentence tokenizer
		article.nlp()#  Keyword extraction wrapper
		return article.top_image
	except:
		summary = "/static/none.png"

def recommend(query):  # search query
    if query != Storage.link_name:
        Storage.clear()
        Storage.name_change(query)
    elif query == "":
        return
    resource = build("customsearch", 'v1', developerKey=api_key).cse()
    result = resource.list(q=Storage.link_name, cx='009557628044748784875:5lejfe73wrw').execute()
    try:
        Storage.increment()
        webbrowser.open_new_tab(result['items'][Storage.count]['link'])
    except:
        print("Error")
"""
PYTHON MAIN
"""

if __name__ == '__main__':
	newCategory = None
	categoryClickCounts = {}
	app.run(debug=True)

