param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('I2VA','FL2VA','L2VA','T2VA','Ref2VA')]
    [string]$Mode,
    [Parameter(Mandatory=$true)]
    [string]$Prompt,
    [string]$ExpectedDialogue = '',
    [switch]$CalmCloudSea,
    [switch]$OpeningSubjectRequired
)

$ErrorActionPreference = 'Stop'
$errors = [System.Collections.Generic.List[string]]::new()

function Require-InOrder([string[]]$Labels) {
    $cursor = 0
    foreach ($label in $Labels) {
        $index = $Prompt.IndexOf($label, $cursor, [System.StringComparison]::Ordinal)
        if ($index -lt 0) {
            $errors.Add("Missing or out-of-order prompt field: $label")
            return
        }
        $cursor = $index + $label.Length
    }
}

if ($Mode -eq 'Ref2VA') {
    Require-InOrder @(
        'subject_definitions:',
        'summary:',
        'retention_analysis:',
        'detailed_description:',
        'overall_soundscape:',
        'non_diegetic_music:'
    )
}
else {
    Require-InOrder @(
        'integrated_multimodal_description:',
        'overall_soundscape:',
        'non_diegetic_music:'
    )
}

if ($Prompt -notmatch '(?im)^non_diegetic_music:\s*N/A\s*$') {
    $errors.Add('non_diegetic_music must be exactly N/A for this production.')
}

if (-not [string]::IsNullOrWhiteSpace($ExpectedDialogue)) {
    $escaped = [regex]::Escape($ExpectedDialogue)
    if ($Prompt -notmatch "<d>\[Chinese\]\s*$escaped\s*</d>") {
        $errors.Add('Expected Chinese dialogue is absent from the official dialogue tag or does not match exactly.')
    }
    if ($Prompt -notmatch '(?s)<Subject\s+\d+>\s*\(S\d+\).*?says:\s*<d>\[Chinese\]') {
        $errors.Add('The speaking event must bind <Subject N> and (Sx) directly to says: <d>[Chinese].')
    }
}

if ($CalmCloudSea) {
    $banned = @(
        '\bsurge(?:s|d|ing)?\b',
        '\broll(?:s|ed|ing)?\b',
        '\bwave motion\b',
        '\bbroad coherent (?:wave|waves|layer|layers)\b',
        '\bbillow(?:s|ed|ing)? (?:toward|towards|into) (?:the )?camera\b'
    )
    foreach ($pattern in $banned) {
        if ($Prompt -match $pattern) {
            $errors.Add("Calm-cloud prompt contains disaster-scale motion language: $($Matches[0])")
        }
    }
    if ($Prompt -notmatch '(?i)(stable|constant).{0,80}(height|outer (?:shape|silhouette|contour))') {
        $errors.Add('Calm-cloud prompt must anchor cloud height or outer silhouette as stable.')
    }
    if ($Prompt -notmatch '(?i)(fine|subtle|low[- ]amplitude).{0,100}(lateral|horizontal|along the horizon).{0,80}(drift|advection|movement|motion)') {
        $errors.Add('Calm-cloud prompt must specify subtle low-amplitude lateral internal drift.')
    }
}

if ($OpeningSubjectRequired -and $Prompt -match '(?i)(enters?|walks?)\s+(?:in\s+)?from\s+(?:outside|off[- ]?screen|the side|out of frame)') {
    $errors.Add('Opening subject is required, but the prompt asks the subject to enter from outside the frame.')
}

if ($errors.Count -gt 0) {
    throw "H3 prompt preflight failed:`n- $($errors -join "`n- ")"
}

Write-Output 'H3_PROMPT_PREFLIGHT_OK'
