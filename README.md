# 🛠️ Instruções para rodar o projeto Rede Farol

1️⃣ Se estiver em C:\, digite e  Entre na pasta do projeto

cd "C:\Rede Farol\rede_farol"

2️⃣ Ative o ambiente virtual

& "C:/Rede Farol/venv/Scripts/Activate.ps1"

Para Desativar: 


deactivate

Para voltar: 
cd..
--------------------------------------------
✅ Você verá (venv) no início da linha.

3️⃣ Instale as dependências (só uma vez)

pip install flask flask-mysqldb bcrypt pymysql

4️⃣ Rode o Flask

python app.py

5️⃣ Entre na pasta do projeto

cd C:\Rede Farol\rede_farol

⚠️ Importante: não coloque espaço no nome da pasta! 

Se sua pasta se chama 
"rede farol" (com espaço), 

renomeie para "rede_farol" (com underline).

✅ Se tudo der certo, vai aparecer:
* Running on http://127.0.0.1:5000

---------------------------------------------------------------------------------------

⚠️ FAZER backup
copy -Recurse rede_farol "rede_farol_backup_$(Get-Date -Format 'yyyyMMdd')"

--------------------------------------------

& "C:/Rede Farol/venv/Scripts/Activate.ps1"

cd rede farol

python app.py

http://127.0.0.1:5000

--------------------------------------------

