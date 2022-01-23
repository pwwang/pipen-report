from pipen import Pipen, Proc


class LargeReport(Proc):
    """Process with large report"""

    input = "a"
    output = "a:var:{{in.a}}"
    script = "echo {{in.a}}"
    plugin_opts = {
        "report_paging": 25,
        "report": """
        {% for i in range(200) %}
        <h1>h{{i}}</h1>
        <div>
            <div>
                <table>
                    <thead><tr><th>Head{{i}}</th></tr></thead>
                    <tbody><tr><td>Cell{{i}}</td></tr></tbody>
                </table>
            </div>
        </div>
        {% endfor %}
        """,
    }


if __name__ == "__main__":
    Pipen(
        "LargeReportPipe", plugin_opts={"report_logging": "debug", "report_forks": 4}
    ).set_start(LargeReport).run()
