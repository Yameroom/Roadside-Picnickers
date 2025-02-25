from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

uri = "mongodb+srv://banentremen:Pkm4TgtZ1UQwU1Fd@cluster0.wkjwq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client.SensorDatabase
collection = db.SensorData

@app.route("/sensor", methods=["POST"])
def receive_sensor_data():
    try:
        data = request.get_json()
        if data and all(key in data for key in ("temperature", "humidity", "motion")):
            temperature = data["temperature"]
            humidity = data["humidity"]
            motion = data["motion"]
            timestamp = datetime.now()
            sensor_data = {"temperature": temperature, "humidity": humidity, "motion": motion, "timestamp": timestamp}
            collection.insert_one(sensor_data)
            return jsonify({"message": "Data received and saved"}), 200
        else:
            return jsonify({"error": "Invalid data"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
