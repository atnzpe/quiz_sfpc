# Quiz App com Python, Flet e Google Sheets

Este é um aplicativo de quiz interativo em desenvolvimento que visa proporcionar uma experiência desafiadora e engajadora para testar seus conhecimentos sobre Scrum.

## Tela Inicial:

A tela inicial do aplicativo já está implementada, proporcionando uma recepção agradável e intuitiva aos usuários. Ela conta com:

- Um ícone do Scrum, que simboliza a metodologia ágil empregada no desenvolvimento do projeto, priorizando iterações rápidas e eficientes.
- Um botão "Iniciar Quiz", claro e convidativo, pronto para conduzir os usuários à experiência interativa do quiz.
- Um botão "Fechar", oferecendo a flexibilidade de sair do aplicativo a qualquer momento.


## Funcionalidades:

### Em Desenvolvimento Ativo:

- **Funcionalidades Essenciais do Quiz:**
    - Apresentação de quatro opções de resposta para cada pergunta, desafiando o conhecimento dos usuários de forma eficaz.
    - Implementação de um temporizador de 1 hora para criar uma atmosfera de desafio e simular um ambiente de teste real.
    - Feedback imediato sobre a resposta escolhida, informando se está correta ou incorreta, e permitindo que os usuários aprendam durante o processo.
    - Cálculo e exibição da pontuação final, acompanhada de uma mensagem clara de aprovação ou reprovação, motivando os usuários a melhorar seu desempenho.

### Funcionalidades Implementadas:

- **Base Sólida:**
    - Lógica principal do quiz, incluindo o controle das perguntas, respostas, temporizador e pontuação, fornecendo uma base sólida para o desenvolvimento futuro.
    - Interface da tela inicial, proporcionando uma primeira impressão positiva e intuitiva aos usuários, convidando-os a iniciar o quiz.
    - Estrutura de código organizada em múltiplos arquivos, cada um com sua responsabilidade bem definida, facilitando a manutenção e a evolução do projeto. 
    - Implementação de um sistema de cache offline usando JSON, garantindo que os usuários possam aproveitar o quiz mesmo sem conexão com a internet.
    - Integração com Google Sheets para carregar perguntas, permitindo que o conteúdo do quiz seja gerenciado de forma externa e fácil.
    - Integração com Google Docs para carregar perguntas, automatizando o processo de atualização do quiz a partir de um documento centralizado.
    - Monitoramento contínuo do Google Docs para atualização automática, garantindo que o quiz esteja sempre atualizado com as últimas perguntas.

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

3. **Criar uma conta de serviço:**
   - No menu à esquerda, vá para "IAM e administração" -> "Contas de serviço".
   - Clique em "Criar conta de serviço".
   - Dê um nome à conta de serviço (ex: "quiz-app-sheets-service" para o Google Sheets e "quiz-app-docs-service" para o Google Docs).
   - Deixe as opções padrão para a função.
   - Clique em "Criar e continuar" e depois em "Concluído".

4. **Gerar chaves JSON:**
   - Na lista de contas de serviço, localize a conta que você acabou de criar e clique nos três pontos à direita.
   - Selecione "Gerenciar chaves".
   - Clique em "Adicionar chave" -> "Criar nova chave".
   - Escolha o tipo de chave "JSON" e clique em "Criar".
   - Um arquivo JSON será baixado. 
     - Renomeie o arquivo para **`credentials.json`** para a conta de serviço do Google Sheets.
     - Renomeie o arquivo para **`credentials_docs.json`** para a conta de serviço do Google Docs.
   - Mova os arquivos JSON para o diretório do seu projeto.

5. **Conceder permissões:**
   - **Google Sheets:**
     - Abra a planilha do Google Sheets.
     - Clique em "Compartilhar".
     - Adicione o endereço de e-mail da conta de serviço do Google Sheets com a permissão "Editor".
   - **Google Docs:**
     - Abra o documento do Google Docs.
     - Clique em "Compartilhar".
     - Adicione o endereço de e-mail da conta de serviço do Google Docs com a permissão "Leitor".

## Execução do Aplicativo:

1. **Instale as dependências:** `pip install -r requirements.txt`
2. **Execute o aplicativo:** `flet run`
   - O aplicativo iniciará e o monitoramento do Google Docs será executado em segundo plano automaticamente.

## Formato das Perguntas no Google Docs:

- As perguntas devem estar numeradas (ex: 1., 2., 3., etc.).
- A pergunta em si e a resposta correta devem estar formatadas em **negrito**.
- As opções de resposta devem ser formatadas com letras (a), b), c), d)).

## Próximos Passos:

O desenvolvimento do Quiz App está em ritmo acelerado! Nossos próximos passos incluem:

- **Finalizar as funcionalidades essenciais do quiz em andamento.**
- Implementar testes abrangentes para garantir a qualidade do código e a robustez do aplicativo.
- Realizar testes de usabilidade com usuários reais para coletar feedback e aprimorar a experiência do usuário.
- Explorar opções de implantação para disponibilizar o quiz online e torná-lo acessível a todos.

## Como Contribuir:

Acreditamos no poder da comunidade e suas contribuições são muito valiosas para nós! Se você quiser participar do desenvolvimento deste projeto, sinta-se à vontade para:

- Explorar o código-fonte e reportar bugs.
- Propor novas funcionalidades ou melhorias.
- Criar pull requests com correções ou implementações.

Juntos, podemos tornar este Quiz App ainda mais incrível!

