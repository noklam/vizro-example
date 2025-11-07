"""Custom chart functions for Vizro dashboard.

This module contains chart functions decorated with @capture("graph")
that can be used in Vizro Graph components. Each function accepts a
data_frame parameter and optional filter parameters like year.
"""

import pandas as pd
import vizro.plotly.express as px
from vizro.models.types import capture


@capture("graph")
def gapminder_line_chart(data_frame: pd.DataFrame, year=None):
    """Create a Gapminder line chart showing GDP trends.

    The year parameter is controlled by the Parameter component to filter data.
    When year is provided as a range, it filters the data accordingly.

    Args:
        data_frame: The gapminder dataset from data_manager
        year: Optional year range filter from Parameter component [min_year, max_year]

    Returns:
        Plotly express line chart figure
    """
    # Apply year filter if provided
    if year is not None:
        min_year, max_year = year
        data_frame = data_frame[(data_frame["year"] >= min_year) & (data_frame["year"] <= max_year)]

    # Filter for a few countries to make the chart readable
    countries = ["United States", "China", "India", "Germany", "Brazil"]
    df_filtered = data_frame[data_frame["country"].isin(countries)]

    fig = px.line(
        df_filtered,
        x="year",
        y="gdpPercap",
        color="country",
        title="GDP per Capita Over Time (Selected Countries)",
    )
    return fig


@capture("graph")
def gapminder_scatter_chart(data_frame: pd.DataFrame, year=None):
    """Create a Gapminder scatter plot for the latest year.

    The year parameter is controlled by the Parameter component to filter data.
    When year is provided as a range, it filters the data accordingly.

    Args:
        data_frame: The gapminder dataset from data_manager
        year: Optional year range filter from Parameter component [min_year, max_year]

    Returns:
        Plotly express scatter chart figure
    """
    # Apply year filter if provided
    if year is not None:
        min_year, max_year = year
        data_frame = data_frame[(data_frame["year"] >= min_year) & (data_frame["year"] <= max_year)]

    # Use the most recent year from filtered data
    latest_year = data_frame["year"].max()
    df_latest = data_frame[data_frame["year"] == latest_year]

    fig = px.scatter(
        df_latest,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        title=f"Life Expectancy vs GDP per Capita ({latest_year})",
        size_max=60,
    )
    fig.update_layout(xaxis_type="log")
    return fig


@capture("graph")
def gapminder_bar_chart(data_frame: pd.DataFrame, year=None):
    """Create a bar chart showing population by continent.

    The year parameter is controlled by the Parameter component to filter data.
    When year is provided as a range, it filters the data accordingly.

    Args:
        data_frame: The gapminder dataset from data_manager
        year: Optional year range filter from Parameter component [min_year, max_year]

    Returns:
        Plotly express bar chart figure
    """
    # Apply year filter if provided
    if year is not None:
        min_year, max_year = year
        data_frame = data_frame[(data_frame["year"] >= min_year) & (data_frame["year"] <= max_year)]

    # Use the most recent year from filtered data
    latest_year = data_frame["year"].max()
    df_latest = data_frame[data_frame["year"] == latest_year]

    # Sum population by continent
    continent_pop = df_latest.groupby("continent")["pop"].sum().reset_index()

    fig = px.bar(
        continent_pop,
        x="continent",
        y="pop",
        title=f"Total Population by Continent ({latest_year})",
        color="continent",
    )
    fig.update_layout(yaxis_title="Population")
    return fig
