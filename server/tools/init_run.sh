#!/usr/bin/env bash

# 가상환경 생성하기
. ./tools/makevenv.sh
# db 초기화
. ./tools/reset_db.sh

. ./.activate
cd ./web
# 스테틱 폴더가 없으면 생성하기
if [ ! -s ./static/ ]
then
    mkdir static
fi
echo "* 정적파일 수집하기"
python manage.py collectstatic
cd ..
deactivate