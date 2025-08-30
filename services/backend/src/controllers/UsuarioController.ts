import { Request, Response } from "express";
import { UsuarioModel } from "../models/Usuario";

export const cadastrarUsuario = (req: Request, res: Response) => {
  const { nome } = req.body;
  const novoUsuario = UsuarioModel.criar(nome);
  res.status(201).json(novoUsuario);
};

export const listarUsuarios = (req: Request, res: Response) => {
  res.json(UsuarioModel.listar());
};
