# Quiz App com Python, Flet e Google Sheets - Preparatório para a SFPC™

Este é um aplicativo de quiz interativo em desenvolvimento que visa proporcionar uma experiência desafiadora e engajadora para testar seus conhecimentos em preparação para a Scrum Foundation Professional Certification (SFPC™). Vamos ou Bora?! 🚀

**Detalhes do Exame:**

* **Formato:** Perguntas de múltipla escolha
* **Perguntas:** 40.
* **Livro aberto:** Não
* **Idioma:** Inglês / Espanhol / Português (em desenvolvimento)
* **Pontuação de aprovação:** 32/40 (80%) - Ver.2020
* **Duração:** 60 minutos

## Tela Inicial:

A tela inicial do aplicativo já está implementada, proporcionando uma recepção agradável e intuitiva aos usuários. Ela conta com:

- Um título centralizado "Quiz - SFPC™".
- Um ícone da CertiProf, simbolizando a certificação alvo do quiz.
- Um botão "Iniciar Quiz", pronto para conduzir os usuários à experiência interativa do quiz.
- Um botão "Fechar", oferecendo a flexibilidade de sair do aplicativo a qualquer momento.
- Um botão "Certificação agora!", que leva o usuário ao site da CertiProf para mais informações sobre a certificação.

## Funcionalidades:

### Em Desenvolvimento Ativo:

- **Funcionalidades Essenciais do Quiz:**
    - Apresentação de quatro opções de resposta para cada pergunta. ✅
    - Implementação de um temporizador de 1 hora. ✅
    - Feedback imediato sobre a resposta escolhida, informando se está correta ou incorreta. ✅
    - Cálculo e exibição da pontuação final, acompanhada de uma mensagem clara de aprovação ou reprovação. ✅
- **Melhorias na Experiência do Usuário (UX):**
    - Exibir link para download do Guia Scrum para usuários não aprovados.
    - Retornar à tela inicial ao fechar o modal de resultados.
    - Refinar a reprodução de áudio para momentos específicos do quiz.

### Funcionalidades Implementadas:

- **Base Sólida:**
    - Lógica principal do quiz, incluindo o controle das perguntas, respostas, temporizador e pontuação. ✅
    - Interface da tela inicial com elementos centralizados e botões com tamanho otimizado. ✅
    - Estrutura de código organizada com o padrão MVC (Model-View-Controller). ✅
    - Implementação de um sistema de cache offline usando JSON. ✅
    - Integração com Google Sheets para carregar perguntas. ✅
    - Integração com Google Docs para carregar perguntas. ✅
    - Monitoramento contínuo do Google Docs para atualização automática. ✅
    - Seletor de tema claro/escuro. ✅
    - Correção da lógica de pontuação do quiz. ✅

## Configuração das Credenciais do Google Cloud:

**Para usar este aplicativo, você precisará configurar credenciais do Google Cloud para acessar o Google Sheets e o Google Docs. Siga estas etapas:**

1. **Criar um projeto no Google Cloud Platform:**
   - Acesse o Google Cloud Console: [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Crie um novo projeto ou selecione um existente.

2. **Ativar as APIs necessárias:**
   - **Google Sheets API:**
     - Na barra de pesquisa, digite "Google Sheets API" e ative a API.
   - **Google Docs API:**
     - Na barra de pesquisa, digite "Google Docs API" e ative a API.

3. **Criar duas contas de serviço, uma para o Google Sheets e outra para o Google Docs:**
   - No menu à esquerda, vá para "IAM e administração" -> "Contas de serviço".
   - Clique em "Criar conta de serviço".
   - Dê um nome à conta de serviço (ex: "quiz-app-sheets-service" para o Google Sheets e "quiz-app-docs-service" para o Google Docs).
   - Deixe as opções padrão para a função.
   - Clique em "Criar e continuar" e depois em "Concluído".

4. **Gerar chaves JSON para cada conta de serviço:**
   - Na lista de contas de serviço, localize cada conta que você criou e clique nos três pontos à direita.
   - Selecione "Gerenciar chaves".
   - Clique em "Adicionar chave" -> "Criar nova chave".
   - Escolha o tipo de chave "JSON" e clique em "Criar".
   - Um arquivo JSON será baixado para cada conta de serviço. 
     - Renomeie os arquivos para **`credentials_sheets.json`** (para a conta de serviço do Google Sheets) e **`credentials_docs.json`** (para a conta de serviço do Google Docs).
   - Mova os arquivos JSON para o diretório do seu projeto. **Atenção:** Nunca faça commit desses arquivos no seu repositório Git!

5. **Conceder permissões às contas de serviço:**
   - **Google Sheets:**
     - Abra a planilha do Google Sheets.
     - Clique em "Compartilhar".
     - Adicione o endereço de e-mail da conta de serviço do Google Sheets (`quiz-app-sheets-service`) com a permissão "Editor".
   - **Google Docs:**
     - Abra o documento do Google Docs.
     - Clique em "Compartilhar".
     - Adicione o endereço de e-mail da conta de serviço do Google Docs (`quiz-app-docs-service`) com a permissão "Leitor".

## Execução do Aplicativo:

1. **Certifique-se de ter o Flet versão 0.23.0 ou superior instalado.** 
2. **Instale as dependências:** `pip install -r requirements.txt`
3. **Configure as variáveis de ambiente para os caminhos dos arquivos de credenciais (`credentials_sheets.json` e `credentials_docs.json`).**
4. **Execute o aplicativo:** `flet run`
   - O aplicativo iniciará e o monitoramento do Google Docs será executado em segundo plano automaticamente.

## Formato das Perguntas no Google Docs:

- **A pergunta em si e a resposta correta devem estar formatadas em negrito.**
- As opções de resposta devem ser formatadas com letras (a), b), c), d)).

## Próximos Passos:

O desenvolvimento do Quiz App está em ritmo acelerado! Nossos próximos passos incluem:

- **Finalizar as funcionalidades essenciais do quiz em andamento.**
- Implementar testes abrangentes para garantir a qualidade do código e a robustez do aplicativo.
- Realizar testes de usabilidade com usuários reais para coletar feedback e aprimorar a experiência do usuário.
- Explorar opções de implantação para disponibilizar o quiz online e torná-lo acessível a todos.
- **Publicar o Aplicativo:** 
    - Seguir as instruções de publicação do Flet: [https://flet.dev/docs/publish](https://flet.dev/docs/publish)
    - Explorar opções de publicação, como Flet Cloud, Streamlit Cloud, Heroku, PythonAnywhere, entre outras.
    - Definir a melhor plataforma de publicação com base nas necessidades do projeto e do público-alvo.

## Como Contribuir:

Acreditamos no poder da comunidade e suas contribuições são muito valiosas para nós! Se você quiser participar do desenvolvimento deste projeto, sinta-se à vontade para:

- Explorar o código-fonte e reportar bugs.
- Propor novas funcionalidades ou melhorias.
- Criar pull requests com correções ou implementações.

Juntos, podemos tornar este Quiz App ainda mais incrível!
