---
title: What a schema change does to four models
h1: What one unannounced schema change did to four models over thirty days
definition: A column rename that broke nothing visibly degraded answer accuracy across every model tested, and none of them reported difficulty.
date: 2026-09-15
lastReviewed: 2026-09-18
type: lab
pillar: silent-failure-problem
group: detection
tags:
  - drift
  - evaluation
  - lineage
summary: Thirty days of the same hundred questions against a schema that changed underneath them on day ten.
draft: false
lab:
  runDate: 2026-09-15
  models:
    - claude-opus-5
    - claude-sonnet-5
    - gpt-5.2
    - gemini-3-pro
  schemaVersion: v2
  harness: https://github.com/smaddanki/silent-failure-harness
---

## Results

PLACEHOLDER — results come before method, deliberately.

## Method

PLACEHOLDER.

## What we did not test

PLACEHOLDER.

{{< cite >}}
