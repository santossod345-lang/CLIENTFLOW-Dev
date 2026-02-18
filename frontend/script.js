// ========== CONFIGURAÇÃO GLOBAL DA API ========== 
let API_URL = "https://clientflow-production-99f1.up.railway.app";
// Tenta ler API_URL de variável de ambiente (Next.js, Vite, etc)
if (typeof process !== 'undefined' && process.env && process.env.API_URL) {
    API_URL = process.env.API_URL;
} else if (window && window.API_URL) {
    API_URL = window.API_URL;
} else if (window && window.location && window.location.hostname === 'localhost') {
    API_URL = "http://localhost:8000";
}

// Função utilitária para requisições autenticadas (JWT ou token antigo)
async function fetchAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    const accessToken = localStorage.getItem('access_token');
    options = options || {};
    options.headers = options.headers || {};
    if (accessToken) {
        options.headers['Authorization'] = `Bearer ${accessToken}`;
    } else if (token) {
        // Compatibilidade antiga: token na query
        const sep = url.includes('?') ? '&' : '?';
        url = `${url}${sep}token=${token}`;
    }
    const response = await fetch(url, options);
    if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('access_token');
        localStorage.removeItem('empresa');
        window.location.href = 'login.html';
        return null;
    }
    return response;
}

// Unwrap standardized API responses to keep compatibility with legacy payloads
function unwrapApiPayload(payload) {
    if (payload && typeof payload === 'object' && payload.status && Object.prototype.hasOwnProperty.call(payload, 'data')) {
        return payload.data;
    }
    return payload;
}

async function readJson(response) {
    const payload = await response.json();
    return unwrapApiPayload(payload);
}
// ========== CONFIRMAÇÃO DE LOGOUT ==========
function handleLogout() {
    if (confirm('Tem certeza que deseja sair?')) {
        localStorage.removeItem('token');
        localStorage.removeItem('empresa');
        window.location.href = 'login.html';
    }
}
// ========== AUTO-PREENCHIMENTO DE CLIENTE POR TELEFONE ==========
document.addEventListener('DOMContentLoaded', function() {
    const telInput = document.getElementById('cliente-telefone');
    if (telInput) {
        telInput.addEventListener('blur', async function() {
            const telefone = telInput.value.replace(/\D/g, '');
            if (!telefone) return;
            const token = localStorage.getItem('token');
            try {
                // CORRIGIDO: fetch para clientes
                const resp = await fetch(`${API_URL}/api/clientes?token=${token}`);
                if (!resp.ok) return;
                const clientes = await readJson(resp);
                const cliente = clientes.find(c => (c.telefone||'').replace(/\D/g, '') === telefone);
                if (cliente) {
                    document.getElementById('cliente-nome').value = cliente.nome;
                    showToast('Cliente já cadastrado! Dados preenchidos automaticamente.','success');
                }
            } catch {}
        });
    }
});
// ========== INTELIGÊNCIA ARTIFICIAL (IA) ========== 
// CORRIGIDO: API_IA para /api/ia
const API_IA = `${API_URL}/api/ia`;

async function analisarClienteIA() {
    const clienteId = prompt("Digite o ID do cliente para analisar:");
    if (!clienteId) return;
    showLoading();
    try {
        const resp = await fetch(`${API_IA}/resumo_cliente/${clienteId}`);
        const data = await readJson(resp);
        showIAResposta(data.resumo || "Erro ao analisar cliente.");
    } catch (e) {
        showIAResposta("Erro ao analisar cliente.");
    } finally { hideLoading(); }
}

async function verSugestoesIA() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return showIAResposta("Empresa não encontrada.");
    showLoading();
    try {
        const resp = await fetch(`${API_IA}/sugestoes/${empresa.id}`);
        const data = await readJson(resp);
        showIAResposta(data.sugestoes ? data.sugestoes.map(s=>`${s.cliente}: ${s.sugestao}`).join('<br>') : "Erro ao obter sugestões.");
    } catch (e) {
        showIAResposta("Erro ao obter sugestões.");
    } finally { hideLoading(); }
}

