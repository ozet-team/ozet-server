<div align="center">
  <h1>OZET Core </h1>
  <p>
    <img src="https://user-images.githubusercontent.com/36470472/129739040-bf35eae7-97fe-4ddd-9140-9f3619ad7bf8.png" alt="Logo" width="150" height="150">
  </p>
  <div>
    <a href="#" target="_blank"><img src="https://img.shields.io/badge/Python%203.9.6-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="python" /></a>
    <a href="#" target="_blank"><img src="https://img.shields.io/badge/Django%203.2.6-092E20?style=flat&logo=Django&logoColor=white" alt="django" /></a>
  </div>
  <div>
    <a href="#" target="_blank"><img src="https://img.shields.io/badge/Docker-2496ED?style=fpip inlat&logo=Docker&logoColor=white" alt="docker" /></a>
    <a href="#" target="_blank"><img src="https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=Mysql&logoColor=white" alt="mysql" /></a>
    <a href="#" target="_blank"><img src="https://img.shields.io/badge/Redis-DC382D?style=flat&logo=Redis&logoColor=white" alt="redis" /></a>
  </div>
</div>

## Getting Started

아래는 `OZET Core` 를 실행하기 위한 가이드 입니다.

### Prerequisites

---
아래 사항들이 설치 및 선행 되어 있어야 합니다.
* #### [pyenv](https://github.com/pyenv/pyenv)
    * Mac 설치
    ```
    $ brew update
    $ brew install pyenv
    ```
* #### [venv](https://docs.python.org/ko/3.6/tutorial/venv.html)
    ```
    $ python3 -m venv /path/to/new/virtual/environment
    ```
* #### [pip-tools](https://pypi.org/project/pip-tools/)
    ```
    $ pip install pip-tools
    ```
* #### [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Installing

---
아래는 프로젝트를 설치하는 방법입니다.
1. #### 레포지토리 설치
    ```
    $ git clone git@github.com:LuxQuad/ozet-core.git
    $ cd ozet-core
    ```

2. #### 라이브러리 추가 및 업데이트
    > :warning: *`.misc/requirements/base.in` 내 추가하고싶은 라이브러리 버전과 함께 명시 한후 `$ sh .misc/runner/run_requirements.sh` 를 실행하여 `*.txt` 파일 업데이트*
    ```
    $ pip-sync .misc/requirements/dev.txt
    ```
3. #### Local 서버 환경 구축
    1. #### [MySQL](https://formulae.brew.sh/formula/mysql) 설치 (Mac 기준)
        ```
        $ brew update
        $ brew search mysql
        $ brew install mysql
        ```
        
        위 커맨드가 성공적으로 설치가 완료되면 하단의 커맨드를 이용해 데이터베이스 및 계정을 설정합니다.        
        ```
        $ mysql -u root
        ```
        ```
        mysql> CREATE DATABASE 'ozet' DEFAULT CHARACTER SET UTF8; 
        mysql> CREATE USER 'root'@'127.0.0.1' IDENTIFIED BY 'root';
        mysql> GRANT ALL PRIVILEGES ozet.* 'root'@'127.0.0.1' IDENTIFIED BY 'root' with grant option;
        mysql> FLUSH PRIVILEGES;
        ```
    2. #### [Redis](https://hub.docker.com/_/redis) 설치
        ```
        $ docker pull redis
        $ docker run --name redis -d -p 6379:6379 redis
        ```
        `$ docker ps` 실행시 아래와 같은 나오면 설치가 완료된 것 입니다.
        ```
        CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS      NAMES
        1620858a95a7   redis     "docker-entrypoint.s…"   13 seconds ago   Up 13 seconds   6379/tcp   redis
        ```
        
4. #### Local 환경 설정
    ```
    $ mkdir ozet/settings/local
    $ touch ozet/settings/__init__.py  
    $ touch ozet/settings/local/local.py
    ```
    위 파일을 Local 에 설치한 환경에 맞게 추가로 작성합니다.
    > *이렇게 작성된 `local.py` 는 이후 자동으로 불러오게 됩니다.*
    아래는 간단한 local.py 예시입니다. 
    ```
    # -*- coding: utf-8 -*-
    from ..base import *
   
    ...
   
    # Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ozet',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
    DATABASE_QUERY_PREFIX = 'development'
   
    ...
    ```
5. #### Local DB Migration
    위의 모든 설정이 완료되었다면 `Django Migration` 을 사용해 DB 상태를 제일 최근으로 Migrate 합니다.
    ```
    $ python manage.py migrate
    ```

5. #### StaticFile Collect
    실행하는데 필요한 Static 파일을 수집합니다.
    ```
    $ python manage.py collectstatic --noinput
    ```

## Tests
* ### PyTest or Unit Tests
    하단의 스크립트를 실행하면 테스트 코드가 작동합니다.
    ```
    ```


## Running
아래는 프로젝트를 실질적으로 실행하는 방법에 대해 설명합니다.

* ### [Django](https://docs.djangoproject.com/ko/2.1/intro/tutorial01/#the-development-server)
    ```
    $ python manage.py runserver
    ```
    ```
    ...

    ```

* ### [Gunicorn](https://docs.gunicorn.org/en/stable/)
    ```
    $ gunicorn ozet.wsgi:application
    ```
    ```
    ...

    [2021-08-06 15:59:17 +0900] [75121] [INFO] Starting gunicorn 20.1.0
    [2021-08-06 15:59:17 +0900] [75121] [INFO] Listening at: http://127.0.0.1:8000 (75121)
    [2021-08-06 15:59:17 +0900] [75121] [INFO] Using worker: sync
    [2021-08-06 15:59:17 +0900] [75123] [INFO] Booting worker with pid: 75123
    ```

## Workflow
현재 Workflow 는 기본적으로 [Git Flow](https://techblog.woowahan.com/2553/) 를 사용하고 있습니다.
> * `master` : 제품으로 출시될 수 있는 브랜치
> * `develop` : 다음 출시 버전을 개발하는 브랜치
> * `feature` : 기능을 개발하는 브랜치
> * `release` : 이번 출시 버전을 준비하는 브랜치
> * `hotfix` : 출시 버전에서 발생한 버그를 수정 하는 브랜치
> * `fix` : 기존에 발생한 버그를 수정하는 브랜치
>
>
> <div align="center"> <img src="https://user-images.githubusercontent.com/36470472/128487175-e5d28ce3-b5b7-48f2-914d-4b9383277986.png" width="800" alt="git-flow" /></div>

## Directory Structure
```
```
