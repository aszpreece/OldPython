import mariadb
from enum import Enum

class ExperimentStatus(Enum):
    NOT_STARTED='NOTSTARTED'
    RUNNING='RUNNING'
    COMPLETE='COMPLETE'

# Schema of experiments for reference

# CREATE TABLE IF NOT EXISTS experiments (
#     id INTEGER NOT NULL AUTO_INCREMENT,
#     alias VARCHAR(30) NOT NULL,
#     exp_status VARCHAR(5) NOT NULL,
#     PRIMARY KEY (id)
# );

def create_experiment(connection, alias, context):

    """Creates an experiment for the given context user with a status of 'NOTSTARTED'. 
    Remember to call commit after this operation.

    Args:
        connection (Connection): The connection object.
        alias (str): The alias of the experiment. Must be unique to this user.
        context (Context): The context object for this user.
    """    
    sql = """
    INSERT INTO 
        experiments (alias, exp_status)
    VALUES
        (?, ?)
    """
    data = (alias, ExperimentStatus.NOT_STARTED)
    context.logger.debug('Creating experiment entry.')
    cur = connection.cursor()
    try:
        cur.execute(sql, data)
    except mariadb.Error as e: 
        context.logger.error(f"Error: {e}")
    context.logger.debug('Creating experiment entry.')

def get_experiments(connection, context):
    """Fetches all experiments created by the user.

    Args:
        connection (Connection): The connection object.
        context (Context): The context object for the user.
    """    
    sql = """
    SELECT id, alias, exp_status
    FROM experiments
    """
    data = (alias, ExperimentStatus.NOT_STARTED,)
    cur = connection.cursor()
    try: 
        cur.execute(sql, data) 
    except mariadb.Error as e: 
        print(f"Error: {e}")