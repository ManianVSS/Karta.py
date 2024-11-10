from fastapi import FastAPI
from starlette.responses import FileResponse

from framework.core.models.Context import Context
from framework.core.models.TestFeature import TestFeature
from framework.core.models.TestStep import TestStep
from framework.core.runner.KartaRuntime import KartaRuntime

karta_runtime = KartaRuntime(step_def_package='step_definitions')
karta_runtime.init_framework()

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
    return [key for key in karta_runtime.default_step_runner.get_steps().keys()]


@app.post("/run_feature")
async def run_feature_api(feature: TestFeature):
    return karta_runtime.run_feature(feature)


@app.post("/run_step")
async def run_step_api(step: TestStep):
    context = Context()
    return karta_runtime.run_step(step, context)
