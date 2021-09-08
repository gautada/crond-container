# crond

A container to hold and run a crond daemon.  This container will  holds multiple scripts that provided various tasks that make sense to be scheduled. This container can run independently or as part of a kubernets cron serivce.

## Configuration

The services, probably python scripts, should be installed and be able to run with all dependencies

WARNING: These sripts should not automatically provide their configuration, specifically any secrets. Usually the secrets should be provided via the launch of the container. 

## Services

### cachet-component-tester.py

Provides a way to run pre-defined test on components defined in a cachet status server. This script uses a test file to define the tests and checks against the components of a cachet server.

#### To-Do:

Continue to run tests against non-operational components, that have an existing incident, state equals performance issues, and has fewer than five updates.

### glacier-backup

This should "auto magically" support 3-2-1 backups.  3 backup copies across at least 2 locations with at least 1 location off-site. Requirements for this backup service are:

1. Automatic which is, "set it and forget it"
2. Local high quality encryption
3. Multiple Drop points - I don't know what this ment originally. Now I take it to mean that it can pull data files from multiple points.
4. Should provide an ability to do statusing. - At a minimum container health status.

https://www.withoutthesarcasm.com/using-amazon-glacier-for-personal-backups/

#### Needs

- Backup postgres server, create daily snapshot, back that up
- Backup live sqlite data.
- flip/flop v


