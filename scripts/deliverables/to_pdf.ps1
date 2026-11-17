# Update Word fields (contents, lists, captions) and export the report and slides to PDF with Microsoft Office.
param([string]$Root = "D:\heritage3d\Deliverables")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
Get-ChildItem "$Root\Report\*.docx" | ForEach-Object {
  $d = $word.Documents.Open($_.FullName)
  $d.Fields.Update() | Out-Null
  foreach ($t in $d.TablesOfContents) { $t.Update() }
  foreach ($t in $d.TablesOfFigures) { $t.Update() }
  $d.Fields.Update() | Out-Null
  $d.Save()
  $d.ExportAsFixedFormat(($_.FullName -replace '\.docx$', '.pdf'), 17)
  "pages: " + $d.ComputeStatistics(2) + "  " + $_.Name
  $d.Close()
}
$word.Quit()
$ppt = New-Object -ComObject PowerPoint.Application
Get-ChildItem "$Root\Presentation\*.pptx", "$Root\Poster\*.pptx" -ErrorAction SilentlyContinue | ForEach-Object {
  $p = $ppt.Presentations.Open($_.FullName, $true, $false, $false)
  $p.SaveAs(($_.FullName -replace '\.pptx$', '.pdf'), 32)
  "slides: " + $p.Slides.Count + "  " + $_.Name
  $p.Close()
}
$ppt.Quit()
