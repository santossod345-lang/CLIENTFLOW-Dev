/**
 * ClientFlow - Script Principal
 * Funções compartilhadas entre as páginas
 */

// URL da API
const API_URL = 'http://localhost:8000/api';

// Verificar se está autenticado
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && !window.location.href.includes('login.html')) {
        window.location.href = 'login.html';
    }
}

// Formatar data para formato brasileiro
function formatarData(dataString) {
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR');
}

// Formatar data e hora para formato brasileiro
function formatarDataHora(dataString) {
    const data = new Date(dataString);
    return data.toLocaleString('pt-BR');
}

// Função para fazer requisições autenticadas
async function fetchAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    // Adicionar token à URL
    const separator = url.includes('?') ? '&' : '?';
    const urlWithToken = `${url}${separator}token=${token}`;
    
    try {
        const response = await fetch(urlWithToken, options);
        
        // Se não autorizado, redirecionar para login
        if (response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('empresa');
            window.location.href = 'login.html';
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// Validar email
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Formatar telefone brasileiro
function formatarTelefone(telefone) {
    // Remove tudo que não é número
    const numeros = telefone.replace(/\D/g, '');
    
    // Aplica a formatação
    if (numeros.length === 11) {
        return numeros.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (numeros.length === 10) {
        return numeros.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    
    return telefone;
}

// Debounce para otimizar buscas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
