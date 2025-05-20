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

    # Break the new copy into lines, ignoring blank ones
    new_lines = [line.strip() for line in new_text.split("\n") if line.strip()]
    
    # Find all <p> tags with text content (ignoring empty lines)
    p_tags = [p for p in soup.find_all("p") if p.get_text(strip=True)]

    for i, (p, new_line) in enumerate(zip(p_tags, new_lines)):
        # Clear current tag contents and insert the new line as text, keeping the formatting span
        for tag in p.find_all(text=True):
            tag.replace_with("")  # Clear existing text

        # Find the deepest span or element and update it
        deepest = p
        while len(deepest.contents) == 1 and hasattr(deepest.contents[0], 'contents'):
            deepest = deepest.contents[0]

        # Replace only the text, not structure
        if deepest.string is not None:
            deepest.string.replace_with(new_line)
        else:
            deepest.append(new_line)

    return str(soup)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
