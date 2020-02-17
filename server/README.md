# Instructions To Run Server

Make sure python 3.8+ is installed on your system.

## Windows

### Install django
In terminal execute 
`pip install django`

### Run server
`cd` to this directory (`cs261db/server/`)

Django by default uses port 8000, you can omit it in the following command.
`python manage.py runserver 8000`.
If you have troubles with this port you can try a different one.

If successful the (second to) last line in console will be
`Starting development server at http://127.0.0.1:8000/`

Connect on `localhost:8000` (or whatever port you may have specified)

Stop server using `Ctrl+C`

## Mac/Linux

### Install django
In terminal execute 
`pip3 install django`

### Run server
`cd` to this directory (`cs261db/server/`)

Django by default uses port 8000, you can omit it in the following command:
`python3 manage.py runserver 8000`.
If you have troubles with this port you can try a different one.

If successful the (second to) last line in console will be
`Starting development server at http://127.0.0.1:8000/`

Connect on `localhost:8000` (or whatever port you may have specified)

Stop server using `Ctrl+C`

## Login to admin page

(Mac/Linux please replace `python` with `python3`)

`python manage.py createsuperuser`

`python manage.py makemigrations`

`python manage.py migrate`

Admin page URL: `localhost:8000/admin`

## Load CSV data

```bash
python manage.py migrate
python manage.py shell  # This will create a python shell!
```

Then, in the created Python shell:

```python
>>>import loadcsv
>>>loadcsv.main()
```

Note: For example purposes it is sufficient to load a single year.
(Approx 10 minutes for `all` months YMMV)
Select more years at your own risk (and waste of time).

Note Note: Do not commit the resulting `db.sqlite3` file yet...

## Bundle Webpack data and run server

Due to the use of `npm init`, Node modules have only been installed locally, and not to the system PATH. Therefore, to bundle any changes you have made to the React code, you should run, from the directory server:

```bash
./node_modules/.bin/webpack --config webpack.config.js
```

To automatically re-bundle if any changes are made, you can tell Webpack to watch the files with:

```bash
./node_modules/.bin/webpack --config webpack.config.js --watch
```
