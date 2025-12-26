#~  Given a project, container command name, and list of session IDs, start the containers for each session.
import argparse
import logging
import os
from datetime import time
from time import sleep
import xnat

import requests



def main():
    parser = argparse.ArgumentParser(description='Given a project, container command name, and list of connection IDs, start the containers for each connection.')
    parser.add_argument('--project', required=True, help='Specify project id.')
    parser.add_argument('--session_id_file', required=False, help='Specify path to a file with a list of experiment IDs, one per line.')
    parser.add_argument('--session_label_file', required=False, help='Specify path to a file with a list of experiment labels, one per line.')
    parser.add_argument('--container', required=False, help='Specify container wrapper label.')
    parser.add_argument('--wrapper_id', required=False, help='Specify container wrapper ID. If not provided, will look up by container label.')
    parser.add_argument('--delay', type=int, default=1, help='Delay in seconds between starting each container (default: 1 second).')
    parser.add_argument("--host", default=os.getenv("XNAT_HOST"),
                        help="XNAT server URL (default: environment variable XNAT_HOST)."
                        )
    parser.add_argument("--user", default=os.getenv("XNAT_USER"),
                        help="XNAT username (default: environment variable XNAT_USER)."
                        )
    parser.add_argument("--password", default=os.getenv("XNAT_PASS"),
                        help="XNAT password (default: environment variable XNAT_PASS)."
                        )
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    if not args.session_id_file and not args.session_label_file:
        raise ValueError("You must specify either --session_id_file or --session_label_file.")
    elif args.session_id_file and args.session_label_file:
        raise ValueError("You cannot specify both --session_id_file and --session_label_file. Choose one.")
    elif args.session_id_file:
        args.experiments = args.session_id_file
        args.ids_provided = True
    elif args.session_label_file:
        args.experiments = args.session_label_file
        args.ids_provided = False
    if not args.host:
        raise ValueError("XNAT host must be specified with --host or XNAT_HOST environment variable.")
    if not args.user:
        raise ValueError("XNAT user must be specified with --user or XNAT_USER environment variable.")
    if not args.password:
        raise ValueError("XNAT password must be specified with --password or XNAT_PASSWORD environment variable.")

    logging.debug(f"Connecting to XNAT at {args.host} with user {args.user}")
    connection = xnat.connect(args.host, user=args.user, password=args.password, detect_redirect=True)
    try:
        wrapper_id = None;
        if not args.wrapper_id:
            wrapper_dict = get_containers(connection, args.host, args.project)
            if args.container not in wrapper_dict.keys():
                raise ValueError(
                    f"Container '{args.container}' not found. Choose from container wrapper names: {list(wrapper_dict.keys())}")

            wrapper_id = wrapper_dict.get(args.container)
        else:
            wrapper_id = args.wrapper_id

        logging.debug(f"Starting container {args.container} with ID {wrapper_id}")

        experiments = parse_sessions(args.experiments)

        for experiment in experiments:
            if not experiment:
                continue
            if args.ids_provided:
                experiment_id = experiment
                logging.debug(f"Launching container for session ID: {experiment_id.strip()}")
            else:
                experiment_id = lookup_experiment_id(connection, args.project, experiment.strip())
                logging.debug(f"Launching container for session label: {experiment} ,ID: {experiment_id.strip()}")

            print(f"Starting container: {args.container}: {wrapper_id} on experiment: {experiment_id}")
            launch_session_container(connection, args.project, experiment_id, wrapper_id)
            if args.delay > 0:
                print(f"Delaying {args.delay} seconds before starting the next container.")
                sleep(args.delay)
                args.delay += 0.5  # Increment delay for the next iteration
    finally:
        connection.disconnect()
        print("Disconnected from XNAT.")


def lookup_experiment_id(connection, project_id, experiment_label):
    experiments = connection.projects[project_id].experiments.values()
    for exp in experiments:
        if exp.label == experiment_label:
            return exp.id
    raise ValueError(f"Experiment with label '{experiment_label}' not found in project '{project_id}'.")

def parse_sessions(exp_file):
    experiments = []
    if exp_file:
        with open(exp_file, 'r') as f:
            for line in f:
                experiments.append(line.strip())
    return experiments


def get_containers(connection, host, project, count=0):
    url = f"/xapi/commands/available?project={project}&xsiType=xnat%3ActSessionData&format=json"
    logging.debug(f"Retrieving containers from URL: {url}")
    headers = {'Content-Type': 'application/json'}
    response = connection.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve containers from URL: {url}")
        logging.error(f"Pausing for 10 seconds before retrying...")
        sleep(10)
        if count < 5:
            return get_containers(connection, host, project, count+1)
        else:
            logging.error(f"Failed to retrieve containers after multiple attempts. Status code: {response.status_code}")
            raise Exception(f"Failed to get containers: {response.text}")

    elif response.status_code == 200 and response.json() is not None:
        return {item["wrapper-name"]: item["wrapper-id"] for item in response.json()}
    else:
        return {}

def launch_session_container(connection, project, experiment_id, wrapper_id):
    # REST API endpoint for session launch
    api_endpoint = f"/xapi/projects/{project}/wrappers/{wrapper_id}/root/session/launch"

    request_object = {
        "project": f"/archive/projects/{project}",
        "session": f"/archive/experiments/{experiment_id}"
    }

    # Make the API call
    logging.debug(f"Launching with url: {api_endpoint} and request object: {request_object}")
    response = connection.post(api_endpoint, json=request_object)

    if response.status_code == 200:
        print(f"Container launch request sent successfully: {api_endpoint}")
    else:
        logging.error(f"Failed to launch session: {api_endpoint}")
        logging.error(f"Status code: {response.status_code}")
        logging.error(f"Error message: {response.text}")


if __name__ == '__main__':
    main()