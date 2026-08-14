param(
    [Parameter(Mandatory=$true)]
    [string]$WavPath,
    [Parameter(Mandatory=$true)]
    [string]$ExpectedText,
    [double]$MinimumConfidence = 0.55,
    [string]$OutputPath = ''
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $WavPath)) { throw "WAV file not found: $WavPath" }

function Normalize-Dialogue([string]$Text) {
    if ([string]::IsNullOrWhiteSpace($Text)) { return '' }
    return [regex]::Replace($Text, '[\s，。！？、,.!?：:；;“”"''（）()]', '')
}

Add-Type -AssemblyName System.Speech
$recognizerInfo = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers() |
    Where-Object { $_.Culture.Name -eq 'zh-CN' } |
    Select-Object -First 1
if ($null -eq $recognizerInfo) { throw 'No offline zh-CN Windows speech recognizer is installed.' }

$recognizer = [System.Speech.Recognition.SpeechRecognitionEngine]::new($recognizerInfo)
$recognizer.LoadGrammar([System.Speech.Recognition.DictationGrammar]::new())
$recognizer.SetInputToWaveFile((Resolve-Path -LiteralPath $WavPath).Path)
$segments = @()
while ($true) {
    $result = $recognizer.Recognize()
    if ($null -eq $result) { break }
    $segments += [pscustomobject]@{
        text = $result.Text
        confidence = [double]$result.Confidence
        start_seconds = [double]$result.Audio.AudioPosition.TotalSeconds
        duration_seconds = [double]$result.Audio.Duration.TotalSeconds
    }
}
$recognizer.Dispose()

$recognizedText = ($segments | ForEach-Object { $_.text }) -join ''
$confidence = if ($segments.Count) { [double](($segments | Measure-Object -Property confidence -Average).Average) } else { 0.0 }
$expectedNormalized = Normalize-Dialogue $ExpectedText
$recognizedNormalized = Normalize-Dialogue $recognizedText
$exactMatch = -not [string]::IsNullOrWhiteSpace($recognizedNormalized) -and $recognizedNormalized.Contains($expectedNormalized)
$report = [ordered]@{
    wav = (Resolve-Path -LiteralPath $WavPath).Path
    expected_text = $ExpectedText
    recognized_text = $recognizedText
    confidence = $confidence
    minimum_confidence = $MinimumConfidence
    exact_match = $exactMatch
    automatic_pass = [bool]($exactMatch -and $confidence -ge $MinimumConfidence)
    segments = $segments
    note = 'Automatic ASR evidence only; a failed or low-confidence result requires semantic review or retry.'
}
$json = $report | ConvertTo-Json -Depth 10
if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $parent = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    [IO.File]::WriteAllText($OutputPath, $json, [Text.UTF8Encoding]::new($false))
}
Write-Output $json
