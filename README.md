# Biblioteca · Aplicación web (Flask)

## Despliegue en EC2 (Ubuntu)
```bash
sudo apt update && sudo apt install -y python3-venv git
git clone <URL_DEL_REPOSITORIO> && cd biblioteca-web
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env     # credenciales del usuario app_web
python app.py                          # escucha en 0.0.0.0:5000
```
Abrir: `http://<IP_PUBLICA_EC2>:5000`

## Base de datos
Ejecutar `schema.sql` con el usuario maestro (vía túnel SSH desde MySQL Workbench),
cambiando antes las contraseñas de `app_web` y `app_desktop`.

## Mantener la app activa al cerrar SSH (opcional)
```bash
nohup python app.py > app.log 2>&1 &
```
