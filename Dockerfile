###########
# BUILDER #
###########

# Указывает Docker использовать официальный образ python 3 с dockerhub в качестве базового образа
FROM python:3.11-alpine as builder
# Устанавливает переменную окружения, которая гарантирует,
# что вывод из python будет отправлен прямо в терминал без предварительной буферизации
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
# Устанавливает рабочий каталог контейнера — "/usr/src/app"
WORKDIR /usr/src/app
# Обновляет менджер пакетов до последней версии
RUN pip install --upgrade pip
# Устанавливает зависимости psycopg2
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
# Устанваливает остальные зависимости
COPY ./requirements.txt ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

#########
# FINAL #
#########
FROM python:3.11-alpine

# Создаст домашний каталог для пользователя 'app'
RUN mkdir -p /home/app
# Создаст пользователя 'app' и группу 'app'.
# Очень важно, чтобы у пользователя не было полномочий 'root',
# поскольку если вы root в контейнере, вы будете root на хосте.
# Дургими словами, если приложение содержит уязвимость, то
# злоумышленик может получить полный контроль над сервером.
RUN addgroup --system app && adduser --system app --ingroup app

# Задает переменную среды с домашним каталогом пользователя
ENV HOME=/home/app
# Задает переменную серды с рабочим каталогом приложения
ENV APP_HOME=/home/app/tlearn
# Создает рабочий каталог приложения
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
# Устанавливает рабочий каталог приложения как рабочий каталог текущего окружения
WORKDIR $APP_HOME

# Устанавливает зависимости
RUN apk update && apk add libpq
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Копирует скрипт инициализации в рабочий каталог приложения
COPY ./entrypoint.sh $APP_HOME
# Копирует само приложение
COPY ./src $APP_HOME

# Объявляет пользователя 'app' владельцем всех файлов
RUN chown -R app:app $APP_HOME
# Переключает теуущего пользователя на 'app'
USER app

# Запускает скрипт первоначальной настройки после развертывания
ENTRYPOINT ["/home/app/tlearn/entrypoint.sh"]