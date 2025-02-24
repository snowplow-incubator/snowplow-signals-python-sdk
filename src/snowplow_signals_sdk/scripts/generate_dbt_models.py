import json
from models.data_model_autogen.filtered_events_data_model import FilteredEventsDataModel
from typing_extensions import Annotated
import typer


def generate(
    update: Annotated[bool, typer.Option()] = False,
):
    """
    Generate a data model .sql files from the config file
    """

    data_model = FilteredEventsDataModel()
    print("Generating Data Models...")

    with open("dbt_project/utils/config.json") as f:
        data = json.load(f)

    context = {
        "properties": data["properties"],
        "event_names": data["event_names"],
    }

    try:
        data_model.generate_filtered_events_table(update=update, context=context)

    except ValueError as e:
        print(e)
        raise typer.Exit()

    print("✅ Finished generating!")


if __name__ == "__main__":
    generate(update=True)
