from pipen import Pipen, Proc

class LargeReport(Proc):
    """Process with large report"""
    input = "a"
    output = "a:var:{{in.a}}"
    script = "echo {{in.a}}"
    plugin_opts = {
        "report": """
        {% for i in range(2000) %}
        <div>
            <div>
                <table>
                    <thead><tr><th></th></tr></thead>
                    <tbody><tr><td></td></tr></tbody>
                </table>
            </div>
        </div>
        {% endfor %}
        """
    }

if __name__ == "__main__":
    Pipen("LargeReportPipe").set_start(LargeReport).run()
