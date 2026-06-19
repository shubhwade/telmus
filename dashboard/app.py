from __future__ import annotations

import streamlit as st

from valkit.core.scanner import ValkitScanner


def main() -> None:
    st.title("valkit")
    st.caption("financial statement analysis · real data · no API key")

    ticker = st.text_input("Ticker", placeholder="INFY, TCS, AAPL, MSFT")
    if st.button("Analyse") and ticker:
        try:
            with st.spinner("scanning..."):
                result = ValkitScanner().scan(ticker.strip().upper())

            cols = st.columns(3)
            cols[0].metric("Piotroski F-score", result.health.piotroski_f)
            cols[1].metric("Altman Z-score", f"{result.health.altman_z:.2f}" if result.health.altman_z is not None else "n/a")
            cols[2].metric("P/E Ratio", f"{result.valuation.pe_ratio:.2f}" if result.valuation.pe_ratio is not None else "n/a")

            if result.highest_concern == "low":
                st.success(result.analyst_brief)
            elif result.highest_concern == "medium":
                st.warning(result.analyst_brief)
            else:
                st.error(result.analyst_brief)

            if result.red_flags:
                st.subheader("Red flags")
                st.dataframe([flag.__dict__ for flag in result.red_flags])

            with st.expander("Full JSON report"):
                st.code(result.to_json(), language="json")
        except Exception:
            st.error("Could not fetch data for ticker. Check the symbol and try again.")

    st.caption("Data via yfinance · valkit v0.1.0 · MIT License")


if __name__ == "__main__":
    main()
