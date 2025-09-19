import { Router } from "express";
import bcrypt from "bcryptjs";
import jwt, { SignOptions } from "jsonwebtoken";
import { Usuario } from "../models/Usuario";

const router = Router();

const JWT_SECRET: string = process.env.JWT_SECRET!;
if (!JWT_SECRET) {
  console.error("JWT_SECRET não configurado. Crie um .env com JWT_SECRET.");
  process.exit(1);
}

const JWT_EXPIRES_IN = Number(process.env.JWT_EXPIRES_IN_SECONDS) || 3600;

router.post("/registro", async (req, res) => {
  const { username, password, nome } = req.body;
  if (!username || !password)
    return res.status(400).json({ error: "Username e senha são obrigatórios" });

  try {
    const hash = await bcrypt.hash(password, 10);
    const user = await Usuario.create({ 
      username, 
      password: hash,
      nome: nome || username
    });
    res.json({ message: "Usuário registrado", id: user.id });
  } catch (err: any) {
    if (err.name === "SequelizeUniqueConstraintError") {
      return res.status(400).json({ error: "Usuário já existe" });
    }
    console.error(err);
    res.status(500).json({ error: "Erro no servidor" });
  }
});

router.post("/login", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password)
    return res.status(400).json({ error: "Username e password obrigatórios" });

  try {
    const user = await Usuario.findOne({ where: { username } });
    if (!user) return res.status(401).json({ error: "Usuário não encontrado" });

    const valid = await bcrypt.compare(password, user.password);
    if (!valid) return res.status(401).json({ error: "Senha incorreta" });

    const payload = { id: user.id, username: user.username };
    const options: SignOptions = { expiresIn: JWT_EXPIRES_IN };

    const token = jwt.sign(payload, JWT_SECRET, options);
    return res.json({ token });
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: "Erro no servidor" });
  }
});

export default router;
