# terminal_displays.ps1
function testresults(){
    # Write-Host "`nin testresults"
    try {
        if ((Test-Path -Path "$($PWD)/setup.cfg" -PathType Leaf)){
            $found = ie "python -c 'from logunittest.logunittest import Coverage; Coverage()()' 2>&1"
            # Write-Host "cov found: $found"
            # $C = $found | Select-Object -Property Exception
            $C = $found | Select-Object -Property Exception
            $out = Out-String -InputObject $C -Width 100
            $text = $out.Split([Environment]::NewLine)
            $result = $text | Select-String -Pattern '(<@>)(.*)(<@>)' -CaseSensitive `
                            | foreach-object { $_.Matches[0].Groups[2].Value }
            $time, $stats = $result.split('!')
            $err = $stats   | Select-String -Pattern '(err:)(\d)' `
                            | foreach-object { $_.Matches[0].Groups[2].Value }
            $err = [int]$err
        }
        else{
            $time = $null
            $stats = $null
            $err = 0
        }
    }
    catch {
        $time = 'ERROR'
        $stats = 'stats not found'
        $err = 1
    }
    # ie "python digi_add_my_ip_to_trusted.py"
    return $time, $stats, $err
}

function display_stats() {
    $time, $stats, $err = ie testresults
    if ($stats -ne $NULL) {
        $branch = git rev-parse --abbrev-ref HEAD
        Write-Host(" | ") -NoNewline -foregroundcolor darkyellow
        Write-Host("COV:") -foregroundcolor white -NoNewline
        Write-Host(" $time ") -foregroundcolor darkblue -NoNewline
        if ($err -ne 0) {
            Write-Host($stats) -foregroundcolor red
        }
        elseif ($time -eq '{time}') {
            Write-Host($stats) -foregroundcolor gray
        }
        else {
            Write-Host($stats) -foregroundcolor green
        }
    }
    else {
        Write-Host(" | ") -NoNewline -foregroundcolor darkyellow
        Write-Host ("COV: ") -foregroundcolor white -NoNewline
        Write-Host ("<None>") -backgroundcolor darkgray -NoNewline
    }

}
