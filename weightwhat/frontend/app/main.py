import altair as alt
import pandas as pd
import requests
import streamlit as st

st.title("Weightwhat")
st.write("Weight tracking and analysis")


@st.cache
def preprocess_data(raw_data):
    data = raw_data.sort_values(by="created_at", ascending=True).reset_index(drop=True)
    data = data[["weight", "created_at"]]
    data["timestamp"] = pd.to_datetime(data["created_at"])
    data["date"] = data["timestamp"].dt.date
    data["year_month"] = data["timestamp"].dt.strftime("%Y-%m")
    data["month_of_year"] = data["timestamp"].dt.month
    data["week_of_year"] = data["timestamp"].dt.week
    data["day_of_week"] = data["timestamp"].dt.dayofweek
    data["day_name"] = data["timestamp"].dt.day_name()
    data["diff"] = data.groupby("year_month")["weight"].diff().fillna(0)
    return data


@st.cache
def load_data():
    response = requests.get("http://api:8000/api/weights")
    raw_data = pd.DataFrame(response.json())
    data = preprocess_data(raw_data)
    return data


data = load_data()

d = pd.to_datetime(st.date_input("weight since", data.timestamp.min()), utc=True)

c1 = (
    alt.Chart(data[data.timestamp > d])
    .mark_line()
    .encode(
        alt.Y(
            "weight",
            scale=alt.Scale(domain=[data.weight.max() * 0.8, data.weight.max()]),
        ),
        x="date:T",
    )
    .properties(height=400, width=300)
    .interactive()
)

c2 = (
    alt.Chart(
        data[data.timestamp > d].groupby("year_month")["diff"].sum().reset_index()
    )
    .mark_bar()
    .encode(y="year_month", x="diff:Q")
    .properties(height=400, width=200)
    .interactive()
)

c3 = c1 | c2
st.altair_chart(c3, use_container_width=True)
