"""Tests for standards/ontology — the tracked ontology canon.

Guards the composition benchmark: the working graphs must parse and compose
to the known triple counts. If a TTL edit changes a count, that is a
deliberate ontology decision — update the benchmark here in the same commit.
"""
from pathlib import Path

import pytest

rdflib = pytest.importorskip("rdflib")

STANDARDS = Path(__file__).resolve().parents[1] / "standards" / "ontology"
CORE = ["risk.ttl", "sites.ttl"]
INSTANCE = "risk_instance_pe_asset.ttl"

CORE_TRIPLES = 263
ALL_TRIPLES = 325


@pytest.mark.parametrize("ttl", CORE + [INSTANCE])
def test_each_ttl_parses(ttl):
    g = rdflib.Graph()
    g.parse(STANDARDS / ttl, format="turtle")
    assert len(g) > 0, f"{ttl} parsed empty"


def _compose(files):
    g = rdflib.Graph()
    for f in files:
        g.parse(STANDARDS / f, format="turtle")
    return g


def test_core_composition_benchmark():
    assert len(_compose(CORE)) == CORE_TRIPLES


def test_full_composition_benchmark():
    assert len(_compose(CORE + [INSTANCE])) == ALL_TRIPLES


def test_core_classes_present():
    g = _compose(CORE)
    ns = "https://mas.example/ontology/core#"
    for cls in ("Asset", "Hazard", "Capability", "ExitValue"):
        subj = rdflib.URIRef(ns + cls)
        assert (subj, None, None) in g or any(g.triples((None, None, subj))), (
            f"core class {cls} missing from composed graph"
        )
