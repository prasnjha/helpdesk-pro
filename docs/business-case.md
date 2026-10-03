# Business Case — HelpDesk Pro

Capstone reference: BC-AINE-007. Domain: enterprise SaaS customer support.

It explains why the product exists, who uses it, how success is judged, which business rules must hold, and what value it creates. The full requirements are in `specs/brd/brd.md`.

## 1. Problem

A B2B software company receives support requests from many client organizations at once. Today, without a shared system, requests arrive by email and get lost, sent to the wrong person, or answered late. Nobody can say with confidence which requests are about to miss a promised response time. Leaders cannot show whether service commitments were met. Good answers given to one customer stay in one agent's inbox.

HelpDesk Pro is meant to fix four things:

- Requests reach the right team without someone reading each one first.
- Every ticket has a visible clock for the first response and for the final resolution.
- Missed clocks escalate automatically to a more senior queue.
- Solutions from resolved tickets become searchable knowledge for customers and agents.

The build itself has a constraint. The company is testing whether a platform like this can be specified, built, and reviewed by AI agents under human supervision, with no hand-written production code. The business question is therefore twofold: does the product work, and can the process be trusted?

## 2. Target Users

**Customers** are staff at client companies who need help with billing, technical faults, or their account. They are not support specialists. They want a short form, a clear status, and a way to answer questions the support team asks. They use phones as well as desktops.

**Support agents** work a shared queue most of the day. They need to see what is urgent and what is at risk, take ownership of a ticket, pass it on when it belongs elsewhere, leave internal notes for colleagues, and reply to the customer. They also contribute to the knowledge base when they solve something useful.

**Support admins** own the service commitments. They decide how fast each priority must receive a first response and a resolution. They manage teams and people, and they review how the service performed. They change commitments through a policy editor, not through a developer.

Each group is limited to what its role allows. Customers see only their own tickets. Agents work the queues. Admins set policy and manage the team.

## 3. Success Metrics

Success is measured in four places.

**Functional correctness.** All ten acceptance criteria (AC-01 to AC-10) pass, and each has at least one test whose name carries its identifier. A failing criterion means the release is not done.

**Routing and timing accuracy.** On the seed data set, every ticket reaches the team that matches its category. Every SLA timer is computed in whole minutes. Every seeded breach scenario moves the ticket to the higher-tier queue and marks it escalated. The target for each is 100 percent, with no tolerance.

**Integrity and access.** No code path updates or deletes ticket history, notes, replies, assignments, or SLA events. No customer can read another customer's ticket. No request bypasses routing. Each is checked by automated tests. The target is zero failures.

**Delivery quality.** Line coverage is at least 80 percent, with a target of 100 percent of meaningful code. The application starts with one command and its health endpoint answers within one second. A new reviewer can reach a running system with seed data in about ten minutes using the README.

For the capstone, the working target is a Merit grade (75 or above), with Distinction (90 or above) as the stretch goal.

**Business outcomes (proposed, to be confirmed).** Once live, the service should have 95 percent of tickets receive a first response within SLA, and fewer than 5 percent of tickets escalate. Median time to first response is tracked per priority. The number of knowledge base articles published per month is tracked. The share of customers who find an answer in the knowledge base before opening a ticket is tracked.

## 4. Domain Rules

These rules define the business. They are enforced in the domain layer and checked by tests.

**Ticket lifecycle.** A ticket has five states: open, in progress, pending customer, resolved, closed. The normal path follows that order. An agent may resolve a ticket directly from in progress, and a customer reply on a pending ticket returns it to open. Any other move is refused with an explicit error. Closed tickets cannot be changed.

**Routing.** Every new ticket lands in exactly one team queue, chosen by its category: Billing, Technical, or Account. A ticket with no valid category is not accepted. Routing cannot be skipped.

**Ownership.** Agents can claim a ticket or reassign it to another agent. Every change records who acted, what changed, and when. The record cannot be edited.

**Response and resolution clocks.** Each ticket starts two clocks at creation, one for the first response and one for the resolution. The response clock stops at the first reply an agent sends the customer. The resolution clock runs until the ticket is resolved, including time spent waiting on the customer. Clocks are measured in whole minutes.

**Escalation.** When either clock runs past its limit, the ticket is flagged as escalated and moves to the higher-tier queue for its category. The lifecycle state does not change. Escalation happens once per clock.

**Communication.** Agents can write internal notes that customers never see, and public replies that customers do see. Both are permanent records. Customers can reply on their own tickets. A customer reply on a pending ticket returns it to open.

**Knowledge base.** An agent can publish a resolved ticket as a knowledge article with a title, body, and tags. Only agents and admins can create or change articles. Customers can search them.

**Service policy.** Each priority has a response limit and a resolution limit in minutes. Admins edit these limits without a code change. Every published version is kept and cannot be altered. A new change creates a new version.

**Data handling.** Personal details in ticket text, such as emails, phone numbers, and names, are masked in logs. Only synthetic data is used in this project.

## 5. Value Proposition

For the company that runs support, HelpDesk Pro turns a shared inbox into a managed service. Customers get a clear path in and a visible status. Agents get a queue that shows what is urgent. Admins get commitments they can change without a release and a record that shows whether they were met.

For the capstone, the product proves a specific claim: a complete, rule-heavy business system can be built by AI agents under a strict specification, with quality gates for architecture, access control, timing accuracy, and tests. The human's job is to write the spec, set the rules, and review the work, not to type the code.

What the product deliberately does not do: it does not read email, chat in real time, use machine learning to route tickets, or log in through an external identity provider. These are left out so the core rules can be built and checked properly.
