##### Русский
## Описание
Это backend репозиторий онлайн мини-игры, созданной для людей, проводящих реальную игру, в которой несколько команд отвечают на вопросы на веб-сайте и вводят ответы, найденные за его пределами.

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
<img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/1c43e873-d71e-46e0-98cd-1d0008c015ee" width="400px" height="200px" />

**Страница редактирования игры (Edit game page)**
<img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/d00eab14-7b99-428e-ac9d-6c66e6396108" width="400px" />

**Форма добавления подсказки и вопроса (Adding hint and question form)**
<img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/7af6d7cc-db93-4047-a22d-1b01db95c4e5" width="400px" />
<img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/ae31c481-0743-4e15-8e16-2292ed1616a0" width="400px" />

**Страница игры (Game detail page)**
<img src="https://github.com/grimma2/quiz-back-prod/assets/80467627/62e3367c-1570-4a02-9a44-82a028794ab6" width="400px" />






