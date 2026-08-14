param(
    [Parameter(Mandatory=$true)]
    [string]$ManifestPath,
    [string]$StatePath = '',
    [string]$LogPath = '',
    [int]$PollSeconds = 30,
    [int]$MaxMinutes = 120
)

$ErrorActionPreference = 'Stop'

function Get-Field($Object, [string]$Name, $Default = $null) {
    if ($null -eq $Object) { return $Default }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property -or $null -eq $property.Value) { return $Default }
    return $property.Value
}

function Set-Field($Object, [string]$Name, $Value) {
    $property = $Object.PSObject.Properties[$Name]
    if ($null -ne $property) { $property.Value = $Value }
    else { $Object.PSObject.Properties.Add([System.Management.Automation.PSNoteProperty]::new($Name, $Value)) }
}

function Resolve-ConfigPath([string]$Value, [string]$ManifestDir, [string]$Workspace) {
    if ([string]::IsNullOrWhiteSpace($Value)) { return '' }
    if ([System.IO.Path]::IsPathRooted($Value)) { return $Value }
    $fromManifest = Join-Path $ManifestDir $Value
    if (Test-Path -LiteralPath $fromManifest) { return (Resolve-Path -LiteralPath $fromManifest).Path }
    $fromWorkspace = Join-Path $Workspace $Value
    if (Test-Path -LiteralPath $fromWorkspace) { return (Resolve-Path -LiteralPath $fromWorkspace).Path }
    return $fromManifest
}

function Set-JsonProperty($Object, [string]$Name, $Value) {
    $property = $Object.PSObject.Properties[$Name]
    if ($null -ne $property) { $property.Value = $Value }
    else { $Object.PSObject.Properties.Add([System.Management.Automation.PSNoteProperty]::new($Name, $Value)) }
}

function Get-NodeId($Task, $Defaults, [string]$Name, [string]$Fallback) {
    $taskMap = Get-Field $Task 'node_map' $null
    $defaultMap = Get-Field $Defaults 'node_map' $null
    $value = Get-Field $taskMap $Name $null
    if ([string]::IsNullOrWhiteSpace([string]$value)) { $value = Get-Field $defaultMap $Name $null }
    if ([string]::IsNullOrWhiteSpace([string]$value)) { return $Fallback }
    return [string]$value
}

function Write-Log([string]$Message) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Add-Content -LiteralPath $script:ResolvedLogPath -Value $line -Encoding UTF8
    Write-Output $line
}

function Save-State($State) {
    $State | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $script:ResolvedStatePath -Encoding UTF8
}

function Find-ExistingOutput([string]$Prefix, [string]$OutputDir) {
    if ([string]::IsNullOrWhiteSpace($OutputDir) -or -not (Test-Path -LiteralPath $OutputDir)) { return @() }
    $leaf = [System.IO.Path]::GetFileName(($Prefix -replace '\\','/'))
    if ([string]::IsNullOrWhiteSpace($leaf)) { return @() }
    return @(Get-ChildItem -LiteralPath $OutputDir -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "$leaf*" } | Select-Object -ExpandProperty Name)
}

function Set-StateRecord($State, [string]$SectionName, [string]$TaskId, $Record) {
    $section = Get-Field $State $SectionName $null
    if ($null -eq $section) {
        $section = [pscustomobject]@{}
        Set-Field $State $SectionName $section
    }
    Set-Field $section $TaskId $Record
    Save-State $State
}

function Get-WorkflowPath($Task, $Defaults, [string]$Mode, [string]$ManifestDir, [string]$Workspace) {
    $key = switch ($Mode) {
        'Ref2VA' { 'ref2v_workflow' }
        'T2VA' { 't2v_workflow' }
        'L2VA' { 'l2v_workflow' }
        default { 'i2v_workflow' }
    }
    $value = Get-Field $Task 'workflow' ''
    if ([string]::IsNullOrWhiteSpace($value)) { $value = Get-Field $Task $key '' }
    if ([string]::IsNullOrWhiteSpace($value)) { $value = Get-Field $Defaults $key '' }
    if ($Mode -eq 'L2VA' -and [string]::IsNullOrWhiteSpace($value)) { $value = Get-Field $Defaults 'i2v_workflow' '' }
    $path = Resolve-ConfigPath $value $ManifestDir $Workspace
    if (-not (Test-Path -LiteralPath $path)) { throw "Workflow JSON not found for $Mode task: $path" }
    return $path
}

