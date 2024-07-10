1. Clone the repository

git clone https://github.com/Aravindhan-Master/Ecommerce.git

2. Create a virtual environment

python -m venv venv

3. Activate the virtual environment

venv\Scripts\activate

4. Install dependecies

pip install -r requirements.txt

5. Create migrations folder inside each applications

6. Create __init__.py file inside each migrations folder

7. Add these in .env file

DJANGO_SECRET_KEY=django_secret_key
DEBUG=True


DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=ecommerce_local
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=3306

CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=django-db

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=email
EMAIL_HOST_PASSWORD=password
DEFAULT_FROM_EMAIL=email

8. Migrate database

python manage.py makemigrations

python manage.py migrate

9. Start redis server for celery

10. Start celery

celery -A ecommerce.celery worker --poop=solo -l info

11. Start celery beat

celery -A ecommerce.celery beat -l info

12. Include google_oauth configuration file for google login