import json
from models.data_model_autogen.dbt_config_generator import DbtConfigGenerator
from models.data_model_autogen.filtered_events_data_model import FilteredEventsDataModel
from models.data_model_autogen.filtered_events_this_run_data_model import (
    FilteredEventsThisRunDataModel,
)
from models.data_model_autogen.daily_agg_this_run_data_model import (
    DailyAggThisRunDataModel,
)
from models.data_model_autogen.daily_agg_data_model import DailyAggDataModel

from typing_extensions import Annotated
import typer


def generate(
    update: Annotated[bool, typer.Option()] = False,
    utils_path: Annotated[str, typer.Option()] = "dbt_project/utils/config.json",
):
    """
    Generate data model .sql files from the config file
    """

    with open(utils_path) as f:
        data = json.load(f)

    generator = DbtConfigGenerator(data=data)
    context = generator.create_dbt_config()

    print("Generating Data Models...")

    filtered_events_this_run_data_model = FilteredEventsThisRunDataModel()
    filtered_events_data_model = FilteredEventsDataModel()
    daily_agg_this_run_data_model = DailyAggThisRunDataModel()
    daily_agg_data_model = DailyAggDataModel()

    try:
        filtered_events_this_run_data_model.generate_filtered_events_this_run_table(
            update=update, context=context
        )
        filtered_events_data_model.generate_filtered_events_table(
            update=update, context=context
        )
        daily_agg_this_run_data_model.generate_daily_agg_this_run_table(
            update=update, context=context
        )
        daily_agg_data_model.generate_daily_agg_table(update=update, context=context)

    except ValueError as e:
        print(e)
        raise typer.Exit()

    print("✅ Finished generating!")


if __name__ == "__main__":
    generate(update=True, utils_path="dbt_project/utils/config.json")
