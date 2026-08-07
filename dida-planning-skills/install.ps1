param(
  [string]$Destination = (Join-Path $HOME ".agents\skills")
)

$ErrorActionPreference = "Stop"
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$Items = @(
  "dida-cli",
  "dida-task-capture",
  "dida-task-breakdown",
  "dida-task-estimator",
  "dida-daily-planner",
  "dida-task-progress",
  "dida-weekly-review",
  "dida-planning-profile",
  "dida-planning-memory",
  "dida-planning-core"
)

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
foreach ($Item in $Items) {
  $From = Join-Path $Source $Item
  $To = Join-Path $Destination $Item
  if (Test-Path $To) { Remove-Item -Recurse -Force $To }
  Copy-Item -Recurse -Force $From $To
  Write-Host "Installed $Item -> $To"
}

$Validator = Join-Path $Destination "dida-planning-core\scripts\package_validator.py"
python $Validator --root $Source
Write-Host "Done. Restart Codex only if /skills does not refresh automatically."
