"""Vizro multi-page dashboard with a guided feature tour using Mantine UI.

This builds two Vizro pages with navigation and layers a custom Mantine-based
tour (ModalStack + tooltip) that can be triggered anywhere in the app.
"""

from typing import Literal

import dash_mantine_components as dmc
import vizro.models as vm
import vizro.plotly.express as px
from dash import Input, Output, callback, ctx, html, no_update
from vizro import Vizro

# Sample data
df = px.data.iris()

# Define walkthrough steps content
WALKTHROUGH_STEPS = [
    {
        "id": "modal-welcome",
        "title": "Welcome to Your Dashboard!",
        "content": "This walkthrough highlights navigation, charts, and filters. Click 'Next' to continue or 'Skip' to close the tour.",
    },
    {
        "id": "modal-nav",
        "title": "Multi-page Navigation",
        "content": "Use the top navigation bar to switch between Overview and Deep Dive pages. The filter panel applies across pages.",
    },
    {
        "id": "modal-charts",
        "title": "Interactive Charts",
        "content": "Hover to see point details, drag to zoom, and double-click to reset. Both pages use the same Iris dataset so filters stay in sync.",
    },
    {
        "id": "modal-filters",
        "title": "Filtering Data",
        "content": "Use the species filter to narrow the view. Charts on whichever page you're on will update automatically.",
    },
    {
        "id": "modal-help",
        "title": "Getting Help",
        "content": "Click the floating '?' button anytime to reopen this tour. Feel free to skip or finish when you're done.",
    },
]


class WalkthroughModalStack(vm.VizroBaseModel):
    """Custom component for walkthrough modal stack using dash-mantine-components."""

    type: Literal["walkthrough_modal_stack"] = "walkthrough_modal_stack"

    def build(self):
        """Build the modal stack component with walkthrough steps."""
        total_steps = len(WALKTHROUGH_STEPS)
        modals = []

        for i, step in enumerate(WALKTHROUGH_STEPS):
            step_num = i + 1
            is_first = i == 0
            is_last = i == total_steps - 1

            # Build navigation buttons
            buttons = []
            if is_first:
                buttons.append(
                    dmc.Button("Skip Tour", id="btn-skip-tour", variant="subtle", color="gray")
                )
            else:
                buttons.append(
                    dmc.Button("← Back", id=f"btn-{step['id']}-back", variant="outline")
                )

            if is_last:
                buttons.append(
                    dmc.Button("Get Started", id="btn-finish-tour", color="green")
                )
            else:
                buttons.append(
                    dmc.Button("Next →", id=f"btn-{step['id']}-next", color="blue")
                )

            modal = dmc.ManagedModal(
                id=step["id"],
                title=step["title"],
                centered=False,
                overlayProps={"opacity": 0.25},
                styles={
                    "content": {
                        "position": "fixed",
                        "right": "20px",
                        "bottom": "20px",
                        "margin": 0,
                        "maxWidth": "360px",
                    }
                },
                children=[
                    dmc.Text(step["content"], mb="md"),
                    dmc.Text(
                        f"Step {step_num} of {total_steps}",
                        c="dimmed",
                        size="sm",
                        mb="md",
                    ),
                    dmc.Group(buttons, justify="flex-end"),
                ],
            )
            modals.append(modal)

        return html.Div(
            [
                # Help button to trigger walkthrough (tooltip gives a popover-style hint)
                dmc.Tooltip(
                    label="Start the guided tour",
                    withArrow=True,
                    position="left",
                    children=dmc.Button(
                        "?",
                        id="help-trigger-btn",
                        variant="filled",
                        color="blue",
                        radius="xl",
                        style={
                            "position": "fixed",
                            "bottom": "20px",
                            "right": "20px",
                            "zIndex": 1000,
                            "width": "44px",
                            "height": "44px",
                            "fontSize": "1.2rem",
                            "fontWeight": "bold",
                            "padding": 0,
                        },
                    ),
                ),
                # Modal Stack for walkthrough
                dmc.ModalStack(
                    id="walkthrough-modal-stack",
                    children=modals,
                ),
                # Popover-style highlights that sit next to key features during the tour
                dmc.Tooltip(
                    id="tour-tip-charts",
                    label="Interactive chart: hover, zoom, and filter to explore relationships.",
                    target="overview-scatter",
                    opened=False,
                    withArrow=True,
                    position="right",
                    withinPortal=False,
                ),
                dmc.Tooltip(
                    id="tour-tip-filters",
                    label="Use the species filter to slice the dataset; changes apply across pages.",
                    target="species-filter",
                    opened=False,
                    withArrow=True,
                    position="right",
                    withinPortal=False,
                ),
            ]
        )


# Register the custom component with Vizro (single instance to avoid duplicate ids)
vm.Page.add_type("components", WalkthroughModalStack)
WALKTHROUGH_COMPONENT = WalkthroughModalStack(id="walkthrough-tour")


# --- Callbacks for modal navigation ---

