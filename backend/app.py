from flask import Flask, request, jsonify
from flask_cors import CORS
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPException

class ActiveDirectory:
    def __init__(self, server_address, domain, base_dn, admin_user, admin_password):
        """
        Inicializa a conexão com o servidor Active Directory.

        :param server_address: Endereço do servidor AD.
        :param domain: Domínio do Active Directory.
        :param base_dn: Base DN para buscas.
        :param admin_user: Usuário administrador para autenticação.
        :param admin_password: Senha do usuário administrador.
        """
        self.server_address = server_address
        self.domain = domain
        self.base_dn = base_dn
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.server = Server(server_address, get_info=ALL)

    def authenticate_user(self, username, password):
        """
        Autentica um usuário no Active Directory.

        :param username: Nome de usuário para autenticação.
        :param password: Senha do usuário.
        :return: True se a autenticação for bem-sucedida, False caso contrário.
        """
        user_dn = f"uid={username},{self.base_dn}"
        try:
            connection = Connection(self.server, user=user_dn, password=password, auto_bind=True)
            return True
        except LDAPException as e:
            print(f"Erro de autenticação: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
        return False

    def get_user_profile(self, username):
        """
        Retorna o perfil de um usuário a partir do AD.

        :param username: Nome de usuário a ser pesquisado.
        :return: Dicionário com atributos do perfil do usuário, ou None se não encontrado.
        """
        search_filter = f"(uid={username})"
        try:
            with Connection(self.server, user=self.admin_user, password=self.admin_password, auto_bind=True) as conn:
                conn.search(search_base=self.base_dn, search_filter=search_filter, attributes=ALL_ATTRIBUTES)
                if conn.entries:
                    user_entry = conn.entries[0]
                    return {attr: user_entry[attr].value for attr in user_entry.entry_attributes}
                else:
                    print("Usuário não encontrado.")
        except LDAPException as e:
            print(f"Erro ao buscar perfil de usuário: {e}")
        return None

    def validate_user(self, username):
        """
        Valida a existência de um usuário no AD.

        :param username: Nome de usuário a ser validado.
        :return: True se o usuário existir, False caso contrário.
        """
        search_filter = f"(uid={username})"
        try:
            with Connection(self.server, user=self.admin_user, password=self.admin_password, auto_bind=True) as conn:
                conn.search(search_base=self.base_dn, search_filter=search_filter, attributes=['cn'])
                return len(conn.entries) > 0
        except LDAPException as e:
            print(f"Erro ao validar usuário: {e}")
        return False


# Configuração do Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir chamadas do frontend

# Configurações do LDAP
SERVER_ADDRESS = "ldap.forumsys.com"
DOMAIN = "example.com"
BASE_DN = "dc=example,dc=com"
ADMIN_USER = "cn=read-only-admin,dc=example,dc=com"
ADMIN_PASSWORD = "password"

# Instância do Active Directory
ad = ActiveDirectory(SERVER_ADDRESS, DOMAIN, BASE_DN, ADMIN_USER, ADMIN_PASSWORD)

@app.route('/ldap-auth', methods=['POST'])
def authenticate_user():
    """
    Endpoint para autenticação de usuário no AD.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username e password são obrigatórios.'}), 400

    if ad.authenticate_user(username, password):
        profile = ad.get_user_profile(username)
        if profile:
            return jsonify({'status': 'success', 'profile': profile}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Perfil do usuário não encontrado.'}), 404
    else:
        return jsonify({'status': 'error', 'message': 'Credenciais inválidas.'}), 401

@app.route('/validate-user', methods=['POST'])
def validate_user():
    """
    Endpoint para validar a existência de um usuário no AD.
    """
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({'status': 'error', 'message': 'Username é obrigatório.'}), 400

    if ad.validate_user(username):
        return jsonify({'status': 'success', 'message': f'Usuário {username} existe no AD.'}), 200
    else:
        return jsonify({'status': 'error', 'message': f'Usuário {username} não encontrado.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
