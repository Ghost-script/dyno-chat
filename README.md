dyno-chat
=========
CREATE USER 'kickchat'@'localhost' IDENTIFIED BY 'kickme';

python manage.py syncdb

python manage.py pulse

