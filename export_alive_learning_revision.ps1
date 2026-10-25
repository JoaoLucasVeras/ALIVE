$ErrorActionPreference = 'Stop'
$inputDoc = 'C:\Users\Joaol\Documents\ChatGPT\ALIVE\ALIVE_Learning_and_Evolution_Revised_Proposal.docx'
$outputPdf = 'C:\Users\Joaol\Documents\ChatGPT\ALIVE\output\pdf\ALIVE_Learning_and_Evolution_Revised_Proposal.pdf'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPdf) | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $document = $word.Documents.Open($inputDoc, $false, $true)
    $document.ExportAsFixedFormat($outputPdf, 17)
    $document.Close($false)
}
finally { $word.Quit() }
Write-Output $outputPdf
