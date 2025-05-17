import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

CONFIG_PATH = Path("config/triggers.json")

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    CORS(app)

    @app.route("/")
    def index():
        return render_template("editor.html")

    @app.route("/api/triggers", methods=["GET", "POST"])
    def triggers():
        if request.method == "POST":
            data = request.get_json() or {}
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(data, indent=2))
            return jsonify(status="ok", triggers=data)
        else:
            if not CONFIG_PATH.exists():
                return jsonify(triggers={})
            return jsonify(triggers=json.loads(CONFIG_PATH.read_text()))

    return app
