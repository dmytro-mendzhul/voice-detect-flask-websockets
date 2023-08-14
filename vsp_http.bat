call venv\Scripts\activate.bat
start "HTTP 7001" cmd /k py vsp_http.py -p 7001 -v
timeout 5
start "HTTP 7002" cmd /k py vsp_http.py -p 7002 -v
timeout 5
start "HTTP 7003" cmd /k py vsp_http.py -p 7003 -v
