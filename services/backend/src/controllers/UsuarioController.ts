import { Request, Response } from "express";
import db from "../db/db";
import bcrypt from "bcryptjs";

// Cadastro de usuário
export const cadastrarUsuario = async (req: Request, res: Response) => {
  const { nome, email, password, cargo } = req.body;

  if (!nome || !email || !password) {
    return res
      .status(400)
      .json({ error: "Nome, email e senha são obrigatórios" });
  }

  try {
    const hash = await bcrypt.hash(password, 10);

    const [result] = await db.execute(
      `INSERT INTO usuarios (nome, email, password, cargo, status, receberEmails)
       VALUES (?, ?, ?, ?, 'ativo', 1)`,
      [nome, email, hash, cargo || "USUARIO"],
    );

    return res.status(201).json({
      message: "Usuário cadastrado com sucesso",
      id: (result as any).insertId,
    });
  } catch (error: any) {
    if (error.code === "ER_DUP_ENTRY") {
      return res.status(400).json({ error: "Email já cadastrado" });
    }
    console.error("Erro ao cadastrar usuário:", error);
    return res.status(500).json({ error: "Erro ao cadastrar usuário" });
  }
};

// Listagem de usuários
export const listarUsuarios = async (req: Request, res: Response) => {
  try {
    const [rows] = await db.query(
      "SELECT id, nome, email, cargo, status, receberEmails FROM usuarios",
    );
    return res.json(rows);
  } catch (error) {
    console.error("Erro ao listar usuários:", error);
    return res.status(500).json({ error: "Erro ao buscar usuários" });
  }
};


