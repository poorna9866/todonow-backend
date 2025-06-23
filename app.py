from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# PostgreSQL connection (RDS credentials through environment variables)
DB_HOST = os.environ.get("DB_HOST", "your-rds-endpoint")
DB_NAME = os.environ.get("DB_NAME", "postgres")
DB_USER = os.environ.get("DB_USER", "pguser")
DB_PASS = os.environ.get("DB_PASS", "admin1234")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.route("/todos", methods=["GET"])
def get_todos():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, task FROM todos ORDER BY id;")
        rows = cur.fetchall()
        todos = [{"id": r[0], "task": r[1]} for r in rows]
        cur.close()
        conn.close()
        return jsonify(todos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/todos", methods=["POST"])
def add_todo():
    try:
        task = request.json.get("task")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO todos (task) VALUES (%s)", (task,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Task added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    # Required for ALB routing and ECS communication
    app.run(host="0.0.0.0", port=5000)
