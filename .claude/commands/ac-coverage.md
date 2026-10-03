---
name: ac-coverage
description: List AC-01..AC-10 and the tests that carry each id, and report any criterion with no test.
---

# /ac-coverage

1. Read the traceability table in `specs/app_spec.md` for the ten acceptance criteria.
2. Search `backend/tests`, `frontend/src` and `e2e` for test names or tags containing each id, in any spelling such as `AC-05`, `AC05` or `AC_05`.
3. Print a table: AC id, owning spec, test count, up to three test names.
4. List every AC with zero tests under the heading GAPS.
5. Do not edit any file. End with `COVERAGE: COMPLETE` if every AC has at least one test, otherwise `COVERAGE: GAPS`.