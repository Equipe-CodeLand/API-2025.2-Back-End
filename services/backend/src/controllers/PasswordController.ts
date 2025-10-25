import { Request, Response } from "express";
import db from "../db/db";
import crypto from "crypto";
import { enviarEmail } from "../services/emailService";
import bcrypt from "bcryptjs";

// Tempo de validade do token em ms (1 hora)
const TOKEN_VALID_MS = 1000 * 60 * 60;

export const forgotPassword = async (req: Request, res: Response) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ error: "Email é obrigatório" });
  }

  try {
    // Busca usuário
    const [rows] = await db.query("SELECT id, nome FROM usuarios WHERE email = ?", [email]);
    if ((rows as any[]).length === 0) {
      // Não vaza informação: responde sucesso mesmo que não exista
      return res.json({ message: "Se o email estiver cadastrado, um link para redefinir a senha foi enviado." });
    }

    const user = (rows as any[])[0];

    // Gera token
    const token = crypto.randomBytes(32).toString("hex");
    const expiresAt = new Date(Date.now() + TOKEN_VALID_MS);

    // Cria tabela password_resets se não existir
    await db.execute(`
      CREATE TABLE IF NOT EXISTS password_resets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        token VARCHAR(128) NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX (token),
        INDEX (user_id)
      ) ENGINE=InnoDB;
    `);

    // Insere o token
    await db.execute(
      `INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)`,
      [user.id, token, expiresAt],
    );

    // Monta link para frontend
    const FRONT_URL = process.env.FRONTEND_URL || process.env.REACT_APP_FRONTEND_URL || "http://localhost:3000";
    const resetLink = `${FRONT_URL}/reset-senha?token=${token}`;

    // Envia email
    const html = `
      <p>Olá ${user.nome || "usuário"},</p>
      <p>Recebemos uma solicitação para redefinir sua senha. Clique no link abaixo para criar uma nova senha (válido por 1 hora):</p>
      <p><a href="${resetLink}">Redefinir minha senha</a></p>
      <p>Se você não solicitou a alteração, ignore este e-mail.</p>
    `;

    await enviarEmail({
      to: email,
      subject: "Redefinição de senha",
      html,
    });

    return res.json({ message: "Se o email estiver cadastrado, um link para redefinir a senha foi enviado." });
  } catch (error: any) {
    console.error("Erro em forgotPassword:", error);
    return res.status(500).json({ error: "Erro ao processar solicitação" });
  }
};

export const resetPassword = async (req: Request, res: Response) => {
  const { token, password } = req.body;

  if (!token || !password) {
    return res.status(400).json({ error: "Token e nova senha são obrigatórios" });
  }

  try {
    // Busca token válido
    const [rows] = await db.query(
      `SELECT pr.id, pr.user_id, pr.expires_at, u.email FROM password_resets pr JOIN usuarios u ON u.id = pr.user_id WHERE pr.token = ?`,
      [token],
    );

    if ((rows as any[]).length === 0) {
      return res.status(400).json({ error: "Token inválido ou expirado" });
    }

    const record = (rows as any[])[0];
    const expiresAt = new Date(record.expires_at);
    if (expiresAt.getTime() < Date.now()) {
      // Remove token expirado
      await db.execute(`DELETE FROM password_resets WHERE id = ?`, [record.id]);
      return res.status(400).json({ error: "Token inválido ou expirado" });
    }

    // Atualiza senha do usuário
    const hash = await bcrypt.hash(password, 10);
    await db.execute(`UPDATE usuarios SET password = ? WHERE id = ?`, [hash, record.user_id]);

    // Remove token usado
    await db.execute(`DELETE FROM password_resets WHERE id = ?`, [record.id]);

    return res.json({ message: "Senha redefinida com sucesso" });
  } catch (error: any) {
    console.error("Erro em resetPassword:", error);
    return res.status(500).json({ error: "Erro ao redefinir senha" });
  }
};
