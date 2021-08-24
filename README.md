# Container - crond

A container to hold and run a crond daemon.  This container will  holds multiple "services" that provided various tasks that make sense to be scheduled. This container can run independently or as part of a kubernets cron serivce.

## Configuration

The services, probably python scripts, should be installed and be able to run with all dependencies

WARNING: These sripts should not automatically provide their configuration, specifically any secrets. Usually the secrets should be provided via the launch of the container. 

## Services

### cachet-component-tester.py

Provides a way to run pre-defined test on components defined in a cachet status server. This script uses a test file to define the tests and checks against the components of a cachet server.

#### To-Do:

Continue to run tests against non-operational components, that have an existing incident, state equals performance issues, and has fewer than five updates.

### glacier-backup

to-do: define this.
https://www.withoutthesarcasm.com/using-amazon-glacier-for-personal-backups/

