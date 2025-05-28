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

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
def data():
    log()
    return jsonify(data_wrangler())

if __name__ == '__main__':
    app.run(debug=True)