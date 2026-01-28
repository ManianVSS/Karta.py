import traceback
from datetime import datetime

from fastapi import FastAPI
# from fastapi import Request
from starlette.responses import FileResponse

from karta.core.models.generic import Context
from karta.core.models.test_catalog import Feature, Scenario
from karta.core.models.test_execution import StepResult, Run, FeatureResult, RunResult
from karta.runner.runtime import karta_runtime
from karta.server.models import FeatureRunInfo, FeatureSourceRunInfo, StepRunInfo, TagRunInfo

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
async def get_steps() -> list[str]:
    return [key for key in karta_runtime.get_steps()]


@app.post("/run_tags")
async def run_tags(tag_run_info: TagRunInfo) -> RunResult:
    tags = set(tag_run_info.tags)
    context = Context(tag_run_info.context) if tag_run_info.context else Context()
    return karta_runtime.run_tags(tags=tags, run_name=tag_run_info.name, run_description=tag_run_info.description,
                                  context=context)


@app.post("/run_feature")
async def run_feature_api(feature_run_info: FeatureRunInfo) -> FeatureResult:
    run = Run()
    run.name = feature_run_info.name
    run.description = feature_run_info.description
    feature = feature_run_info.feature
    context = Context(feature_run_info.context) if feature_run_info.context else Context()
    return karta_runtime.run_feature(run, feature, context)


@app.post("/run_feature_source")
async def run_feature_source_api(feature_source_run_info: FeatureSourceRunInfo) -> FeatureResult:
    run = Run()
    run.name = feature_source_run_info.name
    run.description = feature_source_run_info.description
    feature = karta_runtime.plugins['Kriya'].parse_feature(feature_source_run_info.source)
    context = Context(feature_source_run_info.context) if feature_source_run_info.context else Context()
    return karta_runtime.run_feature(run, feature, context)


# @app.post("/run_feature_source")
# async def run_feature_api(request: Request):
#     """
#     <b><u>Can't try this out in the swagger UI as body input is not being allowed due to a limitation</u></b>.<br>
#     To use this you need to pass a gherkin feature file contents in body and set content type to text/plain
#     """
#     feature_source = (await request.body()).decode("utf-8")
#     feature = karta_runtime.plugins['Kriya'].parse_feature(feature_source)
#     feature.source = request.query_params["source"] if ("source" in request.query_params.keys()) else request.url.path
#     return karta_runtime.run_feature(Run(), feature, Context())

# @app.post("/run_scenario")
# async def run_scenario_api(scenario_run_info: ScenarioRunInfo) -> ScenarioResult:
#     context = Context(scenario_run_info.context) if scenario_run_info.context else Context()
#     if not context.data:
#         context.data = {}
#     start_time = datetime.now()
#
#     feature_name = scenario_run_info.feature_name
#     iteration_index = scenario_run_info.iteration_index
#     scenario = scenario_run_info.scenario
#
#     run = Run()
#     run.name = scenario_run_info.name
#     run.description = scenario_run_info.description
#
#     return karta_runtime.run_scenario(run, feature_name, iteration_index, scenario, context)


run_contexts: dict[str, Context] = {}
feature_contexts: dict[str, Context] = {}
scenario_contexts: dict[str, Context] = {}


@app.post("/registry/run_start")
async def run_start(context: dict):
    context = Context(context) if context else Context()
    run = context.run if context.run else Run()
    run_contexts[run.name] = context


@app.post("/run_step")
async def run_step_api(step_run_info: StepRunInfo) -> StepResult:
    context = Context(step_run_info.context) if step_run_info.context else Context()
    if not context.data:
        context.data = {}
    start_time = datetime.now()

    feature_name = step_run_info.feature_name
    iteration_index = step_run_info.iteration_index
    scenario_name = step_run_info.scenario_name
    step = step_run_info.step

    run = Run()
    run.name = step_run_info.name
    run.description = step_run_info.description

    try:
        return karta_runtime.run_step(run, feature_name, iteration_index, scenario_name, step, context)
    except Exception as e:
        step_result = StepResult(name=step.identifier)
        step_result.start_time = start_time
        step_result.successful = False
        step_result.error = str(e) + "\n" + traceback.format_exc()
        step_result.end_time = datetime.now()
        return step_result


@app.get("/list_scenarios")
async def list_scenarios() -> list[Scenario]:
    return karta_runtime.test_catalog_manager.list_scenarios()


@app.get("/list_features")
async def list_features() -> dict[str, Feature]:
    return karta_runtime.test_catalog_manager.list_features()
