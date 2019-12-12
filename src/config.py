import logging
import sys

from configparser import ConfigParser

module_logger = logging.getLogger("GithubApi." + __name__)


def config(filename, section='postgresql'):
    logger = logging.getLogger("GithubApi." + __name__ + '.' + sys._getframe(  ).f_code.co_name)

    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        logger.error('Section {0} not found in the {1} file'.format(section, filename))

    return db
