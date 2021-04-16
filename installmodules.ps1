'finding modules'
py findmodules.py
'getting modules'
$modules = Get-Content modules.txt
'installing modules'
function ForBegin($mod) {
    "Upgrading pip"
    pip install --upgrade pip
    $mod | ForEach-Object -Process {
        "Downloading $_"
        pip download $_
    }
}
$modules | ForEach-Object -Begin {ForBegin($modules)} -Process {
    "installing $_"
    pip install $_ -U --no-index
}
