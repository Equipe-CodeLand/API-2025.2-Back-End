import { Request, Response, NextFunction } from "express";
import { Cargo } from "../enum/Cargo";

export function isAdminMiddleware(req: Request, res: Response, next: NextFunction) {
  if (!req.user) {
    console.log("isAdminMiddleware: req.user is undefined");
    return res.status(401).json({ error: "Usuário não autenticado" });
  }

  if (req.user.cargo === Cargo.ADMINISTRADOR) {
    next();
  } else {
    return res.status(403).json({ error: "Acesso permitido apenas para administradores" });
  }
}