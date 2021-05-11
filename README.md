# dbis_lab_3

Інструкцыя з розвертання апплікейшну на Хероку:

1. Додати всі файли з репозиторію в одну папку
2. Створити на сайті Хероку новий аплікейшн
3. Встановити git та heroku cli та авторизуватися в них
4. Встановити Heroku postgre addon та за необхідності додати в нього дані за допомогою файлу chess-backup.bck
5. З папки з проєктом послідовно виконати команди:
   
   git init
   
   heroku git:remote -a <app_name>
  
   git add .
   
   git commit -am "<message>"
   
   git push heroku master
 

Посилання на розгорнутий апплікейшн:
https://buslaiev-lab3.herokuapp.com/
