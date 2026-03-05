"""Gradio web interface for restaurant recommendations."""

from typing import Optional

import gradio as gr

from .recommend_logic import get_cuisines, get_locations, recommend


def build_ui():
    cuisines = get_cuisines()
    locations = get_locations()
    price_choices = ["Any", "low", "medium", "high", "very_high"]

    with gr.Blocks(title="Restaurant Recommendations", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# AI Restaurant Recommendations")
        gr.Markdown("Set your preferences and get personalized restaurant suggestions.")

        with gr.Row():
            cuisine_dd = gr.Dropdown(
                choices=cuisines,
                value="Any",
                label="Cuisine",
                allow_custom_value=False,
            )
            location_dd = gr.Dropdown(
                choices=locations,
                value="Any",
                label="Location",
                allow_custom_value=True,
            )
        with gr.Row():
            price_dd = gr.Dropdown(
                choices=price_choices,
                value="Any",
                label="Price range",
            )
            min_rating_num = gr.Number(
                value=None,
                label="Min rating (0-5)",
                minimum=0,
                maximum=5,
                step=0.5,
            )
            num_rec = gr.Slider(1, 20, value=5, step=1, label="Number of results")
        add_pref = gr.Textbox(
            label="Additional preferences (optional)",
            placeholder="e.g. vegetarian, outdoor seating",
            lines=1,
        )
        btn = gr.Button("Get recommendations", variant="primary")

        summary_out = gr.Textbox(label="Summary", interactive=False, lines=2)
        results_out = gr.Markdown(label="Recommendations")

        def on_click(c, l, p, r, n, a):
            results, summary = recommend(c, l, p, r, n, a)
            return results, summary

        btn.click(
            fn=on_click,
            inputs=[cuisine_dd, location_dd, price_dd, min_rating_num, num_rec, add_pref],
            outputs=[results_out, summary_out],
        )

    return demo


def run_ui(share: bool = False, server_port: Optional[int] = None):
    demo = build_ui()
    demo.launch(share=share, server_port=server_port or 7860)


if __name__ == "__main__":
    run_ui()
