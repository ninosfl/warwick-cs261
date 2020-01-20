# Instructions To Run Server

Make sure python 3.7+ is installed on your system.

## Windows

### Install django
In terminal execute 
`pip install django`

### Run server
`cd` to this directory (`cs261db/server/`)

Django by default uses port 8000, you can omit it in the following command.
`python manage.py runserver 8000`
If you have troubles with this port you can try a different one.

If successful the last line in console will be
`Starting development server at http://127.0.0.1:8000/`

Connect on `localhost:8000` (or whatever port you may have specified)

Stop server using `Ctrl+C`

## Mac/Linux

### Install django
In terminal execute 
`pip3 install django`

### Run server
`cd` to this directory (`cs261db/server/`)

Django by default uses port 8000, you can omit it in the following command.
`python3 manage.py runserver 8000`
If you have troubles with this port you can try a different one.

If successful the last line in console will be
`Starting development server at http://127.0.0.1:8000/`

Connect on `localhost:8000` (or whatever port you may have specified)

Stop server using `Ctrl+C`