async function verInsightsIA() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return showIAResposta("Empresa não encontrada.");
    showLoading();
    try {
        const resp = await fetch(`${API_IA}/insights/${empresa.id}`);
        const data = await readJson(resp);
        showIAResposta(data.insights ? data.insights.join('<br>') : "Erro ao obter insights.");
    } catch (e) {
        showIAResposta("Erro ao obter insights.");
    } finally { hideLoading(); }
}

async function gerarResumoIA() {
    const clienteId = prompt("Digite o ID do cliente para gerar resumo:");
    if (!clienteId) return;
    showLoading();
    try {
        const resp = await fetch(`${API_IA}/resumo_cliente/${clienteId}`);
        const data = await readJson(resp);
        showIAResposta(data.resumo || "Erro ao gerar resumo.");
    } catch (e) {
        showIAResposta("Erro ao gerar resumo.");
    } finally { hideLoading(); }
}

async function perguntarIA() {
    const pergunta = document.getElementById('pergunta-ia').value;
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!pergunta || !empresa) return showIAResposta("Preencha a pergunta e empresa.");
    showLoading();
    try {
        const resp = await fetch(`${API_IA}/perguntar`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pergunta, empresa_id: empresa.id })
        });
        const data = await readJson(resp);
        showIAResposta(data.resposta || "Erro ao perguntar à IA.");
    } catch (e) {
        showIAResposta("Erro ao perguntar à IA.");
    } finally { hideLoading(); }
}

