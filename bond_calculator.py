import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Bond Price Calculator", layout="wide")

st.title("🏦 Bond Price Calculator")
st.markdown("""
This app calculates the **fair price of a bond** based on four inputs.
Move any slider and the price updates instantly.

**Key concept:** When market rates rise above a bond's coupon rate, 
the bond becomes less valuable — its price falls below face value (a *discount* bond).
When market rates fall below the coupon rate, the bond trades above face value (a *premium* bond).
""")

st.markdown("---")

st.subheader("⚙️ Scenario Presets")
preset = st.radio(
    "Load a preset scenario or customize manually:",
    ["Custom", "SVB HTM Portfolio (1.63% / 4.5% / 10yr)", "SVB AFS Portfolio (1.79% / 4.5% / 3.6yr)"],
    horizontal=True
)

if preset == "SVB HTM Portfolio (1.63% / 4.5% / 10yr)":
    default_face = 1000
    default_coupon = 1.63
    default_years = 10
    default_market = 4.5
elif preset == "SVB AFS Portfolio (1.79% / 4.5% / 3.6yr)":
    default_face = 1000
    default_coupon = 1.79
    default_years = 4
    default_market = 4.5
else:
    default_face = 1000
    default_coupon = 5.0
    default_years = 10
    default_market = 5.0

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    face_value = st.slider(
        "Face Value ($) — The amount paid back at maturity",
        min_value=100,
        max_value=100000,
        value=default_face,
        step=100
    )

    coupon_rate = st.slider(
        "Coupon Rate (%) — Annual interest the bond pays",
        min_value=0.0,
        max_value=15.0,
        value=default_coupon,
        step=0.01
    )

with col2:
    years_to_maturity = st.slider(
        "Years to Maturity — How long until the bond expires",
        min_value=1,
        max_value=30,
        value=default_years,
        step=1
    )

    market_rate = st.slider(
        "Market Interest Rate (%) — Current rate environment",
        min_value=0.0,
        max_value=20.0,
        value=default_market,
        step=0.25
    )


def calculate_bond_price(face_value, coupon_rate, years_to_maturity, market_rate):
    c = coupon_rate / 100
    r = market_rate / 100
    coupon_payment = face_value * c

    if r == 0:
        pv_coupons = coupon_payment * years_to_maturity
    else:
        pv_coupons = coupon_payment * (1 - (1 + r) ** -years_to_maturity) / r

    pv_face_value = face_value / (1 + r) ** years_to_maturity
    return pv_coupons + pv_face_value


bond_price = calculate_bond_price(face_value, coupon_rate, years_to_maturity, market_rate)
annual_coupon = face_value * (coupon_rate / 100)
premium_discount = bond_price - face_value
pct_change = (premium_discount / face_value) * 100

st.markdown("---")
st.subheader("📊 Results")

res_col1, res_col2, res_col3, res_col4 = st.columns(4)

with res_col1:
    st.metric(
        label="💰 Bond Price",
        value=f"${bond_price:,.2f}",
        delta=f"${premium_discount:+,.2f} vs Face Value"
    )

with res_col2:
    st.metric(
        label="📬 Annual Coupon Payment",
        value=f"${annual_coupon:,.2f}"
    )

with res_col3:
    st.metric(
        label="📈 Total Payout if Held to Maturity",
        value=f"${(annual_coupon * years_to_maturity + face_value):,.2f}"
    )

with res_col4:
    st.metric(
        label="📉 Price Change from Face Value",
        value=f"{pct_change:+.2f}%"
    )

st.markdown("---")
if bond_price > face_value:
    st.success(f"✅ **Premium Bond** — The bond's coupon rate ({coupon_rate}%) exceeds the market rate ({market_rate}%), so investors pay MORE than face value.")
elif bond_price < face_value:
    st.error(f"⚠️ **Discount Bond** — The market rate ({market_rate}%) exceeds the coupon rate ({coupon_rate}%), so the bond trades BELOW face value. This is exactly what happened to SVB.")
else:
    st.info("⚖️ **Par Bond** — Coupon rate equals market rate. Bond trades exactly at face value.")


if preset in ["SVB HTM Portfolio (1.63% / 4.5% / 10yr)", "SVB AFS Portfolio (1.79% / 4.5% / 3.6yr)"]:
    st.markdown("---")
    st.subheader("🏦 SVB Scenario Breakdown")

    loss_per_bond = face_value - bond_price
    pct_loss = (loss_per_bond / face_value) * 100

    if preset == "SVB HTM Portfolio (1.63% / 4.5% / 10yr)":
        portfolio_size = 91_300_000_000
        reported_fair_value = 76_200_000_000
        label = "HTM"
    else:
        portfolio_size = 28_600_000_000
        reported_fair_value = 26_069_000_000
        label = "AFS"

    num_bonds = portfolio_size / face_value
    scaled_loss = num_bonds * loss_per_bond
    reported_loss = portfolio_size - reported_fair_value

    svb_col1, svb_col2, svb_col3 = st.columns(3)

    with svb_col1:
        st.metric(
            label=f"Loss Per $1,000 Bond",
            value=f"${loss_per_bond:,.2f}",
            delta=f"-{pct_loss:.1f}% of face value"
        )

    with svb_col2:
        st.metric(
            label=f"SVB {label} Portfolio Size",
            value=f"${portfolio_size/1e9:.1f}B"
        )

    with svb_col3:
        st.metric(
            label=f"Reported Unrealized Loss",
            value=f"${reported_loss/1e9:.1f}B",
            delta=f"-{(reported_loss/portfolio_size)*100:.1f}% of portfolio"
        )

    st.markdown(f"""
    > **What this means in plain English:**
    > SVB paid face value for these bonds when rates were near zero. 
    > By early 2023, every $1,000 bond was only worth **${bond_price:,.2f}** on the open market — 
    > a loss of **${loss_per_bond:,.2f} per bond ({pct_loss:.1f}%)**.
    > Multiplied across their **${portfolio_size/1e9:.1f} billion** {label} portfolio, 
    > that produced **${reported_loss/1e9:.1f} billion** in unrealized losses.
    > SVB carried these at book value on their balance sheet — hidden from plain sight until it was too late.
    """)

st.markdown("---")
st.subheader("📉 Bond Price vs. Market Interest Rate")
st.markdown("*This chart shows how the bond's price changes as market rates shift — holding all other inputs constant.*")

rate_range = np.arange(0.5, 20.25, 0.25)
prices = [calculate_bond_price(face_value, coupon_rate, years_to_maturity, r) for r in rate_range]

chart_data = pd.DataFrame({
    "Market Rate (%)": rate_range,
    "Bond Price ($)": prices
}).set_index("Market Rate (%)")

st.line_chart(chart_data)

st.markdown("---")
st.subheader("📋 SVB Portfolio Reference")
st.markdown("""
| | AFS Portfolio | HTM Portfolio |
|---|---|---|
| Coupon Yield | 1.79% | 1.63% |
| Avg. Maturity | ~3.6 years | 10+ years |
| Book Value | $28.6B | $91.3B |
| Fair Market Value | $26.1B | $76.2B |
| Unrealized Loss | $2.5B | $15.1B |
| Savings Account Rate (2023) | 4.5% | 4.5% |
| Net Loss Per Dollar | ~2.71% | ~2.87% |
""")
