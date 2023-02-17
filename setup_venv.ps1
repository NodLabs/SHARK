<#
.SYNOPSIS
  A script to update and install the SHARK runtime and its dependencies.

.DESCRIPTION
  This script updates and installs the SHARK runtime and its dependencies.
  It checks the Python version installed and installs any required build
  dependencies into a Python virtual environment.
  If that environment does not exist, it creates it.
  
.PARAMETER update-src
  updates to latest version from git .\source

.PARAMETER force
  removes and recreates venv to force update all dependencies
  
.EXAMPLE
  .\setup_venv.ps1 --force

.EXAMPLE
  .\setup_venv.ps1 --update-src

.INPUTS
  None

.OUTPUTS
  None

.NOTES
  Version        1.0
  Author         powderluv, xzuyn
  Creation Date  2023-02-17
  PurposeChange Initial script development

#>

param([string]$arguments)

if ($arguments -eq "--update-src"){
	git pull
}

if ($arguments -eq "--force"){
	if (Test-Path env:VIRTUAL_ENV) {
        Write-Host "deactivating..."
        Deactivate
    }
    
    if (Test-Path .\shark.venv\) {
        Write-Host "removing and recreating venv..."
        Remove-Item .\shark.venv -Force -Recurse
        if (Test-Path .\shark.venv\) {
            Write-Host 'could not remove .\shark-venv - please try running ".\setup_venv.ps1 --force" again!'
            break
        }
    }
}


#Write-Host "Installing python"

#Start-Process winget install Python.Python.3.10 '/quiet InstallAllUsers=1 PrependPath=1' -wait -NoNewWindow

#Write-Host "python installation completed successfully"

#Write-Host "Reload environment variables"
#$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
#Write-Host "Reloaded environment variables"


# redirect stderr into stdout
$p = &{python -V} 2>&1
# check if an ErrorRecord was returned
$version = if($p -is [System.Management.Automation.ErrorRecord])
{
    # grab the version string from the error message
    $p.Exception.Message
}
else
{
    # otherwise return as is
    $p
}

Write-Host "Python version found is"
Write-Host $p
if ($p -notlike "*3.11*")
{
    Write-Host "Please install Python 3.11 and try again"
    break
}

Write-Host "Installing Build Dependencies"
py -3.11 -m venv .\shark.venv\
.\shark.venv\Scripts\activate
python -m pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
pip install --pre torch-mlir torch torchvision --extra-index-url https://download.pytorch.org/whl/nightly/cpu -f https://llvm.github.io/torch-mlir/package-index/
pip install --upgrade -f https://nod-ai.github.io/SHARK-Runtime/pip-release-links.html iree-compiler iree-runtime
Write-Host "Building SHARK..."
pip install -e . -f https://llvm.github.io/torch-mlir/package-index/ -f https://nod-ai.github.io/SHARK-Runtime/pip-release-links.html
Write-Host "Build and installation completed successfully"
Write-Host "Source your venv with ./shark.venv/Scripts/activate"
