"""Parameter components for cross-page filtering.

This module contains functions to create Vizro Parameter components
with custom Dash callbacks for cross-page synchronization using dcc.Store.
"""

from typing import List

import dash
import vizro.models as vm
from dash import Input, Output, State, callback
from vizro.managers import data_manager


def create_date_range_parameters(prefix: str, data_frame: str, target_components: List[str]):
    """Create cross-page date range parameters using Dash callbacks.

    This creates a parameter that filters data by year range across multiple pages.
    The callbacks sync the state between different page parameters using dcc.Store,
    enabling cross-page filtering with independent parameter instances.

    The function creates two callbacks:
    1. sync_to_store: Updates the shared store when this parameter's slider changes
    2. sync_from_store: Updates this parameter's slider when the store changes from another page

    Args:
        prefix: Prefix for component IDs to avoid conflicts between pages
        data_frame: Name of the data frame registered in data_manager
        target_components: List of component IDs (Graph IDs) to target with the filter

    Returns:
        List containing a single vm.Parameter instance with RangeSlider selector
    """

    # Callback to sync this parameter's value TO the shared store
    # allow_duplicate=True because multiple pages can write to the same store
    @callback(
        Output("year_range_store", "data", allow_duplicate=True),
        Input(f"{prefix}year_range-selector", "value"),
        State("year_range_store", "data"),
        prevent_initial_call=True,
    )
    def sync_to_store(selected_range, stored_data):
        """Update the shared store when this parameter changes.

        Args:
            selected_range: Current value from the slider [min_year, max_year]
            stored_data: Current value in the store (unused but needed for State)

        Returns:
            The selected range to store in dcc.Store
        """
        return selected_range

    # Callback to sync FROM the shared store to this parameter
    @callback(
        Output(f"{prefix}year_range-selector", "value"),
        Input("year_range_store", "data"),
        State(f"{prefix}year_range-selector", "value"),
        prevent_initial_call=True,
    )
    def sync_from_store(stored_range, current_value):
        """Update this parameter when the shared store changes from another page.

        This callback prevents infinite loops by only updating when the value
        actually changed. This is crucial for bidirectional synchronization.

        Args:
            stored_range: The new value from the store [min_year, max_year]
            current_value: Current value of this slider

        Returns:
            Either the new value to update the slider, or dash.no_update to skip
        """
        # Only update if the value actually changed to avoid infinite loops
        if stored_range != current_value:
            return stored_range
        return dash.no_update

    # Get year range from data_manager using .load() method
    df = data_manager[data_frame].load()
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())

    year_range_parameter = vm.Parameter(
        id=f"{prefix}year_range",
        targets=[f"{component_id}.year" for component_id in target_components],
        selector=vm.RangeSlider(
            id=f"{prefix}year_range-selector",
            title="Year Range",
            min=min_year,
            max=max_year,
            step=5,
            value=[min_year, max_year],
        ),
    )

    return [year_range_parameter]
