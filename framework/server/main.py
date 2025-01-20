import traceback
from datetime import datetime

from fastapi import FastAPI
from fastapi import Request
from starlette.responses import FileResponse

from framework.core.models.generic import Context
from framework.core.models.test_catalog import TestFeature, TestStep
from framework.core.models.test_execution import StepResult, Run
from framework.runner.runtime import karta_runtime

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
    return [key for key in karta_runtime.get_steps()]


@app.post("/run_feature")
async def run_feature_api(feature: TestFeature):
    return karta_runtime.run_feature(Run(), feature)


@app.post("/run_gherkin_feature")
async def run_feature_api(request: Request):
    """
    <b><u>Can't try this out in the swagger UI as body input is not being allowed due to a limitation</u></b>.<br>
    To use this you need to pass a gherkin feature file contents in body and set content type to text/plain
    """
    feature_source = (await request.body()).decode("utf-8")
    feature = karta_runtime.plugins['Gherkin'].parse_feature(feature_source)
    feature.source = request.query_params["source"] if ("source" in request.query_params.keys()) else request.url.path
    return karta_runtime.run_feature(Run(),feature)


@app.post("/run_step")
async def run_step_api(step: TestStep):
    context = Context()
    context.data = {}
    start_time = datetime.now()
    try:
        return karta_runtime.run_step(Run(), None, None, step, context)
    except Exception as e:
        step_result = StepResult(name=step.name)
        step_result.start_time = start_time
        step_result.successful = False
        step_result.error = str(e) + "\n" + traceback.format_exc()
        step_result.end_time = datetime.now()
        return step_result


@app.get("/get_catalog")
async def get_catalog():
    return karta_runtime.test_catalog_manager.get_catalog()


@app.post("/run_tags")
async def run_tags(tags: set[str]):
    return karta_runtime.run_tags(tags)