function New-WorkflowForTask($Task, $Defaults, [string]$ManifestDir, [string]$Workspace) {
    $mode = [string](Get-Field $Task 'mode' '')
    if ($mode -notin @('I2VA','FL2VA','Ref2VA','T2VA','L2VA')) { throw "Unsupported mode: $mode" }
    $workflowPath = Get-WorkflowPath $Task $Defaults $mode $ManifestDir $Workspace
    $workflow = Get-Content -Raw -Encoding UTF8 -LiteralPath $workflowPath | ConvertFrom-Json
    $prompt = [string](Get-Field $Task 'prompt' '')
    if ([string]::IsNullOrWhiteSpace($prompt)) { throw "Task $($Task.id) has an empty prompt." }
    $duration = [double](Get-Field $Task 'duration' (Get-Field $Defaults 'duration' 4.0))
    $megapixels = [double](Get-Field $Task 'megapixels' (Get-Field $Defaults 'megapixels' 0.9))
    $outputPrefix = [string](Get-Field $Task 'output_prefix' ("video/" + $Task.id))
    $resolutionId = Get-NodeId $Task $Defaults 'resolution' '115'
    $saveId = Get-NodeId $Task $Defaults 'save_video' '92'
    $resolution = $workflow.PSObject.Properties[$resolutionId].Value
    $save = $workflow.PSObject.Properties[$saveId].Value
    if ($null -eq $resolution -or $null -eq $save) { throw "Workflow $workflowPath is missing resolution or SaveVideo node." }
    $resolution.inputs.aspect_ratio = [string](Get-Field $Task 'aspect_ratio' (Get-Field $Defaults 'aspect_ratio' '16:9 (Widescreen)'))
    $resolution.inputs.megapixels = $megapixels
    $save.inputs.filename_prefix = $outputPrefix

    if ($mode -eq 'Ref2VA') {
        $refs = @((Get-Field $Task 'references' @()))
        if ($refs.Count -lt 2) { throw "Ref2VA task $($Task.id) requires at least two references." }
        $firstRefId = Get-NodeId $Task $Defaults 'reference_1' '137'
        $secondRefId = Get-NodeId $Task $Defaults 'reference_2' '139'
        $videoId = Get-NodeId $Task $Defaults 'video_node' '136'
        $promptId = Get-NodeId $Task $Defaults 'prompt' '138'
        $durationId = Get-NodeId $Task $Defaults 'duration' '132'
        $workflow.PSObject.Properties[$firstRefId].Value.inputs.image = [string]$refs[0]
        $workflow.PSObject.Properties[$secondRefId].Value.inputs.image = [string]$refs[1]
        for ($i = 2; $i -lt $refs.Count; $i++) {
            $nodeId = [string](140 + $i - 2)
            $node = [pscustomobject]@{ inputs = [pscustomobject]@{ image = [string]$refs[$i] }; class_type = 'LoadImage'; _meta = [pscustomobject]@{ title = 'Load Image' } }
            Set-JsonProperty $workflow $nodeId $node
            Set-JsonProperty $workflow.PSObject.Properties[$videoId].Value.inputs ("ref_images.ref_image_$i") @($nodeId, 0)
        }
        $workflow.PSObject.Properties[$promptId].Value.inputs.value = $prompt
        $workflow.PSObject.Properties[$durationId].Value.inputs.value = $duration
    }
    elseif ($mode -eq 'T2VA') {
        $videoId = Get-NodeId $Task $Defaults 'video_node' '105:104'
        $durationId = Get-NodeId $Task $Defaults 'duration' '105:111'
        $workflow.PSObject.Properties[$videoId].Value.inputs.prompt = $prompt
        $workflow.PSObject.Properties[$durationId].Value.inputs.value = $duration
    }
    elseif ($mode -eq 'L2VA') {
        $lastFrame = [string](Get-Field $Task 'last_frame' '')
        if ([string]::IsNullOrWhiteSpace($lastFrame)) { throw "L2VA task $($Task.id) requires last_frame." }
        $videoId = Get-NodeId $Task $Defaults 'video_node' '105:104'
        $durationId = Get-NodeId $Task $Defaults 'duration' '105:111'
        $lastNodeId = Get-NodeId $Task $Defaults 'last_frame' '116'
        $lastNode = [pscustomobject]@{ inputs = [pscustomobject]@{ image = $lastFrame }; class_type = 'LoadImage'; _meta = [pscustomobject]@{ title = 'Load Last Frame' } }
        Set-JsonProperty $workflow $lastNodeId $lastNode
        Set-JsonProperty $workflow.PSObject.Properties[$videoId].Value.inputs 'last_frame' @($lastNodeId, 0)
        $workflow.PSObject.Properties[$videoId].Value.inputs.prompt = $prompt
        $workflow.PSObject.Properties[$durationId].Value.inputs.value = $duration
    }
    else {
        $firstFrame = [string](Get-Field $Task 'first_frame' '')
        if ([string]::IsNullOrWhiteSpace($firstFrame)) { throw "$mode task $($Task.id) requires first_frame." }
        if ($mode -eq 'FL2VA' -and [string]::IsNullOrWhiteSpace([string](Get-Field $Task 'last_frame' ''))) { throw "FL2VA task $($Task.id) requires last_frame." }
        $firstId = Get-NodeId $Task $Defaults 'first_frame' '114'
        $videoId = Get-NodeId $Task $Defaults 'video_node' '105:104'
        $durationId = Get-NodeId $Task $Defaults 'duration' '105:111'
        $workflow.PSObject.Properties[$firstId].Value.inputs.image = $firstFrame
        $workflow.PSObject.Properties[$videoId].Value.inputs.prompt = $prompt
        $workflow.PSObject.Properties[$durationId].Value.inputs.value = $duration
        if ($mode -eq 'FL2VA') {
            $lastNodeId = Get-NodeId $Task $Defaults 'last_frame' '116'
            $lastNode = [pscustomobject]@{ inputs = [pscustomobject]@{ image = [string]$Task.last_frame }; class_type = 'LoadImage'; _meta = [pscustomobject]@{ title = 'Load Last Frame' } }
            Set-JsonProperty $workflow $lastNodeId $lastNode
            Set-JsonProperty $workflow.PSObject.Properties[$videoId].Value.inputs 'last_frame' @($lastNodeId, 0)
        }
    }
    return [pscustomobject]@{ Workflow = $workflow; Mode = $mode; OutputPrefix = $outputPrefix; Duration = $duration; Megapixels = $megapixels }
}

