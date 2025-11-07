"""Vizro Dashboard Example using gapminder dataset with data_manager.

This example demonstrates Vizro best practices including:
- Custom charts using @capture("graph") decorator
- Data registration with data_manager for efficient data handling
- Cross-filtering across pages using data_manager
"""

import pandas as pd
import plotly.express as px
from vizro import Vizro
from vizro.managers import data_manager
from vizro.models import Dashboard, Page, Graph
from vizro.models.types import capture
from vizro.plotly.data import gapminder

# Register the gapminder dataset with data_manager for lazy loading
data_manager["gapminder"] = gapminder


@capture("graph")
def gapminder_line_chart(data_frame: pd.DataFrame):
    """Create a Gapminder line chart showing GDP trends.

    Args:
        data_frame: The gapminder dataset from data_manager

    Returns:
        Plotly express line chart figure
    """
    # Filter for a few countries to make the chart readable
    countries = ["United States", "China", "India", "Germany", "Brazil"]
    df_filtered = data_frame[data_frame["country"].isin(countries)]

    fig = px.line(
        df_filtered,
        x="year",
        y="gdpPercap",
        color="country",
        title="GDP per Capita Over Time (Selected Countries)"
    )
    return fig


@capture("graph")
def gapminder_scatter_chart(data_frame: pd.DataFrame):
    """Create a Gapminder scatter plot for the latest year.

    Args:
        data_frame: The gapminder dataset from data_manager

    Returns:
        Plotly express scatter chart figure
    """
    # Use the most recent year
    latest_year = data_frame['year'].max()
    df_latest = data_frame[data_frame['year'] == latest_year]

    fig = px.scatter(
        df_latest,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        title=f"Life Expectancy vs GDP per Capita ({latest_year})",
        size_max=60
    )
    fig.update_layout(xaxis_type="log")
    return fig


@capture("graph")
def gapminder_bar_chart(data_frame: pd.DataFrame):
    """Create a bar chart showing population by continent.

    Args:
        data_frame: The gapminder dataset from data_manager

    Returns:
        Plotly express bar chart figure
    """
    # Use the most recent year
    latest_year = data_frame['year'].max()
    df_latest = data_frame[data_frame['year'] == latest_year]

    # Sum population by continent
    continent_pop = df_latest.groupby('continent')['pop'].sum().reset_index()

    fig = px.bar(
        continent_pop,
        x="continent",
        y="pop",
        title=f"Total Population by Continent ({latest_year})",
        color="continent"
    )
    fig.update_layout(yaxis_title="Population")
    return fig


# Dashboard configuration
dashboard = Dashboard(
    title="Gapminder Data Dashboard",
    pages=[
        Page(
            title="Economic Trends",
            components=[
                Graph(
                    id="line_chart",
                    figure=gapminder_line_chart,
                )
            ]
        ),
        Page(
            title="Global Analysis",
            components=[
                Graph(
                    id="scatter_chart",
                    figure=gapminder_scatter_chart,
                ),
                Graph(
                    id="bar_chart",
                    figure=gapminder_bar_chart,
                )
            ]
        )
    ]
)


def main():
    """Run the Vizro dashboard."""
    # Build and run the dashboard
    app = Vizro().build(dashboard)
    app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
