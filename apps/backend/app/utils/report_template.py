def render_report_html(data):
    asl_parameters = data.get("asl_parameters", {})
    if isinstance(asl_parameters, dict):
        parameter_items = asl_parameters.items()
    else:
        parameter_items = asl_parameters

    missing_parameters = data.get("missing_required_parameters", data.get("missing_parameters", []))
    if isinstance(missing_parameters, dict):
        missing_items = missing_parameters.keys()
    else:
        missing_items = missing_parameters

    params_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in parameter_items)
    missing_html = "".join(f"<li>{param}</li>" for param in missing_items)
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
            th, td {{ padding: 8px; }}
        </style>
    </head>
    <body>
        <h1>ASL Report</h1>
        <h2>Parameters</h2>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            {params_html}
        </table>
        <h2>Basic Report</h2>
        <p>{data.get("basic_report", "No basic report available.")}</p>
        <h2>Extended Report</h2>
        <p>{data.get("extended_report", "No extended report available.")}</p>
        <h2>Missing Parameters</h2>
        <ul>
            {missing_html}
        </ul>
    </body>
    </html>
    """
