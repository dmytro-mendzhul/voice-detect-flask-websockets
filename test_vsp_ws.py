import argparse
import asyncio
from datetime import datetime
import os
import random
import websockets


async def send_wav_chunks(
    chunks_directory: str, host: str, port: int, accountcode: int
):
    url = f"ws://{host}:{port}"
    async with websockets.connect(url) as websocket:
        for filename in os.listdir(chunks_directory):
            if filename.endswith(".wav"):
                print(f"sending {filename}")
                full_path = os.path.join(chunks_directory, filename)
                with open(full_path, "rb") as wav_file:
                    wav_data = wav_file.read()

                message = {
                    "text": f"{accountcode_name}={accountcode}",
                    "binary_data": wav_data,
                }

                await websocket.send(str(message))
                print(
                    f"Sent {filename} to server {url} {accountcode_name}={accountcode}"
                )
                resp = await websocket.recv()
                if resp != "OK":
                    print(f"closing connection due to response: {resp}")
                    await close_connection(websocket)
                    break
                await asyncio.sleep(5 / 1000)
        
        await close_connection(websocket)
        print("Done")


async def close_connection(websocket):
    try:
        await websocket.close()
        print("connection closed")
    except Exception as e:
        print(f"exception om websocket.close(): {e}")
    finally:
        print(f"closed")


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, default="data/chunks_sample1")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("-p", "--port", type=int, default=6001)

    args = parser.parse_args()
    config = vars(args)
    return config


if __name__ == "__main__":
    config = get_config()

    dir = config["directory"]
    send_to_host = config["host"]
    send_to_port = config["port"]
    seed = datetime.now().timestamp() - hash(dir)
    random.seed(seed)
    accountcode = random.randint(1, 2000)
    accountcode_name = "ACCOUNTCODE"

    print(
        f"Sending chunks to {send_to_host}:{send_to_port} {accountcode_name}: {accountcode} Chunks dir: {dir}"
    )

    asyncio.get_event_loop().run_until_complete(
        send_wav_chunks(dir, send_to_host, send_to_port, accountcode)
    )
