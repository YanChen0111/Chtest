from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class JMeterRunnerCommandError(ValueError):
    pass


@dataclass(frozen=True)
class JMeterTestResultCandidate:
    test_name: str
    test_file: str | None
    status: str
    duration_ms: int | None
    failure_message: str | None
    metadata: dict[str, Any]


@dataclass(frozen=True)
class JMeterSample:
    label: str
    success: bool
    elapsed_ms: int
    latency_ms: int | None
    response_code: str
    response_message: str
    bytes_received: int | None
    timestamp_ms: int | None


def parse_jmeter_jtl(jtl_path: str | Path) -> tuple[dict[str, Any], list[JMeterTestResultCandidate]]:
    path = Path(jtl_path)
    if not path.exists():
        raise JMeterRunnerCommandError("JMeter JTL file was not produced.")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise JMeterRunnerCommandError("JMeter JTL file contains no sampler results.")

    samples = parse_jmeter_xml(content) if content.startswith("<") else parse_jmeter_csv(content)
    if not samples:
        raise JMeterRunnerCommandError("JMeter JTL file contains no sampler results.")
    return summarize_jmeter_samples(samples)


def parse_jmeter_csv(content: str) -> list[JMeterSample]:
    rows = csv.DictReader(content.splitlines())
    samples: list[JMeterSample] = []
    for row in rows:
        if not row:
            continue
        label = first_present(row, "label", "Label", "samplerData") or "sampler"
        response_code = first_present(row, "responseCode", "response_code", "rc") or ""
        response_message = first_present(row, "responseMessage", "response_message", "rm") or ""
        samples.append(
            JMeterSample(
                label=label,
                success=parse_bool(first_present(row, "success", "s")),
                elapsed_ms=parse_int(first_present(row, "elapsed", "t")),
                latency_ms=parse_optional_int(first_present(row, "Latency", "latency", "lt")),
                response_code=response_code,
                response_message=response_message,
                bytes_received=parse_optional_int(first_present(row, "bytes", "by")),
                timestamp_ms=parse_optional_int(first_present(row, "timeStamp", "ts")),
            ),
        )
    return samples


def parse_jmeter_xml(content: str) -> list[JMeterSample]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise JMeterRunnerCommandError("JMeter JTL XML is invalid.") from exc

    samples: list[JMeterSample] = []
    for element in root.iter():
        if element.tag not in {"sample", "httpSample"}:
            continue
        label = element.attrib.get("lb") or element.attrib.get("label") or "sampler"
        response_code = element.attrib.get("rc") or element.attrib.get("responseCode") or ""
        response_message = element.attrib.get("rm") or element.attrib.get("responseMessage") or ""
        samples.append(
            JMeterSample(
                label=label,
                success=parse_bool(element.attrib.get("s") or element.attrib.get("success")),
                elapsed_ms=parse_int(element.attrib.get("t") or element.attrib.get("elapsed")),
                latency_ms=parse_optional_int(element.attrib.get("lt") or element.attrib.get("Latency")),
                response_code=response_code,
                response_message=response_message,
                bytes_received=parse_optional_int(element.attrib.get("by") or element.attrib.get("bytes")),
                timestamp_ms=parse_optional_int(element.attrib.get("ts") or element.attrib.get("timeStamp")),
            ),
        )
    return samples


def summarize_jmeter_samples(samples: list[JMeterSample]) -> tuple[dict[str, Any], list[JMeterTestResultCandidate]]:
    passed = sum(1 for sample in samples if sample.success)
    failed = sum(1 for sample in samples if not sample.success)
    total = len(samples)
    duration_ms = sum(sample.elapsed_ms for sample in samples)
    latencies = [sample.latency_ms for sample in samples if sample.latency_ms is not None]
    average_latency_ms = int(sum(latencies) / len(latencies)) if latencies else 0
    parsed_result = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": 0,
        "error": 0,
        "sampler_count": total,
        "assertion_count": total,
        "duration_ms": duration_ms,
        "average_latency_ms": average_latency_ms,
    }
    return parsed_result, [sample_to_result(sample) for sample in samples]


def sample_to_result(sample: JMeterSample) -> JMeterTestResultCandidate:
    status = "passed" if sample.success else "failed"
    failure_message = None if sample.success else failure_message_for_sample(sample)
    return JMeterTestResultCandidate(
        test_name=f"jmeter/{sample.label}",
        test_file=None,
        status=status,
        duration_ms=sample.elapsed_ms,
        failure_message=failure_message,
        metadata={
            "source": "jmeter_runner",
            "sampler_label": sample.label,
            "response_code": sample.response_code,
            "response_message": sample.response_message,
            "latency_ms": sample.latency_ms,
            "bytes_received": sample.bytes_received,
            "timestamp_ms": sample.timestamp_ms,
        },
    )


def failure_message_for_sample(sample: JMeterSample) -> str:
    details = " ".join(part for part in (sample.response_code, sample.response_message) if part)
    return details or "JMeter sampler failed"


def first_present(row: dict[str, str | None], *keys: str) -> str | None:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def parse_bool(value: str | None) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_int(value: str | None) -> int:
    parsed = parse_optional_int(value)
    return parsed if parsed is not None else 0


def parse_optional_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(str(value)))
    except ValueError:
        return None
