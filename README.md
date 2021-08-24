# Container - crond

A container to hold a simple crond service.  This service holds multiple "clients" that provided various services that make sense to be scheduled. This should work in conjunction with k8s cron mechanism.

## Services

### cachet-component-tester.py

Provides a way to run pre-defined test on components defined in a cachet status server. This script uses a test file to define the tests and checks against the components of a cachet server.

#### To-Do:

Continue to run tests against non-operational components, that have an existing incident, state equals performance issues, and has fewer than five updates.

### glacier-backup

to-do: define this.
