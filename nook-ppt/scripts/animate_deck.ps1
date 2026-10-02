# 用 PowerPoint 执行零件登记的动效计划（*.anim.json）：页面切换淡入；元素按计划出现（自动播放，不用点击）
param([string]$In, [string]$Out, [string]$Plan)
$ErrorActionPreference = "Stop"
$steps = Get-Content -Raw -Encoding UTF8 $Plan | ConvertFrom-Json
$transId = @{ fade = 3849; morph = 3954 }
$effId = @{ fade = 10; zoom = 53; wipe = 22; appear = 1 }
$trig = @{ after = 3; with = 2; click = 1; beat = 1 }
$dirId = @{ left = 4; right = 2; up = 1; down = 3 }
$app = New-Object -ComObject PowerPoint.Application
try {
  $pres = $app.Presentations.Open($In, $false, $false, $false)
  $report = @(); $miss = @()
  foreach ($s in $pres.Slides) {
    $tr = $steps | Where-Object { $_.slide -eq $s.SlideIndex -and $_.transition }
    $kind = if ($tr) { $tr.transition } else { 'fade' }
    $s.SlideShowTransition.EntryEffect = $transId[$kind]          # 淡入 / 平滑
    $s.SlideShowTransition.Duration = if ($tr) { [double]$tr.dur } else { 0.6 }
    $byName = @{}
    foreach ($sh in $s.Shapes) { $byName[$sh.Name] = $sh }
    $seq = $s.TimeLine.MainSequence
    foreach ($a in ($steps | Where-Object { $_.slide -eq $s.SlideIndex -and $_.name })) {
      if (-not $byName.ContainsKey($a.name)) { $miss += "slide $($s.SlideIndex): $($a.name)"; continue }
      $e = $seq.AddEffect($byName[$a.name], $effId[$a.effect], 0, $trig[$a.trigger])
      $e.Timing.Duration = [double]$a.dur
      if ([double]$a.delay -gt 0) { $e.Timing.TriggerDelayTime = [double]$a.delay }
      if ($a.dir -and $a.effect -eq "wipe") { $e.EffectParameters.Direction = $dirId[$a.dir] }
    }
    $report += "slide $($s.SlideIndex): effects=$($seq.Count)"
  }
  $pres.SaveAs($Out, 24)
  $pres.Close()
  $report
  if ($miss.Count) { "找不到形状：" ; $miss }
} finally { $app.Quit() }
