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
      "SELECT id, nome, email, cargo, status, password, receberEmails FROM usuarios",
    );
    return res.json(rows);
  } catch (error) {
    console.error("Erro ao listar usuários:", error);
    return res.status(500).json({ error: "Erro ao buscar usuários" });
  }
};

// Exclusão de usuário
import { AuthRequest } from "../middlewares/auth";

export const deletarUsuario = async (req: AuthRequest, res: Response) => {
  const { id } = req.params;

  if (!id) {
    return res.status(400).json({ error: "ID do usuário é obrigatório" });
  }

  try {
    if (req.user && req.user.id === parseInt(id, 10)) {
      return res.status(403).json({ error: "Você não pode excluir sua própria conta" });
    }

    const [rows] = await db.query("SELECT id FROM usuarios WHERE id = ?", [id]);

    if ((rows as any[]).length === 0) {
      return res.status(404).json({ error: "Usuário não encontrado" });
    }

    await db.execute("DELETE FROM usuarios WHERE id = ?", [id]);

    return res.status(200).json({ message: "Usuário excluído com sucesso" });
  } catch (error) {
    console.error("Erro ao excluir usuário:", error);
    return res.status(500).json({ error: "Erro ao excluir usuário" });
  }
};

// Atualização de usuário
export const atualizarUsuario = async (req: AuthRequest, res: Response) => {
  const { id } = req.params;
  const { nome, email, password, cargo, status, receberEmails } = req.body;

  if (!id) {
    return res.status(400).json({ error: "ID do usuário é obrigatório" });
  }

  try {
    const [rows] = await db.query("SELECT * FROM usuarios WHERE id = ?", [id]);

    if ((rows as any[]).length === 0) {
      return res.status(404).json({ error: "Usuário não encontrado" });
    }

    const usuarioAtual = (rows as any[])[0];

    let hashPassword = usuarioAtual.password;
    if (password) {
      hashPassword = await bcrypt.hash(password, 10);
    }

    await db.execute(
      `UPDATE usuarios
       SET nome = ?, email = ?, password = ?, cargo = ?, status = ?, receberEmails = ?
       WHERE id = ?`,
      [
        nome || usuarioAtual.nome,
        email || usuarioAtual.email,
        hashPassword,
        cargo || usuarioAtual.cargo,
        status || usuarioAtual.status,
        receberEmails !== undefined ? receberEmails : usuarioAtual.receberEmails,
        id,
      ]
    );

    return res.status(200).json({ message: "Usuário atualizado com sucesso" });
  } catch (error) {
    console.error("Erro ao atualizar usuário:", error);
    return res.status(500).json({ error: "Erro ao atualizar usuário" });
  }
};
