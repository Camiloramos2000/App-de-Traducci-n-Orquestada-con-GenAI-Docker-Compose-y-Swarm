import os
import gradio as gr
from Translate import Translater

css = """"""
model = Translater()

with gr.Blocks(theme=None, css=css) as demo:
    with gr.Column(elem_id="interface"):
        with gr.Group(elem_id="chatInterface"):
            gr.Markdown("Translate")
            salida = gr.Textbox(placeholder="Resultado", show_label=False, elem_id="chat", label="Result")
            duration = gr.HTML("", elem_id="duration")
            with gr.Row(elem_id="chatInput"):
                texto = gr.Textbox(placeholder="Escribe algo...", elem_id="textbox", autoscroll=False, show_label=True, label="Texto")
                idiomaOutput = gr.Dropdown([
                    "Español","English","Français","Deutsch","Italiano","Português","日本語"
                ], label="Idioma de salida", visible=True, elem_id="options")

    texto.submit(
        fn=model.translate,
        inputs=[texto, idiomaOutput],
        outputs=[salida, duration]
    )

port = int(os.getenv("GRADIO_SERVER_PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
