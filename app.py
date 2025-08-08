# app.py
from flask import Flask, render_template, jsonify
import speedtest
import threading
import time

app = Flask(__name__)

# Global variable to store the latest test results
latest_results = {
    "status": "idle",
    "download": 0,
    "upload": 0,
    "ping": 0,
    "progress": 0,
    "error": None
}

def run_speed_test():
    """Run the internet speed test and update global results"""
    global latest_results
    
    try:
        st = speedtest.Speedtest()
        latest_results["status"] = "finding_server"
        latest_results["progress"] = 20
        st.get_best_server()
        
        latest_results["status"] = "testing_download"
        latest_results["progress"] = 40
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        
        latest_results["status"] = "testing_upload"
        latest_results["progress"] = 60
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        
        latest_results["status"] = "processing"
        latest_results["progress"] = 80
        ping = st.results.ping
        
        latest_results.update({
            "download": round(download_speed, 2),
            "upload": round(upload_speed, 2),
            "ping": round(ping, 2),
            "status": "complete",
            "progress": 100,
            "error": None
        })
        
    except Exception as e:
        latest_results.update({
            "status": "error",
            "error": str(e),
            "progress": 0
        })

@app.route("/")
def index():
    """Render the main page"""
    return render_template("index.html")

@app.route("/start-test", methods=["POST"])
def start_test():
    """Start a new speed test in a background thread"""
    global latest_results
    
    # Reset results
    latest_results = {
        "status": "starting",
        "download": 0,
        "upload": 0,
        "ping": 0,
        "progress": 0,
        "error": None
    }
    
    # Start the test in a separate thread
    threading.Thread(target=run_speed_test).start()
    return jsonify(success=True)

@app.route("/results")
def get_results():
    """Return the current test results"""
    return jsonify(latest_results)

if __name__ == "__main__":
    app.run(debug=True)