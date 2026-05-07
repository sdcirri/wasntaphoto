worker_class = 'uvicorn.workers.UvicornWorker'
bind = '0.0.0.0:8000'
workers = 3
worker_tmp_dir = '/dev/shm'
pidfile = '/app/.gunicorn'
control_socket_disable = True
