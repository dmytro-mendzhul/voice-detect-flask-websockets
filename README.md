# voice-detect-flask-websockets

## Simple Flask app for voice detection on WAV stream using silero-vad model + websockets load balancer

This is simple a proof-of-concept project made as a test task.

Scripts in order of running:

1. `split.py` - splits WAV files at `data` directory into 100ms frames and saves into corresponding folders. Could be run by `split.bat`.

2. `vsp_ws.py` - A WebSocket server that listens for packets from clients and resends data to one of HTTP servers depending on ACCOUNTCODE that is in the text part of the packet. Kinda load balancer. Batch file `vsp_ws.bat` starts it on port 6001.

3. `vsp_http.py` - A Flask HTTP server with one endpoint POST "/" that uses a neural network to detect voice in audio data. Batch file `vsp_http.bat` starts multiple instances on different ports: 7001, 7002, 7003.

4. `test_vsp_ws.py` - sends audio frames to WebSocket server. Batch file `test_vsp_ws.bat` starts separate processes for each audio sample. Should be run the last.

Structure of WebSocket message:
`{ "text": ACCOUNTCODE=1234", "binary_data": wav_data }`

### Output

The results of the voice detection (with/without) will be logged to files named `<`ACCOUNTCODE`>`.txt in the same folder as the scripts.
One row per batch (100ms audio frame) in the format:

`<`time`>` voice=`<`1 or 0 `>`, `<`http port`>`, `<`detection time`>`ms

- 1 - voice detected, 0 - no voice
- `<`detection time`>` - time in milliseconds taken by artificial neural network to process audio

Example of log file:

```
2023-01-20 13:44:44.123435 voice=0, 7001, 50ms
2023-01-20 13:44:44.123544 voice=1, 7001, 34ms
2023-01-20 13:44:44.123655 voice=1, 7001, 44ms
```

The following example shows how to send a packet with the ACCOUNTCODE 1691 and audio data that contains voice:

curl -X POST -H "Content-Type: application/json" -d '{"ACCOUNTCODE": "1691", "data": [1, 2, 3, 4, ...]}' http://localhost:6001/

The vsp_http.py script on port 7001 will then detect the voice in the audio data and log the result to the file 1691.txt. The log entry will contain the following information:

The time the HTTP request was received
Whether voice was detected in the packet
The port that the HTTP server is listening on
The total time it took to process the packet

### Requirements:

- Python 3.11+
- aiohttp
- flask
- silero-vad
- ...

### Installation:

pip install -r requirements.txt

## License

This project is licensed under the MIT License.
