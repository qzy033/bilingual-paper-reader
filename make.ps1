param(
  [Parameter(Mandatory = $true)][string]$Pdf,     # 论文 PDF 路径
  [Parameter(Mandatory = $true)][string]$Slug,    # 目录名 / 论文 id
  [switch]$NoTranslate,                           # 只抽取，不翻译
  [switch]$Force,                                 # 重译已有译文
  [switch]$Package                                # 结束后打包 zip
)

# 一条龙：PDF -> 分节 -> 翻译 -> 术语表 -> 构建 -> 可选打包
# 用法:  .\make.ps1 -Pdf "C:\path\paper.pdf" -Slug my-paper -Package

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Need($cmd, $hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    Write-Host "缺少 $cmd，$hint" -ForegroundColor Red
    exit 1
  }
}

Need python "请先安装 Python 3.9+（并勾选 Add to PATH）"
python -c "import pymupdf" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "缺少 PyMuPDF，正在安装..." -ForegroundColor Yellow
  python -m pip install --quiet pymupdf
}

Write-Host "`n[1/4] 抽取 PDF 文本" -ForegroundColor Cyan
python tools/pdf_to_json.py $Pdf $Slug
if ($LASTEXITCODE -ne 0) { exit 1 }

if ($NoTranslate) {
  Write-Host "`n[2/4] 跳过翻译（-NoTranslate）" -ForegroundColor Yellow
} else {
  Write-Host "`n[2/4] 翻译 + 术语表（需要 OPENAI_API_KEY）" -ForegroundColor Cyan
  if (-not $env:OPENAI_API_KEY) {
    Write-Host "没有 OPENAI_API_KEY：先跑一次 --dry-run 看工作量，或加 -NoTranslate 自己译。" -ForegroundColor Yellow
    python tools/translate.py --slug $Slug --dry-run
    exit 2
  }
  $extra = @()
  if ($Force) { $extra += "--force" }
  python tools/translate.py --slug $Slug --with-terms @extra
  if ($LASTEXITCODE -ne 0) { exit 1 }
}

Write-Host "`n[3/4] 构建阅读器数据" -ForegroundColor Cyan
python build_paper.py
if ($LASTEXITCODE -ne 0) { exit 1 }

if ($Package) {
  Write-Host "`n[4/4] 打包" -ForegroundColor Cyan
  python tools/package.py
}

Write-Host "`n完成：打开 reader/index.html 就能读。" -ForegroundColor Green
