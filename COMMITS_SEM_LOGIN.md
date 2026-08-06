# Guia de Segurança Git: Commits e Pushes em Computadores Públicos

Programar em computadores de laboratórios públicos exige cuidados extras de segurança para não deixar suas credenciais do GitHub salvas na máquina física de terceiros. Abaixo estão os caminhos seguros para configurar o Git, commitar e enviar seu código para a nuvem.

---

## 🔒 1. Como fazer Commits Locais com segurança (Sem Login Global)
Para fazer commits locais, o Git exige apenas um nome e um e-mail. Em computadores públicos, **nunca** use a flag `--global`. Use a flag `--local` para que suas informações fiquem gravadas apenas dentro da pasta oculta `.git` do seu projeto.

Ao abrir o terminal no laboratório, digite:
```bash
# Configura o Git apenas para a pasta deste projeto atual
git config --local user.name "Seu Nome Completo"
git config --local user.email "seu_email_do_github@email.com"

# Adiciona e faz o commit local (não exige login de internet ou senha)
git add .
git commit -m "Minha mensagem de commit"
```
*Se você fechar a pasta ou desligar o PC, essas configurações não ficarão salvas na máquina do laboratório.*

---

## 🌐 2. Como enviar (Push) para o GitHub de forma segura
Para enviar seu código local para o servidor do GitHub sem deixar suas senhas gravadas na máquina do laboratório, escolha um destes três métodos:

### Método A: Usar o GitHub Codespaces (O mais recomendado)
Se você desenvolver seu projeto dentro do **GitHub Codespaces** no navegador, você **não precisa digitar nenhuma senha ou token** para dar `push`.
- O Codespaces é uma máquina virtual que já inicia autenticada com a sua conta do GitHub.
- Você digita apenas:
  ```bash
  git add .
  git commit -m "Atualizando projeto"
  git push origin main
  ```
- O envio é imediato. Ao fechar a aba do navegador e deslogar do site do GitHub, ninguém no laboratório terá acesso à sua conta.

---

### Método B: Desativar o Gerenciador de Credenciais (Ao usar o Git local do PC)
Se você estiver usando o terminal do computador do laboratório e quiser dar `git push`, certifique-se de que a máquina não vai salvar seu Token de Acesso de forma permanente.

1. Rode este comando no terminal para desativar a gravação de senhas:
   ```bash
   git config --global credential.helper ""
   ```
2. Crie um **Personal Access Token (PAT)** temporário nas configurações do seu GitHub (*Settings -> Developer Settings -> Personal Access Tokens*).
3. Ao dar `git push`, o Git pedirá seu usuário e senha. **Use o Token criado como se fosse a sua senha**.
4. Como desativamos o `credential.helper`, ao fechar o terminal, a máquina esquecerá o Token.

---

### Método C: Upload Direto pelo Navegador (Sem usar terminal)
Para quem tem muita dificuldade com o Git no terminal em computadores públicos:
1. Acesse o site do GitHub no navegador e entre no seu repositório.
2. Clique no botão **"Add file" -> "Upload files"**.
3. Arraste e solte seus arquivos modificados diretamente na página.
4. Digite a mensagem de alteração no campo e clique em **"Commit changes"**.
5. **Importante**: Lembre-se de clicar em "Sign Out" (Sair) da sua conta no site do GitHub antes de ir embora do laboratório.
