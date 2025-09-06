from flask import Flask, request, jsonify
from flask_cors import CORS
from bigcalc import eval_expr

app = Flask(__name__)
CORS(app)  # <-- Enable CORS

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    expr = data.get("expression", "")
    try:
        result = eval_expr(expr)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
