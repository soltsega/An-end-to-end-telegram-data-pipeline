from dagster import define_asset_job, AssetSelection

# Define a job that materializes all our assets
daily_pipeline_job = define_asset_job(
    name="daily_pipeline_job",
    selection=AssetSelection.all()
)
