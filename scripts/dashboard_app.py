from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CONFIG_PATH = REPO_ROOT / "config" / "dashboard.yaml"
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"


@st.cache_data(ttl=30)
def load_config() -> dict:
    payload = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return payload["dashboard"]


@st.cache_data(ttl=30)
def load_logs() -> pd.DataFrame:
    if not LOG_PATH.exists():
        return pd.DataFrame()
    records: list[dict] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    return df


def filter_window(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    if df.empty:
        return df
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    return df[df["ts"] >= cutoff]


def threshold_badge(value: float, threshold: dict) -> str:
    op = threshold["operator"]
    limit = threshold["value"]
    ok = value <= limit if op == "lte" else value >= limit
    icon = "PASS" if ok else "BREACH"
    cmp_txt = f"<= {limit}" if op == "lte" else f">= {limit}"
    return f"[{icon}] threshold {cmp_txt}"


def main() -> None:
    config = load_config()
    st.set_page_config(page_title=config["title"], layout="wide")
    st.markdown(
        f'<meta http-equiv="refresh" content="{config["refresh_seconds"]}">',
        unsafe_allow_html=True,
    )

    df = filter_window(load_logs(), config["time_range_minutes"])
    panels = {p["id"]: p for p in config["panels"]}

    st.title(config["title"])
    st.caption(
        f"Time range: {config['time_range_minutes']} phut | "
        f"Refresh: {config['refresh_seconds']}s | "
        f"Records trong cua so: {len(df)}"
    )

    if df.empty:
        st.warning(
            "Chua co log trong data/logs.jsonl (hoac ngoai time range). "
            "Chay API + scripts/load_test.py truoc."
        )
        st.stop()

    responses = df[df["event"] == "response_sent"] if "event" in df else pd.DataFrame()
    requests_df = df[df["event"] == "request_received"] if "event" in df else pd.DataFrame()
    failed_df = df[df["event"] == "request_failed"] if "event" in df else pd.DataFrame()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader(panels["latency"]["title"])
        latency = responses.dropna(subset=["latency_ms"]) if "latency_ms" in responses else pd.DataFrame()
        if not latency.empty:
            p50, p95, p99 = latency["latency_ms"].quantile([0.5, 0.95, 0.99])
            st.metric("P50 (ms)", f"{p50:.0f}")
            st.metric("P95 (ms)", f"{p95:.0f}")
            st.metric("P99 (ms)", f"{p99:.0f}")
            st.caption(threshold_badge(p95, panels["latency"]["threshold"]))
            series = latency.set_index("ts")["latency_ms"].resample("1min").quantile(0.95)
            st.line_chart(series)
        else:
            st.info("Chua co response_sent")

    with col2:
        st.subheader(panels["traffic"]["title"])
        st.metric("Total requests", len(requests_df))
        if not requests_df.empty:
            rate = requests_df.set_index("ts").resample("1min").size()
            latest_rate = int(rate.iloc[-1]) if not rate.empty else 0
            st.metric("Requests/phut (gan nhat)", latest_rate)
            st.caption(threshold_badge(latest_rate, panels["traffic"]["threshold"]))
            st.bar_chart(rate)
        else:
            st.info("Chua co request_received")

    with col3:
        st.subheader(panels["errors"]["title"])
        total_req = len(requests_df)
        error_rate = (len(failed_df) / total_req * 100) if total_req else 0.0
        st.metric("Error rate (%)", f"{error_rate:.2f}")
        st.caption(threshold_badge(error_rate, panels["errors"]["threshold"]))
        if not failed_df.empty and "error_type" in failed_df:
            st.bar_chart(failed_df["error_type"].value_counts())
        else:
            st.info("Khong co loi trong cua so hien tai")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.subheader(panels["cost"]["title"])
        if not responses.empty and "cost_usd" in responses:
            total_cost = responses["cost_usd"].sum()
            st.metric("Total cost (USD)", f"{total_cost:.4f}")
            st.caption(threshold_badge(total_cost, panels["cost"]["threshold"]))
            cost_series = responses.set_index("ts")["cost_usd"].resample("1min").sum()
            st.bar_chart(cost_series)
        else:
            st.info("Chua co cost_usd")

    with col5:
        st.subheader(panels["tokens"]["title"])
        if not responses.empty and "tokens_in" in responses and "tokens_out" in responses:
            tokens_in = responses["tokens_in"].sum()
            tokens_out = responses["tokens_out"].sum()
            st.metric("Tokens in", int(tokens_in))
            st.metric("Tokens out", int(tokens_out))
            st.caption(threshold_badge(tokens_in + tokens_out, panels["tokens"]["threshold"]))
        else:
            st.info("Chua co tokens_in/tokens_out")

    with col6:
        st.subheader(panels["quality"]["title"])
        if not responses.empty and "quality_score" in responses:
            mean_q = responses["quality_score"].mean()
            st.metric("Mean quality score", f"{mean_q:.2f}")
            st.caption(threshold_badge(mean_q, panels["quality"]["threshold"]))
            st.line_chart(responses.set_index("ts")["quality_score"])
        else:
            st.info("Chua co quality_score")


main()
