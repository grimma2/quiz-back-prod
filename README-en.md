##### <a href="https://github.com/grimma2/quiz-back-prod/tree/main">Русский</a> / <a href="https://github.com/grimma2/quiz-back-prod/blob/main/README-en.md">English</a>
## Description
This is the backend repository for an online mini-game created for people conducting a real game where multiple teams answer questions on a website and input answers found beyond its boundaries. The site will soon be accessible to everyone at this link https://quiz-game1.ru

## Functionality
Any user can configure the game without registration. In this configuration, they need to enter the following data:
- Teams participating in the game.
- Questions and corresponding answers.
- Choose the type of question that affects how the question is presented during the game.
- Hints that appear as teams answer questions (time intervals for hint appearance).
- Teams enter the game using a code generated for each team, which directs them to the game process page. On this page, they can see:
  - A timer indicating the time until the next hint.
  - The number of answers they need to enter.
  - Already entered answers and their correctness.

Additionally, when someone answers a question, all users in the game synchronize, and everyone moves on to the next question together.

## How to Install
### Installation and Running of the Backend Part
Python version >= 3.10 is required.

Create a virtual environment in the repository and activate it.
Install dependencies
```
pip install -r requirements.txt
```

Create a <code>.env.bat</code> file with environment variables as shown below. Replace the values in angle brackets.
**Note: POSTGRES_PASSWORD is only needed for production**
```
set CHANNEL_REDIS=redis://localhost:6379/1
set SECRET_KEY=<YOUR_SECRET_KEY>
set POSTGRES_PASSWORD=<YOUR_POSTGRES_PASSWORD>
set CELERY_REDIS=redis://localhost:6379/0
```

To activate these variables, open the Windows cmd in the project directory and run

```
call .env.bat
```

Afterward, start the Django server

```
python manage.py runserver
```

### Installation and Running of the Frontend Part
To fully experience the project's functionality, you can also download the frontend repository **quiz-front-prod** from this account and run it with a couple of commands. However, before doing that, download **node js** from the official website if you don't have it installed: https://nodejs.org/en
Install dependencies

```
npm install
```

and start the server

```
npm run serve
```

### Installation and Running of Celery
For proper operation, specifically to run the game process itself, you need to install **Celery**. To do this, you need to install **Docker**, here's a guide for Windows:
https://docs.docker.com/desktop/install/windows-install/ and for Linux (Ubuntu): https://docs.docker.com/engine/install/ubuntu/
After you have installed **Docker**, you need to run either **redis** or **rabbitmq** in it. Here's an example with Redis:

```
docker run -d -p 6379:6379 redis
```

And start Redis while being in the project directory with all dependencies installed and environment variables enabled using <code>call .env.bat</code>

```
celery -A quiz worker -l info
```

Note: If your device doesn't have enough power to run Celery with this command, use this one instead:

```
celery -A quiz worker -l info --pool=solo
```

**Game List Page**
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/1c43e873-d71e-46e0-98cd-1d0008c015ee" width="150px" height="350px" /></div>

**Game Editing Page**
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/d00eab14-7b99-428e-ac9d-6c66e6396108" width="150px" height="350px" /></div>

**Hint and Question Addition Form**
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/7af6d7cc-db93-4047-a22d-1b01db95c4e5" width="150px" height="350px" /></div>
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/ae31c481-0743-4e15-8e16-2292ed1616a0" width="150px" height="350px" /></div>

**Game Page**
<div><img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/62e3367c-1570-4a02-9a44-82a028794ab6" width="150px" height="350px" /></div>