function Submit-Task($Prepared, [string]$ComfyUrl) {
    $payload = @{ prompt = $Prepared.Workflow; client_id = [guid]::NewGuid().Guid } | ConvertTo-Json -Depth 100 -Compress
    $encoding = New-Object System.Text.UTF8Encoding($false)
    $client = New-Object System.Net.WebClient
    $client.Headers['Content-Type'] = 'application/json; charset=utf-8'
    $response = [System.Text.Encoding]::UTF8.GetString($client.UploadData("$ComfyUrl/prompt", 'POST', $encoding.GetBytes($payload))) | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace([string]$response.prompt_id)) { throw 'ComfyUI did not return a prompt_id.' }
    return [string]$response.prompt_id
}

function Wait-Task([string]$ComfyUrl, [string]$PromptId, [int]$Seconds, [int]$Minutes) {
    $deadline = (Get-Date).AddMinutes($Minutes)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds $Seconds
        $history = Invoke-RestMethod -Uri "$ComfyUrl/history/$PromptId"
        $entry = $history.PSObject.Properties[$PromptId]
        if ($null -eq $entry) { continue }
        $status = [string]$entry.Value.status.status_str
        if ($status -eq 'success') {
            $names = @()
            foreach ($output in $entry.Value.outputs.PSObject.Properties) {
                foreach ($collectionName in @('images','gifs','videos')) {
                    $collection = Get-Field $output.Value $collectionName @()
                    foreach ($item in @($collection)) {
                        $name = [string](Get-Field $item 'filename' '')
                        if (-not [string]::IsNullOrWhiteSpace($name)) { $names += $name }
                    }
                }
            }
            return [pscustomobject]@{ PromptId = $PromptId; Outputs = $names }
        }
        if ($status -eq 'error' -or ($entry.Value.status.completed -eq $true -and $status -ne 'success')) {
            throw "H3 task failed: prompt_id=$PromptId status=$status"
        }
    }
    throw "Timed out waiting for prompt_id=$PromptId after $Minutes minutes."
}

$manifestFull = (Resolve-Path -LiteralPath $ManifestPath).Path
$manifestDir = Split-Path -Parent $manifestFull
$manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath $manifestFull | ConvertFrom-Json
$defaults = Get-Field $manifest 'defaults' ([pscustomobject]@{})
$workspaceValue = [string](Get-Field $defaults 'workspace' '.')
$workspace = Resolve-ConfigPath $workspaceValue $manifestDir $manifestDir
if (-not (Test-Path -LiteralPath $workspace)) { throw "Workspace not found: $workspace" }
$comfyUrl = [string](Get-Field $defaults 'comfy_url' 'http://127.0.0.1:8188')
$outputDirValue = [string](Get-Field $defaults 'output_dir' '')
$outputDir = Resolve-ConfigPath $outputDirValue $manifestDir $workspace
$script:ResolvedStatePath = if ([string]::IsNullOrWhiteSpace($StatePath)) { Join-Path $manifestDir '.h3-batch-state.json' } else { Resolve-ConfigPath $StatePath $manifestDir $workspace }
$script:ResolvedLogPath = if ([string]::IsNullOrWhiteSpace($LogPath)) { Join-Path $manifestDir 'h3-batch.log' } else { Resolve-ConfigPath $LogPath $manifestDir $workspace }

