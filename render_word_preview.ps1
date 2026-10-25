$ErrorActionPreference = 'Stop'
$inputDoc = 'C:\Users\Joaol\Documents\ChatGPT\ALIVE\Trait_Graph_Coevolution_Project_Brief.docx'
$outputDir = 'C:\Users\Joaol\Documents\ChatGPT\ALIVE\rendered_brief'
$outputPdf = Join-Path $outputDir 'Trait_Graph_Coevolution_Project_Brief.pdf'
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
