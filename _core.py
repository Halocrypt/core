from set_env import setup_env

setup_env()
from app.main import app

if __name__ == "__main__":

    import uvicorn

    uvicorn.run("app.main:app", reload=True, debug=True, port=5000)
