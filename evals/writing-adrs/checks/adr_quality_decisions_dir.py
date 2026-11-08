#!/usr/bin/env python3
"""Options-and-costs check for ADRs kept in docs/decisions/."""

import os
import runpy

os.environ["ADR_DIR"] = "docs/decisions"
runpy.run_path(os.path.join(os.path.dirname(__file__), "adr_has_options_and_costs.py"), run_name="__main__")
