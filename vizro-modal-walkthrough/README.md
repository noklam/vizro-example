# Vizro multi-page dashboard with a Mantine feature tour

This example shows how to build a two-page Vizro dashboard and overlay a guided tour built with Dash Mantine Components (`ModalStack` + tooltip). The tour is mounted once at the layout level so it follows the user across pages.

## Features

- Multi-page Vizro dashboard (Overview + Deep Dive) with the built-in top navigation
- Iris dataset visuals using Plotly Express, plus shared filters on both pages
- Floating Mantine help button with tooltip; opens a multi-step tour (ManagedModal stack)
- Back/next/skip controls with optional finish CTA to close the tour
- Layout wrapper keeps the tour available everywhere without altering Vizro internals

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:8050 to explore.

## How it works

- `WalkthroughModalStack` (in app.py) builds a help button and a Mantine `ModalStack` of steps.
- After building the Vizro dashboard, the original Dash layout is wrapped so the tour component sits outside individual pages, making it global.
- Dash callbacks handle the step-to-step navigation (open/close ManagedModal ids) and the skip/finish actions.

### Customize the tour

Edit `WALKTHROUGH_STEPS` in `app.py` to change titles, body text, or step count. Each entry needs an `id`, `title`, and `content`.

### Extend the UI

- Add more Vizro pages or filters; the navigation bar updates automatically.
- Replace the tooltip with another Mantine overlay (e.g., Popover or Spotlight) if you want a different entry point for the tour.
