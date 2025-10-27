import { Request, Response } from "express";
import axios from "axios";

const PLN_URL = "http://127.0.0.1:5000";

export async function enviarMensagem(req: Request, res: Response) {
    try{
        const usuarioId = req.user?.id;
        const resp = await axios.post(`${PLN_URL}/chat`, {
          usuario_id: usuarioId,
          texto: req.body.texto
        });
    
        return res.json(resp.data);
      } 
      catch (err: any) {
        console.error(err);
        return res.status(500).json({ error: "Erro ao gerar relatório" });
      }
}