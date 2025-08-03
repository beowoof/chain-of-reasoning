# --- 1. Check and Start Ollama ---
Write-Host "Checking if Ollama service is available..."
# Try to list models. If it fails, the service is likely down.
if (-not (ollama list 2>$null)) {
    Write-Host "Ollama service not responding. Starting it in the background..."
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Write-Host "Waiting for Ollama to initialize..." -NoNewline
    
    do {
        Start-Sleep -Seconds 1
        Write-Host "." -NoNewline
    } until (ollama list 2>$null)
    
    Write-Host "`nOllama is ready."
} else {
    Write-Host "Ollama is running."
}

# --- 2. Check for Ollama Models ---
Write-Host "Checking for required Ollama models..."

# Check for llama3:instruct
if (-not (ollama list | Select-String "llama3:instruct")) {
    Write-Host "'llama3:instruct' model not found. Pulling it now..."
    ollama pull llama3:instruct
} else {
    Write-Host "'llama3:instruct' model found."
}

# Check for mxbai-embed-large:latest
if (-not (ollama list | Select-String "mxbai-embed-large:latest")) {
    Write-Host "'mxbai-embed-large:latest' model not found. Pulling it now..."
    ollama pull mxbai-embed-large:latest
} else {
    Write-Host "'mxbai-embed-large:latest' model found."
}

# --- 3. Kill Existing Backend Process (if any) ---
Write-Host "Checking for existing process on port 8000..."
$existingProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($existingProcess) {
    Write-Host "Process found on port 8000. Terminating it..."
    Stop-Process -Id $existingProcess.OwningProcess -Force
    Start-Sleep -Seconds 1
}

# --- 4. Set Environment Variables ---
Write-Host "Setting environment variables..."
# Ensure the environment variable for Tavily API key is set
if (-not $env:TAVILY_API_KEY) {
    Write-Host "TAVILY_API_KEY is not set. Please set it before running this script." -ForegroundColor Red
    exit 1
}

# --- 5. Start FastAPI Backend ---
Write-Host "Starting FastAPI backend in the background..."
# Run from the project root so Python can find the package 'src'
$backend = Start-Process -FilePath "poetry" -ArgumentList "run", "uvicorn", "src.backend.main:app", "--reload" -PassThru -WindowStyle Hidden

# --- 6. Wait for Backend to be Ready ---
Write-Host "Waiting for backend to be ready..." -NoNewline
do {
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline
    $testConnection = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
} until ($testConnection.TcpTestSucceeded)

Write-Host "`nBackend is ready!"

# --- 7. Start Streamlit Frontend ---
Write-Host "Starting Streamlit frontend..."
# Run from the project root
try {
    poetry run streamlit run src/frontend/app.py
} finally {
    # Cleanup when the script ends
    if ($backend) {
        Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    }
    # Find and stop any remaining uvicorn or streamlit processes
    Get-Process -Name *uvicorn*, *streamlit* -ErrorAction SilentlyContinue | Stop-Process -Force
}
