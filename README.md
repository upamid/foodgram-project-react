# praktikum_new_diplom

Docker проект **foodgram-project-react**

Итоговый проект _Яндекс.Практикум_ по курсу **"Дипломный проект"**

Описание
=====================

Окружение для работы с базой данных
-----------------------------------
### Инструкция по заполению .env

```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

Docker
-----------------------------------
### Инструкция по установке Docker

[Ссылка](https://docs.docker.com/engine/install/ubuntu/)


Команды
-----------------------------------

### Команда клонирования проекта с DockerHub

`sudo docker pull upamid/yamdb_final`

### Команда для запуска приложения

`docker-compose up -d --build `

### Команда запуска docker-compose

`docker-compose up`

### Команда миграции базы данных

`docker-compose exec web python manage.py migrate --noinput`

### Команда для создания суперпользователя

`docker-compose exec web python manage.py createsuperuser`

### Команда для заполнения базы начальными данными

`docker-compose exec web python manage.py loaddata fixtures.json`

### Команда для остановки приложения

`sudo docker-compose stop`

# workflow
![workflow](https://github.com/upamid/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# участник

[Дмитрий Ступницкий.](https://github.com/upamid) 

# Рабочий проект

[Проект](http://84.252.143.136/recipes)

