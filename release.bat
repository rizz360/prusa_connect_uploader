@echo off
setlocal enabledelayedexpansion

REM === Configuration ===
set PLUGIN_INIT=octoprint_prusa_connect_uploader\__init__.py
set FILES_TO_UPDATE=setup.py %PLUGIN_INIT%
set ZIP_PREFIX=prusa_connect_uploader

REM === Extract current version from your __init__.py ===
for /f "usebackq tokens=2 delims== " %%V in (`
  findstr /c:"__plugin_version__ =" "%PLUGIN_INIT%"
`) do (
  set version=%%~V
  set version=!version:"=!
)

if not defined version (
  echo ❌ Could not find __plugin_version__ in %PLUGIN_INIT%
  exit /b 1
)

REM === Split into major.minor.patch ===
for /f "tokens=1-3 delims=." %%A in ("!version!") do (
  set major=%%A
  set minor=%%B
  set patch=%%C
)

REM === Decide bump type ===
set bump=%1
if /i "%bump%"==""    set bump=patch
if /i "%bump%"=="patch" (
  set /a patch+=1
) else if /i "%bump%"=="minor" (
  set /a minor+=1
  set patch=0
) else if /i "%bump%"=="major" (
  set /a major+=1
  set minor=0
  set patch=0
) else (
  echo ❌ Invalid bump type "%bump%". Use major, minor, or patch.
  exit /b 1
)

set new_version=%major%.%minor%.%patch%
echo Bumping version %version% → %new_version%

REM === Update version in files ===
for %%F in (%FILES_TO_UPDATE%) do (
  powershell -Command ^
    "(Get-Content '%%F') -replace '__plugin_version__ = \"[0-9]+\.[0-9]+\.[0-9]+\"', '__plugin_version__ = \"%new_version%\"' | Set-Content '%%F'"
  powershell -Command ^
    "(Get-Content '%%F') -replace 'version\s*=\s*\"[0-9]+\.[0-9]+\.[0-9]+\"', 'version = \"%new_version%\"' | Set-Content '%%F'"
)

REM === Git commit & tag ===
git add %FILES_TO_UPDATE%
git commit -m "Release v%new_version%"
git tag v%new_version%
git push
git push origin v%new_version%

REM === Create ZIP ===
git archive --format=zip --output %ZIP_PREFIX%-%new_version%.zip v%new_version%

echo.
echo ✅ Released v%new_version% → %ZIP_PREFIX%-%new_version%.zip
echo.
pause
