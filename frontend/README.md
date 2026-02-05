# Interface Web - Portal de Despesas ANS

Este módulo contém a interface de usuário (Frontend) desenvolvida para visualizar os dados processados pelo ETL e servidos pela API.

## 🛠️ Tecnologias Utilizadas
* **Vue.js 3 (Composition API):** Framework progressivo e reativo.
* **Vite:** Build tool de alta performance.
* **Axios:** Cliente HTTP para comunicação com a API.
* **CSS Nativo:** Estilização leve e sem dependências externas.

---

## ⚖️ Trade-offs e Decisões de Arquitetura

### 1. Escolha do Framework (Vue.js vs React/Angular)
* **Decisão:** Utilização do Vue.js 3.
* **Justificativa:** O Vue oferece a curva de aprendizado mais rápida e simplicidade e tambem era requisito do teste

### 2. Estrutura de Componentes (Single File Component)
* **Decisão:** Centralização da lógica no `App.vue` sem uso de `Vue Router`.
* **Justificativa (KISS - Keep It Simple, Stupid):**
    * Como o requisito do teste é uma tela única com modal, implementar um Router ou dividir em múltiplos micro-componentes seria **Over-engineering** (complexidade desnecessária).
    * A abordagem monolítica neste contexto específico facilita a leitura do código pelo avaliador e reduz o tamanho do bundle final.

### 3. Gerenciamento de Estado (Reactivity API vs Pinia/Vuex)
* **Decisão:** Uso de estado local com `ref()` e `reactive()`.
* **Justificativa:** O escopo da aplicação não exige compartilhamento de estado global complexo. Introduzir Pinia ou Redux adicionaria camadas de abstração sem benefício real para uma aplicação de uma única página.

### 4. Estilização (CSS Scoped vs Bootstrap/Tailwind)
* **Decisão:** CSS nativo com escopo local.
* **Justificativa:**
    * **Performance:** Evita o carregamento de bibliotecas pesadas de UI.
    * **Demonstração de Competência:** Mostra domínio dos fundamentos de CSS (Flexbox, Posicionamento, Variáveis) sem depender de frameworks prontos.

---

## 🚀 Como Rodar o Frontend

1. Entre na pasta:
   ```bash
   cd frontend
Instale as dependências:

Bash
**npm install**
Execute o servidor de desenvolvimento:

Bash
**npm run dev**
Acesse no navegador: http://localhost:5173


---
