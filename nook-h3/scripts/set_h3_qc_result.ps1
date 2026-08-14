param(
    [Parameter(Mandatory=$true)]
    [string]$StatePath,
    [Parameter(Mandatory=$true)]
    [string]$TaskId,
    [Parameter(Mandatory=$true)]
    [ValidateSet('pass','retry','rework','manual')]
    [string]$Result,
    [string[]]$FailureReasons = @(),
    [string]$PromptRevision = '',
    [string]$ManifestPath = '',
    [string]$RevisedPrompt = ''
)

$ErrorActionPreference = 'Stop'

function Ensure-Section($State, [string]$Name) {
    if ($null -eq $State.PSObject.Properties[$Name]) {
        $State.PSObject.Properties.Add([System.Management.Automation.PSNoteProperty]::new($Name, [pscustomobject]@{}))
    }
    return $State.$Name
}

function Set-Record($Section, [string]$Name, $Value) {
    if ($null -ne $Section.PSObject.Properties[$Name]) { $Section.$Name = $Value }
    else { $Section.PSObject.Properties.Add([System.Management.Automation.PSNoteProperty]::new($Name, $Value)) }
}

if (-not (Test-Path -LiteralPath $StatePath)) { throw "State file not found: $StatePath" }
$state = Get-Content -Raw -Encoding UTF8 -LiteralPath $StatePath | ConvertFrom-Json
$awaiting = Ensure-Section $state 'awaiting_qc'
$pendingProperty = $awaiting.PSObject.Properties[$TaskId]
if ($null -eq $pendingProperty) { throw "Task is not awaiting QC: $TaskId" }
$pending = $pendingProperty.Value
$record = [ordered]@{
    status = $Result
    task_id = $TaskId
    attempt = $pending.attempt
    seed = $pending.seed
    prompt_id = $pending.prompt_id
    outputs = @($pending.outputs)
    failure_reasons = @($FailureReasons)
    prompt_revision = $PromptRevision
    reviewed_at = (Get-Date).ToString('o')
}

switch ($Result) {
    'pass' {
        $record.status = 'success'
        Set-Record (Ensure-Section $state 'completed') $TaskId ([pscustomobject]$record)
    }
    'retry' {
        $record.status = 'retry_pending'
        Set-Record (Ensure-Section $state 'rework_pending') $TaskId ([pscustomobject]$record)
    }
    'rework' {
        $record.status = 'rework_pending'
        Set-Record (Ensure-Section $state 'rework_pending') $TaskId ([pscustomobject]$record)
    }
    'manual' {
        $record.status = 'manual_review'
        Set-Record (Ensure-Section $state 'failed') $TaskId ([pscustomobject]$record)
    }
}

if (($Result -eq 'retry' -or $Result -eq 'rework') -and -not [string]::IsNullOrWhiteSpace($RevisedPrompt)) {
    if ([string]::IsNullOrWhiteSpace($ManifestPath) -or -not (Test-Path -LiteralPath $ManifestPath)) {
        throw 'ManifestPath is required when RevisedPrompt is supplied.'
    }
    $manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $ManifestPath | ConvertFrom-Json
    $task = @($manifest.tasks | Where-Object { [string]$_.id -eq $TaskId })
    if ($task.Count -ne 1) { throw "Expected exactly one manifest task with id: $TaskId" }
    if ($null -ne $task[0].PSObject.Properties['prompt']) { $task[0].prompt = $RevisedPrompt }
    else { $task[0].PSObject.Properties.Add([System.Management.Automation.PSNoteProperty]::new('prompt', $RevisedPrompt)) }
    $manifestJson = $manifest | ConvertTo-Json -Depth 100
    [IO.File]::WriteAllText((Resolve-Path -LiteralPath $ManifestPath).Path, $manifestJson, [Text.UTF8Encoding]::new($false))
}

$awaiting.PSObject.Properties.Remove($TaskId)
$json = $state | ConvertTo-Json -Depth 100
[IO.File]::WriteAllText((Resolve-Path -LiteralPath $StatePath).Path, $json, [Text.UTF8Encoding]::new($false))
Write-Output "QC_RECORDED task_id=$TaskId result=$Result"
