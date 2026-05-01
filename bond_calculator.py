import streamlit as st
import numpy as np
import pandas as pd

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Bond Price Calculator",
    layout="wide"
)

# -------------------------
# HEADER
# -------------------------
st.title("Bond Price Calculator")

st.markdown("""
### Understand Bond Pricing in Seconds

Adjust the inputs below to see how bond prices react to interest rate changes.

**Core idea:**
- 📉 If market rates rise above the coupon → bond trades at a **discount**
- 📈 If market rates fall below the coupon → bond trades at a **premium**
""")

st.divider()

# -------------------------
# PRESETS
# -------------------------
st.subheader("⚙️ Scenario Presets")

preset = st.radio(
    "Choose a scenario:",
    [
        "Custom",
        "SVB HTM Portfolio (1.63% / 4.5% / 10yr)",
        "SVB AFS Portfolio (1.79% / 4.5% / 3.6yr)"
    ],
    horizontal=True
)

def load_defaults(preset):
    if preset == "SVB HTM Portfolio (1.63% / 4.5% / 10yr)":
        return 1000, 1.63, 10, 4.5
    elif preset == "SVB AFS Portfolio (1.79% / 4.5% / 3.6yr)":
        return 1000, 1.79, 4, 4.5
    else:
        return 1000, 5.0, 10, 5.0

face_default, coupon_default, years_default, market_default = load_defaults(preset)

st.divider()

# -------------------------
# INPUTS
# -------------------------
st.subheader("Inputs")

col1, col2 = st.columns(2)

with col1:
    face_value = st.slider(
        "Face Value ($)",
        100, 100000, face_default, step=100,
        help="Amount repaid at maturity"
    )

    coupon_rate = st.slider(
        "Coupon Rate (%)",
        0.0, 15.0, coupon_default, step=0.01,
        help="Annual interest paid"
    )

with col2:
    years_to_maturity = st.slider(
        "Years to Maturity",
        1, 30, years_default,
        help="Time until bond expires"
    )

    market_rate = st.slider(
        "Market Interest Rate (%)",
        0.0, 20.0, market_default, step=0.25,
        help="Current interest rate environment"
    )

# -------------------------
# CALCULATION
# -------------------------
def calculate_bond_price(face, coupon, years, market):
    c = coupon / 100
    r = market / 100
    payment = face * c

    if r == 0:
        pv_coupons = payment * years
    else:
        pv_coupons = payment * (1 - (1 + r) ** -years) / r

    pv_face = face / (1 + r) ** years
    return pv_coupons + pv_face

bond_price = calculate_bond_price(face_value, coupon_rate, years_to_maturity, market_rate)

annual_coupon = face_value * (coupon_rate / 100)
premium_discount = bond_price - face_value
pct_change = (premium_discount / face_value) * 100

# -------------------------
# RESULTS
# -------------------------
st.divider()
st.subheader("Results")

r1, r2, r3, r4 = st.columns(4)

r1.metric(
    "💰 Bond Price",
    f"${bond_price:,.2f}",
    f"{premium_discount:+,.2f}"
)

r2.metric(
    "📬 Annual Coupon",
    f"${annual_coupon:,.2f}"
)

r3.metric(
    "Total Payout",
    f"${(annual_coupon * years_to_maturity + face_value):,.2f}"
)

r4.metric(
    "📉 % vs Face Value",
    f"{pct_change:+.2f}%"
)

# -------------------------
# STATUS MESSAGE
# -------------------------
st.divider()

if bond_price > face_value:
    st.success(
        f"**Premium Bond** — Coupon ({coupon_rate}%) > Market ({market_rate}%)"
    )
elif bond_price < face_value:
    st.error(
        f"**Discount Bond** — Market ({market_rate}%) > Coupon ({coupon_rate}%)\n\n"
        "This dynamic is exactly what impacted SVB."
    )
else:
    st.info("⚖️ **Par Bond** — Coupon equals market rate")

# -------------------------
# SVB ANALYSIS
# -------------------------
if "SVB" in preset:
    st.divider()
    st.subheader("SVB Scenario Breakdown")

    loss_per_bond = face_value - bond_price
    pct_loss = (loss_per_bond / face_value) * 100

    if "HTM" in preset:
        portfolio_size = 91_300_000_000
        reported_fair_value = 76_200_000_000
        label = "HTM"
    else:
        portfolio_size = 28_600_000_000
        reported_fair_value = 26_069_000_000
        label = "AFS"

    reported_loss = portfolio_size - reported_fair_value

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Loss per Bond",
        f"${loss_per_bond:,.2f}",
        f"-{pct_loss:.1f}%"
    )

    c2.metric(
        f"{label} Portfolio",
        f"${portfolio_size/1e9:.1f}B"
    )

    c3.metric(
        "Unrealized Loss",
        f"${reported_loss/1e9:.1f}B",
        f"-{(reported_loss/portfolio_size)*100:.1f}%"
    )

    st.info(f"""
Each $1,000 bond is now worth **${bond_price:,.2f}**, a loss of **${loss_per_bond:,.2f} ({pct_loss:.1f}%)**.

Scaled across a **${portfolio_size/1e9:.1f}B** portfolio, that becomes roughly **${reported_loss/1e9:.1f}B** in unrealized losses.

These losses were largely hidden on the balance sheet until liquidity pressure forced recognition.
""")

# -------------------------
# CHART
# -------------------------
st.divider()
st.subheader("📉 Price Sensitivity to Interest Rates")

rates = np.arange(0.5, 20.25, 0.25)
prices = [
    calculate_bond_price(face_value, coupon_rate, years_to_maturity, r)
    for r in rates
]

df = pd.DataFrame({
    "Market Rate (%)": rates,
    "Bond Price ($)": prices
}).set_index("Market Rate (%)")

st.line_chart(df)

# -------------------------
# TABLE
# -------------------------
st.divider()
st.subheader("SVB Portfolio Reference")

st.dataframe(pd.DataFrame({
    "Metric": [
        "Coupon Yield",
        "Avg Maturity",
        "Book Value",
        "Market Value",
        "Unrealized Loss",
        "Savings Rate (2023)",
        "Loss per Dollar"
    ],
    "AFS": ["1.79%", "~3.6y", "$28.6B", "$26.1B", "$2.5B", "4.5%", "~2.71%"],
    "HTM": ["1.63%", "10+y", "$91.3B", "$76.2B", "$15.1B", "4.5%", "~2.87%"]
}))
