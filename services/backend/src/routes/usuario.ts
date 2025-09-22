import { Router } from "express";
import { cadastrarUsuario} from "../controllers/UsuarioController";

const router = Router();

router.post("/cadastro/usuario", cadastrarUsuario);


// rota de listagem

export default router;
