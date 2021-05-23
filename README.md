## Whys test shop 
Test project in Django REST Framework with postgres database

1. install requirements from requirments.txt

2. in postrgresql create database with credentials:

            'NAME': 'shop',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '5432'

3. run commands in app directory 

            ./python3 manage.py makemigrations
            ./python3 manage.py migrate
            ./python3 manage.py runserver





