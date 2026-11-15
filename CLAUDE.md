<!--
  Arquivo: CLAUDE.md
  Para que serve: as regras que o Claude Code segue ao trabalhar neste repositório (Quiz SFPC).
  É lido em toda conversa: fica curto e muda quando uma decisão mudar.
-->

# CLAUDE.md · Quiz SFPC

- **O que é:** simulado para a certificação **Scrum Foundation Professional Certificate (SFPC™)**, em Python + Flet:
  perguntas de múltipla escolha, cronômetro e nota final. As perguntas vêm de uma planilha e ficam guardadas no app (`quiz_cache.json`, 130 perguntas).
- **Rumo (15/11/2026):** virar **app Android (APK) para celular e TV**, usando o que já existe. O APK é gerado pelo GitHub Actions com `flet build apk`
  (repositório público não gasta a cota grátis). Este é o **primeiro** dos apps Android a sair.
- **Pessoas:** Gleyson Atanazio (desenvolvedor e Scrum Master) e a PO e QA do time, que testa cada APK no celular e na TV antes de publicar.
- **Autonomia:** o Claude cria branch, commit, push e PR sem pedir. O merge e a publicação (Releases do GitHub, Play Store) são do Gleyson.
- **Idioma:** tudo em português do Brasil, em linguagem simples, com todo termo técnico explicado.

## Onde está cada coisa

| O quê | Onde |
|---|---|
| Telas, controle e dados | `app/views.py`, `app/controllers.py`, `app/models.py` |
| Regras do quiz (cronômetro, resposta, resultado) | `quiz_logic.py` |
| Perguntas guardadas no app | `quiz_cache.json` |
| Atualizar as perguntas a partir da planilha | `automate_spreadsheet.py` (precisa de credencial do Google, que **nunca** entra no Git) |
| O que falta fazer | [ROADMAP.md](ROADMAP.md) |
| O que aprendi | [APRENDIZADO.md](APRENDIZADO.md) |

## Definição de Pronto

1. O app abre e funciona **sem internet**, usando `quiz_cache.json`.
2. O APK gerado pelo GitHub Actions instala e abre no celular; a PO e QA marcou o teste como aprovado no painel do time.
3. 3 linhas de "o que aprendi" no [APRENDIZADO.md](APRENDIZADO.md).

## Regras que não mudam

- **Nenhuma credencial, senha ou token no repositório nem dentro do APK.** O app lê só o arquivo de perguntas.
- **Marca:** SFPC™ e CertiProf são marcas de terceiros; o app é um simulado de estudo, sem ligação oficial, e diz isso na tela inicial.
- **Código comentado para qualquer pessoa entender** (regra inegociável do Gleyson): vale para todo arquivo criado ou alterado, inclusive o workflow YAML.
