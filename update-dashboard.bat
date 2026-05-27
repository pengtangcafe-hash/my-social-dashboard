@echo off
chcp 65001 > nul
echo [update-dashboard] Starting...

:: Step 1: Regenerate dashboard from latest CSV data
python src\generate_dashboard.py sample-data\
if errorlevel 1 (
    echo [ERROR] generate_dashboard.py failed
    pause
    exit /b 1
)
echo [update-dashboard] Dashboard generated.

:: Step 2: Inject dynamic data constants into dashboard HTML
echo [update-dashboard] Injecting data constants...

python src\posting_time_analyzer.py inject dashboard\index.html
if errorlevel 1 echo [WARNING] posting_time_analyzer inject failed (continuing...)

python src\update_logger.py inject dashboard\index.html
if errorlevel 1 echo [WARNING] update_logger inject failed (continuing...)

python src\competitor_tracker.py inject dashboard\index.html
if errorlevel 1 echo [WARNING] competitor_tracker inject failed (continuing...)

python src\goal_tracker.py inject dashboard\index.html
if errorlevel 1 echo [WARNING] goal_tracker inject failed (continuing...)

python src\monthly_trend.py inject dashboard\index.html
if errorlevel 1 echo [WARNING] monthly_trend inject failed (continuing...)

python src\content_category_analyzer.py inject dashboard\index.html
if errorlevel 1 echo [WARNING] content_category_analyzer inject failed (continuing...)

python src\ad_tracker.py inject dashboard\index.html
if errorlevel 1 echo [WARNING] ad_tracker inject failed (continuing...)

echo [update-dashboard] All constants injected.

:: Step 3: Copy to docs/ for GitHub Pages
copy /Y dashboard\index.html docs\index.html > nul
echo [update-dashboard] Copied to docs\

:: Step 4: Commit and push
git add docs\index.html dashboard\index.html
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Update dashboard %date:~6,4%%date:~3,2%%date:~0,2%"
    git push
    echo [update-dashboard] Pushed to GitHub Pages.
) else (
    echo [update-dashboard] No changes to commit.
)

echo [update-dashboard] Done!
pause
