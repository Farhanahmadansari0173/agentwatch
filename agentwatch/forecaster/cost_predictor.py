import sys
import json
import time
import uuid
sys.path.insert(0, '/Users/farhanahmadansari/Documents/agentwatch')
import splunklib.client as client
import splunklib.results as results
import config

def get_splunk_service():
    return client.connect(
        host=config.SPLUNK_HOST,
        port=config.SPLUNK_PORT,
        username=config.SPLUNK_USERNAME,
        password=config.SPLUNK_PASSWORD
    )

def run_forecast():
    print("Running token usage forecast...")
    spl = """search index=agentwatch_traces earliest=-7d
| timechart span=1h sum(tokens_estimated) as hourly_tokens
| fillnull value=0 hourly_tokens
| predict hourly_tokens future_timespan=24 holdback=0 lower95=lower95 upper95=upper95
| eval anomaly=if(hourly_tokens > 'upper95(prediction(hourly_tokens))', "SPIKE", "normal")
| eval alert_msg=if(anomaly="SPIKE",
    "Token spike: " + tostring(round(hourly_tokens,0)) + " tokens/hr exceeds " + tostring(round('upper95(prediction(hourly_tokens))',0)),
    null())
| where anomaly="SPIKE"
| table _time, hourly_tokens, prediction(hourly_tokens), upper95(prediction(hourly_tokens)), anomaly, alert_msg"""

    try:
        service = get_splunk_service()
        job = service.jobs.create(spl, earliest_time="-7d", latest_time="now")
        while not job.is_done():
            time.sleep(1)
        anomalies = []
        reader = results.JSONResultsReader(job.results(output_mode='json'))
        for result in reader:
            if isinstance(result, dict):
                anomalies.append(result)
                print(f"🔴 SPIKE at {result.get('_time','?')} — {result.get('alert_msg','')}")
        print(f"\n✅ Forecast complete. Found {len(anomalies)} anomalies.")
        return anomalies
    except Exception as e:
        print(f"❌ Forecast failed: {e}")
        return []

def get_forecast_summary():
    spl = """search index=agentwatch_traces earliest=-7d
| timechart span=1h sum(tokens_estimated) as hourly_tokens
| fillnull value=0 hourly_tokens
| predict hourly_tokens future_timespan=24 holdback=0 upper95=upper95
| where isnull(hourly_tokens)
| eval predicted_cost=round('prediction(hourly_tokens)' * 0.001, 4)
| table _time, prediction(hourly_tokens), upper95(prediction(hourly_tokens)), predicted_cost"""

    try:
        service = get_splunk_service()
        job = service.jobs.create(spl, earliest_time="-7d", latest_time="now")
        while not job.is_done():
            time.sleep(1)
        forecasts = []
        reader = results.JSONResultsReader(job.results(output_mode='json'))
        for result in reader:
            if isinstance(result, dict):
                forecasts.append(result)
        print(f"📊 Next 24h forecast: {len(forecasts)} hourly predictions ready")
        return forecasts
    except Exception as e:
        print(f"❌ Forecast summary failed: {e}")
        return []

if __name__ == "__main__":
    print("=" * 60)
    print("AgentWatch Anomaly Forecaster")
    print("=" * 60)
    anomalies = run_forecast()
    print("\n--- Next 24 Hours Forecast ---")
    forecasts = get_forecast_summary()
    if forecasts:
        print(f"First prediction: {forecasts[0].get('_time')} → {round(float(forecasts[0].get('prediction(hourly_tokens)',0)),0)} tokens/hr")
