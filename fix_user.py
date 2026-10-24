import pymysql

# Coloque a senha do seu usuário 'root' do MySQL abaixo
ROOT_PASSWORD = input("Digite a senha do root do MySQL: ")

try:
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password=ROOT_PASSWORD,
        autocommit=True
    )
    cursor = connection.cursor()

    commands = [
        "DROP USER IF EXISTS 'ia_reader'@'localhost';",
        "DROP USER IF EXISTS 'ia_reader'@'127.0.0.1';",
        "DROP USER IF EXISTS 'ia_reader'@'%';",
        "CREATE USER 'ia_reader'@'%' IDENTIFIED WITH mysql_native_password BY 'SenhaSeguraIA123!';",
        "CREATE USER 'ia_reader'@'localhost' IDENTIFIED WITH mysql_native_password BY 'SenhaSeguraIA123!';",
        "GRANT SELECT ON empresa_db.* TO 'ia_reader'@'%';",
        "GRANT SELECT ON empresa_db.* TO 'ia_reader'@'localhost';",
        "FLUSH PRIVILEGES;"
    ]

    for cmd in commands:
        cursor.execute(cmd)

    print("✅ Usuário 'ia_reader' recriado com sucesso com mysql_native_password!")
    connection.close()
except Exception as e:
    print(f"❌ Erro ao configurar usuário: {e}")