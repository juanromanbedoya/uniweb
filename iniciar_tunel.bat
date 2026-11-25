@echo off
REM Crea una URL publica (tunel) hacia http://127.0.0.1:8000
REM Ejecutar DESPUES de iniciar_servidor.bat, en otra ventana. No cerrar esta ventana.

where cloudflared >nul 2>nul
if %errorlevel%==0 (
  echo Usando Cloudflare Tunnel. Copie la URL https://....trycloudflare.com que aparece abajo.
  cloudflared tunnel --url http://127.0.0.1:8000
) else (
  echo cloudflared no esta instalado: usando localhost.run por SSH.
  echo Copie la URL https://....lhr.life que aparece abajo.
  ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -R 80:127.0.0.1:8000 nokey@localhost.run
)
