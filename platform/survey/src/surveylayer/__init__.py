"""Àlááfìa survey layer.

INGEST step of the pipeline (spine = RESOLVE, done). Pulls national and
subnational health indicators from published sources and lands them on the
geography spine as one long, sourced, uncertainty-bearing table.

v1 source: the DHS program API (StatCompiler) — free, no auth, Nigeria
DHS 1990–2024 + MIS 2010–2021, state level from 2013 on. Survey microdata
and small-area models build on top of this later.
"""

__version__ = "0.1.0"
