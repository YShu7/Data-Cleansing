[![Build Status](https://travis-ci.com/YShu7/Data-Cleansing.svg?branch=master)](https://travis-ci.com/YShu7/Data-Cleansing)
[![Build Status](https://codecov.io/gh/YShu7/Data-Cleansing/branch/master/graph/badge.svg)](https://codecov.io/gh/YShu7/Data-Cleansing)

# Introduction

Data cleansing is a common task in model training. While in most cases, a person can validate the correctness of data reliablely, when it comes to domain specific knowledge, we would like to seek agreement among individuals.

This application provides a platform which allows user to clean data without considering the allcation and summarization of data cleansing tasks.

It provides function including:

- assign different tasks to users
- validate and update data based on responses from users
- generate new dataset for training
- generate working report for management purpose

# Set up

1. Install necessary packages: `pip install -r requirements.txt`  
   OR  
   Activate virtual environment: `source datacleansingenv/bin/activate`  

2. Install psycopg2 manually if the previous step fails to install it:  
   For Mac:  
   `xcode-select --install`  
   `env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"`  
   `pip install psycopg2`  
   For Ubuntu:  
   If `psycopg2` cannot be installed, install `psycopg2-binary` instead:  
   `pip install psycopg2-binary`

3. Install PostgresSQL
   For Mac:  
   `brew install postgresql`  
   For Ubuntu:  
   `sudo apt-get install postgresql`  
   Create User:  
   `sudo -u postgres createuser datacleansinguser`  
   `alter role datacleansinguser with superuser;`  
   `alter role datacleansinguser with password 'L1feI5T0ugh';`  
   Switch to the created user:  
   `set role datacleansinguser;`  
   Create database:  
   `create database datacleansing;`  

   > If PostgresSQL version doesn't meet the requirement:
   > `brew postgresql-upgrade-database`

   If you would like to use the other user or database:  
   Approach `settings.py - DATABASES`. Set `NAME`, `USER`, `PASSWORD` as required. 

4. Migrate: `python manage.py migrate`  

5. To set up data for testing: run `python set_up.py`

6. To start Django server: run `python manage.py runserver`

7. To log into the website:

   Superuser account: `superuser@gmail.com` password: `superuser`

   Admin account: `admin@gmail.com` password: `admin`
   
   User account: `alice@gmail.com` password: `alice`

# Roles

## Superuser

Superuser is a group of people who **do NOT require domain specific knowledge**. Their role is to **manage different groups, accounts and dataset at higher level**. 

Superuser is expected to be the account that has the most permissions.

### Allowed actions

[Details](pages/templates/help/en/superuser.md)

#### Group

- To create/delete group

#### Account

- To approve/reject user account
- To activate/deactivate user account
- To assign the admin role

#### Dataset

- To view/download dataset
- To update data

#### Report & Log

- To view/download working report
- To view admin log

## Admin

Admin is a group of people who **do NOT require domain specific knowledge**. Their role is to **manage accounts and dataset within their own group**.

### Allowed actions

[Details](pages/templates/help/en/admin.md)

#### Account

- To approve/reject user account
- To activate/deactivate user account

#### Dataset

- To view/download dataset
- To update data

#### Report & Log

- To view/download working report
- To view admin log

#### Assign & Summarize

- To assign tasks
- To summarize and update individual report

## User

User is a group of people who require domain specific knowledge. Their role is to finish any tasks allocated to them by admin. User should NOT have any permission regarding management.

### Allowed actions

[Details](pages/templates/help/en/user.md)

- To submit response for tasks allocated to the user
- To change password

# Task Types

## Validating Tasks

Validating tasks require users to agree or disagree with question-answer pairs. The users should either **approve a pair** or **provide the correct answer if they disapprove a pair**.

The responses to these tasks will be collected each time a response is submitted. When responses from one side is confirmed to be greater than the other side, the data is considered to be cleaned and the majority will be the response for it. 

If majority consider the data as false, the data will be input to voting tasks, and all new answers submitted will be converted to its choices.

If majority consider the data as true, the data will directly be finalized.

## Voting Tasks

Voting tasks require users to select the best answer from at most 3 choices for a question.

The choice that has the highest votes will be considered as the answer to the question. Whenever a tie occurs, the choice with lower id will be selected as the correct answer.

## Keyword Selection Tasks

Keyword selection tasks require users to select keywords for both question and answer from a pair. The keyword does not have to be a single word, it can be any substring of the question and answer.

All responses submitted will be union together and considered as the keywords for a question-answer pair.

## Image Label Validation Tasks

Image label validation tasks shares the same logic as voting tasks, while instead of question-answer pairs, its target is image-label pairs.

