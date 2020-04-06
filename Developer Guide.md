### Apps

#### authentication

App for customizing authentication and authorization, which inheritated from Django authentication application.

The following represents models of this app:



Users are required to log in with **email and password**.

#### assign

App for assigning tasks for each user. The task assignment logic was implemented in `views.py`. The `assign` function should be imported and called whenever task allocation is needed inside other apps.

#### pages

Main app for data cleansing logic, including two parts: `admin` and `user`.

##### admin - superuser and admin



##### user