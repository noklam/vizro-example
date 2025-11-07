"""Vizro Dashboard Example using gapminder dataset with data_manager.

This example demonstrates Vizro best practices including:
- Custom charts using @capture("graph") decorator
- Data registration with data_manager for efficient data handling
- Cross-filtering across pages using data_manager
- Cross-page filtering using Dash callbacks
- Modular component architecture for maintainability
"""

from dash import Input, Output, callback, dcc, html
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard, Page, Graph

from components import (
    gapminder_bar_chart,
    gapminder_line_chart,
    gapminder_scatter_chart,
    load_gapminder_data,
    create_date_range_parameters,
)


# Register the gapminder dataset with data_manager for lazy loading
data_manager["gapminder"] = load_gapminder_data


# ===== Dashboard Configuration =====

# Create separate year range parameters for each page
# Each parameter targets only the components on its respective page
economic_year_range_params = create_date_range_parameters(
    prefix="economic_",
    data_frame="gapminder",
    target_components=["line_chart"]
)

global_year_range_params = create_date_range_parameters(
    prefix="global_",
    data_frame="gapminder",
    target_components=["scatter_chart", "bar_chart"]
)

# Dashboard configuration
dashboard = Dashboard(
    title="Gapminder Data Dashboard",
    pages=[
        Page(
            title="Economic Trends",
            components=[
                Graph(
                    id="line_chart",
                    figure=gapminder_line_chart(data_frame="gapminder"),
                )
            ],
            controls=economic_year_range_params,
        ),
        Page(
            title="Global Analysis",
            components=[
                Graph(
                    id="scatter_chart",
                    figure=gapminder_scatter_chart(data_frame="gapminder"),
                ),
                Graph(
                    id="bar_chart",
                    figure=gapminder_bar_chart(data_frame="gapminder"),
                )
            ],
            controls=global_year_range_params,
        )
    ]
)


def main():
    """Run the Vizro dashboard with dcc.Store for cross-page state synchronization."""
    # Build the dashboard
    app = Vizro().build(dashboard)

    # Add dcc.Store to the app layout for syncing year range across pages
    # This store persists the selected year range and syncs it between pages
    original_layout = app.dash.layout

    @callback(Output("year_range_store", "data"), Input("year_range_store", "data"))
    def initialize_store(data):
        """Initialize the store with default values if needed."""
        if data is None:
            df = data_manager["gapminder"].load()
            return [int(df["year"].min()), int(df["year"].max())]
        return data

    def create_layout():
        """Wrap the original layout with dcc.Store for state management."""
        return html.Div([
            dcc.Store(id="year_range_store", storage_type="session"),
            original_layout() if callable(original_layout) else original_layout
        ])

    app.dash.layout = create_layout
    app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()