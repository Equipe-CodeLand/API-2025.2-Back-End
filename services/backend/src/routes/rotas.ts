import bcrypt from "bcryptjs";
import jwt, { SignOptions } from "jsonwebtoken";
import { Router } from "express";
import {
  cadastrarUsuario,
  listarUsuarios,
} from "../controllers/UsuarioController";
import db from "../db/db";
import axios from "axios";
import { authMiddleware } from "../middlewares/auth";
import {
  gerarRelatorioGeral,
  gerarRelatorioSku,
  listarRelatorios,
} from "../controllers/RelatorioController";

const PLN_URL = "http://127.0.0.1:5000";
const router = Router();

/* Rotas de usuários */
router.post("/usuario/cadastrar", cadastrarUsuario);
router.get("/usuario/listar", listarUsuarios);

// rotas relatório
router.post("/relatorio/geral", authMiddleware, gerarRelatorioGeral);
router.post("/relatorio/skus", authMiddleware, gerarRelatorioSku);
router.get("/relatorio/listar", authMiddleware, listarRelatorios);

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
      "SELECT id, email, password FROM usuarios WHERE email = ?",
      [email],
    );

    if (rows.length === 0) {
      return res.status(401).json({ error: "Usuário não encontrado" });
    }

    const user = rows[0];

    // Verifica senha
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) {
      return res.status(401).json({ error: "Senha incorreta" });
    }

    // Gera token JWT
    const payload = { id: user.id, email: user.email };
    const options: SignOptions = { expiresIn: JWT_EXPIRES_IN };
    const token = jwt.sign(payload, JWT_SECRET, options);

    return res.json({ token });
  } catch (err: any) {
    console.error("Erro no login:", err);
    return res.status(500).json({ error: "Erro no servidor" });
  }
});

router.get("/relatorios/geral", async (req, res) => {
  try {
    const response = await axios.get(`${PLN_URL}/relatorio`);
    res.json(response.data);
  } catch (error) {
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
