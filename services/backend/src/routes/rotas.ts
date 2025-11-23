import { authMiddleware } from './../middlewares/auth';
import bcrypt from "bcryptjs";
import jwt, { SignOptions } from "jsonwebtoken";
import { Router } from "express";
import db from "../db/db";
import axios from "axios";
import {
  atualizarRelatorio,
  excluirRelatorio,
  gerarRelatorioGeral,
  gerarRelatorioSku,
  gerarAssertividadeSkus,
  listarRelatorios,
  debugRelatorios,
} from "../controllers/RelatorioController";
import { enviarRelatorioPorEmail } from "../controllers/enviarEmailController";
import { atualizarUsuario, cadastrarUsuario, deletarUsuario, listarUsuarios, obterUsuarioAtual } from "../controllers/UsuarioController";
import { isAdminMiddleware } from "../middlewares/isAdmin";
import { forgotPassword, resetPassword } from "../controllers/PasswordController";
import chatController from "../controllers/chatController";

const PLN_URL = "http://127.0.0.1:5000";
const router = Router();

/* Rotas de usuários */
router.post("/usuario/cadastrar", cadastrarUsuario);
router.get("/usuario/listar", authMiddleware, isAdminMiddleware, listarUsuarios);
router.delete("/usuario/deletar/:id", authMiddleware, isAdminMiddleware, deletarUsuario);
router.put("/usuario/atualizar/:id", authMiddleware, isAdminMiddleware, atualizarUsuario);
router.get("/usuario/atual", authMiddleware, obterUsuarioAtual);


// rotas relatório
router.post("/relatorio/geral", authMiddleware, gerarRelatorioGeral);
router.post("/relatorio/skus", authMiddleware, gerarRelatorioSku);
router.post("/relatorio/skus-assertividade", authMiddleware, gerarAssertividadeSkus);
router.get("/relatorio/listar", authMiddleware, listarRelatorios);
router.get("/relatorio/debug", debugRelatorios);
router.post("/relatorio/enviar-email", authMiddleware, enviarRelatorioPorEmail);
router.delete("/relatorio/:id", authMiddleware, excluirRelatorio);
router.put("/relatorio/atualizar/:id", authMiddleware, atualizarRelatorio);


router.post("/chat", authMiddleware, chatController.enviarMensagem);
router.post("/chat/criar", authMiddleware, chatController.criarChat);
router.get("/chats", authMiddleware, chatController.listarChats);
router.get("/chat/:chatId/mensagens", authMiddleware, chatController.listarMensagens);
router.put("/chat/:chatId/titulo", authMiddleware, chatController.atualizarTitulo);
router.delete("/chat/:id",authMiddleware, chatController.excluirChat);



/* Rota para autenticação */
const JWT_SECRET: string = process.env.JWT_SECRET!;
if (!JWT_SECRET) {
  console.error("JWT_SECRET não configurado. Crie um .env com JWT_SECRET.");
  process.exit(1);
}

const JWT_EXPIRES_IN = Number(process.env.JWT_EXPIRES_IN_SECONDS) || 3600;

router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: "Email e senha são obrigatórios" });
  }

  try {
    // Busca usuário por email
    const [rows]: [any[], any] = await db.query(
      "SELECT id, email, password, cargo FROM usuarios WHERE email = ?",
      [email],
    );

    if (rows.length === 0) {
      console.log(`Usuário não encontrado para email: ${email}`);
      return res.status(401).json({ error: "Usuário não encontrado" });
    }

    const user = rows[0];

    // Verifica senha
    const valid = await bcrypt.compare(password, user.password);
    console.log(`Resultado da verificação de senha: ${valid ? "válida" : "inválida"}`);
    
    if (!valid) {
      return res.status(401).json({ error: "Senha incorreta" });
    }

    // Gera token JWT incluindo a role
    const payload = { 
      id: user.id, 
      email: user.email,
      cargo: user.cargo
    };
    const options: SignOptions = { expiresIn: JWT_EXPIRES_IN };
    const token = jwt.sign(payload, JWT_SECRET, options);

    return res.json({ token });
  } catch (err: any) {
    console.error("Erro no login:", err);
    return res.status(500).json({ error: "Erro no servidor" });
  }
});

// Rotas para recuperação de senha (sem autenticação)
router.post("/auth/forgot-password", forgotPassword);
router.post("/auth/reset-password", resetPassword);

router.get("/relatorios/geral", async (req, res) => {
  try {
    const response = await axios.get(`${PLN_URL}/relatorio`);
    res.json(response.data);
  } catch (error: any) {
    res.status(500).json({ erro: `Erro ao buscar relatório do PLN: ${error.message}` });
  }
});

router.get("/relatorios/skus", async (req, res) => {
  try {
    const response = await axios.get(`${PLN_URL}/relatorio-skus`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ erro: "Erro ao buscar relatório de SKUs do PLN" });
  }
});

export default router;