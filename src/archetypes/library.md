---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
h1: "{{ replace .File.ContentBaseName "-" " " | title }}"
definition: ""
date: {{ .Date | time.Format "2006-01-02" }}
tags: []
summary: ""
draft: true
library:
  # tool | mcp | skill | persona — must exist in src/data/library.yaml
  kind: ""
  version: ""
  # e.g. "MCP spec 2026-06-18, schema v2"
  checkedAgainst: ""
  repo: ""
---
