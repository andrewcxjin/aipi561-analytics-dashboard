from flask import Flask, render_template, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Process data from csv file
def data_wrangler():
    df = pd.read_csv("data/co2_emissions.csv")

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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CO2 Emissions in Europe Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }
        h1 {
            text-align: center;
        }
        canvas {
            max-width: 900px;
            margin: auto;
        }
    </style>
</head>
<body>
    <h1>CO2 Emissions by European State</h1>
    <canvas id="co2Chart"></canvas>

    <script>
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                const states = data.map(row => row.STATE_NAME);
                const emissions = data.map(row => row.CO2_QTY_TONNES);

                const ctx = document.getElementById('co2Chart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: states,
                        datasets: [{
                            label: 'Total CO2 Emissions (Tonnes)',
                            data: emissions,
                            backgroundColor: 'rgba(75, 192, 192, 0.7)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'CO2 Tonnes'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'State'
                                }
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
    return render_template(HTML_TEMPLATE)

@app.route('/api/data')
def data():
    log()
    return jsonify(data_wrangler())

if __name__ == '__main__':
    app.run(debug=True)