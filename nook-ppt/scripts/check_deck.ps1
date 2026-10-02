# 用 PowerPoint 自己打开 PPTX：逐页导出 PNG，并检查每个文字容器里文字的实际高度是否超出容器
param([string]$Pptx, [string]$OutDir, [string]$Pdf = "")
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force $OutDir | Out-Null
$app = New-Object -ComObject PowerPoint.Application
try {
  $pres = $app.Presentations.Open($Pptx, $true, $false, $false)
  $issues = @(); $n = 0
  function Check($sh, $idx) {
    $res = @()
    if ($sh.Type -eq 6) { foreach ($g in $sh.GroupItems) { $res += Check $g $idx } ; return $res }
    if ($sh.HasTable) {
      $res += [pscustomobject]@{slide=$idx; name=$sh.Name; kind="table"; top=[math]::Round($sh.Top,1); h=[math]::Round($sh.Height,1); bottom=[math]::Round($sh.Top+$sh.Height,1); over=$false}
      return $res
    }
    if ($sh.Rotation -ne 0 -and ($sh.Rotation % 180) -ne 0) { return $res }      # 旋转的文本框（如矩阵纵轴）PowerPoint 会把宽高量反，不检查
    if ($sh.HasTextFrame -and $sh.TextFrame2.HasText) {
      $tf = $sh.TextFrame2
      $avail = $sh.Height - $tf.MarginTop - $tf.MarginBottom
      $availw = $sh.Width - $tf.MarginLeft - $tf.MarginRight
      $bh = $tf.TextRange.BoundHeight; $bw = $tf.TextRange.BoundWidth
      $over = ($bh -gt $avail + 1.0) -or ($bw -gt $availw + 24.0)      # 宽度容差 24pt：标点悬挂会向外多出一个字，落在内边距里
      $res += [pscustomobject]@{slide=$idx; name=$sh.Name; kind="text"; boundH=[math]::Round($bh,1); availH=[math]::Round($avail,1); boundW=[math]::Round($bw,1); availW=[math]::Round($availw,1); over=$over; top=[math]::Round($sh.Top,1)}
    }
    return $res
  }
  $all = @()
  foreach ($s in $pres.Slides) {
    $n++
    $s.Export((Join-Path $OutDir ("slide_{0:D2}.png" -f $n)), "PNG", 1920, 1080)
    foreach ($sh in $s.Shapes) { $all += Check $sh $n }
  }
  $all | ConvertTo-Json -Depth 3 | Set-Content -Encoding UTF8 (Join-Path $OutDir "check.json")
  $bad = $all | Where-Object { $_.over }
  "slides=$n shapes=$($all.Count) overflow=$(@($bad).Count)"
  $bad | Format-Table -AutoSize | Out-String
  if ($Pdf) { $pres.SaveAs($Pdf, 32); "pdf=$Pdf" }
  $pres.Close()
} finally { $app.Quit() }
