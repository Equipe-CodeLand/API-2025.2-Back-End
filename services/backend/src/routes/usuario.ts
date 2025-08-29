import { Router } from "express";
import { cadastrarUsuario, listarUsuarios } from "../controllers/usuarioController";

const router = Router();

// /usuario/cadastrar
router.post("/cadastrar", cadastrarUsuario);

// /usuario/listar
router.get("/listar", listarUsuarios);

export default router;