$tasks = @((Get-Field $manifest 'tasks' @()))
if ($tasks.Count -eq 0) { throw 'Manifest tasks array is empty.' }
$ids = @($tasks | ForEach-Object { [string](Get-Field $_ 'id' '') })
if ($ids | Where-Object { [string]::IsNullOrWhiteSpace($_) }) { throw 'Every task needs a non-empty id.' }
if (($ids | Sort-Object -Unique).Count -ne $ids.Count) { throw 'Task ids must be unique.' }

if (Test-Path -LiteralPath $script:ResolvedStatePath) {
    $state = Get-Content -Raw -Encoding UTF8 -LiteralPath $script:ResolvedStatePath | ConvertFrom-Json
}
else {
    $state = [pscustomobject]@{ completed = [pscustomobject]@{}; failed = [pscustomobject]@{} }
    Save-State $state
}

try {
    Invoke-RestMethod -Uri "$comfyUrl/system_stats" -Method Get | Out-Null
}
catch {
    throw "ComfyUI preflight failed at $comfyUrl. Start ComfyUI and verify the endpoint before running the batch. Details: $($_.Exception.Message)"
}

Write-Log "BATCH START tasks=$($tasks.Count) comfy_url=$comfyUrl workspace=$workspace"
foreach ($task in $tasks) {
    $id = [string]$task.id
    $completed = Get-Field (Get-Field $state 'completed' $null) $id $null
    if ($null -ne $completed -and (Get-Field $completed 'status' '') -eq 'success') {
        Write-Log "SKIP id=$id reason=state_completed"
        continue
    }
    $outputPrefix = [string](Get-Field $task 'output_prefix' ("video/" + $id))
    $existingOutputs = @(Find-ExistingOutput $outputPrefix $outputDir)
    if ($existingOutputs.Count -gt 0) {
        Set-StateRecord $state 'completed' $id ([pscustomobject]@{ status = 'success'; prompt_id = 'existing-output'; outputs = $existingOutputs; completed_at = (Get-Date).ToString('o') })
        Write-Log "SKIP id=$id reason=existing_output outputs=$($existingOutputs -join ',')"
        continue
    }
    $mode = [string](Get-Field $task 'mode' '')
    $maxRetries = [int](Get-Field $task 'max_retries' (Get-Field $defaults 'max_retries' 3))
    if ($maxRetries -lt 1) { throw "Task $id has max_retries less than 1." }
    $taskPoll = [int](Get-Field $task 'poll_seconds' (Get-Field $defaults 'poll_seconds' $PollSeconds))
    $taskMaxMinutes = [int](Get-Field $task 'max_minutes' (Get-Field $defaults 'max_minutes' $MaxMinutes))
    $done = $false
    for ($attempt = 1; $attempt -le $maxRetries -and -not $done; $attempt++) {
        try {
            $prepared = New-WorkflowForTask $task $defaults $manifestDir $workspace
            Write-Log "SUBMIT id=$id attempt=$attempt mode=$mode duration=$($prepared.Duration) megapixels=$($prepared.Megapixels)"
            $promptId = Submit-Task $prepared $comfyUrl
            Write-Log "POLL id=$id prompt_id=$promptId"
            $result = Wait-Task $comfyUrl $promptId $taskPoll $taskMaxMinutes
            Set-StateRecord $state 'completed' $id ([pscustomobject]@{ status = 'success'; prompt_id = $result.PromptId; outputs = @($result.Outputs); completed_at = (Get-Date).ToString('o') })
            Write-Log "SUCCESS id=$id prompt_id=$($result.PromptId) outputs=$($result.Outputs -join ',')"
            $done = $true
        }
        catch {
            Write-Log "FAIL id=$id attempt=$attempt error=$($_.Exception.Message)"
            if ($attempt -ge $maxRetries) {
                Set-StateRecord $state 'failed' $id ([pscustomobject]@{ status = 'failed'; attempts = $attempt; error = $_.Exception.Message; failed_at = (Get-Date).ToString('o') })
                throw "Batch stopped at task $id after $attempt attempts."
            }
            Start-Sleep -Seconds 5
        }
    }
}
Write-Log 'BATCH COMPLETE all tasks succeeded or were already completed'
