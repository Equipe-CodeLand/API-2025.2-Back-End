import bcrypt from "bcryptjs";
import jwt, { SignOptions } from "jsonwebtoken";
import { Router } from "express";
import {
  atualizarUsuario,
  cadastrarUsuario,
  deletarUsuario,
  listarUsuarios,
} from "../controllers/usuarioController";
import db from "../db/db";
import { authMiddleware } from "../middlewares/auth";

const router = Router();

/* Rotas de usuários */
router.post("/usuario/cadastrar", cadastrarUsuario);
router.get("/usuario/listar", listarUsuarios);
router.delete("/usuario/deletar/:id", authMiddleware, deletarUsuario);
router.put("/usuario/atualizar/:id", authMiddleware, atualizarUsuario);

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

export default router;
