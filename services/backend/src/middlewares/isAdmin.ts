import { Response, NextFunction } from "express";
import { AuthRequest } from "./auth";

export function isAdminMiddleware(req: AuthRequest, res: Response, next: NextFunction) {
  if (!req.user) {
    return res.status(401).json({ error: "Usuário não autenticado" });
  }

  if (req.user.role !== 'Administrator') {
    return res.status(403).json({ error: "Acesso permitido apenas para administradores" });
  }
  
  next();
}