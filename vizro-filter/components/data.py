"""Data loading functions for Vizro dashboard."""

import vizro.plotly.express as px


def load_gapminder_data():
    """Load gapminder data from vizro.plotly.express.

    This function is registered with data_manager to enable lazy loading
    and cross-filtering across pages.

    Returns:
        DataFrame containing gapminder dataset
    """
    return px.data.gapminder()
