---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
h1: "{{ replace .File.ContentBaseName "-" " " | title }}"
# ONE sentence, no preamble. Rendered directly under the h1 and used as the
# meta description. The single most costly field to leave weak.
definition: ""
date: {{ .Date | time.Format "2006-01-02" }}
lastReviewed: {{ .Date | time.Format "2006-01-02" }}
# perspective | blueprint | lab — selects the layout
type: perspective
# exactly one slug, must have a page under src/content/categories/
categories: ""
# zero or more, each must exist in src/data/tags.yaml
tags: []
summary: ""
draft: true
# Lab pieces only — delete this block for perspective and blueprint.
# lab:
#   runDate: {{ .Date | time.Format "2006-01-02" }}
#   models: []
#   schemaVersion: ""
#   harness: ""
---