function showIAResposta(msg) {
    const div = document.getElementById('ia-resposta');
    div.innerHTML = msg;
    div.style.display = 'block';
    setTimeout(()=>{div.style.display='none';}, 12000);
}
// ========== NOTIFICAÇÃO AUTOMÁTICA DE RETORNO DE CLIENTES ==========
function checarNotificacoesRetorno() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return;
    fetch(`${API_URL}/api/clientes_para_retorno/${empresa.id}`)
        .then(resp => readJson(resp))
        .then(clientes => {
            if (clientes && clientes.length) {
                const nomes = clientes.map(c => c.cliente_nome || c.nome).join(', ');
                const msg = `⚡ Clientes para retorno nesta semana: ${nomes}`;
                const notif = document.getElementById('notificacao-retorno');
                notif.textContent = msg;
                notif.style.display = 'block';
                setTimeout(()=>{notif.style.display='none';}, 8000);
            }
        });
}
window.addEventListener('DOMContentLoaded', checarNotificacoesRetorno);
// ========== LOGS DE AÇÕES (AUDITORIA/ADMIN) ==========
function carregarLogsAcoes() {
    showLoading();
    fetch(`${API_URL}/api/logs_acoes`)
        .then(resp => readJson(resp))
        .then(logs => {
            const container = document.getElementById('logs-acoes-list');
            if (!logs.length) {
                container.innerHTML = '<p>Nenhum log encontrado.</p>';
                return;
            }
            container.innerHTML = logs.map(l => `
                <div class="list-item">
                    <b>${l.acao.toUpperCase()}</b> ${l.entidade} #${l.entidade_id} por ${l.usuario} <br>
                    <small>${new Date(l.data).toLocaleString()}${l.detalhes ? '<br><i>'+l.detalhes+'</i>' : ''}</small>
                </div>
            `).join('');
        })
        .catch(()=>showToast('Erro ao carregar logs','error'))
        .finally(hideLoading);
}
// ========== EXPORTAÇÃO DE DADOS (CSV) ==========
function exportarCSV(tipo) {
    showLoading();
    let url = tipo==='clientes' ? `${API_URL}/api/clientes` : `${API_URL}/api/atendimentos`;
    fetchAuth(url)
        .then(resp => readJson(resp))
        .then(dados => {
            if (!Array.isArray(dados) || !dados.length) {
                showToast('Nenhum dado para exportar.','error');
                return;
            }
            const campos = Object.keys(dados[0]);
            const csv = [campos.join(',')].concat(
                dados.map(obj => campos.map(k => '"'+String(obj[k]).replace(/"/g,'""')+'"').join(','))
            ).join('\n');
            const blob = new Blob([csv], {type:'text/csv'});
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = tipo+"_"+new Date().toISOString().slice(0,10)+".csv";
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
            showToast('Exportação concluída!','success');
        })
        .catch(()=>showToast('Erro ao exportar dados.','error'))
        .finally(hideLoading);
}
// ========== ONBOARDING/DICAS ==========
function mostrarOnboarding() {
    if (localStorage.getItem('onboarding_visto')) return;
    document.getElementById('onboarding-modal').style.display = 'flex';
}
function fecharOnboarding() {
    document.getElementById('onboarding-modal').style.display = 'none';
    localStorage.setItem('onboarding_visto','1');
}
window.addEventListener('DOMContentLoaded', mostrarOnboarding);
// ========== SPINNER LOADING GLOBAL ==========
function showLoading() {
    document.getElementById('global-loading').style.display = 'flex';
}
function hideLoading() {
    document.getElementById('global-loading').style.display = 'none';
}
// ========== TOAST FEEDBACK ==========
function showToast(msg, type='success') {
    const toast = document.getElementById('toast-feedback');
    toast.textContent = msg;
    toast.className = 'toast ' + type;
    toast.style.display = 'block';
    setTimeout(() => { toast.style.display = 'none'; }, 2600);
}
// ========== CLIENTES PARA RETORNO ==========
async function loadClientesRetorno() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return;
    const container = document.getElementById('clientes-retorno');
    container.innerHTML = '<p>Carregando...</p>';
    try {
        const response = await fetchAuth(`${API_URL}/api/clientes_retorno/${empresa.id}`);
        const clientes = await readJson(response);
        if (response.ok) {
            if (clientes.length === 0) {
                container.innerHTML = '<p>Nenhum cliente para retorno.</p>';
            } else {
                const hoje = new Date();
                container.innerHTML = clientes.map(c => {
                    let classe = '';
                    if (c.data_proxima_revisao) {
                        const dataRetorno = new Date(c.data_proxima_revisao);
                        if (dataRetorno < hoje) {
                            classe = 'retorno-atrasado';
                        } else if ((dataRetorno - hoje) / (1000*60*60*24) <= 7) {
                            classe = 'retorno-proximo';
                        }
                    }
                    return `
                        <div class="list-item ${classe}">
                            <strong>${c.cliente_nome}</strong>
                            <p>Serviço: ${c.tipo_servico}</p>
                            <p>Retorno previsto: ${c.data_proxima_revisao ? formatarData(c.data_proxima_revisao) : '-'}</p>
                        </div>
                    `;
                }).join('');
            }
        } else {
            container.innerHTML = '<p>Erro ao carregar clientes para retorno.</p>';
        }
    } catch (e) {
        container.innerHTML = '<p>Erro ao carregar clientes para retorno.</p>';
    }
}

// ========== BUSCA GLOBAL DE CLIENTES ==========

const handleBuscaGlobal = debounce(async function() {
    const q = document.getElementById('busca-global').value.trim().toLowerCase();
    const container = document.getElementById('resultados-busca');
    if (!container) return;
    if (!q) {
        container.innerHTML = '';
        return;
    }
    try {
        const response = await fetchAuth(`${API_URL}/api/clientes`);
        if (!response) return;
        let clientes = await readJson(response);
        if (response.ok && Array.isArray(clientes)) {
            clientes = clientes.filter(c =>
                (c.nome || '').toLowerCase().includes(q) ||
                (c.telefone || '').replace(/\D/g, '').includes(q.replace(/\D/g, ''))
            );
            if (!clientes.length) {
                container.innerHTML = '<div class="cf-list-item"><span>Nenhum resultado.</span></div>';
                return;
            }
            container.innerHTML = clientes.slice(0, 6).map(c => `
                <div class="cf-list-item" onclick="mostrarHistoricoCliente(${c.id}, '${c.nome}')">
                    <strong>${c.nome}</strong>
                    <span>${formatarTelefone(c.telefone || '')}</span>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Erro ao buscar clientes:', error);
        container.innerHTML = '<div class="cf-list-item"><span>Erro na busca.</span></div>';
    }
}, 400);

// ========== HISTÓRICO POR CLIENTE ==========
async function mostrarHistoricoCliente(clienteId, nomeCliente) {
    const card = document.getElementById('historico-cliente-card');
    const container = document.getElementById('historico-cliente');
    const totalDiv = document.getElementById('cliente-total-gasto');
    card.style.display = 'block';
    container.innerHTML = '<p>Carregando histórico...</p>';
    totalDiv.textContent = '';
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/api/clientes/${clienteId}?token=${token}`);
        const perfil = await readJson(response);
        if (response.ok) {
            totalDiv.textContent = `Total já gasto: R$ ${perfil.total_gasto.toFixed(2)}`;
            if (!perfil.atendimentos || perfil.atendimentos.length === 0) {
                container.innerHTML = '<p>Nenhum atendimento registrado para este cliente.</p>';
            } else {
                container.innerHTML = perfil.atendimentos.map(at => `
                    <div class="list-item">
                        <p><strong>Valor:</strong> R$ ${at.valor_cobrado || '0,00'}</p>
                        <p><strong>Descrição:</strong> ${at.descricao || '-'}</p>
                        <p><strong>Data:</strong> ${at.data || '-'}</p>
                    </div>
                `).join('');
            }
        } else {
            totalDiv.textContent = '';
            container.innerHTML = '<p>Erro ao carregar histórico.</p>';
        }
    } catch (e) {
        totalDiv.textContent = '';
        container.innerHTML = '<p>Erro ao carregar histórico.</p>';
    }
}

function fecharHistoricoCliente() {
    document.getElementById('historico-cliente-card').style.display = 'none';
    document.getElementById('historico-cliente').innerHTML = '';
}

// ========== ESTATÍSTICAS DO DASHBOARD ==========
async function loadEstatisticasDashboard() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return;
    const container = document.getElementById('estatisticas-dashboard');
    container.innerHTML = '<p>Carregando...</p>';
    try {
        const response = await fetchAuth(`${API_URL}/api/estatisticas/${empresa.id}`);
        const stats = await readJson(response);
        if (response.ok) {
            let html = `
                <p><strong>Total de clientes:</strong> ${stats.total_clientes}</p>
                <p><strong>Total de atendimentos:</strong> ${stats.total_atendimentos}</p>
            `;
            if (typeof stats.tempo_medio_retorno !== 'undefined' && stats.tempo_medio_retorno !== null) {
                html += `<p><strong>Tempo médio de retorno:</strong> ${stats.tempo_medio_retorno} dias</p>`;
            }
            if (typeof stats.clientes_novos_mes !== 'undefined' && stats.clientes_novos_mes !== null) {
                html += `<p><strong>Clientes novos este mês:</strong> ${stats.clientes_novos_mes}</p>`;
            }
            html += `
                <p><strong>Último cliente:</strong> ${stats.ultimo_cliente ? stats.ultimo_cliente.nome + ' (' + formatarTelefone(stats.ultimo_cliente.telefone) + ')' : '-'}</p>
                <p><strong>Último atendimento:</strong> ${stats.ultimo_atendimento ? formatarDataHora(stats.ultimo_atendimento.data_atendimento) + ' - ' + stats.ultimo_atendimento.tipo_servico : '-'}</p>
            `;
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p>Erro ao carregar estatísticas.</p>';
        }
    } catch (e) {
        container.innerHTML = '<p>Erro ao carregar estatísticas.</p>';
    }
}

// ========== ATENDIMENTOS ==========
async function loadAtendimentos() {
    const token = localStorage.getItem('token');
    const tbody = document.getElementById('atendimentos-tbody');
    if (!tbody) return;
    showLoading();
    tbody.innerHTML = '<tr><td colspan="7">Carregando...</td></tr>';
    try {
        let url = `${API_URL}/api/atendimentos?token=${token}`;
        const periodo = document.getElementById('filtro-periodo')?.value;
        if (periodo) url += `&periodo=${periodo}`;
        const response = await fetch(url);
        let atendimentos = await readJson(response);
        if (response.ok) {
            // Ordenar por data_atendimento decrescente
            atendimentos = atendimentos.sort((a, b) => new Date(b.data_atendimento) - new Date(a.data_atendimento));
            if (atendimentos.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7">Nenhum atendimento registrado ainda.</td></tr>';
            } else {
                tbody.innerHTML = atendimentos.map(at => `
                    <tr>
                        <td>${at.cliente_nome}</td>
                        <td>${at.tipo_servico || '-'}</td>
                        <td>${at.descricao_servico || '-'}</td>
                        <td>${at.status_atendimento || '-'}</td>
                        <td>${formatarDataHora(at.data_atendimento)}</td>
                        <td><button class="btn-edit" onclick="editarAtendimento(${at.id})">✏️</button></td>
                        <td><button class="btn-delete" onclick="excluirAtendimento(${at.id})">🗑️</button></td>
                    </tr>
                `).join('');
            }
        } else {
            tbody.innerHTML = '<tr><td colspan="7">Erro ao carregar atendimentos.</td></tr>';
        }
    } catch (error) {
        console.error('Erro ao carregar atendimentos:', error);
        tbody.innerHTML = '<tr><td colspan="7">Erro ao carregar atendimentos.</td></tr>';
    } finally { hideLoading(); }
// ========== EDITAR/EXCLUIR ATENDIMENTO ==========
function editarAtendimento(id) {
    abrirModalEdicao('atendimento', id);
}

function excluirAtendimento(id) {
    if (!confirm('Tem certeza que deseja excluir este atendimento?')) return;
    const token = localStorage.getItem('token');
    fetch(`${API_URL}/api/atendimentos/${id}?token=${token}`, { method: 'DELETE' })
        .then(resp => {
            if (resp.ok) {
                showToast('Atendimento excluído com sucesso!','success');
                loadAtendimentos();
            } else {
                showToast('Erro ao excluir atendimento.','error');
            }
        })
        .catch(() => showToast('Erro ao excluir atendimento.','error'));
}
// ========== EDITAR/EXCLUIR CLIENTE ==========
function editarCliente(id) {
    abrirModalEdicao('cliente', id);
// ========== MODAL DE EDIÇÃO GENÉRICO ==========
let edicaoTipo = null;
let edicaoId = null;
function abrirModalEdicao(tipo, id) {
        edicaoTipo = tipo;
        edicaoId = id;
        const modal = document.getElementById('modal-edicao');
        const form = document.getElementById('form-edicao');
        form.innerHTML = '<p>Carregando...</p>';
        document.getElementById('modal-edicao-titulo').textContent = tipo === 'cliente' ? 'Editar Cliente' : 'Editar Atendimento';
        modal.style.display = 'flex';
        const token = localStorage.getItem('token');
        let url = tipo === 'cliente' ? `${API_URL}/api/clientes/${id}?token=${token}` : `${API_URL}/api/atendimentos/${id}?token=${token}`;
        fetch(url)
            .then(resp => resp.json())
            .then(data => {
                form.innerHTML = '';
                for (const [k, v] of Object.entries(data)) {
                    if (['id','empresa_id','cliente_id'].includes(k)) continue;
                    let label = k.replace(/_/g,' ').replace(/\b\w/g, l => l.toUpperCase());
                    if (k === 'status_atendimento') {
                        form.innerHTML += `<label>${label}<br><select name="status_atendimento">
                            <option value="Novo" ${v==='Novo'?'selected':''}>Novo</option>
                            <option value="Em andamento" ${v==='Em andamento'?'selected':''}>Em andamento</option>
                            <option value="Concluído" ${v==='Concluído'?'selected':''}>Concluído</option>
                        </select></label>`;
                        continue;
                    }
                    let inputType = typeof v === 'number' ? 'number' : (typeof v === 'string' && v.length > 60 ? 'textarea' : 'text');
                    if (k.includes('data')) inputType = 'date';
                    form.innerHTML += `<label>${label}<br>${inputType==='textarea'?`<textarea name="${k}">${v||''}</textarea>`:`<input name="${k}" type="${inputType}" value="${v||''}">`}</label>`;
                }
                form.innerHTML += '<button type="submit">Salvar</button>';
            });
}
function fecharModalEdicao() {
        document.getElementById('modal-edicao').style.display = 'none';
        edicaoTipo = null; edicaoId = null;
}
function salvarEdicao(e) {
        e.preventDefault();
        const form = e.target;
        const dados = {};
        for (const el of form.elements) {
            if (!el.name) continue;
            dados[el.name] = el.type === 'number' ? Number(el.value) : el.value;
        }
        const token = localStorage.getItem('token');
        let url = edicaoTipo === 'cliente' ? `${API_URL}/api/clientes/${edicaoId}?token=${token}` : `${API_URL}/api/atendimentos/${edicaoId}?token=${token}`;
        showLoading();
        fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        })
        .then(resp => {
            if (resp.ok) {
                showToast('Alterações salvas!','success');
                fecharModalEdicao();
                if (edicaoTipo === 'cliente') { if (typeof loadDashboard==='function') loadDashboard(); if (typeof loadClientesRecentes==='function') loadClientesRecentes(); }
                if (edicaoTipo === 'atendimento') { if (typeof loadAtendimentos==='function') loadAtendimentos(); }
            } else {
                showToast('Erro ao salvar alterações.','error');
            }
        })
        .finally(hideLoading);
}
}

function excluirCliente(id) {
    if (!confirm('Tem certeza que deseja excluir este cliente? Esta ação não poderá ser desfeita.')) return;
    const token = localStorage.getItem('token');
    fetch(`${API_URL}/api/clientes/${id}?token=${token}`, { method: 'DELETE' })
        .then(resp => {
            if (resp.ok) {
                showToast('Cliente excluído com sucesso!','success');
                if (typeof loadDashboard === 'function') loadDashboard();
                if (typeof loadClientesRecentes === 'function') loadClientesRecentes();
            } else {
                showToast('Erro ao excluir cliente.','error');
            }
        })
        .catch(() => showToast('Erro ao excluir cliente.','error'));
}
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

// ========== CLIENTES RECENTES ==========
async function loadClientesRecentes() {
    const token = localStorage.getItem('token');
    const container = document.getElementById('clientes-recentes');
    container.innerHTML = '<p>Carregando...</p>';
    try {
        const response = await fetch(`${API_URL}/api/clientes?token=${token}`);
        const clientes = await readJson(response);
        if (response.ok) {
            if (clientes.length === 0) {
                container.innerHTML = '<p>Nenhum cliente cadastrado ainda.</p>';
            } else {
                // Ordenar por data_primeiro_contato decrescente e pegar os 5 mais recentes
                const recentes = clientes.sort((a, b) => new Date(b.data_primeiro_contato) - new Date(a.data_primeiro_contato)).slice(0, 5);
                container.innerHTML = recentes.map(cliente => `
                    <div class="list-item">
                        <strong>${cliente.nome}</strong>
                        <p>📱 ${formatarTelefone(cliente.telefone)}</p>
                        <small>${formatarData(cliente.data_primeiro_contato)}</small>
                    </div>
                `).join('');
            }
        } else {
            container.innerHTML = '<p>Erro ao carregar clientes recentes.</p>';
        }
    } catch (error) {
        container.innerHTML = '<p>Erro ao carregar clientes recentes.</p>';
    }
}

// ========== ATENDIMENTOS RECENTES ==========
async function loadAtendimentosRecentes() {
    const token = localStorage.getItem('token');
    const container = document.getElementById('atendimentos-recentes');
    container.innerHTML = '<p>Carregando...</p>';
    try {
        const response = await fetch(`${API_URL}/api/atendimentos?token=${token}`);
        const atendimentos = await readJson(response);
        if (response.ok) {
            if (atendimentos.length === 0) {
                container.innerHTML = '<p>Nenhum atendimento registrado ainda.</p>';
            } else {
                // Ordenar por data_atendimento decrescente e pegar os 5 mais recentes
                const recentes = atendimentos.sort((a, b) => new Date(b.data_atendimento) - new Date(a.data_atendimento)).slice(0, 5);
                container.innerHTML = recentes.map(at => `
                    <div class="list-item">
                        <strong>${at.cliente_nome}</strong>
                        <p>${at.tipo_servico || '-'} - ${formatarDataHora(at.data_atendimento)}</p>
                        <small>${at.descricao_servico || '-'}</small>
                    </div>
                `).join('');
            }
        } else {
            container.innerHTML = '<p>Erro ao carregar atendimentos recentes.</p>';
        }
    } catch (error) {
        container.innerHTML = '<p>Erro ao carregar atendimentos recentes.</p>';
    }
}

// Chamar essas funções ao carregar o dashboard
const oldInitDashboard = window.initDashboard;
window.initDashboard = function() {
    if (typeof oldInitDashboard === 'function') oldInitDashboard();
    loadClientesRecentes();
    loadAtendimentosRecentes();
};

function filtrarClientesTabela() {
    const filtro = document.getElementById('filtro-clientes').value.toLowerCase();
    const linhas = document.querySelectorAll('#clientes-tbody tr');
    linhas.forEach(linha => {
        const nome = linha.children[0]?.textContent.toLowerCase() || '';
        const telefone = linha.children[1]?.textContent.toLowerCase() || '';
        if (nome.includes(filtro) || telefone.includes(filtro)) {
            linha.style.display = '';
        } else {
            linha.style.display = 'none';
        }
    });
}

// Atualizar loadDashboard para mostrar clientes ativos/inativos
const oldLoadDashboard = window.loadDashboard;
window.loadDashboard = async function() {
    try {
        const response = await fetchAuth(`${API_URL}/api/dashboard`);
        if (!response) return;
        const data = await readJson(response);
        if (!response.ok || !data) {
            if (response.status === 401) handleLogout();
            return;
        }

        const metricas = data.metricas || data.estatisticas || {};

        const setText = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        setText('total-clientes', metricas.total_clientes || 0);
        setText('total-atendimentos', metricas.total_atendimentos || 0);
        setText('clientes-novos', metricas.clientes_novos_periodo || metricas.clientes_novos_mes || 0);
        setText('taxa-atividade', `${metricas.taxa_atividade_diaria || 0}%`);
        setText('total-atendimentos-ring', metricas.total_atendimentos || 0);
        setText('total-clientes-ativos', metricas.total_clientes_ativos || 0);
        setText('total-clientes-inativos', metricas.total_clientes_inativos || 0);

        const container = document.getElementById('atendimentos-recentes');
        if (container) {
            const recentes = data.atendimentos_recentes || [];
            container.innerHTML = recentes.length === 0
                ? '<p>Nenhum atendimento registrado ainda.</p>'
                : recentes.map(at => `
                    <div class="cf-list-item">
                        <div>
                            <strong>${at.cliente_nome || '-'}</strong>
                            <p>${at.tipo_servico || at.tipo || '-'} • ${at.data || '-'}</p>
                        </div>
                        <span class="cf-badge">Em andamento</span>
                    </div>
                `).join('');
        }

        const rankingContainer = document.getElementById('ranking-clientes');
        if (rankingContainer) {
            const top = data.top_clientes || [];
            rankingContainer.innerHTML = top.length === 0
                ? '<p>Nenhum cliente ativo encontrado.</p>'
                : top.map((c, idx) => `
                    <div class="cf-list-item">
                        <strong>#${idx + 1} ${c.nome}</strong>
                        <span>${c.total_atendimentos} atendimentos</span>
                    </div>
                `).join('');
        }
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
    }
};

// Carregar gráficos do dashboard
async function loadGraficosDashboard() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return;
    // Atendimentos por mês
    const resAt = await fetchAuth(`${API_URL}/api/estatisticas/${empresa.id}`);
    if (!resAt) return;
    const dadosAt = await readJson(resAt);
    if (!dadosAt || !dadosAt.labels) return;
    if (window.graficoAtendimentos) window.graficoAtendimentos.destroy();
    const ctxAt = document.getElementById('grafico-atendimentos').getContext('2d');
    window.graficoAtendimentos = new Chart(ctxAt, {
        type: 'bar',
        data: {
            labels: dadosAt.labels,
            datasets: [{ label: 'Atendimentos', data: dadosAt.data, backgroundColor: '#6366f1' }]
        },
        options: { plugins: { legend: { display: false } } }
    });
    // Clientes por mês
    const resCl = await fetchAuth(`${API_URL}/api/estatisticas/${empresa.id}`);
    if (!resCl) return;
    const dadosCl = await readJson(resCl);
    if (!dadosCl || !dadosCl.labels) return;
    if (window.graficoClientes) window.graficoClientes.destroy();
    const ctxCl = document.getElementById('grafico-clientes').getContext('2d');
    window.graficoClientes = new Chart(ctxCl, {
        type: 'line',
        data: {
            labels: dadosCl.labels,
            datasets: [{ label: 'Novos Clientes', data: dadosCl.data, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.2)', fill: true }]
        },
        options: { plugins: { legend: { display: false } } }
    });
}

// Chamar ao carregar dashboard
const oldInitDashboardCharts = window.initDashboard;
window.initDashboard = function() {
    if (typeof oldInitDashboardCharts === 'function') oldInitDashboardCharts();
    if (window.Chart) loadGraficosDashboard();
};

async function loadClientesInativos() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return;
    const container = document.getElementById('clientes-inativos');
    container.innerHTML = '<p>Carregando...</p>';
    try {
        const response = await fetch(`${API_URL}/api/clientes_inativos/${empresa.id}`);
        const clientes = await readJson(response);
        if (clientes.length === 0) {
            container.innerHTML = '<p>Nenhum cliente inativo.</p>';
        } else {
            container.innerHTML = clientes.map(c => `
                <div class="list-item">
                    <strong>${c.nome}</strong>
                    <p>📱 ${formatarTelefone(c.telefone)}</p>
                </div>
            `).join('');
        }
    } catch (e) {
        container.innerHTML = '<p>Erro ao carregar clientes inativos.</p>';
    }
}

async function loadClientesParaRetorno() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return;
    const container = document.getElementById('clientes-para-retorno');
    container.innerHTML = '<p>Carregando...</p>';
    try {
        const response = await fetch(`${API_URL}/api/clientes_para_retorno/${empresa.id}`);
        const clientes = await readJson(response);
        if (clientes.length === 0) {
            container.innerHTML = '<p>Nenhum cliente para retorno.</p>';
        } else {
            container.innerHTML = clientes.map(c => `
                <div class="list-item">
                    <strong>${c.cliente_nome}</strong>
                    <p>Serviço: ${c.tipo_servico}</p>
                    <p>Retorno previsto: ${c.data_proxima_revisao ? formatarData(c.data_proxima_revisao) : '-'}</p>
                </div>
            `).join('');
        }
    } catch (e) {
        container.innerHTML = '<p>Erro ao carregar clientes para retorno.</p>';
    }
}

