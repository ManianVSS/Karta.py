from fastapi import FastAPI
from starlette.responses import FileResponse

from framework.core.models.Context import Context
from framework.core.models.TestFeature import TestFeature
from framework.core.models.TestStep import TestStep
from framework.core.runner.main import run_feature, init_framework, default_step_runner, run_step

init_framework('step_definitions')

app = FastAPI(
    title="Karta.py",
    description="Karta.py is a port of Karta test automation framework to python.",
    version="0.0.1",
    contact={
        "name": "Manian VSS",
        "url": "http://github.com/manianvss/Karta.py",
        "email": "manianvss@hotmail.com",
    },
    license_info={
        "name": "BSD 3 Clause",
        "url": "https://github.com/ManianVSS/Karta.py/blob/main/LICENSE",
    },
)


@app.get("/")
async def get_index_html():
    return FileResponse("templates/index.html")


@app.get("/steps")
async def get_steps():
    return [key for key in default_step_runner.get_steps().keys()]


@app.post("/run_feature")
async def run_feature_api(feature: TestFeature):
    return run_feature(feature)


@app.post("/run_step")
async def run_step_api(step: TestStep):
    context = Context()
    return run_step(step, context)
