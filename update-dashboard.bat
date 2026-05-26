@echo off
chcp 65001 > nul
echo [update-dashboard] Starting...

python src\generate_dashboard.py sample-data\
if errorlevel 1 (
    echo [ERROR] generate_dashboard.py failed
    pause
    exit /b 1
)

copy /Y dashboard\index.html docs\index.html > nul
echo [update-dashboard] Copied dashboard to docs\

git add docs\index.html dashboard\index.html
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Update dashboard %date:~6,4%%date:~3,2%%date:~0,2%"
    git push
    echo [update-dashboard] Pushed to GitHub
) else (
    echo [update-dashboard] No changes to commit
)

echo [update-dashboard] Done.
pause
