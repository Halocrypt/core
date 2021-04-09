def when_ready(server):
    print("Initialising log server")
    # touch app-initialized when ready
    try:
        open("/tmp/app-initialized", "w").close()
    except:
        pass


bind = "localhost:5001"
workers = 1
max_requests = 1200
max_requests_jitter = 10
timeout = 500
