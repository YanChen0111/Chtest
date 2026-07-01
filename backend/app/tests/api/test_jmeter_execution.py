from __future__ import annotations

from pathlib import Path

import pytest

from backend.app.modules.execution.jmeter_runner import JMeterRunnerCommandError, parse_jmeter_jtl


JTL_CSV = """timeStamp,elapsed,label,responseCode,responseMessage,threadName,success,bytes,grpThreads,allThreads,Latency,IdleTime,Connect
1719820800000,120,GET /coupons,200,OK,Thread Group 1-1,true,512,1,1,80,0,12
1719820800200,240,POST /coupons,500,Internal Server Error,Thread Group 1-1,false,256,1,1,180,0,24
1719820800600,90,GET /health,200,OK,Thread Group 1-1,true,128,1,1,50,0,6
"""


JTL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testResults version="1.2">
  <httpSample t="120" lt="80" ts="1719820800000" s="true" lb="GET /coupons" rc="200" rm="OK" by="512" />
  <httpSample t="240" lt="180" ts="1719820800200" s="false" lb="POST /coupons" rc="500" rm="Internal Server Error" by="256" />
</testResults>
"""


def test_parse_jmeter_jtl_csv_summarizes_sampler_counts(tmp_path: Path) -> None:
    jtl_path = tmp_path / "results.jtl"
    jtl_path.write_text(JTL_CSV, encoding="utf-8")

    parsed, results = parse_jmeter_jtl(jtl_path)

    assert parsed == {
        "total": 3,
        "passed": 2,
        "failed": 1,
        "skipped": 0,
        "error": 0,
        "sampler_count": 3,
        "assertion_count": 3,
        "duration_ms": 450,
        "average_latency_ms": 103,
    }
    assert [item.test_name for item in results] == [
        "jmeter/GET /coupons",
        "jmeter/POST /coupons",
        "jmeter/GET /health",
    ]
    assert results[1].status == "failed"
    assert results[1].failure_message == "500 Internal Server Error"
    assert results[1].metadata["response_code"] == "500"
    assert results[1].metadata["latency_ms"] == 180


def test_parse_jmeter_jtl_xml_summarizes_sampler_counts(tmp_path: Path) -> None:
    jtl_path = tmp_path / "results.xml"
    jtl_path.write_text(JTL_XML, encoding="utf-8")

    parsed, results = parse_jmeter_jtl(jtl_path)

    assert parsed["total"] == 2
    assert parsed["passed"] == 1
    assert parsed["failed"] == 1
    assert parsed["duration_ms"] == 360
    assert parsed["average_latency_ms"] == 130
    assert results[0].test_name == "jmeter/GET /coupons"
    assert results[1].failure_message == "500 Internal Server Error"


def test_parse_jmeter_jtl_rejects_missing_or_empty_results(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.jtl"
    empty_path = tmp_path / "empty.jtl"
    empty_path.write_text("", encoding="utf-8")

    with pytest.raises(JMeterRunnerCommandError, match="JMeter JTL file was not produced"):
        parse_jmeter_jtl(missing_path)

    with pytest.raises(JMeterRunnerCommandError, match="JMeter JTL file contains no sampler results"):
        parse_jmeter_jtl(empty_path)
