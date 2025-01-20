import React from "react";
import ReactDOM from "react-dom/client"; // Importação alterada
import App from "./App";
import "./index.css";

// Criação da raiz do React com a nova API
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
