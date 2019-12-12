import psycopg2
import logging
import sys

module_logger = logging.getLogger("GithubApi." + __name__)


def configure_db(params, repos):
    logger = logging.getLogger("GithubApi." + __name__ + '.' + sys._getframe().f_code.co_name)
    keys = ['name', 'html_url', 'description', 'created_at', 'watchers', 'private']
    create_table(params, col_names=keys)
    logger.info('table repos created')
    repos = [
        {
            key: x.get(key, '') for key in keys
        }
        for x in repos
    ]

    repos_values = [[x[key] for key in keys] for x in repos]
    insert_repos(params, repos_values, keys)
    logger.info('values inserted into table repos')


def delete_table(params):
    command = '''DROP TABLE IF EXISTS repos'''
    execute_command(params, command)


def select(params, repo_id=None):
    logger = logging.getLogger("GithubApi." + __name__ + '.' + sys._getframe().f_code.co_name)
    command = """SELECT * FROM repos"""
    if repo_id:
        command += """ WHERE repo_id=%s""" % repo_id
    repos = []
    conn = None
    try:
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(command)
        repos = cur.fetchall()
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return repos


def execute_command(params, command, args=None):
    logger = logging.getLogger("GithubApi." + __name__ + '.' + sys._getframe().f_code.co_name)

    conn = None
    try:
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(command, args)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()


def create_table(params, col_names):
    """ create table repos"""
    command = """
        CREATE TABLE IF NOT EXISTS repos (
            repo_id SERIAL PRIMARY KEY,
            %s VARCHAR(255) NOT NULL,
            %s VARCHAR(255) NOT NULL,
            %s VARCHAR(255),
            %s TIMESTAMP NOT NULL,
            %s INTEGER NOT NULL,
            %s BOOLEAN NOT NULL
        );
        """ % tuple(col_names, )
    execute_command(params, command)


def insert_repos(params, repo_list, col_names):
    """ insert multiple repos into the repos table  """
    command = '''INSERT INTO repos (%s, %s, %s, %s, %s, %s) ''' % tuple(col_names)
    command += '''VALUES(%s, %s, %s, %s, %s, %s) RETURNING repo_id;'''

    for repo in repo_list:
        execute_command(params, command, tuple(repo))
