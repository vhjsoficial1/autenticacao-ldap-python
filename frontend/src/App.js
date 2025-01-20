import React, { useState } from "react";
import './App.css';  // Ou './index.css' se você preferir adicionar no index.css

const App = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [response, setResponse] = useState("");

    // Função que lida com o envio do formulário
    const handleSubmit = async (e) => {
        e.preventDefault();  // Previne o comportamento padrão do formulário
        try {
            // Envia a requisição POST para o backend Flask
            const res = await fetch("http://localhost:5000/ldap-auth", {
                method: "POST", // O método é POST
                headers: {
                    "Content-Type": "application/json",  // Cabeçalho especificando que o corpo é JSON
                },
                body: JSON.stringify({ username, password }),  // Envia o nome de usuário e senha em formato JSON
            });
            const data = await res.json();  // Converte a resposta do backend em JSON
            setResponse(data);  // Atualiza o estado com a resposta do backend
        } catch (error) {
            console.error("Erro:", error);  // Caso haja erro, loga no console
        }
    };

    return (
        <div className="container">  {/* Contêiner para centralizar o conteúdo */}
            <h1>Autenticação LDAP</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}  // Atualiza o estado com o valor do input
                />
                <input
                    type="text"  // Mantém o tipo como "password" para esconder a senha
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit">Login</button>
            </form>
            {response && <pre>{JSON.stringify(response, null, 2)}</pre>}  {/* Exibe a resposta do backend */}
        </div>
    );
};

export default App;
