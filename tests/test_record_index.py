#!/usr/bin/env python3
"""/record resolves the RDF's own ids (v3.0.0, backlog item 7).

web/public/record-index.json maps each edge id to the edge's position in
/graph.json. This checks every id against tools/query/export_rdf.py, and checks
that the page's lookup rule (filter the edge's references by volume and
paragraph, take the n-th) finds exactly the reference each claim IRI names.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "query"))
from export_rdf import claim_ids, edge_id  # noqa: E402

INDEX = os.path.join(ROOT, "web", "public", "record-index.json")
GRAPH = os.path.join(ROOT, "web", "public", "graph.json")
PAGE = os.path.join(ROOT, "web", "public", "record.html")
ID = re.compile(r"^([0-9a-f]{16})(?:-([0-9a-z]+)-([0-9]+)(?:-([0-9]+))?)?$")


@unittest.skipUnless(os.path.exists(INDEX), "record-index.json not built; run node web/build-atlas.mjs")
class RecordIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.load(open(INDEX))["edges"]
        cls.graph = json.load(open(GRAPH))["edges"]

    def test_every_edge_id_matches_the_exporter(self):
        self.assertEqual(len(self.index), len(self.graph), "an edge id collides or is missing")
        for i, edge in enumerate(self.graph):
            self.assertEqual(self.index.get(edge_id(edge)), i, edge_id(edge))

    def test_every_claim_id_resolves_to_its_reference(self):
        n = 0
        for i, edge in enumerate(self.graph):
            for ref, local in claim_ids(edge):
                m = ID.match(local)
                self.assertTrue(m, local)
                hit = self.graph[self.index[m.group(1)]]
                same_place = [r for r in hit["references"]
                              if str(r["volume"]) == m.group(2) and str(r["paragraph"]) == m.group(3)]
                nth = int(m.group(4) or 1)
                self.assertIs(same_place[nth - 1], ref, local)
                n += 1
        self.assertEqual(n, sum(len(e["references"]) for e in self.graph))

    def test_page_uses_the_same_id_pattern(self):
        page = open(PAGE).read()
        self.assertIn(ID.pattern.replace("^", "").replace("$", ""), page)
        self.assertIn('content="noindex"', page)


if __name__ == "__main__":
    unittest.main()
