from pathlib import Path
import gradio as gr
from PIL import Image
from apps.stable_diffusion.scripts import txt2img_inf
from apps.stable_diffusion.src import prompt_examples, args
from apps.stable_diffusion.web.ui.utils import (
    available_devices,
    nodlogo_loc,
    get_custom_model_path,
    get_custom_model_files,
    scheduler_list_txt2img,
    predefined_models,
)

with gr.Blocks(title="Text-to-Image") as txt2img_web:
    with gr.Row(elem_id="ui_title"):
        nod_logo = Image.open(nodlogo_loc)
        with gr.Row():
            with gr.Column(scale=1, elem_id="demo_title_outer"):
                gr.Image(
                    value=nod_logo,
                    show_label=False,
                    interactive=False,
                    elem_id="top_logo",
                ).style(width=150, height=50)
    with gr.Row(elem_id="ui_body"):
        with gr.Row():
            with gr.Column(scale=1, min_width=600):
                with gr.Row():
                    with gr.Column(scale=10):
                        with gr.Row():
                            custom_model = gr.Dropdown(
                                label=f"Models (Custom Model path: {get_custom_model_path()})",
                                value=args.ckpt_loc
                                if args.ckpt_loc
                                else "None",
                                choices=get_custom_model_files()
                                + predefined_models,
                            )
                            hf_model_id = gr.Textbox(
                                placeholder="Select 'None' in the Models dropdown on the left and enter model ID here e.g: SG161222/Realistic_Vision_V1.3",
                                value="",
                                label="HuggingFace Model ID",
                                lines=3,
                            )
                    with gr.Column(scale=1, min_width=170):
                        png_info_img = gr.Image(
                            label="Import PNG info",
                            elem_id="txt2img_prompt_image",
                            type="pil",
                            tool="None",
                            visible=True,
                        )

                with gr.Group(elem_id="prompt_box_outer"):
                    prompt = gr.Textbox(
                        label="Prompt",
                        value=args.prompts[0],
                        lines=1,
                        elem_id="prompt_box",
                    )
                    negative_prompt = gr.Textbox(
                        label="Negative Prompt",
                        value=args.negative_prompts[0],
                        lines=1,
                        elem_id="negative_prompt_box",
                    )
                with gr.Accordion(label="Advanced Options", open=False):
                    with gr.Row():
                        scheduler = gr.Dropdown(
                            label="Scheduler",
                            value=args.scheduler,
                            choices=scheduler_list_txt2img,
                        )
                        with gr.Group():
                            save_metadata_to_png = gr.Checkbox(
                                label="Save prompt information to PNG",
                                value=args.write_metadata_to_png,
                                interactive=True,
                            )
                            save_metadata_to_json = gr.Checkbox(
                                label="Save prompt information to JSON file",
                                value=args.save_metadata_to_json,
                                interactive=True,
                            )
                    with gr.Row():
                        height = gr.Slider(
                            384, 768, value=args.height, step=8, label="Height"
                        )
                        width = gr.Slider(
                            384, 768, value=args.width, step=8, label="Width"
                        )
                        precision = gr.Radio(
                            label="Precision",
                            value=args.precision,
                            choices=[
                                "fp16",
                                "fp32",
                            ],
                            visible=False,
                        )
                        max_length = gr.Radio(
                            label="Max Length",
                            value=args.max_length,
                            choices=[
                                64,
                                77,
                            ],
                            visible=False,
                        )
                    with gr.Row():
                        steps = gr.Slider(
                            1, 100, value=args.steps, step=1, label="Steps"
                        )
                        guidance_scale = gr.Slider(
                            0,
                            50,
                            value=args.guidance_scale,
                            step=0.1,
                            label="CFG Scale",
                        )
                    with gr.Row():
                        batch_count = gr.Slider(
                            1,
                            100,
                            value=args.batch_count,
                            step=1,
                            label="Batch Count",
                            interactive=True,
                        )
                        batch_size = gr.Slider(
                            1,
                            4,
                            value=args.batch_size,
                            step=1,
                            label="Batch Size",
                            interactive=True,
                        )
                with gr.Row():
                    seed = gr.Number(
                        value=args.seed, precision=0, label="Seed"
                    )
                    device = gr.Dropdown(
                        label="Device",
                        value=available_devices[0],
                        choices=available_devices,
                    )
                with gr.Row():
                    random_seed = gr.Button("Randomize Seed")
                    random_seed.click(
                        None,
                        inputs=[],
                        outputs=[seed],
                        _js="() => -1",
                    )
                    stable_diffusion = gr.Button("Generate Image(s)")
                with gr.Accordion(label="Prompt Examples!", open=False):
                    ex = gr.Examples(
                        examples=prompt_examples,
                        inputs=prompt,
                        cache_examples=False,
                        elem_id="prompt_examples",
                    )

            with gr.Column(scale=1, min_width=600):
                with gr.Group():
                    txt2img_gallery = gr.Gallery(
                        label="Generated images",
                        show_label=False,
                        elem_id="gallery",
                    ).style(grid=[2])
                    std_output = gr.Textbox(
                        value="Nothing to show.",
                        lines=1,
                        show_label=False,
                    )
                output_dir = args.output_dir if args.output_dir else Path.cwd()
                output_dir = Path(output_dir, "generated_imgs")
                output_loc = gr.Textbox(
                    label="Saving Images at",
                    value=output_dir,
                    interactive=False,
                )
                with gr.Row():
                    txt2img_sendto_img2img = gr.Button(value="SendTo Img2Img")
                    txt2img_sendto_inpaint = gr.Button(value="SendTo Inpaint")
                    txt2img_sendto_outpaint = gr.Button(
                        value="SendTo Outpaint"
                    )

        kwargs = dict(
            fn=txt2img_inf,
            inputs=[
                prompt,
                negative_prompt,
                height,
                width,
                steps,
                guidance_scale,
                seed,
                batch_count,
                batch_size,
                scheduler,
                custom_model,
                hf_model_id,
                precision,
                device,
                max_length,
                save_metadata_to_json,
                save_metadata_to_png,
            ],
            outputs=[txt2img_gallery, std_output],
            show_progress=args.progress_bar,
        )

        prompt.submit(**kwargs)
        negative_prompt.submit(**kwargs)
        stable_diffusion.click(**kwargs)

        from apps.stable_diffusion.web.utils.png_metadata import (
            import_png_metadata,
        )

        png_info_img.change(
            fn=import_png_metadata,
            inputs=[
                png_info_img,
            ],
            outputs=[
                png_info_img,
                prompt,
                negative_prompt,
                steps,
                scheduler,
                guidance_scale,
                seed,
                width,
                height,
                custom_model,
                hf_model_id,
            ],
        )
