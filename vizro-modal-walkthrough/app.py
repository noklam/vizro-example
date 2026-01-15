"""Vizro multi-page dashboard with a guided feature tour using Mantine UI.

This builds two Vizro pages with navigation and layers a custom Mantine-based
tour (ModalStack + tooltip) that can be triggered anywhere in the app.
"""

from typing import Literal

import dash_mantine_components as dmc
import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash import Input, Output, callback, ctx, dcc, html, no_update
from vizro import Vizro

# Sample data
df = px.data.iris()
pipeline_df = pd.DataFrame(
    {
        "run": list(range(1, 11)),
        "health": [92, 88, 90, 94, 96, 91, 93, 95, 97, 96],
    }
)

# Define walkthrough steps content
WALKTHROUGH_STEPS = [
    {
        "id": "modal-welcome",
        "title": "Welcome to Your Dashboard!",
        "content": "This walkthrough highlights the key chart. Click 'Next' to continue or 'Skip' to close the tour.",
    },
    {
        "id": "modal-charts",
        "title": "Overview Scatter",
        "content": "This scatter plot shows the relationship between sepal length and petal width by species.",
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
                withOverlay=False,  # keep background interactive while tour card is open
                closeOnClickOutside=False,
                trapFocus=False,
                overlayProps={"opacity": 0},
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
                # Modal Stack for walkthrough
                dmc.ModalStack(
                    id="walkthrough-modal-stack",
                    children=modals,
                ),
                # (POC) Only keep the overview-scatter tooltip
            ]
        )


# Register the custom component with Vizro (single instance to avoid duplicate ids)
vm.Page.add_type("components", WalkthroughModalStack)
WALKTHROUGH_COMPONENT = WalkthroughModalStack(id="walkthrough-tour")


# --- Callbacks for modal navigation ---

@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("tour-step", "data", allow_duplicate=True),
    Input("help-trigger-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_walkthrough(n_clicks):
    """Open the first modal when help button is clicked."""
    if n_clicks:
        return "modal-welcome", "modal-welcome"
    return no_update, no_update


@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Output("tour-step", "data", allow_duplicate=True),
    Input("btn-modal-welcome-next", "n_clicks"),
    prevent_initial_call=True,
)
def welcome_to_charts(n_clicks):
    """Navigate from welcome to charts modal."""
    if n_clicks:
        return "modal-charts", "modal-welcome", "modal-charts"
    return no_update, no_update, no_update


@callback(
    Output("walkthrough-modal-stack", "open", allow_duplicate=True),
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Output("tour-step", "data", allow_duplicate=True),
    Input("btn-modal-charts-back", "n_clicks"),
    prevent_initial_call=True,
)
def charts_back_to_welcome(n_clicks):
    """Navigate back from charts to welcome modal."""
    if n_clicks:
        return "modal-welcome", "modal-charts", "modal-welcome"
    return no_update, no_update, no_update
# Close all modals (skip or finish)
@callback(
    Output("walkthrough-modal-stack", "close", allow_duplicate=True),
    Output("tour-step", "data", allow_duplicate=True),
    Input("btn-skip-tour", "n_clicks"),
    Input("btn-finish-tour", "n_clicks"),
    prevent_initial_call=True,
)
def close_all_modals(skip_clicks, finish_clicks):
    """Close all modals when skip or finish is clicked."""
    triggered = ctx.triggered_id
    if triggered in ["btn-skip-tour", "btn-finish-tour"]:
        return [step["id"] for step in WALKTHROUGH_STEPS], None
    return no_update, no_update


# Sync tour popovers with the active walkthrough step
@callback(
    Output("tour-tip-charts", "opened"),
    Output("tour-debug", "children"),
    Input("tour-step", "data"),
)
def toggle_popovers(active_step):
    is_open = active_step == "modal-charts"
    return is_open, f"tour step={active_step} | tooltip_open={is_open}"


# --- Dashboard Setup (multi-page) ---

overview_page = vm.Page(
    title="Overview",
    components=[
        vm.Graph(
            id="pipeline-health-chart",
            title="Pipeline Health (last 10 runs)",
            figure=px.line(
                pipeline_df,
                x="run",
                y="health",
                markers=True,
            ).update_layout(margin=dict(l=20, r=20, t=40, b=20)),
        ),
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
            dmc.Tooltip(
                id="tour-tip-charts",
                label="Random note on the overview scatter.",
                target="#overview-scatter",
                opened=False,
                withArrow=True,
                position="right",
                withinPortal=True,
            ),
            dcc.Store(id="tour-step", data=None),
            html.Div(
                id="tour-debug",
                style={
                    "position": "fixed",
                    "bottom": "12px",
                    "left": "12px",
                    "zIndex": 3000,
                    "background": "rgba(0,0,0,0.7)",
                    "color": "white",
                    "padding": "6px 10px",
                    "borderRadius": "6px",
                    "fontSize": "12px",
                    "fontFamily": "monospace",
                },
            ),
        ],
    )


app.dash.layout = layout_with_walkthrough


if __name__ == "__main__":
    app.run(debug=True, port=8051)
