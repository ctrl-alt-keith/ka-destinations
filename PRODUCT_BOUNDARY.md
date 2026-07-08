# Product Boundary

`ka-destinations` is the destination layer for explicit downstream
publication. It takes an already-produced knowledge bundle and publishes it
into a downstream destination.

The repository question is:

> How does an already-produced knowledge bundle get explicitly published into a
> downstream destination?

## Product Role

`ka-destinations` owns:

- explicit publication
- destination-specific rendering
- destination authentication
- destination creation
- publication receipts
- destination-specific publish behavior

It does not own acquisition, editorial judgment, analysis, or downstream
lifecycle management.

## Core Invariant

Publish the packaged bundle; do not acquire, judge, analyze, or manage the
downstream lifecycle.

This means the repository starts after a knowledge bundle already exists. Its
job is to deliver that bundle intentionally into a destination, using the
destination's required authentication, creation, rendering, and publish
behavior. It may return or record destination-specific publication receipts.

The repository should not decide whether the bundle should exist, whether the
bundle is true, how retained knowledge should be reviewed, or how destination
content should be managed after publication.

## Product Object

The primary product object is a publication event.

A publication event records or performs the explicit act of publishing an
approved bundle to a destination. It is not an editorial review, an acquisition
record, a retained knowledge object, or an analytical finding.

## Repository Boundaries

- `knowledge-adapters` owns acquisition and normalization.
- `knowledge-vault` owns editorial review and retention.
- `ka-destinations` owns publication.
- `trusted-ai-environment` owns analytical processing over trusted evidence.

## Publication Philosophy

Publication means:

- intentionally delivering an approved bundle
- destination-specific behavior
- destination-specific receipts

Publication does not mean:

- acquisition
- editorial review
- destination lifecycle management
- synchronization
- publication policy
- ownership of destination content after publication

## Product Decision Filter

Use these questions when deciding whether a change belongs here:

- Does this improve explicit publication?
- Does this improve destination-specific behavior?
- Does this improve publication reliability or receipts?
- Does this begin acquiring knowledge?
- Does this begin reviewing retained knowledge?
- Does this begin managing destination lifecycle?
- Does this begin analytical inference?

Changes that answer yes to acquisition, retained-knowledge review, destination
lifecycle management, or analytical inference likely belong outside this
repository.

## Non-Goals

- acquisition
- normalization
- editorial review
- retention
- truth verification
- destination synchronization
- bidirectional sync
- long-term destination management
- analytical inference
