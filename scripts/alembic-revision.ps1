param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Message
)

$joined = $Message -join ' '
if (-not $joined) { $joined = "manual" }
alembic -c backend/alembic.ini revision --autogenerate -m "$joined"
