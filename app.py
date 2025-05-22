from flask import Flask, render_template, request
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    generated_html = ""
    if request.method == "POST":
        template_text = request.form.get("template_text", "")
        new_copy = request.form.get("new_copy", "")

        generated_html = replace_copy_preserving_format(template_text, new_copy)

    return render_template("index.html.txt", generated_html=generated_html)

def replace_copy_preserving_format(template_html, new_text):
    soup = BeautifulSoup(template_html, "html.parser")

    new_lines = [line.strip() for line in new_text.split("\n") if line.strip()]
    new_index = 0

    p_tags = soup.find_all("p")

    last_formatted_tag = None

    for p in p_tags:
        if new_index >= len(new_lines):
            break

        # Skip <p> with no spans and no visible style
        if not p.get_text(strip=True) and not p.find("span"):
            continue

        # Try to find the deepest span in this <p>
        current = p
        while len(current.contents) == 1 and hasattr(current.contents[0], 'contents'):
            current = current.contents[0]

        # If it contains a span or formatting, save it as fallback
        if p.find("span"):
            last_formatted_tag = p.decode_contents()

        # Now replace the text
        if current.string is not None:
            current.string.replace_with(new_lines[new_index])
        else:
            current.append(new_lines[new_index])

        # If the <p> was blank (unstyled), apply previous formatting
        if not p.find("span") and last_formatted_tag:
            styled_fallback = BeautifulSoup(f"<p>{last_formatted_tag}</p>", "html.parser").p
            p.clear()
            for child in styled_fallback.contents:
                # Replace text inside fallback span with new text
                if child.name == "span" and child.string:
                    child.string.replace_with(new_lines[new_index])
                p.append(child)

        new_index += 1

    return str(soup)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
