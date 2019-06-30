#!/bin/sh

DATABASE_HOSTNAME=${DATABASE_CONTAINER_NAME}
DATABASE_PORT=${DATABASE_PORT:-'3306'}

echo "Waiting for database"
while ! nc -zv $DATABASE_HOSTNAME $DATABASE_PORT
do
  sleep 0.1
done

PRJ_NAME=${DJANGO_PROJECT_NAME}
APP_NAME=${DJANGO_APPLICATION_NAME}

/${PRJ_NAME}/manage.py makemigrations
/${PRJ_NAME}/manage.py migrate
/${PRJ_NAME}/manage.py makemigrations ${APP_NAME}
/${PRJ_NAME}/manage.py migrate ${APP_NAME}

# Create Admin User
EXIST_ADMIN=`python manage.py shell < /check_admin.py`
if [ ${EXIST_ADMIN} = 'True' ]; then
  :
else
  echo "Does not exist admin user."
  /${PRJ_NAME}/manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', os.environ.get('DJANGO_ADMIN_EMAIL','admin@localhost.com'), os.environ.get('DJANGO_ADMIN_PASSWORD','admin'))"
  echo "Created admin user!! ('admin', ${DJANGO_ADMIN_EMAIL:-'admin@localhost.com'}, ${DJANGO_ADMIN_PASSWORD:-'admin'})"
fi

python /${PRJ_NAME}/manage.py collectstatic --noinput

# Run WSGI Server
/usr/local/bin/uwsgi --socket :${WSGI_PORT:-'5000'} --wsgi-file /${PRJ_NAME}/${PRJ_NAME}/wsgi.py --master --processes ${WSGI_PROCESSES:-'4'} --threads ${WSGI_THREADS:-'2'} --chdir /${PRJ_NAME}
