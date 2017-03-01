#!/usr/bin/env bash

# 마이그레이션할 앱 목록
apps=('home')
. ./.activate
echo "* DB 마이그레이션"
cd web
# cp gubda/settings.ini.sample gubda/settings.ini
python manage.py migrate
python manage.py makemigrations

# 각 모델의 테이블을 생성해준다
for m in $apps
do
    python manage.py makemigrations $m
done

python manage.py migrate
cd ..
deactivate
