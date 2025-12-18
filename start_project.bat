@echo off
echo Starting Job Portal Application...
echo.
echo Opening Backend Terminal...
start "Django Backend" cmd /k "cd backend && start_backend.bat"
echo.
echo Opening Frontend Terminal...
start "React Frontend" cmd /k "cd frontend && start_frontend.bat"
echo.
echo Both servers are starting in separate terminals.
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:3000
pause