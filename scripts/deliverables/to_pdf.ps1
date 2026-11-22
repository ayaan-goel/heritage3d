# Update Word fields (contents, lists, captions) and export the report to PDF with Microsoft Word.
# Slides and posters are exported only with -Slides, and only when PowerPoint is not already running,
# so a presentation someone is editing is never touched and their PowerPoint window is never closed.
param([string]$Root = "D:\heritage3d\Deliverables", [switch]$Slides)

$wordRunning = [bool](Get-Process WINWORD -ErrorAction SilentlyContinue)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
Get-ChildItem "$Root\Report\*.docx" | Where-Object { $_.Name -notlike '~$*' } | ForEach-Object {
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
if (-not $wordRunning) { $word.Quit() }

if ($Slides) {
  if (Get-Process POWERPNT -ErrorAction SilentlyContinue) {
    "PowerPoint is open: slides and posters NOT exported (close PowerPoint and rerun with -Slides)."
  } else {
    $ppt = New-Object -ComObject PowerPoint.Application
    Get-ChildItem "$Root\Presentation\*.pptx", "$Root\Poster\*.pptx" -ErrorAction SilentlyContinue | ForEach-Object {
      $p = $ppt.Presentations.Open($_.FullName, $true, $false, $false)
      $p.SaveAs(($_.FullName -replace '\.pptx$', '.pdf'), 32)
      "slides: " + $p.Slides.Count + "  " + $_.Name
      $p.Close()
    }
    $ppt.Quit()
  }
}
