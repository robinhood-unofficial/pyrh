"""Handles Robinhood's verification workflow, including email, SMS, and app-based approvals."""

import time

import requests


def request_post(
    url: str,
    session: requests.Session,
    payload=None,
    json=False,
):
    """For a given url and payload, makes a post request and returns the response. Allows for responses other than 200.

    Args:
        url: The url to send a post request to.
        session: The requests session to use for the post request.
        payload: Dictionary of parameters to pass to the url as url/?key1=value1&key2=value2.
        json: This will set the 'content-type' parameter of the session header to 'application/json'

    Returns:
        Returns the data from the post request.

    """
    timeout = 16
    try:
        if json:
            session.headers["Content-Type"] = "application/json"
            res = session.post(url, json=payload, timeout=timeout)
            session.headers[
                "Content-Type"
            ] = "application/x-www-form-urlencoded; charset=utf-8"
        else:
            res = session.post(url, data=payload, timeout=timeout)
        assert res.status_code in (
            200,
            201,
            202,
            204,
            301,
            302,
            303,
            304,
            307,
            400,
            401,
            402,
            403,
        ), "Received " + str(res.status_code)
        return res.json()
    except (
        AssertionError,
        requests.RequestException,
        requests.JSONDecodeError,
    ) as message:
        print("Error in request_post: {0}".format(message))
    return None


def request_get(url: str, session: requests.Session):
    """For a given url and payload, makes a get request and returns the data.

    Args:

        url: The url to send a get request to.
        session: The requests session to use for the get request.

    Returns:
         Returns the data from the get request. If jsonify_data=True and requests returns an http code other than <200>
         then either '[None]' or 'None' will be returned based on what the dataType parameter was set as.

    """
    try:
        res = session.get(url)
        res.raise_for_status()
        return res.json()
    except (requests.exceptions.HTTPError, AttributeError) as message:
        print(message)
        return None


def verify_workflow(
    session: requests.Session, device_token: str, workflow_id: str
) -> None:
    """Handle Robinhood's verification workflow, including email, SMS, and app-based approvals.

    Args:
        session: Session object to use for requests.
        device_token: Device token for the user's device.
        workflow_id: Workflow ID for the verification process.

    """
    pathfinder_url = "https://api.robinhood.com/pathfinder/user_machine/"
    machine_payload = {
        "device_id": device_token,
        "flow": "suv",
        "input": {"workflow_id": workflow_id},
    }
    machine_data = request_post(
        url=pathfinder_url, session=session, payload=machine_payload, json=True
    )

    machine_id = machine_data["id"]
    inquiries_url = (
        f"https://api.robinhood.com/pathfinder/inquiries/{machine_id}/user_view/"
    )

    start_time = time.time()

    # 2-minute timeout
    while time.time() - start_time < 120:
        time.sleep(5)
        inquiries_response = request_get(url=inquiries_url, session=session)

        # Handle case where response is None
        if not inquiries_response:
            print("Error: No response from Robinhood API. Retrying...")
            continue

        if (
            "context" in inquiries_response
            and "sheriff_challenge" in inquiries_response["context"]
        ):
            challenge = inquiries_response["context"]["sheriff_challenge"]
            challenge_type = challenge["type"]
            challenge_status = challenge["status"]
            challenge_id = challenge["id"]
            if challenge_type == "prompt":
                print("Check robinhood app for device approvals method...")
                prompt_url = (
                    f"https://api.robinhood.com/push/{challenge_id}/get_prompts_status/"
                )
                while True:
                    time.sleep(5)
                    prompt_challenge_status = request_get(
                        url=prompt_url, session=session
                    )
                    if prompt_challenge_status["challenge_status"] == "validated":
                        break
                break

            # Stop polling once verification is complete
            if challenge_status == "validated":
                break

            if challenge_type in ["sms", "email"] and challenge_status == "issued":
                user_code = input(
                    f"Enter the {challenge_type} verification code sent to your device: "
                )
                challenge_url = (
                    f"https://api.robinhood.com/challenge/{challenge_id}/respond/"
                )
                challenge_payload = {"response": user_code}
                challenge_response = request_post(
                    url=challenge_url, session=session, payload=challenge_payload
                )

                if challenge_response.get("status") == "validated":
                    break
    poll_workflow_status(session=session, machine_id=machine_id, start_time=start_time)


def poll_workflow_status(
    session: requests.Session, machine_id: str, start_time: float
) -> None:
    """Poll the workflow status to confirm final approval.

    Args:
        session: The requests session to use for the post request.
        machine_id: Machine ID from the initial request.
        start_time: Start time of the workflow to check for timeout.

    """
    inquiries_url = (
        f"https://api.robinhood.com/pathfinder/inquiries/{machine_id}/user_view/"
    )

    # Allow up to 5 retries in case of 500 error codes
    retry_attempts = 5

    # 2-minute timeout
    while time.time() - start_time < 120:
        try:
            inquiries_payload = {
                "sequence": 0,
                "user_input": {"status": "continue"},
            }
            inquiries_response = request_post(
                url=inquiries_url, session=session, payload=inquiries_payload, json=True
            )
            if (
                "type_context" in inquiries_response
                and inquiries_response["type_context"]["result"]
                == "workflow_status_approved"
            ):
                return
            else:
                # **Increase delay between requests to prevent rate limits**
                time.sleep(5)
        except requests.exceptions.RequestException as e:
            time.sleep(5)
            print(f"API request failed: {e}")
            retry_attempts -= 1
            if retry_attempts == 0:
                raise TimeoutError(
                    "Max retries reached. Assuming login approved and proceeding."
                )
            print("Retrying workflow status check...")
            continue

        if not inquiries_response:
            time.sleep(5)
            print("Error: No response from Robinhood API. Retrying...")
            retry_attempts -= 1
            if retry_attempts == 0:
                raise TimeoutError(
                    "Max retries reached. Assuming login approved and proceeding."
                )
            continue

        workflow_status = inquiries_response.get("verification_workflow", {}).get(
            "workflow_status"
        )

        if workflow_status == "workflow_status_approved":
            print("Workflow status approved! Proceeding with login...")
            return
        elif workflow_status == "workflow_status_internal_pending":
            print("Still waiting for Robinhood to finalize login approval...")
        else:
            retry_attempts -= 1
            if retry_attempts == 0:
                raise TimeoutError(
                    "Max retries reached. Assuming login approved and proceeding."
                )

    raise TimeoutError("Timeout reached. Assuming login is approved and proceeding.")
