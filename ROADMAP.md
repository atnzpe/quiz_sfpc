<!--
  Arquivo: ROADMAP.md
  Para que serve: o caminho do Quiz SFPC até o APK para celular e TV, em ordem.
  Atualizado em 15/11/2026.
-->

# Roadmap · Quiz SFPC

## Já feito

- [x] Tela inicial (título, ícone, Iniciar, Fechar e link para a certificação)
- [x] Perguntas de múltipla escolha com cronômetro e resultado final
- [x] 130 perguntas guardadas no app (`quiz_cache.json`), com conferência de internet

## Agora: versão 1 no celular

1. [ ] Conferir o app no computador: 40 perguntas por prova, 60 minutos, aprovação com 32 de 40 (80%)
2. [ ] Garantir que o app usa **só** o `quiz_cache.json` (sem credencial do Google dentro do APK)
3. [ ] Aviso na tela inicial: "simulado de estudo, sem ligação oficial com a CertiProf"
4. [ ] `pyproject.toml` com nome, versão e ícone do app (o que o `flet build` lê)
5. [ ] Workflow do GitHub Actions que gera o APK a cada versão (`flet build apk`) e guarda o arquivo para baixar
6. [ ] Teste no celular Android: instalar, abrir sem internet, girar a tela, fazer uma prova inteira

## Depois

7. [ ] Teste na TV Android: usar só o controle remoto (setas e OK)
8. [ ] Publicar o APK nas Releases do GitHub (grátis)
9. [ ] Play Store (US$ 25 uma vez), só se fizer sentido e com o sim do Gleyson
10. [ ] Perguntas em inglês e espanhol
