@echo off
cd /d "%~dp0"
echo ============================================
echo  Observatorio de Projetos Integradores
echo ============================================

REM Verifica se o .venv existe; se nao, cria e instala dependencias
if not exist ".venv\Scripts\python.exe" (
    echo [SETUP] Ambiente virtual nao encontrado. Criando...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o ambiente virtual.
        echo Verifique se o Python esta instalado e no PATH.
        pause
        exit /b 1
    )
    echo [SETUP] Instalando dependencias...
    .venv\Scripts\pip.exe install -r observatorio_pi\requirements.txt
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias.
        pause
        exit /b 1
    )
    echo [SETUP] Configuracao concluida.
)

echo [INFO] Iniciando servidor...
echo [INFO] Acesse: http://127.0.0.1:8000
echo [INFO] Pressione CTRL+C para parar.
echo.
.venv\Scripts\python.exe run.py
pause
