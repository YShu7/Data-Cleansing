[![Build Status](https://travis-ci.com/YShu7/Data-Cleansing.svg?branch=master)](https://travis-ci.com/YShu7/Data-Cleansing)

1. Install necessary packages: `pip install -r requirements.txt`  
   OR  
   Activate virtual environment: `source datacleansingenv/bin/activate`  
   
2. Install psycopg:

   `xcode-select --install`
   `env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install psycopg2`

3. Install PostgresSQL

   If PostgresSQL version doesn't meet the requirement: `brew postgresql-upgrade-database`

4. Creat user and database for this application
   Approach `settings.py - DATABASES`. Set `NAME`, `USER`, `PASSWORD` as required. 

5. To set up data for testing: run `python set_up.py`

6. To start Django server: run `python manage.py runserver`





### Apps

#### authentication

App for customizing authentication and authorization, which inheritated from Django authentication application.

The following represents models of this app:



Users are required to log in with **email and password**.

#### assign

App for assigning tasks for each user. The task assignment logic was implemented in `views.py`. The `assign` function should be imported and called whenever task allocation is needed inside other apps.

#### pages

Main app for data cleansing logic, including two parts: `admin` and `user`.

##### admin

##### user
