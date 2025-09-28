import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import db from "../db/db";
import { Cargo } from "../enum/Cargo";

export const authMiddleware = async (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: "Token não fornecido" });
  }

  const token = authHeader.split(" ")[1];

  try {
    const JWT_SECRET: string = process.env.JWT_SECRET!;
    const decoded = jwt.verify(token, JWT_SECRET) as any;

    // Buscar dados completos do usuário
    const [userRows]: [any[], any] = await db.query(
      "SELECT id, email, nome, receberEmails, cargo FROM usuarios WHERE id = ?",
      [decoded.id]
    );

    if (userRows.length === 0) {
      return res.status(401).json({ error: "Usuário não encontrado" });
    }

    const user = userRows[0];
    // Garantir que o cargo seja do tipo correto para o enum
    req.user = {
      ...user,
      cargo: user.cargo as Cargo
    };
    next();
  } catch (error) {
    return res.status(401).json({ error: "Token inválido" });
  }
};
