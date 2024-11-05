from fastapi import FastAPI
from starlette.responses import FileResponse

from framework.core.models.Context import Context
from framework.core.models.TestFeature import TestFeature
from framework.core.runner import step_definition_mapping
from framework.core.runner.main import run_feature, init_framework

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
async def root():
    return FileResponse("templates/index.html")


@app.get("/steps")
async def root():
    return [key for key in step_definition_mapping.keys()]


@app.post("/run_feature")
async def root(feature: dict):
    return run_feature(TestFeature(**feature))


@app.post("/run_step")
async def root(feature_name: str, scenario_name: str, step_identifier: str, data: dict):
    context = Context()
    context.feature_name = feature_name
    context.scenario_name = scenario_name
    context.step_name = step_identifier
    context.step_data = data
    step_definition_mapping[step_identifier](context=context)
    return context

