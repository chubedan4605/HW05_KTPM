param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Load","Stress","Spike","Soak")]
    [string]$Scenario
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$low = $Scenario.ToLower()
$jmx = Join-Path $Root "testplans\23120279_${Scenario}_20261122.jmx"
$resDir = Join-Path $Root "results\$low"
$jtl = Join-Path $resDir "23120279_${Scenario}_20261122.jtl"
$htmlDir = Join-Path $resDir "html"
$monCsv = Join-Path $Root "evidence\mon\${Scenario}_resources.csv"
$consoleLog = Join-Path $Root "evidence\mon\${Scenario}_jmeter_console.log"
$dbFile = Join-Path (Split-Path -Parent $Root) "eshop-sut\backend\database.sqlite"

# 1. Verify backend is reachable on localhost:3000
try {
    $null = Invoke-WebRequest -Uri "http://localhost:3000/api/products" -UseBasicParsing -TimeoutSec 3
} catch {
    Write-Error "Backend chua chay tai http://localhost:3000! Hay khoi dong 'node server.js' truoc."
    exit 1
}

# 2. Reset account lockout + clean old results
node scripts/reset_lockout.js
Remove-Item -Recurse -Force $htmlDir -ErrorAction SilentlyContinue
Get-ChildItem $resDir -Filter "23120279_${Scenario}_20261122.jtl*" -ErrorAction SilentlyContinue | Remove-Item -Force

# 3. Start background Windows resource monitor for node.exe (every 5s)
$nodePid = (Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1).OwningProcess
$monJob = Start-Job -ScriptBlock {
    param($pidToWatch, $csvPath, $dbPath)
    "ts,elapsed_s,cpu_pct_1core,rss_mb,load1,db_mb,orders" | Set-Content -Path $csvPath -Encoding UTF8
    $t0 = Get-Date
    $prevCpu = 0.0
    $prevT = $t0
    if ($pidToWatch) {
        $p = Get-Process -Id $pidToWatch -ErrorAction SilentlyContinue
        if ($p) { $prevCpu = $p.CPU }
    }
    while ($true) {
        Start-Sleep -Seconds 5
        $now = Get-Date
        $dt = ($now - $prevT).TotalSeconds
        $el = [math]::Round(($now - $t0).TotalSeconds, 1)
        $cpuPct = 0.0; $rssMb = 0.0
        if ($pidToWatch) {
            $p = Get-Process -Id $pidToWatch -ErrorAction SilentlyContinue
            if ($p) {
                $curCpu = $p.CPU
                if ($dt -gt 0) { $cpuPct = [math]::Round((($curCpu - $prevCpu) / $dt) * 100.0, 1) }
                $prevCpu = $curCpu
                $rssMb = [math]::Round($p.WorkingSet64 / 1MB, 1)
            }
        }
        $prevT = $now
        $dbMb = if (Test-Path $dbPath) { [math]::Round((Get-Item $dbPath).Length / 1MB, 3) } else { 0.0 }
        "$($now.ToString('HH:mm:ss')),$el,$cpuPct,$rssMb,0,$dbMb,0" | Add-Content -Path $csvPath -Encoding UTF8
    }
} -ArgumentList $nodePid, $monCsv, $dbFile

Write-Host "=== Running $Scenario (node PID=$nodePid) ===" -ForegroundColor Cyan
Write-Host "JMX: $jmx"
Write-Host "JTL: $jtl"

try {
    jmeter -n -t $jmx -l $jtl -e -o $htmlDir 2>&1 | Tee-Object -FilePath $consoleLog
} finally {
    Stop-Job $monJob -ErrorAction SilentlyContinue
    Remove-Job $monJob -Force -ErrorAction SilentlyContinue
}

Write-Host "=== Done $Scenario! HTML report: $htmlDir\index.html ===" -ForegroundColor Green
