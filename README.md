<div align="center">
	<img src="static/linkbook_logo_main.png" alt="Linkbook Logo">
</div>

# Linkbook

Linkbook is a powerful web app that can store your favorite links, keep you organized, and much more. Linkbook does all the heavy lifting for you by parsing websites to give you a clean and clear snapshot of each page you save by grabbing the website's top image, title, and summary. It also recommends related articles based on keywords found in each website you save.

![Home](https://raw.githubusercontent.com/wyattharrell/linkbook/master/static/website/cardexample.png?token=AFAYOTPBEHK6AYNMNM2F2ES6BE2UW)

## Installation:

Install the requirements: `pip install -r requirements.txt`. The main dependencies are Flask and Pyrebase. However, there are a few other libraries required for web scraping.

## Configuration:

You will need to create a Firebase database (for storing links, login/register authentication, etc.) as well as a Google API key (for use of the *googleapiclient.discovery* library). Once this is complete, place your API key in `api_key=""` and Firebase project configuration in `config={}`. Both variables are located in `linkbook.py` 

## Launching Linkbook:

Run the website:
```
python linkbook.py
```

Visit page in web browser:
```
http://localhost:5000/
```

## Screenshots:

![Home](https://raw.githubusercontent.com/wyattharrell/linkbook/master/static/website/home.png?token=AFAYOTO6XASR6RG2FSKPAPS6BEYQ4)

![Categories](https://raw.githubusercontent.com/wyattharrell/linkbook/master/static/website/cats.png?token=AFAYOTMOKVDB7OXG2QRITDS6BEZTO)

![Videos Category](https://raw.githubusercontent.com/wyattharrell/linkbook/master/static/website/videos.png?token=AFAYOTI6G76KWWFYLEJ22V26BE2YI)

![All Category](https://raw.githubusercontent.com/wyattharrell/linkbook/master/static/website/all.png?token=AFAYOTOYRNPRUEHDBATYNOC6BE45Q)

![Dashboard](https://raw.githubusercontent.com/wyattharrell/linkbook/master/static/website/dashboard.png?token=AFAYOTLNQ5JAHINJALTSOUK6BE45I)
