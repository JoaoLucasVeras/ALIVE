$docx = 'C:\Users\Joaol\Documents\ChatGPT\ALIVE\ALIVE_Comprehensive_Project_Blueprint.docx'
$renderDir = 'C:\Users\Joaol\Documents\ChatGPT\ALIVE\tmp\blueprint_render'
$pdf = Join-Path $renderDir 'ALIVE_Comprehensive_Project_Blueprint.pdf'
New-Item -ItemType Directory -Force -Path $renderDir | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docx, $false, $true)
    $doc.ExportAsFixedFormat($pdf, 17)
    $doc.Close($false)
}
finally {
    $word.Quit()
}
Get-Item -LiteralPath $pdf | Select-Object FullName, Length, LastWriteTime
