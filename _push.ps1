$ErrorActionPreference = "Stop"
$repo = "E:\project\dsh\out\bilingual-paper-reader"
Set-Location $repo

# 1) 取回已保存的 GitHub 凭据（不打印 secret）
$input = "protocol=https`nhost=github.com`n`n"
$out = $input | git credential fill 2>$null
$user = ($out | Select-String "^username=").ToString() -replace "^username=",""
$pass = ($out | Select-String "^password=").ToString() -replace "^password=",""
Write-Output ("credential user=" + $user + " tokenLen=" + $pass.Length)

$headers = @{ Authorization = "token $pass"; "User-Agent" = "dsh-agent"; Accept = "application/vnd.github+json" }

# 2) 这个 token 是谁
try {
  $me = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -TimeoutSec 30
  Write-Output ("api login=" + $me.login + " name=" + $me.name)
} catch {
  Write-Output ("API-FAILED: " + $_.Exception.Message)
  exit 2
}

# 3) 仓库是否已存在
$name = "bilingual-paper-reader"
$exists = $true
try {
  $null = Invoke-RestMethod -Uri "https://api.github.com/repos/$($me.login)/$name" -Headers $headers -TimeoutSec 30
} catch {
  if ($_.Exception.Response.StatusCode.value__ -eq 404) { $exists = $false }
}
Write-Output ("repo exists=" + $exists)

if (-not $exists) {
  $body = @{
    name        = $name
    description = "Dependency-free bilingual paper reader: original on the left, translation on the right, sentence-aligned. Ships the tool + one original demo paper, no third-party full text."
    private     = $false
    has_issues  = $true
    has_wiki    = $false
    license_template = "mit"
  } | ConvertTo-Json
  try {
    $created = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json; charset=utf-8" -TimeoutSec 30
    Write-Output ("created: " + $created.html_url)
  } catch {
    Write-Output ("CREATE-FAILED: " + $_.Exception.Message)
    exit 3
  }
}

$remoteUrl = "https://github.com/$($me.login)/$name.git"
Write-Output ("remote: " + $remoteUrl)
