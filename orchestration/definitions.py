#This file is used to define the assets and jobs that will be used in the pipeline
# it is also used to define the dependencies between the assets
# it is also used to define the schedule for the pipeline

from dagster import Definitions, load_assets_from_modules
from . import assets, jobs

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    jobs=[jobs.daily_pipeline_job],
)