async function loadRankingClientes() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return;
    const container = document.getElementById('ranking-clientes');
    container.innerHTML = '<p>Carregando...</p>';
    try {
        const response = await fetch(`${API_URL}/api/ranking_clientes/${empresa.id}`);
        const ranking = await readJson(response);
        if (ranking.length === 0) {
            container.innerHTML = '<p>Nenhum dado.</p>';
        } else {
            container.innerHTML = ranking.map((c, i) => `
                <div class="list-item">
                    <span style="font-weight:bold;">#${i+1}</span> ${c.nome} <span style="float:right;">${c.qtd} atendimentos</span>
                </div>
            `).join('');
        }
    } catch (e) {
        container.innerHTML = '<p>Erro ao carregar ranking.</p>';
    }
}

async function loadServicosComuns() {
    const empresa = JSON.parse(localStorage.getItem('empresa'));
    if (!empresa) return;
    const container = document.getElementById('servicos-comuns');
    container.innerHTML = '<p>Carregando...</p>';
    try {
        const response = await fetch(`${API_URL}/api/servicos_comuns/${empresa.id}`);
        const servicos = await readJson(response);
        if (servicos.length === 0) {
            container.innerHTML = '<p>Nenhum dado.</p>';
        } else {
            container.innerHTML = servicos.map(s => `
                <div class="list-item">
                    <span>${s.tipo_servico}</span> <span style="float:right;">${s.qtd} atendimentos</span>
                </div>
            `).join('');
        }
    } catch (e) {
        container.innerHTML = '<p>Erro ao carregar serviços.</p>';
    }
}

// Chamar ao carregar dashboard
const oldInitDashboardClientes = window.initDashboard;
window.initDashboard = function() {
    if (typeof oldInitDashboardClientes === 'function') oldInitDashboardClientes();
    loadClientesInativos();
    loadClientesParaRetorno();
    loadRankingClientes();
    loadServicosComuns();
};
