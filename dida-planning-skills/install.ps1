param(
  [string]$Destination = (Join-Path $HOME '.agents\skills'),
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$Installer = Join-Path $PSScriptRoot 'install.py'
$Arguments = @($Installer, '--destination', $Destination)
if ($DryRun) { $Arguments += '--dry-run' }
& python @Arguments
if ($LASTEXITCODE -ne 0) { throw "Dida installation failed with exit code $LASTEXITCODE" }
