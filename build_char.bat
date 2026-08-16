@echo off
"C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe" "C:\rAthena\rathena\rAthena.sln" /t:char-server /p:Configuration=Release /p:Platform=x64 /v:detailed /nologo
