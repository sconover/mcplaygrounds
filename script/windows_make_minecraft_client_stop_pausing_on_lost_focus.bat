powershell -Command "(gc \"%APPDATA%\.minecraft\options.txt\") -replace 'pauseOnLostFocus:true', 'pauseOnLostFocus:false' | Out-File \"%APPDATA%\.minecraft\options.txt\""
