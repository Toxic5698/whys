Whys test shop in Django REST Framework with postgres database

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

4. urlpatterns
            - admin/
            - api/token/ [name='token_obtain_pair']
            - api/token/refresh/ [name='token_refresh']
            - register/ [name='register']
            - email-verify/ [name='email-verify']
            - login/ [name='login']
            - logout/ [name='logout']
            - import/ [name='import']
            - detail/<str:model_name>/ [name='list']
            - detail/<str:model_name>/<int:pk>/ [name='detail']
            - product/ [name='product']




