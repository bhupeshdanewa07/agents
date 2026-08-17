import re
import gradio as gr
import os
from dotenv import load_dotenv
from research_manager import ResearchManager
from styles import CSS, JS, EXAMPLES, HEADER_HTML

load_dotenv(override=True)

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def is_valid_email(email: str) -> bool:
    if not email:
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))


async def run(query: str, recipient_email: str = ""):
    query = (query or "").strip()
    recipient_email = (recipient_email or "").strip()

    if not recipient_email:
        gr.Warning("Enter your email first!")
        yield "⚠️ **Enter your email first!**"
        return

    if not query:
        yield "⚠️ **Please enter a research question to investigate.**"
        return

    if not is_valid_email(recipient_email):
        gr.Warning("Invalid email format!")
        yield f"❌ **Invalid email format (`{recipient_email}`).** Please enter a valid email address (e.g. `user@example.com`)."
        return

    async for status_update in ResearchManager().run(query, recipient_email=recipient_email):
        yield status_update


with gr.Blocks(title="Deep Research AI | Bhupesh Danewa") as ui:
    gr.HTML(HEADER_HTML)

    with gr.Row(elem_classes="dr-email-row"):
        email_textbox = gr.Textbox(
            placeholder="Enter recipient email address to receive report (required, e.g. user@example.com)...",
            label="Recipient Email Address",
            show_label=True,
            container=True,
            elem_id="dr-email",
        )

    with gr.Row(elem_classes="dr-query-row"):
        query_textbox = gr.Textbox(
            placeholder="Type a research question...",
            show_label=False,
            container=False,
            autofocus=True,
            elem_id="dr-query",
            scale=5,
        )
        run_button = gr.Button("Investigate", variant="primary", elem_id="dr-run", scale=1)

    gr.HTML('<div class="dr-examples-label">Try one</div>')
    gr.Examples(examples=EXAMPLES, inputs=query_textbox, elem_id="dr-examples")

    report = gr.Markdown(elem_id="dr-report")

    run_button.click(run, inputs=[query_textbox, email_textbox], outputs=report)
    query_textbox.submit(run, inputs=[query_textbox, email_textbox], outputs=report)
    email_textbox.submit(run, inputs=[query_textbox, email_textbox], outputs=report)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    # Use 0.0.0.0 on Render (when PORT env var is present) and 127.0.0.1 locally for Windows browser compatibility
    server_name = "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"
    print(f"Launching app on http://{server_name}:{port}")
    ui.launch(server_name=server_name, server_port=port, css=CSS, js=JS, theme=gr.themes.Base())
