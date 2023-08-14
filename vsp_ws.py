import argparse
import asyncio
import aiohttp
import websockets
from websockets.server import serve
from datetime import datetime


async def redirect(websocket: websockets.WebSocketServerProtocol):
    async for message in websocket:
        account_code, binary_data = parse_message(message)
        if not account_code:
            await websocket.close()
            return

        target_port = choose_target_port(account_code)
        target_url = f"http://{target_host}:{target_port}"
        await send_http_request(account_code, binary_data, target_url)
        await websocket.send("OK")


async def send_http_request(account_code, binary_data, url):
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False, limit=1000),
        headers={
            accountcode_name: account_code,
            # "Content-Type": "application/octet-stream"}, # aiohttp adds automatically
        },
        timeout=aiohttp.ClientTimeout(total=1),
    ) as session:
        if verbose:
            print(
                f"Sending {len(binary_data)} bytes to {url} {accountcode_name}={account_code}"
            )
        async with session.post(url, data=binary_data) as response:
            if response.status != 200:
                print(f"Status code: {response.status}")


def parse_message(message) -> (str, bytes):
    account_code = None
    try:
        parsed_message = eval(message)
        if isinstance(parsed_message, websockets.ConnectionClosed):
            print("Connection closed.")
            return (account_code, None)

        if isinstance(parsed_message, dict):
            text_message: str = parsed_message["text"]
            binary_data: bytes = parsed_message["binary_data"]

            # Parse 'ACCOUNTCODE' value
            for item in text_message.split(";"):
                key, value = item.split("=")
                if key.strip() == accountcode_name:
                    account_code = value.strip()
                    break

            if account_code:
                print(
                    f"Received {accountcode_name}: {account_code} bytes: {len(binary_data)}"
                )
            else:
                print(f"No {accountcode_name} found in message.")
        else:
            print("Invalid message format.")

    except Exception as e:
        print(f"Error parsing message: {e}")
    return (account_code, binary_data)


def choose_target_port(account_code: str):
    # Some approaches are:
    # 0. Use load balancing. Too complex for this task.

    # 1. Use random and dictionary to store redirect ports, e.g:
    #   if account_code not in redirects:
    #       redirects[account_code] = redirect_ports[random.randint(0, len(redirect_ports)-1)]
    #   port = redirects[account_code]
    # But it takes additional time and memory, and should use random.seed(..) to be deterministic
    # It is also unknown based on task definition, how long redirection should be stored

    # 2. Use hash_code of string account_code (not int since it returns almost same value), e.g.:
    #   redirect_ports[hash(account_code)%len(redirect_ports)]
    # Deterministic, but not very efficient.

    # 3. Use separate instance of random.Random and seed it each time based on account_code, e.g.:
    #   def genr(i, n):
    #       xr.seed(i)
    #       return xr.randint(0,n-1)
    #   redirect_ports[genr(int(account_code), len(redirect_ports))]
    # Deterministic, but not very efficient.

    # 4. Use Modular arithmetic (current solution)
    # It is deterministic, efficient and simple, but...
    # could cause non-trivial issues for different targets count:
    # For example, if targets count is 10, and account_code has tailing zeros, it will return same port.
    # But for targets count 3, as in this task, divisibility by 3 depends on all digits of account_code,
    # and since no other conditions were specified in task, I chose this option:
    return redirect_ports[int(account_code) % len(redirect_ports)]


def get_config():
    parser = argparse.ArgumentParser(
        prog="websocket_redirect",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )

    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("-p", "--port", default="6001", help="Listening on port")
    parser.add_argument("--target-host", type=str, default="localhost")
    parser.add_argument(
        "-t",
        "--target-ports",
        nargs="+",
        default=[7001, 7002, 7003],
        help="Targets to redirect",
    )
    parser.add_argument("-v", "--verbose", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    config = vars(args)
    return config


async def main():
    async with serve(redirect, host, listen_port):
        await asyncio.Future()


if __name__ == "__main__":
    config = get_config()
    listen_port = config["port"]
    redirect_ports = config["target_ports"]
    host = config["host"]
    target_host = config["target_host"]
    accountcode_name = "ACCOUNTCODE"
    verbose: bool = config["verbose"]

    print(f"Listening port: {listen_port}")
    print(f"Redirecting to http ports: {redirect_ports}")
    asyncio.run(main())
