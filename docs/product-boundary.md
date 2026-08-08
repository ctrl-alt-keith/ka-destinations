# Product Boundary

The Publication Product Candidate owns the authorized external-delivery
transaction and publication-receipt semantics.

`ka-destinations` currently implements the destination-specific publication
behavior for that boundary. It takes a caller-supplied artifact and, under
authorization supplied by an authorized publication authorizer, publishes the
artifact into a downstream destination.

The repository implementation question is:

> How does this repository currently implement explicit delivery of a
> caller-supplied artifact to a supported downstream destination and emit the
> resulting publication receipt?

This question is limited to current implementation, validation, review, and
merge facts in this repository. It does not transfer Publication authority to
the repository.

## Publication Product Candidate Role

Publication owns:

- the authorized external-delivery transaction;
- publication-receipt meaning; and
- the boundary between an authorized publication event and downstream
  lifecycle management.

Publication does not own acquisition, editorial judgment, analytical
interpretation, or downstream lifecycle management. An authorized publication
authorizer, not the Product Candidate, repository, CLI, validator, or
destination driver, supplies the consequential authorization for a specific
external delivery.

## Current Repository Implementation

`ka-destinations` currently:

- implements destination-specific rendering and creation behavior;
- uses caller-configured destination authentication;
- packages the CLI and destination drivers;
- validates the local inputs its CLI accepts;
- performs supported destination API operations; and
- emits publication receipts.

This placement is replaceable. Moving the implementation would not move or
change Publication authority.

## Core Invariant

Publish the caller-supplied artifact under an existing authorization; do not
acquire, judge, analyze, authorize, or manage the downstream lifecycle.

This means the repository starts after an artifact already exists and an
authorized publication authorizer has supplied the consequential
authorization. Its runtime components deliver that artifact intentionally into
a destination, using the destination's required authentication, creation,
rendering, and publish behavior. They may return or emit destination-specific
publication receipts.

The repository and its runtime components do not decide whether the artifact
should exist, whether it is true, whether it should be retained, whether
publication is authorized, or how destination content should be managed after
publication. Authentication establishes access to a provider; it does not
supply the human authorization for consequential delivery.

## Product Object

The primary product object is a publication event.

A publication event records or performs the explicit act of publishing a
caller-supplied artifact to a destination. It is not an editorial review, an
acquisition record, a retained knowledge object, or an analytical finding.
The authorized publication authorizer supplies publication authorization.
Editorial review and retention decisions remain with their applicable
authority roles; `ka-destinations` does not determine whether the artifact was
approved or retained.

## Contract And Runtime Roles

- **Semantic Contract Producer:** Publication owns shared
  publication-receipt meaning and compatible evolution.
- **Normative contract host:** no separate versioned publication-receipt
  interchange contract is currently declared. This repository contains the
  receipt-producing implementation and documents its user-facing fields.
- **Runtime Producer:** the CLI emits a publication receipt for a dry run or
  completed live publish. A destination driver performs the destination API
  operation and returns observed destination identity.
- **Contract consumer:** callers and automations that consume JSON receipt
  output own their acceptance policy for receipt shape and use. No receipt
  consumer implementation is hosted here today.
- **Transport or orchestration:** the caller selects and supplies the artifact
  and invokes the publication path. Transport does not own Publication
  semantics or downstream consumer policy.
- **Consequential human authority:** an authorized publication authorizer
  decides whether the specific artifact may be delivered to the selected
  destination.

A receipt is evidence of the requested or performed operation. It is not
authorization, editorial approval, retained knowledge, or proof of external
truth. Successful validation, authentication, execution, or receipt emission
does not create any of those decisions.

## Caller-Supplied Artifact Boundary

The current CLI accepts a caller-supplied UTF-8 markdown file. It validates the
local input conditions documented by the CLI, but it does not consume or
validate a complete Source Package contract, prove provenance or editorial
acceptance, or select which artifact is authorized.

The caller is responsible for supplying the exact artifact covered by the
publication authorization. Adding producer-contract consumption, artifact
selection policy, or upstream approval interpretation would be a separate
contract or architecture change.

## Repository Boundaries

- The Source Acquisition Product Candidate owns acquisition semantics;
  `knowledge-adapters` currently implements acquisition and normalization.
- The Knowledge Record Enduring Product owns the editorial-retention authority
  boundary. The canonical Playbook [Product Status](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/main/docs/product-status.md#knowledge-record)
  records that current accepted state. [Human Product Promotion Decision #1](https://github.com/ctrl-alt-keith/ai-workflow-playbook/blob/main/docs/product-promotion-decisions/human-product-promotion-decision-001.md)
  preserves the promotion decision provenance, effective 2026-07-24. Its
  current implementation and evidence live outside this repository.
- Publication owns the authorized external-delivery transaction;
  `ka-destinations` currently implements destination-specific publication
  behavior and emits receipts.
- The Evidence Synthesis Product Candidate owns its bounded analytical-attempt
  semantics; analytical inference remains outside this repository.

## Publication Philosophy

Publication means:

- intentionally delivering a caller-supplied artifact under an existing
  publication authorization
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

First ask whether a change fits Publication:

- Does this preserve the authorized external-delivery transaction?
- Does this preserve or improve publication-receipt semantics?
- Does this begin acquiring knowledge?
- Does this make an editorial, retention, or publication-authorization
  decision?
- Does this begin managing destination lifecycle?
- Does this begin analytical inference?

Then ask whether its current implementation belongs in this repository:

- Does it implement a supported destination driver, rendering path, CLI
  behavior, or receipt emission?
- Does it preserve the caller-supplied artifact boundary?
- Does it require a new cross-repository contract, authorization mechanism,
  lifecycle manager, or consumer policy?

A change can fit Publication without belonging in `ka-destinations`. Changes
that acquire material, make consequential human decisions, manage downstream
lifecycle, perform analytical inference, or introduce a new contract or
authorization boundary require separate architectural review and likely belong
outside this repository.

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
