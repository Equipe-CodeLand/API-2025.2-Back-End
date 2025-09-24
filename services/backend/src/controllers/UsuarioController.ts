import { Request, Response } from "express";
import { Usuario } from "../models/Usuario";
import { Cargo } from "../enum/Cargo";
import bcrypt from "bcryptjs";

export const cadastrarUsuario = async (req: Request, res: Response) => {
  const { nome, email, senha, cargo, receberEmails } = req.body;

  if (!nome || !email || !senha || !cargo) {
    return res.status(400).json({ mensagem: "Todos os campos são obrigatórios." });
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({ mensagem: "Email inválido." });
  }

  if (!Object.values(Cargo).includes(cargo)) {
    return res.status(400).json({ mensagem: "Cargo inválido." });
  }

  try {
    const hash = await bcrypt.hash(senha, 10);

    const novoUsuario = await Usuario.create({
      nome,
      email,
      password: hash,
      cargo,
      receberEmails,
    });

    return res.status(201).json(novoUsuario);
  } catch (error: any) {
    console.error(error);

    if (error.name === "SequelizeUniqueConstraintError") {
      return res.status(409).json({ mensagem: "Email já cadastrado." });
    }

    return res.status(500).json({ mensagem: "Erro ao cadastrar usuário." });
  }
};

export const listarUsuarios = async (req: Request, res: Response) => {
  try {
    const usuarios = await Usuario.findAll({
      attributes: { exclude: ["password"] }
    });

    return res.status(200).json(usuarios);
  } catch (error) {
    console.error(error);
    return res.status(500).json({ mensagem: "Erro ao buscar usuários." });
  }
};

export const listarUsuario = async (req: Request, res: Response) => {
  const { id } = req.params;

  try {
    const usuario = await Usuario.findByPk(id, {
      attributes: { exclude: ["password"] }
    });

    if (!usuario) {
      return res.status(404).json({ mensagem: "Usuário não encontrado." });
    }

    return res.status(200).json(usuario);
  } catch (error) {
    console.error(error);
    return res.status(500).json({ mensagem: "Erro ao buscar usuário." });
  }
};