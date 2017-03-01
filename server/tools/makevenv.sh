#!/usr/bin/env bash

SYSTEM=$(uname)

# pgsql requierments 설치
# 운영체제가 리눅스일 경우
if [ $SYSTEM = 'Linux' ]; then
	SYSTEM_TYPE=$SYSTEM
	sudo apt-get install libpq-dev
# 운영체제가 맥일 경우
elif [ $SYSTEM = 'Darwin' ]; then
	SYSTEM_TYPE='Mac OS X'
	INSTALL_COMMAND="brew -y "
else
	SYSTEM_TYPE='NOT VALID'
fi


if [ -d ./.venv ]
then
    echo " 이전의 가상환경을 삭제하겠습니다.";
    sudo rm -rf ./.venv
fi

echo "* 가상환경을 생성합니다"
python3.6 -m venv ./.venv
# 가상환경 활성화 파일 심볼릭 링크 생성
ln -s -f ./.venv/bin/activate ./.activate
# 가상환경 활성화
. ./.activate

if [ -s ./requirments.txt ]
then
    echo "* requirments.txt파일을 발견하여 필수 모듈을 설치합니다."
    pip install -r ./requirments.txt
fi
deactivate

echo "모든 작업이 완료 되었습니다. 모든 작업은 가상환경에서 실행하세요"
echo "source .activate 로 가상환경을 실행하고"
echo "deactivate로 가상환경을 종료하면 됩니다"
