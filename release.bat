@echo off
setlocal ENABLEDELAYEDEXPANSION

REM === Step 0: Configuration ===
set FILES_TO_UPDATE=setup.py octoprint_prusa_connect_uploader\__init__.py
set ZIP_PREFIX=prusa_connect_uploader

REM === Step 1: Extract current version from setup.py ===
for /f "tokens=2 delims== " %%v in ('findstr /r /c:"^plugin_version *= *\"" setup.py') do (
    set version=%%v
    set version=!version:"=!
)

REM === Step 2: Parse version into major.minor.patch ===
for /f "tokens=1-3 delims=." %%a in ("!version!") do (
    set major=%%a
    set minor=%%b
    set patch=%%c
)

REM === Step 3: Determine bump type ===
set arg=%1
if "%arg%"=="" set arg=patch

if /i "%arg%"=="patch" (
    set /a patch=patch + 1
) else if /i "%arg%"=="minor" (
    set /a minor=minor + 1
    set patch=0
) else if /i "%arg%"=="major" (
    set /a major=major + 1
    set minor=0
    set patch=0
) else (
    echo Invalid argument. Use patch, minor, or major.
    exit /b 1
)

REM === Step 4: Build new version string ===
set new_version=%major%.%minor%.%patch%

echo.
echo Bumping version: %version% → %new_version%
echo.

REM === Step 5: Replace version in files ===
for %%f in (%FILES_TO_UPDATE%) do (
    powershell -Command "(Get-Content %%f) -replace 'plugin_version\s*=\s*\".*?\"', 'plugin_version = \"%new_version%\"' | Set-Content %%f"
    powershell -Command "(Get-Content %%f) -replace '__plugin_version__\s*=\s*\".*?\"', '__plugin_version__ = \"%new_version%\"' | Set-Content %%f"
)

REM === Step 6: Commit and tag ===
git add %FILES_TO_UPDATE%
git commit -m "Release v%new_version%"
git tag %new_version%
git push
git push origin %new_version%

REM === Step 7: Create ZIP archive ===
git archive --format zip --output %ZIP_PREFIX%-%new_version%.zip %new_version%

echo.
echo ✅ Release v%new_version% created and zipped!
echo → Archive: %ZIP_PREFIX%-%new_version%.zip
echo.

endlocal
pause
