import uvicorn

from framework.core.runner.main import init_framework
from framework.server.main import app

if __name__ == "__main__":
    init_framework('step_definitions')
    uvicorn.run(app, host="0.0.0.0", port=8000)
