import argparse
from datetime import datetime
from flask import Flask, request
from model.voice_detect import VoiceDetect

app = Flask(__name__)


@app.route("/", methods=["POST"])
async def receive_post_request():
    receive_time = datetime.utcnow()
    try:
        account_code = request.headers.get(accountcode_name)
        binary_data = request.data
        print(f"Received {len(binary_data)} bytes from {account_code}")

        speech_prob = await voice_detect_model.voice_prob(binary_data)
        voice = None
        if speech_prob is None:
            print("Voice detection failed.")
        else:
            voice = 1 if speech_prob > 0.5 else 0
        
        processed_time = datetime.utcnow()
        processing_time_mcs = (processed_time - receive_time).microseconds
        processing_time_ms = int(round(processing_time_mcs / 1000, 0))

        log_record = f"{processed_time} voice={voice}, {port}, {processing_time_ms}ms"
        log_to_file(account_code, log_record)

        if verbose:
            print(
                f"{accountcode_name}={account_code} - {log_record} ({processing_time_mcs}mcs)"
            )

        return "OK"

    except Exception as e:
        print(f"Error processing request: {e}\n\n\n")
        return "Error processing request."


def log_to_file(account_code, message):
    """Logs a message to a file with the specified ID.

    Args:
        id (str): The ID of the file to log to.
        message (str): The message to log.
    """
    with open(f"{account_code}.txt", "a") as file:
        file.write(f"{message}\n")


def get_config():
    parser = argparse.ArgumentParser(
        prog="websocket_redirect",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )

    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("-p", "--port", default="7001", help="Listening on port")
    parser.add_argument("-v", "--verbose", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    config = vars(args)
    return config


if __name__ == "__main__":
    voice_detect_model = VoiceDetect(num_threads=1, use_onnx=True)
    config = get_config()
    host: str = config["host"]
    port: str = config["port"]
    verbose: bool = config["verbose"]
    accountcode_name = "ACCOUNTCODE"
    print(f"Listening on {host}:{port}")

    from waitress import serve

    serve(app, host=host, port=port)
