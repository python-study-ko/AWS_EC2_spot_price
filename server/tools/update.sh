#!/usr/bin/env bash

echo "코드를 업데이트 합니다"
git pull

echo "DB를 마이그레이션 합니다"
. ./tools/migrate.sh

echo "서버를 시작 합니다"
. ./.activate
pyton manage.py runserver