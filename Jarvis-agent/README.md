# JARVIS v2.0 — AI Agent estilo Claude Code

Assistente de IA com controle real do PC: lê, edita e cria arquivos, executa comandos,
faz planos de ação, confirma antes de ações destrutivas.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edita .env com sua GROQ_API_KEY
python main.py