@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Input("help-trigger-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_walkthrough(n_clicks):
    """Open the first modal when help button is clicked."""
    if n_clicks:
        return "modal-welcome"
    return no_update


# Navigation: Welcome -> Nav
@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-modal-welcome-next", "n_clicks"),
    prevent_initial_call=True,
)
def welcome_to_nav(n_clicks):
    """Navigate from welcome to navigation modal."""
    if n_clicks:
        return "modal-nav", "modal-welcome"
    return no_update, no_update


# Navigation: Nav -> Welcome (back)
@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-modal-nav-back", "n_clicks"),
    prevent_initial_call=True,
)
def nav_back_to_welcome(n_clicks):
    """Navigate back from navigation to welcome modal."""
    if n_clicks:
        return "modal-welcome", "modal-nav"
    return no_update, no_update


# Navigation: Nav -> Charts
@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-modal-nav-next", "n_clicks"),
    prevent_initial_call=True,
)
def nav_to_charts(n_clicks):
    """Navigate from navigation to charts modal."""
    if n_clicks:
        return "modal-charts", "modal-nav"
    return no_update, no_update


# Navigation: Charts -> Nav (back)
@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-modal-charts-back", "n_clicks"),
    prevent_initial_call=True,
)
def charts_back_to_nav(n_clicks):
    """Navigate back from charts to navigation modal."""
    if n_clicks:
        return "modal-nav", "modal-charts"
    return no_update, no_update


# Navigation: Charts -> Filters
@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-modal-charts-next", "n_clicks"),
    prevent_initial_call=True,
)
def charts_to_filters(n_clicks):
    """Navigate from charts to filters modal."""
    if n_clicks:
        return "modal-filters", "modal-charts"
    return no_update, no_update


# Navigation: Filters -> Charts (back)
@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-modal-filters-back", "n_clicks"),
    prevent_initial_call=True,
)
def filters_back_to_charts(n_clicks):
    """Navigate back from filters to charts modal."""
    if n_clicks:
        return "modal-charts", "modal-filters"
    return no_update, no_update


# Navigation: Filters -> Help
@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-modal-filters-next", "n_clicks"),
    prevent_initial_call=True,
)
def filters_to_help(n_clicks):
    """Navigate from filters to help modal."""
    if n_clicks:
        return "modal-help", "modal-filters"
    return no_update, no_update


# Navigation: Help -> Filters (back)
@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-modal-help-back", "n_clicks"),
    prevent_initial_call=True,
)
def help_back_to_filters(n_clicks):
    """Navigate back from help to filters modal."""
    if n_clicks:
        return "modal-filters", "modal-help"
    return no_update, no_update


# Close all modals (skip or finish)
@callback(
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Input("btn-skip-tour", "n_clicks"),
    Input("btn-finish-tour", "n_clicks"),
    prevent_initial_call=True,
)
def close_all_modals(skip_clicks, finish_clicks):
    """Close all modals when skip or finish is clicked."""
    triggered = ctx.triggered_id
    if triggered in ["btn-skip-tour", "btn-finish-tour"]:
        return [step["id"] for step in WALKTHROUGH_STEPS]
    return no_update


# Sync tour popovers with the active walkthrough step
@callback(
    Output("tour-tip-charts", "opened"),
    Output("tour-tip-filters", "opened"),
    Input("walkthrough-modal-stack", "open"),
)
def toggle_popovers(active_step):
    show_charts = active_step == "modal-charts"
    show_filters = active_step == "modal-filters"
    return show_charts, show_filters


# --- Dashboard Setup (multi-page) ---

overview_page = vm.Page(
    title="Overview",
    components=[
        vm.Graph(
            id="overview-scatter",
            title="Sepal Length vs Petal Width",
            figure=px.scatter(
                df,
                x="sepal_length",
                y="petal_width",
                color="species",
            ),
        ),
        vm.Graph(
            id="overview-hist",
            title="Distribution of Sepal Width by Species",
            figure=px.histogram(
                df,
                x="sepal_width",
                color="species",
            ),
        ),
    ],
    controls=[vm.Filter(id="species-filter", column="species")],
)

deep_dive_page = vm.Page(
    title="Deep Dive",
    components=[
        vm.Graph(
            id="deepdive-scatter",
            title="Petal Length vs Petal Width",
            figure=px.scatter(
                df,
                x="petal_length",
                y="petal_width",
                color="species",
            ),
        ),
        vm.Graph(
            id="deepdive-box",
            title="Sepal Length Distribution",
            figure=px.box(
                df,
                x="species",
                y="sepal_length",
                color="species",
            ),
        ),
    ],
    controls=[vm.Filter(id="species-filter-deep", column="species")],
)

dashboard = vm.Dashboard(pages=[overview_page, deep_dive_page])


# Layer the walkthrough on top of the Vizro layout so it follows the user across pages.
app = Vizro().build(dashboard)
original_layout = app.dash.layout


def layout_with_walkthrough():
    base_layout = original_layout() if callable(original_layout) else original_layout
    return dmc.MantineProvider(
        withGlobalClasses=True,
        children=[
            WALKTHROUGH_COMPONENT.build(),
            base_layout,
        ],
    )


app.dash.layout = layout_with_walkthrough


if __name__ == "__main__":
    app.run(debug=True)
