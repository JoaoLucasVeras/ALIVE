$ErrorActionPreference = 'Stop'
$inputDoc = 'C:\Users\Joaol\Documents\ChatGPT\ALIVE\ALIVE_Project_Proposal.docx'
$outputDir = 'C:\Users\Joaol\Documents\ChatGPT\ALIVE\rendered_alive'
$outputPdf = Join-Path $outputDir 'ALIVE_Project_Proposal.pdf'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($inputDoc, $false, $true)
    $doc.ExportAsFixedFormat($outputPdf, 17)
    $doc.Close($false)
}
finally {
    $word.Quit()
}
Write-Output $outputPdf
