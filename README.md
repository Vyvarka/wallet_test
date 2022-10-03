# wallet_test

### This is a test API client for transactions between users' wallets.
It allows you to register users, create no more than 5 wallets for one user, and make transactions. Shows current user data, wallet list, transaction list, and transactions for the current user's wallet.

### Stack: Python 3.10, Django 4, DRF 3, Django ORM, PostgreSQL

### To run this project on Win10 you need to:
* Install Python 3.10+ release
> [Download for Win10](https://www.python.org/downloads/windows/)
---
* Open command line
> press 'windows' --> enter 'cmd' --> press 'Enter'
---
* go to disk project (for example) and into project folder:
	* > D:
	* > cd some_projects_or_other_folder

* Create a separate folder for the project on your PC (for example)

> mkdir wallet_project
---
* In this folder create the virtual environment and run it
	* > python -m venv venv
	* > venv\Scripts\activate 
---
* Install Git on your PC if it is not installed
> Instruction [here](https://git-scm.com/book/ru/v2/%D0%92%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D0%A3%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0-Git)
---
* Clone this repository into the project folder
> git clone https://github.com/Vyvarka/wallet_test.git
---
* Install all modules, libraries and frameworks to work with the API
> pip install -r requirements.txt
---
* If you __have__ PostgreSQL installed:
	* create a separate database
	* create file .env[^1] and put the real data for variables:
		> DB_USER=admin\
		DB_PASS=password\
		DB_NAME=wallet_db\
		DB_PORT=5432	
---
* If you __DON'T have__ PostgreSQL installed, then replace the current settings in wallet/wallet/settings.py with the following:
> DATABASES = {\
    'default': {\
        'ENGINE': 'django.db.backends.sqlite3',\
        'NAME': BASE_DIR / 'db.sqlite3',\
    }\
}
---
* Using the console, go into the project folder ..\wallet_test\wallet 
> cd wallet_test\wallet
---
* Make migrations
> python manage.py migrate
---
* Create a superuser
> python manage.py createsuperuser
---
* Run the server
> python manage.py runserver
---

### And you can start using the API in your browser.

* Available routes (if you have not changed the default port number when starting the server):
	* [for login](http://127.0.0.1:8000/api/login/)
	* [for logout](http://127.0.0.1:8000/api/logout/)
	* [to create a user](http://127.0.0.1:8000/api/users/)
	* [get wallet list is for authenticated users](http://127.0.0.1:8000/api/wallets/)
	* You can see the other routes in api\urls.py

### To use the API testing module, you need to change the code of the pytest.ini file. Leave only the following:
> [pytest]\
pythonpath = ../wallet\
DJANGO_SETTINGS_MODULE = wallet.settings\
python_files = tests.py test_*.py *_tests.py

* To run tests you must:
	* be in the folder ..\wallet_test
	* use command:
		> pytest tests


[^1]: This file contains the names of environment variables. They are used in the project settings to protect personal data. If you change the names of the variables, you must also change the settings.py file, the DATABASES section. Otherwise the database won't run.

