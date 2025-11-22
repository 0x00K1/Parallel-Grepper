param(
    [string]$inputFile = "data/test_10mb.txt",
    [int]$topN = 100,
    [int]$threads = 4,
    [int]$runs = 3
)

Write-Host "Running synchronization mode tests: reduction, atomic, critical" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path results\parallel | Out-Null

$modes = @('reduction','atomic','critical')
foreach ($mode in $modes) {
    $outFile = "results/parallel/output_${($inputFile -replace 'data/','')}_${mode}.txt"
    Write-Host "\nMode: $mode" -ForegroundColor Yellow
    for ($i = 1; $i -le $runs; $i++) {
        Write-Host "  Run #$i..."
        & "build\parallel_counter.exe" $inputFile $outFile $topN $threads $mode
    }
}

Write-Host "Done. Results saved under results/parallel/" -ForegroundColor Green
