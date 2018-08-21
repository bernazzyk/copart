1. Create appropriate droplet on "www.digitalocean.com".
Recommend Ubuntu16.04.
2. Connect with web-console www.digitalocean.com.
It will ask username and password. Default username is ‘root’ and password will sent to your email.
3. Connect to droplet with WinSCP.
4. open terminal
5. apt update
6. apt install docker
7. apt install docker-compose


1. git clone https://gitlab.com/zaza316/copart.git
2. cd copart/
3. docker-compose up -d
4. docker exec -ti copart_web_1 bash
5. python manage.py makemigrations
6. python manage.py migrate
7. python manage.py createsuperuser
8. python manage.py loaddata copart/fixtures/vehiclemakes.json
9. python manage.py collectstatic
10. #Install Selenium
apt update
apt install -y libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome*.deb
apt install -y -f
wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
apt install -y unzip
unzip chromedriver_linux64.zip
chmod +x chromedriver
mv -f chromedriver /usr/local/bin/chromedriver
11. exit

12. docker exec -ti copart_celery_1 bash
13. Install Selenium(repeat 10)
14. exit

15. docker-compose restart
