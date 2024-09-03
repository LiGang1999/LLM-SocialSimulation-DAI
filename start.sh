cd frontend_online_old && nohup npm run dev >stdout.log 2>&1 &
cd environment/frontend_server && nohup python manage.py runserver >stdout.log 2>&1 &
cd reverie/backend_server && PYTHONUNBUFFERED=1 nohup python3 manage.py runserver | tee > stdout.log 2>&1 &