1. Install necessary packages: `pip install -r requirements.txt`  
   OR  
   Activate virtual environment: `source datacleansingenv/bin/activate`  
2. Install PostgresSQL  
   Creat user and database for this application
   Approach `settings.py - DATABASES`. Set `NAME`, `USER`, `PASSWORD` as required. 
3. To set up data for testing: run `python set_up.py`
4. To start Django server: run `python manage.py runserver`