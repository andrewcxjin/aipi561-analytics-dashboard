from flask import Flask, render_template_string, jsonify
import pandas as pd
from datetime import datetime
import os
import json
import traceback

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "co2_emissions.csv")

# Process data from csv file
def data_wrangler():
    df = pd.read_csv(CSV_PATH, encoding='latin1')

    df.columns = df.columns.str.strip().str.upper()
    df['FLIGHT_MONTH'] = pd.to_datetime(df['FLIGHT_MONTH'], format="%m-%d-%Y")
    df["CO2_PER_FLIGHT"] = df["CO2_QTY_TONNES"] / df["TF"]

    summary = df.groupby("STATE_NAME").agg({
        "CO2_QTY_TONNES": "sum",
        "TF": "sum",
        "CO2_PER_FLIGHT": "mean"
    }).reset_index().sort_values(by="CO2_QTY_TONNES", ascending=False)

    return summary.to_dict(orient="records")

# Monitoring data
def log():
    current = datetime.utcnow().isoformat()
    print(f"[{current}] Data requested from /api/data")

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>CO2 Emissions in Europe from Airplanes</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
        }
        h1 {
            margin-top: 20px;
        }
        .chart-container {
            width: 90%;
            height: 80vh;
            margin: auto;
        }
        canvas {
            width: 100% !important;
            height: 100% !important;
        }
    </style>
</head>
<body>
    <h1>CO2 Emissions by European State</h1>
    <div class="chart-container">
        <canvas id="co2Chart"></canvas>
    </div>
    <script>
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                const labels = data.map(row => row.State);
                const values = data.map(row => row['Total CO2 Emissions (Tonnes)']);

                new Chart(document.getElementById('co2Chart'), {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Total CO2 Emissions (Tonnes)',
                            data: values,
                            backgroundColor: 'rgba(72, 202, 228, 0.7)',
                            borderColor: 'rgba(72, 202, 228, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                ticks: {
                                    maxRotation: 90,
                                    minRotation: 60,
                                    autoSkip: false
                                }
                            },
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'CO2 Tonnes'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: true
                            },
                            title: {
                                display: false
                            }
                        }
                    }
                });
            });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def data():
    log()
    try:
        return jsonify(data_wrangler())
    except Exception as e:
        print("Error in /api/data:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)