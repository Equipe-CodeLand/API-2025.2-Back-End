import { Response, NextFunction } from "express";
import { AuthRequest } from "./auth";

export function isAdminMiddleware(req: AuthRequest, res: Response, next: NextFunction) {
  if (!req.user) {
    console.log("isAdminMiddleware: req.user is undefined");
    return res.status(401).json({ error: "Usuário não autenticado" });
  }

  if (req.user.cargo === "Administrador") {
    next();
  } else {
    return res.status(403).json({ error: "Acesso permitido apenas para administradores" });
  }
}