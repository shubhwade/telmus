import os

path = r"c:\Users\Shubh\OneDrive\Documents\Desktop\telmus\telmus\exporters\excel.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

new_charts = """
                        if len(chart4.series) > 0:
                            chart4.series[0].graphicalProperties.line.solidFill = "3B82F6" # Blue
                        
                        # Chart 5: Revenue History
                        chart5 = BarChart()
                        chart5.type = "col"
                        chart5.title = "Revenue History"
                        chart5.y_axis.title = "Revenue"
                        chart5.x_axis.title = "Year"
                        chart5.legend = None

                        rev_data = []
                        for col in revenue.index:
                            try:
                                r_val = float(revenue.loc[col])
                                y_str = str(col.year) if hasattr(col, "year") else str(col)[:4]
                                rev_data.append((y_str, r_val))
                            except Exception:
                                pass
                        rev_data.sort(key=lambda x: x[0])
                        
                        if rev_data:
                            ws_dash.cell(row=3, column=14, value="Year")
                            ws_dash.cell(row=3, column=15, value="Revenue")
                            self._style_range(
                                ws_dash, "N3:O3", font=self.font_data_bold, fill=self.fill_alt,
                                border=self.border_all, alignment=Alignment(horizontal="center")
                            )
                            r_idx = 4
                            for yr, rval in rev_data:
                                ws_dash.cell(row=r_idx, column=14, value=yr)
                                ws_dash.cell(row=r_idx, column=15, value=rval)
                                r_idx += 1
                            self._style_range(
                                ws_dash, f"N4:O{r_idx-1}", font=self.font_data, fill=self.fill_white,
                                border=self.border_all, alignment=Alignment(horizontal="center")
                            )
                            cats5 = Reference(ws_dash, min_col=14, min_row=4, max_row=r_idx-1)
                            data5 = Reference(ws_dash, min_col=15, min_row=3, max_row=r_idx-1)
                            chart5.add_data(data5, titles_from_data=True)
                            chart5.set_categories(cats5)
                            if len(chart5.series) > 0:
                                chart5.series[0].graphicalProperties.solidFill = "10B981"
                        
                        # Chart 6: P/E History
                        # Fetch price history to calculate P/E
                        chart6 = LineChart()
                        chart6.title = "P/E History"
                        chart6.y_axis.title = "P/E Ratio"
                        chart6.x_axis.title = "Year"
                        chart6.legend = None

                        pe_data = []
                        try:
                            import yfinance as yf
                            hist = yf.Ticker(result.ticker).history(period="5y")
                            eps_series = _get_series_fallback(income_stmt, ["Basic EPS", "Diluted EPS"])
                            if eps_series is not None and not hist.empty:
                                hist['Year'] = hist.index.year
                                last_prices = hist.groupby('Year')['Close'].last()
                                for col in eps_series.index:
                                    y_str = int(col.year) if hasattr(col, "year") else int(str(col)[:4])
                                    eps_val = float(eps_series.loc[col])
                                    if eps_val > 0 and y_str in last_prices:
                                        pe_val = last_prices[y_str] / eps_val
                                        pe_data.append((str(y_str), pe_val))
                        except Exception:
                            pass
                        
                        pe_data.sort(key=lambda x: x[0])
                        if pe_data:
                            ws_dash.cell(row=3, column=17, value="Year")
                            ws_dash.cell(row=3, column=18, value="P/E")
                            self._style_range(
                                ws_dash, "Q3:R3", font=self.font_data_bold, fill=self.fill_alt,
                                border=self.border_all, alignment=Alignment(horizontal="center")
                            )
                            p_idx = 4
                            for yr, pval in pe_data:
                                ws_dash.cell(row=p_idx, column=17, value=yr)
                                ws_dash.cell(row=p_idx, column=18, value=pval)
                                p_idx += 1
                            self._style_range(
                                ws_dash, f"Q4:R{p_idx-1}", font=self.font_data, fill=self.fill_white,
                                border=self.border_all, alignment=Alignment(horizontal="center")
                            )
                            cats6 = Reference(ws_dash, min_col=17, min_row=4, max_row=p_idx-1)
                            data6 = Reference(ws_dash, min_col=18, min_row=3, max_row=p_idx-1)
                            chart6.add_data(data6, titles_from_data=True)
                            chart6.set_categories(cats6)
                            if len(chart6.series) > 0:
                                chart6.series[0].graphicalProperties.line.solidFill = "F59E0B"
"""

target = """                        if len(chart4.series) > 0:
                            chart4.series[0].graphicalProperties.line.solidFill = "3B82F6" # Blue"""

code = code.replace(target, new_charts)

# Add charts to Dashboard
add_charts = """        # Add charts to Dashboard in a 2x2 grid layout
        ws_dash.add_chart(chart1, "B6")
        ws_dash.add_chart(chart2, "J6")
        ws_dash.add_chart(chart3, "B22")
        if chart4 is not None:
            ws_dash.add_chart(chart4, "J22")
        if chart5 is not None:
            ws_dash.add_chart(chart5, "B38")
        if chart6 is not None:
            ws_dash.add_chart(chart6, "J38")"""

target_add = """        # Add charts to Dashboard in a 2x2 grid layout
        ws_dash.add_chart(chart1, "B6")
        ws_dash.add_chart(chart2, "J6")
        ws_dash.add_chart(chart3, "B22")
        if chart4 is not None:
            ws_dash.add_chart(chart4, "J22")"""

code = code.replace(target_add, add_charts)

chart_vars = """        chart4 = None
        chart5 = None
        chart6 = None"""

target_vars = """        chart4 = None"""
code = code.replace(target_vars, chart_vars, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated excel.py with chart 5 and 6")
