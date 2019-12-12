import logging.config

from flask_github import GitHub
from flask import Flask, request, redirect, abort, jsonify, url_for

from src.database import configure_db, select, delete_table
from src.config import config

CLIENT_ID = 'afc640aa84a96a863dc0'
CLIENT_SECRET = 'ba1df79ad9319d747f07beb97e192e0281d4cdcc'
OAUTH_TOKEN = None
GITHUB_CLIENT_ID = 'afc640aa84a96a863dc0'
GITHUB_CLIENT_SECRET = 'ba1df79ad9319d747f07beb97e192e0281d4cdcc'

DB_CONFIG_FILE = 'database.ini'
DB_PARAMS = config(DB_CONFIG_FILE)

JSONIFY_PRETTYPRINT_REGULAR = True

app = Flask('GithubApi')
app.config.from_object(__name__)

github = GitHub(app)


@app.route('/repos', methods=['GET'])
def get_repos():
    repo_id = request.args.get('id')
    if app.config['OAUTH_TOKEN'] is None:
        return redirect(url_for('login', next='login/' + repo_id if repo_id else ''))

    if not (repo_id is None or repo_id.isdigit()):
        abort(422, f'{repo_id} is not a valid value for parameter id.')

    repos = select(app.config['DB_PARAMS'], repo_id)
    if not repos:
        abort(404, f'Repository with id={repo_id} was not found.' if repo_id else 'User has no repositories.')

    keys = ['id', 'name', 'html_url', 'description', 'created_at', 'watchers', 'private']
    repos = [dict(zip(keys, repo)) for repo in repos]
    return jsonify(*repos)


@app.route('/repos/<int:repo_id>', methods=['GET'])
def get_repo_by_id(repo_id):
    return redirect(f'/repos?id={repo_id}')


@github.access_token_getter
def token_getter():
    token = app.config['OAUTH_TOKEN']
    if token is not None:
        return token


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    if access_token is None:
        return redirect('/login')

    if app.config['OAUTH_TOKEN'] is None:
        app.config['OAUTH_TOKEN'] = access_token

    configure_db(params=app.config['DB_PARAMS'], repos=github.get('/user/repos'))

    return redirect('/repos')


@app.route('/login')
def login():
    if app.config['OAUTH_TOKEN'] is None:
        return github.authorize()
    return redirect('/repos')


@app.route('/logout')
def logout():
    app.config['OAUTH_TOKEN'] = None
    delete_table(app.config['DB_PARAMS'])
    return 'You logged out'


if __name__ == '__main__':
    logfile = open('server_logs.log', 'a', encoding='utf-8')
    logging.basicConfig(stream=logfile, level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    delete_table(app.config['DB_PARAMS'])
    app.run(debug=False)

