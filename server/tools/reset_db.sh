#!/usr/bin/env bash

# 프로젝트 폴더
project_dir="./web/"
# 앱 폴더
homeApp=$project_dir"home/"

# db 파일
dbFile=$project_dir'db.sqlite3'

# 이전 db파일이 존재하면 삭제
if [ -s $dbFile ]
then
    echo "* 이전 데이터베이스를 발견하여 삭제합니다."
    rm -rf $dbFile
fi

# 이전 마이그레이션 파일이 존재하면 삭제
if [ -d ./web/home/migrations/ ]
then
    echo "* 이번 마이그레이션 파일을 삭제 합니다"
    rm -rf ./web/home/migrations/
fi

# db마이그레이션
. ./tools/migrate.sh

# 최고관리자 생성
. ./.activate
cd ./web/
echo "* 최고 관리자 생성하기"
python manage.py createsuperuser
echo "settings.ini을 이용하여 설정을 관리하세요."
cd ..
deactivate
