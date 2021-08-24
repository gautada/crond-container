#! /usr/bin/python3

# python libraries for script
import argparse
import json
from os.path import exists
import logging

# cachet client
import cachetclient
from cachetclient.v1 import enums

# libraries for testing
from pythonping import ping
import requests

"""This is an atomic component tester for status reporting. This connects a test type with a payload
configuration for a specific component.
"""
def test_ping_func(ip=None, domain=None, timeout=5, count=5):
    
    assert ip is not None or domain is not None, 'IP address or domain must be provided'
    assert ip is None or domain is None, 'Only IP address or domain must be provided'
    
    dest = domain if ip is None else ip
    try:
        return (0, ping(dest, timeout=count, count=count, verbose=False))
    except Exception as e:
        return (1, e)

def test_get_func(url=None):
    try:
        response = requests.get(url)
        return(0, "%s - %s" % (response.status_code, response.reason))
    except Exception as e:
        return (1, e)
    
def func_psql(payload=None):
    pass # connect to db, query, and check results.
    
def check_group(group):
    pass
    
def load_metadata(endpoint=None, api_token=None):
    
    assert endpoint is not None, 'Endpoint must be provided'
    assert api_token is not None, 'API Token must be provided'
    
    client = cachetclient.Client(
        endpoint=args.endpoint,
        api_token=args.api_token,
    )
    
    if not client.ping():
        raise ResourceWarning("Cachet service(%s) is not accessable" % endpoint)
    
    groups = {}
    list = client.component_groups.list()
    for item in list:
        groups[item.name.lower()] = item
    
    components = {}
    list = client.components.list()
    for item in list:
        components[item.name.lower()] = item
    
    
    return (client, groups, components)
    
def create_incident(client=None, group=None, component=None, test=None, message=None):
    
    assert client is not None, 'Client must be provided'
    assert group is not None, 'Group must be provided'
    assert component is not None, 'Component must be provided'
    assert message is not None, 'Message must be provided'
    assert 0 < len(message), 'Message must contain some data'
    assert component.status == enums.COMPONENT_STATUS_OPERATIONAL, 'Component status must be operational'
        
    incident = client.incidents.create(name="Component Status Test Failure (%s/%s:%s)" % (group.name, component.name, test),
            message=message, status=enums.INCIDENT_INVESTIGATING, visible=True, stickied=False, component_id=component.id,
            component_status=enums.COMPONENT_STATUS_PARTIAL_OUTAGE)
    logging.info("Created incident(%s)" % incident.id)
    
# to-do: should update incident on continued failure.
def test_status(metadata=None, group=None, component=None, test=None, payload=None):
    
    assert metadata is not None, 'Metadata must be provided'
    assert group is not None, 'Group must be provided'
    assert component is not None, 'Component must be provided'
    assert test is not None, 'Test must be provided'
    assert payload is not None, 'Payload must be provided'
    assert group.lower() in metadata[1].keys(), 'Group(%s) must exist in metadata' % group
    assert component.lower() in metadata[2].keys(), 'Component(%s) must exists in metadata' % component
    
    group = metadata[1][group.lower()]
    component = metadata[2][component.lower()]
    
    if not component.enabled:
        logging.info("TEST (%s/%s:%s) SKIP - Component Disabled" % (group.name, component.name, test))
    elif test.lower() not in component.tags:
        logging.info("TEST(%s/%s:%s) SKIP - Component Not Tagged for Test" % (group.name, component.name, test))
    elif enums.COMPONENT_STATUS_OPERATIONAL != component.status:
        logging.info("TEST(%s/%s:%s) SKIP - Component status not operational" % (group.name, component.name, test))
    else:
        response = None
        if 'ping' == test.lower():
            response = test_ping_func(**payload)
        elif 'get' == test.lower():
            response = test_get_func(**payload)
        else:
            logging.info("TEST(%s/%s:%s) SKIP - Test function not found" % (group.name, component.name, test))
    
        if 0 == response[0]:
            logging.info("TEST(%s/%s:%s) SUCCESS" % (group.name, component.name, test))
            logging.debug("Test Response\n%s" % response[1])
        elif 1 == response[0]:
            logging.error("TEST(%s/%s:%s) FAILED(Exception) - %s" % (group.name, component.name, test, response[1]))
            create_incident(metadata[0], group, component, test, "%s" % response[1])
        else:
            pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Cachet component status tester')
    parser.add_argument('-d', '--definitions', help='A filepath for a list of test definitions to run(1 per line).')
    parser.add_argument('-c', '--config', help='A filepath to the configuration file', default='/etc/cachet/client.json')
    parser.add_argument('-e', '--endpoint', help='A uri to the Cachet server')
    parser.add_argument('-l', '--log', help='Logging level [NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL]')
    parser.add_argument('-t', '--api_token', help='Unique API token for the user to execute the test and update Cachet')
    parser.add_argument('tests', nargs='?', help="JSON formated test defintions to append to the run queue")
    args = parser.parse_args()

    vargs = vars(args)
    
    # Load the configuration from the config file
    if args.config is not None:
        if exists(args.config):
            with open(args.config) as file:
                config = json.load(file)
                for key in config.keys():
                    if key in vargs and vargs[key] is None:
                        if key == "definitions":
                            args.definitions = config[key]
                        elif key == "endpoint":
                            args.endpoint = config[key]
                        elif key == "api_token":
                            args.api_token = config[key]
                        elif key == "log":
                            args.log = config[key]
                        else:
                            logging.warning("Key(%s) in configuration not supported" % key)
            file.close()

    # to-do: override with environment variables, this allows for changing the config settings at runtime. MAYBE, needs testing
    
    # Configure the logging subsystem to add timestamp level message, the level is provided by the config system with a default
    # level equal to WARNING.
    logging.basicConfig(format='%(asctime)s %(message)s', level=getattr(logging, ("%s" % args.log).upper(), logging.WARNING))
    
    # load the test from definitions file
    queue = []
    if args.definitions is not None:
        if exists(args.definitions):
            with open(args.definitions) as file:
                queue = json.load(file)
            file.close()
        
    # load test from arguments
    if args.tests is not None:
        tests = json.loads(args.tests)
        if isinstance(tests, dict):
            queue.append(tests)
        elif isinstance(tests, list):
            queue += tests
        else:
            logging.warning("Test(%s) is not added to queue" % args.tests)

    # connect to server
    metadata = load_metadata(args.endpoint, args.api_token)
    
    # execute tests
    logging.debug("Executing %s component status tests" % len(queue))
    for test in queue:
        test_status(metadata=metadata, **test)

