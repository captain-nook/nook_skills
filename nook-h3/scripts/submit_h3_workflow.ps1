param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('I2VA','FL2VA','Ref2VA','T2VA','L2VA')]
    [string]$Mode,
    [string]$Workspace = (Get-Location).Path,
    [string]$ComfyUrl = 'http://127.0.0.1:8188',
    [string]$WorkflowPath = '',
    [Parameter(Mandatory=$true)]
    [string]$Prompt,
    [string]$FirstFrame = '',
    [string]$LastFrame = '',
    [string[]]$ReferenceImages = @(),
    [string]$OutputPrefix = 'video/h3_clip',
    [double]$Megapixels = 0.9,
    [double]$Duration = 4.0,
    [long]$Seed = -1,
    [switch]$Wait,
    [int]$PollSeconds = 30,
    [int]$MaxMinutes = 120
)

$ErrorActionPreference = 'Stop'

function Set-JsonProperty($Object, [string]$Name, $Value) {
    $property = $Object.PSObject.Properties[$Name]
    if ($null -ne $property) { $property.Value = $Value }
    else { $Object.PSObject.Properties.Add([System.Management.Automation.PSNoteProperty]::new($Name, $Value)) }
}

function Find-Workflow([string]$Base, [string]$ModeName) {
    $pattern = switch ($ModeName) {
        'Ref2VA' { '*ref*.json' }
        'T2VA' { '*t2v*.json' }
        'L2VA' { '*l2v*.json' }
        default { '*i2v*.json' }
    }
    $candidate = Get-ChildItem -LiteralPath $Base -Filter $pattern -File | Select-Object -First 1
    if ($null -eq $candidate) { throw "WorkflowPath is required; no $pattern workflow was found in $Base" }
    return $candidate.FullName
}

if ([string]::IsNullOrWhiteSpace($WorkflowPath)) {
    $WorkflowPath = Find-Workflow -Base $Workspace -ModeName $Mode
}
if (-not (Test-Path -LiteralPath $WorkflowPath)) { throw "Workflow JSON not found: $WorkflowPath" }

$workflow = Get-Content -Raw -Encoding UTF8 -LiteralPath $WorkflowPath | ConvertFrom-Json
if ($Seed -lt 0) { $Seed = [long]((Get-Date).Ticks % 1000000000000000) }
$seedApplied = $false
foreach ($nodeProperty in $workflow.PSObject.Properties) {
    $node = $nodeProperty.Value
    if ($null -ne $node -and [string]$node.class_type -eq 'RandomNoise' -and $null -ne $node.inputs.PSObject.Properties['noise_seed']) {
        $node.inputs.noise_seed = $Seed
        $seedApplied = $true
    }
}
if (-not $seedApplied) { throw "Workflow has no RandomNoise noise_seed input: $WorkflowPath" }
if ($Mode -eq 'Ref2VA') {
    if ($ReferenceImages.Count -lt 2) { throw 'Ref2VA requires at least two reference images.' }
    $workflow.'137'.inputs.image = $ReferenceImages[0]
    $workflow.'139'.inputs.image = $ReferenceImages[1]
    for ($i = 2; $i -lt $ReferenceImages.Count; $i++) {
        $nodeId = [string](140 + $i - 2)
        $node = [pscustomobject]@{ inputs = [pscustomobject]@{ image = $ReferenceImages[$i] }; class_type = 'LoadImage'; _meta = [pscustomobject]@{ title = 'Load Image' } }
        Set-JsonProperty $workflow $nodeId $node
        Set-JsonProperty $workflow.'136'.inputs ("ref_images.ref_image_$i") @($nodeId, 0)
    }
    $workflow.'138'.inputs.value = $Prompt
    $workflow.'132'.inputs.value = $Duration
}
elseif ($Mode -eq 'T2VA') {
    $workflow.'105:111'.inputs.value = $Duration
    $workflow.'105:104'.inputs.prompt = $Prompt
}
elseif ($Mode -eq 'L2VA') {
    if ([string]::IsNullOrWhiteSpace($LastFrame)) { throw 'L2VA requires -LastFrame.' }
    $workflow.'105:111'.inputs.value = $Duration
    $lastNode = [pscustomobject]@{ inputs = [pscustomobject]@{ image = $LastFrame }; class_type = 'LoadImage'; _meta = [pscustomobject]@{ title = 'Load Last Frame' } }
    Set-JsonProperty $workflow '116' $lastNode
    Set-JsonProperty $workflow.'105:104'.inputs 'last_frame' @('116', 0)
    $workflow.'105:104'.inputs.prompt = $Prompt
}
else {
    if ([string]::IsNullOrWhiteSpace($FirstFrame)) { throw "$Mode requires -FirstFrame." }
    if ($Mode -eq 'FL2VA' -and [string]::IsNullOrWhiteSpace($LastFrame)) { throw 'FL2VA requires -LastFrame.' }
    $workflow.'114'.inputs.image = $FirstFrame
    $workflow.'105:111'.inputs.value = $Duration
    if ($Mode -eq 'FL2VA') {
        $lastNode = [pscustomobject]@{ inputs = [pscustomobject]@{ image = $LastFrame }; class_type = 'LoadImage'; _meta = [pscustomobject]@{ title = 'Load Last Frame' } }
        Set-JsonProperty $workflow '116' $lastNode
        Set-JsonProperty $workflow.'105:104'.inputs 'last_frame' @('116', 0)
    }
    $workflow.'105:104'.inputs.prompt = $Prompt
}

$workflow.'115'.inputs.aspect_ratio = '16:9 (Widescreen)'
$workflow.'115'.inputs.megapixels = $Megapixels
$workflow.'92'.inputs.filename_prefix = $OutputPrefix

$payload = @{ prompt = $workflow; client_id = [guid]::NewGuid().Guid } | ConvertTo-Json -Depth 100 -Compress
$encoding = New-Object System.Text.UTF8Encoding($false)
$bytes = $encoding.GetBytes($payload)
$client = New-Object System.Net.WebClient
$client.Headers['Content-Type'] = 'application/json; charset=utf-8'
$response = [System.Text.Encoding]::UTF8.GetString($client.UploadData("$ComfyUrl/prompt", 'POST', $bytes)) | ConvertFrom-Json
$promptId = $response.prompt_id
if ([string]::IsNullOrWhiteSpace($promptId)) { throw 'ComfyUI did not return a prompt_id.' }
Write-Output "SUBMITTED mode=$Mode prompt_id=$promptId seed=$Seed output_prefix=$OutputPrefix"

if ($Wait) {
    $deadline = (Get-Date).AddMinutes($MaxMinutes)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds $PollSeconds
        $history = Invoke-RestMethod -Uri "$ComfyUrl/history/$promptId"
        $entry = $history.PSObject.Properties[$promptId]
        if ($null -eq $entry) { continue }
        $status = $entry.Value.status.status_str
        if ($status -eq 'success') {
            $names = @($entry.Value.outputs.PSObject.Properties | ForEach-Object {
                @($_.Value.images, $_.Value.gifs) | Where-Object { $null -ne $_ } | ForEach-Object { $_.filename }
            })
            Write-Output "SUCCESS prompt_id=$promptId output=$($names -join ',')"
            exit 0
        }
        if ($status -eq 'error' -or ($entry.Value.status.completed -eq $true -and $status -ne 'success')) {
            throw "H3 task failed: prompt_id=$promptId status=$status"
        }
    }
    throw "Timed out waiting for prompt_id=$promptId after $MaxMinutes minutes."
}
