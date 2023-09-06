##### Русский
## Описание
Это backend репозиторий онлайн мини-игры, созданной для людей, проводящих реальную игру, в которой несколько команд отвечают на вопросы на веб-сайте и вводят ответы, найденные за его пределами.

## Как установить
### Установка и запуск backend части
Версия python>=3.10.**

Создать в репазитории виртуальное окружение и активировать его.
Установить зависимости
```
pip install -r requirements.txt
```

Создать файл <code>.env.bat</code> с переменными окружения, как в примере ниже. Значения в треугольных скобках нужно заменить.
**Примечание: POSTGRES_PASSWORD нужен только для production**
```
set CHANNEL_REDIS=redis://localhost:6379/1
set SECRET_KEY=<YOUR_SECRET_KEY>
set POSTGRES_PASSWORD=<YOUR_POSTGRES_PASSWORD>
set CELERY_REDIS=redis://localhost:6379/0
```
Чтобы активировать эти переменные, необходимо в Windows cmd, находясь в директории проекта прописать
```
call .env.bat
```

После чего запустить Django сервер
```
python manage.py runserver
```

### Установка и запуск frontend части
Для того, чтлбы в полной мере увидеть функциональность проекта, так же можно и скачать fontend репазиторий **quiz-front-prod** на этом аккаунте и запустить его парой командой, но перед этим, скачать **node js** на оффициальном сайте, если он у вас не установлен https://nodejs.org/en
Установка зависимостей
```
npm install
```
и запуск сервера
```
npm run serve
```

### Установка и запуск Celery
Для коректной работы, а именно, для того, чтобы запустить сам процесс игры, нужно установить **Celery**. ДЛя этого, необходимо установить **Docker**, вот гайд для Windows:
https://docs.docker.com/desktop/install/windows-install/ и для Linux (Ubuntu): https://docs.docker.com/engine/install/ubuntu/
После того, как вы установили **Docker**, необходимо запустить в нём либо **redis** либо **rabbitmq**, здесь будет показан пример в редисом:
```
docker run -d -p 6379:6379 redis
```
И запустить сам redis находясь при этом в директории проекта со всеми установленными зависимостями и включёнными переменными окружения с помощью <code>call .env.bat</code>
```
celery -A quiz worker -l info
```
Примечание: если у вашего устройства не хватает мощьности для запуска Celery такой командой, успользуйте вместо неё
```
celery -A quiz worker -l info --pool=solo
```

## Функциональность
Любой пользователь может создать конфигурацию игры без регистрации. В этой конфигурации они должны ввести следующие данные:
- Команды, участвующие в игре.
- Вопросы и соответствующие ответы.
- Выбрать тип вопроса, который влияет на то, как вопрос представлен во время игры.
- Подсказки, которые появляются по мере ответов команды на вопросы (временные интервалы для появления подсказок).
- Команды входят в игру с помощью генерируемого для каждой команды кода, который направляет их на страницу процесса игры. На этой странице они могут видеть:
  - Таймер, указывающий время до следующей подсказки.
  - Количество ответов, которые им нужно ввести.
  - Уже введенные ответы и их правильность.

Кроме того, когда кто-то отвечает на вопрос, все пользователи в игре синхронизируются, и каждый переходит к следующему вопросу вместе.

##### English
## Description
This is the backend repository of an online mini-game created for individuals who participate in a real-life game where multiple teams answer questions on a website and input answers they find outside the game.

## Functionality
Any user can create a game configuration without registration. In this configuration, they must input the following details:
- Teams participating in the game.
- Questions and their corresponding answers.
- Select the question type that will affect how the question is presented during the game.
- Hints that will appear as the team answers questions (user-inputted time intervals for hint appearance).
- Teams enter the game using a code generated for each team, which directs them to the game process page. On this page, they can see:
  - A timer indicating the time until the next hint.
  - The number of answers they need to input.
  - Answers already entered and whether they are correct.

Additionally, when someone answers a question, all users in the game are synchronized, and everyone is moved to the next question together.


**Страница списка игр (Games list page)**
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/1c43e873-d71e-46e0-98cd-1d0008c015ee" width="150px" height="350px" /></div>

**Страница редактирования игры (Edit game page)**
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/d00eab14-7b99-428e-ac9d-6c66e6396108" width="150px" height="350px" /></div>

**Форма добавления подсказки и вопроса (Adding hint and question form)**
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/7af6d7cc-db93-4047-a22d-1b01db95c4e5" width="150px" height="350px" /></div>
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/ae31c481-0743-4e15-8e16-2292ed1616a0" width="150px" height="350px" /></div>

**Страница игры (Game detail page)**
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/62e3367c-1570-4a02-9a44-82a028794ab6" width="150px" height="350px" /></div>






