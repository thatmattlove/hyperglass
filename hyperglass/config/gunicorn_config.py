import multiprocessing

command = "/usr/local/bin/gunicorn"
pythonpath = "/opt/hyperglass/hyperglass"
bind = "[::1]:8001"
workers = multiprocessing.cpu_count() * 2
user = "www-data"
