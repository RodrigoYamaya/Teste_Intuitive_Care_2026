<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

// --- ESTADO (Variáveis) ---
const operadoras = ref([])
const busca = ref('')
const page = ref(1)
const totalPages = ref(1)
const loading = ref(false)
const modalAberto = ref(false)
const opSelecionada = ref(null)
const despesas = ref([])

// Configuração da API (aponta para o seu Backend)
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api'
})

// --- FUNÇÕES ---

// 1. Carregar Operadoras
const carregarOperadoras = async () => {
  loading.value = true
  try {
    const res = await api.get('/operadoras', {
      params: {
        page: page.value,
        limit: 10,
        busca: busca.value
      }
    })
    operadoras.value = res.data.data
    totalPages.value = res.data.meta.total_pages
  } catch (error) {
    console.error(error)
    alert('Erro ao conectar. Verifique se o Backend (Python) está rodando!')
  } finally {
    loading.value = false
  }
}

// 2. Abrir Modal com Detalhes
const abrirDetalhes = async (cnpj) => {
  try {
    const resOp = await api.get(`/operadoras/${cnpj}`)
    opSelecionada.value = resOp.data

    const resDesp = await api.get(`/operadoras/${cnpj}/despesas`)
    despesas.value = resDesp.data

    modalAberto.value = true
  } catch (error) {
    alert('Erro ao carregar detalhes.')
  }
}

// 3. Fechar Modal
const fecharModal = () => {
  modalAberto.value = false
  opSelecionada.value = null
  despesas.value = []
}

// 4. Navegação
const mudarPagina = (novaPagina) => {
  if (novaPagina >= 1 && novaPagina <= totalPages.value) {
    page.value = novaPagina
    carregarOperadoras()
  }
}

// 5. Busca (Delay para não buscar a cada letra digitada)
let timeout = null
const aoDigitar = () => {
  clearTimeout(timeout)
  timeout = setTimeout(() => {
    page.value = 1
    carregarOperadoras()
  }, 500)
}

// Inicializa
onMounted(() => {
  carregarOperadoras()
})
</script>

<template>
  <div class="container">
    <header>
      <h1>🔍 Portal ANS</h1>
      <input
        v-model="busca"
        @input="aoDigitar"
        placeholder="Busque por Razão Social..."
      />
    </header>

    <main>
      <div v-if="loading" class="loading">Carregando...</div>

      <table v-else>
        <thead>
          <tr>
            <th>CNPJ</th>
            <th>Razão Social</th>
            <th>Modalidade</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="op in operadoras" :key="op.cnpj">
            <td>{{ op.cnpj }}</td>
            <td>{{ op.razao_social }}</td>
            <td>{{ op.modalidade }}</td>
            <td>
              <button @click="abrirDetalhes(op.cnpj)" class="btn-detalhes">
                Detalhes
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="page === 1" @click="mudarPagina(page - 1)">Anterior</button>
        <span>Página {{ page }} de {{ totalPages }}</span>
        <button :disabled="page === totalPages" @click="mudarPagina(page + 1)">Próximo</button>
      </div>
    </main>

    <div v-if="modalAberto" class="modal-overlay" @click.self="fecharModal">
      <div class="modal">
        <button class="close-btn" @click="fecharModal">×</button>
        <div v-if="opSelecionada">
          <h2>{{ opSelecionada.razao_social }}</h2>
          <p><strong>CNPJ:</strong> {{ opSelecionada.cnpj }}</p>
          <p><strong>UF:</strong> {{ opSelecionada.uf || 'N/A' }}</p>

          <h3>Histórico de Despesas</h3>
          <div class="scroll-table">
            <table class="mini-table">
              <thead>
                <tr>
                  <th>Ano/Trimestre</th>
                  <th>Valor</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(d, i) in despesas" :key="i">
                  <td>{{ d.ano }}/{{ d.trimestre }}</td>
                  <td>R$ {{ d.valor.toLocaleString('pt-BR', {minimumFractionDigits: 2}) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* Design Profissional e Limpo */
:root { --primary: #007bff; --bg: #f8f9fa; }
body { font-family: sans-serif; background: var(--bg); margin: 0; padding: 20px; }
.container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
h1 { color: #333; margin: 0; font-size: 1.5rem; }
input { padding: 8px; width: 300px; border: 1px solid #ccc; border-radius: 4px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #eee; }
.btn-detalhes { background: var(--primary); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
.pagination { margin-top: 20px; display: flex; justify-content: center; gap: 10px; align-items: center; }
.pagination button { padding: 5px 10px; cursor: pointer; }
.pagination button:disabled { opacity: 0.5; }
/* Modal */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }
.modal { background: white; padding: 20px; border-radius: 8px; width: 500px; max-height: 80vh; overflow-y: auto; position: relative; }
.close-btn { position: absolute; top: 10px; right: 10px; border: none; background: none; font-size: 1.5rem; cursor: pointer; }
.mini-table th { background: #666; color: white; }
</style>