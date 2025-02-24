from typing import Dict, Any, List, Set, FrozenSet
from pydantic import BaseModel
from models.data_model_autogen.modeling_step import (
    ModelingStep,
    FilterCombinator,
    FilterCondition,
)
import re


class DbtConfigGenerator(BaseModel):
    data: Dict[str, Any]

    def create_dbt_config(self) -> Dict[str, Any]:
        """
        Process overview config in case there are changes and prepare properties for the jinja template.
        """

        aggregate_features = []
        first_value_features = []
        last_value_features = []

        features = self.data.get("transformed_features", [])
        for feature in features:
            for step in feature:
                if step["step_type"] == "daily_aggregation":
                    if step["type"] == "first":
                        first_value_features.append(
                            {
                                "step_type": step["step_type"],
                                "type": step["type"],
                                "column_name": step["column_name"],
                                "condition_clause": step["column_name"].removesuffix(
                                    "_first"
                                ),
                            }
                        )
                    elif step["type"] == "last":
                        last_value_features.append(
                            {
                                "step_type": step["step_type"],
                                "type": step["type"],
                                "column_name": step["column_name"],
                                "condition_clause": step["column_name"].removesuffix(
                                    "_last"
                                ),
                            }
                        )
                    else:
                        condition_clause = "case when "
                        conditions = (
                            step["filter"]["condition"] if step["filter"] else []
                        )
                        combinator = (
                            " " + step["filter"]["combinator"] + " "
                            if step["filter"]
                            else "and"
                        )
                        condition_statements = []  # Collect all condition strings

                        for condition in conditions:
                            prop = condition["property"]
                            value = condition["value"]
                            operator = condition["operator"]

                            # Format SQL based on operator type
                            if operator == "equals":
                                condition_sql = f"{prop} = '{value}'"
                            elif operator == "like":
                                condition_sql = f"{prop} LIKE '%{value}%'"
                            elif operator == "greater_than":
                                condition_sql = f"{prop} > {value}"
                            elif operator == "less_than":
                                condition_sql = f"{prop} < {value}"
                            else:
                                raise ValueError(f"Unsupported operator: {operator}")

                            condition_statements.append(
                                f"{condition_sql}"
                            )  # Wrap condition in parentheses

                        # Join conditions with the combinator (AND/OR)
                        condition_clause += f" {' '.join([combinator.join(condition_statements)])} then 1 else 0 end"

                        aggregate_features.append(
                            {
                                "step_type": step["step_type"],
                                "type": step["type"],
                                "column_name": step["column_name"],
                                "condition_clause": condition_clause,
                            }
                        )

        config = {
            "events": self.data["events"],
            "properties": self.data["properties"],
            "event_names": self.data["event_names"],
            "aggregate_features": aggregate_features,
            "first_value_features": first_value_features,
            "last_value_features": last_value_features,
        }

        return config
