# API for front-end/back-end communication

For now, this is wildly incomplete - but you can test it out as it is!

Once you have the web server running, with `python3 manage.py runserver`, you can test out the api with: `curl localhost:8000/api/`.

To pass additional arguments to the api view (in order to provide functions that will perform back-end processing), please make the following changes to the main URLconf (which in this case can be found at `server/djangoserver/urls.py`):

- Add a dictionary as the third argument to `path`, with the names laid out in the `api_main()` method signature as the keys, and the appropriate function as the value.

e.g.

```Python
path("api/", include("api.urls"), {'func_name': (lambda x: x * 2)})
```
