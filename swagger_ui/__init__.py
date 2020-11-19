from pathlib import Path
from bottle import get, static_file, redirect

here: Path = Path(__file__).absolute().parent

UI_ROOT = here / 'node_modules/swagger-ui-dist'


@get('/')
def root():
    return redirect('/swagger-ui/')


@get('/swagger-ui/')
@get('/swagger-ui/<filename:path>')
def send_static(filename=None):
    return static_file(filename or 'index.html', root=UI_ROOT)
