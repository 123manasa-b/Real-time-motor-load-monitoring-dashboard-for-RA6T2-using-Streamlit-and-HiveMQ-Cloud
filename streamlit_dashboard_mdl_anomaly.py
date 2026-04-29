import streamlit as st
import paho.mqtt.client as mqtt
import ssl
import time

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Motor Load Condition", layout="centered")

# ----------------- HIVEMQ CLOUD DETAILS -----------------
MQTT_BROKER = "42a266e38db843c5b8363c2895d9726e.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "motorload"
MQTT_PASSWORD = "Motor@123"

LOAD_TOPIC = "motor/load/status"

# ----------------- MQTT STORAGE -----------------
@st.cache_resource
def get_mqtt_store():
    return {"load_value": 0}

mqtt_store = get_mqtt_store()

# ----------------- MQTT CALLBACKS -----------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(LOAD_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip()

    try:
        value = int(payload)

        if value in [0, 1, 2]:
            mqtt_store["load_value"] = value

    except:
        pass

# ----------------- START MQTT -----------------
@st.cache_resource
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.tls_set(
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS
    )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    return client

client = start_mqtt()

# ----------------- CURRENT VALUE -----------------
load_value = mqtt_store["load_value"]

# ----------------- CSS -----------------
st.markdown("""
<style>
.stApp { background-color: #eef6ff; }

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 35px;
    color: #1e293b;
}

.circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    margin: 0 auto;
    border: 5px solid #bfd0e2;
    background-color: #dfe7f1;
}

.green { background-color: #22c55e !important; }
.yellow { background-color: #facc15 !important; }
.red { background-color: #ef4444 !important; }

.circle-text {
    margin-top: 14px;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
}

.result-box {
    margin-top: 40px;
    text-align: center;
    padding: 24px;
    font-size: 32px;
    font-weight: bold;
    color: white;
    border-radius: 14px;
}

.sub-box {
    margin-top: 20px;
    text-align: center;
    padding: 20px;
    font-size: 24px;
    font-weight: bold;
    color: white;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

# ----------------- TITLE -----------------
st.markdown('<div class="main-title">Motor Load Condition</div>', unsafe_allow_html=True)

# ----------------- LOAD LOGIC -----------------
no_load_class = ""
normal_load_class = ""
heavy_load_class = ""

result_color = "#475569"
result_text = "UNKNOWN"

if load_value == 0:
    no_load_class = "green"
    result_color = "#16a34a"
    result_text = "NO LOAD"

elif load_value == 1:
    normal_load_class = "yellow"
    result_color = "#ca8a04"
    result_text = "NORMAL LOAD"

elif load_value == 2:
    heavy_load_class = "red"
    result_color = "#dc2626"
    result_text = "HEAVY LOAD"

# ----------------- ANOMALY LOGIC -----------------
if load_value == 2:
    anomaly_color = "#dc2626"
    anomaly_text = "ANOMALY DETECTED"
else:
    anomaly_color = "#16a34a"
    anomaly_text = "NORMAL"

# ----------------- CIRCLES -----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="text-align:center">
        <div class="circle {no_load_class}"></div>
        <div class="circle-text">No Load</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align:center">
        <div class="circle {normal_load_class}"></div>
        <div class="circle-text">Normal Load</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="text-align:center">
        <div class="circle {heavy_load_class}"></div>
        <div class="circle-text">Heavy Load</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- RESULT -----------------
st.markdown(f"""
<div class="result-box" style="background-color:{result_color};">
    {result_text}
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="sub-box" style="background-color:{anomaly_color};">
    {anomaly_text}
</div>
""", unsafe_allow_html=True)

# ----------------- AUTO REFRESH -----------------
time.sleep(1)
st.experimental_rerun()