from backend.app.modules.knowledge.service import (
    MAX_KNOWLEDGE_CARDS_PER_SOURCE,
    candidate_sentences,
    classify_knowledge,
    infer_module_key,
    knowledge_fingerprint,
)


def test_structure_aware_chunks_keep_heading_and_more_than_twenty_rows() -> None:
    text = "# OTA\n\n" + "\n".join(
        f"{index}\tOTA command {index}\tDevice must return success for command {index}"
        for index in range(30)
    )

    chunks = candidate_sentences(text)

    assert len(chunks) == 30
    assert chunks[0].startswith("OTA:")
    assert len(chunks) <= MAX_KNOWLEDGE_CARDS_PER_SOURCE


def test_evse_domain_classification_and_module_inference() -> None:
    assert classify_knowledge("OTA download must recover after network reconnect") == "RecoveryScenario"
    assert classify_knowledge("OCPP BootNotification request must include charge point model") == "APIContract"
    assert classify_knowledge("OTA success rate must reach 98 percent") == "PerformanceConstraint"
    assert infer_module_key("The charger sends OCPP BootNotification") == "ocpp"
    assert classify_knowledge("Fallback starts after timeout") == "RecoveryScenario"
    assert classify_knowledge("Charging current must remain below 32A") == "BoundaryCondition"
    assert classify_knowledge("If the charger is offline then use static load balancing") == "BusinessRule"
    assert classify_knowledge("If charging pauses for 10 minutes, the vehicle cannot recover") == "RecoveryScenario"
    assert classify_knowledge("Display the last applied online or offline value") == "TestStrategyNote"
    assert classify_knowledge("\u79bb\u7ebf\u60c5\u51b5\u4e0b\u76f4\u63a5\u8fd0\u884c\u8d1f\u8f7d\u5747\u8861") == "BusinessRule"
    assert infer_module_key("Single phase charger fallback") == "charging"


def test_normalized_fingerprint_deduplicates_formatting_variants() -> None:
    assert knowledge_fingerprint("Network reconnect is required.") == knowledge_fingerprint(
        "network-reconnect is required"
    )


def test_spreadsheet_rows_are_mapped_with_headers() -> None:
    chunks = candidate_sentences(
        "# Sheet: commands\n1\tCommand\tPurpose\tParameters\n"
        "2\tlogin [pincode]\tAuthenticate device\tpincode:string"
    )

    assert chunks == [
        "Sheet: commands: Command: login [pincode]; Purpose: Authenticate device; Parameters: pincode:string"
    ]
    assert classify_knowledge(chunks[0]) == "CommandReference"


def test_image_urls_do_not_become_api_contracts() -> None:
    chunks = candidate_sentences(
        "# Charger protection\nCharging pauses on critical error: "
        "[Image](https://internal.example/space/api/image/123)"
    )

    assert chunks == []


def test_limited_is_not_treated_as_an_explicit_boundary() -> None:
    assert classify_knowledge("Limited load balancing is active") == "TestStrategyNote"


def test_protocol_name_without_contract_semantics_stays_domain_knowledge() -> None:
    assert classify_knowledge("OCPP has higher priority than fixed three-phase charging") == "TestStrategyNote"
    assert classify_knowledge("OCPP diagnostics respond to vehicle operations") == "TestStrategyNote"
    assert classify_knowledge("OCPP logs are uploaded several days after the issue") == "TestStrategyNote"
