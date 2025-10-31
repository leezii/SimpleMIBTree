# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project summary
- Flask-based web app to parse SNMP MIB files and render a clickable tree on the frontend.

Common commands
- Create venv: python3 -m venv venv && source venv/bin/activate
- Install deps: pip install -r requirements.txt
- Run dev server: python app.py  # serves http://127.0.0.1:5000 with debug
- Tests: README mentions a script test_mib_parser.py; if present, run: python test_mib_parser.py
- Lint/typecheck: no configuration files found (e.g., ruff/flake8/black/mypy not present).

Architecture overview
- Entry point: app.py
  - App setup: Flask app with UPLOAD_FOLDER=uploads, MAX_CONTENT_LENGTH=16MB, logging=DEBUG; ensures uploads/ exists.
  - Routes
    - GET/POST / → renders templates/index.html; POST echoes form data via process_form_data().
    - GET/POST /hello → renders templates/hello.html; POST echoes form data, logs request.
    - GET /mib-parser → renders templates/mib_parser.html.
    - POST /upload-mib → accepts file field mib_file; validates extension in {mib, txt, my}; saves to uploads/, parses, deletes the saved file, returns JSON.
  - MIB parsing pipeline (custom, string-based)
    - parse_mib_file(path) → reads file and delegates to parse_mib_content(content, filename).
    - parse_mib_content(content, filename)
      - Scans lines to collect raw_objects:
        - OBJECT-TYPE blocks: captures name, SYNTAX, MAX-ACCESS, STATUS, and OID (from ::= ...), building oid_path.
        - OBJECT IDENTIFIER lines with ::= create identifier nodes and oid_path.
        - MODULE-IDENTITY adds a leading module node.
      - calculate_numeric_oids(raw_objects)
        - Builds name → object and name → numeric OID maps.
        - Seeds STANDARD_OID_MAP for roots and hardcodes sampleMIB → 1.3.6.1.4.1.99999.
        - Iteratively resolves numeric OIDs based on parent names and child IDs.
      - build_hierarchy(raw_objects)
        - Attaches children to parents using the last resolvable name in oid_path.
        - Falls back to organize_by_naming_convention() to group sample* items (system/config groupings) under module roots.
    - allowed_file(filename): guards extensions.
    - process_form_data(): trivial helper for demo forms.
  - Templates expected (not included in repo): templates/index.html, templates/hello.html, templates/mib_parser.html.
  - Upload handling: uses werkzeug.utils.secure_filename; temporary file is removed after parse attempt.

Key dependencies (requirements.txt)
- Flask==2.3.3, Werkzeug==2.3.7, pysmi==1.1.13, pysnmp==4.4.12
  - Current code path uses a custom, simplified parser and does not invoke pysmi/pysnmp directly.

API surface (from README)
- POST /upload-mib
  - Form-data: mib_file (file)
  - Response JSON: { success: bool, module: string, tree: [nodes...] } where each node has text, type (object|identifier|module), oid, optional syntax/access/status/children, and computed numeric_oid when available.
