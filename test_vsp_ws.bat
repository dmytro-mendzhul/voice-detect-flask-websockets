call venv\Scripts\activate.bat
start "chunks_sample1" py test_vsp_ws.py -p 6001 -d data/chunks_sample1
timeout 1
start "chunks_sample2" py test_vsp_ws.py -p 6001 -d data/chunks_sample2
timeout 1
start "chunks_sample3" py test_vsp_ws.py -p 6001 -d data/chunks_sample3
timeout 1
start "chunks_en_example" py test_vsp_ws.py -p 6001 -d data/chunks_en_example
