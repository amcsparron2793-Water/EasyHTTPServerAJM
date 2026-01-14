from http.server import SimpleHTTPRequestHandler
from html import escape
from pathlib import Path
import os
from string import Template


class PrettyDirectoryHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        """Generate a custom HTML directory listing."""
        # path = path to the directory you want listed
        try:
            entries = sorted(os.listdir(path))
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None

        displaypath = escape(self.path)
        enc = "utf-8"
        title = f"Index of {displaypath}"

        # Build your custom HTML
        html = [
            "<!DOCTYPE html>",
            "<html><head>",
            f"<meta charset='{enc}'>",
            f"<title>{title}</title>",
            "<style>",
            "body { font-family: sans-serif; margin: 2rem; }",
            "table { border-collapse: collapse; }",
            "th, td { padding: 0.25rem 0.5rem; }",
            "tr:nth-child(even) { background: #f4f4f4; }",
            "a { text-decoration: none; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>",
            "<table>",
            "<tr><th>Name</th></tr>",
        ]

        # Parent directory link
        if self.path not in ("/", ""):
            html.append("<tr><td><a href='..'>..</a></td></tr>")

        for name in entries:
            fullname = os.path.join(path, name)
            display = name + ("/" if os.path.isdir(fullname) else "")
            link = escape(display)
            html.append(f"<tr><td><a href='{link}'>{display}</a></td></tr>")

        html.extend(["</table>", "</body></html>"])
        encoded = "\n".join(html).encode(enc, "surrogateescape")

        # Send HTTP headers
        self.send_response(200)
        self.send_header("Content-type", f"text/html; charset={enc}")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()