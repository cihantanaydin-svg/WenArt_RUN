"""29 Oct 2026 (user: "GPU usage enough to justify? ... make the pod use the GPU fully"; lesson UL110): independent
AI calls go to the server at once (``model.map_calls``), the agent server takes 8 sequences, and the pod time report
shows the GPU's use from the job's log (CPU)."""
import time

from wenart.agent import model as MM
from wenart.report import podtime as PT

from test_podtime_20261029 import _run


class _Fake:
    parallel = 4


def test_calls_run_at_once_in_order_and_keep_their_errors():
    def slow(j):
        time.sleep(0.2)
        if j == 2:
            raise ValueError("no answer")
        return j * 10

    t = time.time()
    got = MM.map_calls(_Fake(), slow, [0, 1, 2, 3])
    assert time.time() - t < 0.6                                   # four at once, not 0.8 s one after the other
    assert [r for r, _e in got] == [0, 10, None, 30] and isinstance(got[2][1], ValueError)
    assert MM.parallel_of(MM.MockModel()) == 1 and MM.parallel_of(object()) == 1     # scripted: in order
    assert MM.AgentModel("http://x/v1", "m", parallel=8).parallel == 8


def test_the_report_shows_the_gpu_use(tmp_path):
    res = _run(tmp_path)
    (res / "logs").mkdir()
    rows = [f"2026/10/28 16:{m:02d}:00.000, {90 if m < 10 else 0}, 50000, 97887" for m in range(0, 46, 1)]
    (res / "logs" / "gpu_use_20261028-154514-full.csv").write_text("\n".join(rows) + "\n")
    bd = PT.breakdown(str(res), "p", minutes=70)
    assert bd["gpu"]["buckets"]["Blender: build the scene"] == 90.0          # 16:00-16:10
    assert bd["gpu"]["buckets"][PT.AGENT] == 0.0                              # 16:10-16:40
    assert "GPU use" in PT.markdown(bd, "p") and bd["gpu"]["samples"] == 46
