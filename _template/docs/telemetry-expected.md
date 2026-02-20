# [Emulation Name] Expected Telemetry

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This document describes what endpoint telemetry tools SHOULD capture.
Use this to validate your detection capabilities.
============================================================================
```

## Overview

This document lists the telemetry signals that security tools should capture at each stage of execution. If your EDR/SIEM doesn't capture these events, you have a visibility gap.

## Telemetry by Stage

### Stage 1: [Stage Name]

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| [Type] | [Field] | [Value] |

**EDR Detection Logic:**
```
[Detection rule pseudocode]
```

### Stage 2: [Stage Name]

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| [Type] | [Field] | [Value] |

**EDR Detection Logic:**
```
[Detection rule pseudocode]
```

[Continue for each stage...]

## Complete Process Tree

```
[Full process tree]
```

## Event Summary Table

| Stage | Event Count | Key Detection |
|-------|-------------|---------------|
| [Stage] | [Count] | [Detection] |

## SIEM Correlation Rules

### Rule 1: [Rule Name]

```
[Rule logic]
```

### Rule 2: [Rule Name]

```
[Rule logic]
```

## Visibility Gap Checklist

| Telemetry Type | Required For | ✓ |
|----------------|--------------|---|
| [Type] | [Stage] | ☐ |

## Sample Queries

### Splunk

```spl
[Splunk query]
```

### Elastic/KQL

```kql
[KQL query]
```
