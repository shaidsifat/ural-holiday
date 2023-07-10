# booking-app
# Redeploy app with last code update
1- go to app directory by using this command:

  cd /Docker/uralholidays.com/deploy 
  
2- stop running dockers containers by using this command:
  
   docker compose down

3- change directory to app root folder by using this command:

  cd /Docker/uralholidays.com/

4- pull last code by using this command 

  git pull

5- check code status by using this command 

  git status

you should find this message: 

  On branch main
  Your branch is up to date with 'origin/main'.
  nothing to commit, working tree clean

6- change directory to deploy part by using this command:

  cd /Docker/uralholidays.com/deploy

7-build a new docker image by using this command:

  docker compose build

8- run the new docker image by using this command:

  docker compose up -d

9-last step check the stats of running docker containers by using this command 

  docker ps

10-you should find the following:

  deploy_django_backend_uk	  0.0.0.0:9000->9000/tcp

  deploy_django_backend	0.0.0.0:8000->8000/tcp

  db_server	0.0.0.0:3306->3306/tcp
