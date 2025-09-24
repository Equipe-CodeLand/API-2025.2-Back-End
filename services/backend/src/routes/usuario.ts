import { Router } from "express";
import { cadastrarUsuario, listarUsuarios, listarUsuario} from "../controllers/UsuarioController";

const router = Router();

router.post("/cadastro/usuario", cadastrarUsuario);

router.get("/usuarios", listarUsuarios);

router.get("/usuarios/:id", listarUsuario);


// rota de listagem

export default router;
