import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify

def create_app(config_path: str = "config/triggers.json"):
    app = Flask(__name__, 
                template_folder=Path(__file__).parent / "templates")

    triggers_file = Path(config_path)

    def load_triggers():
        if not triggers_file.exists():
            triggers_file.parent.mkdir(parents=True, exist_ok=True)
            triggers_file.write_text("{}")
        return json.loads(triggers_file.read_text())

    def save_triggers(data):
        triggers_file.write_text(json.dumps(data, indent=2))

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/triggers", methods=["GET"])
    def get_triggers():
        return jsonify(load_triggers())

    @app.route("/api/triggers", methods=["POST"])
    def post_triggers():
        try:
            data = request.get_json()
            save_triggers(data)
            return jsonify({"status": "ok"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    return app
