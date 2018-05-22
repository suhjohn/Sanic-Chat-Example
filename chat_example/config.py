import os


DB_NAME = os.environ['RDS_DB_NAME']
DB_USER = os.environ['RDS_USERNAME']
DB_PASSWORD = os.environ['RDS_PASSWORD']
DB_HOST = os.environ["RDS_HOSTNAME"]
DB_PORT = os.environ["RDS_PORT"]
REDIS_HOSTNAME = os.environ["REDIS_HOSTNAME"]
REDIS_PORT = os.environ["REDIS_PORT"]